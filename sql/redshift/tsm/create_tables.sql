--Schema Notes:
--Truve Standard Data Model (TSM) is created as a common schema across different data sources such as CMS, CRM, Accounting, etc. For instance, TSM should be able to capture the key data points needed for all CMS systems that are being integrated to our technology. Third-Party Application (TPAs) integration process will include data engineering pipes that eventually extracts, transforms and loads (ETL) data into TSM data structure.

--Rules
--TSM is expected to change and expand over time.
--Custom 1-5 fields are added as a placeholder in case our technology needs to capture any custom columns that are not otherwise included. If there is no need to use these fields, they will stay empty.
--TSM is expected to capture customers from multiple tiers, e.g. small, medium and large package. This is to make sure our technology can be targeted to capture the needs of different types of clients provided that we are not overwhelming the clients with large amounts of data needs especially when they don't have the right set up. Our data transformation pipeline will consider the data needed from different tiers of customers. Therefore, one of the custom fields will be used to define which data fields are required in different tiers.

--There will be three groups TPAs;
----Those that will have a static schema and global technologies, e.g. Instagram, Google, Facebook. The schema will be same from one client to another except the truve client id we assign to the client. The data will not need much transformation since the incoming data is coming in a standard format.
----Those that will have dynamic schema, e.g. Filevine
----Those that will have strong static schema with some modification capabilities, e.g. CasePeer case management software, Litify, etc.


-- CMS Standard Models
CREATE TABLE IF NOT EXISTS CMS_PeopleType (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  People_Type_ID int not null, 
  People_Type varchar(255) not null,
  People_Sub_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, People_Type_ID) --JS added Client_Org_ID as source system may be assigned same people type IDs to different clients
);

CREATE TABLE IF NOT EXISTS CMS_Teams (
  Truve_Org_ID int not null,
  Client_Org_ID int not null,
  Team_ID int not null,
  Team_Name varchar(255) not null, --JS removed 'unique'
  Team_Type varchar(255),
  Team_Sub_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Team_ID), --JS Revised to add Client Org ID. Reason: Different clients may have the same Team ID.
  Constraint UniqueTeams UNIQUE (Client_Org_ID, Team_Name) --JS added unique constraint
);

CREATE TABLE IF NOT EXISTS CMS_People (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  People_ID int not null,
  --Team_ID int, --JS removed 'not null' Reason: this can be null if there is no team structure. Removed references since reference captured below under foreign key. DC removed and moved it to CMS_PeopleRoleAssignments
  --People_Type_ID int, --JS added, DC removed since one person can have multiple type_id assignments
  First_Name varchar(255) not null, -- JS added 'not'
  Middle_Name varchar(255), -- JS removed 'null',
  Last_Name varchar(255), -- JS added 'not', Shiv Removed it after checking Last_Name is null in Filevine
  Date_of_Birth date,
  Gender varchar(50),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, People_ID) --JS Revised to add Client Org ID. Reason: Different clients may have the same Team ID.
  --foreign key (Client_Org_ID, Team_ID) references CMS_Teams (Client_Org_ID, Team_ID) -- JS added. DC removed
  --foreign key (Client_Org_ID, People_Type_ID) references CMS_PeopleType (Client_Org_ID, People_Type_ID)
);

--JS removed this table
--DC revised the name and added it back
CREATE TABLE IF NOT EXISTS CMS_PeopleRoleAssignments (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  People_ID int not null,  -- references CMS_People(People_ID)
  People_Type_ID int , -- JS removed 'not null references CMS_PeopleType(People_Type_ID)' 
  Team_ID int, --DC added since a person can belong to different teams for different roles
  primary key (Client_Org_ID, People_ID, People_Type_ID), --DC added People_ID
  foreign key (Client_Org_ID, People_ID) references CMS_People(Client_Org_ID, People_ID), --JS added
  foreign key (Client_Org_ID, People_Type_ID) references CMS_PeopleType(Client_Org_ID, People_Type_ID), --JS added
  foreign key (Client_Org_ID, Team_ID) references CMS_Teams (Client_Org_ID, Team_ID) -- DC added
);


--JS moved over CMS_CaseTypes for referential integrity
CREATE TABLE IF NOT EXISTS CMS_PracticeTypes (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Practice_Type_ID int not null,
  Practice_Type_Name varchar(255) not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Practice_Type_ID), --JS added Client_Org_ID
  Constraint UniquePracticeNames UNIQUE (Client_Org_ID, Practice_Type_Name)
);


