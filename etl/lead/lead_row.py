from collections import ChainMap
import pandas as pd
import yaml
from yaml.loader import SafeLoader

from etl.datamodel import LeadDocketConfig, ColumnConfig
from etl.destination import ETLDestination
from .lead_modeletl import LeadModelETL

class LeadRowETL(LeadModelETL):

    def extract_data_from_source(self, statuses:list):
        # Using this statuses get all lead row table.
        return self.ld_client.get_lead_row(statuses)

    def extract_lead_metadata(self):
        # Get all status
        return self.ld_client.get_statuses()

    def transform(self, lead:dict):
        return pd.DataFrame([lead])

    def get_snapshot(self):
        statuses = self.ld_client.get_statuses()
        for statuse in statuses:
            leads = self.extract_data_from_source([statuse])
            if leads:
                return leads[0]

        return {}

    def trigger_row(self, lead_row_chunks):
        """
            Function to trigger conccurent run of lead_detail etl. 
            If each lead detail have Contact or Opportunity id then also trigger contact and opport etl
        """
        for each_ex in lead_row_chunks:
            try:
                transformed = self.transform(each_ex[0])
                df = self.eliminate_nonyaml(transformed)
                self.load_data(trans_df=df)

            except Exception as e:
                print("="*100)
                print(e)
                print(f"Problem occurs")
      


