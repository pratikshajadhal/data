from leaddocket.client import LeadDocketClient
from etl.datamodel import LeadDocketConfig
from etl.datamodel import ColumnConfig
from etl.datamodel import ColumnDefn
from etl.destination import ETLDestination, S3Destination
import pandas as pd
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