CREATE TABLE IF NOT EXISTS CMS_CaseTypes (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Practice_Type_ID int not null, --JS added
  Case_Type_ID int not null,
  Case_Type_Name varchar(255) not null, --JS removed 'unique'. Need to pull this value from ptojecttypecode for the existing client instance
  Case_Type_Category varchar(255),
  Case_Type_Sub_Category varchar(255),
  --Phase_Change_Date date, --JS took out this. Must have been left here by mistake
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Practice_Type_ID, Case_Type_ID), --JS added Client_Org_ID, Practice_Type_ID
  foreign key (Client_Org_ID, Practice_Type_ID) references CMS_PracticeTypes (Client_Org_ID, Practice_Type_ID),
  Constraint UniqueCaseTypes UNIQUE (Client_Org_ID, Practice_Type_ID, Case_Type_Name) --JS added Buse to check
);


CREATE TABLE IF NOT EXISTS CMS_Phases (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Practice_Type_ID int, --JS taken out 'not null references CMS_PracticeTypes (Practice_Type_ID)'
  Phase_ID int not null,
  Phase_Name varchar(255) not null, --can we make this unique for a given Client Org ID and Practice ID? 
  Phase_Order int,
  Phase_Category varchar(255),
  Phase_Sub_Category varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Practice_Type_ID, Phase_ID), --JS added Client_Org_ID and Practice Type ID
  foreign key (Client_Org_ID, Practice_Type_ID) references CMS_PracticeTypes (Client_Org_ID, Practice_Type_ID), --JS added reference
  Constraint UniqueNames UNIQUE (Client_Org_ID, Practice_Type_ID, Phase_Name) --JS added Buse to check
);


CREATE TABLE IF NOT EXISTS CMS_StatusMaster (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Status_ID int not null,
  --Practice_Type_ID int, --JS removed this line
  --Case_Type_ID int, --JS removed this line
  Status_Name varchar(255) not null,
  Sub_Status_Name varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Status_ID) --JS added Client_Org_ID
);


CREATE TABLE IF NOT EXISTS CMS_Cases ( --JS This is similar to the Projects table from Filevine
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Parent_Case_ID int not null, --JS added. If there is not parent case ID, this will be same as Case_ID. 
  Case_ID int not null, --JS This is the project_id field from Filevine
  Case_Name varchar(255), --JS Added
  Practice_Type_ID int not null, --JS removed 'not null references CMS_PracticeTypes (Practice_Type_ID)'
  --Case_Type_ID int not null, --JS added. Shiv Removed it as Case_Type_ID is already present in CaseDetails
  Case_Status_ID int, --JS Added
  --Is_Archived boolean, --JS removed
  Date_of_Incident date,
  Case_Create_Date date, --JS Added
  primary key (Client_Org_ID, Parent_Case_ID, Case_ID), ----JS added Client_Org_ID, Parent_Case_ID
  foreign key (Client_Org_ID, Practice_Type_ID) references CMS_PracticeTypes (Client_Org_ID, Practice_Type_ID), --JS added
  foreign key (Client_Org_ID, Case_Status_ID) references CMS_StatusMaster (Client_Org_ID, Status_ID), --JS added
  --foreign key (Client_Org_ID, Practice_Type_ID, Case_Type_ID) references CMS_CaseTypes (Client_Org_ID, Practice_Type_ID, Case_Type_ID) -- DC added Practice_Type_ID too. Shiv Removed it as Case_Type_ID is alredy present in Case_Details
);


CREATE TABLE IF NOT EXISTS CMS_InsuranceMaster (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Insurance_ID int not null,
  Insurance_Name varchar(255) not null,
  Insurance_Type varchar(255) not null,
  Insurance_Sub_Type varchar(255), --removed 'not null'
  Insurance_Limit1_Type varchar(255),
  Insurance_Limit2_Type varchar(255),
  Limit_Value1 decimal(10,4),
  Limit_Value2 decimal(10,4),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Insurance_ID) --JS added Client_Org_ID
);


