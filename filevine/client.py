from typing import Dict
import requests
import os
import json 
import logging

from dotenv import load_dotenv

load_dotenv()

class FileVineClient(object):

    def __init__(self, org_id:str, user_id:str):
        self.api_key = os.environ["LOCAL_TPA_API_KEY_FILEVINE"]
        self.org_id = org_id
        self.base_url = "https://api.filevine.io/"
        self.api_timestamp = "2021-08-18T12:37:03.438Z"
        self.user_id = user_id
        self.api_hash = None

    def generate_api_hash(self):
        return "567a20d5f3ff434a3e1926f86853bcdb"

    def generate_session(self):
        if not self.api_hash:
            self.api_hash = self.generate_api_hash()

        url = f"{self.base_url}session"
        data = {
			"mode": "key",
			"apiKey": self.api_key,
			"apiHash": self.api_hash,
			"apiTimestamp": self.api_timestamp,
			"userId" : self.user_id,
			"orgId" : self.org_id
		}
        response = requests.post(url, headers={"Content-Type" : "application/json"}, data=json.dumps(data))
        if response.status_code != 200:
            logging.error("Unable to generate tokens")
            raise Exception("Token genreation error")
        return json.loads(response.text)

    def make_request(self, end_point:str, query_param:Dict={}):
        session_info = self.generate_session()
        url = f"{self.base_url}{end_point}"
        print("Hitting URL {}".format(url))
        headers = {"x-fv-sessionid" : session_info["refreshToken"], 
                "Authorization" : "Bearer {}".format(session_info["accessToken"])}
        print(query_param)
        response = requests.get(url, headers=headers, params=query_param)
        if response.status_code != 200:
            logging.error(response.text)
            logging.error(response.status_code)
            if response.status_code == 404:
                return None
            raise
        
        return json.loads(response.text)

    def get_entity(self, end_point:str, requested_fields:list=['*']):
        has_more = True
        limit=1000
        offset=0
        item_list = []
        
        while has_more:
            response = self.make_request(end_point=end_point, 
                                    query_param={"limit" : limit, "requestedFields" : ','.join(requested_fields), "offset" : offset})
            has_more = response["hasMore"]
            offset = offset + limit
            items = response["items"]
            item_list = item_list + items
            
        return item_list

    def get_section_metadata(self, projectTypeId, section_name):
        end_point = f"core/projecttypes/{projectTypeId}/sections/{section_name}"
        section_metadata = self.make_request(end_point)
        return section_metadata


    def get_contact_metadata(self):
        contact_metadata = self.make_request("core/custom-contacts-meta")
        return contact_metadata

    def get_project_contacts(self, project_id:int):
        raw_contact_items = self.get_entity(f"core/projects/{project_id}/contacts")
        contact_list = [item["orgContact"] for item in raw_contact_items]
        return contact_list

    def get_contacts(self):
        raw_contact_items = self.get_entity(f"core/contacts")
        contact_list = raw_contact_items
        return contact_list

    def get_section_data(self, project_id:int, section_name:str):
        end_point = f"core/projects/{project_id}/forms/{section_name}"
        section_data = self.make_request(end_point)
        return section_data

    def get_collections(self, project_id:int, collection_name:str):
        end_point = f"core/projects/{project_id}/collections/{collection_name}?limit=1000"
        collection_data = self.make_request(end_point)
        if collection_data:
            return collection_data["items"]
        return None

    def get_projects(self, requested_fields:list[str]=['*']):
        return self.get_entity("core/projects", requested_fields=requested_fields)
        

if __name__ == "__main__":
    fv_client = FileVineClient("6586", "31958")
    #print(fv_client.get_contacts(project_id=10561860))
    #print(fv_client.get_section_data(10568297, "intake"))
    print(json.dumps(fv_client.get_collections(5965342, "meds")))
    #collection_metadata = fv_client.get_section_metadata(projectTypeId=18764, section_name="meds")
    #print(json.dumps(collection_metadata))