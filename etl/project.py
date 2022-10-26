from typing import Dict

import pandas as pd

from .datamodel import ColumnDefn, ETLDestination, ETLSource, RedshiftConfig
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
        
        #if len(project_list) > 1:
        #    raise Exception("More than 1 project_list is not supported in this entity")
        
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


    def get_snapshot(self, project_type_id):
        project_list = self.fv_client.get_projects(requested_fields=["projectId", "projectTypeId"])
        for project in project_list:
            print(project)
            if project["projectTypeId"]["native"] == project_type_id:
                snapshot_data = self.fv_client.get_projects(project_list=[project["projectId"]["native"]])
                return snapshot_data[0]
        return {}
        
    def trigger_etl(self, project_list:list[int], dest_col_format):
        for contact in project_list:
            try:
                contact_df = self.transform_data(record_list=[contact])
                projectId = contact_df["projectId"].tolist()[0]
                project_vital = self.fv_client.get_project_vital(project_id=contact["projectId"])
                #project_record = {"fieldName" : "projectId", 
                #                "friendlyName" : "projectId",
                #                "fieldType" : "string",
                #                "value" : f"{contact['projectId']}",
                #                }
                #project_vital.append(project_record)
                vital_df = pd.DataFrame(project_vital)
                vital_schema = [ColumnDefn(name="fieldName", data_type="string"),
                            ColumnDefn(name="friendlyName", data_type="string"),
                            ColumnDefn(name="fieldType", data_type="string"),
                            ColumnDefn(name="value", data_type="string"),
                            ColumnDefn(name="position", data_type="string"),
                            ColumnDefn(name="links", data_type="string")]
                self.load_data_to_destination(trans_df=contact_df, schema=dest_col_format, project=projectId)
                self.load_data_to_destination(trans_df=vital_df, schema=vital_schema, project=projectId, extra_params={"subentity" : "vitals"})
            except Exception as e:
                print(f"Error::::: processing in project {contact} {e}")        
            

    
if __name__ == "__main__":
    RedshiftConfig(table_name="fv_contact_raw", schema_name="pipeline_dev", dbname="dev")
    ETLDestination(name="contact_model")
    ProjectETL(source=ETLSource(end_point=""), )
 