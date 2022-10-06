import json
import os
from uuid import UUID

import uvicorn
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

from api_server.config import FVWebhookInput,  FVContactWebhookInput
from api_server.helper import handle_wb_input
from etl.destination import get_postgres
from etl.helper import get_fv_etl_object, get_ld_etl_object
from filevine.client import FileVineClient
from leaddocket.client import LeadDocketClient
from models.request import ExecStatus, JobStatusInfo
from models.response import OK
from service.truve_api import client as truve_client
from tasks.hist_helper import *
from utils import determine_pipeline_status_from_jobs, get_logger, get_yaml_of_org

# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -
logger = get_logger(__name__)

APP_NAME = "webhook-listener"
app = FastAPI(
    title="Data Integration API",
    description="Handles data source webhook events and data source onboarding",
    version=0.1
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


# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -
@app.on_event("startup")
async def loadVersion():
    global serverSourceVersion

    with open('../version', 'r') as f:
        serverSourceVersion = f.read().strip()

    print('\n\n  data-api v%s\n=====================\n\n' % serverSourceVersion, flush=True)


@app.get("/diag/health", status_code=200)
async def home():
    return {
        "status": "OK",
        "version": serverSourceVersion.strip()
    }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - FILEVINE - - - - - - - - -

@app.get("/fv/{org}/snapshots", tags=["filevine"])
async def fv_get_snapshot(org, project_type_id: int, entity_type, entity_name):
    """
        Function to return snapshot of given entity.
        Parameters:
            org: organization_id = 6586
            project_type_id= 18764
            entity_type: Types of entity fv includes
                - Form
                - Collection
                - Projects
                - .

        Request example:
            GET http://127.0.0.1:8000/fv/6586/snapshots?project_type_id=18764&entity_type=form&entity_name=casesummary

        Response example:
            "project_type_id": 18764,
            "data": {
                "courtinfo": null,
                "keydates": null,
                ...}

    """
    logger.debug(f"{org} {project_type_id} {entity_name} {entity_type}")
    org_config = get_yaml_of_org(org)
    etl_object = get_fv_etl_object(org_config, entity_type=entity_type, entity_name=entity_name,
                                   project_type_id=project_type_id)
    return {"project_type_id": project_type_id,
            "data": etl_object.get_snapshot(project_type_id=project_type_id)}


@app.get("/fv/{org}/sections", tags=["filevine"])
async def fv_get_sections(org: int, project_type_id: int):
    """
        Function to return sections(entity names)
        Parameters:
            org: organization_id = 6586
            project_type_id= 18764

        Request example:
            GET http://127.0.0.1:8000/fv/6586/sections?project_type_id=18764
        Response example:
            {
            "project_type_id": 18764,
            "data": [
                {
                    "id": "casesummary",
                    "name": "Case Summary",
                    "isCollection": false
                },
                {
                    "id": "parties",
                    "name": "Service of Process",
                    "isCollection": true
                },
                ...
            }

    """

    logger.debug(f"{org} {project_type_id}")
    org_config = get_yaml_of_org(org)
    fv_client = FileVineClient(org_id=org, user_id=org_config.user_id)
    section_data = fv_client.get_sections(projectTypeId=project_type_id)

    section_data = section_data["items"]
    items = [{"id": section["sectionSelector"], "name": section["name"], "isCollection": section["isCollection"]} for
             section in section_data]

    return {"project_type_id": project_type_id,
            "data": items}


@app.post("/master_webhook_handler", tags=["filevine"])
async def fv_webhook_handler(request: Request):
    '''
    Function to handle webhooks for filevine

    Sample Payload
    Project initial event data:  
    {
        'Timestamp': 1654733926323,
        'Object': 'Project',
        'Event': 'PhaseChanged',
        'ObjectId': {'ProjectTypeId': 18764, 'PhaseId': 176616},
        'OrgId': 6586,
        'ProjectId': 10146521,
        'UserId': 48697,
        'Other': {'PhaseName': 'Demand Pending'}
    }

    Form Event data:
    {
        'Timestamp': 1654741352640,
        'Object': 'Form',
        'Event': 'Updated',
        'ObjectId': {'ProjectTypeId': 18764, 'SectionSelector': 'intake'},
        'OrgId': 6586,
        'ProjectId': 10561086,
        'UserId': 26712,
        'Other': {}
    }

    Meds Event Data

    '''
    event_json = await request.json()
    logger.info(f"Got FV Webhook Request {event_json}")

    # Extract Metadata
    entity = event_json["Object"]

    if entity == "Project":
        # In case of project webhook, Handling will be different
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

    elif entity == "Contact":
        #  {'Timestamp': 1664144392853, 'Object': 'Contact', 'Event': 'Updated', 'ObjectId': {'PersonId': 35633825}, 'OrgId': 6586, 'ProjectId': None, 'UserId': 56907, 'Other': {}}
        #  {'Timestamp': 1664238262647, 'Object': 'Contact', 'Event': 'Updated', 'ObjectId': {'PersonId': 35643917}, 'OrgId': 6586, 'ProjectId': None, 'UserId': 66137, 'Other': {}}
        person_id = event_json["ObjectId"].get("PersonId")
        org_id = event_json.get("OrgId")
        project_id = event_json.get("ProjectId")
        entity = event_json.get("Object")
        event_name = event_json.get("Event")
        event_time = event_json.get("Timestamp")
        user_id = event_json.get("user_id")

        wh_input = FVContactWebhookInput(
            person_id=person_id,
            org_id=org_id,
            event_name=event_name,
            event_timestamp=event_time,
            entity=entity,
            project_id=project_id,
            user_id=user_id,
            webhook_body=event_json
            )

    else:
        project_type_id = event_json["ObjectId"]["ProjectTypeId"]
        org_id = event_json["OrgId"]
        project_id = event_json["ProjectId"]
        entity = event_json["Object"]
        section = event_json["ObjectId"].get("SectionSelector")
        event_name = event_json["Event"]
        event_time = event_json["Timestamp"]

    # Create Input dataclass
    if 'wh_input' not in locals():
        wh_input = FVWebhookInput(
            project_type_id=project_type_id,
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

    # finally:
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - LEADDOCKET - - - - - - - - - 

@app.get("/ld/{org}/snapshots", tags=["leaddocket"])
async def ld_get_snapshot(org, entity_name):
    """
        Function to return snapshot of given entity for leaddocket.
        Parameters:
            org: organization_name = "aliawadlaw". One caveat, organization_id for lead docket is a bit different than filevine.
            entity_name: entity,table name

        Request example:
            GET http://127.0.0.1:8000/ld/aliawadlaw/snapshots?entity_name=leaddetail

        Response example:
            {
            "data": {
                "Id": 10587,
                "Summary": "No contact yet \r\n\r\nMe\r\n\r\nNun\r\n",
                "InjuryInformation": null,
                "Status": "Chase",
                "SubStatus": "Second Attempt",
                "SeverityLevel": "Unlikely Case - No Injuries",
                "Code": null,
                ...
            }

    """
    logger.debug(f"{org} {entity_name}")
    org_config = get_yaml_of_org(org, client='ld')
    etl_object = get_ld_etl_object(org_config, entity_name=entity_name)
    if not etl_object:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")
    return {"data": etl_object.get_snapshot()}


# In lead docket the tables are static hence table names needs to be served manually!.
@app.get("/ld/sections", tags=["leaddocket"])
async def lg_get_sections():
    """
        Function to return entity names-table-names for leaddocket
    """
    table_list = ["statuses", "leadsource", "casetype", "leadrow", "leaddetail", "contact", "opportunities",
                  "referrals", "users"]
    return {"section_names": table_list}


@app.get("/ld/customfields/list", tags=["leaddocket"])
async def lg_get(org_name):
    """
        Function to return customfields list for leaddocket
    """

    # Find yaml based on organization identifier. TODO: Currently ignoring
    logger.debug(f" {org_name}")
    org_config = get_yaml_of_org(org_name, "ld")
    ld_client = LeadDocketClient(org_config.base_url)

    custom_fields = ld_client.get_custom_fields()
    return {
        "status": "success",
        "data": custom_fields
    }


@app.post("/lead_webhook_handler", tags=["leaddocket"])
async def lead_webhook_handler(request: Request, clientId: str):
    """
     Function to handle webhooks for leaddocket

        API endpoint to handle webhook incoming request.
        Currently webhook was set for 5 different incomings.
        - LeadEdited
        - LeadCreated
        - LeadStatusChanged
        - Contact Added
        - Contact Edited
        - Opportunity Added.

    Example:
    {
        "EventType": "Lead Created", "EventTypeId": 1, "EventByUser": "Abraham Patricio", "ContactId": 10721, "ContactFirstName": "ERICK", "ContactMiddleName": null, "ContactLastName": "TIDD", "ContactFullName": "ERICK TIDD", "ContactAddress1": null, "ContactAddress2": null, "ContactCity": null, "ContactCounty": null, "ContactState": "GA", "ContactZip": null, "ContactHomePhone": "", "ContactWorkPhone": "", "ContactMobilePhone": "", "ContactEmail": null, "ContactPreferredContactMethod": null, "ContactBirthdate": null, "ContactDeceased": false, "ContactMinor": false, "ContactGender": null, "ContactLanguage": "English", "ContactCreatedDate": "2022-07-15T02:30:11.483", "ContactCreatedBy": "Abraham Patricio", "ContactCode": null, "ContactTimezone": "Eastern Standard Time", "ContactNotes": null, "LeadId": 10678, "LeadCode": null, "OpportunityId": 2705, "OpportunityName": "Walker/LosDefensores", "OpportunityCreatedDate": "2022-07-15T02:15:11.543", "OpportunityProcessedDate": "2022-07-15T02:30:11.797", "LeadCaseType": "Motor Vehicle Collision - MVC", "LeadCaseTypeCode": "18764", "LeadStatus": "Rejected", "LeadSubstatus": "Not A Case - At Fault", "LeadSeverityLevel": "No Case", "LeadSeverityLevelId": 1, "LeadSummary": "----All posted information----\r\nSentBy : json\r\nDateOfIncident : 12/14/2021\r\nInvoiceId : 74995\r\nInvoicePackageId : 211650\r\nPackageId : 2874\r\nFullName : ERICK TIDD\r\nFirstName : ERICK\r\nLastName : TIDD\r\nHomePhoneNum : 678-770-6899\r\nWorkPhoneNum : 470-699-3335\r\nPrimaryPhoneNum : 678-770-6899\r\nPrimaryPhoneNumType : Cell\r\nOtherPhoneNum1 : 470-699-3335\r\nOtherPhoneNum1Type : Cell\r\nIncidentState : GA\r\nIncidentCity : GAINESVILLE", "LeadInjuryInformation": null, "LeadReferredBy": null, "LeadMarketingSource": "Walker/Los Defensores", "LeadMarketingSourceDetails": null, "ReferringUrl": null, "CurrentUrl": null, "UTM": null, "ClientId": null, "ClickId": null, "Keywords": null, "Campaign": null, "LeadContactSource": "Walker/Los Defensores", "LeadCreatedDate": "2022-07-15T02:15:00", "LastStatusChangeDate": "2022-07-15T02:30:11.56", "LeadIntakeName": "Ali Awad", "LeadIntakeCode": "17316234", "LeadIntakeEmail": "attorney@aliawadlaw.com", "LeadCreatorName": "Abraham Patricio", "LeadCreatorCode": "abraham2", "LeadCreatorEmail": "Abraham@aliawadlaw.com", "Qualified Lead": "No", "Were You At Fault?": "No"
    }

    """
    incoming_json = await request.json()
    event_type = incoming_json["EventType"]
    logger.info(f"Got LeadDocket Webhook Request {event_type}")
    #TODO: Find appropriate yaml file based on clientId(org_name)
    s3_conf_file_path = "confs/src-lead.yaml"

    event_type = incoming_json.get("EventType")
    if event_type == 'Lead Edited' or event_type == 'Lead Created' or event_type == 'Lead Status Changed':
        # Extract Metadata
        lead_id = incoming_json.get("LeadId")
        # Update Lead Detail
        start_lead_detail_etl(s3_conf_file_path=s3_conf_file_path, lead_ids=[lead_id], client_id=clientId)

        # Update lead row
        start_lead_row_etl(s3_conf_file_path=s3_conf_file_path, lead_payload= incoming_json)


    elif event_type == 'Contact Added':
        # #Extract Metadata
        contact_id = incoming_json.get("ContactId")

        # Update Contact ETL
        start_lead_contact_etl(s3_conf_file_path=s3_conf_file_path, contact_ids=[contact_id], client_id=clientId)

    elif event_type == 'Contact Edited':
        contact_id = incoming_json.get("ContactId")

        # Update Contact ETL
        start_lead_contact_etl(s3_conf_file_path=s3_conf_file_path, contact_ids=[contact_id], client_id=clientId)

    elif event_type == 'Opportunity Created':
        # #Extract Metadata
        opportunity_id = incoming_json.get("OpportunityId")

        start_opport_etl(s3_conf_file_path=s3_conf_file_path, opport_ids=[opportunity_id], client_id=clientId)

    else:
        raise ValueError('Unexpected event_type {}'.format(event_type))

    return {
        'statusCode': 200,
        'body': json.dumps('Success')}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - SOCIAL MEDIA and TASKS- - - - - - - - - - 
@app.post("/tasks/add", tags=["tasks"])
async def add_tasks(request: Request):
    """
        Function to add tasks as a background job.
        TODO: This is test func it will be parsed and smth. Plz ignore current function.
    """
    logger.debug(f"Adding task")
    task_json = await request.json()

    from tasks.tasks import run_lead_historical
    # TODO:
    parsed_conf_path = 'confs/src-lead.yaml' # It will parsed from request body.
    run_lead_historical(s3_conf_file_path=parsed_conf_path)
    # task_type = from_dict(data=task_json, data_class=TruveDataTask)

    # logger.debug(task_type)

    return {"status": "success", "message": "Task added successfully"}


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
        - Contact Edited
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


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - PIPELINES - - - - - - - - - -


@app.put(
    "/pipelines/{pipeline_id}/jobs/{job_id}",
    response_model=OK,
    response_model_exclude_none=True,
    tags=["pipeline"],
)
async def update_job_status(pipeline_id: UUID, job_id: UUID, body: JobStatusInfo, request: Request):
    # Temporary auth check solution:
    if os.environ["SERVER_ENV"] not in ('LOCAL', 'TEST') and request.headers.get("Authorization", "Bearer x").replace(
            'Bearer ') != os.environ["DATA_WORKER_INBOUND_AUTH_TOKEN"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

    reason = details = None
    if body.error is not None:
        reason = body.error.reason
        details = body.error.details

    if not get_postgres().set_job_status(body.status, pipeline_id, job_id, reason, details):
        raise HTTPException(status_code=404, detail="job/pipeline not found")

    # TODO: Replay attack: set status to PENDING or if already RUNNING, set to RUNNING again.

    jobs = get_postgres().jobs(pipeline_id)
    pipeline_status = determine_pipeline_status_from_jobs(jobs)
    if pipeline_status is not None:
        # Pipeline status needs to be updated.
        get_postgres().set_pipeline_status(pipeline_id, pipeline_status)
        pipeline = get_postgres().pipeline(pipeline_id)
        # Notify truve-api
        # For now, we only notify success/failure, i.e. after pipeline is complete.
        if pipeline_status in (ExecStatus.SUCCESS, ExecStatus.FAILURE):
            status_str = 'succeeded' if pipeline_status == ExecStatus.SUCCESS else 'failed'
            try:
                http_status, body = await truve_client.send_tpa_pipeline_status(
                    status_str, pipeline.org, pipeline.tpa, pipeline.number)
                if http_status // 100 in (4, 5):
                    logger.error(f"failed to notify truve-api (http: {http_status}) body: {body}")
                    raise HTTPException(status_code=500, detail="unknown error")
            except ClientError as e:
                logger.error("couldn't connect truve-api", e)
                raise HTTPException(status_code=500, detail="unknown error")

    return OK()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ["SERVER_PORT"]), reload=True, root_path="/")
