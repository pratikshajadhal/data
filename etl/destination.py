from ctypes import Union
import pandas as pd
import os

from etl.datamodel import RedshiftConfig

class Destination(object):

    def __init__(self, config: RedshiftConfig):
        self.config = config

    def get_config(self) -> RedshiftConfig:
        return {}

    def load_data(self, data_df:pd.DataFrame):
        return 0 

class RedShiftDestination(Destination):

    def initialize_destination(self, table_name) -> RedshiftConfig:
        rs_config = RedshiftConfig(table_name=table_name, 
                    schema_name=os.environ["schema_name"],
                    host=os.environ["host"],
                    port=os.environ["port"],
                    user=os.environ["user"],
                    password=os.environ["password"],
                    s3_bucket=os.environ["s3_bucket"],
                    s3_temp_dir=os.environ["s3_temp_dir"])
        self.config = rs_config

    def load_data(self, data_df:pd.DataFrame):
        import pandas_redshift as pr
        rs_config = self.config
        pr.connect_to_redshift(dbname=rs_config.dbname,
                                host=rs_config.host,
                                port=rs_config.port,
                                user=rs_config.user,
                                password=rs_config.password)

        pr.connect_to_s3(
                        bucket=rs_config.s3_bucket,
                        subdirectory=rs_config.s3_temp_dir)

        # Write the DataFrame to S3 and then to redshift
        pr.pandas_to_redshift(data_frame=data_df, redshift_table_name=rs_config.table_name)
