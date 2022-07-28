from typing import Dict, List
import requests
import os
import json 
import logging
import pandas as pd
import yaml
from dacite import from_dict
from utils import get_logger

logger = get_logger(__name__)
from dotenv import load_dotenv

load_dotenv()

class LeadDocketClient(object):

    def __init__(self, base_url:str, api_key:str=os.environ["LOCAL_TPA_API_KEY_LEADDOCKET"]):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
                        'Accept': 'application/json',
                        'api_key': self.api_key
                        }

    def make_request(self, end_point:str, query_param:Dict={}):
        url = f"{self.base_url}{end_point}"
        logger.info("Hitting URL {}".format(url))
        response = requests.get(url, headers=self.headers, params=query_param)
        if response.status_code != 200:
            logging.error(response.text)
            logging.error(response.status_code)
            if response.status_code == 404:
                return None
            raise
        return json.loads(response.text)

    def get_row_lead_iteratively(self, endpoint, status, page=1):
        query_param = {"status": status,
                "page": page}
        output = self.make_request(endpoint, query_param)
        incoming_page = output["TotalPages"]
        output_list = list()
        
        if not output:
            return 0

        if (incoming_page) > page :
            output_list += (output["Records"])
            for i in range(page+1, incoming_page+1):
                query_param = {"status": status,
                                "page": i}
                output = self.make_request(endpoint, query_param)
                output_list += output["Records"]
            return output_list
        else:
            return output["Records"]

    def get_lookups(self, lookup_type:str):
        endpoint = f"/api/lookups"
        query_param = {"type": lookup_type}
        logger.info(f"Given Param is: {query_param}")
        return self.make_request(end_point = endpoint, query_param=query_param)

    def get_statuses(self):
        lookup_type = "Statuses"
        statuses = self.get_lookups(lookup_type=lookup_type)

        status_list = [status.get("Status") for status in statuses]
        return status_list
    
    def get_lead_row(self, statuses:List):
        endpoint = f"/api/leads"

        records = list()
        for status in statuses:
            print("(+) STATUS : {}".format(status))
            outy = self.get_row_lead_iteratively(endpoint, status)
            if outy:
                records += outy

        return records

    def get_lead(self, lead_id:int, field=None):
        endpoint = f"/api/leads/{lead_id}"
        out = self.make_request(endpoint)
        
        if field is not None:
            if out[field]:
                return out[field].get("Id")
            else:
                return

        return out

    def get_lead_details(self, lead_id:int, field=None):
        
        return self.get_lead(lead_id, field)

    def get_contact(self, contact_id: int):
        endpoint = f"/api/contacts/{contact_id}"
        return self.make_request(endpoint)
    
    def get_opport(self, opport_id: int):

        endpoint = f"/api/opportunities/{opport_id}"
        return self.make_request(endpoint)

    def get_referrals(self):
        endpoint = "/api/referrals/list"
        return self.make_request(end_point=endpoint)

    def get_users(self):
        endpoint = "/api/users"
        return self.make_request(end_point=endpoint)

    def get_custom_fields(self):
        endpoint = "/api/customfields/list"
        return self.make_request(endpoint)
