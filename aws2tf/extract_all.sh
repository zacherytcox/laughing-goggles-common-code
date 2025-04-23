#!/bin/bash

# https://github.com/aws-samples/aws2tf?tab=readme-ov-file#quickstart-guide-to-using-the-tool
# Have Step 2 set the 'default' profile as the profile to assume with 'aws configure sso --profile default'
# Instead of step 3, run "bash ./extract_all.sh"


sections=("net" "acm" "apigw" "appmesh" "apprunner" "appstream" "artifact" "athena" "aurora" "asg" "bedrock" "batch" "code" "cf" "ct" "wan" "logs" "c9" "cloudform" "cognito" "config" "connect" "dz" "dms" "dynamodb" "eb" "ec2" "ecr" "ecs" "efs" "eks" "emr" "glue" "glue2" "group" "igw" "iam" "kendra" "kinesis" "kms" "lambda" "elb" "lf" "msk" "mwaa" "natgw" "nfw" "org" "params" "privatelink" "ram" "redshift" "route53" "rds" "s3" "s3tables" "subnet" "sagemaker" "secret" "sc" "sfn" "security-group" "sns" "sqs" "spot" "sso" "tgw" "transfer" "lattice" "user" "vpc" "waf" "wafv2" "workspaces")
this_name="$(aws --profile default sts get-caller-identity --query "Account" --output text)-$(aws --profile default configure get region)-$(date +%m-%d-%y)"
mkdir "$this_name"

# Iterate over each element in the list. Performing the 'all' option caused the command to fail.
for element in "${sections[@]}"
do
    echo "----> Processing $element"
    # Add your processing logic here
    ./aws2tf.py  -p default -s -t "$element"

    # shellcheck disable=2116,2086
    this_filename=main-$(echo $element).tf
    # shellcheck disable=2086
    cp generated/tf*/main.tf $this_name/$this_filename
    rm -rf ./generated/tf*
done