CREATE TABLE IF NOT EXISTS CMS_CaseDetails (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  --Case_Create_Date date, --JS removed
  --Date_of_Incident date, --JS removed
  --Case_Name varchar(255), --JS removed
  Plaintiff_Full_Name varchar(255),
  Case_Marketing_Source varchar(255),
  Case_Source_Name varchar(255),
  Attorney_Fee_Percentage decimal(10,4),
  Estimated_Settlement_Date date, --Revised the name from Projected_Settlement_Date
  Estimated_Settlement_Amount decimal(10,4), --Revised the name from Projected_Settlement_Amount
  --Actual_Settlement_Date date, --JS removed this should be part of case figure type
  --Actual_Settlement_Amount decimal(8,2), --JS removed this should be part of case figure value
  If_Case_Settled_Presuit varchar(50),
  If_VIP_Case varchar(50),
  If_Case_Referred_Out varchar(50),
  Case_Type_ID int , --JS removed 'references CMS_CaseTypes(Case_Type_ID)'
  Attorney_ID int , --JS removed 'references CMS_People (People_ID)'
  Prelitigation_Paralegal_ID int , --JS removed 'references CMS_People (People_ID)'
  Litigation_Paralegal_ID int , --JS removed 'references CMS_People (People_ID)'
  CaseManager_ID int , --JS removed 'references CMS_People (People_ID)'
  Cocounsel_ID int , --JS removed 'references CMS_People (People_ID)'
  Case_Team_ID int , --JS removed 'references CMS_Teams (Team_ID)'
  Case_Status_ID int , --JS removed 'references CMS_StatusMaster (Status_ID)'
  Insurance_ID int , --JS removed 'references CMS_InsuranceMaster (Insurance_ID)'
  Case_Phase_ID int , --JS removed 'references CMS_Phases (Phase_ID)'
  Practice_Type_ID int, --JS added
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  Custom4 varchar(255),
  Custom5 varchar(255),
  primary key (Client_Org_ID, Parent_Case_ID, Case_ID), --JS Revised to add Client_Org_ID
  foreign key (Client_Org_ID, Parent_Case_ID, Case_ID) references CMS_Cases (Client_Org_ID, Parent_Case_ID, Case_ID), --JS added
  foreign key (Client_Org_ID, Practice_Type_ID, Case_Type_ID) references CMS_CaseTypes (Client_Org_ID, Practice_Type_ID, Case_Type_ID), -- DC added Practice_Type_ID too
  foreign key (Client_Org_ID, Attorney_ID) references CMS_People (Client_Org_ID, People_ID),
  foreign key (Client_Org_ID, Prelitigation_Paralegal_ID) references CMS_People(Client_Org_ID, People_ID),
  foreign key (Client_Org_ID, Litigation_Paralegal_ID) references CMS_People(Client_Org_ID, People_ID),
  foreign key (Client_Org_ID, CaseManager_ID) references CMS_People(Client_Org_ID, People_ID),
  foreign key (Client_Org_ID, Cocounsel_ID) references CMS_People(Client_Org_ID, People_ID),
  foreign key (Client_Org_ID, Case_Team_ID) references CMS_Teams (Client_Org_ID, Team_ID),
  foreign key (Client_Org_ID, Case_Status_ID) references CMS_StatusMaster (Client_Org_ID, Status_ID),
  foreign key (Client_Org_ID, Insurance_ID) references CMS_InsuranceMaster (Client_Org_ID, Insurance_ID),
  foreign key (Client_Org_ID, Practice_Type_ID, Case_Phase_ID) references CMS_Phases (Client_Org_ID, Practice_Type_ID, Phase_ID),
  foreign key (Client_Org_ID, Practice_Type_ID) references CMS_PracticeTypes (Client_Org_ID, Practice_Type_ID) --DC added
);


CREATE TABLE IF NOT EXISTS CMS_CaseFigures (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Case_Figure_ID varchar(255),
  Figure_Type varchar(255),
  Figure_Sub_Type varchar(255), --JS added
  Figure_Date date,
  Figure_Status varchar(255),
  Value decimal(10,4),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Parent_Case_ID, Case_ID, Case_Figure_ID), --JS added
  foreign key (Client_Org_ID, Parent_Case_ID, Case_ID) references CMS_CaseDetails (Client_Org_ID, Parent_Case_ID, Case_ID) --JS revised to add Client_Org_ID
);

