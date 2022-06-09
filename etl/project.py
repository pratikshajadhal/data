from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client

class ProjectETL(ModelETL):

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        
        for  field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : "string"}

        flattend_map[self.key_column] = {"type" : "int"}

        return flattend_map

    def get_schema_of_model(self) -> Dict:
        return []

    def extract_data_from_source(self, project_list:list[int]=[]):
        final_contact_list = []
        project_list = self.fv_client.get_projects()
        for project in project_list:
            if project["projectTypeId"]["native"] == self.project_type:
                project["projectId"] = project["projectId"]["native"]
                final_contact_list.append(project)
        print(len(final_contact_list))
        return final_contact_list

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ProjectETL(source=ETLSource(end_point=""), )
 