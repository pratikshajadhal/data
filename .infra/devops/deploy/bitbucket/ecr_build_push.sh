#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for AWS Access Key ID
export AWS_ACCESS_KEY_ID=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/ecr_build_push.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# REQUIRED 2nd argument for AWS Secret Access Key
export AWS_SECRET_ACCESS_KEY=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/ecr_build_push.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# REQUIRED 3rd argument for AWS Default Region
export AWS_DEFAULT_REGION=$3
if [ -z "$3" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/ecr_build_push.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# REQUIRED 4th argument for ECR image tag
SERVICE_ECR_IMAGE_TAG=$4
if [ -z "$4" ]
then
    echo 'Usage: "sh .infra/devops/deploy/bitbucket/ecr_build_push.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>'
    exit 1
fi

# Optional 5th argument for environment (resource name prefix)
ENV_NAME=$5
if [ -z "$5" ]
then
    ENV_NAME="dev"
fi

# Optional 6th argument for cluster CloudFormation stack name
ECS_CLUSTER_STACK_NAME=$6
if [ -z "$6" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

echo
echo "Preparing to build/push image..."
echo

# Query AWS Account ID
echo "Fetching AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Query name of ECR
echo "Fetching Service ECR Name..."
SERVICE_ECR_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiEcrName`].OutputValue' --output text)

# Check if tag already exists
echo "Checking if image tag already exists in ECR..."
set +e
IMG_SHA_256=$(aws ecr describe-images --repository-name=$SERVICE_ECR_NAME --image-ids=imageTag=$SERVICE_ECR_IMAGE_TAG --query '(imageDetails | [0]).imageDigest' --output text 2> /dev/null)
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
aws ecr get-login-password | docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com || exit 1

# Image build
echo "Image building..."
echo
docker build -t $SERVICE_ECR_NAME:latest . || exit 1
 
# Tag
echo
echo "Image tagging..."
docker tag $SERVICE_ECR_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$SERVICE_ECR_NAME:$SERVICE_ECR_IMAGE_TAG
docker tag $SERVICE_ECR_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$SERVICE_ECR_NAME:latest

# Push
echo "Push image/tags..."
echo
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$SERVICE_ECR_NAME
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$SERVICE_ECR_NAME:$SERVICE_ECR_IMAGE_TAG

echo
echo
echo "Push complete!"
