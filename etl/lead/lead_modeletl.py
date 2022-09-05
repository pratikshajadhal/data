from leaddocket.client import LeadDocketClient
from etl.datamodel import LeadDocketConfig
from etl.datamodel import ColumnConfig
from etl.destination import ETLDestination, S3Destination
import pandas as pd
from abc import abstractmethod
from utils import get_logger

logger = get_logger(__name__)

class LeadModelETL(object):
    
    def __init__(self, model_name:str,
                    ld_config: LeadDocketConfig, 
                    column_config: ColumnConfig, 
                    fields,
                    destination: ETLDestination,
                    ):
        self.model_name = model_name
        self.ld_config = ld_config
        self.column_config = column_config
        self.base_url = ld_config.base_url
        self.ld_client = LeadDocketClient(ld_config.base_url)
        self.fields = fields
        self.destination = destination

        self.key_mapper = {"int64": "int",
                            "object": "string",
                            "bool": "boolean",
                            "float64":"float"}

    def load_data(self, trans_df:pd.DataFrame, client_id:str=None):
        dest = self.destination

        if hasattr(self, 'dtypes'):
            final_dtypes = self.dtypes
        else:
            dtypes = trans_df.dtypes.to_dict()
            final_dtypes = {}
            for key, value in dtypes.items():
                final_dtypes[key] = self.key_mapper[str(value)]

        push_id = trans_df["Id"].values[0]
        # If there is no client id parse clientId from url
        if client_id:
            organization_identifier = client_id
        else:
            organization_identifier = (self.base_url.split(".")[0]).split("//")[1]
        if isinstance(dest, S3Destination):
            dest.load_data(data_df= trans_df,
                            section="leaddocket",
                            model_name=self.model_name,
                            dtype = final_dtypes,
                            push_id = push_id,
                            organization_identifier = organization_identifier,
                            entity= "lead")
                            

    def eliminate_nonyaml(self, lead_df:pd.DataFrame):
        for each_field in  lead_df.columns.values.tolist():
            if each_field not in  self.column_config.fields:
                logger.debug(f"Field: {each_field} is eliminating. Not in yaml file.")
                lead_df.drop([each_field], axis = 1, inplace = True)

        return lead_df


    @abstractmethod
    def transform(self):
        pass


    def get_snapshot(self):
        return self.extract_data_from_source()[0]
