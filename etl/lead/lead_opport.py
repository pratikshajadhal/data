from typing import List
from leaddocket.client import LeadDocketClient
from etl.datamodel import LeadDocketConfig
from etl.datamodel import ColumnConfig
from etl.datamodel import ColumnDefn
from etl.destination import ETLDestination, S3Destination
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
        for lead_id in lead_ids[:10]:
            opport_ids.append(self.ld_client.get_lead_details(lead_id, field="Opportunity"))

        # opport_ids = [2483, 2482, None, 2469, None, 2417, 2436, 2362, 2432, None]
        filtered_list = [ ele for ele in opport_ids if ele is not None ]
        return filtered_list


    def transform(self, opport:dict):
        for key, value in opport.items():

            if key == "CustomFields":
                custom_fields = list()
                for each_custom_field in value:
                    custom_fields.append(each_custom_field["CustomFieldId"])

                opport[key] = ",".join( map( str, custom_fields ))

            if key == "AssignedTo":
                if value:
                    name = opport[key][0].get("FirstName") + " " + opport[key][0].get("LastName")
                else:
                    name = ""

                opport[key] = name

            if key == "ProcessedBy":
                if isinstance(value, dict):
                    name = opport[key].get("FirstName") + " " + opport[key].get("LastName")
                else:
                    name = ""

                opport[key] = name


        return pd.DataFrame([opport])




