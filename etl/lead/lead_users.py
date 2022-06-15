from typing import List
import pandas as pd
from .lead_modeletl import LeadModelETL


class LeadUsersETL(LeadModelETL):

    def extract_data_from_source(self):
        return self.ld_client.get_users()


    def transform(self, users:List):
        return (pd.DataFrame([users]))