CREATE TABLE IF NOT EXISTS CMS_IntakeDetails (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null, --JS added
  Parent_Case_ID int not null,
  Case_ID int not null,
  Intake_ID int not null,
  Person_Performing_Intake_ID int,
  Intake_Source varchar(255),
  Date_of_Intake date,
  Date_of_Incident date,
  Date_of_Signup date, --JS Added
  DUI_or_HitandRun varchar(50),
  Referral_Fee_Percentage decimal (10,4) , --JS revised from Referral_Fee_ID int
  If_Case_Referred_In varchar(50),
  If_Qualified_Case varchar(50),
  If_VIP_Lead varchar(50),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Parent_Case_ID, Case_ID, Intake_ID), --JS revised to add Client_Org_ID, Parent_Case_ID, Case_ID
  foreign key (Client_Org_ID, Parent_Case_ID, Case_ID) references CMS_CaseDetails (Client_Org_ID, Parent_Case_ID, Case_ID), --JS revised to add Client_Org_ID
  foreign key (Client_Org_ID, Person_Performing_Intake_ID) references CMS_People (Client_Org_ID, People_ID)
);



CREATE TABLE IF NOT EXISTS CMS_PhaseChanges (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Parent_Case_ID int not null,
  Case_ID int not null,
  Practice_Type_ID int,
  Phase_ID int not null, --JS removed 'references CMS_Phases (Phase_ID)'
  Phase_Change_Date date not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  foreign key (Client_Org_ID, Parent_Case_ID, Case_ID) references CMS_CaseDetails (Client_Org_ID, Parent_Case_ID, Case_ID), --JS revised to add Client_Org_ID
  foreign key (Client_Org_ID, Practice_Type_ID, Phase_ID) references CMS_Phases (Client_Org_ID, Practice_Type_ID, Phase_ID) --JS added
);


--Social Media Standard Models

