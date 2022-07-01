from utils import load_config 
from etl.datamodel import FileVineConfig
from etl.form import FormETL
from etl.destination import S3Destination

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