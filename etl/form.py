from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client

class FormETL(ModelETL):

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        for field in source_schema:
            field_data_type = field["customFieldType"]
            field_name = field["fieldSelector"].replace("custom.", "")
            if field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : field_data_type}

        flattend_map[self.key_column] = {"type" : "ProjectId"}

        
        unique_data_type = {}
        for key, value in flattend_map.items():
            unique_data_type[value["type"]] = ""

    
        #print(flattend_map)
        #exit()
        return flattend_map

    def get_schema_of_model(self) -> Dict:
        form_schema = self.fv_client.get_section_metadata(projectTypeId=self.project_type, section_name=self.model_name)
        
        distinct_data_type = {}
        for cf in form_schema["customFields"]:
            distinct_data_type[cf['customFieldType']] = ""
            
        #print(distinct_data_type)
        #Contact ID Field
        #contact_schema.append({"fieldName" : "Contact ID", "selector" : "personId", "value" : "object"})
        
        self.source_schema = form_schema["customFields"]

        for field in self.source_schema:
            print(field["fieldSelector"])

        #exit()
        
        self.persist_source_schema()

        return form_schema

    def get_projects(self) -> list[int]:
        project_data_list = self.fv_client.get_projects(requested_fields=["projectId"])
        project_list = [project_data["projectId"]["native"] for project_data in project_data_list]
        return project_list

    def extract_data_from_source(self, project_list:list[int]=[]):
        section_data_list = []
        for index, project in enumerate(project_list):
            print(f"Getting contact for project {project} {index}")
            section_data = self.fv_client.get_section_data(project_id=project, section_name=self.model_name)
            section_data["projectId"] = project
            if not section_data:
                continue
            section_data_list = section_data_list + [section_data]

        return section_data_list

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    #ContactETL(source=ETLSource(end_point=""), )