--Instagram
CREATE TABLE IF NOT EXISTS IG_Posts (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
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


CREATE TABLE IF NOT EXISTS IG_Dates (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Date_Date date not null,
  Followers int,
  Posts int,
  Comments int,
  Likes int
);


CREATE TABLE IF NOT EXISTS IG_Hashtags (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Hashtag varchar(255) not null,
  Hashtag_Date date,
  Posts int,
  Media_Count_Type varchar(255),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_MediaTypes (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Media_Type varchar(255) not null,
  Media_Type_Date date,
  Posts int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Countries (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Country varchar(255) not null,
  Countries_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Ages (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Age varchar(255) not null,
  Ages_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Gender (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Gender varchar(255) not null,
  Gender_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Locales (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Locale varchar(255) not null,
  Locale_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Hours (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Hour varchar(255) not null,
  Hours_Date date,
  Posts int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);


CREATE TABLE IF NOT EXISTS IG_Cities (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  City varchar(255) not null,
  Cities_Date date,
  Followers int,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255)
);

--Application functionality schemas

CREATE TABLE IF NOT EXISTS APP_Departments (
  Truve_Org_ID int not null,
  Department_id int not null,
  Department_name varchar(255) not null, --JS removed 'unique', DC revised the name Deparment_name to Department_name
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Truve_Org_ID, Department_id), --JS added Truve_Org_ID, DC revised the name Deparment_id to Department_id
  Constraint UniqueDeps UNIQUE (Truve_Org_ID, department_name) -- JS added , DC revised the name Deparment_name to Department_name
);


CREATE TABLE IF NOT EXISTS APP_TeamsforTargets (
  Truve_Org_ID int not null,
  Team_ID int not null,
  Team_Name varchar(255) not null, --JS removed unique
  Team_Type varchar(255),
  Team_Sub_Type varchar(255),
  Team_Member_ID int, -- JS removed references CMS_People(people_id)
  Department_ID int, --JS removed 'references APP_Departments(department_id)' 
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Truve_Org_ID, Team_ID, Team_Member_ID), --JS added Truve Org ID
  --foreign key (Truve_Org_ID, Team_Member_ID) references CMS_People(Truve_Org_ID, People_ID), --JS added. DC removed it
  foreign key (Truve_Org_ID, Department_ID) references APP_Departments (Truve_Org_ID, Department_id), -- JS added, DC revised the name Deparment_ID to Department_ID and the name Deparment_id to Department_id
  Constraint APP_UniqueTeams UNIQUE (Truve_Org_ID, Team_Name) -- DC revised the constraint name 
);


CREATE TABLE IF NOT EXISTS APP_Targets (
  Truve_Org_ID int not null,
  Target_ID int not null,
  Department_ID int not null, --JS removed ' references APP_Departments(department_id)', DC revised the name Deparment_ID to Department_ID
  Team_Member_ID int not null, --JS removed ' references CMS_People(people_id)' 
  Year int not null,
  Quarter int not null,
  Month int not null,
  Week int not null,
  Target decimal(10,4),
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Truve_Org_ID, Target_ID), -- JS added Truve Org ID
  --foreign key (Truve_Org_ID, Team_Member_ID) references CMS_People(Truve_Org_ID, People_ID), --JS added. Dc removed it
  foreign key (Truve_Org_ID, Department_ID) references APP_Departments (Truve_Org_ID, Department_id) -- JS added, DC revised the name Deparment_ID to Department_ID and the name Deparment_id to Department_id
);


--CRM Standard Models

CREATE TABLE IF NOT EXISTS CRM_Users (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  User_ID int, --revised from User_ID
  First_Name varchar(255), --revised from FirstName
  Middle_Name varchar(255), -- DC added
  Last_Name varchar(255), --revised from LastName
  Email varchar(255),
  --Code varchar(255), --JS removed
  --CRM_Roles varchar(max), --JS removed
  --CRM_Permissions varchar(max), --JS removed
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, User_ID)
  );


CREATE TABLE IF NOT EXISTS CRM_Contacts ( --Revised from CRM_Contact
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Contact_ID int, --Js revised from ID
  FirstName varchar(255) not null, --added not null
  MiddleName varchar(255),
  LastName varchar(255),
  Address1 varchar(255),
  Address2 varchar(255),
  City varchar(255),
  State varchar(255),
  Zip varchar(255),
  County varchar(255),
  HomePhone varchar(255),
  MobilePhone varchar(255),
  WorkPhone varchar(255),
  Email varchar(255),
  PreferredContactMethod varchar(255),
  Date_of_Birth timestamp, --JS revised from Birthdate
  --Longitude varchar(255), --JS removed
  --Latitude varchar(255), --JS removed
  --SubscribeToMailingList boolean, --JS removed
  --BadAddress boolean, --JS removed
  If_Deceased boolean, --JS revised from Deceased
  Gender varchar(255),
  Minor boolean,
  Language varchar(255),
  Contact_Source varchar(255),--JS added
  Contact_Source_Type varchar(255),--JS added
  Contact_Source_SubType varchar(255),--JS added
  --Code varchar(255), --JS removed
  --DoNotText boolean, --JS removed
  Created_On date, --changed data type
  Created_By_ID int, --revised from CreatedBy_ID
  --PendingGeocode boolean, --JS removed
  --LeadIds varchar(255), --JS removed
  --CustomFields varchar(255) -- JS removed
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, Contact_ID), --JS added
  foreign key (Client_Org_ID, Created_By_ID) references CRM_Users (Client_Org_ID, User_ID)
);


  CREATE TABLE IF NOT EXISTS CRM_Status (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Id int,
  Summary varchar(max),
  InjuryInformation varchar(255),
  Status varchar(255),
  SubStatus varchar(255),
  SeverityLevel varchar(255),
  Code varchar(255),
  Contact int,
  PracticeArea int,
  MarketingSource varchar(255),
  ContactSource varchar(255),
  TalkedToOtherAttorneys varchar(255),
  FoundUsNotes varchar(255),
  UTM varchar(255),
  CurrentUrl varchar(255),
  ReferringUrl varchar(255),
  ClickId varchar(255),
  ClientId varchar(255),
  Keywords varchar(255),
  Campaign varchar(255),
  AppointmentLocation varchar(255),
  Office varchar(255),
  OfficeCode varchar(255),
  ReferredTo varchar(255),
  ReferredByName varchar(255),
  ReferredBy varchar(255),
  CreatedDate timestamp,
  IncidentDate timestamp,
  RejectedDate timestamp,
  ReferredDate timestamp,
  AssignedDate timestamp,
  AppointmentScheduledDate timestamp,
  ChaseDate timestamp,
  SignedUpDate timestamp,
  CaseClosedDate timestamp,
  LostDate timestamp,
  UnderReviewDate timestamp,
  PendingSignupDate timestamp,
  HoldDate timestamp,
  Intake int,
  Paralegal varchar(255),
  Investigator varchar(255),
  Attorney int,
  AssignedTo varchar(255),
  Creator int,
  RelatedContacts varchar(max),
  Messages varchar(max),
  Notes varchar(max),
  Opportunity varchar(255),
  PhoneCall varchar(255),
  CustomFields varchar(max),
  Settlements varchar(255),
  QualifiedLead varchar(255),
  WereYouAtFault varchar(255),
  Wasanyoneelseinthevehiclewithyou varchar(255),
  TreatmentatHospital varchar(255),
  Didyouseekanyotherdoctorstreatment varchar(255)
  );

-- DC removed - duplication
--  CREATE TABLE IF NOT EXISTS CMS_PhaseChanges (
--  Truve_Org_ID int not null,
--  Client_Org_ID varchar(255) not null,
--  Parent_Case_ID int not null,
--  Case_ID int not null,
--  Practice_Type_ID int,
--  Phase_ID int not null, --JS removed 'references CMS_Phases (Phase_ID)'
--  Phase_Change_Date date not null,
--  Custom1 varchar(255), --JS added
--  Custom2 varchar(255), --JS added
--  Custom3 varchar(255), --JS added
--  foreign key (Client_Org_ID, Parent_Case_ID, Case_ID) references CMS_CaseDetails (Client_Org_ID, Parent_Case_ID, Case_ID) --JS revised to add Client_Org_ID
--  foreign key (Client_Org_ID, Practice_Type_ID, Phase_ID) references CMS_Phases (Client_Org_ID, Practice_Type_ID, Phase_ID) --JS added
--);

-- DC added below table
CREATE TABLE IF NOT EXISTS CRM_PracticeTypes (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Practice_Type_ID int not null,
  Practice_Type_Name varchar(255) not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  primary key (Client_Org_ID, Practice_Type_ID), --JS added Client_Org_ID
  Constraint CRM_UniquePracticeNames UNIQUE (Client_Org_ID, Practice_Type_Name) -- DC revised constraint name
);

--DC changed the place of the below table for referential integrity
CREATE TABLE IF NOT EXISTS CRM_CaseTypes ( --JS revised from CaseType
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Practice_Type_ID varchar(255), --JS removed, DC added back, revised from Code
  Case_Type_ID int, --JS revised from ID
  Case_Type_Name varchar(255), --JS revised from TypeName
  Case_Type_NameShort varchar(255), --JS revised from TypeNameShort
  IsMassTort boolean,
  --CustomQuestionOrder varchar(255) --JS removed
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, Practice_Type_ID, Case_Type_ID), --DC added Client_Org_ID, Practice_Type_ID
  foreign key (Client_Org_ID, Practice_Type_ID) references CRM_PracticeTypes (Client_Org_ID, Practice_Type_ID), -- DC added
  Constraint CRM_UniqueCaseTypes UNIQUE (Client_Org_ID, Practice_Type_ID, Case_Type_Name) -- DC added, revised the constraint name
  );

