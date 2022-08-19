from dataclasses import dataclass
from typing import Any, Dict, Literal
from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Literal, List, Optional


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
class Onboarding(BaseModel):
    org_id: int
    tpa_id: str
    credentials: dict

    class Config:
        schema_extra = {
            "example": {
                "org_id": 123,
                "tpa_id": "INSTAGRAM",
                "credentials":{
                    "api_key": "foo",
                    "user_id": 31958
                    }
                }
        }


class Notify(BaseModel):
    org_id: int
    tpa_id: str

    class Config:
        schema_extra = {
            "example": {
                "org_id": 123123,
                "tpa_id": "FILEVINE",
                }
            }


class TaskStatus(BaseModel):
    truve_id: int 
    job_identifier : str 
    job_result: dict
    error_body: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                    "truve_id": 1,
                    "job_identifier": "INSTAGRAM_HOURLY_POSTS_PULL",
                    "job_result":{
                        "Status": "SUCCESS"
                    }
                }
            }

# - - - - Update job complete
class pipeline_statusses(str, Enum):
    success='SUCCESS'
    fail='FAILED'

class EtlStatus(BaseModel):
    truve_id: int 
    tpa_id : str 
    pipeline_status: pipeline_statuses
    fail_detail: Optional[dict] = None

    # #TODO: If pipeline status FAILED then fail detail needs to be required. Check how to solve
    # TODO: Might dive detail. But if pipeline_Status fail then fail_detail must be required?
    # @root_validator
    # def validate_date(cls, values):
    #     if values["pipeline_status"] == 'FAILED':
    #         values["some_date"] = values["some_list"][0]
    #     return values


    class Config:
        use_enum_values = True  # <--
        schema_extra = {
            "example": {
                        "truve_id": 123,
                        "tpa_id": "FILEVINE",
                        "pipeline_status": "SUCCESS"
                    }
            }
# - - - - 