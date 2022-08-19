CREATE TABLE IF NOT EXISTS PeopleType (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  People_Type_ID int not null,
  People_Type varchar(255) not null,
  People_Sub_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (People_Type_ID)
);

CREATE TABLE IF NOT EXISTS Teams (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Team_ID int not null,
  Team_Name varchar(255) not null unique,
  Team_Type varchar(255),
  Team_Sub_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Team_ID)
);


CREATE TABLE IF NOT EXISTS PeopleMaster (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  People_ID int not null,
  People_Type_ID int not null references PeopleType(People_Type_ID),
  Team_ID int not null references Teams(Team_ID),
  First_Name varchar(255) not null,
  Middle_Name varchar(255) not null,
  Last_Name varchar(255) not null,
  Date_of_Birth date,
  Gender varchar(50),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (People_ID)
);

CREATE TABLE IF NOT EXISTS CaseTypes (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Case_Type_ID int not null,
  Case_Type_Name varchar(255) not null unique,
  Case_Type_Category varchar(255),
  Case_Type_Sub_Category varchar(255),
  Phase_Change_Date date,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Case_Type_ID)
);


CREATE TABLE IF NOT EXISTS PracticeTypes (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Practice_Type_ID int not null,
  Practice_Type_Name varchar(255) not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Practice_Type_ID)
);


CREATE TABLE IF NOT EXISTS PhaseMaster (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Phase_ID int not null,
  Phase_Name varchar(255) not null unique,
  Phase_Order int not null unique,
  Phase_Category varchar(255),
  Phase_Sub_Category varchar(255),
  Practice_Type_ID int not null references PracticeTypes (Practice_Type_ID),
  Case_Type_ID int not null references CaseTypes (Case_Type_ID),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Phase_ID)
);



CREATE TABLE IF NOT EXISTS StatusMaster (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Status_ID int not null,
  Practice_Type_ID int not null references PracticeTypes (Practice_Type_ID),
  Case_Type_ID int not null references CaseTypes (Case_Type_ID),
  Status_Name varchar(255) not null,
  Sub_Status_Name varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Status_ID)
);


CREATE TABLE IF NOT EXISTS InsuranceMaster (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Insurance_ID int not null,
  Insurance_Name varchar(255) not null,
  Insurance_Type varchar(255) not null,
  Insurance_Sub_Type varchar(255) not null,
  Insurance_Limit1_Type varchar(255),
  Insurance_Limit2_Type varchar(255),
  Limit_Value1 decimal(8,2),
  Limit_Value2 decimal(8,2),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Insurance_ID)
);


CREATE TABLE IF NOT EXISTS CaseSummary (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Practice_Type_ID int not null references PracticeTypes(Practice_Type_ID),
  Case_Type_ID int not null references CaseTypes(Case_Type_ID),
  Case_Create_Date date not null,
  Date_of_Incident date not null,
  Case_Name varchar(255),
  Plaintiff_Full_Name varchar(255),
  Attorney_ID int references PeopleMaster (People_ID),
  Prelitigation_Paralegal_ID int references PeopleMaster (People_ID),
  Litigation_Paralegal_ID int references PeopleMaster (People_ID),
  CaseManager_ID int references PeopleMaster (People_ID),
  Cocounsel_ID int references PeopleMaster (People_ID),
  Case_Team_ID int not null references Teams (Team_ID),
  Case_Status_ID int not null references StatusMaster (Status_ID),
  Insurance_ID int not null references InsuranceMaster (Insurance_ID),
  Case_Marketing_Source varchar(255),
  Case_Source_Name varchar(255),
  Attorney_Fee_Percentage decimal(3,2),
  Projected_Settlement_Date date,
  Projected_Settlement_Amount date,
  Actual_Settlement_Date date,
  Actual_Settlement_Amount date,
  If_Case_Settled_Presuit varchar(50),
  If_VIP_Case varchar(50),
  If_Case_Referred_Out varchar(50),
  Case_Phase_ID int not null references PhaseMaster (Phase_ID),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  Custom4 varchar(255),
  Custom5 varchar(255),
  primary key (Parent_Case_ID, Case_ID)
);


CREATE TABLE IF NOT EXISTS CaseFigures (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Case_Figure_ID int not null,
  Figure_Type varchar(255),
  Figure_Date date,
  Figure_Status varchar(255),
  Value decimal(8,2),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Case_Figure_ID),
  foreign key (Parent_Case_ID, Case_ID) references CaseSummary (Parent_Case_ID, Case_ID)
);

CREATE TABLE IF NOT EXISTS IntakeSummary (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Intake_ID int not null,
  Person_Performing_Intake_ID int not null references PeopleMaster (People_ID),
  Intake_Source varchar(255) not null DEFAULT 'None',
  Date_of_Intake date,
  Date_of_Incident date,
  DUI_or_HitandRun varchar(50),
  Referral_Fee_ID int not null references CaseFigures (Case_Figure_ID),
  If_Case_Referred_In varchar(50),
  If_Qualified_Case varchar(50),
  If_VIP_Lead varchar(50),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Intake_ID),
  foreign key (Parent_Case_ID, Case_ID) references CaseSummary (Parent_Case_ID, Case_ID)
);



CREATE TABLE IF NOT EXISTS PhaseChanges (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Phase_ID int not null references PhaseMaster (Phase_ID),
  Phase_Change_Date date not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  foreign key (Parent_Case_ID, Case_ID) references CaseSummary (Parent_Case_ID, Case_ID)
);


--Social Media Standard Models

--Instagram
CREATE TABLE IF NOT EXISTS igPosts (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Post_ID varchar(255) not null,
  PostDate timestamp not null,
  Caption text,
  Username varchar(255),
  Media_Type varchar(255),
  Media_Url varchar(255),
  Permalink varchar(255),
  Comments int,
  Likes int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Post_ID)
);


CREATE TABLE IF NOT EXISTS igDates (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Date_Date date not null,
  Followers int,
  Posts int,
  Comments int,
  Likes int
);


CREATE TABLE IF NOT EXISTS igHashtags (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Hashtag varchar(255) not null,
  Hashtag_Date date,
  Posts int,
  Media_Count_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igMediaTypes (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Media_Type varchar(255) not null,
  Media_Type_Date date,
  Posts int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igCountries (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Country varchar(255) not null,
  Countries_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igAges (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Age varchar(255) not null,
  Ages_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igGender (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Gender varchar(255) not null,
  Gender_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igLocales (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Locale varchar(255) not null,
  Locale_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igHours (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Hour varchar(255) not null,
  Hours_Date date,
  Posts int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS igCities (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  City varchar(255) not null,
  Cities_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);

----------------------------------------------

CREATE TABLE IF NOT EXISTS Departments (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  department_id int not null,
  deparment_name varchar(255) not null unique,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
  primary key (deparment_id)
)



CREATE TABLE IF NOT EXISTS TeamsforTargets (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Team_ID int not null,
  Team_Name varchar(255) not null unique,
  Team_Type varchar(255),
  Team_Sub_Type varchar(255),
  Team_member_id int references PeopleMaster(people_id),
  department_id int references Departments(department_id),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Team_ID, team_member_id)
)




CREATE TABLE IF NOT EXISTS Targets (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Target_ID int not null,
  deparment_id int not null references Departments(department_id),  
  Team_member_id int not null references PeopleMaster(people_id),
  Year int not null,
  Quarter int not null,
  Month int not null,
  Week int not null,
  Target decimal(12,2),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (target_id)



)