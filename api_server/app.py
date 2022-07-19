import uvicorn
import json

from fastapi import FastAPI, File, HTTPException, Request
from dacite import from_dict

from api_server.config import FVWebhookInput, TruveDataTask
from api_server.helper import handle_wb_input
from etl.helper import get_fv_etl_object, get_ld_etl_object
from filevine.client import FileVineClient
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

@app.get("/ld/{org}/snapshots", tags=["ld_snapshots"])
async def ld_get_snapshot(org, entity_name):
    logger.debug(f"{org} {entity_name}")
    org_config = get_yaml_of_org(org, client='ld')
    etl_object = get_ld_etl_object(org_config, entity_name=entity_name)
    if not etl_object:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    return {"data" : etl_object.get_snapshot()}

@app.get("/fv/{org}/sections", tags=["fv_sections"])
async def fv_get_sections(org:int, project_type_id:int):
    logger.debug(f"{org} {project_type_id}")
    org_config = get_yaml_of_org(org)
    fv_client = FileVineClient(org_id=org, user_id=org_config.user_id)
    section_data = fv_client.get_sections(projectTypeId=project_type_id)

    section_data = section_data["items"]
    items = [{"id" : section["sectionSelector"], "name": section["name"], "isCollection" : section["isCollection"]} for section in section_data]
    
    return {"project_type_id" : project_type_id,
            "data" : items}

@app.post("/tasks/add", tags=["add_tasks"])
async def add_tasks(request: Request):
    logger.debug(f"Adding task")
    task_json = await request.json()

    task_type = from_dict(data=task_json, data_class=TruveDataTask)

    logger.debug(task_type)

    return {"status" : "success", "message" : "Task added successfully"}

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
async def listen_lead(request: Request, clientId:str):
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
        start_lead_detail_etl(lead_ids=[lead_id], client_id=clientId)


    elif event_type == 'Contact Added':
        # #Extract Metadata
        contact_id = incoming_json.get("ContactId")

        # Update Contact ETL
        start_lead_contact_etl(contact_ids=[contact_id], client_id=clientId)

    elif event_type == 'Opportunity Created':
        # #Extract Metadata
        opportunity_id = incoming_json.get("OpportunityId")

        start_opport_etl(opport_ids=[opportunity_id], client_id=clientId)

    else:
        raise ValueError('Unexpected event_type {}'.format(event_type))
        

    return {
        'statusCode': 200,
        'body': json.dumps('Success')}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, root_path="/")