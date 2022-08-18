from utils import load_config 
from etl.datamodel import FileVineConfig
from etl.form import FormETL
from etl.destination import S3Destination

def test_fv_webhook_phase():
    payload = {
                "Timestamp": 1655210533742,
                "Object": "Project",
                "Event": "PhaseChanged",
                "ObjectId": {
                    "ProjectTypeId": 25962,
                    "PhaseId": 141438
                },
                "OrgId": 6586,
                "ProjectId": 10567083,
                "UserId": 62385,
                "Other": {
                    "PhaseName": "Ready For Demand"
                }
            }
    # TODO add tests cases 


def test_fv_webhook_form():
    payload = {"Timestamp": 1659389672522, 
                "Object": "Form", 
                "Event": "Updated", 
                "ObjectId": {
                            "ProjectTypeId": 18764, 
                            "SectionSelector": "intake"
                            }, 
                "OrgId": 6586, 
                "ProjectId": 9665828, 
                "UserId": 48697, 
                "Other": {}
                }
    # TODO add tests cases


def test_fv_webhook_project():
    payload = {"Timestamp": 1659383279769, 
                "Object": "Project", 
                "Event": "Updated", 
                "ObjectId": {"ProjectId": 10176082}, 
                "OrgId": 6586, 
                "ProjectId": 10176082, 
                "UserId": None, 
                "Other": {"Action": "ReplacedHashtags"}}
    # TODO add tests cases

def test_fv_webhook_collections():
    payload = {"Timestamp": 1659392519669, 
                "Object": "CollectionItem", 
                "Event": "Created", 
                "ObjectId": {"ProjectTypeId": 18764, "SectionSelector": "meds", "ItemId": "9e21b8c6-1681-4fa6-8f22-35f005b5824d"}, 
                "OrgId": 6586, "ProjectId": 10465844, "UserId": 5840, "Other": {}}
    # TODO add tests cases

def test_snapshot_intake():
    selected_field_config = load_config(file_path="src.yaml")
    print(selected_field_config.projectTypes[0])
    fv_config = FileVineConfig(org_id=selected_field_config.org_id, user_id=selected_field_config.user_id)

    form_name = "intake"

    for section in selected_field_config.projectTypes[0].sections:
        if section.name == form_name:
            form_etl = FormETL(model_name=form_name, 
                        source=None, 
                        entity_type="form",
                        project_type=18764,
                        destination=S3Destination(org_id=fv_config.org_id), 
                        fv_config=fv_config, 
                        column_config=section, 
                        primary_key_column="projectId")

            snapshot = form_etl.get_snapshot(18764)  
            print(snapshot)

if __name__ == "__main__":
    test_snapshot_intake()