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
        if len(project_list) > 1:
            raise Exception("More than 1 project_list is not supported in this entity")
        
        project_list = self.fv_client.get_projects(project_list)
        
        
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

    def start_etl(self):
        self.get_schema_of_model()

        self.flattend_map = self.get_filtered_schema(self.source_schema)

        dest_col_format = self.convert_schema_into_destination_format(self.flattend_map)

        count = 0
        
        contact_list = self.extract_data_from_source()

        for contact in contact_list:
            contact_df = self.transform_data(record_list=[contact])
            projectId = contact_df["projectId"].tolist()[0]
            self.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=projectId)
            
        print("Total processed {}".format(count))


    
if __name__ == "__main__":
    print("Write test cases")
 