--DC changed the place of the below table for referential integrity
 CREATE TABLE IF NOT EXISTS CRM_Leads ( --JS Revised from LeadRow
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Lead_Id int, --Revised from ID
  Contact_ID int, --JS added
  Practice_Type_ID int, --DC added, it should be the same as Code in CRM_CaseTypes and CRM_PracticeTypes
  --PhoneNumber varchar(255),--JS Removed
  --MobilePhone varchar(255),--JS Removed
  --HomePhone varchar(255),--JS Removed
  --WorkPhone varchar(255),--JS Removed
  --PreferredContactMethod varchar(255),--JS Removed
  --Email varchar(255),--JS Removed
  --FirstName varchar(255),--JS Removed
  --LastName varchar(255),--JS Removed
  --StatusId int, --JS Removed
  --StatusName varchar(255),--JS Removed
  --SubStatusId varchar(255),--JS Removed
  --SubStatusName varchar(255),--JS Removed
  Case_Type_ID int,
  --Code varchar(255),--JS Removed
  --LastStatusChangeDate timestamp --JS removed
  Date_of_Incident date, --JS added
  Lead_Create_date date, --JS added
  Created_By_ID int, --JS added
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, Lead_ID), --JS added
  foreign key (Client_Org_ID, Contact_ID) references CRM_Contacts (Client_Org_ID, Contact_ID), --JS added
  foreign key (Client_Org_ID, Practice_Type_ID, Case_Type_ID) references CRM_CaseTypes (Client_Org_ID, Practice_Type_ID, Case_Type_ID), --JS added, DC added Practice_Type_ID too
  foreign key (Client_Org_ID, Practice_Type_ID) references CRM_PracticeTypes (Client_Org_ID, Practice_Type_ID), --DC added
  foreign key (Client_Org_ID, Created_By_ID) references CRM_Users (Client_Org_ID, User_ID)
   );

