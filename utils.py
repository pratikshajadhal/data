from itertools import islice
import json
from dacite import from_dict

import pandas as pd
import yaml

from etl.datamodel import RedshiftConfig, SelectedConfig 

standard_dtypes = ["string", "bool", "int", "decimal"]

def load_config(file_path: str) -> SelectedConfig:
    """Loads devenv.yaml from the given file path."""
    with open(file_path, "r") as stream:
        data = yaml.safe_load(stream)
        #print(data)
        return from_dict(data=data, data_class=SelectedConfig)


def read_contact_metadata():
    with open("contacts-metadata.json") as f:
        contact_schema = json.loads(f.read())

    contact_map = {}

    for field in contact_schema:
        field_data_type = field["value"]
        contact_map[field["selector"].replace("custom.", "")] = {"type" : field_data_type}

    return contact_map

def transform_source_to_destination(source, destination_map):
    post_processed_contact = {}
    for key, value in source.items():
        if key not in destination_map:
            print(f"{key} not found in contact")
            continue
        field_config = destination_map[key]
        if field_config["type"] == "object":
            field_value = json.dumps(value)
        elif isinstance(value, list):
            field_value = '|'.join(value)
        else:
            field_value = value

        post_processed_contact[key] = field_value
    return post_processed_contact

def get_chunks(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

        

if __name__ == "__main__":

    config = load_config(file_path="src.yaml")
    print(config.projectTypes)
    '''
    contact_map = read_contact_metadata()
    with open("contacts.json", "r") as f:
        contact_data = json.loads(f.read())
    contact_list = contact_data["items"]
    record_list = []
    for contact in contact_list:
        post_processed_contact = transform_source_to_destination(contact["orgContact"], contact_map)
        record_list.append(post_processed_contact)

    contact_df = pd.DataFrame(record_list)
    '''