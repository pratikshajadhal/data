create extension if not exists "uuid-ossp";

create table if not exists exec_statuses (
    id int not null,
    status_name varchar(20) not null unique,
    primary key (id)
);

create table if not exists error_reasons (
    id int not null,
    reason_name varchar(20) not null unique,
    primary key (id)
);

create table if not exists pipelines (
    id int,
    uuid uuid not null unique,
    org_uuid uuid not null,
    org_pipeline_number int not null,
    tpa_identifier varchar(50) not null,
    config_yaml text not null,
    status_id int not null references exec_statuses(id),
    started_at timestamp,
    ended_at timestamp,
    created_at timestamp not null DEFAULT current_timestamp,
    updated_at timestamp not null DEFAULT current_timestamp,
    unique(org_uuid, org_pipeline_number),
    primary key (id)
);

create table if not exists jobs (
    id int,
    uuid varchar(36) unique not null,
    pipeline_id int not null references pipelines(id),
    job_identifier varchar(50) not null,
    exec_status_id int not null references exec_statuses(id),
    error_reason int references error_reasons(id),
    error_details jsonb,
    started_at timestamp not null DEFAULT current_timestamp,
    ended_at timestamp,
    created_at timestamp not null DEFAULT current_timestamp,
    updated_at timestamp not null DEFAULT current_timestamp,
    primary key (id)
);
