import abc
from typing import Dict, List
import yaml
from dacite import from_dict
import json

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame as SP_DATAFRAME
from pyspark.sql.types import *
from pyspark.sql.functions import split, col, explode, lit, monotonically_increasing_id
from pyspark.sql import functions as F


from sstm_transformation.datamodel import SSTM, TSMTableField

class TSMBuilder(metaclass=abc.ABCMeta):

    def __init__(self, config_yaml: str, spark: SparkSession) -> None:
        with open(config_yaml, "r") as file:
            self.config : SSTM = from_dict(data=yaml.safe_load(file), data_class=SSTM)
        self.spark = spark
        self.raw_data : Dict = {}

    def _get_truve_org(self, fv_org_id: int) -> int:
        return fv_org_id

    def add_default_columns(self, df: SP_DATAFRAME):
        return df.withColumn("date_ingested", F.current_timestamp())

    def _read_tsm(self, tsm_table_name: str) -> SP_DATAFRAME:
        # TODO read dependent TSM table from S3. 
        
        # As of now, read from local. Need to remove 
        # contact_df = self.spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/historical_contacts.parquet")
        #return self.build_peopletypes(contact_df)

        return self.spark.read.parquet("s3://dev-truve-devops-05-databr-bucketetlprocesseddata-h2m2xopoctot/peopletypes")
        "s3://dev-truve-devops-05-databricks-bucketetlrawdata-wu3m2thgf3o/filevine/6586/contact/historical_contacts.parquet"

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

    def build_peopletypes(self, contact_df:SP_DATAFRAME):
        """
        columns = StructType([StructField('Truve_Org_ID',
                            IntegerType(), True),
                    StructField('Client_Org_ID',
                        IntegerType(), False),
                    StructField('People_Type_ID',
                        IntegerType(), True),
                    StructField('People_Type',
                        StringType(), True),
                    StructField('People_Sub_Type',
                        StringType(), True),
                    StructField('Custom1',
                        StringType(), True),
                    StructField('Custom2',
                        StringType(), True)
                    StructField('Custom3',
                        StringType(), True)])
        """
        table_fields = self._get_table_config("PeopleType")

        #table_schema = self._load_table_schema("PeopleType")
        
        
        people_type_col_name = None
        for field in table_fields:
            if field.name == "People_Type":
                people_type_col_name = field.transform.source_field

        person_type_df = (contact_df.select(people_type_col_name).distinct())
        
        person_type_df = person_type_df.withColumn("People_Type",explode(split(col(people_type_col_name),'\\|'))).drop(people_type_col_name).distinct()
        person_type_df = person_type_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        person_type_df = person_type_df.withColumn('Custom1', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('Custom2', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('Custom3', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('People_Sub_Type', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn("People_Type_Id", monotonically_increasing_id())

        self.add_default_columns(person_type_df)

        return person_type_df

    def build_peoplemaster(self, contact_df:SP_DATAFRAME):
        """
        columns = StructType([StructField('Truve_Org_ID',
                            IntegerType(), True),
                    StructField('Client_Org_ID',
                        IntegerType(), False),
                    StructField('People_ID',
                        IntegerType(), True),
                    StructField('People_Type_ID',
                        IntegerType(), True),
                    StructField('Team_ID',
                        IntegerType(), True),
                    StructField('First_Name',
                        StringType(), True)
                    StructField('Middle_Name',
                        StringType(), True)    
                    StructField('Last_Name',
                        StringType(), True),
                    StructField('Date_of_Birth',
                        DateType(), True),
                    StructField('Gender',
                        StringType(), True),
                    StructField('Custom1',
                        StringType(), True)
                    StructField('Custom2',
                        StringType(), True)
                    StructField('Custom3',
                        StringType(), True)
                        ])
        """
        table_fields = self._get_table_config("PeopleMaster")

        #table_schema = self._load_table_schema("PeopleMaster")

        
        contact_df = contact_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                contact_df = contact_df.withColumn(field.name, contact_df[field.transform.source_field])
            elif not field.transform:
                contact_df = contact_df.withColumn(field.name, lit(None).cast(StringType()))
                
        #Populate people type
        people_type_df = self._read_tsm(tsm_table_name="PeopleType")

        people_type_col_name = self._get_col_name(table_fields=table_fields, tsm_col_name="People_Type_ID")

        contact_type_df = (contact_df.select("People_ID", people_type_col_name.name))
        
        
        contact_type_df = contact_type_df.withColumn("People_Type",explode(split(col(people_type_col_name.name),'\\|'))).select("People_ID", "People_Type")
        contact_type_df.printSchema()
        contact_type_df = contact_type_df.join(people_type_df, on=["People_Type"], how="left").select("People_ID", "People_Type_ID")
        contact_df = contact_df.withColumn('Middle_Name', lit(None).cast(StringType()))
        

        contact_df = contact_df.select("Truve_Org_ID", "People_ID", "First_Name", "Middle_Name", "Last_Name", "Date_of_Birth", "Gender", "Custom1", "Custom2", "Custom3")
        
        self.add_default_columns(contact_df)
        self.add_default_columns(contact_type_df)

        return {"PeopleMaster" : contact_df, "PeopleMaster_PeopleType" : contact_type_df}

    def build_project(self, project_df: SP_DATAFRAME):
        project_df = project_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        table_fields = self._get_table_config("ProjectMaster")

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                project_df = project_df.withColumn(field.name, project_df[field.transform.source_field])
            elif not field.transform:
                project_df = project_df.withColumn(field.name, lit(None).cast(StringType()))

        # TODO Change datatype here
        col_list = ["Truve_Org_ID", "Project_ID", "Project_Type_ID", "Is_Archived", "Incident_Date"]
        project_df = project_df.select("Truve_Org_ID", "Project_ID", "Project_Type_ID", "Is_Archived", "Incident_Date")
        project_df.printSchema()

        self.add_default_columns(project_df)
        return {"ProjectMaster", project_df}

    def build_casesummary(self, casesummary_df: SP_DATAFRAME):
        casesummary_df = casesummary_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        table_fields = self._get_table_config("CaseSummary")

        for field in table_fields:
            if field.transform and field.transform.type == "data":
                casesummary_df = casesummary_df.withColumn(field.name, casesummary_df[field.transform.source_field])
            elif not field.transform:
                casesummary_df = casesummary_df.withColumn(field.name, lit(None).cast(StringType()))

if __name__ == "__main__":
    print("Hi")
    '''
    spark = SparkSession.builder.appName('TSMTransformation').getOrCreate()
    
    contact_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/historical_contacts.parquet")
    #contact_df.printSchema()

    builder = TSMBuilder("sstm.yaml", spark=spark)
    #builder.build_peopletypes(contact_df=contact_df)
    builder.build_peoplemaster(contact_df=contact_df)
    
    project_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/project.parquet")
    project_df.printSchema()
    print(project_df.count())
    
    builder.build_project(project_df)
    '''