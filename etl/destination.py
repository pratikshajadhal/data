import json
from pprint import pprint
from uuid import UUID
from datetime import datetime

from cmath import phase
from ctypes import Union
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional
from numpy import dtype
import pandas as pd
import os
import psycopg2
from dacite import from_dict
import logging

import boto3
import pandas_redshift as pr
import awswrangler as wr

from models.request import ExecStatus, ErrorReason
from models.response import Job, Pipeline
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
                    "bucket" : s3_bucket or os.environ["AWS_S3_BUCKET_NAME_ETL_RAW_DATA"]
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
            #file_name = "{}.parquet".format(kwargs['project'])
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['entity']}/historical_contacts.parquet"
        elif kwargs["section"] == "core" and kwargs["entity"] == "project":
            file_name = "{}.parquet".format(kwargs['project'])
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['project_type']}/{kwargs['project']}/project.parquet"
        elif kwargs["section"] == "core" and kwargs["entity"] == "projecttype":
            s3_key = f"filevine/{self.config['org_id']}/{kwargs['entity']}/projecttypes.parquet"
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

        #Temp code
        #data_df.to_parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/projecttypes.parquet")
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
                    s3_bucket=os.environ["AWS_S3_BUCKET_NAME_ETL_RAW_DATA"],
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


class PostgresDestination(ETLDestination):
    def __init__(self, **kwargs):
        # Establishing the connection
        super().__init__(**kwargs)
        self.connect = psycopg2.connect(
            database=os.environ["LOCAL_POSTGRES_DB"],
            user=os.environ["LOCAL_POSTGRES_USER"],
            password=os.environ["LOCAL_POSTGRES_PASS"],
            host=os.environ["LOCAL_POSTGRES_HOST"],
            port='5432'
        )
        self.connect.autocommit = True
        self.cursor = self.connect.cursor()

    def set_job_status(
            self,
            status: ExecStatus,
            pipeline_uuid: UUID,
            job_uuid: UUID,
            error_reason: Optional[ErrorReason] = None,
            error_details: Optional[object] = None) -> bool:
        """Update started_at, ended_at, error_details, status_id, error_reason_id, updated_at depending on status."""
        with self.connect as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    UPDATE jobs j
                    SET started_at      = CASE WHEN %(status)s = 'RUNNING' THEN now() ELSE started_at END,
                        ended_at        = CASE WHEN %(status)s <> 'RUNNING' THEN now() END,
                        error_details   = %(details)s, -- No need for using CASE on this one because 'null' is NULL.
                        status_id       = (SELECT es.id
                                           FROM exec_statuses es
                                           WHERE es.status_name = %(status)s),
                        error_reason_id = CASE WHEN %(reason)s IS NOT NULL
                                                   THEN (SELECT id 
                                                         FROM error_reasons
                                                         WHERE reason_name = %(status)s) END,
                        updated_at      = now()
                    WHERE j.uuid = %(job)s
                      AND j.pipeline_id = (SELECT pipeline_id FROM pipelines WHERE uuid = %(pipeline)s);
                """, ({
                    'status': status.value,
                    'job': str(job_uuid),
                    'pipeline': str(pipeline_uuid),
                    'details': json.dumps(error_details),
                    'reason': error_reason,
                }))

                # Returns False if job/pipeline not found
                return curs.rowcount == 1

    def job(self, pipeline_uuid: UUID, job_uuid: UUID) -> Optional[Job]:
        rv = [i for i in self.jobs(pipeline_uuid) if i.uuid == job_uuid]
        return rv[0] if len(rv) else None

    def jobs(self, pipeline_uuid: UUID) -> list[Job]:
        with self.connect as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    SELECT j.uuid,
                           (SELECT es.status_name FROM exec_statuses es WHERE es.id = j.status_id),
                           j.updated_at, j.started_at, j.ended_at,
                           (SELECT er.reason_name FROM error_reasons er WHERE er.id = j.error_reason_id),
                           j.error_details
                    FROM jobs j JOIN pipelines p ON j.pipeline_id = p.id
                    WHERE p.uuid = %s;
                """, (str(pipeline_uuid),))
                res = [Job(
                    uuid=i[0],
                    status=i[1],
                    updated_at=i[2],
                    started_at=i[3],
                    ended_at=i[4],
                    reason=i[5],
                    details=i[6],
                ) for i in curs.fetchall()]
        return res

    def set_pipeline_status(self, pipeline_uuid: UUID, status: ExecStatus):
        with self.connect as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    UPDATE pipelines p
                    SET started_at      = CASE WHEN %(status)s = 'RUNNING' THEN now() ELSE started_at END,
                        ended_at        = CASE WHEN %(status)s <> 'RUNNING' THEN now() END,
                        status_id       = (SELECT es.id
                                           FROM exec_statuses es
                                           WHERE es.status_name = %(status)s),
                        updated_at      = now()
                    WHERE p.uuid = %(pipeline)s;
                """, ({
                    'status': status.value,
                    'pipeline': str(pipeline_uuid),
                }))

                # Returns False if pipeline not found
                return curs.rowcount == 1

    def pipeline(self, pipeline_uuid: UUID) -> Pipeline:
        with self.connect as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    SELECT uuid,
                           org_uuid,
                           tpa_identifier,
                           pipeline_number,
                           started_at,
                           ended_at,
                           updated_at,
                           (SELECT es.status_name FROM exec_statuses es WHERE es.id = status_id)
                    FROM pipelines
                    WHERE uuid = %s;
                """, (str(pipeline_uuid),))
                p = curs.fetchone()

        return Pipeline(
            uuid=p[0],
            org=p[1],
            tpa=p[2],
            number=p[3],
            started_at=p[4],
            ended_at=p[5],
            updated_at=p[6],
            status=p[7],
        )


# DO NOT use __pg_dest directly. Use get_postgres() instead.
__pg_dest: Optional[PostgresDestination] = None


def get_postgres():
    global __pg_dest
    if __pg_dest is None:
        __pg_dest = PostgresDestination()
    return __pg_dest


def reset_db():
    if os.environ['SERVER_ENV'] == 'TEST':
        if __pg_dest is None:
            get_postgres()
        with __pg_dest.cursor as curs:
            curs.execute("DELETE FROM jobs;")
            curs.execute("DELETE FROM pipelines;")
            with open('../sql/postgres/pipelines/insert_test_data.sql') as f:
                curs.execute(f.read())
