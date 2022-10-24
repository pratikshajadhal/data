from typing import List
import pandas as pd
from .lead_modeletl import LeadModelETL


class LeadOpportETL(LeadModelETL):

    def extract_data_from_source(self, opport_id:int):
        return self.ld_client.get_opport(opport_id)


    def extract_lead_metadata(self):
        # Get all lead id 
        # Get all status
        statuses = self.ld_client.get_statuses()
        # Using this statuses get all lead row table.
        leads = self.ld_client.get_lead_row(statuses)

        lead_ids = [lead["Id"] for lead in leads]
        
        # Get ooport_id using leads.
        opport_ids = list()
        for lead_id in lead_ids:
            opport_ids.append(self.ld_client.get_lead_details(lead_id, field="Opportunity"))

        # opport_ids = [2483, 2482, None, 2469, None, 2417, 2436, 2362, 2432, None]
        filtered_list = [ ele for ele in opport_ids if ele is not None ]
        return filtered_list


    def transform(self, opport:dict):
        # needed_custom_fields = ["AssignedToEmail", "ProcessedByEmail"]
        # for needed in needed_custom_fields:
        #     opport[needed] = None
            
        for key, value in opport.items():

            if key == "CustomFields":
                custom_fields = list()
                for each_custom_field in value:
                    custom_fields.append(each_custom_field["CustomFieldId"])

                opport[key] = ",".join( map( str, custom_fields ))

            if key == "AssignedTo":
                if value:
                    name = opport[key][0].get("Email")
                else:
                    name = ""

                opport[key] = name

            if key == "ProcessedBy":
                if isinstance(value, dict):
                    name = opport[key].get("Email")
                else:
                    name = ""

                opport[key] = name


        return pd.DataFrame([opport])


    def get_snapshot(self):
        statuses = self.ld_client.get_statuses()
        for statuse in statuses:
            leads = self.ld_client.get_lead_row([statuse])
            if leads:
                break

        lead_ids = [lead["Id"] for lead in leads]
        for lead_id in lead_ids:
            opport_id = self.ld_client.get_lead_details(lead_id, field="Opportunity")
            if opport_id is not None:
                opport_data = self.extract_data_from_source(opport_id)
                if opport_data:
                    return opport_data

        return {}


