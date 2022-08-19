import os
import requests
import uvicorn
import json
import uvicorn

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from fastapi import FastAPI, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, status
from fastapi import FastAPI, HTTPException, Request
from dacite import from_dict

from api_server.config import FVWebhookInput,  TaskStatus, EtlStatus, Notify, Onboarding
from api_server.helper import onboard_fv, onboard_ld, onboard_social, update_redshift_pipeline_status, update_redshift_job_status
from etl.destination import S3Destination, RedShiftDestination
from task.hist_helper import *
from utils import get_logger, get_yaml_of_org
from api_server.exceptions import  ValidationErr, AuthErr
from fastapi.responses import JSONResponse
from api_server.exceptions import  ValidationErr, AuthErr
from api_server.config import Onboarding



# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 

logger = get_logger(__name__)

APP_NAME = "DATA API"
description = """

## Actions
Truve API will be able to:
* **Create new TPA integration onboarding**.
* **Notify onboarding mapping populated** (_Prod table updating phase is not implemented yet_).

Worker will be able to:
* **Update job complete** (_Prod table updating phase is not implemented yet_) 

Databricks or GLUE be able to:
* **Update Pipeline complete** (_Prod table updating phase is not implemented yet_)
"""

tags_metadata = [
    {
        "name": "TPA",
        "externalDocs": {
            "description": "TPA docs",
            "url": "https://www.notion.so/truveai/Data-Source-TPA-Onboarding-b00a2ed5c4a24f87a019cd7403f1bf9b",
        },
    },
]

app = FastAPI(
    title=APP_NAME,
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata
)

# CORS config (TODO: handle through env var)
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse({"message": "Unknown error", "code": 500, "detail":str(exc)}, status_code=500)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse({"message": "Bad request", "code": 422, "detail":str(exc)}, status_code=422)

@app.exception_handler(ValidationErr) 
async def validation_exception_handler(request: Request, exc: ValidationErr):
    return exc.response()

@app.exception_handler(AuthErr) 
async def validation_exception_handler(request: Request, exc: AuthErr):
    return exc.response()

# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 

@app.on_event("startup")
async def loadVersion():
    global serverSourceVersion

    with open('version', 'r') as f:
        serverSourceVersion = f.read().strip()

    print('\n\n  data-api v%s\n=====================\n\n' % serverSourceVersion, flush=True)

@app.get("/")
async def home():
    return {"message": "V1.0"}

@app.get("/diag/health", status_code=200)
async def home():
    return {
        "status": "OK",
        "version": serverSourceVersion.strip()
    }
@app.post("/tpa/test", tags=["TPA"])
async def test(name: str):
    pass

# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 

# ------------------- ------------------- TPA ------------------- -------------------
@app.post("/tpa/onboard", tags=["TPA"]) 
async def create_integration_onboarding(onboard: Onboarding):
    # TODO: Needs to be private and only accesible to truve-api

    TPA_CUSTOM_SCHEMAS = ("FILEVINE", "LEADDOCKET")
    TPA_WITHOUT_CUSTOM_SCHEMAS = ("INSTAGRAM", "FACEBOOK")

    # Essantial configs and ids
    org_id = onboard.org_id,
    creds = onboard.credentials
    logger.info(f"Onboarding for TPA: {onboard.tpa_id}, Org:{onboard.org_id} started!")
    
    if onboard.tpa_id == 'FILEVINE':

        message, groom, project_type_id = onboard_fv(onboard.org_id, onboard.credentials)
        data = {
                "project_type_id": project_type_id,
                "entities": groom
                }
    elif onboard.tpa_id == 'LEADDOCKET':
        message, data= onboard_ld()
    elif onboard.tpa_id == 'INSTAGRAM':
        message, data = onboard_social()
    elif onboard.tpa_id == 'test':
        print(3 / 0)


    return {
            "message": message,
            "data": data
    }


