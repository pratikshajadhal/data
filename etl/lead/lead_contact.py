from typing import List
import pandas as pd
from .lead_modeletl import LeadModelETL


class LeadContactETL(LeadModelETL):

    def extract_data_from_source(self, contact_id:int):
        return self.ld_client.get_contact(contact_id)


    def extract_lead_metadata(self):
        # Get all lead id 
        # Get all status
        statuses = self.ld_client.get_statuses()
        # Using this statuses get all lead row table.
        leads = self.ld_client.get_lead_row(statuses)

        lead_ids = [lead["Id"] for lead in leads]
        contact_ids = list()
        for lead_id in lead_ids:
            contact_ids.append(self.ld_client.get_lead_details(lead_id, field="Contact"))

        return contact_ids


    def transform(self, contact:dict):
        for key, value in contact.items():

            if key == "CustomFields":
                custom_fields = list()
                for each_custom_field in value:
                    custom_fields.append(each_custom_field["CustomFieldId"])

                contact[key] = ",".join( map( str, custom_fields ))

            if isinstance(value, list):
                lead_list = list()
                for each_val in value:
                    lead_list.append(each_val)    
                contact[key] = ",".join( map( str, lead_list ))

        
        return pd.DataFrame([contact])


    def get_snapshot(self):
        statuses = self.ld_client.get_statuses()
        for statuse in statuses:
            leads = self.ld_client.get_lead_row([statuse])
            if leads:
                break

        lead_ids = [lead["Id"] for lead in leads]
        for lead_id in lead_ids:
            contact_id = self.ld_client.get_lead_details(lead_id, field="Contact")
            if contact_id is not None:
                contact_data = self.extract_data_from_source(contact_id)
                if contact_data:
                    return contact_data

        return {}




