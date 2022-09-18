from typing import List
import pandas as pd
from .lead_modeletl import LeadModelETL


class LeadReferralsETL(LeadModelETL):

    def extract_data_from_source(self):
        return self.ld_client.get_referrals()


    def transform(self, referrals:List):
        return (pd.DataFrame(referrals))






