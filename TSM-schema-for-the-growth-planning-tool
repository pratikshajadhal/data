create table if not exists tsm.cst_org_settings
(
    id int primary key,
    uuid varchar(100) not null unique,
    org_id int not null references organizations(id),
    settings varchar(250)
);

create table if not exists tsm.cst_departments
(
    id int primary key,
    uuid varchar(100) not null unique,
    cst_org_settings_id int not null references tsm.cst_org_settings(id),
    name varchar(255) not null,
    dept_description text
);


create table if not exists tsm.cst_teams
(
    id int primary key,
    uuid varchar(100) not null unique,
    name varchar(255),
    team_description text,
    cst_department_id int references tsm.cst_departments(id)
);

create table if not exists tsm.cst_team_members
(
    id int primary key,
    uuid varchar(100) not null unique,
    cst_team_id int not null references tsm.cst_teams(id),
    org_people_id int references tsm.cms_people(people_id),
    name varchar(255)
);

--tsm.org_members doesn't exist so it doesn't work. I changed it with cms_people

create table if not exists tsm.cst_targets
(
    id int primary key,
    uuid varchar(100) not null unique,
    parent_target_id int references tsm.cst_targets(id),
    department_id int references tsm.cst_departments(id),
    team_id int references tsm.cst_teams(id),
    team_member_id int references tsm.cst_team_members(id),
    org_settings_id int not null references tsm.cst_org_settings(id),
    target_value numeric(10,2) not null,
    start_date date not null,
    end_date date not null
);
