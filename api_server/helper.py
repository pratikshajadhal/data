from etl.datamodel import  FileVineConfig, SelectedConfig
from etl.destination import S3Destination
from .config import FVWebhookInput
from etl.helper import get_fv_etl_object, get_ld_etl_object
from etl.form import FormETL
from etl.project import ProjectETL
from etl.collections import CollectionETL
from utils import load_config, get_config_of_section, get_logger
from filevine.client import FileVineClient
from api_server.exceptions import AuthErr

logger = get_logger(__name__)

def handle_project_object(wb_input:FVWebhookInput, selected_field_config:SelectedConfig):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=wb_input.entity.lower(), 
                                                project_type_id=wb_input.project_type_id,
                                                is_core=True)

    project_etl = ProjectETL(model_name="project", 
                                source=None, 
                                entity_type="core",
                                project_type=wb_input.project_type_id,
                                destination=S3Destination(org_id=wb_input.org_id), 
                                fv_config=fv_config, 
                                column_config=selected_column_config,
                                primary_key_column="projectId")
    return project_etl

def handle_form_object(wb_input:FVWebhookInput, selected_field_config:SelectedConfig):
    
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)


    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=wb_input.section, 
                                                project_type_id=wb_input.project_type_id,
                                                is_core=True)

    form_etl = FormETL(model_name=wb_input.section, 
                                source=None, 
                                entity_type="form",
                                project_type=wb_input.project_type_id,
                                destination=S3Destination(org_id=wb_input.org_id), 
                                fv_config=fv_config, 
                                column_config=selected_column_config, 
                                primary_key_column="projectId")
    return form_etl

def handle_collection_object(wb_input:FVWebhookInput, selected_field_config:SelectedConfig):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)


    selected_column_config = get_config_of_section(selected_config=selected_field_config, 
                                                section_name=wb_input.section, 
                                                project_type_id=wb_input.project_type_id,
                                                is_core=True)

    collection_etl = CollectionETL(model_name=wb_input.section, 
                                source=None, 
                                entity_type="collection",
                                project_type=wb_input.project_type_id,
                                destination=S3Destination(org_id=wb_input.org_id), 
                                fv_config=fv_config, 
                                column_config=selected_column_config, 
                                primary_key_column="projectId")
    return collection_etl


def handle_wb_input(wb_input:FVWebhookInput):
    logger.debug("inside handle_wb_input()")

    selected_field_config = load_config(file_path="src.yaml")
    

    if wb_input.entity == "Project":
        if wb_input.event_name == "PhaseChanged":
            s3_dest = S3Destination(org_id=wb_input.org_id)
            key = f"filevine/{wb_input.org_id}/{wb_input.project_type_id}/{wb_input.project_id}/phases/{wb_input.event_timestamp}.parquet"
            logger.info(f"PhaseChanged event {key}")
            phase_name = wb_input.webhook_body["Other"]["PhaseName"]
            s3_dest.save_project_phase(s3_key=key, project_id=wb_input.project_id, phase_name=phase_name)
            return
        else:    
            cls = handle_project_object(wb_input, selected_field_config)
    elif wb_input.entity == "Form":
        cls = handle_form_object(wb_input, selected_field_config)
    elif wb_input.entity == "CollectionItem":
        cls = handle_collection_object(wb_input, selected_field_config)
    
    else:
        return None
    
    cls.get_schema_of_model()

    cls.flattend_map = cls.get_filtered_schema(cls.source_schema)

    dest_col_format = cls.convert_schema_into_destination_format(cls.flattend_map)

    entity_data = cls.extract_data_from_source(project_list=[wb_input.project_id])

    entity_df = cls.transform_data(record_list=entity_data)
                
    cls.load_data_to_destination(trans_df=entity_df, schema=dest_col_format, project=wb_input.project_id)

                
    #TODO - Handle delete event specifically for Collections


# -- - - - - - - - - - - - - - - - - - - - - - - - - - -  TPA Onboarding grooming

def get_pre_needs(fv_client: FileVineClient):
    project_list = fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
    # project_type_ids = fv_client.get_all_project_type_ids() # Will be commented out
    project_type_ids = [18764] # TODO: it will be for all project_type_ids. TODO: delete it.
    logger.info("Project list and project_type_ids has been fetched!")

    return project_list, project_type_ids


def get_all_snapshot(fv_client: FileVineClient,section_data, org_id, creds, project_list, project_type_ids):
    entities = list()

    temp_entities = ["casesummary", "intake", "meds","project", "contact"]
    # temp_entities = ["casesummary", "intake", "meds", "negotiations","project", "contact"]
    for each_entity in section_data:
        output = dict()
        entity_name = each_entity["id"]
        if entity_name in temp_entities: #TODO: delete. Currently we are doing just for temp_entities
            print(f"entity name {entity_name} is processing")
            if each_entity["isCollection"] == True:
                etl_object = get_fv_etl_object(org_id=org_id, creds=creds, entity_type="collections", entity_name=entity_name, project_type_id=project_type_ids[0])


            elif each_entity["isCollection"] == False:
                etl_object = get_fv_etl_object(org_id=org_id, creds=creds, entity_type="form", entity_name=entity_name, project_type_id=project_type_ids[0])


            snapshot = etl_object.get_snapshot(project_type_ids[0], project_list)
            section = fv_client.get_section_metadata(projectTypeId=project_type_ids[0], section_name=entity_name)
            output["name"] = entity_name
            output["fields"] = section["customFields"]
            output["snapshot"] = snapshot

            entities.append(output)
        else:
            # Currently skipping
            continue

    return entities


def onboard_fv(org_id, creds):
    fv_client = FileVineClient(org_id=org_id, user_id=creds.user_id, api_key=creds.api_key)
    try:
        check_auth = fv_client.get_keys()
    except:
        raise AuthErr()


    project_list, project_type_ids = get_pre_needs(fv_client)
    for each_pt_id in project_type_ids:
        section_data = fv_client.get_sections(projectTypeId=each_pt_id)["items"]
    section_data = [{"id" : section["sectionSelector"], "name": section["name"], "isCollection" : section["isCollection"]} for section in section_data]
    
    # Get entities to be returned: Entity, section, snapshot
    # TODO: add project and contacts snapshot.
    # TODO: solve project_type_id based solution. Whic project id do we need to get??
    entities = get_all_snapshot(fv_client, section_data, org_id, creds, project_list, project_type_ids)
    message = "Success, custom mapping required, snapshot success, grooming file returned"

    return message, entities, project_type_ids[0]


def onboard_ld():
    #TODO:
    message =  "Success, custom mapping required, snapshot success, grooming file returned"
    data = "TODO:"
    return message, data
    pass


def onboard_social():
    #TODO:
    message = "Success, no custom mapping required"
    return message, "None"
    pass



# -- - - - - - - - - - - - - TPA parts- - - - - - - - - - - - - -  















# Flink dene
