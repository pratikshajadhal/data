from dataclasses import asdict
from os import environ
import re
from select import select
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig
from dotenv import load_dotenv
import os

from dacite import from_dict

from etl.destination import RedShiftDestination
from utils import load_config 

load_dotenv()

print(os.environ['host'])


if __name__ == "__main__":

    selected_field_config = load_config(file_path="src.yaml")

    for model in selected_field_config.models:
        print(model.name)
        if model.name == "contact":
            rs_config = RedShiftDestination().get_default_config(table_name="contact")
        contact_etl = ContactETL(model_name="contact", source=None, destination=RedShiftDestination(rs_config), fv_config=FileVineConfig(user_id=31958, org_id=6586), column_config=model, primary_key_column="personId")

        project_list = [10568297] #contact_etl.get_projects()
        src_contact_data = contact_etl.extract_data_from_source(project_list=project_list[:10])
        
        contact_df = contact_etl.transform_data(record_list=src_contact_data)
        print(contact_df)
        print(contact_df.dtypes)
        break
