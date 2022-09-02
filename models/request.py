"""This file consists of the body parameter models (subclasses pydantic. BaseModel)"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ExecStatus(str, Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    CANCELLED = 'CANCELLED'
    FAILURE = 'FAILURE'


class ErrorReason(str, Enum):
    GENERAL = 'GENERAL'
    AUTH = 'AUTH'
    SCHEMA_CFG = 'SCHEMA_CFG'


class JobStatusInfo(BaseModel):
    # TODO: If Tyler approves, we can use Enums with pydantic for verification.
    status: ExecStatus = Field(default=ExecStatus.PENDING, description="Job's last status, can be any of "
                                                                       "{PENDING, RUNNING, SUCCESS, CANCELLED, "
                                                                       "FAILURE}.")

    # TODO: Upgrading to 3.10 would allow us to write `object | None`
    # reason: Optional[object] = Field(default=None, description="Reason for the error (if any).")