@app.post("/tpa/notify", tags=["TPA"]) 
async def notify_mapping(notify: Notify):
    logger.debug(f"Tpa notify")
    rs = RedShiftDestination()

    # -- Check data statuses from Truve API. 4th step  Get integration statuses
    # Get request to Truve API
    URL = "truve-test.com"
    try:
        # TODO:
        r = requests.get(url = URL)
        data_status = r["data"]
    except:
        import random
        my_bet = ["PENDING", "FAILED", "SUCCESS"]
        data_status = (random.choice(my_bet))

    options = {'FAILED' :"onboarding failure", 'PENDING':f"pipeline not ready"}
    if data_status == 'SUCCESS':
        # TODO: Trigger pipeline
        # Update redshift table ?
        return {"message": "Success, pipeline triggered"}

    return {"message": (f"SUCESS, {options[data_status]}" + f" (data_status is {data_status})")}


@app.post("/task/status", tags=["TPA"])
async def update_job_complete(task_status: TaskStatus):
    # Burası sadece update etcek abi sanıırm???
    # TODO: Needs to be private and only accesible to truve-api
    # This endpoint get request and update status of tasks. Will be called by workers.
    logger.info(f"Truve_id: {task_status.truve_id}, job_identifier: {task_status.job_identifier}")
    status_mapper = {
        "PENDING": 1,
        "RUNNING": 2,
        "SUCCESS": 3,
        "FAILURE": 4
    }
    status_id = status_mapper[task_status.job_result["Status"]]
    
    update_redshift_job_status(task_status.truve_id, task_status.job_identifier, status_id)
    return {"message": "Success, job updated"}


@app.post("/pipeline/status", tags=["TPA"])
async def update_etl_pipeline_complete(etl_status: EtlStatus):
    # TODO: Needs to be private and only accesible to Databricks
    # Once all jobs are being completed, Pipeline statuss will be completed.
    status_mapper = {
        "SUCCESS": 3,
        "FAILED": 4
    }
    status_id = status_mapper[etl_status.pipeline_status]

    update_redshift_pipeline_status(etl_status.truve_id, etl_status.tpa_id, status_id)
    return {"message": "Success, Valid request received"}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - FILEVINE - - - - - - - - - 

# @app.get("/fv/{org}/snapshots", tags=["filevine"])
# async def fv_get_snapshot(org, project_type_id:int, entity_type, entity_name):
#     """
#         Function to return snapshot of given entity.
#         Parameters:
#             org: organization_id = 6586
#             project_type_id= 18764
#             entity_type: Types of entity fv includes
#                 - Form
#                 - Collection
#                 - Projects
#                 - .

#         Request example:
#             GET http://127.0.0.1:8000/fv/6586/snapshots?project_type_id=18764&entity_type=form&entity_name=casesummary

#         Response example:
#             "project_type_id": 18764,
#             "data": {
#                 "courtinfo": null,
#                 "keydates": null,
#                 ...}

#     """
#     logger.debug(f"{org} {project_type_id} {entity_name} {entity_type}")
#     org_config = get_yaml_of_org(org)
#     etl_object = get_fv_etl_object(org_config, entity_type=entity_type, entity_name=entity_name, project_type_id=project_type_id)
#     return {"project_type_id" : project_type_id,
#             "data" : etl_object.get_snapshot(project_type_id=project_type_id)}


# @app.get("/fv/{org}/sections", tags=["filevine"])
# async def fv_get_sections(org:int, project_type_id:int):
#     """
#         Function to return sections(entity names)
#         Parameters:
#             org: organization_id = 6586
#             project_type_id= 18764

#         Request example:
#             GET http://127.0.0.1:8000/fv/6586/sections?project_type_id=18764
#         Response example:
#             {
#             "project_type_id": 18764,
#             "data": [
#                 {
#                     "id": "casesummary",
#                     "name": "Case Summary",
#                     "isCollection": false
#                 },
#                 {
#                     "id": "parties",
#                     "name": "Service of Process",
#                     "isCollection": true
#                 },
#                 ...
#             }

#     """
    
#     logger.debug(f"{org} {project_type_id}")
#     org_config = get_yaml_of_org(org)
#     fv_client = FileVineClient(org_id=org, user_id=org_config.user_id)
#     section_data = fv_client.get_sections(projectTypeId=project_type_id)

#     section_data = section_data["items"]
#     items = [{"id" : section["sectionSelector"], "name": section["name"], "isCollection" : section["isCollection"]} for section in section_data]
    
