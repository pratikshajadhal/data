from __future__ import annotations

import os
from abc import ABC, abstractmethod
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import urlopen
from uuid import UUID

from aiohttp import request

from models.request import JobError
from service.aws import get_stack_output


class AbstractClient(ABC):

    @abstractmethod
    async def send_tpa_pipeline_status(self, status: str, org_uuid: UUID, tpa_identifier: str,
                                       pipeline_number: int, error: JobError | None = None) -> (int, object):
        ...


class Mock(AbstractClient):
    def __init__(self, *args, **kwargs):
        ...

    async def send_tpa_pipeline_status(self, status: str, org_uuid: UUID, tpa_identifier: str,
                                       pipeline_number: int, error: JobError | None = None) -> (int, object):
        return 200, None


class Live(AbstractClient):
    def __init__(self, base_url: str, route_tpa_events: str, static_auth_token: str):
        self.__tpa_events: str = urljoin(base_url, route_tpa_events)
        self.__headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {static_auth_token}",
        }

    async def send_tpa_pipeline_status(self, status: str, org_uuid: UUID, tpa_identifier: str,
                                       pipeline_number: int, error: JobError | None = None) -> (int, object):
        """ Right now, status can only be one of {failed, succeeded}. """
        payload = {
            "pipelineNumber": pipeline_number,
            "status": status,
        }
        if status == 'failed':
            payload.update({
                "error": error,
            })
        async with request("POST", self.__tpa_events.format(**{
            # Example path template: /organizations/{orgId}/tpas/{tpaIdentifier}/events
            "orgId": str(org_uuid),
            "tpaIdentifier": tpa_identifier,
        }), headers=self.__headers, json=payload) as resp:
            return resp.status, await resp.json()


ClientClass = Live

mock = os.environ["TRUVE_API_USE_MOCK"]
api_base_url = os.environ["TRUVE_API_BASE_URL"]

if os.environ["SERVER_ENV"] == "TEST" or mock.lower() in ('y', '1', 't', 'true', 'on', 'yes'):
    ClientClass = Mock
elif os.environ["SERVER_ENV"] != "LOCAL":
    # Use cloudformation stacks query in DEV/PROD
    health_check = get_stack_output(os.environ["TRUVE_API_STACK_NAME"])
    try:
        if urlopen(health_check).status != 200:
            raise Exception("truve-api is unhealthy. Hint: check stack name.")
    except URLError:
        Exception("couldn't connect to truve-api")
    api_base_url = health_check.split('/health')[0]

api_auth_token = os.environ["TRUVE_API_OUTBOUND_AUTH_TOKEN"]
api_route_tpa_events = os.environ["TRUVE_API_ROUTE_TPA_EVENTS"]

client: AbstractClient = ClientClass(api_base_url, api_route_tpa_events, api_auth_token)

del Live, Mock, AbstractClient, ClientClass
