import requests
from filevine.client import FileVineClient

if __name__ == "__main__":
    fv_client = FileVineClient(org_id=6586, user_id=31958)
    project_list = fv_client.get_projects()
    #print(project_list)
    for index, project in enumerate(project_list):
        project_id = project["projectId"]["native"]
        project_type_id = project["projectTypeId"]["native"]
        print(f"Syncing {index}/{len(project_list)} {project_id}, {project_type_id}")
        if project_id >= 10157655:
            continue

        url =  "https://6ek0vhwfgk.execute-api.us-west-2.amazonaws.com/default/lambda_scylla_form_webhook"
        body = {
                    "Timestamp": 1564500130149,
                    "Object": "Form",
                    "Event": "Updated",
                    "ObjectId": {
                        "ProjectTypeId": project_type_id,
                        "SectionSelector": "intake"
                    },
                    "OrgId": 6586,
                    "ProjectId": project_id,
                    "UserId": 31958,
                    "Other": {}
                }
        #10246326 10157655 9653744, 7532691
        response = requests.post(url=url, json=body)
        if response.status_code != 200:
            print(response.text)
            raise
        #break