#     return {"project_type_id" : project_type_id,
#             "data" : items}


# @app.post("/master_webhook_handler", tags=["filevine"])
# async def fv_webhook_handler(request: Request):
#     '''
#     Function to handle webhooks for filevine

#     Sample Payload 
#     Project initial event data:  {'Timestamp': 1654733926323, 
#                         'Object': 'Project', 
#                         'Event': 'PhaseChanged', 
#                         'ObjectId': {'ProjectTypeId': 18764, 'PhaseId': 176616}, 
#                         'OrgId': 6586, 
#                         'ProjectId': 10146521, 
#                         'UserId': 48697, 
#                         'Other': {'PhaseName': 'Demand Pending'}}

#     Form Event data:
#     {'Timestamp': 1654741352640, 
#     'Object': 'Form', 
#     'Event': 'Updated', 
#     'ObjectId': {'ProjectTypeId': 18764, 'SectionSelector': 'intake'}, 
#     'OrgId': 6586, 
#     'ProjectId': 10561086, 
#     'UserId': 26712, 
#     'Other': {}}

#     Meds Event Data

#     '''
#     event_json = await request.json()

#     logger.info(f"Got FV Webhook Request {event_json}")
    
#     #Extract Metadata
#     entity = event_json["Object"]
    
#     if entity == "Project":
#         #In case of project webhook, Handling will be different
        
#         event_name = event_json["Event"]
        
#         if event_name != "PhaseChanged":
#             project_type_id = None
#             org_id = event_json["OrgId"]
#             project_id = event_json["ObjectId"]["ProjectId"]
#             entity = event_json["Object"]
#             section = "core"
#             event_name = event_json["Event"]
#             event_time = event_json["Timestamp"]
#         else:
#             project_type_id = event_json["ObjectId"]["ProjectTypeId"]
#             org_id = event_json["OrgId"]
#             project_id = event_json["ProjectId"]
#             entity = event_json["Object"]
#             section = None
#             event_name = event_json["Event"]
#             event_time = event_json["Timestamp"]
#     else:
#         project_type_id = event_json["ObjectId"]["ProjectTypeId"]
#         org_id = event_json["OrgId"]
#         project_id = event_json["ProjectId"]
#         entity = event_json["Object"]
#         section = event_json["ObjectId"].get("SectionSelector")
#         event_name = event_json["Event"]
#         event_time = event_json["Timestamp"]

#     wh_input = FVWebhookInput(project_type_id=project_type_id,
#                 org_id=org_id,
#                 project_id=project_id,
#                 entity=entity,
#                 event_name=event_name,
#                 event_timestamp=event_time,
#                 user_id=None,
#                 section=section,
#                 webhook_body=event_json
#                 )

#     try:
#         response = handle_wb_input(wb_input=wh_input)
#     except Exception as e:
#         raise e
        
#     #finally:
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Success')
#     }


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - LEADDOCKET - - - - - - - - - 

# @app.get("/ld/{org}/snapshots", tags=["leaddocket"])
# async def ld_get_snapshot(org, entity_name):
#     """
#         Function to return snapshot of given entity for leaddocket.
#         Parameters:
#             org: organization_name = "aliawadlaw". One caveat, organization_id for lead docket is a bit different than filevine.
#             entity_name: entity,table name

#         Request example:
#             GET http://127.0.0.1:8000/ld/aliawadlaw/snapshots?entity_name=leaddetail

#         Response example:
#             {
#             "data": {
#                 "Id": 10587,
#                 "Summary": "No contact yet \r\n\r\nMe\r\n\r\nNun\r\n",
#                 "InjuryInformation": null,
#                 "Status": "Chase",
#                 "SubStatus": "Second Attempt",
#                 "SeverityLevel": "Unlikely Case - No Injuries",
#                 "Code": null,
#                 ...
#             }

#     """
#     logger.debug(f"{org} {entity_name}")
#     org_config = get_yaml_of_org(org, client='ld')
#     etl_object = get_ld_etl_object(org_config, entity_name=entity_name)
#     if not etl_object:
#         raise HTTPException(status_code=422, detail="Unprocessable Entity")
#     return {"data" : etl_object.get_snapshot()}


