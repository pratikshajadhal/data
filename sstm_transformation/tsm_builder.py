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

class TSMBuilder(metaclass=abc.ABCMeta):

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
        df = df.withColumn("Truve_Org_ID", df["Truve_Org_ID"].cast(IntegerType()))
        
        return df

    def _read_tsm(self, tsm_table_name: str) -> SP_DATAFRAME:
        # TODO read dependent TSM table from S3. 
        
        # As of now, read from local. Need to remove 
        #contact_df = self.spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/historical_contacts.parquet")
        # return (self.build_peopletypes(contact_df))["CMS_PeopleType"]

        return self.spark.read.parquet("s3://dev-truve-devops-05-databr-bucketetlprocesseddata-h2m2xopoctot/cms_peopletype")
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
        table_name = "CMS_PeopleType"
        table_fields = self._get_table_config(table_name)

        people_type_col_name = None
        for field in table_fields:
            if field.name == "People_Type":
                people_type_col_name = field.transform.source_field

        person_type_df = (contact_df.select(people_type_col_name).distinct())
        
        person_type_df = person_type_df.withColumn("People_Type",explode(split(col(people_type_col_name),'\\|'))).drop(people_type_col_name).distinct()
        person_type_df = person_type_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        person_type_df = person_type_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        
        person_type_df = person_type_df.withColumn('Custom1', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('Custom2', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('Custom3', lit(None).cast(StringType()))
        person_type_df = person_type_df.withColumn('People_Sub_Type', lit(None).cast(StringType()))

        window = Window.orderBy(col("People_Type"))
        person_type_df = person_type_df.withColumn("People_Type_Id", F.row_number().over(window))
        
        person_type_df = self.add_default_columns(person_type_df)


        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            person_type_df = person_type_df.withColumn(field.name, person_type_df[field.name].cast(cls))


        return {table_name : person_type_df}

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
        table_fields = self._get_table_config("CMS_People")

        #table_schema = self._load_table_schema("PeopleMaster")

        
        contact_df = contact_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        contact_df = contact_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        
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
        people_type_df.printSchema()
        contact_type_df = contact_type_df.join(people_type_df, on=["People_Type"], how="left").select("People_ID", "People_Type_ID")
        contact_df = contact_df.withColumn('Middle_Name', lit(None).cast(StringType()))
        
        #ContactDF DataType 
        contact_df = contact_df.withColumn("People_ID", contact_df["People_ID"].cast(IntegerType()))
        contact_df = contact_df.withColumn("Date_of_Birth", contact_df["Date_of_Birth"].cast(DateType()))

        contact_type_df = contact_type_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        contact_type_df = contact_type_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        contact_type_df = contact_type_df.withColumn("People_ID", contact_type_df["People_ID"].cast(IntegerType()))
        contact_type_df = contact_type_df.withColumn("People_Type_ID", contact_type_df["People_Type_ID"].cast(IntegerType()))
        
        
        contact_df = contact_df.select("Truve_Org_ID", "Client_Org_ID", "People_ID", "First_Name", "Middle_Name", "Last_Name", "Date_of_Birth", "Gender", "Custom1", "Custom2", "Custom3")
        
        
        contact_df = self.add_default_columns(contact_df)
        contact_type_df = self.add_default_columns(contact_type_df)
        
        contact_df = contact_df.withColumn("Team_ID", lit(1).cast(IntegerType()))

        for field in self._get_table_config("CMS_People"):
            if field.name == "People_Type_ID":
                continue
            cls = self._get_dtype_mapping(field.data_type)
            contact_df = contact_df.withColumn(field.name, contact_df[field.name].cast(cls))
        
        
        #for field in self._get_table_config("CMS_PeoplePeopleTypes"):
        #    cls = self._get_dtype_mapping(field.data_type)
        #    contact_type_df = contact_type_df.withColumn(field.name, contact_type_df[field.name].cast(cls))
        
        return {"CMS_People" : contact_df, "CMS_PeoplePeopleTypes" : contact_type_df}

    def build_casemaster(self, project_df: SP_DATAFRAME):
        table_name = "CMS_Cases"
        project_df = project_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        project_df = project_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                project_df = project_df.withColumn(field.name, project_df[field.transform.source_field])
            elif not field.transform:
                project_df = project_df.withColumn(field.name, lit(None).cast(StringType()))

        project_df.select("Practice_Type_ID").show()
        
        project_df = project_df.withColumn("Practice_Type_ID", F.regexp_replace(col("Practice_Type_ID"), "'", '"'))\
                    .withColumn("Practice_Type_ID", F.regexp_replace(col("Practice_Type_ID"), "None", 'null'))
        
        project_df = project_df.withColumn("Practice_Type_ID", F.from_json(col("Practice_Type_ID"), MapType(StringType(), StringType()), {"mode" : "FAILFAST"}))
        
        project_df = project_df.withColumn("Practice_Type_ID", project_df.Practice_Type_ID.getItem("native"))
        
        project_df = project_df.withColumn("Case_ID", project_df["Case_ID"].cast(IntegerType()))

        project_df = project_df.withColumn("Practice_Type_ID", project_df["Practice_Type_ID"].cast(IntegerType()))
        project_df = project_df.withColumn("Is_Archived", project_df["Is_Archived"].cast(BooleanType()))
        project_df = project_df.withColumn("Incident_Date", project_df["Incident_Date"].cast(DateType()))
        
        
        # TODO Change datatype here
        col_list = ["Truve_Org_ID", "Client_Org_ID", "Case_ID", "Practice_Type_ID", "Is_Archived", "Incident_Date"]
        project_df = project_df.select("Truve_Org_ID", "Client_Org_ID", "Case_ID", "Practice_Type_ID", "Is_Archived", "Incident_Date")
        project_df.printSchema()

        self.add_default_columns(project_df)

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            project_df = project_df.withColumn(field.name, project_df[field.name].cast(cls))

        project_df.show(10)
        return {table_name : project_df}

    def build_practicetypes(self, projecttype_df: SP_DATAFRAME):
        table_name = "CMS_PracticeTypes"
        projecttype_df = projecttype_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        projecttype_df = projecttype_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                projecttype_df = projecttype_df.withColumn(field.name, projecttype_df[field.transform.source_field])
            elif not field.transform:
                projecttype_df = projecttype_df.withColumn(field.name, lit(None).cast(StringType()))

        projecttype_df = projecttype_df.withColumn("Practice_Type_ID", projecttype_df["Practice_Type_ID"].cast(IntegerType()))
        # TODO Change datatype here
        col_list = ["Truve_Org_ID", "Client_Org_ID", "Practice_Type_ID", "Practice_Type_Name", "Custom1", "Custom2", "Custom3"]
        projecttype_df = projecttype_df.select(["Truve_Org_ID", "Client_Org_ID", "Practice_Type_ID", "Practice_Type_Name", "Custom1", "Custom2", "Custom3"])
        projecttype_df.printSchema()

        projecttype_df = self.add_default_columns(projecttype_df)

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            projecttype_df = projecttype_df.withColumn(field.name, projecttype_df[field.name].cast(cls))

        return {table_name: projecttype_df}

    def build_phasemaster(self, projecttypedf: SP_DATAFRAME):
        #explode projecttype to get Phases 
        table_name = "CMS_Phases"
        from pyspark.sql.functions import explode
        import pyspark.sql.functions as F

        raw_phases_df = projecttypedf.select(projecttypedf.projectTypeId, explode(projecttypedf.phases))
        raw_phases_df = raw_phases_df.select(raw_phases_df.projectTypeId, F.col("col.name"), F.col("col.phaseId"), F.col("col.isPermanent"))
        
        raw_phases_df = raw_phases_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        raw_phases_df = raw_phases_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)).cast(StringType()))
        
        table_fields = self._get_table_config(table_name)

        for field in table_fields:
            if field.transform and field.transform.type == "data":
                raw_phases_df = raw_phases_df.withColumn(field.name, raw_phases_df[field.transform.source_field])
            elif not field.transform:
                raw_phases_df = raw_phases_df.withColumn(field.name, lit(None).cast(StringType()))

        col_list = [field.name for field in table_fields]
        
        phase_master_df = raw_phases_df.select(*col_list)

        phase_master_df.show(n=100)

        phase_master_df = phase_master_df.withColumn("Phase_ID", phase_master_df["Phase_ID"].cast(IntegerType()))
        phase_master_df = phase_master_df.withColumn("Practice_Type_ID", phase_master_df["Practice_Type_ID"].cast(IntegerType()))
        
        phase_master_df = self.add_default_columns(df=phase_master_df)

        phase_master_df.show()

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            phase_master_df = phase_master_df.withColumn(field.name, phase_master_df[field.name].cast(cls))

        return {"CMS_Phases" : phase_master_df}

    def build_casefigures(self, meds_df: SP_DATAFRAME):
        #explode projecttype to get Phases 
        table_name = "CMS_CaseFigures"

        meds_df = meds_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        meds_df = meds_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        
        table_fields = self._get_table_config(table_name)

        for field in table_fields:
            if field.transform and field.transform.type == "data":
                meds_df = meds_df.withColumn(field.name, meds_df[field.transform.source_field])
            elif not field.transform:
                meds_df = meds_df.withColumn(field.name, lit(None).cast(StringType()))

        col_list = [field.name for field in table_fields]
        
        meds_df = meds_df.select(*col_list)

        meds_df.show(n=100)
        self.add_default_columns(df=meds_df)


        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            meds_df = meds_df.withColumn(field.name, meds_df[field.name].cast(cls))

        return {table_name : meds_df}

    def build_intakesummary(self, intake_df: SP_DATAFRAME):
        #explode projecttype to get Phases 
        table_name = "CMS_IntakeDetails"
        intake_df = intake_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        intake_df = intake_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        
        table_fields = self._get_table_config(table_name)

        for field in table_fields:
            if field.transform and field.transform.type == "data":
                intake_df = intake_df.withColumn(field.name, intake_df[field.transform.source_field])
            elif not field.transform:
                intake_df = intake_df.withColumn(field.name, lit(None).cast(StringType()))

        col_list = [field.name for field in table_fields]
        
        intake_df = intake_df.select(*col_list)

        self.add_default_columns(df=intake_df)

        intake_df.show(n=100)

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            intake_df = intake_df.withColumn(field.name, intake_df[field.name].cast(cls))

        return {table_name : intake_df}

    def build_casesummary(self, casesummary_df: SP_DATAFRAME, df_project_vitals: SP_DATAFRAME, df_project: SP_DATAFRAME):
        table_name = "CMS_CaseDetails"
        casesummary_df = casesummary_df.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        casesummary_df = casesummary_df.withColumn("Client_Org_ID", lit(self._get_truve_org(self.config.org_id)))

        #Parse PhaseID 
        df_project = df_project.withColumn("phaseId", F.regexp_replace(col("phaseId"), "'", '"'))\
                    .withColumn("phaseId", F.regexp_replace(col("phaseId"), "None", 'null'))
        
        df_project = df_project.withColumn("phaseId", F.from_json(col("phaseId"), MapType(StringType(), StringType()), {"mode" : "FAILFAST"}))
        df_project = df_project.withColumn("phaseId", df_project.phaseId.getItem("native"))
        

        table_fields = self._get_table_config(table_name)

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            if field.transform and field.transform.type == "data":
                if field.transform.source_entity_name == "casesummary":
                    casesummary_df = casesummary_df.withColumn(field.name, casesummary_df[field.transform.source_field])
            elif not field.transform:
                casesummary_df = casesummary_df.withColumn(field.name, lit(None).cast(cls))

        casesummary_df = casesummary_df.join(df_project.select("projectId", "phaseId"), how="left", on=["projectId"])
        casesummary_df = casesummary_df.drop("Case_Phase_ID").withColumnRenamed("phaseId", "Case_Phase_ID")

        col_list = [field.name for field in table_fields]
        
        casesummary_df = casesummary_df.select(*col_list)

        casesummary_df = self.add_default_columns(df=casesummary_df)

        #Case_Created_Date column deriviation from Project Vitals 
        df_project_vitals = df_project_vitals.filter(df_project_vitals.fieldName == 'createDate') \
                        .withColumn("projectId", df_project_vitals.projectId.cast(IntegerType())) \
                        .withColumnRenamed("projectId","Case_ID").select("Case_ID", "value")
                        

        
        casesummary_df = casesummary_df.join(df_project_vitals, how="left", on=["Case_ID"]) \
            .drop("Case_Create_Date") \
            .withColumnRenamed("value", "Case_Create_Date")

        for field in table_fields:
            cls = self._get_dtype_mapping(field.data_type)
            casesummary_df = casesummary_df.withColumn(field.name, casesummary_df[field.name].cast(cls))

        casesummary_df.show(n=100)

        casesummary_df.printSchema()
        
        return {table_name : casesummary_df}

