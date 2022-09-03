from __future__ import annotations

import os

import boto3

kw = {}
if os.environ["SERVER_ENV"] == 'LOCAL':
    kw.update(
        profile_name=os.environ["LOCAL_AWS_PROFILE_NAME"],
    )

cf = boto3.Session(**kw).client('cloudformation')


def get_stack_output(stack_name: str, output_key: str = 'HealthCheckEndpoint') -> str | None:
    """Return the host output from CloudFormation.

    >>> get_stack_output('dev-truve-api-02-service')
    'https://dev-74fa314bb-api.truve.ai/health'

    """
    try:
        stack = cf.describe_stacks(StackName=stack_name)['Stacks'][0]
        for i in stack['Outputs']:
            if i['OutputKey'] == output_key:
                return i['OutputValue']
    except IndexError:
        return None
