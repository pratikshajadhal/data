#!/usr/bin/env bash

set -e

# REQUIRED 1st argument for local AWS CLI profile name
AWS_CLI_PROFILE_NAME=$1
if [ -z "$1" ]
then
    echo 'Usage: "sh .infra/aws/cf/tools/01-buckets.sh <AWS_CLI_PROFILE_NAME> <optional:ENV_NAME> <optional:STACK_NAME>"'
    exit 1
fi

# Optional 2nd argument for environment name (resource name prefix)
ENV_NAME=$2
if [ -z "$2" ]
then
    ENV_NAME="dev"
fi

# Optional 3rd argument for this CloudFormation stack name
STACK_NAME=$3
if [ -z "$3" ]
then
    STACK_NAME="$ENV_NAME-data-api-01-buckets"
fi

# deploy stack
aws cloudformation deploy --template-file=.infra/aws/cf/01-buckets.yml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --profile $AWS_CLI_PROFILE_NAME
