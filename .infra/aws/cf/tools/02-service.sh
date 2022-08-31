#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for local AWS CLI profile name
AWS_CLI_PROFILE_NAME=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/aws/cf/tools/02-service.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional:SERVICE_DNS_HOSTED_ZONE_NAME> <optional:SERVICE_NAME> <optional:SERVICE_TASK_CONTAINER_PORT> <optional:SERVICE_TASK_MIN_CONTAINERS> <optional:SERVICE_TASK_MAX_CONTAINERS> <optional:SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional:ALB_SSL_CERT_STACK_NAME> <optional:ECS_CLUSTER_STACK_NAME> <optional:DATABRICKS_STACK_NAME> <optional:BUCKETS_STACK_NAME> <optional:STACK_NAME>"'
    exit 1
fi

# REQUIRED 2nd argument for tag of ECR image to be deployed as service/task container
SERVICE_ECR_IMAGE_TAG=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/aws/cf/tools/02-service.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional:SERVICE_DNS_HOSTED_ZONE_NAME> <optional:SERVICE_NAME> <optional:SERVICE_TASK_CONTAINER_PORT> <optional:SERVICE_TASK_MIN_CONTAINERS> <optional:SERVICE_TASK_MAX_CONTAINERS> <optional:SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional:ALB_SSL_CERT_STACK_NAME> <optional:ECS_CLUSTER_STACK_NAME> <optional:DATABRICKS_STACK_NAME> <optional:BUCKETS_STACK_NAME> <optional:STACK_NAME>"'
    exit 1
fi

# Optional 3rd argument for environment DNS alias key (non-prod)
SERVICE_DNS_ENV_ALIAS_KEY=$3
if [ -z "$3" ]
then
    ENV_NAME="prod"
fi

# Optional 4th argument for environment name (resource name prefix)
ENV_NAME=$4
if [ -z "$4" ]
then
    ENV_NAME="dev"
fi

# Optional 5th argument for DNS hosted zone name (root domain)
SERVICE_DNS_HOSTED_ZONE_NAME=$5
if [ -z "$5" ]
then
    SERVICE_DNS_HOSTED_ZONE_NAME="truve.ai"
fi

# Optional 6th argument for environment (resource name prefix)
SERVICE_NAME=$6
if [ -z "$6" ]
then
    SERVICE_NAME="data-api"
fi

# Optional 7th argument for hosted zone name
SERVICE_TASK_CONTAINER_PORT=$7
if [ -z "$7" ]
then
    SERVICE_TASK_CONTAINER_PORT="8080"
fi

# Optional 8th argument for hosted zone name
SERVICE_TASK_MIN_CONTAINERS=$8
if [ -z "$8" ]
then
    SERVICE_TASK_MIN_CONTAINERS=1
fi

# Optional 9th argument for hosted zone name
SERVICE_TASK_MAX_CONTAINERS=$9
if [ -z "$9" ]
then
    SERVICE_TASK_MAX_CONTAINERS=5
fi

# Optional 10th argument for CPU use percentage, after which autoscaling will occur
SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT=${10}
if [ -z "${10}" ]
then
    SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT=50
fi

# Optional 11th argument for CPU use percentage, after which autoscaling will occur
ALB_SSL_CERT_STACK_NAME=${11}
if [ -z "${11}" ]
then
    ALB_SSL_CERT_STACK_NAME="all-truve-devops-00-ssl-alb"
fi

