from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from models.request import ExecStatus, ErrorReason

#TODO:
class Status(BaseModel):
    latest_pipeline_number: int
    latest_pipeline_status: ExecStatus
    reason: Optional[ErrorReason]
    details: Optional[str]

class ErrorData(BaseModel):
    error_reason_id: int or None
    error_reason_status: dict or None