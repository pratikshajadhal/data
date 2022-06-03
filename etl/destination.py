from ctypes import Union
from dataclasses import asdict, dataclass
from typing import Dict
from numpy import dtype
import pandas as pd
import os
import psycopg2
from dacite import from_dict
import datetime
        
import boto3
import pandas_redshift as pr
import awswrangler as wr

from etl.datamodel import ColumnDefn, RedshiftConfig

class ETLDestination(object):

    def __init__(self, **kwargs):
        self.dummy = 1

    def get_config(self) -> Dict:
        return {}

    def load_data(self, data_df:pd.DataFrame, **kwargs):
        return 0 

class S3Destination(ETLDestination):
    def __init__(self, org_id:int, s3_bucket:str=None):
        self.config = {"org_id" : org_id,
                    "bucket" : s3_bucket or os.environ["s3_bucket"]
                    }
        self.s3_session = boto3.Session(aws_access_key_id=os.environ["aws_access_key_id"],
                        aws_secret_access_key=os.environ["aws_secret_access_key"])

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
        
    def load_data(self, data_df: pd.DataFrame, **kwargs):
        file_name = "{}.parquet".format(kwargs['project'])
        
        if kwargs["section"] == "core":
            s3_key = f"{self.config['org_id']}/{kwargs['entity']}/{file_name}"
        else:
            s3_key = f"{self.config['org_id']}/{kwargs['project_type']}/{kwargs['section']}/{kwargs['entity']}/{file_name}"

        print(kwargs['dtype'])
        #data_df.to_csv("sample.csv")

        
        wr.s3.to_parquet(
                df=data_df,
                path=f"s3://{self.config['bucket']}/{s3_key}",
                boto3_session=self.s3_session,
                dtype=kwargs["dtype"]
        )

class RedShiftDestination(ETLDestination):

    def get_default_config(self, **kwargs) -> Dict:
        print(os.environ["host"])
        rs_config = RedshiftConfig(table_name=kwargs["table_name"], 
                    schema_name=os.environ["schema_name"],
                    host=os.environ["host"],
                    port=os.environ["port"],
                    user=os.environ["user"],
                    dbname=os.environ["dbname"],
                    password=os.environ["password"],
                    s3_bucket=os.environ["s3_bucket"],
                    s3_temp_dir=os.environ["s3_temp_dir"])
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

        pr.connect_to_s3(
                        bucket=rs_config.s3_bucket,
                        subdirectory=rs_config.s3_temp_dir,
                        aws_access_key_id=os.environ["aws_access_key_id"],
                        aws_secret_access_key=os.environ["aws_secret_access_key"]
                        )

        # Write the DataFrame to S3 and then to redshift
        pr.pandas_to_redshift(data_frame=data_df, redshift_table_name=rs_config.table_name)
