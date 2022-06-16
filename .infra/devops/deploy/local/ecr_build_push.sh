#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for profile name
AWS_CLI_PROFILE_NAME=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/deploy/local/ecr_build_push.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# REQUIRED 2nd argument for ECR image tag
SERVICE_ECR_IMAGE_TAG=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/devops/deploy/local/ecr_build_push.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# Optional 3rd argument for environment (resource name prefix)
ENV_NAME=$3
if [ -z "$3" ]
then
    ENV_NAME="dev"
fi

# Optional 4th argument for cluster CloudFormation stack name
ECS_CLUSTER_STACK_NAME=$4
if [ -z "$4" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Query AWS Account ID
echo
echo "Fetching AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query AWS Region
echo "Fetching AWS Region..."
AWS_REGION=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[0].[RegionName]' --output text --profile $AWS_CLI_PROFILE_NAME)

# Query name of ECR
echo "Fetching ECR Name..."
SERVICE_ECR_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiEcrName`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Check if tag already exists
echo "Checking if image tag already exists in ECR..."
set +e
IMG_SHA_256=$(aws ecr describe-images --repository-name=$SERVICE_ECR_NAME --image-ids=imageTag=$SERVICE_ECR_IMAGE_TAG --query '(imageDetails | [0]).imageDigest' --output text --profile $AWS_CLI_PROFILE_NAME 2> /dev/null)
set -e
if [ -z "$IMG_SHA_256" ]
then
  echo "Image does not exist yet.  Proceeding..."
else
  echo "Image with tag $SERVICE_ECR_IMAGE_TAG already exists in ECR $SERVICE_ECR_NAME.  Aborting..."
  exit 1
fi

# Docker login
echo "ECR login..."
aws ecr get-login-password --profile $AWS_CLI_PROFILE_NAME | docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com || exit 1

# Image build
echo "Image building..."
echo
docker build -t $SERVICE_ECR_NAME:latest . || exit 1

# Tag
echo
echo "Image tagging..."
docker tag $SERVICE_ECR_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_ECR_NAME:$SERVICE_ECR_IMAGE_TAG
docker tag $SERVICE_ECR_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_ECR_NAME:latest

# Push
echo "Push image/tags..."
echo
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_ECR_NAME
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$SERVICE_ECR_NAME:$SERVICE_ECR_IMAGE_TAG

echo
echo
echo "Push complete!"
