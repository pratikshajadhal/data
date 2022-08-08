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
        project_list = self.fv_client.get_projects(project_list)
        
        if len(project_list) > 1:
            raise Exception("More than 1 project_list is not supported in this entity")
        
        for project in project_list:
            if self.project_type is not None and project["projectTypeId"]["native"] == self.project_type:
                project["projectId"] = project["projectId"]["native"]
                final_contact_list.append(project)
            else:
                project["projectId"] = project["projectId"]["native"]
                
                #VERY IMP. It is initialized only for Webhook as in WEbhook we do not get ProjectTypeID
                self.project_type = project["projectTypeId"]["native"] 

                final_contact_list.append(project)
        
        return final_contact_list


    def get_snapshot(self, project_type_id, project_list):
        # project_list = self.fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
        for project in project_list:
            print(project)
            if project["projectTypeId"]["native"] == project_type_id:
                snapshot_data = self.fv_client.get_projects(project_list=[project["projectId"]["native"]])
                return snapshot_data[0]
        return {}
    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ProjectETL(source=ETLSource(end_point=""), )
 