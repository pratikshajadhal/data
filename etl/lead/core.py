from etl.destination import ETLDestination, S3Destination
import pandas as pd
from .lead_modeletl import LeadModelETL


class CoreETL(LeadModelETL):
    def extract_data_from_source(self):
        # Get core data of model name
        return self.ld_client.get_lookups(lookup_type=self.model_name)

    def transform(self, core:dict):
        return pd.DataFrame(core)

    # Override
    def load_data(self, trans_df:pd.DataFrame, client_id:str=None):
        dest = self.destination

        dtypes = trans_df.dtypes.to_dict()
        final_dtypes = {}
        for key, value in dtypes.items():
            final_dtypes[key] = self.key_mapper[str(value)]

        push_id = f"bulk_{self.model_name}"

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




