from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from models.request import ExecStatus, ErrorReason


class OK(BaseModel):
    message: str = "OK"


class Job(BaseModel):
    uuid: UUID
    status: ExecStatus
    updated_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    reason: Optional[ErrorReason]
    details: Optional[str]


class Pipeline(BaseModel):
    uuid: UUID
    org: UUID
    tpa: str
    number: int
    status: ExecStatus
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    updated_at: datetime
