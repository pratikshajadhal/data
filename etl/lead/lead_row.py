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


    def extract_data_from_webhook_incoming(self, lead_payload:dict) -> dict:
        # Copied from old lambda function.
        new = dict()

        new['Id'] =  lead_payload.get("LeadId") 
        new['ContactId'] = lead_payload.get('ContactId')
        new['PhoneNumber'] = lead_payload.get("PhoneNumber")
        new['MobilePhone'] = lead_payload.get('ContactMobilePhone')
        new['HomePhone'] = lead_payload.get('ContactHomePhone')
        new['WorkPhone'] = lead_payload.get('ContactWorkPhone')
        new['PreferredContactMethod'] = lead_payload.get("PreferredContactMethod")
        new['Email'] = lead_payload.get('ContactEmail')
        new['FirstName'] = lead_payload.get('ContactFirstName')
        new['LastName'] = lead_payload.get('ContactLastName')
        new['StatusId'] = lead_payload.get('ContactId')
        new['StatusName'] = lead_payload.get('LeadStatus')
        new['SubStatusId'] = lead_payload.get('ContactId')
        new['SubStatusName'] = lead_payload.get('ContactId')
        new['CaseType'] = lead_payload.get('LeadCaseType')
        new['Code'] = lead_payload.get('ContactCode')                     ##LeadCode also available in event body
        new['LastStatusChangeDate'] = lead_payload.get('LastStatusChangeDate')
        return new

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
            Function to trigger conccurent run of leadrow etl. 
        """
        for each_ex in lead_row_chunks:
            try:
                transformed = self.transform(each_ex[0])
                df = self.eliminate_nonyaml(transformed)
                self.load_data(trans_df=df)

            except Exception as e:
                print("="*100)
                print(e)
      


