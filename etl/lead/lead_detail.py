import pandas as pd
import time

from .lead_modeletl import LeadModelETL
from .lead_opport import LeadOpportETL
from .lead_contact import LeadContactETL

from utils import get_logger
logger = get_logger(__name__)

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
        needed_custom_fields = [
            "Qualified Lead", "Were You At Fault?", "Was anyone else in the vehicle with you?",
            "Treatment at Hospital", "Did you seek any other doctors/treatment?",
            "PracticeAreaId","PracticeAreaName", "PracticeAreaCode", "PracticeAreaDescription"
        ]
        for needed in needed_custom_fields:
            # Chaning functions is not working ???
            fixed_name = needed.replace(" ", "")
            fixed_name = fixed_name.replace("/", "")
            fixed_name = fixed_name.replace("?", "")
            # fixed_name = ((needed.lower().replace('?', ''))).replace(' ', '_')
            leads[fixed_name] = None

        for key, value in leads.items():

            if key == "Contact" or key =="Intake" or key == 'Creator' or key == "PracticeArea":
                leads[key] = leads[key].get("Id")
            
            if key == "CustomFields":

                custom_fields = list()
                for each_custom_field in value:
                    custom_fields.append(each_custom_field["CustomFieldId"])
                    
                    if each_custom_field["Name"] in needed_custom_fields:
                        fixed_name = each_custom_field["Name"].replace(" ", "")
                        fixed_name = fixed_name.replace("/", "")
                        fixed_name = fixed_name.replace("?", "")
                        leads[fixed_name] = each_custom_field.get("Value")

                leads[key] = value
                # leads[key] = ",".join( map( str, custom_fields ))

            elif key == 'PracticeArea':
                print(value)
                leads["PracticeAreaId"] = value.get("Id")
                leads["PracticeAreaName"] = value.get("Name")
                leads["PracticeAreaCode"] = value.get("Code")
                leads["PracticeAreaDescription"] = value.get("Description")

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


    def trigger_etl(self, lead_ids:list[int], client_id: str or None, contact_obj:LeadContactETL, opport_obj:LeadOpportETL):
            """
                Function to trigger conccurent run of lead_detail etl. 
                If each lead detail have Contact or Opportunity id then also trigger contact and opport etl

                As the program runs concurently, loading data into s3 might be a problem for s3 session. Need to add sleep unfortunately.
            """
            for idx, lead_id in enumerate(lead_ids):
                try:
                    lead = self.extract_data_from_source(lead_id)
                    if lead.get("Contact"):
                        contact_df = contact_obj.transform(lead["Contact"])
                        transformed = contact_obj.eliminate_nonyaml(contact_df)
                        contact_obj.load_data(trans_df=transformed, client_id=client_id)
                        time.sleep(2)

                    if lead.get("Opportunity"):
                        opport_id = lead.get("Opportunity").get("Id")
                        extracted = opport_obj.extract_data_from_source(opport_id)
                        opport_df = opport_obj.transform(extracted)
                        transformed = opport_obj.eliminate_nonyaml(opport_df)
                        opport_obj.load_data(trans_df=transformed, client_id=client_id)
                        time.sleep(2)


                    
                    lead_detail_df = self.transform(lead)
                    transformed_detail_df = self.eliminate_nonyaml(lead_detail_df)
                    self.load_data(trans_df=transformed_detail_df, client_id=client_id)

                except Exception as e:
                    logger.warn("=" * 60)
                    logger.error(e)