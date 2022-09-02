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