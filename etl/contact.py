from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client

class ContactETL(ModelETL):

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        
        for field in source_schema:
            print(field)
            field_data_type = field["value"]
            field_name = field["selector"].replace("custom.", "")
            if field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : field_data_type}

        flattend_map[self.key_column] = {"type" : "Id"}
        flattend_map["projectId"] = {"type" : "ProjectId"}
        flattend_map["personTypes"] = {"type": "string"}

        return flattend_map

    def get_schema_of_model(self) -> Dict:
        contact_schema = self.fv_client.get_contact_metadata()
        
        distinct_data_type = {}
        
        self.source_schema = contact_schema

        self.persist_source_schema()

        return contact_schema

    def get_projects(self) -> list[int]:
        project_data_list = self.fv_client.get_projects(requested_fields=["projectId"])
        project_list = [project_data["projectId"]["native"] for project_data in project_data_list]
        return project_list

    def extract_data_from_source(self, project_list:list[int]=[], bring_one:bool=False):
        final_contact_list = []
        if not bring_one:
            contact_list = self.fv_client.get_contacts()
        else:
            contact_list = self.fv_client.get_single_contact()
        return contact_list


    def get_snapshot(self, project_type_id, project_list):
        # No need to get projects. TODO: Delete line when you sure about endpoint.
        # **core/contacts** or **core/projects/{project_id}/contacts** ?

        # One caveat, when we get snapshot for contacts response may change. It may cause some conflict.Check this

        # project_list = self.fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
        for project in project_list:
            if project["projectTypeId"]["native"] == project_type_id:
                snapshot_data = self.extract_data_from_source(project_list=[project["projectId"]["native"]], bring_one=True)
                if len(snapshot_data) != 0:
                    return snapshot_data[0]                    
        return {}

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ContactETL(source=ETLSource(end_point=""), )
