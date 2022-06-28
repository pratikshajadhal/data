from typing import List
from leaddocket.client import LeadDocketClient
from etl.datamodel import LeadDocketConfig
from etl.datamodel import ColumnConfig
from etl.datamodel import ColumnDefn
from etl.destination import ETLDestination, S3Destination
import pandas as pd
from .lead_modeletl import LeadModelETL


class LeadReferralsETL(LeadModelETL):

    def extract_data_from_source(self):
        return self.ld_client.get_referrals()


    def transform(self, referrals:List):
        return (pd.DataFrame(referrals))