# # In lead docket the tables are static hence table names needs to be served manually!.
# @app.get("/ld/sections", tags=["leaddocket"])
# async def lg_get_sections():
#     """
#         Function to return entity names-table-names for leaddocket
#     """
#     table_list = ["statuses","leadsource","casetype", "leadrow","leaddetail","contact","opportunities","referrals","users"]
#     return {"section_names" : table_list}


# @app.get("/ld/customfields/list", tags=["leaddocket"])
# async def lg_get(org_name):
#     """
#         Function to return customfields list for leaddocket
#     """

#     # Find yaml based on organization identifier. TODO: Currently ignoring
#     logger.debug(f" {org_name}")
#     org_config = get_yaml_of_org(org_name, "ld")
#     ld_client = LeadDocketClient(org_config.base_url)

#     custom_fields = ld_client.get_custom_fields()
#     return {
#         "status":"success",
#         "data": custom_fields
#     }


# @app.post("/lead_webhook_handler", tags=["leaddocket"])
# async def lead_webhook_handler(request: Request, clientId:str):
#     """
#      Function to handle webhooks for filevine

#         API endpoint to handle webhook incoming request.
#         Currently webhook was set for 5 different incomings.
#         - LeadEdited
#         - LeadCreated
#         - LeadStatusChanged
#         - Contact Added
#         - Opportunity Added.
#     """
#     incoming_json = await request.json()
#     logger.info(f"Got LeadDocket Webhook Request {incoming_json}")
#     #TODO: Find appropriate yaml file based on clientId(org_name)
#     s3_conf_file_path = "src-lead.yaml" 

#     event_type = incoming_json.get("EventType")
#     if event_type == 'Lead Edited' or event_type == 'Lead Created' or event_type == 'Lead Status Changed':
#         # #Extract Metadata
#         lead_id = incoming_json.get("LeadId")

#         # Update Lead Detail
#         start_lead_detail_etl(s3_conf_file_path= s3_conf_file_path, lead_ids=[lead_id], client_id=clientId)


#     elif event_type == 'Contact Added':
#         # #Extract Metadata
#         contact_id = incoming_json.get("ContactId")

#         # Update Contact ETL
#         start_lead_contact_etl(s3_conf_file_path= s3_conf_file_path, contact_ids=[contact_id], client_id=clientId)

#     elif event_type == 'Opportunity Created':
#         # #Extract Metadata
#         opportunity_id = incoming_json.get("OpportunityId")

#         start_opport_etl(s3_conf_file_path= s3_conf_file_path, opport_ids=[opportunity_id], client_id=clientId)

#     else:
#         raise ValueError('Unexpected event_type {}'.format(event_type))
        

#     return {
#         'statusCode': 200,
#         'body': json.dumps('Success')}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - SOCIAL MEDIA and TASKS- - - - - - - - - - 
# @app.post("/tasks/add", tags=["tasks"])
# async def add_tasks(request: Request):
#     """
#         Function to add tasks as a background job.
#         TODO: This is test func it will be parsed and smth. Plz ignore current function.
#     """
#     # Step by step

#     logger.debug(f"Adding task")
#     task_json = await request.json()
#     task_object = from_dict(data=task_json, data_class=TruveDataTask)

#     # Find conf file. based on org_id or org_name. Skipping currently
#     org_id = task_object.task_params["org_id"]

#     # What will be the content of this message?
#     # # SQS---
#     queue_name = 'my-test-queue'
#     message = {
#             "FUNC_PARAMS": {
#                 "source": task_object.source,
#                 "type": task_object.task_type
#             },
#             "org_name": org_id,
#             "task_state": "DELIVERED"
#             }
#     send_message_to_queue(queue_name, message)
#     return {"status" : "success", "message" : "Task added to queue successfully"}



# x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x x 

# TODO:It will be TASK. PLZ DO NOT DELETE!
# @app.post("/social/{integration_name}/integrations", tags=["tasks"])
# async def social_run(integration_name:str, org_id:str, dimension:str):
#     logger.debug(f"Social media {integration_name}, {org_id}, {dimension}")

#     return {"status" : "success", "message" : "Task added successfully"}


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
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ["SERVER_PORT"]), reload=True, root_path="/")
