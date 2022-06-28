#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for AWS CLI profile name
AWS_CLI_PROFILE_NAME=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/devops/env/put.sh <AWS_CLI_PROFILE_NAME> <optional: ENV_NAME> <optional:ECS_CLUSTER_STACK_NAME>"'
    exit 1
fi

# Optional 2nd argument for environment name (resource name prefix).  Default is "dev".  Allowed values are provided in the CloudFormation template.
ENV_NAME=$2
if [ -z "$2" ]
then
    ENV_NAME="dev"
fi

# Optional 3rd argument for ECS cluster stack name
ECS_CLUSTER_STACK_NAME=$3
if [ -z "$3" ]
then
    ECS_CLUSTER_STACK_NAME="$ENV_NAME-truve-devops-06-ecs-cluster"
fi

# Create directory for env dotfiles if not present
mkdir -p .infra/devops/env/dotfiles

# Query secret name
echo "Fetching secret ARN..."
SECRET_ARN_ENV_VARS=$(aws cloudformation describe-stacks --stack-name $ECS_CLUSTER_STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`ServiceDataApiSecretArnEnvVars`].OutputValue' --output text --profile $AWS_CLI_PROFILE_NAME)

# Convert local dotfile value to JSON format (temp)
node .infra/devops/env/tools/conv/conv_dot_json.js .infra/devops/env/dotfiles/$ENV_NAME.env .infra/devops/env/dotfiles/$ENV_NAME.json

# Put secret value
echo "Updating secret value..."
aws secretsmanager put-secret-value --secret-id $SECRET_ARN_ENV_VARS --secret-string file://.infra/devops/env/dotfiles/$ENV_NAME.json --profile $AWS_CLI_PROFILE_NAME

# Remove temp JSON file
rm .infra/devops/env/dotfiles/$ENV_NAME.json
