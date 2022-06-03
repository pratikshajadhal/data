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
        
        print(contact_schema)

        distinct_data_type = {}
        
        #for cf in contact_schema:
        #    distinct_data_type[cf['customFieldType']] = ""
            
        #print(distinct_data_type)
        #Contact ID Field
        #contact_schema.append({"fieldName" : "Contact ID", "selector" : "personId", "value" : "object"})
        
        self.source_schema = contact_schema

        for field in self.source_schema:
            print(field["selector"])

        #exit()
        
        self.persist_source_schema()

        return contact_schema

    def get_projects(self) -> list[int]:
        project_data_list = self.fv_client.get_projects(requested_fields=["projectId"])
        project_list = [project_data["projectId"]["native"] for project_data in project_data_list]
        return project_list

    def extract_data_from_source(self, project_list:list[int]=[]):
        final_contact_list = []
        contact_list = self.fv_client.get_contacts()
        return contact_list

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ContactETL(source=ETLSource(end_point=""), )
