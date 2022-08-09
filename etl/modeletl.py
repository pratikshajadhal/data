import os
from ast import List
from typing import Dict
from etl.datamodel import ColumnConfig, ColumnDefn, ETLDestination, ETLSource, FileVineConfig
import pandas as pd
from .destination import ETLDestination, S3Destination
import filevine.client as fv_client
import json

class ModelETL(object):
    
    def __init__(self, model_name:str, 
                    source:ETLSource, 
                    entity_type:str,
                    project_type:str,
                    destination:ETLDestination,
                    fv_config:FileVineConfig, 
                    primary_key_column:str,
                    column_config:ColumnConfig = None):
        self.model_name = model_name
        self.column_config = column_config
        self.source = source
        self.destination = destination
        self.source_df = None
        self.fv_client = fv_client.FileVineClient(org_id=fv_config.org_id, user_id=fv_config.user_id, api_key=fv_config.api_key)
        self.flattend_map = None
        self.source_schema = None
        self.key_column = primary_key_column
        self.project_type = project_type
        self.entity_type = entity_type

        if column_config:
            self.column_config.fields.append(self.key_column)
        
    def persist_source_schema(self):
        directory = os.getcwd()
        if not os.path.exists(f"{directory}/schemas/"):
            os.makedirs(f"{directory}/schemas/")
        with open(f"{directory}/schemas/{self.model_name}.json", "w") as f:
            f.write(json.dumps(self.source_schema))

    def get_schema_of_model(self)-> Dict:
        return {}

    def extract_data_from_source(self) -> List:
        return []

    def get_filtered_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        
        for field in source_schema:
            field_data_type = field["value"]
            field_name = field["selector"].replace("custom.", "")
            if field_name in self.column_config.fields:
                flattend_map[field_name] = {"type" : field_data_type}

        flattend_map[self.key_column] = {"type" : "Id"}
        flattend_map["projectId"] = {"type" : "int"}

        return flattend_map

    def convert_schema_into_destination_format(self, source_flattened_schema:Dict):
        dest_col_defn : list[ColumnDefn] = []

        column_mapper = self.destination.get_column_mapper()

        for col, field_config in source_flattened_schema.items():
            if field_config["type"] == "Header" or field_config["type"] == "DocGen" or field_config["type"] == "ActionButton" or field_config["type"] == "MultiDocGen" or field_config["type"] == "DocList" or field_config["type"] == "Doc" or field_config["type"] == "ReportFusion":
                    continue
                
            dest_col_defn.append(ColumnDefn(name=col, data_type=column_mapper[field_config["type"]]))

        return dest_col_defn

    
    def transform_data(self, record_list:list):
        transformed_record_list = []

        for record in record_list:
            post_processed_record = {}
            for key, value in record.items():
                if key not in self.flattend_map:
                    #print(f"{key} not found in contact")
                    continue
                field_config = self.flattend_map[key]
                if field_config["type"] == "Header" or field_config["type"] == "DocGen" or field_config["type"] == "ActionButton" or field_config["type"] == "MultiDocGen" or field_config["type"] == "DocList" or field_config["type"] == "ReportFusion":
                    continue
                elif field_config["type"] == "Id":
                    if isinstance(value, dict):
                        field_value = value["native"]
                    else:
                        field_value = value
                elif field_config["type"] == "object":
                    if isinstance(value, dict):
                        #TODO Flatten nested data
                        #for subkey, subvalue in value.items():
                        #    post_processed_record[f"{key}__{subkey}"] = subvalue
                        post_processed_record[key] = value
                        continue
                    if isinstance(value, list):
                        field_value = value
                elif field_config["type"] == "PersonLink":
                    if value:
                        if isinstance(value, Dict):
                            field_value = value["id"]
                    else:
                        field_value = None
                elif field_config["type"] == "PersonList":
                    if value:
                        field_value = '|'.join([str(person["id"]) for person in value]) 
                    else:
                        field_value = ""
                    
                
                elif field_config["type"] == "StringList":
                    field_value = '|'.join(value)
                elif isinstance(value, list):
                    field_value = '|'.join(value)
                
                else:
                    field_value = value

                post_processed_record[key] = field_value
            #print(post_processed_record["personTypes"])
            transformed_record_list.append(post_processed_record)

        return pd.DataFrame(transformed_record_list)


    def load_data_to_destination(self, trans_df:pd.DataFrame, schema:list[ColumnDefn], project:int) -> pd.DataFrame:
        dest = self.destination

        dest_map = {}

        col_list = list(trans_df)
        schema_map = {}
        
        
        for dest_col in schema:
            if dest_col.name in col_list:
                dest_map[dest_col.name] = dest_col.data_type

        if isinstance(dest, S3Destination):
            dest.load_data(trans_df, 
                        project_type=self.project_type, 
                        section=self.entity_type, 
                        entity=self.model_name,
                        dtype=dest_map,
                        project=project
                        )

        
        #dest.create_redshift_table(column_def=schema, 
        #                    redshift_table_name=f"{self.model_name}_raw")
        #from destination import RedShiftDestination
        #rs_dest = RedShiftDestination(dest_config)
        #rs_dest.initialize_destination(table_name="contact")
        #dest.load_data(trans_df)

        return 0

    def start_etl(self):
        self.extract_data_from_source()