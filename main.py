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

from dotenv import load_dotenv
import uvicorn


from etl.destination import RedShiftDestination, S3Destination
from etl.form import FormETL
from etl.project import ProjectETL
from utils import load_config, get_chunks, load_lead_config
from tasks.subscriptions import make_fv_subscription

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


def start_statuses_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)
    section = selected_field_config.table_leadstatuses[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(ld_config.org_id))

        
    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)


def start_leadsource_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)
    section = selected_field_config.table_leadsource[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(ld_config.org_id))

    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)


def start_case_type_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)
    section = selected_field_config.table_casetype[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(ld_config.org_id))

    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)


def start_lead_row_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)
    
    section = selected_field_config.table_leadrow[0]
    lead_row = LeadRowETL(model_name=section.name ,
                        ld_config=ld_config,
                        column_config=section, 
                        fields=section.fields,
                        destination=S3Destination(ld_config.org_id))

    statuses = lead_row.extract_lead_metadata()

    extracted = lead_row.extract_data_from_source(statuses)
    for each_ex in extracted:
        transformed = lead_row.transform(each_ex)
        df = lead_row.eliminate_nonyaml(transformed)
        lead_row.load_data(trans_df=df)


def start_lead_detail_etl(lead_ids:list = None):
    """
        Function to fill detail table. Runs for the given lead_ids.
        If ids is not given, then it will run as historical.
    """
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)

    section = selected_field_config.table_leaddetail[0] # Temp
    lead_detail = LeadDetailETL(model_name=section.name ,
                                ld_config=ld_config,
                                column_config=section, 
                                fields=section.fields,
                                destination=S3Destination(ld_config.org_id))

    if lead_ids is None:
        lead_ids = lead_detail.extract_lead_metadata()


    # lead_ids = [9964]
    for idx, lead_id in enumerate(lead_ids):
        # if idx == 100:
        #     time.sleep(60)
        lead = lead_detail.extract_data_from_source(lead_id)
        lead_detail_df = lead_detail.transform(lead)
        transformed_detail_df = lead_detail.eliminate_nonyaml(lead_detail_df)
        lead_detail.load_data(trans_df=transformed_detail_df)
    

def start_lead_contact_etl(contact_ids:list = None):
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)

    section = selected_field_config.table_contact[0]
    contact_etl = LeadContactETL(model_name=section.name ,
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=S3Destination(ld_config.org_id))

    if contact_ids is None:
        contact_ids = contact_etl.extract_lead_metadata()
    # contact_ids = [10184, 9967, 9859, 10167, 6999, 9961, 10166, 10180, 10085, 10094]
    for contact_id in contact_ids:
        extracted = contact_etl.extract_data_from_source(contact_id)
        contact_df = contact_etl.transform(extracted)
        transformed = contact_etl.eliminate_nonyaml(contact_df)
        contact_etl.load_data(trans_df=transformed)


def start_opport_etl(opport_ids:list = None):
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)

    section = selected_field_config.table_opport[0] 
    opport_etl = LeadOpportETL(model_name=section.name ,
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=S3Destination(ld_config.org_id))

    if opport_ids is None:
        opport_ids  = opport_etl.extract_lead_metadata()
    # opport_ids = [2483, 2482, None, 2469, None, 2417, 2436, 2362, 2432, None]
    # opport_ids = [ ele for ele in opport_ids if ele is not None ]
    for opport_id in opport_ids:
        extracted = opport_etl.extract_data_from_source(opport_id)
        opport_df = opport_etl.transform(extracted)
        transformed = opport_etl.eliminate_nonyaml(opport_df)
        opport_etl.load_data(trans_df=transformed)


def start_referrals_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)

    section = selected_field_config.table_referral[0]
    referral_etl = LeadReferralsETL(model_name=section.name ,
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(ld_config.org_id))

    extracted = referral_etl.extract_data_from_source()
    referral_df = referral_etl.transform(extracted)
    transformed = referral_etl.eliminate_nonyaml(referral_df)
    referral_etl.load_data(trans_df=transformed)


def start_users_etl():
    selected_field_config = load_lead_config(file_path="src-lead.yaml")
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)

    section = selected_field_config.table_users[0]
    users_etl = LeadUsersETL(model_name=section.name ,
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(ld_config.org_id))

    extracted = users_etl.extract_data_from_source()
    for each_ex in extracted:
        user_df = users_etl.transform(each_ex)
        transformed = users_etl.eliminate_nonyaml(user_df)
        users_etl.load_data(trans_df=transformed)


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
    # uvicorn.run("api_server.app:app", host="0.0.0.0", port=8000, reload=True, root_path="/")

    # Wh subscription for filevine
    make_fv_subscription(
        s3_conf_file_path="s3://dev-data-api-01-buckets-buckettruverawdata-8d0qeyh8pnrf/confs/filevine/config_6586.yaml", 
        endpoint_to_subscribe="http://ec2-18-196-103-238.eu-central-1.compute.amazonaws.com:8000/master_webhook_handler"
        )
