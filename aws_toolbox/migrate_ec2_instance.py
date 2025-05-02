#!/usr/bin/env python3
"""
Script to copy EC2 instances from one AWS account to another,
handling VPC, security group, and subnet mappings,
validating resource presence, and tracking transfer status with parallel processing.
"""
import boto3
import logging
import time
import concurrent.futures
from botocore.exceptions import ClientError

# Configure logging
debug_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=debug_format)
logger = logging.getLogger(__name__)

# AWS configuration: replace with your profile names or credentials
SOURCE_PROFILE = "source_profile_name"
DEST_PROFILE = "dest_profile_name"
REGION = "us-east-1"

# Waiter and concurrency configuration
WAIT_DELAY = 15  # seconds between checks
MAX_ATTEMPTS = 40  # maximum attempts before timeout
MAX_WORKERS = 5  # threads for parallel execution

# Global transfer status
transfer_status = {}


def create_sessions():
    """Create boto3 sessions for source and destination accounts."""
    src = boto3.Session(profile_name=SOURCE_PROFILE, region_name=REGION)
    dst = boto3.Session(profile_name=DEST_PROFILE, region_name=REGION)
    return src, dst


def build_vpc_mapping(src_ec2, dst_ec2):
    """Map VPC IDs from source to destination by Name tag or CIDR block."""
    vpc_map = {}
    for vpc in src_ec2.vpcs.all():
        name = next((t["Value"] for t in vpc.tags or [] if t["Key"] == "Name"), None)
        filters = []
        if name:
            filters.append({"Name": "tag:Name", "Values": [name]})
        else:
            filters.append({"Name": "cidr-block", "Values": [vpc.cidr_block]})
        try:
            matches = list(dst_ec2.vpcs.filter(Filters=filters))
            if matches:
                vpc_map[vpc.id] = matches[0].id
            else:
                logger.warning(
                    f"[VPC] No match for source VPC {vpc.id} (Name={name}), skipping mapping."
                )
        except ClientError as e:
            logger.error(f"[VPC] Error mapping VPC {vpc.id}: {e}")
    return vpc_map


def build_network_mapping(src_ec2, dst_ec2, vpc_map):
    """Map security group and subnet IDs from source to destination using vpc_map."""
    sg_map = {}
    for sg in src_ec2.security_groups.all():
        name = sg.group_name
        dest_vpc_id = vpc_map.get(sg.vpc_id)
        filters = [{"Name": "group-name", "Values": [name]}]
        if dest_vpc_id:
            filters.append({"Name": "vpc-id", "Values": [dest_vpc_id]})
        try:
            matches = list(dst_ec2.security_groups.filter(Filters=filters))
            if matches:
                sg_map[sg.group_id] = matches[0].group_id
            else:
                # create placeholder mapping; will warn later
                sg_map[sg.group_id] = None
                logger.warning(f"[Network] No SG match for {name} in VPC {dest_vpc_id}")
        except ClientError as e:
            logger.error(f"[Network] SG mapping error for {name}: {e}")

    subnet_map = {}
    for subnet in src_ec2.subnets.all():
        cidr = subnet.cidr_block
        name = next((t["Value"] for t in subnet.tags or [] if t["Key"] == "Name"), None)
        dest_vpc_id = vpc_map.get(subnet.vpc_id)
        filters = [{"Name": "cidr-block", "Values": [cidr]}]
        if name:
            filters.append({"Name": "tag:Name", "Values": [name]})
        if dest_vpc_id:
            filters.append({"Name": "vpc-id", "Values": [dest_vpc_id]})
        try:
            matches = list(dst_ec2.subnets.filter(Filters=filters))
            if matches:
                subnet_map[subnet.id] = matches[0].id
            else:
                subnet_map[subnet.id] = None
                logger.warning(
                    f"[Network] No subnet match for {subnet.id} (CIDR={cidr})"
                )
        except ClientError as e:
            logger.error(f"[Network] Subnet mapping error for {subnet.id}: {e}")

    return sg_map, subnet_map


def validate_destination_resources(src_ec2, dst_ec2, vpc_map, sg_map, subnet_map):
    """Check that destination has mappings for VPCs, SGs, and subnets; return any missing."""
    missing = {"vpcs": [], "security_groups": [], "subnets": []}
    # VPCs
    for vpc in src_ec2.vpcs.all():
        if vpc.id not in vpc_map:
            missing["vpcs"].append(vpc.id)
    # Security Groups
    for sg in src_ec2.security_groups.all():
        if sg.group_id not in sg_map or not sg_map.get(sg.group_id):
            missing["security_groups"].append(sg.group_id)
    # Subnets
    for subnet in src_ec2.subnets.all():
        if subnet.id not in subnet_map or not subnet_map.get(subnet.id):
            missing["subnets"].append(subnet.id)

    if any(missing.values()):
        logger.error(f"[Validation] Missing destination resources: {missing}")
    else:
        logger.info(
            "[Validation] All required resources are present in destination account."
        )
    return missing