# Optional 12th argument for CPU use percentage, after which autoscaling will occur
ECS_CLUSTER_STACK_NAME=${12}
if [ -z "${12}" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Optional 13th argument for Databricks Cloudformation stack name
DATABRICKS_STACK_NAME=${13}
if [ -z "${13}" ]
then
    DATABRICKS_STACK_NAME="$ENV_NAME-truve-devops-05-databricks"
fi

# Optional 14th argument for buckets CloudFormation buckets stack name
BUCKETS_STACK_NAME=${14}
if [ -z "${14}" ]
then
    BUCKETS_STACK_NAME="$ENV_NAME-data-api-01-buckets"
fi

# Optional 15th argument for this CloudFormation service stack name
STACK_NAME=${15}
if [ -z "${15}" ]
then
    STACK_NAME="$ENV_NAME-data-api-02-service"
fi

# Query ECS Cluster Name
echo "Fetching ECS Cluster Name..."
ECS_CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query ECS Cluster Autoscaling Role ARN
echo "Fetching ECS Cluster Autoscaling Role ARN..."
ECS_CLUSTER_AUTOSCALING_ROLE_ARN=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AutoScalingRoleArn`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Service ECR Name
echo "Fetching Service ECR Name..."
SERVICE_ECR_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiEcrName`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Service ALB ARN
echo "Fetching Service ALB ARN..."
SERVICE_ALB_ARN=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiArn`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Service ALB Security Group ID
echo "Fetching Service ALB Security Group ID..."
SERVICE_ALB_SECURITY_GROUP_ID=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiSecurityGroupId`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Service ALB DNS Name
echo "Fetching Service ALB DNS Name..."
SERVICE_ALB_DNS_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiDnsName`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Service DNS Name
echo "Fetching Service ALB Hosted Zone ID..."
SERVICE_ALB_HOSTED_ZONE_ID=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiCanonicalHostedZoneID`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query SSL cert ARN
echo "Fetching SSL Certificate ARN..."
SERVICE_DNS_SSL_SUBDOMAIN_CERT_ARN=$(aws cloudformation describe-stacks --stack-name $ALB_SSL_CERT_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`SslCertArn`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query ETL Raw Bucket name from truve-devops databricks stack
echo "Fetching ETL Raw Data Bucket Name..."
BUCKET_NAME_ETL_RAW_DATA=$(aws cloudformation describe-stacks --stack-name $DATABRICKS_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`BucketNameEtlRawData`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query Etl Temp Data Bucket name from data-api buckets stack
echo "Fetching Temp Data Bucket name..."
BUCKET_NAME_TEMP_DATA=$(aws cloudformation describe-stacks --stack-name $BUCKETS_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`BucketNameEtlTempData`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# deploy stack
aws cloudformation deploy --template-file=.infra/aws/cf/02-service.yml \
    --parameter-overrides \
        ServiceEcrImageTag=$SERVICE_ECR_IMAGE_TAG \
        EnvironmentName=$ENV_NAME \
        ServiceDnsEnvAliasKey=$SERVICE_DNS_ENV_ALIAS_KEY \
        ServiceName=$SERVICE_NAME \
        ServiceDnsHostedZoneName=$SERVICE_DNS_HOSTED_ZONE_NAME \
        ServiceTaskContainerPort=$SERVICE_TASK_CONTAINER_PORT \
        ServiceTaskMinContainers=$SERVICE_TASK_MIN_CONTAINERS \
        ServiceTaskMaxContainers=$SERVICE_TASK_MAX_CONTAINERS \
        ServiceAutoscalingTargetTaskCpuPct=$SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT \
        EcsClusterName=$ECS_CLUSTER_NAME \
        EcsClusterAutoscalingRoleArn=$ECS_CLUSTER_AUTOSCALING_ROLE_ARN \
        ServiceEcrName=$SERVICE_ECR_NAME \
        ServiceAlbArn=$SERVICE_ALB_ARN \
        ServiceAlbSecurityGroupId=$SERVICE_ALB_SECURITY_GROUP_ID \
        ServiceAlbDnsName=$SERVICE_ALB_DNS_NAME \
        ServiceAlbDnsHostedZoneId=$SERVICE_ALB_HOSTED_ZONE_ID \
        ServiceDnsSslCertArn=$SERVICE_DNS_SSL_SUBDOMAIN_CERT_ARN \
        BucketNameTempData=$BUCKET_NAME_TEMP_DATA \
        BucketNameEtlRawData=$BUCKET_NAME_ETL_RAW_DATA \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --profile $AWS_CLI_PROFILE_NAME
