
import os
from datetime import datetime
from dotenv import load_dotenv

from filevine.client import FileVineClient
from utils import load_config, get_logger, find_yaml

logger = get_logger(__name__)
load_dotenv()

# - SUBS - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def make_fv_subscription(s3_conf_file_path: str,
                        endpoint_to_subscribe: str):
    # -- Read conf file from s3
    find_yaml(s3_path=s3_conf_file_path,
                    download_path=f"{os.getcwd()}/tasks/src.yaml")

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
    payload= fv_client.generate_subscription_payload(subscriptions_events, sub_description, endpoint_to_subscribe, sub_name)

    try:
        subscription_id = fv_client.make_webhook_connection(payload)
    except Exception as e:
        logger.warning("(-) Something went wrong in webhook connection")
        logger.error(e)

    logger.info(f"subscription_id:{subscription_id} has been successfully created!")
    return subscription_id


def make_ld_subscription():
    # Currently skipping!.
    pass


# - HISTORICAL - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