def copy_ami(src_cli, dst_cli, inst_id):
    """Create AMI on source and copy it to destination."""
    status = transfer_status[inst_id]["ami_copy"]
    try:
        name = f"copy-{inst_id}-{int(time.time())}"
        resp = src_cli.create_image(InstanceId=inst_id, Name=name, NoReboot=True)
        src_ami = resp["ImageId"]
        status["source_image_id"] = src_ami
        logger.info(f"[AMI] Created source AMI {src_ami}")

        waiter = src_cli.get_waiter("image_available")
        waiter.wait(
            ImageIds=[src_ami],
            WaiterConfig={"Delay": WAIT_DELAY, "MaxAttempts": MAX_ATTEMPTS},
        )

        copy = dst_cli.copy_image(Name=name, SourceImageId=src_ami, SourceRegion=REGION)
        dst_ami = copy["ImageId"]
        status["dest_image_id"] = dst_ami
        logger.info(f"[AMI] Copy initiated to {dst_ami}")

        waiter = dst_cli.get_waiter("image_available")
        waiter.wait(
            ImageIds=[dst_ami],
            WaiterConfig={"Delay": WAIT_DELAY, "MaxAttempts": MAX_ATTEMPTS},
        )

        status["status"] = "completed"
    except ClientError as e:
        status.update({"status": "error", "error": str(e)})
        logger.error(f"[AMI] Error copying AMI: {e}")


def snapshot_volumes(src_cli, dst_cli, instance):
    """Snapshot EBS volumes and copy snapshots."""
    inst_id = instance.id
    for vol in instance.volumes.all():
        st = transfer_status[inst_id]["volume_snapshots"][vol.id]
        try:
            snap = src_cli.create_snapshot(
                VolumeId=vol.id, Description=f"Snap {vol.id}"
            )
            st["source_snapshot_id"] = snap["SnapshotId"]
            waiter = src_cli.get_waiter("snapshot_completed")
            waiter.wait(
                SnapshotIds=[st["source_snapshot_id"]],
                WaiterConfig={"Delay": WAIT_DELAY, "MaxAttempts": MAX_ATTEMPTS},
            )

            copy = dst_cli.copy_snapshot(
                SourceSnapshotId=st["source_snapshot_id"], SourceRegion=REGION
            )
            st["dest_snapshot_id"] = copy["SnapshotId"]
            waiter = dst_cli.get_waiter("snapshot_completed")
            waiter.wait(
                SnapshotIds=[st["dest_snapshot_id"]],
                WaiterConfig={"Delay": WAIT_DELAY, "MaxAttempts": MAX_ATTEMPTS},
            )
            st["status"] = "completed"
        except ClientError as e:
            st.update({"status": "error", "error": str(e)})
            logger.error(f"[Volume] Error on {vol.id}: {e}")


def launch_instance(dst_ec2, instance, sg_map, subnet_map):
    """Launch EC2 in destination using mapped network resources."""
    iid = instance.id
    st = transfer_status[iid]["instance_launch"]
    try:
        src_sgs = [sg["GroupId"] for sg in instance.security_groups]
        dst_sgs = [sg_map.get(g) for g in src_sgs]
        dst_sub = subnet_map.get(instance.subnet_id)

        new = dst_ec2.create_instances(
            ImageId=transfer_status[iid]["ami_copy"]["dest_image_id"],
            InstanceType=instance.instance_type,
            KeyName=instance.key_name,
            SecurityGroupIds=[g for g in dst_sgs if g],
            SubnetId=dst_sub,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {"ResourceType": "instance", "Tags": instance.tags or []}
            ],
        )[0]
        st.update({"dest_instance_id": new.id, "status": "completed"})
        logger.info(f"[Launch] Launched {new.id}")
    except ClientError as e:
        st.update({"status": "error", "error": str(e)})
        logger.error(f"[Launch] Error launching {iid}: {e}")


def process_instance(inst, src_cli, dst_cli, src_ec2, dst_ec2, sg_map, subnet_map):
    """Handle full workflow for a single instance."""
    iid = inst.id
    logger.info(f"--- Transfer {iid} ---")
    transfer_status[iid] = {
        "ami_copy": {
            "status": "pending",
            "error": None,
            "source_image_id": None,
            "dest_image_id": None,
        },
        "volume_snapshots": {
            v.id: {
                "status": "pending",
                "error": None,
                "source_snapshot_id": None,
                "dest_snapshot_id": None,
            }
            for v in inst.volumes.all()
        },
        "instance_launch": {
            "status": "pending",
            "error": None,
            "dest_instance_id": None,
        },
    }
    copy_ami(src_cli, dst_cli, iid)
    if transfer_status[iid]["ami_copy"]["status"] == "completed":
        snapshot_volumes(src_cli, dst_cli, inst)
        if all(
            v["status"] == "completed"
            for v in transfer_status[iid]["volume_snapshots"].values()
        ):
            launch_instance(dst_ec2, inst, sg_map, subnet_map)
    logger.info(f"--- Done {iid}: {transfer_status[iid]} ---")


def main():
    src_sess, dst_sess = create_sessions()
    src_cli, dst_cli = src_sess.client("ec2"), dst_sess.client("ec2")
    src_ec2, dst_ec2 = src_sess.resource("ec2"), dst_sess.resource("ec2")

    # Build mappings
    vpc_map = build_vpc_mapping(src_ec2, dst_ec2)
    sg_map, subnet_map = build_network_mapping(src_ec2, dst_ec2, vpc_map)

    # Validate before transfer
    missing = validate_destination_resources(
        src_ec2, dst_ec2, vpc_map, sg_map, subnet_map
    )
    if any(missing.values()):
        logger.error("Aborting: Destination account missing required resources.")
        return

    # Process instances in parallel
    instances = list(src_ec2.instances.all())
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                process_instance,
                inst,
                src_cli,
                dst_cli,
                src_ec2,
                dst_ec2,
                sg_map,
                subnet_map,
            )
            for inst in instances
        ]
        for f in concurrent.futures.as_completed(futures):
            try:
                f.result()
            except Exception as e:
                logger.error(f"Processing error: {e}")

    logger.info("=== Final Transfer Status ===")
    for iid, s in transfer_status.items():
        logger.info(f"{iid}: {s}")


if __name__ == "__main__":
    main()
