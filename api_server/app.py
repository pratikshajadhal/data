import uvicorn
import json

from fastapi import FastAPI, Request

from api_server.config import FVWebhookInput
from api_server.helper import handle_wb_input
from etl.helper import get_fv_etl_object
from main import *
from utils import get_logger, get_yaml_of_org
# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 
logger = get_logger(__name__)

APP_NAME = "webhook-listener"
app = FastAPI(
    title = "Data Integration API",
    description = "A simple API that listens webhooks events",
    version = 0.1
)

# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 

@app.get("/")
async def home():
    return {"message": "V1.0"}

@app.get("/fv/{org}/snapshots", tags=["fv_snapshots"])
async def fv_get_snapshot(org, project_type_id:int, entity_type, entity_name):
    logger.debug(f"{org} {project_type_id} {entity_name} {entity_type}")
    org_config = get_yaml_of_org(org)
    etl_object = get_fv_etl_object(org_config, entity_type=entity_type, entity_name=entity_name, project_type_id=project_type_id)
    return {"project_type_id" : project_type_id,
            "data" : etl_object.get_snapshot(project_type_id=project_type_id)}

@app.post("/master_webhook_handler", tags=["fv_webhook_listener"])
async def fv_webhook_handler(request: Request):
    '''
    Sample Payload 
    Project initial event data:  {'Timestamp': 1654733926323, 
                        'Object': 'Project', 
                        'Event': 'PhaseChanged', 
                        'ObjectId': {'ProjectTypeId': 18764, 'PhaseId': 176616}, 
                        'OrgId': 6586, 
                        'ProjectId': 10146521, 
                        'UserId': 48697, 
                        'Other': {'PhaseName': 'Demand Pending'}}

    Form Event data:
    {'Timestamp': 1654741352640, 
    'Object': 'Form', 
    'Event': 'Updated', 
    'ObjectId': {'ProjectTypeId': 18764, 'SectionSelector': 'intake'}, 
    'OrgId': 6586, 
    'ProjectId': 10561086, 
    'UserId': 26712, 
    'Other': {}}

    Meds Event Data


    '''
    event_json = await request.json()

    logger.info(f"Got FV Webhook Request {event_json}")
    
    #Extract Metadata
    entity = event_json["Object"]
    
    if entity == "Project":
        #In case of project webhook, Handling will be different
        
        event_name = event_json["Event"]
        
        if event_name != "PhaseChanged":
            project_type_id = None
            org_id = event_json["OrgId"]
            project_id = event_json["ObjectId"]["ProjectId"]
            entity = event_json["Object"]
            section = "core"
            event_name = event_json["Event"]
            event_time = event_json["Timestamp"]
        else:
            project_type_id = event_json["ObjectId"]["ProjectTypeId"]
            org_id = event_json["OrgId"]
            project_id = event_json["ProjectId"]
            entity = event_json["Object"]
            section = None
            event_name = event_json["Event"]
            event_time = event_json["Timestamp"]
    else:
        project_type_id = event_json["ObjectId"]["ProjectTypeId"]
        org_id = event_json["OrgId"]
        project_id = event_json["ProjectId"]
        entity = event_json["Object"]
        section = event_json["ObjectId"].get("SectionSelector")
        event_name = event_json["Event"]
        event_time = event_json["Timestamp"]

    wh_input = FVWebhookInput(project_type_id=project_type_id,
                org_id=org_id,
                project_id=project_id,
                entity=entity,
                event_name=event_name,
                event_timestamp=event_time,
                user_id=None,
                section=section,
                webhook_body=event_json
                )

    try:
        response = handle_wb_input(wb_input=wh_input)
    except Exception as e:
        raise e
        
    #finally:
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }


@app.post("/lead", tags=["leaddocket-webhook-listener"])
async def listen_lead(request: Request):
    """
        API endpoint to handle webhook incoming request.
        Currently webhook was set for 5 different incomings.
        - LeadEdited
        - LeadCreated
        - LeadStatusChanged
        - Contact Added
        - Opportunity Added.
    """
    incoming_json = await request.json()
    logger.info(f"Got LeadDocket Webhook Request {incoming_json}")

    event_type = incoming_json.get("EventType")

    if event_type == 'Lead Edited' or event_type == 'Lead Created' or event_type == 'Lead Status Changed':
        # #Extract Metadata
        lead_id = incoming_json.get("LeadId")

        # Update Lead Detail
        start_lead_detail_etl(lead_ids=[lead_id])


    elif event_type == 'Contact Added':
        # #Extract Metadata
        contact_id = incoming_json.get("ContactId")

        # Update Contact ETL
        start_lead_contact_etl(contact_ids=[contact_id])

    elif event_type == 'Opportunity Created':
        # #Extract Metadata
        opportunity_id = incoming_json.get("OpportunityId")

        start_opport_etl(opport_ids=[opportunity_id])

    else:
        raise ValueError('Unexpected event_type {}'.format(event_type))
        

    return {
        'statusCode': 200,
        'body': json.dumps('Success')}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, root_path="/")