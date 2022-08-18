from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client
from utils import get_logger

logger = get_logger(__name__)

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

        return flattend_map

    def get_schema_of_model(self) -> Dict:
        logger.debug(f"Getting Schema of model {self.model_name}")
        form_schema = self.fv_client.get_section_metadata(projectTypeId=self.project_type, section_name=self.model_name)
        
        distinct_data_type = {}
        for cf in form_schema["customFields"]:
            distinct_data_type[cf['customFieldType']] = ""
            
        self.source_schema = form_schema["customFields"]

        self.persist_source_schema()

        return form_schema

    def get_projects(self) -> list[int]:
        project_data_list = self.fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
        project_list = [project_data["projectId"]["native"] for project_data in project_data_list if project_data["projectTypeId"]["native"] == int(self.project_type) ]
        return project_list

    def extract_data_from_source(self, project_list:list[int]=[]):
        section_data_list = []
        for index, project in enumerate(project_list):
            logger.debug(f"Getting {self.entity_type} for project {project} {index}")
            section_data = self.fv_client.get_section_data(project_id=project, section_name=self.model_name)
            if not section_data:
                continue
            
            section_data["projectId"] = project
            section_data_list = section_data_list + [section_data]

        return section_data_list

    def trigger_etl(self, project_list:list[int], dest_col_format):
        for project in project_list[:500]:
            if project > 10813786:
                continue
            form_data_list = self.extract_data_from_source(project_list=[project])

            form_df = self.transform_data(record_list=form_data_list)

            if form_df.shape[0] == 0:
                print("Empty dataframe")
                continue
            
            self.load_data_to_destination(trans_df=form_df, schema=dest_col_format, project=project)

            #count = count + 1

            #print("Total processed {}".format(count))


    def get_snapshot(self, project_type_id):
        project_list = self.fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
        for project in project_list:
            if project["projectTypeId"]["native"] == project_type_id:
                snapshot_data = self.extract_data_from_source(project_list=[project["projectId"]["native"]])
                return snapshot_data[0]
        return {}
    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    #ETLDestination(name="contact_model")
    #ContactETL(source=ETLSource(end_point=""), )
    