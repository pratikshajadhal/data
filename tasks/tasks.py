
import os
from datetime import datetime
from dotenv import load_dotenv

from filevine.client import FileVineClient
from utils import load_config, get_logger, find_yaml
from tasks.hist_helper import *

logger = get_logger(__name__)
load_dotenv()

# - SUBS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def make_fv_subscription(s3_conf_file_path: str,
                        endpoint_to_subscribe: str):
                        
    # -- Read conf file from s3
    # find_yaml(s3_path=s3_conf_file_path,
    #                 download_path=f"{os.getcwd()}/tasks/src.yaml")


    # -- Read yaml file
    # Since conf file in s3 is deleted, currently we are using base yaml

    # selected_field_config = load_config(file_path="tasks/src.yaml")
    selected_field_config = load_config(file_path="confs/src.yaml")

    # -- Get org_id, user_id from yaml
    org_id = selected_field_config.org_id
    user_id = selected_field_config.user_id

    # -- Make variable for all subscriptions
    subscriptions_events = [
        "Project.Created",
        "Project.PhaseChanged",
        "Project.Updated",
        "Form.Created",
        "Form.Updated",
        "CollectionItem.Created",
        "CollectionItem.Deleted",
        "CollectionItem.Updated"]

    fv_client = FileVineClient(org_id = org_id, user_id = user_id)
    # # To connect webhook 2 steps need to be covered. 
    # # # 1- Get subscription payload(subscription_id). 
    # # # 2- Create webhook connection using subsription payload
    
    # 1-
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sub_name = f"OrgId: {org_id} - Automatic fv-wh integration {now_str}"
    sub_description = f"OrgId: {org_id} -\
                        Automatic filevine webhook integration.\
                        Successfully connected at {now_str}"

                        
    # Payload to create subscriptionId from filevine.
    subscription_id = fv_client.create_subscription(subscriptions_events, sub_description, endpoint_to_subscribe, sub_name)

    logger.info(f"subscription_id:{subscription_id} has been successfully created!")
    return subscription_id


def make_ld_subscription():
    # Currently skipping!.
    pass


# - HISTORICAL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# Skip currently
def run_lead_historical(s3_conf_file_path: str):
    """
    Args:
        s3_conf_file_path (str): yaml location.
        entity_name (str): entity name for historical runs. 
        
    Normally org_id is int in filevine side however there is no organization identifier for leaddocket site. 
    So the unique thing in lead-docket is URL -> https://aliawadlaw.leaddocket.com/api/leads.
    'aliawadlaw' needs to be extracted from this url as an organization identifier.
    """
    # Get data from s3
    conf_path = s3_conf_file_path
    # find_yaml(s3_path=s3_conf_file_path,
    #                         download_path=conf_path)

    # start_statuses_etl(s3_conf_file_path= s3_conf_file_path)
    # start_leadsource_etl(s3_conf_file_path= s3_conf_file_path)
    # start_referrals_etl(s3_conf_file_path= s3_conf_file_path)
    # start_users_etl(s3_conf_file_path= s3_conf_file_path)
    # start_case_type_etl(s3_conf_file_path= s3_conf_file_path)
    
    # start_lead_row_etl(s3_conf_file_path= s3_conf_file_path)
    start_lead_detail_etl(s3_conf_file_path= s3_conf_file_path)

    
def run_fv_historical():
    # TODO:
    pass



def run_social_historical():
    # TODO:
    pass