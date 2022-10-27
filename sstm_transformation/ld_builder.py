import abc
from cmath import phase
from typing import Dict, List
import yaml
from dacite import from_dict
import json

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame as SP_DATAFRAME
from pyspark.sql.types import *
from pyspark.sql.functions import split, col, explode, lit, monotonically_increasing_id, udf
from pyspark.sql import functions as F


from sstm_transformation.datamodel import SSTM, TSMTableField

def deDupeDfCols(df, separator=''):
    newcols = []

    for col in df.columns:
        if col not in newcols:
            newcols.append(col)
        else:
            for i in range(2, 1000):
                if (col + separator + str(i)) not in newcols:
                    newcols.append(col + separator + str(i))
                    break

    return df.toDF(*newcols)

#@staticmethod but Spark gives error.
def split_substatuses(custom: str, substatus_type: str):
    if custom == '[]':
        return ""

    ids = list()
    names = list()
    arr = custom.split("},")
    for each_arr in arr:
        sub_spl = each_arr.split(",")
        id = str(sub_spl[0].split("'Id': ")[1])
        name = str(sub_spl[1].split("'SubStatusName': ")[1].replace("'", "")).replace("}]", "")
        
        ids.append(id)
        names.append(name)

    return ", ".join(ids) if  substatus_type == 'SubStatusId'  else ", ".join(names)


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


        return df
        

    def _get_dtype_mapping(self, data_type):
        d_map = {
            "string": StringType(),
            "str": StringType(),
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
    
    def build_contact(
        self,
        df_contact: SP_DATAFRAME,
        df_ld: SP_DATAFRAME,
        df_users: SP_DATAFRAME
    )-> dict:
        table_name = "CRM_Contacts"
        
        df_contact = df_contact.toDF(*[f'contact_{c}' for c in df_contact.columns])
        df_ld = df_ld.toDF(*[f'ld_{c}' for c in df_ld.columns])
        df_users = df_users.toDF(*[f'users_{c}' for c in df_users.columns])

        # Manipulate users table to join on
        df_users = df_users.withColumn('users_FullName', F.concat(F.col('users_FirstName'),F.lit(' '), F.col('users_LastName')))

        joined1 = df_contact\
            .join(df_ld,  df_contact.contact_LeadIds  ==  df_ld.ld_Id ,"left")\
            .select(df_contact['*'], df_ld['ld_ContactSource'].alias('ld_ContactSource')) 
        joined2 = joined1\
            .join(df_users,  joined1.contact_CreatedBy  ==  df_users.users_FullName ,"left")\
            .select(joined1['*'], df_users['users_Id'].alias('users_Id')) 

        joined2 = joined2.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        joined2 = joined2.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        
        columns = ["Truve_Org_ID", "Client_Org_ID",
            "contact_Id", "contact_FirstName", "contact_MiddleName", 
            "contact_LastName", "contact_Address1",
            "contact_Address2", "contact_City",
            "contact_State", "contact_Zip", "contact_County", "contact_HomePhone", "contact_MobilePhone",
            "contact_WorkPhone", "contact_Email", "contact_PreferredContactMethod",
            "contact_Birthdate", "contact_Deceased", "contact_Gender", "contact_Minor",
            "contact_Language", "ld_ContactSource", "contact_CreatedOn", "users_Id",
            "contact_CreatedBy"]
        final_df = joined2.select(*columns)
        table_fields = self._get_table_config(table_name)
        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                final_df = final_df.withColumn(field.name, final_df[field.transform.source_field])
            elif not field.transform:
                final_df = final_df.withColumn(field.name, lit(None).cast(StringType()))
            
        
        col_list = [field.name for field in table_fields]
        
        final_df = final_df.select(*col_list)

        for field in table_fields:
            dtype = self._get_dtype_mapping(field.data_type)
            final_df = final_df.withColumn(field.name, final_df[field.name].cast(dtype))

        columns = ["Contact_ID", "First_Name", "Contact_Source", "Created_By_ID", "Created_By_Full_Name"]
        final_df.select(*columns).show()
        final_df.printSchema()
        return {table_name : final_df}


    def build_leads(self, df: SP_DATAFRAME):
        table_name = "CRM_Leads"
        df = self.transform(df, table_name)

        # Not null and PK constraints
        df = df.na.drop(subset=["Client_Org_ID", "Client_Org_ID"])
        df = df.dropDuplicates(["Client_Org_ID","Lead_ID"])
        
        df.show()
        return {table_name : df}
        

    def build_leadsource(self, df: SP_DATAFRAME):
        table_name = "CRM_LeadSource"
        df = self.transform(df, table_name)

        # Not null and PK constraints
        df = df.na.drop(subset=["Client_Org_ID", "Lead_Source_ID"])

        df = df.dropDuplicates(["Client_Org_ID","Lead_Source_ID"])
        
        df.show()
        return {table_name : df}

    def build_casetype(self, df: SP_DATAFRAME):
        table_name = "CRM_CaseTypes"
        df = self.transform(df=df, table_name=table_name)

        # Not null and PK constraints
        df = df.na.drop(subset=["Client_Org_ID", "Truve_Org_ID", "Practice_Type_ID", "Case_Type_ID"])
        df = df.dropDuplicates(["Client_Org_ID","Practice_Type_ID", "Case_Type_ID"])
        
        df.show(100)
        return {table_name : df}

    def build_opportunities(self, df: SP_DATAFRAME):
        table_name = "CRM_Opportunities"
        df = self.transform(df=df, table_name=table_name)
        df.show(100)
        return {table_name : df}

    def build_referrals(self, df: SP_DATAFRAME):
        table_name = "CRM_Referrals"
        df = self.transform(df=df, table_name=table_name)

        # Not null and PK constraints
        df = df.na.drop(subset=["Truve_Org_ID", "Client_Org_ID"])
        df = df.dropDuplicates(["Client_Org_ID","Referral_ID"])


        df.show(100)

        return {table_name : df}


    def build_statuses(self, df: SP_DATAFRAME):
        table_name = "CRM_Status"
        df = self.transform(df=df, table_name=table_name)

        get_substatus_ids = udf(lambda z: split_substatuses(z, 'SubStatusId'))
        get_substatus_names = udf(lambda z: split_substatuses(z, "SubStatusName"))

        df = df.withColumn("Substatus_Id", get_substatus_ids(col("Substatus_Id")))
        df = df.withColumn("Substatus_Name", get_substatus_names(col("Substatus_Name")))

        df.show()
        return {table_name : df}

    def build_status_changes(self, df: SP_DATAFRAME):
        table_name = "CRM_StatusChanges"
        df = self.transform(df=df, table_name=table_name)

        # Not null and PK constraints
        df = df.na.drop(subset=["Client_Org_ID", "Truve_Org_ID", "Lead_ID", "Status_ID", "Status_Change_Date"])

        df.show()
        df.printSchema()
        return {table_name : df}

    def build_practice_type(self, df: SP_DATAFRAME):
        table_name = "CRM_PracticeTypes"
        df = self.transform(df=df, table_name=table_name)
        
                
        # Not null and PK constraints# Not null constraint
        df = df.na.drop(subset=["Client_Org_ID", "Truve_Org_ID","Practice_Type_ID","Practice_Type_Name"])
        df = df.distinct()
        
        df.show(100)
        df.printSchema()
        return {table_name : df}

    def build_users(self, df: SP_DATAFRAME):
        table_name = "CRM_Users"
        df = self.transform(df=df, table_name=table_name)
        df = df.withColumn("Full_Name", F.concat_ws(' ', df.First_Name, df.Last_Name))
        df.show(100)
        df.printSchema()

        return {table_name : df}

    def build_leaddetail(
        self,
        df_ld: SP_DATAFRAME, 
        df_opp: SP_DATAFRAME,
        df_statuses: SP_DATAFRAME,
        df_ldsources: SP_DATAFRAME,
        df_users: SP_DATAFRAME,
        df_referral: SP_DATAFRAME
    ) -> Dict:
        """Builds CRM_LeadDetail dataframes using 5 different df

        Args:
            df_ld (SP_DATAFRAME): _description_
            df_opp (SP_DATAFRAME): _description_
            df_statuses (SP_DATAFRAME): _description_
            df_ldsources (SP_DATAFRAME): _description_
            df_users (SP_DATAFRAME): _description_
            df_referral

        Returns:
            Dict: _description_
        """
        table_name = "CRM_LeadDetail"
        
        # Modify column names to prevent naming conflict
        df_ld = df_ld.toDF(*[f'ld_{c}' for c in df_ld.columns])
        df_opp = df_opp.toDF(*[f'opp_{c}' for c in df_opp.columns])
        df_opp.printSchema()
        df_statuses = df_statuses.toDF(*[f'statuses_{c}' for c in df_statuses.columns])
        df_ldsources = df_ldsources.toDF(*[f'sources_{c}' for c in df_ldsources.columns])
        df_users = df_users.toDF(*[f'users_{c}' for c in df_users.columns])
        df_referral = df_referral.toDF(*[f'referral_{c}' for c in df_referral.columns])

        # Joins tables on by on respectively: opport - lead - statuses - sources - users
        joined1 = df_ld.join(df_opp, df_ld.ld_Opportunity == df_opp.opp_Id ,"left")
        
        joined1_0 = joined1\
                    .join(df_referral,joined1.ld_ReferredBy ==  df_referral.referral_Id,"left")\
                    .select(joined1['*'], df_referral['referral_Id'].alias('Referred_By_ID')) # get statuses_Id
        joined2 = joined1_0\
                    .join(df_statuses,joined1_0.ld_Status ==  df_statuses.statuses_Status,"left")\
                    .select(joined1_0['*'], df_statuses['statuses_Id'].alias('Status_ID')) # get statuses_Id
        joined3 = joined2\
                    .join(df_ldsources,joined2.ld_ContactSource ==  df_ldsources.sources_SourceName,"left")\
                    .select(joined2['*'], df_ldsources['sources_Id'].alias('Lead_Source_ID')) # get sources_Id
        joined4 = joined3\
                    .join(df_users,joined3.opp_ProcessedBy ==  df_users.users_Email,"left")\
                    .select(joined3['*'], df_users['users_Id'].alias('Processed_By_ID')) # get users_Id
        joined5 = joined4\
                    .join(df_users,joined4.opp_AssignedTo ==  df_users.users_Email,"left")\
                    .select(joined4['*'], df_users['users_Id'].alias('Assigned_To_ID')) # get users_Id
        
        # Add default columns        
        joined5 = joined5.withColumn("Truve_Org_ID", lit(self._get_truve_org(self.config.org_id)))
        joined5 = joined5.withColumn("Client_Org_ID", lit(self._get_client_org(self.config.org_id)).cast(StringType()))
        # Specify columns to get
        columns = ["Truve_Org_ID", "Client_Org_ID",
                   "ld_Id", "opp_Id", "Status_ID", 
                   "Lead_Source_ID", "opp_Summary",
                   "ld_InjuryInformation", "opp_Note",
                   "ld_ReferredBy", "ld_SeverityLevel", "opp_County", "opp_Processed", "opp_ProcessedDate",
                   "Processed_By_ID", "opp_DisregardReason", "Assigned_To_ID",
                   "ld_RejectedDate", "ld_ReferredDate", "ld_SignedUpDate", "ld_CaseClosedDate",
                   "ld_LostDate", "ld_Paralegal", "ld_Attorney",
                   "ld_QualifiedLead", "ld_WereYouAtFault",
                   "ld_Wasanyoneelseinthevehiclewithyou", "ld_TreatmentatHospital", "ld_Didyouseekanyotherdoctorstreatment"
                   ]
        
        final_df = joined5.select(*columns)
        table_fields = self._get_table_config(table_name)
        
        for field in table_fields:
            if field.transform and field.transform.type == "data":
                final_df = final_df.withColumn(field.name, final_df[field.transform.source_field])
            elif not field.transform:
                final_df = final_df.withColumn(field.name, lit(None).cast(StringType()))
            
        
        col_list = [field.name for field in table_fields]
        
        final_df = final_df.select(*col_list)

        for field in table_fields:
            dtype = self._get_dtype_mapping(field.data_type)
            final_df = final_df.withColumn(field.name, final_df[field.name].cast(dtype))

        # final_df.show()
        
        # final_df \
        #     .write.option("header",True) \
        #     .csv("temp_data/CSV_OUTPUT")
        final_df.printSchema()
        final_df.select(["Lead_ID", "Opportunity_ID", "Status_ID"]).show()
        return {table_name : final_df}





# '''
# # - - - Test Local spark
# from sstm_transformation.ld_builder import LDBuilder
# from pyspark.sql import SparkSession
# spark = SparkSession \
#     .builder \
#     .config("spark.debug.maxToStringFields", 2000) \
#     .config('spark.ui.port', 8284) \
#     .appName('TSMTransformation') \
#     .getOrCreate()

# builder = LDBuilder("confs/ld_sstm.yaml", spark=spark)

# #     ld_users_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\users\12.parquet")
# #     ld_users_df = builder.build_users(df=ld_users_df)
# #     print(ld_users_df)
# #     (ld_users_df["LD_Statuses"]).printSchema()

# #     # - - -

    # ld_contacts = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\contacts\*.parquet")
    # # ld_detail = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_detail\*.parquet")
    # # ld_users_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\users\12.parquet")

    # ld_contacts = builder.build_contact(df=ld_contacts)
    # print(ld_contacts)

# #     # - - -

# #     ld_statuses_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\statuses\*.parquet")
# #     ld_statuses_df = builder.build_statuses(df=ld_statuses_df)
# #     print(ld_statuses_df)

# #     # - - -

# #     ld_casetype_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\casetype\*.parquet")
# #     ld_casetype_df = builder.build_casetype(df=ld_casetype_df)
# #     print(ld_casetype_df)

# #     # - - -

# #     ld_practice_types = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\casetype\*.parquet")
# #     ld_practice_types = builder.build_practice_type(df=ld_practice_types)
# #     print(ld_practice_types)

# #     # # - - -

# #     ld_referral_df = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\referrals\*.parquet")
# #     ld_referral_df = builder.build_referrals(df=ld_referral_df)
# #     print(ld_referral_df)


# # # - - -
# # ld_leads = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_detail\*.parquet")
# # ld_leads = builder.build_leads(df=ld_leads)
# # print(ld_leads)

# # #     # # - - -
# #     ld_status_changes = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_raw\*.parquet")
# #     ld_status_changes = builder.build_status_changes(df=ld_status_changes)
# #     print(ld_status_changes)


# # - - -
# # leadsource = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_source\*.parquet")
# # leadsource = builder.build_leadsource(df=leadsource)
# # print(leadsource)

# # - - -
# ld_detail = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_detail\*.parquet")
# ld_opport = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\opport\*.parquet")
# ld_statuses = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\statuses\*.parquet")
# ld_source = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\lead_source\*.parquet")
# ld_users = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\users\12.parquet")
# ld_referral = spark.read.parquet(r"C:\Users\mert.seven\Desktop\Projects\Truve\shiv-apı\latest\data-api\temp_data\referrals\*.parquet")

# builder.build_leaddetail(ld_detail, ld_opport, ld_statuses, ld_source, ld_users, ld_referral)

# """
# '''
