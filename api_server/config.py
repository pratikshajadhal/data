from dataclasses import dataclass
from typing import Dict, Literal

EVENT_TYPES = ["PhaseChanged", "Created", "Updated", "Deleted"]
ENTITY_TYPES = ["Project", "Form", "CollectionItem"]
SECTION_TYPES = ["intake", "casesummary", "meds", "negotiations"]

source_type = Literal["FILEVINE", "LEADDOCKET"]
task_type = Literal["HISTORICAL_LOAD", "SUBSCRIPTION"]

@dataclass
class FVWebhookInput:
    project_type_id:int
    org_id:int
    event_name:str
    event_timestamp:str
    entity:str
    project_id:int
    section:str
    user_id:int
    webhook_body:Dict

@dataclass
class FVContactWebhookInput:
    person_id: int
    org_id:int
    event_name:str
    event_timestamp:str
    entity:str
    project_id:int
    user_id:int
    webhook_body:Dict

@dataclass
class TruveDataTask:
    source: source_type
    task_type: task_type
    task_params: Dict