from etl.collections import CollectionETL
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig, LeadDocketConfig

from etl.lead.core import CoreETL 
from etl.lead.lead_row import LeadRowETL
from etl.lead.lead_detail import LeadDetailETL
from etl.lead.lead_contact import LeadContactETL
from etl.lead.lead_opport import LeadOpportETL
from etl.lead.lead_referrals import LeadReferralsETL
from etl.lead.lead_users import LeadUsersETL

import os
from dotenv import load_dotenv
import uvicorn
from task.tasks import run_fv_historical

load_dotenv()

if __name__ == "__main__":
    #start_form_etl(18764, "intake")    
    #start_collection_etl(18764, "negotiations")
    #start_form_etl(18764, "casesummary")
    #start_contact_etl()
    #start_project_etl()

    # - - - - 

    uvicorn.run("api_server.app:app", host="0.0.0.0", port=int(os.environ["SERVER_PORT"]), reload=True, root_path="/")

    # # Wh subscription for filevine
    # make_fv_subscription(
    #     s3_conf_file_path="s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml", 
    #     endpoint_to_subscribe="http://ec2-3-74-173-122.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     # endpoint_to_subscribe="http://ec2-18-196-103-238.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     )
