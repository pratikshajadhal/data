from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client
from utils import get_logger

logger = get_logger(__name__)

class CollectionETL(ModelETL):

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        for field in source_schema:
            field_data_type = field["customFieldType"]
            field_name = field["fieldSelector"].replace("custom.", "")
            if field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : field_data_type}

        flattend_map[self.key_column] = {"type" : "Id"}
        flattend_map["projectId"] = {"type" : "ProjectId"}
        
        unique_data_type = {}
        for key, value in flattend_map.items():
            unique_data_type[value["type"]] = ""

        return flattend_map
    
    def get_schema_of_model(self) -> Dict:
        form_schema = self.fv_client.get_section_metadata(projectTypeId=self.project_type, section_name=self.model_name)
        
        distinct_data_type = {}
        for cf in form_schema["customFields"]:
            distinct_data_type[cf['customFieldType']] = ""

        self.source_schema = form_schema["customFields"]

        self.persist_source_schema()

        return form_schema

    def get_projects(self) -> list[int]:
        project_data_list = self.fv_client.get_projects(requested_fields=["projectId"])
        project_list = [project_data["projectId"]["native"] for project_data in project_data_list]
        return project_list

    def extract_data_from_source(self, project_list:list[int]=[]):
        section_data_list = []
        for index, project in enumerate(project_list):
            logger.debug(f"Getting {self.entity_type} for project {project} {index}")
            section_data = self.fv_client.get_collections(project_id=project, collection_name=self.model_name)
            if not section_data:
                continue
            for section in section_data:
                processed_section = section["dataObject"]
                processed_section["projectId"] = project
                processed_section["id"] = section["itemId"]["native"]
                section_data_list.append(processed_section)

        return section_data_list

