from cmath import phase
from ctypes import Union
from dataclasses import asdict, dataclass
from typing import Dict
from numpy import dtype
import pandas as pd
import os
import psycopg2
from dacite import from_dict
import datetime
import logging
        
import boto3
import pandas_redshift as pr
import awswrangler as wr

from utils import get_logger
from etl.datamodel import ColumnDefn, RedshiftConfig

logger = get_logger(__name__)

class ETLDestination(object):

    def __init__(self, **kwargs):
        self.dummy = 1

    def get_config(self) -> Dict:
        return {}

    def load_data(self, data_df:pd.DataFrame, **kwargs):
        return 0 

class S3Destination(ETLDestination):
    def __init__(self, org_id, s3_bucket:str=None):
        self.config = {"org_id" : org_id,
                    "bucket" : s3_bucket or os.environ["AWS_S3_BUCKET_NAME_RAW_DATA"]
                    }

        server_env = os.environ["SERVER_ENV"]

        if server_env == "LOCAL":
            self.s3_session = boto3.Session(aws_access_key_id=os.environ["LOCAL_AWS_ACCESS_KEY_ID"],
                            aws_secret_access_key=os.environ["LOCAL_AWS_SECRET_ACCESS_KEY"])
        else:
            self.s3_session = boto3.Session()

    def get_column_mapper(self):
        column_mapper = {"Text" : "string",
                        "Dropdown" : "string",
                        "Boolean" : "boolean",
                        "PersonLink" : "string",
                        "Date" : "date",
                        "Percent" : "double",
                        "Currency" : "string",
                        "IncidentDate" : "date",
                        "MultiSelectList" : "string",
                        "Header" : "string",
                        "String" : "string",
                        "object" : "struct",
                        "ProjectId" : "int", #Truve Defined
                        "Id" : "string", #Truve Defined
                        "CalculatedCurrency" : "string",
                        "Deadline" : "string",
                        "Instructions" : "string",
                        "StringList" : "string",
                        "PersonList" : "string",
                        "string" : "string",
                        "int" : "int",
                        "bool" : "boolean",
                        "date" : "date",
                        "decimal" : "double"
                        }

        #{'col1': 'timestamp', 'col2': 'bigint', 'col3': 'string'}
        return column_mapper

    def get_key(self, kwargs):
        if kwargs["section"] == "core" and kwargs["entity"] == "contact":
            file_name = "{}.parquet".format(kwargs['project'])
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['entity']}/{file_name}"
        elif kwargs["section"] == "core" and kwargs["entity"] == "project":
            file_name = "{}.parquet".format(kwargs['project'])
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['project_type']}/{kwargs['project']}/project.parquet"
        elif kwargs["section"] == "leaddocket":
            file_name = "{}.parquet".format(kwargs["push_id"])
            s3_key = f"{kwargs['section']}/{kwargs['organization_identifier']}/{kwargs['model_name']}/{file_name}"
        else:
            file_name = "{}.parquet".format(kwargs['project'])
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['project_type']}/{kwargs['project']}/{kwargs['section']}/{kwargs['entity']}.parquet"

        return s3_key

    def save_project_phase(self, s3_key, project_id, phase_name):
        phase_df = pd.DataFrame([{"project_id" : project_id, "phase" : phase_name}])
        
        s3_path = f"s3://{self.config['bucket']}/{s3_key}"
        
        wr.s3.to_parquet(
                df=phase_df,
                path=f"{s3_path}",
                boto3_session=self.s3_session
        )

        logger.info(f"S3 Upload successful for {s3_path}")

    def load_data(self, data_df: pd.DataFrame, **kwargs):

        s3_key = self.get_key(kwargs=kwargs)
        
        logger.info(f"Uploading data to destination in following {s3_key}")

        wr.s3.to_parquet(
                df=data_df,
                path=f"s3://{self.config['bucket']}/{s3_key}",
                boto3_session=self.s3_session,
                dtype=kwargs["dtype"]
        )

        logger.info(f"S3 upload successful for {s3_key}")

        return 0


