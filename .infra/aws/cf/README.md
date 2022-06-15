##### Infrastructure

<h1>CloudFormation</h1>

This directory contains CloudFormation templates in the YAML format.  These templates are used to create/update CloudFormation "stacks".

- [Repo Scope](#repo-scope)
- [Prerequisites](#prerequisites)
- [Stacks](#stacks)
  - [02-service](#02-service)
    - [How to Run](#how-to-run)
      - [Arguments](#arguments)

<br/>

# Repo Scope
Main Data API

<br/>

# Prerequisites

In order to run the tools locally, you will need to have the AWS CLI installed and configured for our AWS project.  Docs with steps on how to do this are [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).  
Make sure to create a local AWS CLI profile for our AWS project and provide that profile name below in substitution for `<AWS_CLI_PROFILE_NAME>`.  
  - To see available profiles, you can run `aws configure list-profiles`.  
  - To create and/or re-configure an AWS CLI profiles, run `aws configure --profile <AWS_CLI_PROFILE_NAME>`
    - Enter default region for project: `us-west-2`
    - Enter default output format: `json`

<br/>

# Stacks

This section describes each template and how to apply.  When setting up a new environment, run in order.  

<br/>

## 02-service

The [02-service.yml](02-service.yml) template sets up resources to run API server as Fargate task in env [ECS cluster](https://bitbucket.org/truveio/truve-devops/src/development/.infra/aws/cf/06-env-ecs-cluster.yml).

<br/>

### How to Run

Apply this template by running the following bash script from repo root:
```sh
sh .infra/aws/cf/tools/02-service.sh <AWS_CLI_PROFILE_NAME> <SERVICE_ECR_IMAGE_TAG> <optional:SERVICE_DNS_ENV_ALIAS_KEY> <optional:ENV_NAME> <optional:SERVICE_DNS_HOSTED_ZONE_NAME> <optional:SERVICE_NAME> <optional:SERVICE_TASK_CONTAINER_PORT> <optional:SERVICE_TASK_MIN_CONTAINERS> <optional:SERVICE_TASK_MAX_CONTAINERS> <optional:SERVICE_AUTOSCALING_TARGET_TASK_CPU_PCT> <optional:STACK_NAME>
```

<br/>

#### Arguments

Required:
- `AWS_CLI_PROFILE_NAME`: (no default) The name of the local AWS CLI profile you made for our AWS project.  

Optional:
- `ENV_NAME`: (default: `dev`) The name of the environment in which the resource will be categorized.  
  - Allowed values can be found in the [template](02-service.yml#L13).  
- `SERVICE_ECR_IMAGE_TAG`: The version or image tag to deploy  
- WIP
