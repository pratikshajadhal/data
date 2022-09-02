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
