from dataclasses import asdict
from os import environ
import re
from select import select
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig
from dotenv import load_dotenv
import os

from dacite import from_dict

from etl.destination import RedShiftDestination, S3Destination
from utils import load_config 

load_dotenv()

#print(os.environ['s3_bucket'])
print("Hi")
print(os.environ)


if __name__ == "__main__":

    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    #Handle Contact Entity
    for model in selected_field_config.core:
        contact_etl = ContactETL(model_name="contact", 
                            source=None, 
                            entity_type="core",
                            project_type=None,
                            destination=S3Destination(org_id=fv_config.org_id), 
                            fv_config=fv_config, 
                            column_config=model, 
                            primary_key_column="personId")

        project_list = [10568297] #contact_etl.get_projects()
        src_contact_data = contact_etl.extract_data_from_source(project_list=project_list[:10])
        
        contact_df = contact_etl.transform_data(record_list=src_contact_data)

        contact_etl.load_data_to_destination(trans_df=contact_df, schema=None)
        print(contact_df)
        print(contact_df.dtypes)
        break
