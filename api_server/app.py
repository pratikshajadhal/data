import uvicorn
import json

from fastapi import FastAPI, Request

from .config import FVWebhookInput
from .helper import handle_wb_input
# - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - -  - - - - - 

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


    '''
    event_json = await request.json()
    
    #Extract Metadata
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
                section=section
                )

    try:
        response = handle_wb_input(wb_input=wh_input)
    except Exception as e:
        raise e
        
    finally:
        return {
            'statusCode': 200,
            'body': json.dumps('Success')
        }


if __name__ == "__main__":
    uvicorn.run("api_server.app:app", host="0.0.0.0", port=8000, reload=True, root_path="/")