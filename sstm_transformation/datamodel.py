from dataclasses import dataclass
from typing import List, Optional

'''
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
'''

TRANSFORM_TYPES = str #Literal["key", "org_id", "data"]
SOURCE_TYPES = str #Literal["internal", "etl"]
DATA_TYPES = str #Literal["int", "string"]

TSM_TABLES = str #Literal["PeopleType", "PeopleMaster"]

@dataclass
class TransformationETL:
    source: str #Literal["internal"]
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
    org_id: str
    tsm: List[TSMTable]
