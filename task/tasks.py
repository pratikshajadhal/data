
# Ugly way to import parent folders, Please fix it Mert.#TODO:
import sys
import os
sys.path.append('..')

import argparse
import fire
from datetime import datetime
from dotenv import load_dotenv

from api_server.config import TruveDataTask
from filevine.client import FileVineClient
from utils import load_config, get_logger, find_yaml
from task.hist_helper import *

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
    selected_field_config = load_config(file_path="src.yaml")

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
def run_lead_historical(s3_conf_file_path: str):
    """
    Args:
        s3_conf_file_path (str): yaml location.
        entity_name (str): entity name for historical runs. 
        
    Normally org_id is int in filevine side however there is no organization identifier for leaddocket site. 
    So the unique thing in lead-docket is URL -> https://aliawadlaw.leaddocket.com/api/leads.
    'aliawadlaw' needs to be extracted from this url as an organization identifier.
    """
    logger.info(f"(H) Historical Lead started!")
    # Get data from s3 #TODO:
    conf_path = s3_conf_file_path
    # find_yaml(s3_path=s3_conf_file_path,
    #                         download_path=conf_path)

    start_statuses_etl(s3_conf_file_path= s3_conf_file_path)
    start_leadsource_etl(s3_conf_file_path= s3_conf_file_path)
    start_case_type_etl(s3_conf_file_path= s3_conf_file_path)
    start_lead_row_etl(s3_conf_file_path= s3_conf_file_path)
    start_lead_detail_etl(s3_conf_file_path= s3_conf_file_path)
    start_lead_contact_etl(s3_conf_file_path= s3_conf_file_path)
    start_opport_etl(s3_conf_file_path= s3_conf_file_path)
    start_referrals_etl(s3_conf_file_path= s3_conf_file_path)
    start_users_etl(s3_conf_file_path= s3_conf_file_path)

    
def run_fv_historical(conf_file: str):
    """
    Args:
        s3_conf_file_path (str): yaml location.
        
    """
    logger.info(f"(H) Historical Filevine started!")
     # Get data from s3 # TODO:
    conf_path = conf_file
    # find_yaml(s3_path=s3_conf_file_path,
    #                         download_path=conf_path
    # start_contact_etl(conf_path)
    start_project_etl(conf_path)
    start_form_etl(conf_path)    
    start_collection_etl(conf_path)
    start_form_etl(conf_path)
    # start_form_etl(18764, "intake")    
    # start_collection_etl(18764, "negotiations")
    # start_form_etl(18764, "casesummary")



def run_social_historical():
    # TODO:
    pass

def create_cli(source:str, type:str) -> str:
  return f'python {os.getcwd()}/task/tasks.py --source={source} --task_type={type}'

def handle_task(incoming_data:TruveDataTask):
    # Parse incoming data

    # Creates appropriate python command line code to run task.py

    command = create_cli(incoming_data.source, incoming_data.task_type)


    # os.system(command)
    # If you want it could be ran.

if __name__ == '__main__':
    # Arg parser
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--source", required=True, help="Please enter the type. Filevine, leaddocket, instagram etc.")
    arg_parser.add_argument("--task_type", required=True, help="Please enter the task_name. historical, wh_subscription etc.")
    args = arg_parser.parse_args()

    task_run_option = args.source
    type_run_option = args.task_type

    if task_run_option == 'LEADDOCKET':
        if  type_run_option == 'HISTORICAL_LOAD':
            print("(+) LEADDOCKET historical ")
            # run_lead_historical()
            # call handle_task
        elif type_run_option == 'SUBSCRIPTION':
            print(" (+) LEADDOCKET subscription")
    elif task_run_option == 'FILEVINE':
        if  type_run_option == 'HISTORICAL_LOAD':
            print("(+) FILEVINE historical ")
            # run_lead_historical()
            # call handle_task
        elif type_run_option == 'SUBSCRIPTION':
            print("(+) FILEVINE subscription")
    elif task_run_option == 'SOCIAL':
        if  type_run_option == 'HISTORICAL_LOAD':
            print("(+) SOCIAL historical ")
            # run_lead_historical()
            # call handle_task
        elif type_run_option == 'SUBSCRIPTION':
            # TODO:
            print("(+) SOCIAL subscription")
    else:
        raise ValueError("Unknown task source")
            

