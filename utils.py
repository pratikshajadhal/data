from itertools import islice
import boto3, botocore
import json
from unicodedata import name
from dacite import from_dict
import logging
import pandas as pd
import os
import yaml
import boto3
import os
import botocore


from etl.datamodel import RedshiftConfig, SelectedConfig, LeadSelectedConfig

standard_dtypes = ["string", "bool", "int", "decimal"]
name_yaml_maps = {
    "statuses":"table_leadstatuses",
    "leadsource":"table_leadsource",
    "casetype":"table_casetype",
    "leadrow":"table_leadrow",
    "leaddetail":"table_leaddetail",
    "contact":"table_contact",
    "opportunities":"table_opport",
    "referrals":"table_referral",
    "users":"table_users",
}

def load_config(file_path: str) -> SelectedConfig:
    """Loads devenv.yaml from the given file path."""
    with open(file_path, "r") as stream:
        data = yaml.safe_load(stream)
        #print(data)
        return from_dict(data=data, data_class=SelectedConfig)

# def get_yaml_of_org(org_id: int) -> SelectedConfig:
#     return load_config("confs/src.yaml")
def get_yaml_of_org(org_id, client='fv'):
    """
        This is a temp function. It will change soon! TODO:
    """
    if client == 'fv':
        return load_config("confs/src.yaml")
    elif client == 'ld':
        return load_lead_config("confs/src-lead.yaml")

def get_config_of_section(selected_config:SelectedConfig, section_name:str, project_type_id:int=None, is_core:bool=False):
    if is_core:
        for core_entity in selected_config.core:
            if core_entity.name == section_name:
                return core_entity

    for project_type in selected_config.projectTypes:
        if project_type.id == project_type_id:
            for section in project_type.sections:
                if section.name == section_name:
                    return section


def get_config_of_lead_section(selected_config:LeadSelectedConfig, section_name:str):
    conf_name = name_yaml_maps[section_name]
    #selected.config.confname equals getattr... 
    return getattr(selected_config, conf_name)

def read_contact_metadata():
    with open("contacts-metadata.json") as f:
        contact_schema = json.loads(f.read())

    contact_map = {}

    for field in contact_schema:
        field_data_type = field["value"]
        contact_map[field["selector"].replace("custom.", "")] = {"type" : field_data_type}

    return contact_map

def transform_source_to_destination(source, destination_map):
    post_processed_contact = {}
    for key, value in source.items():
        if key not in destination_map:
            print(f"{key} not found in contact")
            continue
        field_config = destination_map[key]
        if field_config["type"] == "object":
            field_value = json.dumps(value)
        elif isinstance(value, list):
            field_value = '|'.join(value)
        else:
            field_value = value

        post_processed_contact[key] = field_value
    return post_processed_contact

def get_chunks(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def load_lead_config(file_path:str) -> LeadSelectedConfig:
    with open(file_path, "r") as stream:
        data = yaml.safe_load(stream)
        #print(data)
        return from_dict(data=data, data_class=LeadSelectedConfig)

def get_logger(__name__):
    logging.basicConfig(
        filename="historical_logs",
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=50 # Critical
    )


    logger = logging.getLogger('HistoricalLogs')
    return logger

    # - - - - - - - - - - - - - - - - - - - - - 

    # logger = logging.getLogger(__name__)

    # if len(logger.handlers) > 0:
    #     return logger

    # logger.setLevel(logging.DEBUG)
    
    # # create console handler with a higher log level
    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    
    # # create formatter and add it to the handler
    # formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
    # handler.setFormatter(formatter)
    # # add the handler to the logger
    # logger.addHandler(handler)

    # return logger


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def find_yaml(s3_path: str, download_path: str):
    """
        v.0.1: Returns appropriate yaml config file.
        It could be changed over time depending on our architecture. Currently fetching from s3.
    """

    s3_client = None
    server_env = os.environ["SERVER_ENV"]
    
    # if server_env == "LOCAL":

    #     s3_client = boto3.client(
    #         's3',
    #         aws_access_key_id = os.environ["LOCAL_AWS_ACCESS_KEY_ID"],
    #         aws_secret_access_key = os.environ["LOCAL_AWS_SECRET_ACCESS_KEY"]
    #     )
    # else:
    #     s3_client = boto3.client('s3')

    # Split s3 path: s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml
    bucket_name, key_name = split_s3_bucket_key(s3_path=s3_path)

    # Download file
    try:
        s3_client.download_file(bucket_name, key_name, download_path)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            raise("Unable to download yaml file. The conf file does not exist.")
        else:
            raise

def split_s3_bucket_key(s3_path:str):
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    
    s3_components = s3_path.split('/')
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = '/'.join(s3_components[1:])
    return bucket, s3_key
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":

    config = load_config(file_path="confs/src.yaml")
    print(get_config_of_section(config, section_name="intake", project_type_id=18764))

    #print(config.projectTypes)
    '''
    contact_map = read_contact_metadata()
    with open("contacts.json", "r") as f:
        contact_data = json.loads(f.read())
    contact_list = contact_data["items"]
    record_list = []
    for contact in contact_list:
        post_processed_contact = transform_source_to_destination(contact["orgContact"], contact_map)
        record_list.append(post_processed_contact)

    contact_df = pd.DataFrame(record_list)
    '''