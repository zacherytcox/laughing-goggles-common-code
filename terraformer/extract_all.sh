#!/bin/bash

this_resources="accessanalyzer,acm,alb,api_gateway,appsync,auto_scaling,batch,budgets,cloud9,cloudformation,cloudfront,cloudhsm,cloudtrail,cloudwatch,codebuild,codecommit,codedeploy,codepipeline,cognito,config,customer_gateway,datapipeline,devicefarm,docdb,dynamodb,ebs,ec2_instance,ecr,ecrpublic,ecs,efs,eip,eks,elasticache,elastic_beanstalk,elb,emr,eni,es,firehose,glue,iam,igw,iot,kinesis,kms,lambda,logs,media_package,media_store,medialive,mq,msk,nacl,nat,opsworks,organization,qldb,rds,redshift,resourcegroups,route53,route_table,s3,secretsmanager,securityhub,servicecatalog,ses,sfn,sg,sns,sqs,ssm,subnet,swf,transit_gateway,vpc,vpc_endpoint,vpc_peering,vpn_connection,vpn_gateway,waf,waf_regional,wafv2_cloudfront,wafv2_regional,workspaces,xray"
this_regions=("ap-south-1,eu-north-1,eu-west-3,eu-west-2,eu-west-1,ap-northeast-3,ap-northeast-2,ap-northeast-1,ca-central-1,sa-east-1,ap-southeast-1,ap-southeast-2,eu-central-1,us-east-1,us-east-2,us-west-1,us-west-2")

# Prompt the user for a parameter
read -p "Please enter the name of the AWS Profile to use (specify 'default' for default credential): " parameter

# Check if the parameter is empty
if [ -z "$parameter" ]; then
    error_exit "Error: No profile specified. Exiting..."
fi

terraform --version > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'terraform' is not installed. Installing..."
    brew install terraform
fi

terraformer --version > /dev/null 2>&1
# shellcheck disable=2181
if [ $? -ne 0 ]; then
    echo "'terraformer' is not installed. Installing..."
    brew install terraformer
fi

this_aws_profile=$parameter

echo """
terraform {
  required_providers {
    aws = {
      version = "~> 5.92.0"
    }
  }
}
""" > ./versions.tf

terraform init

# Prompt the user for a parameter
read -p "Enter 'yes' to run terraformer (profile: $this_aws_profile). Anything else to skip." run_runner

# Check if the parameter is empty
if [ "$run_runner" == "yes" ]; then
    echo "Running terraformer..."
    terraformer import aws --resources="$this_resources" --regions="$this_regions" --profile=$this_aws_profile
fi
