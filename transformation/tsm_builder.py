import abc
from typing import List
from pandas import DataFrame
import yaml
from dacite import from_dict

from pyspark.sql import SparkSession
from pyspark.sql import DataFrame as SP_DATAFRAME

from transformation.datamodel import SSTM, TSMTableField

class TSMBuilder(metaclass=abc.ABCMeta):

    def __init__(self, config_yaml) -> None:
        with open(config_yaml, "r") as file:
            self.config : SSTM = from_dict(data=yaml.safe_load(file), data_class=SSTM)
        
    def _get_table_config(self, table_name) -> List[TSMTableField]:
        for table in self.config.tsm:
            if table.name == table_name:
                return table.fields

    def _get_schema_of_table(self, table_name) -> SP_DATAFRAME:
        return None
    
    def build_peopletypes(self):
        """Load in the data set"""
        table_fields = self._get_table_config("PeopleType")

        for field in table_fields:
            if field.transform:
                if field.transform.type == "org_id":


        self.raw_data = {}
        self.raw_data["contact"] = "As"
        #raise NotImplementedError
    
if __name__ == "__main__":
    TSMBuilder("sstm.yaml")