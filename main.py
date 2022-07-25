from etl.collections import CollectionETL
from etl.contact import ContactETL
from etl.datamodel import ETLSource, FileVineConfig, LeadDocketConfig



from dotenv import load_dotenv
import uvicorn


from etl.destination import RedShiftDestination, S3Destination
from etl.form import FormETL
from etl.project import ProjectETL
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

        for contact in contact_list:
            contact_df = contact_etl.transform_data(record_list=[contact])
            personId = contact_df["personId"].tolist()[0]
            contact_etl.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=personId)

        #count = count + 1

        print("Total processed {}".format(count))

        break


def start_project_etl():
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

        #Handle Contact Entity
    for model in selected_field_config.core:
        if model.name == "project":
            contact_etl = ProjectETL(model_name="project", 
                                source=None, 
                                entity_type="core",
                                project_type=18764,
                                destination=S3Destination(org_id=fv_config.org_id), 
                                fv_config=fv_config, 
                                column_config=model, 
                                primary_key_column="projectId")

            project_list = [10568297] #contact_etl.get_projects()

            #project_list = form_etl.get_projects() #[10568297] #contact_etl.get_projects()

                #project_list = [10598323]

            contact_etl.get_schema_of_model()

            contact_etl.flattend_map = contact_etl.get_filtered_schema(contact_etl.source_schema)

            dest_col_format = contact_etl.convert_schema_into_destination_format(contact_etl.flattend_map)

            count = 0
            
            contact_list = contact_etl.extract_data_from_source()

            for contact in contact_list:
                contact_df = contact_etl.transform_data(record_list=[contact])
                projectId = contact_df["projectId"].tolist()[0]
                contact_etl.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=projectId)
                
            #count = count + 1

            print("Total processed {}".format(count))

            break
        

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

            #project_list = [10598323]

            form_etl.get_schema_of_model()

            form_etl.flattend_map = form_etl.get_filtered_schema(form_etl.source_schema)

            dest_col_format = form_etl.convert_schema_into_destination_format(form_etl.flattend_map)

            count = 0
            
            for project in project_list[:100]:
                form_data_list = form_etl.extract_data_from_source(project_list=[project])

                form_df = form_etl.transform_data(record_list=form_data_list)
                
                form_etl.load_data_to_destination(trans_df=form_df, schema=dest_col_format, project=project)

                count = count + 1

                print("Total processed {}".format(count))

            break

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

            
            count = 0
            
            for project in project_list[:100]:
                form_data_list = form_etl.extract_data_from_source(project_list=[project])

                if len(form_data_list) == 0:
                    continue

                form_df = form_etl.transform_data(record_list=form_data_list)
                
                form_etl.load_data_to_destination(trans_df=form_df, schema=dest_col_format, project=project)

                count += 1

                print("Total processed {}".format(count))

            break

if __name__ == "__main__":
    #start_form_etl(18764, "intake")    
    #start_collection_etl(18764, "negotiations")
    #start_form_etl(18764, "casesummary")
    #start_contact_etl()
    #start_project_etl()

    # - - - - 

    # start_statuses_etl()
    # start_case_type_etl()
    # start_leadsource_etl()
    # start_lead_row_etl()
    # start_lead_detail_etl()
    # start_lead_contact_etl()
    # start_opport_etl()
    # start_referrals_etl()
    # start_users_etl()
    uvicorn.run("api_server.app:app", host="0.0.0.0", port=8000, reload=True, root_path="/")

    # # Wh subscription for filevine
    # make_fv_subscription(
    #     s3_conf_file_path="s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml", 
    #     endpoint_to_subscribe="http://ec2-3-74-173-122.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     # endpoint_to_subscribe="http://ec2-18-196-103-238.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
    #     )
