from collections import ChainMap
import pandas as pd
import yaml
from yaml.loader import SafeLoader

from etl.datamodel import LeadDocketConfig, ColumnConfig
from etl.destination import ETLDestination, S3Destination
from .lead_modeletl import LeadModelETL


class LeadDetailETL(LeadModelETL):

    def extract_data_from_source(self, lead_ids):
        lead_details = self.ld_client.get_lead_details(lead_ids)
        return lead_details


    def extract_lead_metadata(self):
        # Get all lead id 
        # Get all status
        statuses = self.ld_client.get_statuses()
        # Using this statuses get all  row table.
        leads = self.ld_client.get_lead_row(statuses)

        lead_ids = [lead["Id"] for lead in leads]
        return lead_ids


    def transform(self, leads):
        for key, value in leads.items():
            if key == "Contact" or key =="Intake" or key == 'Creator' or key == "PracticeArea":
                leads[key] = leads[key].get("Id")
            
            if key == "CustomFields":
                custom_fields = list()
                for each_custom_field in value:
                    custom_fields.append(each_custom_field["CustomFieldId"])


                leads[key] = value
                # leads[key] = ",".join( map( str, custom_fields ))

            elif isinstance(value, list):
                ids = list()
                if isinstance( value, list):
                    for each in leads[key]:
                        ids.append(each.get("Id"))
                    leads[key] = ",".join( map( str, ids ) )
                    
                else:
                    raise ValueError('An unknown list of something came.')

            elif isinstance(value, dict):
                leads[key] = value.get("Id")

        
        return pd.DataFrame([leads])


    def get_snapshot(self):
        statuses = self.ld_client.get_statuses()
        for statuse in statuses:
            leads = self.ld_client.get_lead_row([statuse])
            if leads:
                break

        lead_ids = [lead["Id"] for lead in leads]
        for lead_id in lead_ids:
            data = self.extract_data_from_source(lead_id)
            if data is not None:
                return data
        
        return {}



