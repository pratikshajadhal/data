import threading
from etl.collections import CollectionETL
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig, LeadDocketConfig

from etl.lead.core import CoreETL 
from etl.lead.lead_row import LeadRowETL
from etl.lead.lead_detail import LeadDetailETL
from etl.lead.lead_contact import LeadContactETL
from etl.lead.lead_opport import LeadOpportETL
from etl.lead.lead_referrals import LeadReferralsETL
from etl.lead.lead_users import LeadUsersETL

import os
from dotenv import load_dotenv
import uvicorn


from etl.destination import RedShiftDestination, S3Destination
from etl.form import FormETL
from etl.project import ProjectETL
from etl.projecttypes import ProjectTypeETL
from utils import load_config, get_chunks, load_lead_config
from tasks.tasks import make_fv_subscription

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

        #project_list = form_etl.get_projects() #[10568297] #contact_etl.get_projects()

            #project_list = [10598323]

        contact_etl.get_schema_of_model()

        contact_etl.flattend_map = contact_etl.get_filtered_schema(contact_etl.source_schema)

        dest_col_format = contact_etl.convert_schema_into_destination_format(contact_etl.flattend_map)

        count = 0
        
        contact_list = contact_etl.extract_data_from_source()

        transformed_data = contact_etl.transform_data(contact_list)

        contact_etl.load_data_to_destination(trans_df=transformed_data, schema=dest_col_format, project=None)

        '''
        for contact in contact_list:
            contact_df = contact_etl.transform_data(record_list=[contact])
            personId = contact_df["personId"].tolist()[0]
            contact_etl.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=personId)
        '''
        #count = count + 1

        print("Total processed {}".format(count))

        break

def start_projecttype_etl():
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    #Handle Contact Entity
    for model in selected_field_config.core:
        if model.name != "projecttype":
            continue

        model_etl = ProjectTypeETL(model_name="projecttype", 
                            source=None, 
                            entity_type="core",
                            project_type=None,
                            destination=S3Destination(org_id=fv_config.org_id), 
                            fv_config=fv_config, 
                            column_config=model, 
                            primary_key_column="projectTypeId")

        model_etl.get_schema_of_model()

        model_etl.flattend_map = model_etl.get_filtered_schema(model_etl.source_schema)

        dest_col_format = model_etl.convert_schema_into_destination_format(model_etl.flattend_map)

        count = 0
        
        model_data = model_etl.extract_data_from_source()

        transformed_data = model_etl.transform_data(model_data)

        model_etl.load_data_to_destination(trans_df=transformed_data, schema=dest_col_format, project=None)

