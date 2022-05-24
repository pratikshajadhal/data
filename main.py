from os import environ
import re
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig
from dotenv import load_dotenv
import os

from etl.destination import RedShiftDestination 

load_dotenv()

print(os.environ['host'])


if __name__ == "__main__":
    rs_config = RedShiftDestination().get_default_config("contact")
    contact_etl = ContactETL(model_name="contact", source=None, destination=RedShiftDestination(rs_config), fv_config=FileVineConfig(user_id=31958, org_id=6586))
    project_list = [10568299, 10568297]

    source_schema = contact_etl.get_schema_of_model()
    flattened_schema = contact_etl.flatten_schema(source_schema=source_schema)
    dest_schema = contact_etl.convert_schema_into_destination_format(source_flattened_schema=flattened_schema)

    contact_etl.load_data_to_destination(trans_df=None, schema=dest_schema)
    print(dest_schema)
    exit()
    '''
    record_list = contact_etl.extract_data_from_source(project_list=project_list)

    contact_df = contact_etl.transform_data(record_list=record_list)
    print(contact_df)
    print(list(contact_df))
    print(contact_df.dtypes)
    #source_schema = self.get_schema_of_model()
    #self.flattend_map = self.flatten_schema(source_schema=source_schema)

    contact_etl.load_data_to_destination(contact_df)


    #https://api.filevine.io/core/projects/10568299/contacts
    #https://api.filevine.io/core/projects/10568299/contacts
    '''