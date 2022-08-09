from dataclasses import dataclass
from typing import Any, Dict, Literal
from pydantic import BaseModel

EVENT_TYPES = ["PhaseChanged", "Created", "Updated", "Deleted"]
ENTITY_TYPES = ["Project", "Form", "CollectionItem"]
SECTION_TYPES = ["intake", "casesummary", "meds", "negotiations"]

source_type = Literal["FILEVINE", "LEADDOCKET", "SOCIAL"]
task_type = Literal["HISTORICAL_LOAD", "SUBSCRIPTION"]
pipeline_statuses = Literal["SUCCESS", "FAILED"]
fail_reasons = Literal["auth", "mapping", "data"]


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
class TruveDataTask:
    source: source_type
    task_type: task_type
    task_params: Dict
    

# - - TPA
@dataclass
class Creds:
    api_key: str
    user_id: int

@dataclass
class OnboardingObject:
    org_id: int # TODO: CAUTION, it must be string for lead docket please check.
    tpa_id : str 
    credentials: Creds

@dataclass
class MappingObject:
    tpa_id : int
    cred_key: str

# - - -

@dataclass
class TaskStatus:
    truve_id: int 
    tpa_id : int 
    job_result: dict
    error_body: dict = None

@dataclass
class FailObject:
    fail_reason_prefix: fail_reasons
    fail_error: Dict = None

@dataclass
class EtlStatus:
    truve_id: int 
    tpa_id : int 
    pipeline_status: pipeline_statuses
    fail_data: FailObject = None

# - - -