def start_project_etl():
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

        #Handle Contact Entity
    for model in selected_field_config.core:
        if model.name == "project":
            project_etl = ProjectETL(model_name="project", 
                                source=None, 
                                entity_type="core",
                                project_type=18764,
                                destination=S3Destination(org_id=fv_config.org_id), 
                                fv_config=fv_config, 
                                column_config=model, 
                                primary_key_column="projectId")

            project_list = project_etl.extract_data_from_source()
        
            project_etl.get_schema_of_model()

            project_etl.flattend_map = project_etl.get_filtered_schema(project_etl.source_schema)

            dest_col_format = project_etl.convert_schema_into_destination_format(project_etl.flattend_map)

            count = 0
            
            #Added Multithreading support
            chunk = 10

            chunk_list = [project_list[i * chunk:(i + 1) * chunk] for i in range((len(project_list) + chunk - 1) // chunk )]
            
            thread_count = 10
            processed_chunk_list = 0

            count = 0
            thread_list = []

            print(chunk_list)
            print(len(chunk_list))
            
            for index, project_chunk in enumerate(chunk_list):
                print(f"Total proessed so far {index}")
                if count < thread_count:
                    t = threading.Thread(target=project_etl.trigger_etl, args=(project_chunk, dest_col_format))
                    t.start()
                    thread_list.append(t)
                    processed_chunk_list += 1
                    count += 1
                else:
                    for t in thread_list:
                        t.join()
                    thread_list = []
                    count = 0
            

            '''
            contact_list = contact_etl.extract_data_from_source()

            for contact in contact_list:
                contact_df = contact_etl.transform_data(record_list=[contact])
                projectId = contact_df["projectId"].tolist()[0]
                contact_etl.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=projectId)
                
            #count = count + 1

            print("Total processed {}".format(count))

            break
            '''

def start_form_etl(project_type, form_name):
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

        #Handle Contact Entity
    for section in selected_field_config.projectTypes[0].sections:
        if section.name == form_name:
            form_etl = FormETL(model_name=form_name, 
                            source=None, 
                            entity_type="form",
                            project_type=18764,
                            destination=S3Destination(org_id=fv_config.org_id), 
                            fv_config=fv_config, 
                            column_config=section, 
                            primary_key_column="projectId")

            project_list = form_etl.get_projects() #[10568297] #contact_etl.get_projects()

            project_list = project_list
            form_etl.get_schema_of_model()

            form_etl.flattend_map = form_etl.get_filtered_schema(form_etl.source_schema)

            dest_col_format = form_etl.convert_schema_into_destination_format(form_etl.flattend_map)

            #Added Multithreading support
            chunk = 10

            chunk_list = [project_list[i * chunk:(i + 1) * chunk] for i in range((len(project_list) + chunk - 1) // chunk )]
            
            thread_count = 10
            processed_chunk_list = 0

            count = 0
            thread_list = []

            print(chunk_list)
            print(len(chunk_list))
            
            for index, project_chunk in enumerate(chunk_list):
                print(f"Total proessed so far {index}")
                if count < thread_count:
                    t = threading.Thread(target=form_etl.trigger_etl, args=(project_chunk, dest_col_format))
                    t.start()
                    thread_list.append(t)
                    processed_chunk_list += 1
                    count += 1
                else:
                    for t in thread_list:
                        t.join()
                    thread_list = []
                    count = 0
                
            
            for t in thread_list:
                t.join()
                


            '''
            while True and processed_chunk_list <= len(chunk_list):
                
                thread_list = []
                count = 0
                for index, project_chunk in enumerate(chunk_list):
                    if count <= thread_count:
                        t = threading.Thread(target=form_etl.trigger_etl, args=(project_chunk, dest_col_format))
                        #t.start()
                        thread_list.append(t)
                        processed_chunk_list += 1
                    else:
                        break
                    count += 1
                    
                #for t in thread_list:
                #    t.join()

                print("Assigning new threads")

            break
            '''

def start_collection_etl(project_type, section_name):
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

        #Handle Contact Entity
    for section in selected_field_config.projectTypes[0].sections:
        if section.name == section_name:
            form_etl = CollectionETL(model_name=section_name, 
                            source=None, 
                            entity_type="collections",
                            project_type=18764,
                            destination=S3Destination(org_id=fv_config.org_id), 
                            fv_config=fv_config, 
                            column_config=section, 
                            primary_key_column="id")

            project_list = form_etl.get_projects() #[10568297] #contact_etl.get_projects()

            #project_list = [10598323]

            form_etl.get_schema_of_model()

            form_etl.flattend_map = form_etl.get_filtered_schema(form_etl.source_schema)

            dest_col_format = form_etl.convert_schema_into_destination_format(form_etl.flattend_map)

            #Added Multithreading support
            chunk = 10

            chunk_list = [project_list[i * chunk:(i + 1) * chunk] for i in range((len(project_list) + chunk - 1) // chunk )]
            
            thread_count = 10
            processed_chunk_list = 0

            count = 0
            thread_list = []

            print(chunk_list)
            print(len(chunk_list))
            
            for index, project_chunk in enumerate(chunk_list):
                print(f"Total proessed so far {index}")
                if count < thread_count:
                    t = threading.Thread(target=form_etl.trigger_etl, args=(project_chunk, dest_col_format))
                    t.start()
                    thread_list.append(t)
                    processed_chunk_list += 1
                    count += 1
                else:
                    for t in thread_list:
                        t.join()
                    thread_list = []
                    count = 0
                
            
            for t in thread_list:
                t.join()
            

if __name__ == "__main__":
    #start_form_etl(18764, "intake")    
    #start_collection_etl(18764, "negotiations")
    #start_form_etl(18764, "casesummary")
    #start_contact_etl()
    #exit()
    #start_projecttype_etl()
    #start_form_etl(18764, "casesummary")
    #start_project_etl()

    # - - - - 

    uvicorn.run("api_server.app:app", host="0.0.0.0", port=int(os.environ["SERVER_PORT"]), reload=True, root_path="/")

    # # Wh subscription for filevine
    # make_fv_subscription(
    #     s3_conf_file_path="s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml", 
    #     endpoint_to_subscribe="http://ec2-3-74-173-122.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     # endpoint_to_subscribe="http://ec2-18-196-103-238.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     )
