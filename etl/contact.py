from typing import Dict

import pandas as pd

from .datamodel import ETLDestination, ETLSource, RedshiftConfig
from .modeletl import ModelETL
from filevine import client

class ContactETL(ModelETL):

    def get_schema_of_model(self) -> Dict:
        contact_schema = self.fv_client.get_contact_metadata()
        
        #Contact ID Field
        #contact_schema.append({"fieldName" : "Contact ID", "selector" : "personId", "value" : "object"})
        
        self.source_schema = contact_schema
        
        self.persist_source_schema()
        return contact_schema

    def extract_data_from_source(self, project_list:list[int]=[]):
        final_contact_list = []
        for project in project_list:
            contact_list = self.fv_client.get_contacts(project_id=project)
            final_contact_list = final_contact_list + contact_list

        return final_contact_list

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ContactETL(source=ETLSource(end_point=""), )
