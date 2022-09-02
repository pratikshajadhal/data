from __future__ import annotations

import os
from urllib.parse import urljoin

import aiohttp

from models.response import Pipeline

api_base_url: str | None = None
api_route_tpa_events: str | None = None

api_auth_token: str = os.environ["TRUVE_API_OUTBOUND_AUTH_TOKEN"]

if os.environ["SERVER_ENV"] in "LOCAL":
    api_base_url = os.environ["TRUVE_API_BASE_URL"]
    api_route_tpa_events = os.environ["TRUVE_API_ROUTE_TPA_EVENTS"]
else:
    # TODO: ask CloudFormation for values
    pass


async def send_tpa_event(pipeline: Pipeline) -> (int, object):
    print(api_route_tpa_events)
    route = api_route_tpa_events.format(**{
        "orgId": pipeline.org,
        "tpaIdentifier": pipeline.tpa,
    })
    async with aiohttp.ClientSession() as s:
        async with s.post(urljoin(api_base_url, route), headers={
            "Authentication": f"Bearer {api_auth_token}",
        }, json={
            "pipelineNumber": pipeline.number,
            "status": pipeline.status.value,
        }) as resp:
            return resp.status, resp.json()
