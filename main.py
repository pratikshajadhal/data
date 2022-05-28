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
from etl.form import FormETL
from utils import load_config, get_chunks

load_dotenv()

def start_contact_etl():
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

        '''
        for contact_data in src_contact_data:
            for key in contact_data:
                print(key)
            break
        exit()
        '''
        contact_df = contact_etl.transform_data(record_list=src_contact_data)
        print(contact_df.dtypes)
        print(contact_df.isnull().sum())
        
        contact_etl.load_data_to_destination(trans_df=contact_df, schema=None)
        #print(contact_df)
        break

def start_form_etl(project_type, form_name):
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

        #Handle Contact Entity
    for section in selected_field_config.projectTypes[0].sections:
        if section.name == form_name:
            form_etl = FormETL(model_name="intake", 
                            source=None, 
                            entity_type="form",
                            project_type=18764,
                            destination=S3Destination(org_id=fv_config.org_id), 
                            fv_config=fv_config, 
                            column_config=section, 
                            primary_key_column="projectId")

            project_list = form_etl.get_projects() #[10568297] #contact_etl.get_projects()
            #project_list = [10487166]
            #project_chunks = get_chunks(project_list, size=100)
            
            new_project_list = []

            for project in project_list:
                if project > 10283874:
                    continue
                new_project_list.append(project)
            
            project_list = new_project_list
            
            #project_list = [10487166]
            project_chunks = get_chunks(project_list, size=100)
            
            count = 0
            
            for chunk in project_chunks:
                form_data_list = form_etl.extract_data_from_source(project_list=chunk)

                form_df, dest_col_format = form_etl.transform_data(record_list=form_data_list)
                
                form_etl.load_data_to_destination(trans_df=form_df, schema=dest_col_format)

                count = count + len(chunk)

                print("Total processed {}".format(count))

                #break
            
            break




if __name__ == "__main__":
    start_form_etl(18764, "intake")