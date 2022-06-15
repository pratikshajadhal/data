#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for AWS Access Key ID
export AWS_ACCESS_KEY_ID=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/alerts/ms-teams-deploy/send.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional: ECS_CLUSTER_STACK_NAME> <optional: STACK_NAME_2>'
    exit 1
fi

# REQUIRED 2nd argument for AWS Secret Access Key
export AWS_SECRET_ACCESS_KEY=$2
if [ -z "$2" ]
then
    echo 'Usage: "sh .infra/devops/alerts/ms-teams-deploy/send.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional: ECS_CLUSTER_STACK_NAME> <optional: STACK_NAME_2>'
    exit 1
fi

# REQUIRED 3rd argument for AWS Default Region
export AWS_DEFAULT_REGION=$3
if [ -z "$3" ]
then
    echo 'Usage: "sh .infra/devops/alerts/ms-teams-deploy/send.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional: ECS_CLUSTER_STACK_NAME> <optional: STACK_NAME_2>'
    exit 1
fi


# REQUIRED 4th argument for ECR image tag
SERVICE_ECR_IMAGE_TAG=$4
if [ -z "$4" ]
then
    echo 'Usage: "sh .infra/devops/alerts/ms-teams-deploy/send.sh <AWS_ACCESS_KEY_ID> <AWS_SECRET_ACCESS_KEY> <AWS_DEFAULT_REGION> <SERVICE_ECR_IMAGE_TAG> <optional:ENV_NAME> <optional: ECS_CLUSTER_STACK_NAME> <optional: STACK_NAME_2>'
    exit 1
fi

# Optional 5th argument for environment (resource name prefix)
ENV_NAME=$5
if [ -z "$5" ]
then
    ENV_NAME="dev"
fi

# Optional 6th argument for service stack name
ECS_CLUSTER_STACK_NAME=$6
if [ -z "$6" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Optional 7th argument for service stack name
STACK_NAME_2=$7
if [ -z "$7" ]
then
    STACK_NAME_2="$ENV_NAME-data-api-02-service"
fi

echo 
echo "Preparing to send alert to MS Teams > SRE > Deployment Alerts..."
echo

# Query AWS Account ID
echo "Fetching AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

# Query name of ECR
echo "Fetching Service ECR Name..."
SERVICE_ECR_NAME=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiEcrName`].OutputValue' --output text)

# Query image sha256
echo "Fetching Image Digest..."
IMG_SHA_256=$(aws ecr describe-images --repository-name=$SERVICE_ECR_NAME --image-ids=imageTag=$SERVICE_ECR_IMAGE_TAG --query '(imageDetails | [0]).imageDigest' --output text)

# Query health check endpoint
echo "Fetching Health Check Endpoint..."
HEALTH_CHECK_ENDPOINT=$(aws cloudformation describe-stacks --stack-name $STACK_NAME_2 --query 'Stacks[0].Outputs[?OutputKey==`HealthCheckEndpoint`].OutputValue' --output text)

# Default alert variables
BITBUCKET_REPO_NAME=data-api
BITBUCKET_PIPELINE_URL="$BITBUCKET_GIT_HTTP_ORIGIN/pipelines/results/$BITBUCKET_BUILD_NUMBER"
MS_TEAMS_CHANNEL_WEBHOOK_URL=https://cerebrio.webhook.office.com/webhookb2/26d80bae-6989-4980-a8e8-0ea987ca3488@e0483662-9b22-4571-b42b-a67513759956/IncomingWebhook/06335a32943946f7ac7d2859f18d62f5/8eaf6546-2a09-4966-be76-0f078fdac527

# Send Alert
MS_TEAMS_ALERT_PAYLOAD=$(node .infra/devops/alerts/ms-teams-deploy/payload/send.js \
    $MS_TEAMS_CHANNEL_WEBHOOK_URL \
    $ENV_NAME \
    $BITBUCKET_REPO_NAME \
    $BITBUCKET_PIPELINE_URL \
    $AWS_DEFAULT_REGION \
    $AWS_ACCOUNT_ID \
    $SERVICE_ECR_NAME \
    $IMG_SHA_256 \
    $SERVICE_ECR_IMAGE_TAG \
    $HEALTH_CHECK_ENDPOINT)

echo
echo "Alert Sent!"
echo
echo "Check MS Teams > Teams > SRE > Channels > Deployment Alerts"