-- JS added below table
  CREATE TABLE IF NOT EXISTS CRM_StatusChanges (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Lead_ID int not null,
  Status_ID int not null,
  Status_Change_Date date not null,
  Custom1 varchar(255),
  Custom2 varchar(255),
  Custom3 varchar(255),
  foreign key (Client_Org_ID, Lead_ID) references CRM_Leads (Client_Org_ID, Lead_ID),
  foreign key (Client_Org_ID, Status_ID) references CRM_Status (Client_Org_ID, Status_ID)
  );


  
  CREATE TABLE IF NOT EXISTS CRM_LeadSource (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Lead_Source_ID int, --revised from ID
  Lead_Source_Name varchar(255), --revised from SourceName
  Lead_Source_Type varchar(255), --JS added
  Lead_Source_Subtype varchar(255), --JS added
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, Lead_Source_ID)
  );

  -- DC moved over CRM_LeadDetail for referential integrity
CREATE TABLE IF NOT EXISTS CRM_Referrals (
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Referral_ID int, --revised from ID
  Referral_Name varchar(255), --revised from name
  Referral_Type varchar(255), --revised from Type
  --Code varchar(255), --JS removed
  If_Case_Referred_Out Boolean, --revised from Outgoing
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key(Client_Org_ID, Referral_ID)
  );

    
