from dataclasses import dataclass
from typing import List, Literal, Optional


TRANSFORM_TYPES = Literal["key", "org_id", "data"]
SOURCE_TYPES = Literal["internal", "etl"]
DATA_TYPES = Literal["int", "string"]

TSM_TABLES = Literal["PeopleType"]

@dataclass
class TransformationETL:
    source: Literal["internal"]
    type: str    

@dataclass
class TSMFieldTransform:
    source: SOURCE_TYPES
    type: TRANSFORM_TYPES
    source_entity_type: Optional[str]
    source_entity_name: Optional[str]
    source_field: Optional[str]

@dataclass
class TSMTableField:
    name: str
    data_type: DATA_TYPES
    transform: Optional[TSMFieldTransform]

@dataclass
class TSMTable:
    name: TSM_TABLES
    fields: List[TSMTableField]

@dataclass
class SSTM:
    org_id: int
    tsm: List[TSMTable]
