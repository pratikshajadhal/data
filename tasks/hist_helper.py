from etl.lead.lead_row import LeadRowETL
from etl.lead.lead_detail import LeadDetailETL
from etl.lead.lead_contact import LeadContactETL
from etl.lead.lead_opport import LeadOpportETL
from etl.lead.lead_referrals import LeadReferralsETL
from etl.lead.lead_users import LeadUsersETL
from etl.datamodel import ETLSource, FileVineConfig, LeadDocketConfig
from utils import load_config, get_chunks, load_lead_config
from etl.lead.core import CoreETL 
from etl.destination import RedShiftDestination, S3Destination


def start_leadsource_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)

    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)
    section = selected_field_config.table_leadsource[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(org_id=ld_config.org_name))

    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)


def start_case_type_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)
    section = selected_field_config.table_casetype[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(org_id=ld_config.org_name))

    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)


def start_lead_row_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)
    
    section = selected_field_config.table_leadrow[0]
    lead_row = LeadRowETL(model_name=section.name ,
                        ld_config=ld_config,
                        column_config=section, 
                        fields=section.fields,
                        destination=S3Destination(org_id=ld_config.org_name))

    statuses = lead_row.extract_lead_metadata()

    extracted = lead_row.extract_data_from_source(statuses)
    for each_ex in extracted:
        transformed = lead_row.transform(each_ex)
        df = lead_row.eliminate_nonyaml(transformed)
        lead_row.load_data(trans_df=df)


def start_lead_detail_etl(s3_conf_file_path, lead_ids:list = None, client_id = None):
    """
        Function to fill detail table. Runs for the given lead_ids.
        If ids is not given, then it will run as historical.
    """
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)

    section = selected_field_config.table_leaddetail[0] # Temp
    lead_detail = LeadDetailETL(model_name=section.name ,
                                ld_config=ld_config,
                                column_config=section, 
                                fields=section.fields,
                                destination=S3Destination(org_id=ld_config.org_name))

    if lead_ids is None:
        lead_ids = lead_detail.extract_lead_metadata()

    # lead_ids = [9964]
    for idx, lead_id in enumerate(lead_ids):
        # if idx == 100:
        #     time.sleep(60)
        lead = lead_detail.extract_data_from_source(lead_id)
        lead_detail_df = lead_detail.transform(lead)
        transformed_detail_df = lead_detail.eliminate_nonyaml(lead_detail_df)
        lead_detail.load_data(trans_df=transformed_detail_df, client_id=client_id)
    

def start_lead_contact_etl(s3_conf_file_path, contact_ids:list = None, client_id = None):
    """
        Function to fill contact table. Runs for the given contact_ids.
        If ids is not given, then it will run as historical.
    """
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)

    section = selected_field_config.table_contact[0]
    contact_etl = LeadContactETL(model_name=section.name ,
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=S3Destination(org_id=ld_config.org_name))

    if contact_ids is None:
        contact_ids = contact_etl.extract_lead_metadata()
    # contact_ids = [10184, 9967, 9859, 10167, 6999, 9961, 10166, 10180, 10085, 10094]
    for contact_id in contact_ids:
        extracted = contact_etl.extract_data_from_source(contact_id)
        contact_df = contact_etl.transform(extracted)
        transformed = contact_etl.eliminate_nonyaml(contact_df)
        contact_etl.load_data(trans_df=transformed, client_id=client_id)


def start_opport_etl(s3_conf_file_path, opport_ids:list = None, client_id = None):
    """
        Function to fill opportunuties table. Runs for the given opport_ids.
        If ids is not given, then it will run as historical.
    """
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)

    section = selected_field_config.table_opport[0] 
    opport_etl = LeadOpportETL(model_name=section.name ,
                    ld_config=ld_config,
                    column_config=section, 
                    fields=section.fields,
                    destination=S3Destination(org_id=ld_config.org_name))

    if opport_ids is None:
        opport_ids  = opport_etl.extract_lead_metadata()
    # opport_ids = [2483, 2482, None, 2469, None, 2417, 2436, 2362, 2432, None]
    # opport_ids = [ ele for ele in opport_ids if ele is not None ]
    for opport_id in opport_ids:
        extracted = opport_etl.extract_data_from_source(opport_id)
        opport_df = opport_etl.transform(extracted)
        transformed = opport_etl.eliminate_nonyaml(opport_df)
        opport_etl.load_data(trans_df=transformed, client_id=client_id)


def start_referrals_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)

    section = selected_field_config.table_referral[0]
    referral_etl = LeadReferralsETL(model_name=section.name ,
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(org_id=ld_config.org_name))

    extracted = referral_etl.extract_data_from_source()
    referral_df = referral_etl.transform(extracted)
    transformed = referral_etl.eliminate_nonyaml(referral_df)
    referral_etl.load_data(trans_df=transformed)


def start_users_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)

    section = selected_field_config.table_users[0]
    users_etl = LeadUsersETL(model_name=section.name ,
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(org_id=ld_config.org_name))

    extracted = users_etl.extract_data_from_source()
    for each_ex in extracted:
        user_df = users_etl.transform(each_ex)
        transformed = users_etl.eliminate_nonyaml(user_df)
        users_etl.load_data(trans_df=transformed)

def start_statuses_etl(s3_conf_file_path):
    selected_field_config = load_lead_config(file_path=s3_conf_file_path)
    ld_config = LeadDocketConfig(selected_field_config.org_name, selected_field_config.base_url)
    section = selected_field_config.table_leadstatuses[0] 
    core_etl = CoreETL(model_name=section.name, 
                ld_config=ld_config,
                column_config=section, 
                fields=section.fields,
                destination=S3Destination(org_id=ld_config.org_name))

        
    extracted = core_etl.extract_data_from_source()
    core_df = core_etl.transform(extracted)
    transformed = core_etl.eliminate_nonyaml(core_df)
    core_etl.load_data(trans_df=transformed)
    