from ctypes import Union
from dataclasses import dataclass
from enum import Enum
import os

@dataclass
class ETLSource:
    name: str
    end_point: str


@dataclass
class RedshiftConfig:
    table_name: str
    schema_name: str
    dbname: str
    host: str
    user: str
    port: str
    password: str
    s3_bucket: str
    s3_temp_dir: str

@dataclass
class ETLDestination:
    name: str
    config: RedshiftConfig

@dataclass
class FileVineConfig:
    org_id:int
    user_id:int

