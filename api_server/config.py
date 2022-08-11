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
class Onboarding(BaseModel):
    org_id: int
    tpa_id: str
    credentials: dict

    class Config:
        schema_extra = {
            "example": {
                "org_id": "Foo",
                "tpa_id": "FILEVINE",
                "credentials":{
                    "api_key": "fvpk_f722dca1-73bb-9095-79fe-0a3069636a3f",
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
                "org_id": "Foo",
                "tpa_id": "FILEVINE",
                }
            }


class TaskStatus(BaseModel):
    truve_id: int 
    tpa_id : str 
    job_result: dict
    error_body: dict = None

    class Config:
        schema_extra = {
            "example": {
                    "truve_id": 123,
                    "tpa_id": "FILEVINE",
                    "job_result":{
                        "status": "success"
                    }
                }
            }

class EtlStatus(BaseModel):
    truve_id: int 
    tpa_id : str 
    job_result: dict
    error_body: dict = None

    class Config:
        schema_extra = {
            "example": {
                    # TODO:
                    "truve_id": 123,
                    "tpa_id": "FILEVINE",
                    "job_result":{
                        "status": "success"
                    }
                }
            }


# @dataclass
# class EtlStatus:
#     truve_id: int 
#     tpa_id : str 
#     pipeline_status: pipeline_statuses
#     fail_data: FailObject = None

# - - -

