from etl.collections import CollectionETL
from etl.datamodel import FileVineConfig, SelectedConfig, LeadDocketConfig, LeadSelectedConfig
from etl.form import FormETL
from etl.project import ProjectETL
from etl.lead.core import CoreETL 
from etl.lead.lead_row import LeadRowETL
from etl.lead.lead_detail import LeadDetailETL
from etl.lead.lead_contact import LeadContactETL
from etl.lead.lead_opport import LeadOpportETL
from etl.lead.lead_referrals import LeadReferralsETL
from etl.lead.lead_users import LeadUsersETL
from utils import get_config_of_section, get_config_of_lead_section

def handle_project_object(selected_field_config:SelectedConfig, project_type_id:int, entity:str):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=entity.lower(), 
                                                project_type_id=project_type_id,
                                                is_core=True)

    project_etl = ProjectETL(model_name="project", 
                                source=None, 
                                entity_type="core",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=selected_column_config,
                                primary_key_column="projectId")
    return project_etl

def handle_form_object(selected_field_config:SelectedConfig, project_type_id:int, entity:str):
    
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)


    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=entity.lower(), 
                                                project_type_id=project_type_id,
                                                is_core=True)

    form_etl = FormETL(model_name=entity.lower(), 
                                source=None, 
                                entity_type="form",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=selected_column_config, 
                                primary_key_column="projectId")
    return form_etl

def handle_collection_object(selected_field_config:SelectedConfig, project_type_id:int, entity:str):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)


    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=entity.lower(), 
                                                project_type_id=project_type_id,
                                                is_core=True)

    collection_etl = CollectionETL(model_name=entity.lower(), 
                                source=None, 
                                entity_type="collection",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=selected_column_config, 
                                primary_key_column="projectId")
    return collection_etl


def get_fv_etl_object(org_config:SelectedConfig, entity_type, entity_name, project_type_id=None):
    cls = None
    if entity_type.lower() == "project":
        cls = handle_project_object(org_config, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "form":
        cls = handle_form_object(org_config, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "collections":
        cls = handle_collection_object(org_config, entity=entity_name, project_type_id=project_type_id)

    return cls    


def get_ld_etl_object(org_config: LeadSelectedConfig, entity_name:str):
    cls = None
    # if entity_name == "statuses" or entity_name == 'leadsource' or entity_name == 'casetype':
        # cls = handle_project_object(org_config, entity=entity_name, project_type_id=project_type_id)
    cls = ld_handle_object(org_config, entity=entity_name)

    return cls    


def ld_handle_object(selected_field_config:LeadSelectedConfig, entity:str):
    ld_config = LeadDocketConfig(selected_field_config.org_id, selected_field_config.base_url)


    if entity == "statuses" or entity == 'leadsource' or entity == 'casetype':
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = CoreETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "leadrow":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = LeadRowETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "leaddetail":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = LeadDetailETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "contact":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = LeadContactETL(model_name=section.name, 
                    ld_config=ld_config,    
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "opportunities":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]        
        etl_object = LeadOpportETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "referrals":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = LeadReferralsETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    elif entity == "users":
        section = get_config_of_lead_section(selected_config=selected_field_config, 
                                                section_name=entity.lower())[0]
        etl_object = LeadUsersETL(model_name=section.name, 
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=None)
    else:
        return 0
    return etl_object

    # collection_etl = CollectionETL(model_name=entity.lower(), 
    #                             source=None, 
    #                             entity_type="collection",
    #                             project_type=project_type_id,
    #                             destination=None, 
    #                             fv_config=fv_config, 
    #                             column_config=selected_column_config, 
    #                             primary_key_column="projectId")
    # return collection_etl
