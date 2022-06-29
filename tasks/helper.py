import boto3
import os
import botocore
from utils import get_logger

logger = get_logger(__name__)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def download_s3_file(s3_path: str, download_path: str):
    s3_client = boto3.client(
        's3',
        aws_access_key_id = os.environ["aws_access_key_id"],
        aws_secret_access_key = os.environ["aws_secret_access_key"]
    )

    # Split s3 path: s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml
    bucket_name, key_name = split_s3_bucket_key(s3_path=s3_path)

    # Download file
    try:
        s3_client.download_file(bucket_name, key_name, download_path)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error("Unable to download yaml file. The object does not exist.")
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