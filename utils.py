import json
import logging
import os
from collections import Counter
from datetime import datetime
from itertools import islice
from typing import Optional
from uuid import UUID

import boto3
import botocore
import yaml
from dacite import from_dict

from etl.datamodel import LeadSelectedConfig, SelectedConfig
from models.request import ExecStatus
from models.response import Job

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
#     return load_config("src.yaml")
def get_yaml_of_org(org_id, client='fv'):
    """
        This is a temp function. It will change soon! TODO:
    """
    if client == 'fv':
        return load_config("src.yaml")
    elif client == 'ld':
        return load_lead_config("src-lead.yaml")

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
    logger = logging.getLogger(__name__)

    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handler
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(handler)

    return logger

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def find_yaml(s3_path: str, download_path: str):
    """
        v.0.1: Returns appropriate yaml config file.
        It could be changed over time depending on our architecture. Currently fetching from s3.
    """

    s3_client = None
    server_env = os.environ["SERVER_ENV"]

    if server_env == "LOCAL":
        s3_client = boto3.client(
            's3',
            aws_access_key_id = os.environ["LOCAL_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key = os.environ["LOCAL_AWS_SECRET_ACCESS_KEY"]
        )
    else:
        s3_client = boto3.client('s3')

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

    config = load_config(file_path="src.yaml")
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


def determine_pipeline_status_from_jobs(jobs: list[Job]) -> Optional[ExecStatus]:
    """
    If all no jobs are pending, then:
    - SUCCESS: all the jobs are successful.
    - CANCELLED: there is at least one cancelled job, and the rest succeeded.
    - FAILED: at least one job was failed, regardless of cancelled jobs.

    Else, return None if there are more than one job that are not pending.

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
    ]) is None
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.RUNNING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
    ]) is ExecStatus.RUNNING
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
    ]) is ExecStatus.RUNNING
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING), \
    ]) is None
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.FAILURE),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.CANCELLED), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.PENDING),   \
    ]) is None
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS), \
    ]) is ExecStatus.SUCCESS
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.CANCELLED), \
    ]) is ExecStatus.CANCELLED
    True

    >>> determine_pipeline_status_from_jobs([ \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.SUCCESS),   \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.CANCELLED), \
        Job(uuid=UUID('4d6e2895-e679-472e-ba4c-1067bb120a4e'), updated_at=datetime.now(), status=ExecStatus.FAILURE),   \
    ]) is ExecStatus.FAILURE
    True
    """
    counts = Counter([i.status for i in jobs])
    status: Optional[ExecStatus] = None

    # This means the job has ended, see if all the jobs in this pipeline is finished.
    if counts[ExecStatus.PENDING] == 0:
        # All jobs finished, now decide what should be the pipeline status.
        if counts[ExecStatus.SUCCESS] == len(jobs):
            status = ExecStatus.SUCCESS
        elif counts[ExecStatus.SUCCESS] + counts[ExecStatus.CANCELLED] == len(jobs):
            status = ExecStatus.CANCELLED
        else:
            # No jobs pending, but number of success and
            # failure does not add up, so there is failure.
            status = ExecStatus.FAILURE
    elif counts[ExecStatus.PENDING] == len(jobs) - 1:
        # This means the first job was just started, set pipeline status to RUNNING.
        status = ExecStatus.RUNNING

    # All the cases are handled here, because as long as there is at least one job that is not pending, the pipeline
    # will be active. If there are more than one jobs that are not pending, then the pipeline is already set to running,
    # so we can safely return None, to indicate that the pipeline's status should already have been updated.

    return status
