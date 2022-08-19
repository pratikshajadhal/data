from dataclasses import dataclass

@dataclass
class ETLSource:
    name: str
    end_point: str


@dataclass
class RedshiftConfig:
    schema_name: str
    dbname: str
    host: str
    user: str
    port: str
    password: str
    s3_bucket: str
    s3_temp_dir: str

@dataclass
class ETLDestination:
    name: str
    config: RedshiftConfig

@dataclass
class FileVineConfig:
    org_id:int
    user_id:int
    api_key: str

@dataclass
class ColumnDefn:
    name:str
    data_type:str

@dataclass
class ColumnConfig:
    name:str
    fields:list[str]


@dataclass
class ProjectTypeConfig:
    id: int
    sections: list[ColumnConfig]


@dataclass
class SelectedConfig:
    projectTypes: list[ProjectTypeConfig]
    org_id:int
    user_id:int
    core:list[ColumnConfig]

@dataclass
class LeadDocketConfig:
    org_name: str
    base_url: str

@dataclass
class LeadSelectedConfig:
    org_name: str
    base_url: str
    table_leadstatuses:list[ColumnConfig]
    table_leadsource:list[ColumnConfig]
    table_casetype:list[ColumnConfig]
    table_leadrow:list[ColumnConfig]
    table_leaddetail:list[ColumnConfig]
    table_contact:list[ColumnConfig]
    table_opport:list[ColumnConfig]
    table_referral:list[ColumnConfig]
    table_users:list[ColumnConfig]