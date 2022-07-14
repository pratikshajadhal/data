from etl.collections import CollectionETL
from etl.datamodel import FileVineConfig, SelectedConfig
from etl.form import FormETL
from etl.project import ProjectETL
from etl.contact import ContactETL
from utils import get_config_of_section

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


def handle_contact_object(selected_field_config:SelectedConfig, project_type_id:int, entity:str):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=entity.lower(), 
                                                project_type_id=project_type_id,
                                                is_core=True)

    contact_etl = ContactETL(model_name="contact", 
                                source=None, 
                                entity_type="core",
                                project_type=project_type_id,
                                destination=None, 
                                fv_config=fv_config, 
                                column_config=selected_column_config,
                                primary_key_column="projectId")
    return contact_etl

def get_fv_etl_object(org_config:SelectedConfig, entity_type, entity_name, project_type_id=None):
    cls = None
    if entity_type.lower() == "project":
        cls = handle_project_object(org_config, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "form":
        cls = handle_form_object(org_config, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "collections":
        cls = handle_collection_object(org_config, entity=entity_name, project_type_id=project_type_id)
    elif entity_type.lower() == "contact":
        cls = handle_contact_object(org_config, entity=entity_name, project_type_id=project_type_id)
    else:
        raise Exception("Unknown entity type")
    return cls    
