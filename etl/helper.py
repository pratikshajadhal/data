from etl.collections import CollectionETL
from etl.datamodel import FileVineConfig, SelectedConfig, LeadDocketConfig, LeadSelectedConfig
from etl.form import FormETL
from etl.project import ProjectETL
from etl.contact import ContactETL
from utils import get_config_of_section
from etl.lead.core import CoreETL 
from etl.lead.lead_row import LeadRowETL
from etl.lead.lead_detail import LeadDetailETL
from etl.lead.lead_contact import LeadContactETL
from etl.lead.lead_opport import LeadOpportETL
from etl.lead.lead_referrals import LeadReferralsETL
from etl.lead.lead_users import LeadUsersETL
from utils import get_config_of_section, get_config_of_lead_section

def handle_project_object(org_id, creds, project_type_id:int, entity:str):

    fv_config = FileVineConfig(org_id=org_id, user_id=creds["user_id"], api_key=creds["api_key"])

    # selected_column_config = get_config_of_section(selected_config=selected_field_config, 
    #                                             section_name=entity.lower(), 
    #                                             project_type_id=project_type_id,
    #                                             is_core=True)

    project_etl = ProjectETL(model_name="project", 
                                source=None, 
                                entity_type="core",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=None,
                                primary_key_column="projectId")
    return project_etl

def handle_form_object(org_id, creds, project_type_id:int, entity:str):
    
    fv_config = FileVineConfig(org_id=org_id, user_id=creds["user_id"], api_key=creds["api_key"])


    # selected_column_config = get_config_of_section(selected_config=selected_field_config, 
    #                                             section_name=entity.lower(), 
    #                                             project_type_id=project_type_id,
    #                                             is_core=True)

    form_etl = FormETL(model_name=entity.lower(), 
                                source=None, 
                                entity_type="form",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config,
                                # column_config=selected_column_config, 
                                primary_key_column="projectId")
    return form_etl


def handle_collection_object(org_id, creds, project_type_id:int, entity:str):
    fv_config = FileVineConfig(org_id=org_id, user_id=creds["user_id"], api_key=creds["api_key"])

    # selected_column_config = get_config_of_section(selected_config=selected_field_config, 
    #                                             section_name=entity.lower(), 
    #                                             project_type_id=project_type_id,
    #                                             is_core=True)

    collection_etl = CollectionETL(model_name=entity.lower(), 
                                source=None, 
                                entity_type="collection",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                primary_key_column="projectId")
    return collection_etl


def handle_contact_object(org_id, creds, project_type_id:int, entity:str):
    fv_config = FileVineConfig(org_id=org_id, user_id=creds["user_id"], api_key=creds["api_key"])


    # selected_column_config = get_config_of_section(selected_config=selected_field_config, 
    #                                             section_name=entity.lower(), 
    #                                             project_type_id=project_type_id,
    #                                             is_core=True)

    contact_etl = ContactETL(model_name="contact", 
                                source=None, 
                                entity_type="core",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=None,
                                primary_key_column="projectId")
    return contact_etl


def get_fv_etl_object(org_id, creds, entity_type, entity_name, project_type_id=None):
    cls = None
    if entity_type.lower() == "project":
        cls = handle_project_object(org_id, creds, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "form":
        cls = handle_form_object(org_id, creds, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "collections":
        cls = handle_collection_object(org_id, creds, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "contact":
        cls = handle_contact_object(org_id, creds, entity=entity_name, project_type_id=project_type_id)
    else:
        raise Exception("Unknown entity type")
    return cls    


def get_ld_etl_object(org_config: LeadSelectedConfig, entity_name:str):
    cls = None
    # if entity_name == "statuses" or entity_name == 'leadsource' or entity_name == 'casetype':
        # cls = handle_project_object(org_config, entity=entity_name, project_type_id=project_type_id)
    cls = ld_handle_object(org_config, entity=entity_name)

    return cls    


def ld_handle_object(org_id:str, entity:str, creds):
    ld_config = LeadDocketConfig(org_id, creds["base_url"])

    if entity == "statuses" or entity == 'leadsource' or entity == 'casetype':
        etl_object = CoreETL(
                    model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"])
    elif entity == "leadrow":
        etl_object = LeadRowETL(model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"]
                   )
    elif entity == "leaddetail":
       
        etl_object = LeadDetailETL(model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"])
    elif entity == "contact":
        etl_object = LeadContactETL(model_name=entity, 
                    ld_config=ld_config, 
                    api_key= creds["api_key"]   
                    )
    elif entity == "opportunities":
        etl_object = LeadOpportETL(model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"]
                    )
    elif entity == "referrals":
        etl_object = LeadReferralsETL(model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"]
                    )
    elif entity == "users":
        etl_object = LeadUsersETL(model_name=entity, 
                    ld_config=ld_config,
                    api_key= creds["api_key"]
                    )
    else:
        return 0
    return etl_object