if __name__ == "__main__":
    print("Hi")
    spark = SparkSession.builder.appName('TSMTransformation').getOrCreate()
    builder = TSMBuilder("confs/sstm.yaml", spark=spark)
    
    #builder = TSMBuilder("sstm.yaml", spark=spark)
    '''
    contact_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/historical_contacts.parquet")
    result = builder.build_peopletypes(contact_df=contact_df)
    print(result["CMS_PeopleType"].printSchema())
    result = builder.build_peoplemaster(contact_df=contact_df)
    print(result)
    exit()
    '''
    '''
    project_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/project.parquet")
    project_df.printSchema()
    print(builder.build_casemaster(project_df))
    '''
    '''
    projecttype_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/projecttypes.parquet")
    projecttype_df.printSchema()
    project_type_df = builder.build_practicetypes(projecttype_df)
    print(project_type_df)
    print(project_type_df["CMS_PracticeTypes"].printSchema())
    '''
    '''    
    phase_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/projecttypes.parquet")
    phase_df = builder.build_phasemaster(phase_df)
    print(phase_df)
    exit()
    '''
    '''
    meds_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/meds.parquet")
    meds_df.printSchema()
    print(builder.build_casefigures(meds_df=meds_df))
    exit()
    '''
    '''
    intake_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/intake.parquet")
    intake_df.printSchema()
    print(builder.build_intakesummary(intake_df=intake_df))
    exit()
    '''

    casesummary_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/casesummary.parquet")
    project_vital_df = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/10000654/project_vitals.parquet")
    df_project = spark.read.parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_input_data/10000654/project.parquet")

    #casesummary_df.select("actualsettlementamount").show()
    #exit()

    #df_project.select("phaseId").show()

    #exit()
    
    project_vital_df = project_vital_df.withColumn("input_file", F.input_file_name())
    project_vital_df = project_vital_df.withColumn('projectId', F.element_at(F.split(F.col('input_file'), '/'), -2))



    casesummary_df.printSchema()

    result = builder.build_casesummary(casesummary_df=casesummary_df, df_project_vitals=project_vital_df, df_project=df_project)
    result["CMS_CaseDetails"].show()
    
    #df = result["CMS_CaseDetails"]
    #df.write.mode('append').parquet("/home/ubuntu/freelancer/scylla/data-api/sstm_output_data/casesummary12.parquet")

    #print(df.count())