--Jay removed below table
  CREATE TABLE IF NOT EXISTS CRM_LeadDetail ( --Revised from CRM_Opportunities
  Truve_Org_ID int not null,
  Client_Org_ID varchar(255) not null,
  Opportunity_ID int, --JS revised from ID
  Lead_ID int, --JS added
  --FirstName varchar(255),--JS Removed
  --MiddleName varchar(255),--JS Removed
  --LastName varchar(255),--JS Removed
  --Address1 varchar(255),--JS Removed
  --Address2 varchar(255),--JS Removed
  --City varchar(255),--JS Removed
  --State varchar(255),--JS Removed
  --Zip varchar(255),--JS Removed
  --HomePhone varchar(255),--JS Removed
  --WorkPhone varchar(255),--JS Removed
  --MobilePhone varchar(255),--JS Removed
  --Email varchar(255),--JS Removed
  --Gender varchar(255),--JS Removed
  --Language varchar(255),--JS Removed
  --Birthdate timestamp,--JS Removed
  --PreferredContactMethod varchar(255),--JS Removed
  Status_ID int,
  --LeadStatus varchar(255),--JS Removed
  --SubStatus varchar(255),--JS Removed
  --Office varchar(255),--JS Removed
  Lead_Source_ID int,
  --MarketingSource varchar(255),--JS Removed
  --MarketingSourceDetails varchar(255),--JS Removed
  --ContactSource varchar(255),--JS Removed
  Summary varchar(max),
  InjuryInformation varchar(255),
  --IncidentDate timestamp,--JS Removed
  --CreatedDate timestamp,--JS Removed
  --LeadId int,--JS Removed
  Notes varchar(max), --revised from note
  Referred_By_ID int, -- revised from Referred by
  Referral_ID int, -- DC added
  Severity_Level varchar(255),
  County_of_Event varchar(255), --revised from County
  --AppointmentLocation varchar(255),--JS Removed
  --AppointmentScheduledDate timestamp,--JS Removed
  --Code varchar(255),--JS Removed
  --ReferringUrl varchar(255),--JS Removed
  --CurrentUrl varchar(255),--JS Removed
  --UTM varchar(255),--JS Removed
  --ClientId varchar(255),--JS Removed
  --ClickId varchar(255),--JS Removed
  --Keywords varchar(255),--JS Removed
  --Campaign varchar(255),--JS Removed
  If_Processed boolean, --revised from processed
  Processed_Date date, --revised from ProcessedDate
  Processed_By_ID int, --JS revised from ProcessedbyName
  --OpportunityTypeId int,--JS Removed
  DisregardReason varchar(255),
  --IsBeingEdited boolean,--JS Removed
  --CustomFields varchar(255),--JS Removed
  If_Assigned boolean, --JS added
  Assigned_To_ID int, --revised from AssignedTo
  --ProcessedBy varchar(255),--JS Removed
  Rejected_date date, --JS added
  Referred_date date, --JS added
  Signed_Up_Date date, 
  Case_Close_Date date,
  Lost_Date date,
  Paralegal_ID int,
  --Investigator varchar(255),
  Attorney_ID int,
  If_Qualified_Case boolean, -- DC added, moved from CRM_Leads
  Custom1 varchar(255), --JS added
  Custom2 varchar(255), --JS added
  Custom3 varchar(255), --JS added
  primary key (Client_Org_ID, Opportunity_ID),
  foreign key (Client_Org_ID, Lead_ID) references CRM_Leads(Client_Org_ID, Lead_ID),
  foreign key (Client_Org_ID, Status_ID) references CRM_Status (Client_Org_ID, Status_ID),
  foreign key (Client_Org_ID, Lead_Source_ID) references CRM_LeadSource (Client_Org_ID, Lead_Source_ID),
  foreign key (Client_Org_ID, Referred_By_ID) references CRM_Contacts(Client_Org_ID, Contact_ID),
  foreign key (Client_Org_ID, Referral_ID) references CRM_Referrals (Client_Org_ID, Referral_ID), -- DC added
  foreign key (Client_Org_ID, Processed_By_ID) references CRM_Users(Client_Org_ID, User_ID),
  foreign key (Client_Org_ID, Assigned_To_ID) references CRM_Users(Client_Org_ID, User_ID),
  foreign key (Client_Org_ID, Paralegal_ID) references CRM_Users(Client_Org_ID, User_ID),
  foreign key (Client_Org_ID, Attorney_ID) references CRM_Users(Client_Org_ID, User_ID)
  );

  -- Update from Buse
  CREATE TABLE IF NOT EXISTS ML_CaseValueClusteringKNN (
  Case_ID int not null,
  Neighborhood_Out_Of_2 boolean
  primary key (Case_ID) references CMS_Cases (Case_ID)
  );
  
 --CREATE TABLE IF NOT EXISTS CRM_LeadDetail (
  --Truve_Org_ID int not null,
  --Client_Org_ID varchar(255) not null,
  --Lead_ID int, --JS revised from id
  --Summary varchar(max),
  --InjuryInformation varchar(255),
  --Status varchar(255), --JS removed
  --SubStatus varchar(255), --JS removed
  --SeverityLevel varchar(255),
  --Code varchar(255), --JS removed
  --Contact_ID int, --JS revised from Contact
  --PracticeArea int,
  --MarketingSource varchar(255),
  --ContactSource varchar(255),
  --TalkedToOtherAttorneys varchar(255),
  --FoundUsNotes varchar(255),
  --UTM varchar(255),
  --CurrentUrl varchar(255),
  --ReferringUrl varchar(255),
  --ClickId varchar(255),
  --ClientId varchar(255),
  --Keywords varchar(255),
  --Campaign varchar(255),
  --AppointmentLocation varchar(255), --JS removed
  --Office varchar(255), --JS removed
  --OfficeCode varchar(255),  --JS removed
  --ReferredTo varchar(255),
  --ReferredByName varchar(255),
  --ReferredBy varchar(255),
  --CreatedDate timestamp,
  --IncidentDate timestamp,
  --RejectedDate timestamp,
  --ReferredDate timestamp,
  --AssignedDate timestamp,
  --AppointmentScheduledDate timestamp,
  --ChaseDate timestamp,
  --SignedUpDate timestamp,
  --CaseClosedDate timestamp,
  --LostDate timestamp,
  --UnderReviewDate timestamp,
  --PendingSignupDate timestamp,
  --HoldDate timestamp,
  --Intake int,
  --Paralegal varchar(255),
  --Investigator varchar(255),
  --Attorney int,
  --AssignedTo varchar(255),
  --Creator int,
  --RelatedContacts varchar(max),
  --Messages varchar(max), --JS removed
  --Notes varchar(max),
  --Opportunity varchar(255),
  --PhoneCall varchar(255),
  --CustomFields varchar(max), --JS removed
  --Settlements varchar(255), --JS removed
  --Custom1 varchar(255), --JS added
  --Custom2 varchar(255), --JS added
  --Custom3 varchar(255), --JS added
  --primary key (Client_Org_ID, Lead_ID) --JS added
  --foreign key (Client_Org_ID, Contact_ID) references CRM_Contacts (Client_Org_ID, Contact_ID) --JS added
  --);

 
  

  
  
