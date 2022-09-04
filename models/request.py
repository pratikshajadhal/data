"""This file consists of the body parameter models (subclasses pydantic. BaseModel)"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


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


class JobError(BaseModel):
    reason: ErrorReason = Field(..., description="Enum")
    details: Optional[object] = Field(..., description="An object about the detail of failure. "
                                                       "Might include a `description` string attribute.")


class JobStatusInfo(BaseModel):
    status: ExecStatus
    error: Optional[JobError] = Field(default=None, description="Required if the job failed.")

    @validator('error', always=True)
    def error_provided_for_failed_status(cls, v, values):
        if v is None and values['status'] == ExecStatus.FAILURE:
            raise ValueError(f'must provide a JobError object for status FAILURE')
