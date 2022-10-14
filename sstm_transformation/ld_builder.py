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

class LDBuilder(metaclass=abc.ABCMeta):

    def __init__(self, config_yaml: str, spark: SparkSession) -> None:
        with open(config_yaml, "r") as file:
            self.config : SSTM = from_dict(data=yaml.safe_load(file), data_class=SSTM)
        self.spark = spark
        self.raw_data : Dict = {}

    def transform(self, df, table_name):
        df = df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        df = df.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)
        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                df = df.withColumn(field.name, df[field.transform.source_field])
            elif not field.transform:
                df = df.withColumn(field.name, lit(None).cast(StringType()))
            
        
        # df = self.add_default_columns(df)
        col_list = [field.name for field in table_fields]
        
        df = df.select(*col_list)

        for field in table_fields:
            dtype = self._get_dtype_mapping(field.data_type)
            df = df.withColumn(field.name, df[field.name].cast(dtype))

        df.show(n=100)

        return df
        

    def _get_dtype_mapping(self, data_type):
        d_map = {
            "string": StringType(),
            "date": DateType(),
            "int": IntegerType(),
            "timestamp": TimestampType(),
            "boolean": BooleanType(),
            "float": DoubleType(),
            "double": DecimalType(10,4)
        }
        return d_map[data_type]

    def _get_truve_org(self, fv_org_id: str) -> int:
        return 6586

    
    def _get_client_org(self, fv_org_id: str) -> int:
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
    
    def build_contact(self, df: SP_DATAFRAME):
        table_name = "CRM_Contacts"
        df = self.transform(df, table_name)
        df.show(100)

        return {table_name : df}

    def build_leaddetail(self, df: SP_DATAFRAME):
        table_name = "CRM_LeadDetail"
        df = df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        df = df.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                df = df.withColumn(field.name, df[field.transform.source_field])
            elif not field.transform:
                df = df.withColumn(field.name, lit(None).cast(StringType()))


        df = self.add_default_columns(df)
        col_list = [field.name for field in table_fields]
        
        df = df.select(*col_list)

        df.show(n=100)
        

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            df = df.withColumn(field.name, df[field.name].cast(cls))

        return {table_name : df}

    def build_leadraw(self, df: SP_DATAFRAME):
        table_name = "CRM_LeadRow"
        df = df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        df = df.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                df = df.withColumn(field.name, df[field.transform.source_field])
            elif not field.transform:
                df = df.withColumn(field.name, lit(None).cast(StringType()))


        df = self.add_default_columns(df)
        col_list = [field.name for field in table_fields]
        
        df = df.select(*col_list)

        df.show(n=100)
        

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            df = df.withColumn(field.name, df[field.name].cast(cls))

        return {table_name : df}

    def build_leadsource(self, df: SP_DATAFRAME):
        table_name = "CRM_LeadSource"
        df = df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        df = df.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                df = df.withColumn(field.name, df[field.transform.source_field])
            elif not field.transform:
                df = df.withColumn(field.name, lit(None).cast(StringType()))


        df = self.add_default_columns(df)
        col_list = [field.name for field in table_fields]
        
        df = df.select(*col_list)

        df.show(n=100)
        

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            df = df.withColumn(field.name, df[field.name].cast(cls))

        return {table_name : df}

    def build_casetype(self, df: SP_DATAFRAME):
        table_name = "CRM_CaseTypes"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_opportunities(self, df: SP_DATAFRAME):
        table_name = "CRM_Opportunities"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_referrals(self, df: SP_DATAFRAME):
        table_name = "CRM_Referrals"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_statuses(self, df: SP_DATAFRAME):
        table_name = "CRM_Status"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_status_changes(self, df: SP_DATAFRAME):
        table_name = "CRM_StatusChanges"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_practice_type(self, df: SP_DATAFRAME):
        table_name = "CRM_PracticeTypes"
        df = self.transform(df=df, table_name=table_name)
        return {table_name : df}

    def build_users(self, df: SP_DATAFRAME):
        table_name = "CRM_Users"
        df = self.transform(df=df, table_name=table_name)
        df = df.withColumn("Full_Name", F.concat_ws(' ', df.First_Name, df.Last_Name))
        df.show(100)

        return {table_name : df}


if __name__ == "__main__":
    print("Hi")
    spark = SparkSession.builder.appName('TSMTransformation').getOrCreate()
    builder = LDBuilder("ld_sstm.yaml", spark=spark)

    ld_users_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\users\12.parquet")
    ld_users_df = builder.build_statuses(df=ld_users_df)
    (ld_users_df["LD_Statuses"]).printSchema()
    
    '''
    ld_contact_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_contact.parquet")
    ld_contact_df = builder.build_contact(df=ld_contact_df)
    (ld_contact_df["LD_Contact"]).printSchema()
    '''

    '''
    ld_leaddetail_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_leaddetail.parquet")
    ld_leaddetail_df = builder.build_leaddetail(df=ld_leaddetail_df)
    (ld_leaddetail_df["LD_LeadDetail"]).printSchema()
    '''

    '''
    ld_leadraw_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_leadrow.parquet")
    ld_leadraw_df = builder.build_leadraw(df=ld_leadraw_df)
    (ld_leadraw_df["LD_LeadRow"]).printSchema()
    '''

    '''
    ld_leadsource_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_leadsource.parquet")
    ld_leadsource_df = builder.build_leadsource(df=ld_leadsource_df)
    (ld_leadsource_df["LD_LeadSource"]).printSchema()
    '''

    '''
    ld_casetype_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_casetype.parquet")
    ld_casetype_df = builder.build_casetype(df=ld_casetype_df)
    (ld_casetype_df["LD_CaseType"]).printSchema()
    '''

    '''
    ld_opport_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_opportunities.parquet")
    ld_opport_df = builder.build_opportunities(df=ld_opport_df)
    (ld_opport_df["LD_Opportunities"]).printSchema()
    '''

    '''
    ld_referrals_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_referrals.parquet")
    ld_referrals_df = builder.build_referrals(df=ld_referrals_df)
    (ld_referrals_df["LD_Referrals"]).printSchema()
    '''

    '''
    ld_statuses_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/ld_statuses.parquet")
    ld_statuses_df = builder.build_statuses(df=ld_statuses_df)
    (ld_statuses_df["LD_Statuses"]).printSchema()
    '''
    #bulk_LeadSource

