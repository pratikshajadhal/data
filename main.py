import re
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig

if __name__ == "__main__":
    contact_etl = ContactETL(model_name="contact", source=None, destination=None, fv_config=FileVineConfig(user_id=31958, org_id=6586))
    project_list = [10568299, 10568297]
    record_list = contact_etl.extract_data_from_source(project_list=project_list)

    contact_df = contact_etl.transform_data(record_list=record_list)
    print(contact_df)
    print(list(contact_df))
    print(contact_df.dtypes)
    #source_schema = self.get_schema_of_model()
    #self.flattend_map = self.flatten_schema(source_schema=source_schema)


    #https://api.filevine.io/core/projects/10568299/contacts
    #https://api.filevine.io/core/projects/10568299/contacts