class RedShiftDestination(ETLDestination):

    def get_default_config(self, **kwargs) -> Dict:
        print(os.environ["AWS_REDSHIFT_CONNECTION_HOST"])
        rs_config = RedshiftConfig(table_name=kwargs["table_name"], 
                    schema_name=os.environ["AWS_REDSHIFT_CONNECTION_SCHEMA_NAME"],
                    host=os.environ["AWS_REDSHIFT_CONNECTION_HOST"],
                    port=os.environ["AWS_REDSHIFT_CONNECTION_PORT"],
                    user=os.environ["AWS_REDSHIFT_CONNECTION_UNAME"],
                    dbname=os.environ["AWS_REDSHIFT_CONNECTION_DBNAME"],
                    password=os.environ["AWS_REDSHIFT_CONNECTION_PWORD"],
                    s3_bucket=os.environ["AWS_S3_BUCKET_NAME_RAW_DATA"],
                    s3_temp_dir=os.environ["AWS_S3_BUCKET_NAME_TEMP_DIR"])
        self.config = rs_config
        return asdict(rs_config)

    def get_column_mapper(self):
        column_mapper = {"string" : "varchar(255)",
                        "object" : "text",
                        "int" : "int",
                        "bool" : "boolean",
                        "date" : "date",
                        "decimal" : "numeric(10,3)"
                        }
        return column_mapper

    def connect_to_redshift(self):
        rs_config : RedshiftConfig = from_dict(dataclass=RedshiftConfig, data=self.config)
        connect = psycopg2.connect(dbname=rs_config.dbname,
                                host=rs_config.host,
                                port=rs_config.port,
                                user=rs_config.user,
                                password=rs_config.password
                                )

        cursor = connect.cursor()
        return cursor, connect

    def create_redshift_table(self, 
                          column_def:list[ColumnDefn],
                          redshift_table_name,
                          column_data_types=None,
                          index=False,
                          append=False,
                          diststyle='even',
                          distkey='',
                          sort_interleaved=False,
                          sortkey='',
                          verbose=True):
        """Create an empty RedShift Table
        schema_json : 
        [{"name" : <col_name>, "data_type" : <data_type>}]
        """
        columns_and_data_type = ', '.join(
            ['{0} {1}'.format(column.name, column.data_type) for column in column_def])

        create_table_query = 'create table {0}.{1} ({2})'.format(
            self.config.schema_name, redshift_table_name, columns_and_data_type)

        print(create_table_query)

        #exit()
        if not distkey:
            # Without a distkey, we can set a diststyle
            if diststyle not in ['even', 'all']:
                raise ValueError("diststyle must be either 'even' or 'all'")
            else:
                create_table_query += ' diststyle {0}'.format(diststyle)
        else:
            # otherwise, override diststyle with distkey
            create_table_query += ' distkey({0})'.format(distkey)
        if len(sortkey) > 0:
            if sort_interleaved:
                create_table_query += ' interleaved'
            create_table_query += ' sortkey({0})'.format(sortkey)
        cursor, connect = self.connect_to_redshift()
        cursor.execute('drop table if exists {0}'.format(redshift_table_name))
        cursor.execute(create_table_query)
        connect.commit()

    def load_data(self, data_df:pd.DataFrame, **kwrags):
        rs_config : RedshiftConfig = from_dict(dataclass=RedshiftConfig, data=self.config)
        
        pr.connect_to_redshift(dbname=rs_config.dbname,
                                host=rs_config.host,
                                port=rs_config.port,
                                user=rs_config.user,
                                password=rs_config.password)

        server_env = os.environ["SERVER_ENV"]
        if server_env == "LOCAL":
            pr.connect_to_s3(
                    bucket=rs_config.s3_bucket,
                    subdirectory=rs_config.s3_temp_dir,
                    aws_access_key_id=os.environ["LOCAL_AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=os.environ["LOCAL_AWS_SECRET_ACCESS_KEY"]
            )
        else:
            # Fetch credentials from task role
            credentials = self.s3_session.get_credentials()

            # Credentials are refreshable, so accessing your access key / secret key
            # separately can lead to a race condition. Use this to get an actual matched
            # set.
            credentials = credentials.get_frozen_credentials()
            access_key = credentials.access_key
            secret_key = credentials.secret_key
            
            pr.connect_to_s3(
                    bucket=rs_config.s3_bucket,
                    subdirectory=rs_config.s3_temp_dir,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
            )

        # Write the DataFrame to S3 and then to redshift
        pr.pandas_to_redshift(data_frame=data_df, redshift_table_name=rs_config.table_name)
