import abc
from cmath import phase
from typing import Dict, List
import yaml
from dacite import from_dict
import json

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame as SP_DATAFRAME
from pyspark.sql.types import *
from pyspark.sql.functions import split, col, explode, lit, monotonically_increasing_id
from pyspark.sql import functions as F
from pyspark.sql import Window 


from sstm_transformation.datamodel import SSTM, TSMTableField

class InstagramBuilder(metaclass=abc.ABCMeta):

    def __init__(self, config_yaml: str, spark: SparkSession) -> None:
        with open(config_yaml, "r") as file:
            self.config : SSTM = from_dict(data=yaml.safe_load(file), data_class=SSTM)
        self.spark = spark
        self.raw_data : Dict = {}
        

    def _get_dtype_mapping(self, data_type):
        d_map = {"string" : StringType(), "date" : DateType(), "int" : IntegerType(), "boolean" : BooleanType(), "float" : DoubleType(), "double" : DecimalType(10,4)}
        return d_map[data_type]

    def _get_truve_org(self, fv_org_id: int) -> int:
        return fv_org_id

    def add_default_columns(self, df: SP_DATAFRAME):
        #df = df.withColumn("date_ingested", F.current_timestamp())
        df = df.withColumn("Client_Org_ID", df["Client_Org_ID"].cast(StringType()))
        return df

    def _read_tsm(self, tsm_table_name: str) -> SP_DATAFRAME:
        # TODO read dependent TSM table from S3. 
        
        # As of now, read from local. Need to remove 
        #contact_df = self.spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/historical_contacts.parquet")
        #return (self.build_peopletypes(contact_df))["CMS_PeopleType"]

        return self.spark.read.parquet("s3://dev-truve-devops-05-databr-bucketetlprocesseddata-h2m2xopoctot/peopletypes")
        #"s3://dev-truve-devops-05-databricks-bucketetlrawdata-wu3m2thgf3o/filevine/6586/contact/historical_contacts.parquet"

    def _get_table_config(self, table_name) -> List[TSMTableField]:
        for table in self.config.tsm:
            if table.name == table_name:
                return table.fields

    def _get_schema_of_table(self, table_name) -> SP_DATAFRAME:
        return None

    def _get_col_name(self, table_fields:List[TSMTableField], tsm_col_name:str) -> TSMTableField:
        for field in table_fields:
            if field.name == tsm_col_name:
                return field
 

    def _load_table_schema(self, table_name):
        with open('transformation/schema/{}.json'.format(table_name.lower())) as f:
            return StructType.fromJson(json.load(f))


    def build_age(self, df: SP_DATAFRAME):
        table_name = "IG_Ages"
        return {table_name : df}

    def build_cities(self, df: SP_DATAFRAME):
        table_name = "IG_Cities"
        return {table_name : df}

    def build_countries(self, df: SP_DATAFRAME):
        table_name = "IG_Countries"
        return {table_name : df}

    def build_dates(self, df: SP_DATAFRAME):
        table_name = "IG_Dates"
        return {table_name : df}

    def build_gender(self, df: SP_DATAFRAME):
        table_name = "IG_Gender"
        return {table_name : df}

    def build_hashtags(self, df: SP_DATAFRAME):
        table_name = "IG_Hashtags"
        return {table_name : df}

    def build_hours(self, df: SP_DATAFRAME):
        table_name = "IG_Hours"
        return {table_name : df}

    def build_locals(self, df: SP_DATAFRAME):
        table_name = "IG_Locales"
        return {table_name : df}

    def build_mediatypes(self, df: SP_DATAFRAME):
        table_name = "IG_MediaTypes"
        return {table_name : df}

    def build_posts(self, df: SP_DATAFRAME):
        table_name = "IG_Posts"
        return {table_name : df}
    

if __name__ == "__main__":
    print("Hi")
    spark = SparkSession.builder.appName('TSMTransformation').getOrCreate()
    