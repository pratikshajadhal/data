#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for AWS Access Key ID
export AWS_ACCESS_KEY_ID=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/deploy.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional: SERVICE_DNS_HOSTED_ZONE_NAME> <optional: SERVICE_NAME> <optional: SERVICE_TASK_CONTAINER_PORT> <optional: SERVICE_TASK_MIN_CONTAINERS> <optional: SERVICE_TASK_MAX_CONTAINERS> <optional: SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional: STACK_NAME_1>'
    exit 1
fi

# REQUIRED 2nd argument for AWS Secret Access Key
export AWS_SECRET_ACCESS_KEY=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/deploy.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional: SERVICE_DNS_HOSTED_ZONE_NAME> <optional: SERVICE_NAME> <optional: SERVICE_TASK_CONTAINER_PORT> <optional: SERVICE_TASK_MIN_CONTAINERS> <optional: SERVICE_TASK_MAX_CONTAINERS> <optional: SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional: STACK_NAME_1>'
    exit 1
fi

# REQUIRED 3rd argument for AWS Default Region
export AWS_DEFAULT_REGION=$3
if [ -z "$3" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/deploy.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional: SERVICE_DNS_HOSTED_ZONE_NAME> <optional: SERVICE_NAME> <optional: SERVICE_TASK_CONTAINER_PORT> <optional: SERVICE_TASK_MIN_CONTAINERS> <optional: SERVICE_TASK_MAX_CONTAINERS> <optional: SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional: STACK_NAME_1>'
    exit 1
fi

# REQUIRED 4th argument for tag of ECR image to be deployed as service/task container
SERVICE_ECR_IMAGE_TAG=$4
if [ -z "$4" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/deploy.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional: SERVICE_DNS_HOSTED_ZONE_NAME> <optional: SERVICE_NAME> <optional: SERVICE_TASK_CONTAINER_PORT> <optional: SERVICE_TASK_MIN_CONTAINERS> <optional: SERVICE_TASK_MAX_CONTAINERS> <optional: SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional: STACK_NAME_1>'
    exit 1
fi

# Optional 5th argument for environment DNS alias key (non-prod)
SERVICE_DNS_ENV_ALIAS_KEY=$5

# Optional 6th argument for environment name (resource name prefix)
ENV_NAME=$6
if [ -z "$6" ]
then
    ENV_NAME="dev"
fi

# Optional 7th argument for DNS hosted zone name (root domain)
SERVICE_DNS_HOSTED_ZONE_NAME=$7
if [ -z "$7" ]
then
    SERVICE_DNS_HOSTED_ZONE_NAME="truve.ai"
fi

# Optional 8th argument for service name within ECS cluster
SERVICE_NAME=$8
if [ -z "$8" ]
then
    SERVICE_NAME="data-api"
fi

# Optional 9th argument task container port
SERVICE_TASK_CONTAINER_PORT=$9
if [ -z "$9" ]
then
    SERVICE_TASK_CONTAINER_PORT="8081"
fi

# Optional 10th argument for autoscaling min containers
SERVICE_TASK_MIN_CONTAINERS=${10}
if [ -z "${10}" ]
then
    SERVICE_TASK_MIN_CONTAINERS=1
fi

# Optional 11th argument for autoscaling max containers
SERVICE_TASK_MAX_CONTAINERS=${11}
if [ -z "${11}" ]
then
    SERVICE_TASK_MAX_CONTAINERS=5
fi
# Optional 12th argument for CPU use percentage, after which autoscaling will occur
SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT=${12}
if [ -z "${12}" ]
then
    SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT=50
fi

# Optional 13th argument for ECS cluster stack name
ECS_CLUSTER_STACK_NAME=${13}
if [ -z "${13}" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Optional 14th argument for service stack name
STACK_NAME_1=${14}
if [ -z "${14}" ]
then
    STACK_NAME_1="$ENV_NAME-data-api-01-buckets"
fi

# Optional 15th argument for service stack name
STACK_NAME_2=${15}
if [ -z "${15}" ]
then
    STACK_NAME_2="$ENV_NAME-data-api-02-service"
fi

echo
echo "Deploying stack 01-buckets..."

# Update CloudFormation stack 01-buckets
aws cloudformation deploy --template-file=.infra/aws/cf/01-buckets.yml \
    --stack-name $STACK_NAME_1 \
    --capabilities CAPABILITY_NAMED_IAM

echo
echo
echo "Preparing to deploy stack 02-service..."
echo
echo

# Query ECS Cluster Name
echo "Fetching ECS Cluster Name..."
ECS_CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' --output text)

# Query ECS Cluster Autoscaling Role ARN
echo "Fetching ECS Cluster Autoscaling Role ARN..."
ECS_CLUSTER_AUTOSCALING_ROLE_ARN=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AutoScalingRoleArn`].OutputValue' --output text)

# Query Service ECR Name
echo "Fetching Service ECR Name..."
SERVICE_ECR_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiEcrName`].OutputValue' --output text)

# Query Service ALB ARN
echo "Fetching Service ALB ARN..."
SERVICE_ALB_ARN=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiArn`].OutputValue' --output text)

# Query Service ALB Security Group ID
echo "Fetching Service ALB Security Group ID..."
SERVICE_ALB_SECURITY_GROUP_ID=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiSecurityGroupId`].OutputValue' --output text)

# Query Service ALB DNS Name
echo "Fetching Service ALB DNS Name..."
SERVICE_ALB_DNS_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiDnsName`].OutputValue' --output text)

# Query Service DNS Name
echo "Fetching Service ALB Hosted Zone ID..."
SERVICE_ALB_HOSTED_ZONE_ID=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`AlbDataApiCanonicalHostedZoneID`].OutputValue' --output text)

# Query SSL cert ARN
echo "Fetching SSL Certificate ARN..."
SERVICE_DNS_SSL_SUBDOMAIN_CERT_ARN=$(aws acm list-certificates --query "CertificateSummaryList[?DomainName=='*.$SERVICE_DNS_HOSTED_ZONE_NAME'].CertificateArn | [0]" --output text)

# Query Bucket Name for Truve Raw Data
echo "Fetching Bucket Name for Truve Raw Data..."
BUCKET_NAME_TRUVE_RAW_DATA=$(aws cloudformation describe-stacks --stack-name $STACK_NAME_1 --query 'Stacks[0].Outputs[?OutputKey==`BucketNameTruveRawData`].OutputValue' --output text)

# Query Bucket Name for Truve Temp Data
echo "Fetching Bucket Name for Truve Temp Data..."
BUCKET_NAME_TRUVE_TEMP_DATA=$(aws cloudformation describe-stacks --stack-name $STACK_NAME_1 --query 'Stacks[0].Outputs[?OutputKey==`BucketNameTruveTempData`].OutputValue' --output text)

echo
echo
echo "Deploying stack 02-service..."
echo

# Update CloudFormation stack 02-service
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
        BucketNameTruveRawData=$BUCKET_NAME_TRUVE_RAW_DATA \
        BucketNameTruveTempData=$BUCKET_NAME_TRUVE_TEMP_DATA \
    --stack-name $STACK_NAME_2 \
    --capabilities CAPABILITY_NAMED_IAM \
   
echo 
echo 
echo "Deployment to **$ENV_NAME** complete!"
echo 
