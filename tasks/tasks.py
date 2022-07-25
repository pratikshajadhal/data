
import os
from datetime import datetime
from dotenv import load_dotenv

from filevine.client import FileVineClient
from utils import find_yaml
from utils import load_config, get_logger

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
# Skip currently
def run_lead_historical(organization_identifier_url: str, entity_name: str, s3_conf_file_path: str):
    #TODO
    pass
#     """
#     Args:
#         organization_identifier_url (str): Static organization url needs to be filled from client. 
#         entity_name (str): entity name for historical runs. 
#         s3_conf_file_path (str): yaml location.
        
#     Normally org_id is int in filevine side however there is no organization identifier for leaddocket site. 
#     So the unique thing in lead-docket is URL -> https://aliawadlaw.leaddocket.com/api/leads.
#     'aliawadlaw' needs to be extracted from this url as an organization identifier.
#     """
#     # Get data from s3
#     conf_path = f"{os.getcwd()}/tasks/lead-src.yaml"
#     find_yaml(s3_path=s3_conf_file_path,
#                             download_path=conf_path)

#     org_id = (organization_identifier_url.split(".")[0]).split("//")[1]
#     logger.info(f"{entity_name} historical's running!")
#     if entity_name == 'statuses':
#         start_statuses_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'lead_source':
#         start_leadsource_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'case_type':
#         start_case_type_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'lead_row':
#         start_lead_row_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'lead_detail':
#         start_lead_detail_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'contact':
#         start_lead_contact_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'opport':
#         start_opport_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'referrals':
#         start_referrals_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     elif entity_name == 'users':
#         start_users_etl(org_id=org_id, base_url=organization_identifier_url, conf_file_path=conf_path)
#     else:
#         logger.warning("Entity type is unknown")
#         raise ValueError('Unexpected Entity {}'.format(entity_name))

    
def run_fv_historical():
    # TODO:
    pass



def run_social_historical():
    # TODO:
    pass