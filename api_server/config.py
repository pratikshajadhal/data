from dataclasses import dataclass
from typing import Dict

EVENT_TYPES = ["PhaseChanged", "Created", "Updated", "Deleted"]
ENTITY_TYPES = ["Project", "Form", "CollectionItem"]
SECTION_TYPES = ["intake", "casesummary", "meds", "negotiations"]

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
