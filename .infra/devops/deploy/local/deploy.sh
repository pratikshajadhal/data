#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for AWS CLI profile name
AWS_CLI_PROFILE_NAME=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/deploy/local/deploy.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional:SERVICE_DNS_HOSTED_ZONE_NAME> <optional:SERVICE_NAME> <optional:SERVICE_TASK_CONTAINER_PORT> <optional:SERVICE_TASK_MIN_CONTAINERS> <optional:SERVICE_TASK_MAX_CONTAINERS> <optional:SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional:ECS_CLUSTER_STACK_NAME> <optional:BUCKETS_STACK_NAME> <optional:SERVICE_STACK_NAME>"'
    exit 1
fi

# REQUIRED 2nd argument for tag of ECR image to be deployed as service/task container
SERVICE_ECR_IMAGE_TAG=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/devops/deploy/local/deploy.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional:SERVICE_DNS_HOSTED_ZONE_NAME> <optional:SERVICE_NAME> <optional:SERVICE_TASK_CONTAINER_PORT> <optional:SERVICE_TASK_MIN_CONTAINERS> <optional:SERVICE_TASK_MAX_CONTAINERS> <optional:SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional:ECS_CLUSTER_STACK_NAME> <optional:BUCKETS_STACK_NAME> <optional:SERVICE_STACK_NAME>"'
    exit 1
fi

# Optional 3rd argument for environment (resource name prefix)
SERVICE_DNS_ENV_ALIAS_KEY=$3

# Optional 4th argument for environment name (resource name prefix).  Default is "dev".  Allowed values are provided in the template.
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

# Optional 12th argument for cluster CloudFormation stack name
ECS_CLUSTER_STACK_NAME=${12}
if [ -z "${12}" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Optional 13th argument for buckets CloudFormation stack name
BUCKETS_STACK_NAME=${13}
if [ -z "${13}" ]
then
    BUCKETS_STACK_NAME="$ENV_NAME-data-api-01-buckets"
fi

# Optional 14th argument for this CloudFormation stack name
SERVICE_STACK_NAME=${14}
if [ -z "${14}" ]
then
    SERVICE_STACK_NAME="$ENV_NAME-data-api-02-service"
fi

echo
echo
echo "Preparing to udpate buckets..."

# Update CloudFormation stack 01-buckets
sh .infra/aws/cf/tools/01-buckets.sh $AWS_CLI_PROFILE_NAME $ENV_NAME $BUCKETS_STACK_NAME

echo
echo
echo "Preparing to udpate service..."
echo
echo

# Update CloudFormation stack 02-service
sh .infra/aws/cf/tools/02-service.sh $AWS_CLI_PROFILE_NAME $SERVICE_ECR_IMAGE_TAG $SERVICE_DNS_ENV_ALIAS_KEY $ENV_NAME $SERVICE_DNS_HOSTED_ZONE_NAME $SERVICE_NAME $SERVICE_TASK_CONTAINER_PORT $SERVICE_TASK_MIN_CONTAINERS $SERVICE_TASK_MAX_CONTAINERS $SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT $ALB_SSL_CERT_STACK_NAME $ECS_CLUSTER_STACK_NAME $BUCKETS_STACK_NAME $SERVICE_STACK_NAME

echo 
echo 
echo "Deployment to **$ENV_NAME** complete!"
echo 
