from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client

class ProjectTypeETL(ModelETL):

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        
        for field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : "string"}

        flattend_map[self.key_column] = {"type" : "int"}

        return flattend_map

    def get_schema_of_model(self) -> Dict:
        return []

    def extract_data_from_source(self, project_list:list[int]=[]):
        final_contact_list = []
        project_type_list = self.fv_client.get_projecttypes()
        for project_type in project_type_list:
            project_type["projectTypeId"] = project_type["projectTypeId"]["native"]
            project_type_phases = self.fv_client.get_projecttypes_phases(project_type_id=project_type["projectTypeId"])
            for project_type_phase in project_type_phases:
                project_type_phase["phaseId"] = project_type_phase["phaseId"]["native"]
                project_type_phase.pop("links", None)
            project_type["phases"] = project_type_phases
        return project_type_list

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ProjectETL(source=ETLSource(end_point=""), )
 