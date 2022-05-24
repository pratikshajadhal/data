from ast import List
from typing import Dict
from etl.datamodel import ColumnDefn, ETLDestination, ETLSource, FileVineConfig
import pandas as pd
from .destination import RedShiftDestination
import filevine.client as fv_client
import json

import settings

class ModelETL(object):
    
    def __init__(self, model_name:str, source:ETLSource, destination:RedShiftDestination, fv_config:FileVineConfig):
        self.model_name = model_name
        self.source = source
        self.destination = destination
        self.source_df = None
        self.fv_client = fv_client.FileVineClient(org_id=fv_config.org_id, user_id=fv_config.user_id)
        self.flattend_map = None
        self.source_schema = None

    def persist_source_schema(self):
        with open(f"{settings.SCHEMA_DIR}/{self.model_name}.json", "w") as f:
            f.write(json.dumps(self.source_schema))

    def get_schema_of_model(self)-> Dict:
        return {}

    def extract_data_from_source(self) -> List:
        return []

    def flatten_schema(self, source_schema:Dict) -> Dict:
        flattend_map = {}
        for field in source_schema:
            field_data_type = field["value"]
            flattend_map[field["selector"].replace("custom.", "")] = {"type" : field_data_type}

        return flattend_map

    def convert_schema_into_destination_format(self, source_flattened_schema:Dict, destination:str="redshift"):
        dest_col_defn : list[ColumnDefn] = []

        column_mapper = self.destination.get_column_mapper()

        for col, field_config in source_flattened_schema.items():
            print(f"{col}{field_config}")
            dest_col_defn.append(ColumnDefn(name=col, data_type=column_mapper[field_config["type"]]))

        return dest_col_defn

    def transform_data(self, record_list:list):
        transformed_record_list = []

        self.get_schema_of_model()

        self.flattend_map = self.flatten_schema(self.source_schema)
        
        for record in record_list:
            post_processed_record = {}
            for key, value in record.items():
                if key not in self.flattend_map:
                    print(f"{key} not found in contact")
                    continue
                field_config = self.flattend_map[key]
                if field_config["type"] == "object":
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            post_processed_record[f"{key}__{subkey}"] = subvalue
                        continue
                    if isinstance(value, list):
                        field_value = json.dumps(value)
                elif isinstance(value, list):
                    field_value = '|'.join(value)
                else:
                    field_value = value

                post_processed_record[key] = field_value
            transformed_record_list.append(post_processed_record)

        return pd.DataFrame(transformed_record_list)


    def load_data_to_destination(self, trans_df:pd.DataFrame, schema:list[ColumnDefn]) -> pd.DataFrame:
        dest = self.destination

        dest.create_redshift_table(column_def=schema, 
                            redshift_table_name=f"{self.model_name}_raw")


        
        #from destination import RedShiftDestination
        #rs_dest = RedShiftDestination(dest_config)
        #rs_dest.initialize_destination(table_name="contact")
        dest.load_data(trans_df)

        return 0

    def start_etl(self):
        self.extract_data_from_source()