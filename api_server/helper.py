from __future__ import annotations

from .config import FVContactWebhookInput, FVWebhookInput
from etl.datamodel import FileVineConfig, SelectedConfig, ColumnDefn
from etl.destination import S3Destination
from etl.form import FormETL
from etl.project import ProjectETL
from etl.collections import CollectionETL
from etl.contact import ContactETL
from utils import load_config, get_config_of_section, get_logger

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
                                entity_type="collections",
                                project_type=wb_input.project_type_id,
                                destination=S3Destination(org_id=wb_input.org_id), 
                                fv_config=fv_config, 
                                column_config=selected_column_config, 
                                primary_key_column="projectId")
    return collection_etl


def handle_contact_object(wb_input:FVContactWebhookInput, selected_field_config:SelectedConfig):
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    selected_column_config = get_config_of_section(
        selected_config=selected_field_config,
        section_name=wb_input.entity.lower(),
        project_type_id=None,
        is_core=True
        )

    contact_etl = ContactETL(
        model_name="contact",
        source=None,
        entity_type="core",
        project_type=None,
        destination=S3Destination(org_id=wb_input.org_id),
        fv_config=fv_config,
        column_config=selected_column_config,
        primary_key_column="projectId"
        )

    return contact_etl


def process_webhook_contact(cls: ContactETL, wb_input: FVContactWebhookInput) -> None:
    """_summary_: Handle contact webhook

    Args:
        cls (ContactETL): _description_
        wb_input (FVContactWebhookInput): _description_
    """
    # Generate schema
    source_schema = cls.get_schema_of_model()
    cls.flattend_map = cls.get_filtered_schema(source_schema)
    dest_col_format = cls.convert_schema_into_destination_format(cls.flattend_map)

    # Extract data from fv        
    entity_data = cls.extract_data_from_source(project_list=[wb_input.project_id], bring_one=True, person_id = wb_input.person_id)
    entity_df = cls.transform_data(record_list=[entity_data])
    
    # Append extra columns to both df and schema.
    extra_webhook_columns = {"Event": 'string', "Timestamp": 'bigint'}
    for field_name, field_type in extra_webhook_columns.items():
        df_column_name = "webhook_{}".format(field_name.lower())

        entity_df[df_column_name] = wb_input.webhook_body.get(field_name)
        dest_col_format.append(ColumnDefn(name=df_column_name, data_type=field_type))

    # Load to s3. contact/{person_id}.parquet
    cls.load_data_to_destination(
        trans_df=entity_df,
        schema=dest_col_format, 
        project=wb_input.project_id,
        extra_params = {"person_id": wb_input.webhook_body["ObjectId"].get("PersonId", "1")}
    )


def process_webhook_phase_changed(wb_input:FVWebhookInput):
    """ Handles Phasechanged webhook 

    Args:
        wb_input (FVWebhookInput): _description_
    """
    s3_dest = S3Destination(org_id=wb_input.org_id)
    key = f"filevine/{wb_input.org_id}/{wb_input.project_type_id}/{wb_input.project_id}/phases/{wb_input.event_timestamp}.parquet"
    logger.info(f"PhaseChanged event {key}")
    phase_name = wb_input.webhook_body["Other"]["PhaseName"]
    s3_dest.save_project_phase(s3_key=key, project_id=wb_input.project_id, phase_name=phase_name)
        

def handle_wb_input(wb_input: FVWebhookInput | FVContactWebhookInput):
    """_summary_ Handles webhook inputs for incoming entity.

    Args:
        wb_input (FVWebhookInput | FVContactWebhookInput): _description_

    Returns:
        _type_: _description_
    """
    logger.debug("inside handle_wb_input()")
    selected_field_config = load_config(file_path="confs/src.yaml")

    if wb_input.entity == "Project":
        if wb_input.event_name == "PhaseChanged":
            process_webhook_phase_changed(wb_input)
            return
        else:
            cls = handle_project_object(wb_input, selected_field_config)
    elif wb_input.entity == "Form":
        cls = handle_form_object(wb_input, selected_field_config)
    elif wb_input.entity == "CollectionItem":
        cls = handle_collection_object(wb_input, selected_field_config)
    elif wb_input.entity == "Contact":
        # Get appropriate object for etl.
        cls = handle_contact_object(wb_input, selected_field_config)
        process_webhook_contact(cls, wb_input)
        return
    else:
        return None

    cls.get_schema_of_model()

    cls.flattend_map = cls.get_filtered_schema(cls.source_schema)

    dest_col_format = cls.convert_schema_into_destination_format(cls.flattend_map)

    entity_data = cls.extract_data_from_source(project_list=[wb_input.project_id])

    entity_df = cls.transform_data(record_list=entity_data)

    cls.load_data_to_destination(
        trans_df=entity_df,
        schema=dest_col_format,
        project=wb_input.project_id
        )

    # TODO - Handle delete event specifically for Collections
