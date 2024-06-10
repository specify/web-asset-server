create table casiz.agent
(
    AgentID              int auto_increment
        primary key,
    TimestampCreated     datetime      not null,
    TimestampModified    datetime      null,
    Version              int           null,
    Abbreviation         varchar(50)   null,
    AgentType            tinyint       not null,
    DateOfBirth          date          null,
    DateOfBirthPrecision tinyint       null,
    DateOfDeath          date          null,
    DateOfDeathPrecision tinyint       null,
    DateType             tinyint       null,
    Email                varchar(50)   null,
    FirstName            varchar(50)   null,
    GUID                 varchar(128)  null,
    Initials             varchar(8)    null,
    Interests            varchar(255)  null,
    JobTitle             varchar(50)   null,
    LastName             varchar(256)  null,
    MiddleInitial        varchar(50)   null,
    Remarks              text          null,
    Title                varchar(50)   null,
    URL                  varchar(1024) null,
    CreatedByAgentID     int           null,
    CollectionCCID       int           null,
    InstitutionCCID      int           null,
    DivisionID           int           null,
    InstitutionTCID      int           null,
    SpecifyUserID        int           null,
    ModifiedByAgentID    int           null,
    ParentOrganizationID int           null,
    CollectionTCID       int           null,
    Suffix               varchar(50)   null,
    Date1                date          null,
    Date1Precision       tinyint       null,
    Date2                date          null,
    Date2Precision       tinyint       null,
    Integer1             int           null,
    Integer2             int           null,
    Text1                text          null,
    Text2                text          null,
    VerbatimDate1        varchar(128)  null,
    VerbatimDate2        varchar(128)  null,
    Text3                text          null,
    Text4                text          null,
    Text5                text          null,
    constraint FK58743055327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK58743057699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK587430584B8A3FA
        foreign key (ParentOrganizationID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.address
(
    AddressID         int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Address           varchar(255) null,
    Address2          varchar(255) null,
    Address3          varchar(400) null,
    Address4          varchar(400) null,
    Address5          varchar(400) null,
    City              varchar(64)  null,
    Country           varchar(64)  null,
    EndDate           date         null,
    Fax               varchar(50)  null,
    IsCurrent         bit          null,
    IsPrimary         bit          null,
    IsShipping        bit          null,
    Ordinal           int          null,
    Phone1            varchar(50)  null,
    Phone2            varchar(50)  null,
    PositionHeld      varchar(32)  null,
    PostalCode        varchar(32)  null,
    Remarks           text         null,
    RoomOrBuilding    varchar(50)  null,
    StartDate         date         null,
    State             varchar(64)  null,
    TypeOfAddr        varchar(32)  null,
    AgentID           int          null,
    CreatedByAgentID  int          null,
    ModifiedByAgentID int          null,
    constraint FKBB979BF4384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKBB979BF45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBB979BF47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.addressofrecord
(
    AddressOfRecordID int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Address           varchar(255) null,
    Address2          varchar(255) null,
    City              varchar(64)  null,
    Country           varchar(64)  null,
    PostalCode        varchar(32)  null,
    Remarks           text         null,
    State             varchar(64)  null,
    CreatedByAgentID  int          null,
    AgentID           int          null,
    ModifiedByAgentID int          null,
    constraint FKDBAAE4DC384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKDBAAE4DC5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDBAAE4DC7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index AbbreviationIDX
    on casiz.agent (Abbreviation);

create index AgentFirstNameIDX
    on casiz.agent (FirstName);

create index AgentGuidIDX
    on casiz.agent (GUID);

create index AgentLastNameIDX
    on casiz.agent (LastName(255));

create index AgentTypeIDX
    on casiz.agent (AgentType);

create table casiz.agentidentifier
(
    AgentIdentifierID int auto_increment
        primary key,
    TimestampCreated  datetime      not null,
    TimestampModified datetime      null,
    Version           int           null,
    Date1             date          null,
    Date1Precision    tinyint       null,
    Date2             date          null,
    Date2Precision    tinyint       null,
    Identifier        varchar(2048) not null,
    IdentifierType    varchar(256)  null,
    Remarks           text          null,
    Text1             text          null,
    Text2             text          null,
    Text3             text          null,
    Text4             text          null,
    Text5             text          null,
    YesNo1            bit           null,
    YesNo2            bit           null,
    YesNo3            bit           null,
    YesNo4            bit           null,
    YesNo5            bit           null,
    CreatedByAgentID  int           null,
    ModifiedByAgentID int           null,
    AgentID           int           not null,
    constraint FK6B8FAD6E384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK6B8FAD6E5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6B8FAD6E7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.agentspecialty
(
    AgentSpecialtyID  int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    OrderNumber       int         not null,
    SpecialtyName     varchar(64) not null,
    ModifiedByAgentID int         null,
    AgentID           int         not null,
    CreatedByAgentID  int         null,
    constraint AgentID
        unique (AgentID, OrderNumber),
    constraint FKDB5F5799384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKDB5F57995327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDB5F57997699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.agentvariant
(
    AgentVariantID    int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Country           varchar(2)   null,
    Language          varchar(2)   null,
    Name              varchar(255) null,
    VarType           tinyint      not null,
    Variant           varchar(2)   null,
    CreatedByAgentID  int          null,
    AgentID           int          not null,
    ModifiedByAgentID int          null,
    constraint FK8DA4DE0384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK8DA4DE05327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8DA4DE07699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.auth_group
(
    id   int auto_increment
        primary key,
    name varchar(150) not null,
    constraint name
        unique (name)
)
    charset = utf8mb3;

create table casiz.autonumberingscheme
(
    AutoNumberingSchemeID int auto_increment
        primary key,
    TimestampCreated      datetime    not null,
    TimestampModified     datetime    null,
    Version               int         null,
    FormatName            varchar(64) null,
    IsNumericOnly         bit         not null,
    SchemeClassName       varchar(64) null,
    SchemeName            varchar(64) null,
    TableNumber           int         not null,
    ModifiedByAgentID     int         null,
    CreatedByAgentID      int         null,
    constraint FK8227D14F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8227D14F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SchemeNameIDX
    on casiz.autonumberingscheme (SchemeName);

create table casiz.borrow
(
    BorrowID                  int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    CollectionMemberID        int             not null,
    CurrentDueDate            date            null,
    DateClosed                date            null,
    InvoiceNumber             varchar(50)     not null,
    IsClosed                  bit             null,
    IsFinancialResponsibility bit             null,
    Number1                   decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    OriginalDueDate           date            null,
    ReceivedDate              date            null,
    Remarks                   text            null,
    Text1                     text            null,
    Text2                     text            null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    AddressOfRecordID         int             null,
    ModifiedByAgentID         int             null,
    CreatedByAgentID          int             null,
    BorrowDate                date            null,
    BorrowDatePrecision       tinyint         null,
    NumberOfItemsBorrowed     int             null,
    Status                    varchar(64)     null,
    constraint FKAD8CA9F55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKAD8CA9F57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKAD8CA9F5DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create index BorColMemIDX
    on casiz.borrow (CollectionMemberID);

create index BorInvoiceNumberIDX
    on casiz.borrow (InvoiceNumber);

create index BorReceivedDateIDX
    on casiz.borrow (ReceivedDate);

create table casiz.borrowagent
(
    BorrowAgentID      int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    CollectionMemberID int         not null,
    Remarks            text        null,
    Role               varchar(32) not null,
    CreatedByAgentID   int         null,
    ModifiedByAgentID  int         null,
    BorrowID           int         not null,
    AgentID            int         not null,
    constraint Role
        unique (Role, AgentID, BorrowID),
    constraint FKF48F8A30384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKF48F8A305327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF48F8A307699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF48F8A30F8BF6F28
        foreign key (BorrowID) references casiz.borrow (BorrowID)
)
    charset = utf8mb3;

create index BorColMemIDX2
    on casiz.borrowagent (CollectionMemberID);

create table casiz.borrowmaterial
(
    BorrowMaterialID   int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    CollectionMemberID int          not null,
    Description        varchar(250) null,
    InComments         text         null,
    MaterialNumber     varchar(50)  not null,
    OutComments        text         null,
    Quantity           smallint     null,
    QuantityResolved   smallint     null,
    QuantityReturned   smallint     null,
    CreatedByAgentID   int          null,
    ModifiedByAgentID  int          null,
    BorrowID           int          not null,
    Text1              text         null,
    Text2              text         null,
    constraint FK86254A1C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK86254A1C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK86254A1CF8BF6F28
        foreign key (BorrowID) references casiz.borrow (BorrowID)
)
    charset = utf8mb3;

create index BorMaterialColMemIDX
    on casiz.borrowmaterial (CollectionMemberID);

create index BorMaterialNumberIDX
    on casiz.borrowmaterial (MaterialNumber);

create index DescriptionIDX
    on casiz.borrowmaterial (Description);

create table casiz.borrowreturnmaterial
(
    BorrowReturnMaterialID int auto_increment
        primary key,
    TimestampCreated       datetime not null,
    TimestampModified      datetime null,
    Version                int      null,
    CollectionMemberID     int      not null,
    Quantity               smallint null,
    Remarks                text     null,
    ReturnedDate           date     null,
    ReturnedByID           int      null,
    ModifiedByAgentID      int      null,
    CreatedByAgentID       int      null,
    BorrowMaterialID       int      not null,
    constraint FKA8170B8C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA8170B8C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA8170B8C83F392D6
        foreign key (BorrowMaterialID) references casiz.borrowmaterial (BorrowMaterialID),
    constraint FKA8170B8CC6A93143
        foreign key (ReturnedByID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index BorrowReturnedColMemIDX
    on casiz.borrowreturnmaterial (CollectionMemberID);

create index BorrowReturnedDateIDX
    on casiz.borrowreturnmaterial (ReturnedDate);

create table casiz.collectionobjectattribute
(
    CollectionObjectAttributeID int auto_increment
        primary key,
    TimestampCreated            datetime        not null,
    TimestampModified           datetime        null,
    Version                     int             null,
    CollectionMemberID          int             not null,
    Number1                     decimal(20, 10) null,
    Number10                    decimal(20, 10) null,
    Number11                    decimal(20, 10) null,
    Number12                    decimal(20, 10) null,
    Number13                    decimal(20, 10) null,
    Number14                    decimal(20, 10) null,
    Number15                    decimal(20, 10) null,
    Number16                    decimal(20, 10) null,
    Number17                    decimal(20, 10) null,
    Number18                    decimal(20, 10) null,
    Number19                    decimal(20, 10) null,
    Number2                     decimal(20, 10) null,
    Number20                    decimal(20, 10) null,
    Number21                    decimal(20, 10) null,
    Number22                    decimal(20, 10) null,
    Number23                    decimal(20, 10) null,
    Number24                    decimal(20, 10) null,
    Number25                    decimal(20, 10) null,
    Number26                    decimal(20, 10) null,
    Number27                    decimal(20, 10) null,
    Number28                    decimal(20, 10) null,
    Number29                    decimal(20, 10) null,
    Number3                     decimal(20, 10) null,
    number30                    int             null,
    Number31                    decimal(20, 10) null,
    Number32                    decimal(20, 10) null,
    Number33                    decimal(20, 10) null,
    Number34                    decimal(20, 10) null,
    Number35                    decimal(20, 10) null,
    Number36                    decimal(20, 10) null,
    Number37                    decimal(20, 10) null,
    Number38                    decimal(20, 10) null,
    Number39                    decimal(20, 10) null,
    Number4                     decimal(20, 10) null,
    Number40                    decimal(20, 10) null,
    Number41                    decimal(20, 10) null,
    Number42                    decimal(20, 10) null,
    Number5                     decimal(20, 10) null,
    Number6                     decimal(20, 10) null,
    Number7                     decimal(20, 10) null,
    number8                     int             null,
    Number9                     decimal(20, 10) null,
    Remarks                     text            null,
    Text1                       text            null,
    Text10                      varchar(50)     null,
    Text11                      varchar(50)     null,
    Text12                      varchar(50)     null,
    Text13                      varchar(50)     null,
    Text14                      varchar(50)     null,
    Text15                      varchar(64)     null,
    Text2                       text            null,
    Text3                       text            null,
    Text4                       varchar(50)     null,
    Text5                       varchar(50)     null,
    Text6                       varchar(100)    null,
    Text7                       varchar(100)    null,
    Text8                       varchar(50)     null,
    Text9                       varchar(50)     null,
    YesNo1                      bit             null,
    YesNo2                      bit             null,
    YesNo3                      bit             null,
    YesNo4                      bit             null,
    YesNo5                      bit             null,
    YesNo6                      bit             null,
    YesNo7                      bit             null,
    ModifiedByAgentID           int             null,
    CreatedByAgentID            int             null,
    BottomDistance              decimal(20, 10) null,
    Direction                   varchar(32)     null,
    DistanceUnits               varchar(16)     null,
    PositionState               varchar(32)     null,
    TopDistance                 decimal(20, 10) null,
    Text16                      text            null,
    Text17                      text            null,
    Text18                      text            null,
    Integer1                    int             null,
    Integer10                   int             null,
    Integer2                    int             null,
    Integer3                    int             null,
    Integer4                    int             null,
    Integer5                    int             null,
    Integer6                    int             null,
    Integer7                    int             null,
    Integer8                    int             null,
    Integer9                    int             null,
    Text19                      text            null,
    Text20                      text            null,
    Text21                      text            null,
    Text22                      text            null,
    Text23                      text            null,
    Text24                      text            null,
    Text25                      text            null,
    Text26                      text            null,
    Text27                      text            null,
    Text28                      text            null,
    Text29                      text            null,
    Text30                      text            null,
    YesNo10                     bit             null,
    YesNo11                     bit             null,
    YesNo12                     bit             null,
    YesNo13                     bit             null,
    YesNo14                     bit             null,
    YesNo15                     bit             null,
    YesNo16                     bit             null,
    YesNo17                     bit             null,
    YesNo18                     bit             null,
    YesNo19                     bit             null,
    YesNo20                     bit             null,
    YesNo8                      bit             null,
    YesNo9                      bit             null,
    Date1                       date            null,
    Date1Precision              tinyint         null,
    Agent1ID                    int             null,
    Text31                      text            null,
    Text32                      text            null,
    Text33                      text            null,
    Text34                      text            null,
    Text35                      text            null,
    Text36                      text            null,
    Text37                      text            null,
    Text38                      text            null,
    Text39                      text            null,
    Text40                      text            null,
    constraint FK32E0BFDF5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK32E0BFDF7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK32E0BFDFCF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index COLOBJATTRSColMemIDX
    on casiz.collectionobjectattribute (CollectionMemberID);

create table casiz.continentcodes
(
    code      char(2)     null,
    name      varchar(20) null,
    geonameId int         null
)
    charset = utf8mb3;

create index cc_geonameIdx
    on casiz.continentcodes (geonameId);

create table casiz.countryinfo
(
    iso_alpha2   char(2)      null,
    iso_alpha3   char(3)      null,
    iso_numeric  int          null,
    fips_code    varchar(3)   null,
    name         varchar(255) not null
        primary key,
    capital      varchar(255) null,
    areainsqkm   varchar(16)  null,
    population   varchar(16)  null,
    continent    char(2)      null,
    tld          varchar(32)  null,
    currencycode char(3)      null,
    currencyname char(32)     null,
    phone        char(32)     null,
    postalformat char(128)    null,
    postalregex  text         null,
    languages    varchar(255) null,
    geonameId    int          null,
    neighbors    varchar(255) null
)
    charset = utf8mb3;

create index ci_geonameIdx
    on casiz.countryinfo (geonameId);

create table casiz.datatype
(
    DataTypeID        int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Name              varchar(50) null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    constraint FK6AB199E45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6AB199E47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.deaccession
(
    DeaccessionID     int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    Date1             date            null,
    Date2             date            null,
    DeaccessionDate   date            null,
    DeaccessionNumber varchar(50)     not null,
    Integer1          int             null,
    Integer2          int             null,
    Integer3          int             null,
    Integer4          int             null,
    Integer5          int             null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    Number3           decimal(20, 10) null,
    Number4           decimal(20, 10) null,
    Number5           decimal(20, 10) null,
    Remarks           text            null,
    Status            varchar(64)     null,
    Text1             text            null,
    Text2             text            null,
    Text3             text            null,
    Text4             text            null,
    Text5             text            null,
    Type              varchar(64)     null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    YesNo3            bit             null,
    YesNo4            bit             null,
    YesNo5            bit             null,
    CreatedByAgentID  int             null,
    Agent1ID          int             null,
    Agent2ID          int             null,
    ModifiedByAgentID int             null,
    constraint FKC3EACC35327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC3EACC37699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC3EACC3CF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FKC3EACC3CF197EEA
        foreign key (Agent2ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.deaccessionagent
(
    DeaccessionAgentID int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    Remarks            text        null,
    Role               varchar(50) not null,
    AgentID            int         not null,
    DeaccessionID      int         not null,
    ModifiedByAgentID  int         null,
    CreatedByAgentID   int         null,
    constraint Role
        unique (Role, AgentID, DeaccessionID),
    constraint FKBE551822384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKBE5518225327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBE5518227699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKBE551822BE26B05E
        foreign key (DeaccessionID) references casiz.deaccession (DeaccessionID)
)
    charset = utf8mb3;

create table casiz.disposal
(
    DisposalID        int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    DisposalDate      date            null,
    DisposalNumber    varchar(50)     not null,
    doNotExport       bit             null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    Remarks           text            null,
    Text1             text            null,
    Text2             text            null,
    Type              varchar(64)     null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    ModifiedByAgentID int             null,
    CreatedByAgentID  int             null,
    DeaccessionID     int             null,
    constraint FK10FF9DB15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK10FF9DB17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK10FF9DB1BE26B05E
        foreign key (DeaccessionID) references casiz.deaccession (DeaccessionID)
)
    charset = utf8mb3;

create table casiz.disposalagent
(
    DisposalAgentID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Remarks           text        null,
    Role              varchar(50) not null,
    DisposalID        int         not null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    AgentID           int         not null,
    constraint Role
        unique (Role, AgentID, DisposalID),
    constraint FKD2CB8BF4384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKD2CB8BF45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD2CB8BF47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKD2CB8BF4C7670AE0
        foreign key (DisposalID) references casiz.disposal (DisposalID)
)
    charset = utf8mb3;

create table casiz.django_content_type
(
    id        int auto_increment
        primary key,
    app_label varchar(100) not null,
    model     varchar(100) not null,
    constraint django_content_type_app_label_model_76bd3d3b_uniq
        unique (app_label, model)
)
    charset = utf8mb3;

create table casiz.auth_permission
(
    id              int auto_increment
        primary key,
    name            varchar(255) not null,
    content_type_id int          not null,
    codename        varchar(100) not null,
    constraint auth_permission_content_type_id_codename_01ab375a_uniq
        unique (content_type_id, codename),
    constraint auth_permission_content_type_id_2f476e4b_fk_django_co
        foreign key (content_type_id) references casiz.django_content_type (id)
)
    charset = utf8mb3;

create table casiz.auth_group_permissions
(
    id            int auto_increment
        primary key,
    group_id      int not null,
    permission_id int not null,
    constraint auth_group_permissions_group_id_permission_id_0cd325b0_uniq
        unique (group_id, permission_id),
    constraint auth_group_permissio_permission_id_84c5c92e_fk_auth_perm
        foreign key (permission_id) references casiz.auth_permission (id),
    constraint auth_group_permissions_group_id_b120cbf9_fk_auth_group_id
        foreign key (group_id) references casiz.auth_group (id)
)
    charset = utf8mb3;

create table casiz.django_migrations
(
    id      int auto_increment
        primary key,
    app     varchar(255) not null,
    name    varchar(255) not null,
    applied datetime(6)  not null
)
    charset = utf8mb3;

create table casiz.django_session
(
    session_key  varchar(40) not null
        primary key,
    session_data longtext    not null,
    expire_date  datetime(6) not null
)
    charset = utf8mb3;

create index django_session_expire_date_a5c62663
    on casiz.django_session (expire_date);

create table casiz.dnaprimer
(
    DNAPrimerID                    int auto_increment
        primary key,
    TimestampCreated               datetime        not null,
    TimestampModified              datetime        null,
    Version                        int             null,
    Integer1                       int             null,
    Integer2                       int             null,
    Number1                        decimal(20, 10) null,
    Number2                        decimal(20, 10) null,
    PrimerDesignator               varchar(64)     null,
    PrimerNameForward              varchar(64)     null,
    PrimerNameReverse              varchar(64)     null,
    PrimerReferenceCitationForward varchar(300)    null,
    PrimerReferenceCitationReverse varchar(300)    null,
    PrimerReferenceLinkForward     varchar(300)    null,
    PrimerReferenceLinkReverse     varchar(300)    null,
    PrimerSequenceForward          varchar(128)    null,
    PrimerSequenceReverse          varchar(128)    null,
    purificationMethod             varchar(255)    null,
    Remarks                        text            null,
    ReservedInteger3               int             null,
    ReservedInteger4               int             null,
    ReservedNumber3                decimal(20, 10) null,
    ReservedNumber4                decimal(20, 10) null,
    ReservedText3                  text            null,
    ReservedText4                  text            null,
    Text1                          text            null,
    Text2                          text            null,
    YesNo1                         bit             null,
    YesNo2                         bit             null,
    ModifiedByAgentID              int             null,
    CreatedByAgentID               int             null,
    constraint FK5E4FB5AA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK5E4FB5AA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index DesignatorIDX
    on casiz.dnaprimer (PrimerDesignator);

create table casiz.geographytreedef
(
    GeographyTreeDefID int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    FullNameDirection  int         null,
    Name               varchar(64) not null,
    Remarks            text        null,
    CreatedByAgentID   int         null,
    ModifiedByAgentID  int         null,
    constraint FKE8DD68AB5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE8DD68AB7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.geographytreedefitem
(
    GeographyTreeDefItemID int auto_increment
        primary key,
    TimestampCreated       datetime    not null,
    TimestampModified      datetime    null,
    Version                int         null,
    FullNameSeparator      varchar(32) null,
    IsEnforced             bit         null,
    IsInFullName           bit         null,
    Name                   varchar(64) not null,
    RankID                 int         not null,
    Remarks                text        null,
    TextAfter              varchar(64) null,
    TextBefore             varchar(64) null,
    Title                  varchar(64) null,
    GeographyTreeDefID     int         not null,
    ModifiedByAgentID      int         null,
    CreatedByAgentID       int         null,
    ParentItemID           int         null,
    constraint FKF584963E5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF584963E7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF584963EA1F648D9
        foreign key (ParentItemID) references casiz.geographytreedefitem (GeographyTreeDefItemID),
    constraint FKF584963EBF9C9714
        foreign key (GeographyTreeDefID) references casiz.geographytreedef (GeographyTreeDefID)
)
    charset = utf8mb3;

create table casiz.geography
(
    GeographyID            int auto_increment
        primary key,
    TimestampCreated       datetime       not null,
    TimestampModified      datetime       null,
    Version                int            null,
    Abbrev                 varchar(16)    null,
    CentroidLat            decimal(19, 2) null,
    CentroidLon            decimal(19, 2) null,
    CommonName             varchar(128)   null,
    FullName               varchar(500)   null,
    GeographyCode          varchar(24)    null,
    GML                    text           null,
    GUID                   varchar(128)   null,
    HighestChildNodeNumber int            null,
    IsAccepted             bit            null,
    IsCurrent              bit            null,
    Name                   varchar(128)   null,
    NodeNumber             int            null,
    Number1                int            null,
    Number2                int            null,
    RankID                 int            not null,
    Remarks                text           null,
    Text1                  varchar(32)    null,
    Text2                  varchar(32)    null,
    TimestampVersion       datetime       null,
    ModifiedByAgentID      int            null,
    GeographyTreeDefItemID int            not null,
    ParentID               int            null,
    GeographyTreeDefID     int            not null,
    CreatedByAgentID       int            null,
    AcceptedID             int            null,
    constraint FK496A777C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK496A777C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK496A777C83AAF47E
        foreign key (ParentID) references casiz.geography (GeographyID),
    constraint FK496A777CBF9C9714
        foreign key (GeographyTreeDefID) references casiz.geographytreedef (GeographyTreeDefID),
    constraint FK496A777CE3C6E41A
        foreign key (GeographyTreeDefItemID) references casiz.geographytreedefitem (GeographyTreeDefItemID),
    constraint FK496A777CF484C03B
        foreign key (AcceptedID) references casiz.geography (GeographyID)
)
    charset = utf8mb3;

create table casiz.agentgeography
(
    AgentGeographyID  int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Remarks           text        null,
    Role              varchar(64) null,
    GeographyID       int         not null,
    CreatedByAgentID  int         null,
    AgentID           int         not null,
    ModifiedByAgentID int         null,
    constraint FK89CDCA17384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK89CDCA175327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK89CDCA177699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK89CDCA17D649F6D0
        foreign key (GeographyID) references casiz.geography (GeographyID)
)
    charset = utf8mb3;

create index GeoFullNameIDX
    on casiz.geography (FullName(255));

create index GeoNameIDX
    on casiz.geography (Name);

create index `Index 10`
    on casiz.geography (Number1);

create table casiz.geologictimeperiodtreedef
(
    GeologicTimePeriodTreeDefID int auto_increment
        primary key,
    TimestampCreated            datetime    not null,
    TimestampModified           datetime    null,
    Version                     int         null,
    FullNameDirection           int         null,
    Name                        varchar(64) not null,
    Remarks                     text        null,
    CreatedByAgentID            int         null,
    ModifiedByAgentID           int         null,
    constraint FK8109EA0C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8109EA0C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.geologictimeperiodtreedefitem
(
    GeologicTimePeriodTreeDefItemID int auto_increment
        primary key,
    TimestampCreated                datetime    not null,
    TimestampModified               datetime    null,
    Version                         int         null,
    FullNameSeparator               varchar(32) null,
    IsEnforced                      bit         null,
    IsInFullName                    bit         null,
    Name                            varchar(64) not null,
    RankID                          int         not null,
    Remarks                         text        null,
    TextAfter                       varchar(64) null,
    TextBefore                      varchar(64) null,
    Title                           varchar(64) null,
    ModifiedByAgentID               int         null,
    CreatedByAgentID                int         null,
    ParentItemID                    int         null,
    GeologicTimePeriodTreeDefID     int         not null,
    constraint FKB6DF7F1F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB6DF7F1F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB6DF7F1F9093DC94
        foreign key (ParentItemID) references casiz.geologictimeperiodtreedefitem (GeologicTimePeriodTreeDefItemID),
    constraint FKB6DF7F1F9988ED70
        foreign key (GeologicTimePeriodTreeDefID) references casiz.geologictimeperiodtreedef (GeologicTimePeriodTreeDefID)
)
    charset = utf8mb3;

create table casiz.geologictimeperiod
(
    GeologicTimePeriodID            int auto_increment
        primary key,
    TimestampCreated                datetime        not null,
    TimestampModified               datetime        null,
    Version                         int             null,
    EndPeriod                       decimal(20, 10) null,
    EndUncertainty                  decimal(20, 10) null,
    FullName                        varchar(255)    null,
    GUID                            varchar(128)    null,
    HighestChildNodeNumber          int             null,
    IsAccepted                      bit             null,
    IsBioStrat                      bit             null,
    Name                            varchar(64)     not null,
    NodeNumber                      int             null,
    RankID                          int             not null,
    Remarks                         text            null,
    Standard                        varchar(64)     null,
    StartPeriod                     decimal(20, 10) null,
    StartUncertainty                decimal(20, 10) null,
    Text1                           varchar(128)    null,
    Text2                           varchar(128)    null,
    ParentID                        int             null,
    GeologicTimePeriodTreeDefItemID int             not null,
    AcceptedID                      int             null,
    CreatedByAgentID                int             null,
    ModifiedByAgentID               int             null,
    GeologicTimePeriodTreeDefID     int             not null,
    constraint FKA2A8513B523E3360
        foreign key (AcceptedID) references casiz.geologictimeperiod (GeologicTimePeriodID),
    constraint FKA2A8513B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA2A8513B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA2A8513B9988ED70
        foreign key (GeologicTimePeriodTreeDefID) references casiz.geologictimeperiodtreedef (GeologicTimePeriodTreeDefID),
    constraint FKA2A8513BA8A8AC76
        foreign key (GeologicTimePeriodTreeDefItemID) references casiz.geologictimeperiodtreedefitem (GeologicTimePeriodTreeDefItemID),
    constraint FKA2A8513BE16467A3
        foreign key (ParentID) references casiz.geologictimeperiod (GeologicTimePeriodID)
)
    charset = utf8mb3;

create index GTPFullNameIDX
    on casiz.geologictimeperiod (FullName);

create index GTPGuidIDX
    on casiz.geologictimeperiod (GUID);

create index GTPNameIDX
    on casiz.geologictimeperiod (Name);

create table casiz.geoname
(
    geonameId      int           not null
        primary key,
    name           varchar(255)  null,
    asciiname      varchar(255)  null,
    alternatenames text          null,
    latitude       decimal(9, 7) null,
    longitude      decimal(9, 7) null,
    fclass         char          null,
    fcode          varchar(10)   null,
    country        varchar(2)    null,
    cc2            varchar(60)   null,
    admin1         varchar(20)   null,
    admin2         varchar(80)   null,
    admin3         varchar(20)   null,
    admin4         varchar(20)   null,
    population     int           null,
    elevation      int           null,
    gtopo30        int           null,
    timezone       varchar(40)   null,
    moddate        date          null,
    ISOCode        varchar(24)   null
)
    charset = utf8mb3;

create index nameidx
    on casiz.geoname (name);

create table casiz.hibernate_unique_key
(
    next_hi int null
)
    charset = utf8mb3;

create table casiz.inforequest
(
    InfoRequestID      int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    CollectionMemberID int          not null,
    Email              varchar(50)  null,
    Firstname          varchar(50)  null,
    InfoReqNumber      varchar(32)  null,
    Institution        varchar(127) null,
    Lastname           varchar(50)  null,
    Remarks            text         null,
    ReplyDate          date         null,
    RequestDate        date         null,
    ModifiedByAgentID  int          null,
    CreatedByAgentID   int          null,
    AgentID            int          null,
    constraint FK68918E21384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK68918E215327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK68918E217699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index IRColMemIDX
    on casiz.inforequest (CollectionMemberID);

create table casiz.institutionnetwork
(
    InstitutionNetworkID int auto_increment
        primary key,
    TimestampCreated     datetime     not null,
    TimestampModified    datetime     null,
    Version              int          null,
    AltName              varchar(128) null,
    Code                 varchar(64)  null,
    Copyright            text         null,
    Description          text         null,
    Disclaimer           text         null,
    IconURI              varchar(255) null,
    Ipr                  text         null,
    License              text         null,
    Name                 varchar(255) null,
    Remarks              text         null,
    TermsOfUse           text         null,
    Uri                  varchar(255) null,
    CreatedByAgentID     int          null,
    AddressID            int          null,
    ModifiedByAgentID    int          null,
    constraint FK945C55765327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK945C55767699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK945C5576E6A64D00
        foreign key (AddressID) references casiz.address (AddressID)
)
    charset = utf8mb3;

create index InstNetworkNameIDX
    on casiz.institutionnetwork (Name);

create table casiz.ios_colobjagents
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_colobjagents
    on casiz.ios_colobjagents (NewID);

create table casiz.ios_colobjbio
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_colobjbio
    on casiz.ios_colobjbio (NewID);

create table casiz.ios_colobjchron
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_colobjchron
    on casiz.ios_colobjchron (NewID);

create table casiz.ios_colobjcnts
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_colobjcnts
    on casiz.ios_colobjcnts (NewID);

create table casiz.ios_colobjgeo
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_colobjgeos
    on casiz.ios_colobjgeo (NewID);

create table casiz.ios_colobjlitho
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_colobjlitho
    on casiz.ios_colobjlitho (NewID);

create table casiz.ios_geogeo_cnt
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_geogeo_cnt
    on casiz.ios_geogeo_cnt (NewID);

create table casiz.ios_geogeo_cty
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_geogeo_cty
    on casiz.ios_geogeo_cty (NewID);

create table casiz.ios_geoloc
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_geoloc
    on casiz.ios_geoloc (NewID);

create table casiz.ios_geoloc_cnt
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_geoloc_cnt
    on casiz.ios_geoloc_cnt (NewID);

create table casiz.ios_geoloc_cty
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_geoloc_cty
    on casiz.ios_geoloc_cty (NewID);

create table casiz.ios_taxon_pid
(
    OldID int default 0 not null
        primary key,
    NewID int default 0 not null
)
    charset = latin1;

create index INX_ios_taxon_pid
    on casiz.ios_taxon_pid (NewID);

create table casiz.iz
(
    izId              int          not null
        primary key,
    Catalog_Number    varchar(32)  null,
    Other_Identifiers text         null,
    Phylum            varchar(500) null,
    Class             varchar(500) null,
    `Order`           varchar(500) null,
    Family            varchar(500) null,
    Genus             varchar(500) null,
    Species           varchar(500) null,
    Determined_Date   date         null,
    Determiner        varchar(500) null,
    Notes             text         null,
    Preservative      varchar(32)  null,
    Acronym           varchar(50)  null,
    Acc___            varchar(50)  null,
    Collectors        text         null,
    Start_Date        date         null,
    End_Date          date         null,
    Continent         varchar(500) null,
    Country           varchar(500) null,
    State             varchar(500) null,
    County            varchar(500) null,
    Full_Name         varchar(500) null,
    Island_Group      varchar(64)  null,
    Island            varchar(64)  null,
    Locality          varchar(500) null,
    Latitude1         varchar(20)  null,
    Longitude1        varchar(20)  null,
    Latitude2         varchar(20)  null,
    Longitude2        varchar(20)  null,
    Orig__fix_        varchar(50)  null,
    Start_Depth       double       null,
    End_Depth         double       null,
    Depth_Unit        varchar(23)  null
)
    charset = utf8mb3;

create table casiz.iz_portal
(
    iz_portalId                                       int          not null
        primary key,
    CASIZ_Number                                      varchar(32)  null,
    Type_Status                                       varchar(50)  null,
    Identified_Scientific_Name                        varchar(255) null,
    Accepted_Scientific_Name                          varchar(255) null,
    Identified_Phylum                                 varchar(500) null,
    Phylum                                            varchar(500) null,
    Identified_Subphylum                              varchar(500) null,
    Subphylum                                         varchar(500) null,
    Identified_Class                                  varchar(500) null,
    Class                                             varchar(500) null,
    Identified_Subclass                               varchar(500) null,
    Subclass                                          varchar(500) null,
    Identified_Subterclass                            varchar(500) null,
    Subterclass                                       varchar(500) null,
    Identified_Infraclass                             varchar(500) null,
    Infraclass                                        varchar(500) null,
    Identified_Superorder                             varchar(500) null,
    Superorder                                        varchar(500) null,
    Identified_Order                                  varchar(500) null,
    `Order`                                           varchar(500) null,
    Identified_Infraorder                             varchar(500) null,
    Infraorder                                        varchar(500) null,
    Identified_Suborder                               varchar(500) null,
    Suborder                                          varchar(500) null,
    Identified_Superfamily                            varchar(500) null,
    Superfamily                                       varchar(500) null,
    Identified_Family                                 varchar(500) null,
    Family                                            varchar(500) null,
    Identified_Subfamily                              varchar(500) null,
    Subfamily                                         varchar(500) null,
    Identified_Genus                                  varchar(500) null,
    Accepted_Genus                                    varchar(500) null,
    Identified_Species                                varchar(500) null,
    Accepted_Species                                  varchar(500) null,
    Qualifier                                         varchar(16)  null,
    Addendum                                          varchar(16)  null,
    Specimen_Notes                                    text         null,
    `Prep_type:_Preservative:___of_Specimens`         text         null,
    Orig__fixative                                    varchar(50)  null,
    Determined_by                                     varchar(500) null,
    Determined_Date                                   date         null,
    `SubContinent_[eg_Pacific_Ocean,_Gulf_of_Mexico]` varchar(500) null,
    Continent                                         varchar(500) null,
    Country                                           varchar(500) null,
    `SubCountry_[eg_Gulf_of_California]`              varchar(500) null,
    State                                             varchar(500) null,
    `SubState_[eg_Channel_Islands]`                   varchar(500) null,
    County                                            varchar(500) null,
    Locality                                          varchar(255) null,
    Start_Latitude                                    varchar(20)  null,
    Start_Longitude                                   varchar(20)  null,
    End_Latitude                                      varchar(20)  null,
    End_Longitude                                     varchar(20)  null,
    Collectors                                        text         null,
    `Start_Date_(Year)`                               int          null,
    `Start_Date_(Month)`                              int          null,
    `Start_Date_(Day)`                                int          null,
    `End_Date_(Year)`                                 int          null,
    `End_Date_(Month)`                                int          null,
    `End_Date_(Day)`                                  int          null,
    Verbatim_Coll__Date                               varchar(50)  null,
    Coll__Method                                      varchar(50)  null,
    Expedition___Project                              varchar(400) null,
    Field___Station__                                 text         null,
    Field_haul___Tow__                                varchar(50)  null,
    Other_Spec__Identifiers                           text         null,
    Collection_Name                                   varchar(500) null,
    Start_Depth                                       double       null,
    End_Depth                                         double       null,
    Depth_Unit                                        varchar(23)  null,
    Start_Elevation                                   double       null,
    End_Elevation                                     double       null,
    Original_Elevation_Unit                           varchar(50)  null,
    Internal_Acc___                                   varchar(50)  null,
    Acronym                                           varchar(50)  null,
    Collection_Object_Attachments                     text         null
)
    charset = utf8mb3;

create table casiz.lithostrattreedef
(
    LithoStratTreeDefID int auto_increment
        primary key,
    TimestampCreated    datetime    not null,
    TimestampModified   datetime    null,
    Version             int         null,
    FullNameDirection   int         null,
    Name                varchar(64) not null,
    Remarks             text        null,
    CreatedByAgentID    int         null,
    ModifiedByAgentID   int         null,
    constraint FK268699E15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK268699E17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.lithostrattreedefitem
(
    LithoStratTreeDefItemID int auto_increment
        primary key,
    TimestampCreated        datetime    not null,
    TimestampModified       datetime    null,
    Version                 int         null,
    FullNameSeparator       varchar(32) null,
    IsEnforced              bit         null,
    IsInFullName            bit         null,
    Name                    varchar(64) not null,
    RankID                  int         not null,
    Remarks                 text        null,
    TextAfter               varchar(64) null,
    TextBefore              varchar(64) null,
    Title                   varchar(64) null,
    ModifiedByAgentID       int         null,
    ParentItemID            int         null,
    LithoStratTreeDefID     int         not null,
    CreatedByAgentID        int         null,
    constraint FKEC263C745327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKEC263C7472939D3A
        foreign key (LithoStratTreeDefID) references casiz.lithostrattreedef (LithoStratTreeDefID),
    constraint FKEC263C747699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKEC263C748340DB49
        foreign key (ParentItemID) references casiz.lithostrattreedefitem (LithoStratTreeDefItemID)
)
    charset = utf8mb3;

create table casiz.lithostrat
(
    LithoStratID            int auto_increment
        primary key,
    TimestampCreated        datetime        not null,
    TimestampModified       datetime        null,
    Version                 int             null,
    FullName                varchar(255)    null,
    GUID                    varchar(128)    null,
    HighestChildNodeNumber  int             null,
    IsAccepted              bit             null,
    Name                    varchar(64)     not null,
    NodeNumber              int             null,
    Number1                 decimal(20, 10) null,
    Number2                 decimal(20, 10) null,
    RankID                  int             not null,
    Remarks                 text            null,
    Text1                   text            null,
    Text2                   text            null,
    YesNo1                  bit             null,
    YesNo2                  bit             null,
    LithoStratTreeDefItemID int             not null,
    AcceptedID              int             null,
    LithoStratTreeDefID     int             not null,
    ModifiedByAgentID       int             null,
    CreatedByAgentID        int             null,
    ParentID                int             null,
    constraint FK329297065327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3292970672939D3A
        foreign key (LithoStratTreeDefID) references casiz.lithostrattreedef (LithoStratTreeDefID),
    constraint FK329297067699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK329297067A1D53CB
        foreign key (AcceptedID) references casiz.lithostrat (LithoStratID),
    constraint FK32929706943880E
        foreign key (ParentID) references casiz.lithostrat (LithoStratID),
    constraint FK3292970699E26740
        foreign key (LithoStratTreeDefItemID) references casiz.lithostrattreedefitem (LithoStratTreeDefItemID)
)
    charset = utf8mb3;

create index LithoFullNameIDX
    on casiz.lithostrat (FullName);

create index LithoGuidIDX
    on casiz.lithostrat (GUID);

create index LithoNameIDX
    on casiz.lithostrat (Name);

create table casiz.morphbankview
(
    MorphBankViewID             int auto_increment
        primary key,
    TimestampCreated            datetime     not null,
    TimestampModified           datetime     null,
    Version                     int          null,
    DevelopmentState            varchar(128) null,
    Form                        varchar(128) null,
    ImagingPreparationTechnique varchar(128) null,
    ImagingTechnique            varchar(128) null,
    MorphBankExternalViewID     int          null,
    Sex                         varchar(32)  null,
    SpecimenPart                varchar(128) null,
    ViewAngle                   varchar(128) null,
    ViewName                    varchar(128) null,
    ModifiedByAgentID           int          null,
    CreatedByAgentID            int          null,
    constraint FKDED66BE95327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDED66BE97699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.attachmentimageattribute
(
    AttachmentImageAttributeID int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    CreativeCommons            varchar(500)    null,
    Height                     int             null,
    ImageType                  varchar(80)     null,
    Magnification              double          null,
    MBImageID                  int             null,
    Number1                    decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    Remarks                    text            null,
    Resolution                 double          null,
    Text1                      varchar(200)    null,
    Text2                      varchar(200)    null,
    TimestampLastSend          datetime        null,
    TimestampLastUpdateCheck   datetime        null,
    ViewDescription            varchar(80)     null,
    Width                      int             null,
    YesNo1                     bit             null,
    YesNo2                     bit             null,
    CreatedByAgentID           int             null,
    ModifiedByAgentID          int             null,
    MorphBankViewID            int             null,
    constraint FK857D77845327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK857D77847699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK857D7784FD8D2A2A
        foreign key (MorphBankViewID) references casiz.morphbankview (MorphBankViewID)
)
    charset = utf8mb3;

create table casiz.preparationattribute
(
    PreparationAttributeID int auto_increment
        primary key,
    TimestampCreated       datetime        not null,
    TimestampModified      datetime        null,
    Version                int             null,
    CollectionMemberID     int             not null,
    attrdate               date            null,
    Number1                decimal(20, 10) null,
    Number2                decimal(20, 10) null,
    Number3                decimal(20, 10) null,
    Number4                int             null,
    Number5                int             null,
    Number6                int             null,
    Number7                int             null,
    Number8                int             null,
    Number9                smallint        null,
    Remarks                text            null,
    Text1                  text            null,
    Text10                 text            null,
    Text11                 varchar(50)     null,
    Text12                 varchar(50)     null,
    Text13                 varchar(50)     null,
    Text14                 varchar(50)     null,
    Text15                 varchar(50)     null,
    Text16                 varchar(50)     null,
    Text17                 varchar(50)     null,
    Text18                 varchar(50)     null,
    Text19                 varchar(50)     null,
    Text2                  text            null,
    Text20                 varchar(50)     null,
    Text21                 varchar(50)     null,
    Text22                 varchar(50)     null,
    Text23                 varchar(50)     null,
    Text24                 varchar(50)     null,
    Text25                 varchar(50)     null,
    Text26                 varchar(50)     null,
    Text3                  varchar(50)     null,
    Text4                  varchar(50)     null,
    Text5                  varchar(50)     null,
    Text6                  varchar(50)     null,
    Text7                  varchar(50)     null,
    Text8                  varchar(50)     null,
    Text9                  varchar(50)     null,
    YesNo1                 bit             null,
    YesNo2                 bit             null,
    YesNo3                 bit             null,
    YesNo4                 bit             null,
    CreatedByAgentID       int             null,
    ModifiedByAgentID      int             null,
    constraint FK984BFDE55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK984BFDE57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index PrepAttrsColMemIDX
    on casiz.preparationattribute (CollectionMemberID);

create table casiz.project
(
    ProjectID          int auto_increment
        primary key,
    TimestampCreated   datetime        not null,
    TimestampModified  datetime        null,
    Version            int             null,
    CollectionMemberID int             not null,
    EndDate            date            null,
    GrantAgency        varchar(64)     null,
    GrantNumber        varchar(64)     null,
    Number1            decimal(20, 10) null,
    Number2            decimal(20, 10) null,
    ProjectDescription varchar(255)    null,
    ProjectName        varchar(128)    not null,
    ProjectNumber      varchar(64)     null,
    Remarks            text            null,
    StartDate          date            null,
    Text1              text            null,
    Text2              text            null,
    URL                varchar(1024)   null,
    YesNo1             bit             null,
    YesNo2             bit             null,
    ProjectAgentID     int             null,
    CreatedByAgentID   int             null,
    ModifiedByAgentID  int             null,
    constraint FKED904B195327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKED904B195DDECE9
        foreign key (ProjectAgentID) references casiz.agent (AgentID),
    constraint FKED904B197699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index ProjectNameIDX
    on casiz.project (ProjectName);

create index ProjectNumberIDX
    on casiz.project (ProjectNumber);

create table casiz.sgrmatchconfiguration
(
    id                    bigint auto_increment
        primary key,
    name                  varchar(128) not null,
    similarityFields      text         not null,
    serverUrl             text         not null,
    filterQuery           varchar(128) not null,
    queryFields           text         not null,
    remarks               text         not null,
    boostInterestingTerms tinyint(1)   not null,
    nRows                 int          not null
)
    charset = utf8mb3;

create table casiz.sgrbatchmatchresultset
(
    id                   bigint auto_increment
        primary key,
    insertTime           timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    name                 varchar(128)                        not null,
    recordSetID          bigint                              null,
    matchConfigurationId bigint                              not null,
    query                text                                not null,
    remarks              text                                not null,
    dbTableId            int                                 null,
    constraint sgrbatchmatchresultsetfk2
        foreign key (matchConfigurationId) references casiz.sgrmatchconfiguration (id)
)
    charset = utf8mb3;

create table casiz.sgrbatchmatchresultitem
(
    id                    bigint auto_increment
        primary key,
    matchedId             varchar(128) not null,
    maxScore              float        not null,
    batchMatchResultSetId bigint       not null,
    qTime                 int          not null,
    constraint sgrbatchmatchresultitemfk1
        foreign key (batchMatchResultSetId) references casiz.sgrbatchmatchresultset (id)
            on delete cascade
)
    charset = utf8mb3;

create table casiz.spauditlog
(
    SpAuditLogID      int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    Action            tinyint  not null,
    ParentRecordId    int      null,
    ParentTableNum    smallint null,
    RecordId          int      null,
    RecordVersion     int      not null,
    TableNum          smallint not null,
    ModifiedByAgentID int      null,
    CreatedByAgentID  int      null,
    constraint FKD51C16E65327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD51C16E67699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.spauditlogfield
(
    SpAuditLogFieldID int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    FieldName         varchar(128) null,
    NewValue          text         null,
    OldValue          text         null,
    ModifiedByAgentID int          null,
    SpAuditLogID      int          null,
    CreatedByAgentID  int          null,
    constraint FK154AE9D45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK154AE9D469D0534A
        foreign key (SpAuditLogID) references casiz.spauditlog (SpAuditLogID),
    constraint FK154AE9D47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.specifyuser
(
    SpecifyUserID       int auto_increment
        primary key,
    TimestampCreated    datetime     not null,
    TimestampModified   datetime     null,
    Version             int          null,
    AccumMinLoggedIn    bigint       null,
    EMail               varchar(64)  null,
    IsLoggedIn          bit          not null,
    IsLoggedInReport    bit          not null,
    LoginCollectionName varchar(64)  null,
    LoginDisciplineName varchar(64)  null,
    LoginOutTime        datetime     null,
    Name                varchar(64)  not null,
    Password            varchar(255) not null,
    UserType            varchar(32)  null,
    CreatedByAgentID    int          null,
    ModifiedByAgentID   int          null,
    constraint Name
        unique (Name),
    constraint FKD54E94AC5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD54E94AC7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

alter table casiz.agent
    add constraint FK58743054BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID);

create table casiz.attachment
(
    AttachmentID               int auto_increment
        primary key,
    TimestampCreated           datetime         not null,
    TimestampModified          datetime         null,
    Version                    int              null,
    AttachmentLocation         varchar(128)     null,
    CopyrightDate              varchar(64)      null,
    CopyrightHolder            varchar(64)      null,
    Credit                     varchar(64)      null,
    DateImaged                 varchar(64)      null,
    FileCreatedDate            date             null,
    GUID                       varchar(128)     null,
    License                    varchar(64)      null,
    MimeType                   varchar(1024)    null,
    origFilename               mediumtext       not null,
    Remarks                    text             null,
    ScopeID                    int              null,
    ScopeType                  tinyint          null,
    TableID                    smallint         not null,
    Title                      varchar(255)     null,
    Visibility                 tinyint          null,
    VisibilitySetByID          int              null,
    AttachmentImageAttributeID int              null,
    ModifiedByAgentID          int              null,
    CreatedByAgentID           int              null,
    IsPublic                   bit default b'1' not null,
    CreatorID                  int              null,
    CaptureDevice              varchar(128)     null,
    LicenseLogoUrl             varchar(256)     null,
    MetadataText               varchar(256)     null,
    SubjectOrientation         varchar(64)      null,
    Subtype                    varchar(64)      null,
    Type                       varchar(64)      null,
    AttachmentStorageConfig    text             null,
    constraint FK8AF759235327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8AF759237699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK8AF759237BF1F70B
        foreign key (VisibilitySetByID) references casiz.specifyuser (SpecifyUserID),
    constraint FK8AF759239B37C589
        foreign key (CreatorID) references casiz.agent (AgentID),
    constraint FK8AF75923C620DBC6
        foreign key (AttachmentImageAttributeID) references casiz.attachmentimageattribute (AttachmentImageAttributeID)
)
    charset = utf8mb3;

create table casiz.agentattachment
(
    AgentAttachmentID int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    Ordinal           int      not null,
    Remarks           text     null,
    ModifiedByAgentID int      null,
    CreatedByAgentID  int      null,
    AgentID           int      not null,
    AttachmentID      int      not null,
    constraint FK56FE59E8384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK56FE59E85327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK56FE59E87699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK56FE59E8C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create index AttchScopeIDIDX
    on casiz.attachment (ScopeID);

create index AttchScopeTypeIDX
    on casiz.attachment (ScopeType);

create index AttchmentGuidIDX
    on casiz.attachment (GUID);

create index DateImagedIDX
    on casiz.attachment (DateImaged);

create index TitleIDX
    on casiz.attachment (Title);

create table casiz.attachmentmetadata
(
    AttachmentMetadataID int auto_increment
        primary key,
    TimestampCreated     datetime     not null,
    TimestampModified    datetime     null,
    Version              int          null,
    Name                 varchar(64)  not null,
    Value                varchar(128) not null,
    ModifiedByAgentID    int          null,
    AttachmentID         int          null,
    CreatedByAgentID     int          null,
    constraint FK991701525327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK991701527699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK99170152C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.attachmenttag
(
    AttachmentTagID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Tag               varchar(64) not null,
    ModifiedByAgentID int         null,
    AttachmentID      int         not null,
    CreatedByAgentID  int         null,
    constraint FKA62FAF975327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA62FAF977699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA62FAF97C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.borrowattachment
(
    BorrowAttachmentID int auto_increment
        primary key,
    TimestampCreated   datetime not null,
    TimestampModified  datetime null,
    Version            int      null,
    Ordinal            int      not null,
    Remarks            text     null,
    AttachmentID       int      not null,
    CreatedByAgentID   int      null,
    ModifiedByAgentID  int      null,
    BorrowID           int      not null,
    constraint FK3263D4D85327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3263D4D87699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK3263D4D8C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID),
    constraint FK3263D4D8F8BF6F28
        foreign key (BorrowID) references casiz.borrow (BorrowID)
)
    charset = utf8mb3;

create table casiz.deaccessionattachment
(
    DeaccessionAttachmentID int auto_increment
        primary key,
    TimestampCreated        datetime not null,
    TimestampModified       datetime null,
    Version                 int      null,
    Ordinal                 int      not null,
    Remarks                 text     null,
    DeaccessionID           int      not null,
    CreatedByAgentID        int      null,
    ModifiedByAgentID       int      null,
    AttachmentID            int      not null,
    constraint FKF4032E265327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF4032E267699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF4032E26BE26B05E
        foreign key (DeaccessionID) references casiz.deaccession (DeaccessionID),
    constraint FKF4032E26C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.disposalattachment
(
    DisposalAttachmentID int auto_increment
        primary key,
    TimestampCreated     datetime not null,
    TimestampModified    datetime null,
    Version              int      null,
    Ordinal              int      not null,
    Remarks              text     null,
    DisposalID           int      not null,
    AttachmentID         int      not null,
    ModifiedByAgentID    int      null,
    CreatedByAgentID     int      null,
    constraint FKDCF64D945327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDCF64D947699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKDCF64D94C7670AE0
        foreign key (DisposalID) references casiz.disposal (DisposalID),
    constraint FKDCF64D94C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.notifications_message
(
    id               int auto_increment
        primary key,
    timestampcreated datetime(6) not null,
    content          longtext    not null,
    user_id          int         not null,
    `read`           tinyint(1)  not null,
    constraint notifications_messag_user_id_89f939e6_fk_specifyus
        foreign key (user_id) references casiz.specifyuser (SpecifyUserID)
)
    charset = utf8mb3;

create table casiz.spexportschemamapping
(
    SpExportSchemaMappingID int auto_increment
        primary key,
    TimestampCreated        datetime     not null,
    TimestampModified       datetime     null,
    Version                 int          null,
    CollectionMemberID      int          not null,
    Description             varchar(255) null,
    MappingName             varchar(50)  null,
    TimeStampExported       datetime     null,
    ModifiedByAgentID       int          null,
    CreatedByAgentID        int          null,
    constraint FK68B61F5C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK68B61F5C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SPEXPSCHMMAPColMemIDX
    on casiz.spexportschemamapping (CollectionMemberID);

create table casiz.spfieldvaluedefault
(
    SpFieldValueDefaultID int auto_increment
        primary key,
    TimestampCreated      datetime    not null,
    TimestampModified     datetime    null,
    Version               int         null,
    CollectionMemberID    int         not null,
    FieldName             varchar(32) null,
    IdValue               int         null,
    StrValue              varchar(64) null,
    TableName             varchar(32) null,
    CreatedByAgentID      int         null,
    ModifiedByAgentID     int         null,
    constraint FK14E6C4ED5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK14E6C4ED7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SpFieldValueDefaultColMemIDX
    on casiz.spfieldvaluedefault (CollectionMemberID);

create table casiz.splibraryrole
(
    id          int auto_increment
        primary key,
    name        varchar(1024) not null,
    description longtext      not null
)
    charset = utf8mb3;

create table casiz.splibraryrolepolicy
(
    id       int auto_increment
        primary key,
    resource varchar(1024) not null,
    action   varchar(1024) not null,
    role_id  int           not null,
    constraint splibraryrolepolicy_role_id_3e7ff158_fk_splibraryrole_id
        foreign key (role_id) references casiz.splibraryrole (id)
)
    charset = utf8mb3;

create table casiz.sppermission
(
    SpPermissionID  int auto_increment
        primary key,
    Actions         varchar(256) null,
    Name            varchar(64)  null,
    PermissionClass varchar(256) not null,
    TargetId        int          null
)
    charset = utf8mb3;

create table casiz.spprincipal
(
    SpPrincipalID     int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    GroupSubClass     varchar(255) not null,
    groupType         varchar(32)  null,
    Name              varchar(64)  not null,
    Priority          tinyint      not null,
    Remarks           text         null,
    ModifiedByAgentID int          null,
    CreatedByAgentID  int          null,
    userGroupScopeID  int          null,
    constraint FK56DC3A715327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK56DC3A717699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.recordset
(
    RecordSetID          int auto_increment
        primary key,
    TimestampCreated     datetime     not null,
    TimestampModified    datetime     null,
    Version              int          null,
    CollectionMemberID   int          not null,
    AllPermissionLevel   int          null,
    TableID              int          not null,
    GroupPermissionLevel int          null,
    Name                 varchar(280) not null,
    OwnerPermissionLevel int          null,
    Remarks              text         null,
    Type                 tinyint      not null,
    SpPrincipalID        int          null,
    CreatedByAgentID     int          null,
    ModifiedByAgentID    int          null,
    SpecifyUserID        int          not null,
    InfoRequestID        int          null,
    constraint FK3B38A27110D22B7A
        foreign key (InfoRequestID) references casiz.inforequest (InfoRequestID),
    constraint FK3B38A2714BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK3B38A2715327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3B38A2717699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK3B38A27199A7381A
        foreign key (SpPrincipalID) references casiz.spprincipal (SpPrincipalID)
)
    charset = utf8mb3;

create index RecordSetNameIDX
    on casiz.recordset (Name);

create table casiz.recordsetitem
(
    RecordSetItemID int auto_increment
        primary key,
    RecordId        int not null,
    RecordSetID     int not null,
    OrderNumber     int null,
    constraint FKD0817D047F06EB5A
        foreign key (RecordSetID) references casiz.recordset (RecordSetID)
)
    charset = utf8mb3;

create table casiz.specifyuser_spprincipal
(
    SpecifyUserID int not null,
    SpPrincipalID int not null,
    primary key (SpecifyUserID, SpPrincipalID),
    constraint FK81E18B5E4BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK81E18B5E99A7381A
        foreign key (SpPrincipalID) references casiz.spprincipal (SpPrincipalID)
)
    charset = utf8mb3;

create table casiz.spprincipal_sppermission
(
    SpPermissionID int not null,
    SpPrincipalID  int not null,
    primary key (SpPermissionID, SpPrincipalID),
    constraint FK9DD8B2FA891F8736
        foreign key (SpPermissionID) references casiz.sppermission (SpPermissionID),
    constraint FK9DD8B2FA99A7381A
        foreign key (SpPrincipalID) references casiz.spprincipal (SpPrincipalID)
)
    charset = utf8mb3;

create table casiz.spquery
(
    SpQueryID         int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    ContextName       varchar(64)  not null,
    ContextTableId    smallint     not null,
    CountOnly         bit          null,
    IsFavorite        bit          null,
    Name              varchar(256) not null,
    Ordinal           smallint     null,
    Remarks           text         null,
    SearchSynonymy    bit          null,
    SelectDistinct    bit          null,
    SqlStr            text         null,
    CreatedByAgentID  int          null,
    SpecifyUserID     int          not null,
    ModifiedByAgentID int          null,
    Smushed           bit          null,
    FormatAuditRecIds bit          null,
    constraint FK88FA7C8B4BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK88FA7C8B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK88FA7C8B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SpQueryNameIDX
    on casiz.spquery (Name);

create table casiz.spqueryfield
(
    SpQueryFieldID    int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    AllowNulls        bit          null,
    AlwaysFilter      bit          null,
    ColumnAlias       varchar(64)  null,
    ContextTableIdent int          null,
    EndValue          mediumtext   null,
    FieldName         varchar(32)  not null,
    FormatName        varchar(64)  null,
    IsDisplay         bit          not null,
    IsNot             bit          not null,
    IsPrompt          bit          null,
    IsRelFld          bit          null,
    OperEnd           tinyint      null,
    OperStart         tinyint      not null,
    Position          smallint     not null,
    SortType          tinyint      not null,
    StartValue        mediumtext   null,
    StringId          varchar(500) not null,
    TableList         varchar(500) not null,
    CreatedByAgentID  int          null,
    ModifiedByAgentID int          null,
    SpQueryID         int          null,
    constraint FK8F33434F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8F33434F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK8F33434FB273544E
        foreign key (SpQueryID) references casiz.spquery (SpQueryID)
)
    charset = utf8mb3;

create table casiz.spstynthy
(
    SpStynthyID       int auto_increment
        primary key,
    TimestampCreated  datetime       not null,
    TimestampModified datetime       null,
    MetaXML           mediumblob     null,
    UpdatePeriodDays  int default 30 not null,
    LastExported      datetime       null,
    CollectionID      int            not null,
    MappingXML        mediumblob     null,
    Key1              varchar(256)   null,
    Key2              varchar(256)   null
)
    charset = utf8mb3;

create table casiz.spsymbiotainstance
(
    SpSymbiotaInstanceID int auto_increment
        primary key,
    TimestampCreated     datetime     not null,
    TimestampModified    datetime     null,
    Version              int          null,
    CollectionMemberID   int          not null,
    Description          varchar(256) null,
    InstanceName         varchar(256) null,
    LastCacheBuild       datetime     null,
    LastPull             datetime     null,
    LastPush             datetime     null,
    Remarks              text         null,
    SymbiotaKey          varchar(128) null,
    CreatedByAgentID     int          null,
    SchemaMappingID      int          null,
    ModifiedByAgentID    int          null,
    constraint FK95FF2A005327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK95FF2A007699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK95FF2A00E5409F21
        foreign key (SchemaMappingID) references casiz.spexportschemamapping (SpExportSchemaMappingID)
)
    charset = utf8mb3;

create table casiz.spuserexternalid
(
    id             int auto_increment
        primary key,
    provider       varchar(256)                 not null,
    providerid     varchar(4095)                not null,
    specifyuser_id int                          not null,
    enabled        tinyint(1)                   not null,
    idtoken        longtext collate utf8mb4_bin null,
    constraint spuserexternalid_specifyuser_id_5cb2dacb_fk_specifyus
        foreign key (specifyuser_id) references casiz.specifyuser (SpecifyUserID)
)
    charset = utf8mb3;

create table casiz.spversion
(
    SpVersionID            int auto_increment
        primary key,
    TimestampCreated       datetime    not null,
    TimestampModified      datetime    null,
    Version                int         null,
    AppName                varchar(32) null,
    AppVersion             varchar(16) null,
    DbClosedBy             varchar(32) null,
    IsDBClosed             bit         null,
    SchemaVersion          varchar(16) null,
    WorkbenchSchemaVersion varchar(16) null,
    CreatedByAgentID       int         null,
    ModifiedByAgentID      int         null,
    constraint FK22369BDB5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK22369BDB7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.spvisualquery
(
    SpVisualQueryID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Description       text        null,
    Name              varchar(64) not null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    SpecifyUserID     int         not null,
    constraint FK34BC5F0B4BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK34BC5F0B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK34BC5F0B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SpVisualQueryNameIDX
    on casiz.spvisualquery (Name);

create table casiz.storagetreedef
(
    StorageTreeDefID  int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    FullNameDirection int         null,
    Name              varchar(64) not null,
    Remarks           text        null,
    ModifiedByAgentID int         null,
    CreatedByAgentID  int         null,
    constraint FK21AC10CC5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK21AC10CC7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.institution
(
    UserGroupScopeId            int          not null
        primary key,
    TimestampCreated            datetime     not null,
    TimestampModified           datetime     null,
    Version                     int          null,
    ModifiedByAgentID           int          null,
    CreatedByAgentID            int          null,
    AltName                     varchar(128) null,
    Code                        varchar(64)  null,
    Copyright                   text         null,
    CurrentManagedRelVersion    varchar(8)   null,
    CurrentManagedSchemaVersion varchar(8)   null,
    Description                 text         null,
    Disclaimer                  text         null,
    GUID                        varchar(128) null,
    HasBeenAsked                bit          null,
    IconURI                     varchar(255) null,
    institutionId               int          null,
    Ipr                         text         null,
    IsAccessionsGlobal          bit          not null,
    IsAnonymous                 bit          null,
    IsReleaseManagedGlobally    bit          null,
    IsSecurityOn                bit          not null,
    IsServerBased               bit          not null,
    IsSharingLocalities         bit          not null,
    IsSingleGeographyTree       bit          not null,
    License                     text         null,
    LsidAuthority               varchar(64)  null,
    MinimumPwdLength            tinyint      null,
    Name                        varchar(255) null,
    RegNumber                   varchar(24)  null,
    Remarks                     text         null,
    TermsOfUse                  text         null,
    Uri                         varchar(255) null,
    AddressID                   int          null,
    StorageTreeDefID            int          null,
    constraint FK3529A5B853C7EFD6
        foreign key (StorageTreeDefID) references casiz.storagetreedef (StorageTreeDefID),
    constraint FK3529A5B8E6A64D00
        foreign key (AddressID) references casiz.address (AddressID),
    constraint FK3D0021605327F9423529a5b8
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3D0021607699B0033529a5b8
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

alter table casiz.agent
    add constraint FK587430587E99F68
        foreign key (InstitutionCCID) references casiz.institution (UserGroupScopeId);

create table casiz.division
(
    UserGroupScopeId  int          not null
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    ModifiedByAgentID int          null,
    CreatedByAgentID  int          null,
    Abbrev            varchar(64)  null,
    AltName           varchar(128) null,
    Description       text         null,
    DisciplineType    varchar(64)  null,
    divisionId        int          null,
    IconURI           varchar(255) null,
    Name              varchar(255) null,
    RegNumber         varchar(24)  null,
    Remarks           text         null,
    Uri               varchar(255) null,
    InstitutionID     int          not null,
    AddressID         int          null,
    constraint FK15BD30AD81223908
        foreign key (InstitutionID) references casiz.institution (UserGroupScopeId),
    constraint FK15BD30ADE6A64D00
        foreign key (AddressID) references casiz.address (AddressID),
    constraint FK3D0021605327F94215bd30ad
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3D0021607699B00315bd30ad
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

alter table casiz.agent
    add constraint FK587430597C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId);

create table casiz.autonumsch_div
(
    DivisionID            int not null,
    AutoNumberingSchemeID int not null,
    primary key (DivisionID, AutoNumberingSchemeID),
    constraint FKA8BE49397C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FKA8BE493FE55DD76
        foreign key (AutoNumberingSchemeID) references casiz.autonumberingscheme (AutoNumberingSchemeID)
)
    charset = utf8mb3;

create index DivisionNameIDX
    on casiz.division (Name);

create table casiz.exchangein
(
    ExchangeInID               int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    DescriptionOfMaterial      varchar(120)    null,
    ExchangeDate               date            null,
    Number1                    decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    QuantityExchanged          smallint        null,
    Remarks                    text            null,
    SrcGeography               varchar(32)     null,
    SrcTaxonomy                varchar(32)     null,
    Text1                      text            null,
    Text2                      text            null,
    YesNo1                     bit             null,
    YesNo2                     bit             null,
    CreatedByAgentID           int             null,
    DivisionID                 int             not null,
    CatalogedByID              int             not null,
    ReceivedFromOrganizationID int             not null,
    ModifiedByAgentID          int             null,
    AddressOfRecordID          int             null,
    Contents                   text            null,
    ExchangeInNumber           varchar(50)     null,
    constraint FK366E9E883824C16C
        foreign key (CatalogedByID) references casiz.agent (AgentID),
    constraint FK366E9E885327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK366E9E887699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK366E9E8897C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK366E9E88DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID),
    constraint FK366E9E88F77B069B
        foreign key (ReceivedFromOrganizationID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index DescriptionOfMaterialIDX
    on casiz.exchangein (DescriptionOfMaterial);

create index ExchangeDateIDX
    on casiz.exchangein (ExchangeDate);

create table casiz.exchangeinattachment
(
    ExchangeInAttachmentID int auto_increment
        primary key,
    TimestampCreated       datetime not null,
    TimestampModified      datetime null,
    Version                int      null,
    Ordinal                int      not null,
    Remarks                text     null,
    CreatedByAgentID       int      null,
    ModifiedByAgentID      int      null,
    ExchangeInID           int      not null,
    AttachmentID           int      not null,
    constraint FK4FB76DAB1E18122E
        foreign key (ExchangeInID) references casiz.exchangein (ExchangeInID),
    constraint FK4FB76DAB5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK4FB76DAB7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK4FB76DABC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.exchangeout
(
    ExchangeOutID         int auto_increment
        primary key,
    TimestampCreated      datetime        not null,
    TimestampModified     datetime        null,
    Version               int             null,
    DescriptionOfMaterial varchar(120)    null,
    ExchangeDate          date            null,
    Number1               decimal(20, 10) null,
    Number2               decimal(20, 10) null,
    QuantityExchanged     smallint        null,
    Remarks               text            null,
    SrcGeography          varchar(32)     null,
    SrcTaxonomy           varchar(32)     null,
    Text1                 text            null,
    Text2                 text            null,
    YesNo1                bit             null,
    YesNo2                bit             null,
    CatalogedByID         int             not null,
    SentToOrganizationID  int             not null,
    ModifiedByAgentID     int             null,
    AddressOfRecordID     int             null,
    DivisionID            int             not null,
    CreatedByAgentID      int             null,
    Contents              text            null,
    ExchangeOutNumber     varchar(50)     not null,
    DeaccessionID         int             null,
    constraint FK97654A4B3824C16C
        foreign key (CatalogedByID) references casiz.agent (AgentID),
    constraint FK97654A4B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK97654A4B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK97654A4B97C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK97654A4BA21647A3
        foreign key (SentToOrganizationID) references casiz.agent (AgentID),
    constraint FK97654A4BBE26B05E
        foreign key (DeaccessionID) references casiz.deaccession (DeaccessionID),
    constraint FK97654A4BDC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create index DescriptionOfMaterialIDX2
    on casiz.exchangeout (DescriptionOfMaterial);

create index ExchangeOutNumberIDX
    on casiz.exchangeout (ExchangeOutNumber);

create index ExchangeOutdateIDX
    on casiz.exchangeout (ExchangeDate);

create table casiz.exchangeoutattachment
(
    ExchangeOutAttachmentID int auto_increment
        primary key,
    TimestampCreated        datetime not null,
    TimestampModified       datetime null,
    Version                 int      null,
    Ordinal                 int      not null,
    Remarks                 text     null,
    ExchangeOutID           int      not null,
    CreatedByAgentID        int      null,
    ModifiedByAgentID       int      null,
    AttachmentID            int      not null,
    constraint FKA2C881AE5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA2C881AE7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA2C881AEA542314E
        foreign key (ExchangeOutID) references casiz.exchangeout (ExchangeOutID),
    constraint FKA2C881AEC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.groupperson
(
    GroupPersonID     int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    OrderNumber       smallint not null,
    Remarks           text     null,
    MemberID          int      not null,
    CreatedByAgentID  int      null,
    GroupID           int      not null,
    ModifiedByAgentID int      null,
    DivisionID        int      not null,
    constraint OrderNumber
        unique (OrderNumber, GroupID),
    constraint FK5DEB769450D2EC77
        foreign key (MemberID) references casiz.agent (AgentID),
    constraint FK5DEB76945327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK5DEB76947699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK5DEB76948905F31C
        foreign key (GroupID) references casiz.agent (AgentID),
    constraint FK5DEB769497C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId)
)
    charset = utf8mb3;

create index InstGuidIDX
    on casiz.institution (GUID);

create index InstNameIDX
    on casiz.institution (Name);

create table casiz.journal
(
    JournalID           int auto_increment
        primary key,
    TimestampCreated    datetime     not null,
    TimestampModified   datetime     null,
    Version             int          null,
    GUID                varchar(128) null,
    ISSN                varchar(16)  null,
    JournalAbbreviation varchar(50)  null,
    JournalName         varchar(255) null,
    Remarks             text         null,
    Text1               varchar(32)  null,
    ModifiedByAgentID   int          null,
    InstitutionID       int          not null,
    CreatedByAgentID    int          null,
    constraint FKAB64AF375327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKAB64AF377699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKAB64AF3781223908
        foreign key (InstitutionID) references casiz.institution (UserGroupScopeId)
)
    charset = utf8mb3;

create index JournalGUIDIDX
    on casiz.journal (GUID);

create index JournalNameIDX
    on casiz.journal (JournalName);

create table casiz.permit
(
    PermitID          int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    EndDate           date            null,
    IssuedDate        date            null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    PermitNumber      varchar(50)     not null,
    Remarks           text            null,
    RenewalDate       date            null,
    StartDate         date            null,
    Text1             text            null,
    Text2             text            null,
    Type              varchar(50)     null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    InstitutionID     int             not null,
    IssuedToID        int             null,
    ModifiedByAgentID int             null,
    IssuedByID        int             null,
    CreatedByAgentID  int             null,
    Copyright         varchar(256)    null,
    IsAvailable       bit             null,
    IsRequired        bit             null,
    PermitText        text            null,
    ReservedInteger1  int             null,
    ReservedInteger2  int             null,
    ReservedText3     varchar(128)    null,
    ReservedText4     varchar(128)    null,
    Status            varchar(64)     null,
    StatusQualifier   varchar(128)    null,
    constraint FKC4E3841B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC4E3841B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC4E3841B81223908
        foreign key (InstitutionID) references casiz.institution (UserGroupScopeId),
    constraint FKC4E3841BCDCF181F
        foreign key (IssuedByID) references casiz.agent (AgentID),
    constraint FKC4E3841BCDD72143
        foreign key (IssuedToID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index IssuedDateIDX
    on casiz.permit (IssuedDate);

create index PermitNumberIDX
    on casiz.permit (PermitNumber);

create table casiz.permitattachment
(
    PermitAttachmentID int auto_increment
        primary key,
    TimestampCreated   datetime not null,
    TimestampModified  datetime null,
    Version            int      null,
    Ordinal            int      not null,
    Remarks            text     null,
    PermitID           int      not null,
    CreatedByAgentID   int      null,
    ModifiedByAgentID  int      null,
    AttachmentID       int      not null,
    constraint FK7064B77E5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK7064B77E7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK7064B77EAD1F31F4
        foreign key (PermitID) references casiz.permit (PermitID),
    constraint FK7064B77EC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.referencework
(
    ReferenceWorkID     int auto_increment
        primary key,
    TimestampCreated    datetime        not null,
    TimestampModified   datetime        null,
    Version             int             null,
    GUID                varchar(128)    null,
    IsPublished         bit             null,
    ISBN                varchar(16)     null,
    LibraryNumber       varchar(50)     null,
    Number1             decimal(20, 10) null,
    Number2             decimal(20, 10) null,
    Pages               varchar(50)     null,
    PlaceOfPublication  varchar(50)     null,
    Publisher           varchar(250)    null,
    ReferenceWorkType   tinyint         not null,
    Remarks             text            null,
    Text1               text            null,
    Text2               text            null,
    Title               varchar(400)    null,
    URL                 varchar(1024)   null,
    Volume              varchar(25)     null,
    WorkDate            varchar(25)     null,
    YesNo1              bit             null,
    YesNo2              bit             null,
    JournalID           int             null,
    ContainedRFParentID int             null,
    CreatedByAgentID    int             null,
    InstitutionID       int             not null,
    ModifiedByAgentID   int             null,
    Doi                 text            null,
    Uri                 text            null,
    constraint FK5F7C68DC1B806665
        foreign key (ContainedRFParentID) references casiz.referencework (ReferenceWorkID),
    constraint FK5F7C68DC5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK5F7C68DC748AEC6
        foreign key (JournalID) references casiz.journal (JournalID),
    constraint FK5F7C68DC7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK5F7C68DC81223908
        foreign key (InstitutionID) references casiz.institution (UserGroupScopeId)
)
    charset = utf8mb3;

create table casiz.author
(
    AuthorID          int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    OrderNumber       smallint not null,
    Remarks           text     null,
    AgentID           int      not null,
    ModifiedByAgentID int      null,
    CreatedByAgentID  int      null,
    ReferenceWorkID   int      not null,
    constraint AgentIDX
        unique (ReferenceWorkID, AgentID),
    constraint FKAC2D218B384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKAC2D218B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKAC2D218B69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FKAC2D218B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.exsiccata
(
    ExsiccataID       int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Title             varchar(255) not null,
    ModifiedByAgentID int          null,
    ReferenceWorkID   int          not null,
    CreatedByAgentID  int          null,
    Remarks           text         null,
    Schedae           varchar(255) null,
    constraint FKACC7DD855327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKACC7DD8569734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FKACC7DD857699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index ISBNIDX
    on casiz.referencework (ISBN);

create index RefWrkGuidIDX
    on casiz.referencework (GUID);

create index RefWrkPublisherIDX
    on casiz.referencework (Publisher);

create index RefWrkTitleIDX
    on casiz.referencework (Title);

create table casiz.referenceworkattachment
(
    ReferenceWorkAttachmentID int auto_increment
        primary key,
    TimestampCreated          datetime not null,
    TimestampModified         datetime null,
    Version                   int      null,
    Ordinal                   int      not null,
    Remarks                   text     null,
    ReferenceWorkID           int      not null,
    CreatedByAgentID          int      null,
    ModifiedByAgentID         int      null,
    AttachmentID              int      not null,
    constraint FK9C9B5EFF5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9C9B5EFF69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK9C9B5EFF7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9C9B5EFFC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.repositoryagreement
(
    RepositoryAgreementID     int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    DateReceived              date            null,
    EndDate                   date            null,
    Number1                   decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    Remarks                   text            null,
    RepositoryAgreementNumber varchar(60)     not null,
    StartDate                 date            null,
    Status                    varchar(32)     null,
    Text1                     varchar(255)    null,
    Text2                     varchar(255)    null,
    Text3                     varchar(255)    null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    AgentID                   int             not null,
    CreatedByAgentID          int             null,
    DivisionID                int             not null,
    AddressOfRecordID         int             null,
    ModifiedByAgentID         int             null,
    constraint FKA5A38A00384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKA5A38A005327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA5A38A007699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA5A38A0097C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FKA5A38A00DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create table casiz.accession
(
    AccessionID           int auto_increment
        primary key,
    TimestampCreated      datetime        not null,
    TimestampModified     datetime        null,
    Version               int             null,
    AccessionCondition    varchar(255)    null,
    AccessionNumber       varchar(60)     not null,
    DateAccessioned       date            null,
    DateAcknowledged      date            null,
    DateReceived          date            null,
    Number1               decimal(20, 10) null,
    Number2               decimal(20, 10) null,
    Remarks               text            null,
    Status                varchar(32)     null,
    Text1                 text            null,
    Text2                 text            null,
    Text3                 text            null,
    TotalValue            decimal(12, 2)  null,
    Type                  varchar(32)     null,
    VerbatimDate          varchar(50)     null,
    YesNo1                bit             null,
    YesNo2                bit             null,
    AddressOfRecordID     int             null,
    DivisionID            int             not null,
    RepositoryAgreementID int             null,
    CreatedByAgentID      int             null,
    ModifiedByAgentID     int             null,
    Integer1              int             null,
    Integer2              int             null,
    Integer3              int             null,
    Text4                 text            null,
    Text5                 text            null,
    constraint FK81EF38243EBC6278
        foreign key (RepositoryAgreementID) references casiz.repositoryagreement (RepositoryAgreementID),
    constraint FK81EF38245327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK81EF38247699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK81EF382497C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK81EF3824DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create index AccessionDateIDX
    on casiz.accession (DateAccessioned);

create index AccessionNumberIDX
    on casiz.accession (AccessionNumber);

create table casiz.accessionagent
(
    AccessionAgentID      int auto_increment
        primary key,
    TimestampCreated      datetime    not null,
    TimestampModified     datetime    null,
    Version               int         null,
    Remarks               text        null,
    Role                  varchar(50) not null,
    RepositoryAgreementID int         null,
    AccessionID           int         null,
    ModifiedByAgentID     int         null,
    CreatedByAgentID      int         null,
    AgentID               int         not null,
    constraint Role
        unique (Role, AgentID, AccessionID),
    constraint FK2DC98161384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK2DC981613925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FK2DC981613EBC6278
        foreign key (RepositoryAgreementID) references casiz.repositoryagreement (RepositoryAgreementID),
    constraint FK2DC981615327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK2DC981617699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.accessionattachment
(
    AccessionAttachmentID int auto_increment
        primary key,
    TimestampCreated      datetime not null,
    TimestampModified     datetime null,
    Version               int      null,
    Ordinal               int      not null,
    Remarks               text     null,
    ModifiedByAgentID     int      null,
    AttachmentID          int      not null,
    AccessionID           int      not null,
    CreatedByAgentID      int      null,
    constraint FKA569B4473925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FKA569B4475327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA569B4477699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKA569B447C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.accessionauthorization
(
    AccessionAuthorizationID int auto_increment
        primary key,
    TimestampCreated         datetime not null,
    TimestampModified        datetime null,
    Version                  int      null,
    Remarks                  text     null,
    CreatedByAgentID         int      null,
    RepositoryAgreementID    int      null,
    PermitID                 int      not null,
    ModifiedByAgentID        int      null,
    AccessionID              int      null,
    constraint FK4F2602D53925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FK4F2602D53EBC6278
        foreign key (RepositoryAgreementID) references casiz.repositoryagreement (RepositoryAgreementID),
    constraint FK4F2602D55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK4F2602D57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK4F2602D5AD1F31F4
        foreign key (PermitID) references casiz.permit (PermitID)
)
    charset = utf8mb3;

create table casiz.accessioncitation
(
    AccessionCitationID int auto_increment
        primary key,
    TimestampCreated    datetime    not null,
    TimestampModified   datetime    null,
    Version             int         null,
    FigureNumber        varchar(50) null,
    IsFigured           bit         null,
    PageNumber          varchar(50) null,
    PlateNumber         varchar(50) null,
    Remarks             text        null,
    ModifiedByAgentID   int         null,
    ReferenceWorkID     int         not null,
    CreatedByAgentID    int         null,
    AccessionID         int         not null,
    constraint FK9ED8DF0B3925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FK9ED8DF0B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9ED8DF0B69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK9ED8DF0B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.appraisal
(
    AppraisalID       int auto_increment
        primary key,
    TimestampCreated  datetime       not null,
    TimestampModified datetime       null,
    Version           int            null,
    AppraisalDate     date           not null,
    AppraisalNumber   varchar(64)    not null,
    AppraisalValue    decimal(12, 2) null,
    MonetaryUnitType  varchar(8)     null,
    Notes             text           null,
    AccessionID       int            null,
    AgentID           int            not null,
    ModifiedByAgentID int            null,
    CreatedByAgentID  int            null,
    constraint AppraisalNumber
        unique (AppraisalNumber),
    constraint FK8D3C72E5384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK8D3C72E53925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FK8D3C72E55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8D3C72E57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index AppraisalDateIDX
    on casiz.appraisal (AppraisalDate);

create index AppraisalNumberIDX
    on casiz.appraisal (AppraisalNumber);

create index RefWrkNumberIDX
    on casiz.repositoryagreement (RepositoryAgreementNumber);

create index RefWrkStartDate
    on casiz.repositoryagreement (StartDate);

create table casiz.repositoryagreementattachment
(
    RepositoryAgreementAttachmentID int auto_increment
        primary key,
    TimestampCreated                datetime not null,
    TimestampModified               datetime null,
    Version                         int      null,
    Ordinal                         int      not null,
    Remarks                         text     null,
    AttachmentID                    int      not null,
    CreatedByAgentID                int      null,
    RepositoryAgreementID           int      not null,
    ModifiedByAgentID               int      null,
    constraint FK93663233EBC6278
        foreign key (RepositoryAgreementID) references casiz.repositoryagreement (RepositoryAgreementID),
    constraint FK93663235327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK93663237699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9366323C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.storagetreedefitem
(
    StorageTreeDefItemID int auto_increment
        primary key,
    TimestampCreated     datetime    not null,
    TimestampModified    datetime    null,
    Version              int         null,
    FullNameSeparator    varchar(32) null,
    IsEnforced           bit         null,
    IsInFullName         bit         null,
    Name                 varchar(64) not null,
    RankID               int         not null,
    Remarks              text        null,
    TextAfter            varchar(64) null,
    TextBefore           varchar(64) null,
    Title                varchar(64) null,
    CreatedByAgentID     int         null,
    ParentItemID         int         null,
    StorageTreeDefID     int         not null,
    ModifiedByAgentID    int         null,
    constraint FK589045DF3C85253A
        foreign key (ParentItemID) references casiz.storagetreedefitem (StorageTreeDefItemID),
    constraint FK589045DF5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK589045DF53C7EFD6
        foreign key (StorageTreeDefID) references casiz.storagetreedef (StorageTreeDefID),
    constraint FK589045DF7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.storage
(
    StorageID              int auto_increment
        primary key,
    TimestampCreated       datetime     not null,
    TimestampModified      datetime     null,
    Version                int          null,
    Abbrev                 varchar(16)  null,
    FullName               varchar(255) null,
    HighestChildNodeNumber int          null,
    IsAccepted             bit          null,
    Name                   varchar(64)  not null,
    NodeNumber             int          null,
    Number1                int          null,
    Number2                int          null,
    RankID                 int          not null,
    Remarks                text         null,
    Text1                  varchar(32)  null,
    Text2                  varchar(32)  null,
    TimestampVersion       datetime     null,
    ParentID               int          null,
    AcceptedID             int          null,
    StorageTreeDefItemID   int          not null,
    StorageTreeDefID       int          not null,
    ModifiedByAgentID      int          null,
    CreatedByAgentID       int          null,
    constraint FK8FB0427B3D83D67A
        foreign key (AcceptedID) references casiz.storage (StorageID),
    constraint FK8FB0427B4D340BDC
        foreign key (StorageTreeDefItemID) references casiz.storagetreedefitem (StorageTreeDefItemID),
    constraint FK8FB0427B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK8FB0427B53C7EFD6
        foreign key (StorageTreeDefID) references casiz.storagetreedef (StorageTreeDefID),
    constraint FK8FB0427B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK8FB0427BCCAA0ABD
        foreign key (ParentID) references casiz.storage (StorageID)
)
    charset = utf8mb3;

create table casiz.container
(
    ContainerID        int auto_increment
        primary key,
    TimestampCreated   datetime      not null,
    TimestampModified  datetime      null,
    Version            int           null,
    CollectionMemberID int           not null,
    Description        mediumtext    null,
    Name               varchar(1024) null,
    Number             int           null,
    Type               smallint      null,
    CreatedByAgentID   int           null,
    ParentID           int           null,
    StorageID          int           null,
    ModifiedByAgentID  int           null,
    constraint FKE7814C8121C1C983
        foreign key (ParentID) references casiz.container (ContainerID),
    constraint FKE7814C815327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE7814C817699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKE7814C81EB48144E
        foreign key (StorageID) references casiz.storage (StorageID)
)
    charset = utf8mb3;

create index ContainerMemIDX
    on casiz.container (CollectionMemberID);

create index ContainerNameIDX
    on casiz.container (Name);

create index StorFullNameIDX
    on casiz.storage (FullName);

create index StorNameIDX
    on casiz.storage (Name);

create table casiz.storageattachment
(
    StorageAttachmentID int auto_increment
        primary key,
    TimestampCreated    datetime not null,
    TimestampModified   datetime null,
    Version             int      null,
    Ordinal             int      not null,
    Remarks             text     null,
    ModifiedByAgentID   int      null,
    CreatedByAgentID    int      null,
    StorageID           int      not null,
    AttachmentID        int      not null,
    constraint FKBE9EFDDE5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBE9EFDDE7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKBE9EFDDEC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID),
    constraint FKBE9EFDDEEB48144E
        foreign key (StorageID) references casiz.storage (StorageID)
)
    charset = utf8mb3;

create table casiz.taxonattribute
(
    TaxonAttributeID  int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    Date1             date            null,
    Date1Precision    tinyint         null,
    Number1           decimal(20, 10) null,
    Number10          decimal(20, 10) null,
    Number11          decimal(20, 10) null,
    Number12          decimal(20, 10) null,
    Number13          decimal(20, 10) null,
    Number14          decimal(20, 10) null,
    Number15          decimal(20, 10) null,
    Number16          decimal(20, 10) null,
    Number17          decimal(20, 10) null,
    Number18          decimal(20, 10) null,
    Number19          decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    Number20          decimal(20, 10) null,
    Number3           decimal(20, 10) null,
    Number4           decimal(20, 10) null,
    Number5           decimal(20, 10) null,
    Number6           decimal(20, 10) null,
    Number7           decimal(20, 10) null,
    Number8           decimal(20, 10) null,
    Number9           decimal(20, 10) null,
    Remarks           text            null,
    Text1             varchar(128)    null,
    Text10            varchar(128)    null,
    Text11            varchar(128)    null,
    Text12            varchar(128)    null,
    Text13            varchar(128)    null,
    Text14            varchar(128)    null,
    Text15            varchar(128)    null,
    Text16            varchar(128)    null,
    Text17            varchar(128)    null,
    Text18            varchar(128)    null,
    Text19            varchar(128)    null,
    Text2             varchar(128)    null,
    Text20            varchar(128)    null,
    Text21            varchar(128)    null,
    Text22            varchar(128)    null,
    Text23            varchar(128)    null,
    Text24            varchar(128)    null,
    Text25            varchar(128)    null,
    Text26            varchar(128)    null,
    Text27            varchar(256)    null,
    Text28            varchar(256)    null,
    Text29            varchar(256)    null,
    Text3             varchar(128)    null,
    Text30            varchar(256)    null,
    Text31            varchar(256)    null,
    Text32            varchar(256)    null,
    Text33            varchar(256)    null,
    Text34            varchar(256)    null,
    Text35            varchar(256)    null,
    Text36            varchar(256)    null,
    Text37            varchar(256)    null,
    Text38            varchar(256)    null,
    Text39            varchar(256)    null,
    Text4             varchar(128)    null,
    Text40            varchar(256)    null,
    Text41            varchar(256)    null,
    Text42            varchar(256)    null,
    Text43            varchar(256)    null,
    Text44            varchar(256)    null,
    Text45            varchar(256)    null,
    Text46            varchar(256)    null,
    Text47            varchar(256)    null,
    Text48            varchar(256)    null,
    Text49            text            null,
    Text5             varchar(128)    null,
    Text50            text            null,
    Text51            text            null,
    Text52            text            null,
    Text53            text            null,
    Text54            text            null,
    Text55            text            null,
    Text56            text            null,
    Text57            text            null,
    Text58            text            null,
    Text6             varchar(128)    null,
    Text7             varchar(128)    null,
    Text8             varchar(128)    null,
    Text9             varchar(128)    null,
    YesNo1            bit             null,
    YesNo10           bit             null,
    YesNo11           bit             null,
    YesNo12           bit             null,
    YesNo13           bit             null,
    YesNo14           bit             null,
    YesNo15           bit             null,
    YesNo16           bit             null,
    YesNo17           bit             null,
    YesNo18           bit             null,
    YesNo19           bit             null,
    YesNo2            bit             null,
    YesNo20           bit             null,
    YesNo21           bit             null,
    YesNo22           bit             null,
    YesNo23           bit             null,
    YesNo24           bit             null,
    YesNo25           bit             null,
    YesNo26           bit             null,
    YesNo27           bit             null,
    YesNo28           bit             null,
    YesNo29           bit             null,
    YesNo3            bit             null,
    YesNo30           bit             null,
    YesNo31           bit             null,
    YesNo32           bit             null,
    YesNo33           bit             null,
    YesNo34           bit             null,
    YesNo35           bit             null,
    YesNo36           bit             null,
    YesNo37           bit             null,
    YesNo38           bit             null,
    YesNo39           bit             null,
    YesNo4            bit             null,
    YesNo40           bit             null,
    YesNo41           bit             null,
    YesNo42           bit             null,
    YesNo43           bit             null,
    YesNo44           bit             null,
    YesNo45           bit             null,
    YesNo46           bit             null,
    YesNo47           bit             null,
    YesNo48           bit             null,
    YesNo49           bit             null,
    YesNo5            bit             null,
    YesNo50           bit             null,
    YesNo51           bit             null,
    YesNo52           bit             null,
    YesNo53           bit             null,
    YesNo54           bit             null,
    YesNo55           bit             null,
    YesNo56           bit             null,
    YesNo57           bit             null,
    YesNo58           bit             null,
    YesNo59           bit             null,
    YesNo6            bit             null,
    YesNo60           bit             null,
    YesNo61           bit             null,
    YesNo62           bit             null,
    YesNo63           bit             null,
    YesNo64           bit             null,
    YesNo65           bit             null,
    YesNo66           bit             null,
    YesNo67           bit             null,
    YesNo68           bit             null,
    YesNo69           bit             null,
    YesNo7            bit             null,
    YesNo70           bit             null,
    YesNo71           bit             null,
    YesNo72           bit             null,
    YesNo73           bit             null,
    YesNo74           bit             null,
    YesNo75           bit             null,
    YesNo76           bit             null,
    YesNo77           bit             null,
    YesNo78           bit             null,
    YesNo79           bit             null,
    YesNo8            bit             null,
    YesNo80           bit             null,
    YesNo81           bit             null,
    YesNo82           bit             null,
    YesNo9            bit             null,
    Agent1ID          int             null,
    CreatedByAgentID  int             null,
    ModifiedByAgentID int             null,
    constraint FKDAEA1F125327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDAEA1F127699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKDAEA1F12CF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.taxontreedef
(
    TaxonTreeDefID    int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    FullNameDirection int          null,
    Name              varchar(64)  not null,
    Remarks           varchar(255) null,
    CreatedByAgentID  int          null,
    ModifiedByAgentID int          null,
    constraint FK169B1D9D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK169B1D9D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.discipline
(
    UserGroupScopeId            int         not null
        primary key,
    TimestampCreated            datetime    not null,
    TimestampModified           datetime    null,
    Version                     int         null,
    ModifiedByAgentID           int         null,
    CreatedByAgentID            int         null,
    disciplineId                int         null,
    Name                        varchar(64) null,
    RegNumber                   varchar(24) null,
    Type                        varchar(64) null,
    DataTypeID                  int         not null,
    LithoStratTreeDefID         int         null,
    DivisionID                  int         not null,
    GeologicTimePeriodTreeDefID int         not null,
    TaxonTreeDefID              int         null,
    GeographyTreeDefID          int         not null,
    IsPaleoContextEmbedded      bit         null,
    PaleoContextChildTable      varchar(50) null,
    constraint FK157B9B7072939D3A
        foreign key (LithoStratTreeDefID) references casiz.lithostrattreedef (LithoStratTreeDefID),
    constraint FK157B9B7097C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK157B9B709988ED70
        foreign key (GeologicTimePeriodTreeDefID) references casiz.geologictimeperiodtreedef (GeologicTimePeriodTreeDefID),
    constraint FK157B9B70BF9C9714
        foreign key (GeographyTreeDefID) references casiz.geographytreedef (GeographyTreeDefID),
    constraint FK157B9B70D62E36A6
        foreign key (DataTypeID) references casiz.datatype (DataTypeID),
    constraint FK157B9B70EFA9D5F8
        foreign key (TaxonTreeDefID) references casiz.taxontreedef (TaxonTreeDefID),
    constraint FK3D0021605327F942157b9b70
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3D0021607699B003157b9b70
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.autonumsch_dsp
(
    DisciplineID          int not null,
    AutoNumberingSchemeID int not null,
    primary key (DisciplineID, AutoNumberingSchemeID),
    constraint FKA8BE5C34CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKA8BE5C3FE55DD76
        foreign key (AutoNumberingSchemeID) references casiz.autonumberingscheme (AutoNumberingSchemeID)
)
    charset = utf8mb3;

create table casiz.collectingtripattribute
(
    CollectingTripAttributeID int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    Integer1                  int             null,
    Integer10                 int             null,
    Integer2                  int             null,
    Integer3                  int             null,
    Integer4                  int             null,
    Integer5                  int             null,
    Integer6                  int             null,
    Integer7                  int             null,
    Integer8                  int             null,
    Integer9                  int             null,
    Number1                   decimal(20, 10) null,
    Number10                  decimal(20, 10) null,
    Number11                  decimal(20, 10) null,
    Number12                  decimal(20, 10) null,
    Number13                  decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    Number3                   decimal(20, 10) null,
    Number4                   decimal(20, 10) null,
    Number5                   decimal(20, 10) null,
    Number6                   decimal(20, 10) null,
    Number7                   decimal(20, 10) null,
    Number8                   decimal(20, 10) null,
    Number9                   decimal(20, 10) null,
    Remarks                   text            null,
    Text1                     text            null,
    Text10                    varchar(50)     null,
    Text11                    varchar(50)     null,
    Text12                    varchar(50)     null,
    Text13                    varchar(50)     null,
    Text14                    varchar(50)     null,
    Text15                    varchar(50)     null,
    Text16                    varchar(50)     null,
    Text17                    varchar(50)     null,
    Text2                     text            null,
    Text3                     text            null,
    Text4                     varchar(100)    null,
    Text5                     varchar(100)    null,
    Text6                     varchar(50)     null,
    Text7                     varchar(50)     null,
    Text8                     varchar(50)     null,
    Text9                     varchar(50)     null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    YesNo3                    bit             null,
    YesNo4                    bit             null,
    YesNo5                    bit             null,
    ModifiedByAgentID         int             null,
    DisciplineID              int             not null,
    CreatedByAgentID          int             null,
    constraint FK381CA49F4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK381CA49F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK381CA49F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.collectingtrip
(
    CollectingTripID          int auto_increment
        primary key,
    TimestampCreated          datetime     not null,
    TimestampModified         datetime     null,
    Version                   int          null,
    Collectingtripname        varchar(400) null,
    EndDate                   date         null,
    EndDatePrecision          tinyint      null,
    EndDateVerbatim           varchar(50)  null,
    EndTime                   smallint     null,
    Number1                   int          null,
    Number2                   int          null,
    Remarks                   text         null,
    Sponsor                   varchar(64)  null,
    StartDate                 date         null,
    StartDatePrecision        tinyint      null,
    StartDateVerbatim         varchar(50)  null,
    StartTime                 smallint     null,
    Text1                     varchar(255) null,
    Text2                     varchar(128) null,
    Text3                     varchar(64)  null,
    Text4                     varchar(64)  null,
    YesNo1                    bit          null,
    YesNo2                    bit          null,
    ModifiedByAgentID         int          null,
    CreatedByAgentID          int          null,
    DisciplineID              int          not null,
    Cruise                    varchar(250) null,
    Expedition                varchar(250) null,
    Vessel                    varchar(250) null,
    Date1                     date         null,
    Date1Precision            tinyint      null,
    Date2                     date         null,
    Date2Precision            tinyint      null,
    Text5                     text         null,
    Text6                     text         null,
    Text7                     text         null,
    Text8                     text         null,
    Text9                     text         null,
    Agent1ID                  int          null,
    CollectingTripAttributeID int          null,
    Agent2ID                  int          null,
    constraint FK1080269D169A9556
        foreign key (CollectingTripAttributeID) references casiz.collectingtripattribute (CollectingTripAttributeID),
    constraint FK1080269D4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK1080269D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK1080269D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK1080269DCF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FK1080269DCF197EEA
        foreign key (Agent2ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index COLTRPNameIDX
    on casiz.collectingtrip (Collectingtripname);

create index COLTRPStartDateIDX
    on casiz.collectingtrip (StartDate);

create table casiz.collectingtripattachment
(
    CollectingTripAttachmentID int auto_increment
        primary key,
    TimestampCreated           datetime not null,
    TimestampModified          datetime null,
    Version                    int      null,
    CollectionMemberID         int      not null,
    Ordinal                    int      not null,
    Remarks                    text     null,
    CollectingTripID           int      not null,
    ModifiedByAgentID          int      null,
    CreatedByAgentID           int      null,
    AttachmentID               int      not null,
    constraint FK3E419F805327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3E419F80697B3F98
        foreign key (CollectingTripID) references casiz.collectingtrip (CollectingTripID),
    constraint FK3E419F807699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK3E419F80C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.collectingtripauthorization
(
    CollectingTripAuthorizationID int auto_increment
        primary key,
    TimestampCreated              datetime not null,
    TimestampModified             datetime null,
    Version                       int      null,
    Remarks                       text     null,
    ModifiedByAgentID             int      null,
    CollectingTripID              int      null,
    CreatedByAgentID              int      null,
    PermitID                      int      not null,
    constraint FKDDDC20FC5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDDDC20FC697B3F98
        foreign key (CollectingTripID) references casiz.collectingtrip (CollectingTripID),
    constraint FKDDDC20FC7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKDDDC20FCAD1F31F4
        foreign key (PermitID) references casiz.permit (PermitID)
)
    charset = utf8mb3;

create table casiz.collection
(
    UserGroupScopeId          int          not null
        primary key,
    TimestampCreated          datetime     not null,
    TimestampModified         datetime     null,
    Version                   int          null,
    ModifiedByAgentID         int          null,
    CreatedByAgentID          int          null,
    CatalogFormatNumName      varchar(64)  not null,
    Code                      varchar(50)  null,
    collectionId              int          null,
    CollectionName            varchar(50)  null,
    CollectionType            varchar(32)  null,
    DbContentVersion          varchar(32)  null,
    Description               text         null,
    DevelopmentStatus         varchar(32)  null,
    EstimatedSize             int          null,
    GUID                      varchar(128) null,
    InstitutionType           varchar(32)  null,
    IsEmbeddedCollectingEvent bit          not null,
    IsaNumber                 varchar(24)  null,
    KingdomCoverage           varchar(32)  null,
    PreservationMethodType    varchar(32)  null,
    PrimaryFocus              varchar(32)  null,
    PrimaryPurpose            varchar(32)  null,
    RegNumber                 varchar(24)  null,
    Remarks                   text         null,
    Scope                     text         null,
    WebPortalURI              varchar(255) null,
    WebSiteURI                varchar(255) null,
    DisciplineID              int          not null,
    InstitutionNetworkID      int          null,
    AdminContactID            int          null,
    constraint FK3D0021605327F9429835ae9e
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3D0021607699B0039835ae9e
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9835AE9E4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK9835AE9E6F3E820E
        foreign key (AdminContactID) references casiz.agent (AgentID),
    -- Cyclic dependencies found
    ,
    constraint FK9835AE9E9EAB854A
        foreign key (InstitutionNetworkID) references casiz.institutionnetwork (InstitutionNetworkID),
    constraint FK9835AE9EDE67F146
        foreign key (InstitutionNetworkID) references casiz.institution (UserGroupScopeId)
)
    charset = utf8mb3;

alter table casiz.agent
    add constraint FK58743053D2DAD9A
        foreign key (CollectionCCID) references casiz.collection (UserGroupScopeId);

alter table casiz.agent
    add constraint FK58743053D3567E9
        foreign key (CollectionTCID) references casiz.collection (UserGroupScopeId);

create table casiz.autonumsch_coll
(
    CollectionID          int not null,
    AutoNumberingSchemeID int not null,
    primary key (CollectionID, AutoNumberingSchemeID),
    constraint FK46F04F2A8C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId),
    constraint FK46F04F2AFE55DD76
        foreign key (AutoNumberingSchemeID) references casiz.autonumberingscheme (AutoNumberingSchemeID)
)
    charset = utf8mb3;

create index CollectionGuidIDX
    on casiz.collection (GUID);

create index CollectionNameIDX
    on casiz.collection (CollectionName);

create table casiz.collectionreltype
(
    CollectionRelTypeID   int auto_increment
        primary key,
    TimestampCreated      datetime      not null,
    TimestampModified     datetime      null,
    Version               int           null,
    Name                  varchar(32)   null,
    Remarks               varchar(4096) null,
    LeftSideCollectionID  int           null,
    RightSideCollectionID int           null,
    CreatedByAgentID      int           null,
    ModifiedByAgentID     int           null,
    constraint FK1CAC96F55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK1CAC96F57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK1CAC96F5CB93CD98
        foreign key (LeftSideCollectionID) references casiz.collection (UserGroupScopeId),
    constraint FK1CAC96F5D54425AD
        foreign key (RightSideCollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create index DisciplineNameIDX
    on casiz.discipline (Name);

create table casiz.fieldnotebook
(
    FieldNotebookID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Description       text        null,
    EndDate           date        null,
    Storage           varchar(64) null,
    Name              varchar(32) null,
    StartDate         date        null,
    DisciplineID      int         not null,
    CollectionID      int         not null,
    AgentID           int         not null,
    ModifiedByAgentID int         null,
    CreatedByAgentID  int         null,
    constraint FK4647A8D5384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK4647A8D54CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK4647A8D55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK4647A8D57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK4647A8D58C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create index FNBEndDateIDX
    on casiz.fieldnotebook (EndDate);

create index FNBNameIDX
    on casiz.fieldnotebook (Name);

create index FNBStartDateIDX
    on casiz.fieldnotebook (StartDate);

create table casiz.fieldnotebookattachment
(
    FieldNotebookAttachmentId int auto_increment
        primary key,
    TimestampCreated          datetime not null,
    TimestampModified         datetime null,
    Version                   int      null,
    Ordinal                   int      not null,
    Remarks                   text     null,
    CreatedByAgentID          int      null,
    ModifiedByAgentID         int      null,
    FieldNotebookID           int      not null,
    AttachmentID              int      not null,
    constraint FKDC15BBB85327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKDC15BBB87699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKDC15BBB8B522A4E2
        foreign key (FieldNotebookID) references casiz.fieldnotebook (FieldNotebookID),
    constraint FKDC15BBB8C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.fieldnotebookpageset
(
    FieldNotebookPageSetID int auto_increment
        primary key,
    TimestampCreated       datetime     not null,
    TimestampModified      datetime     null,
    Version                int          null,
    Description            varchar(128) null,
    EndDate                date         null,
    Method                 varchar(64)  null,
    OrderNumber            smallint     null,
    StartDate              date         null,
    CreatedByAgentID       int          null,
    AgentID                int          null,
    FieldNotebookID        int          null,
    DisciplineID           int          not null,
    ModifiedByAgentID      int          null,
    constraint FK6FC0C8FE384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK6FC0C8FE4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK6FC0C8FE5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6FC0C8FE7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK6FC0C8FEB522A4E2
        foreign key (FieldNotebookID) references casiz.fieldnotebook (FieldNotebookID)
)
    charset = utf8mb3;

create table casiz.fieldnotebookpage
(
    FieldNotebookPageID    int auto_increment
        primary key,
    TimestampCreated       datetime     not null,
    TimestampModified      datetime     null,
    Version                int          null,
    Description            varchar(128) null,
    PageNumber             varchar(32)  not null,
    ScanDate               date         null,
    ModifiedByAgentID      int          null,
    DisciplineID           int          not null,
    FieldNotebookPageSetID int          null,
    CreatedByAgentID       int          null,
    constraint FK162198E44CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK162198E45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK162198E47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK162198E49B34BD5A
        foreign key (FieldNotebookPageSetID) references casiz.fieldnotebookpageset (FieldNotebookPageSetID)
)
    charset = utf8mb3;

create index FNBPPageNumberIDX
    on casiz.fieldnotebookpage (PageNumber);

create index FNBPScanDateIDX
    on casiz.fieldnotebookpage (ScanDate);

create table casiz.fieldnotebookpageattachment
(
    FieldNotebookPageAttachmentId int auto_increment
        primary key,
    TimestampCreated              datetime not null,
    TimestampModified             datetime null,
    Version                       int      null,
    Ordinal                       int      not null,
    Remarks                       text     null,
    FieldNotebookPageID           int      not null,
    CreatedByAgentID              int      null,
    ModifiedByAgentID             int      null,
    AttachmentID                  int      not null,
    constraint FK91AA25075327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK91AA250773BF3AE0
        foreign key (FieldNotebookPageID) references casiz.fieldnotebookpage (FieldNotebookPageID),
    constraint FK91AA25077699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK91AA2507C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create index FNBPSEndDateIDX
    on casiz.fieldnotebookpageset (EndDate);

create index FNBPSStartDateIDX
    on casiz.fieldnotebookpageset (StartDate);

create table casiz.fieldnotebookpagesetattachment
(
    FieldNotebookPageSetAttachmentId int auto_increment
        primary key,
    TimestampCreated                 datetime not null,
    TimestampModified                datetime null,
    Version                          int      null,
    Ordinal                          int      not null,
    Remarks                          text     null,
    ModifiedByAgentID                int      null,
    CreatedByAgentID                 int      null,
    FieldNotebookPageSetID           int      not null,
    AttachmentID                     int      not null,
    constraint FKB1477CA15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB1477CA17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB1477CA19B34BD5A
        foreign key (FieldNotebookPageSetID) references casiz.fieldnotebookpageset (FieldNotebookPageSetID),
    constraint FKB1477CA1C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.fundingagent
(
    FundingAgentID    int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    IsPrimary         bit         not null,
    OrderNumber       int         not null,
    Remarks           text        null,
    Type              varchar(32) null,
    AgentID           int         not null,
    DivisionID        int         null,
    ModifiedByAgentID int         null,
    CreatedByAgentID  int         null,
    CollectingTripID  int         not null,
    constraint AgentID
        unique (AgentID, CollectingTripID),
    constraint FKB2AD628384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKB2AD6285327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB2AD628697B3F98
        foreign key (CollectingTripID) references casiz.collectingtrip (CollectingTripID),
    constraint FKB2AD6287699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB2AD62897C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId)
)
    charset = utf8mb3;

create index COLTRIPDivIDX
    on casiz.fundingagent (DivisionID);

create table casiz.gift
(
    GiftID                    int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    DateReceived              date            null,
    GiftDate                  date            null,
    GiftNumber                varchar(50)     not null,
    IsFinancialResponsibility bit             null,
    Number1                   decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    PurposeOfGift             varchar(64)     null,
    ReceivedComments          varchar(255)    null,
    Remarks                   text            null,
    SpecialConditions         text            null,
    SrcGeography              varchar(500)    null,
    SrcTaxonomy               varchar(500)    null,
    Text1                     text            null,
    Text2                     text            null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    DisciplineID              int             not null,
    AddressOfRecordID         int             null,
    CreatedByAgentID          int             null,
    DivisionID                int             null,
    ModifiedByAgentID         int             null,
    Contents                  text            null,
    Integer1                  int             null,
    Integer2                  int             null,
    Integer3                  int             null,
    Date1                     date            null,
    Date1Precision            tinyint         null,
    Status                    varchar(64)     null,
    Text3                     text            null,
    Text4                     text            null,
    Text5                     varchar(128)    null,
    DeaccessionID             int             null,
    constraint FK3069304CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK3069305327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3069307699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK30693097C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK306930BE26B05E
        foreign key (DeaccessionID) references casiz.deaccession (DeaccessionID),
    constraint FK306930DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create index GiftDateIDX
    on casiz.gift (GiftDate);

create index GiftNumberIDX
    on casiz.gift (GiftNumber);

create table casiz.giftagent
(
    GiftAgentID       int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Remarks           text        null,
    Role              varchar(50) not null,
    ModifiedByAgentID int         null,
    GiftID            int         not null,
    CreatedByAgentID  int         null,
    DisciplineID      int         not null,
    AgentID           int         not null,
    Date1             date        null,
    constraint Role
        unique (Role, GiftID, AgentID),
    constraint FK221917D5384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK221917D54CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK221917D55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK221917D57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK221917D59890879E
        foreign key (GiftID) references casiz.gift (GiftID)
)
    charset = utf8mb3;

create index GiftAgDspMemIDX
    on casiz.giftagent (DisciplineID);

create table casiz.giftattachment
(
    GiftAttachmentID  int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    Ordinal           int      not null,
    Remarks           text     null,
    ModifiedByAgentID int      null,
    AttachmentID      int      not null,
    GiftID            int      not null,
    CreatedByAgentID  int      null,
    constraint FKC75A06535327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC75A06537699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC75A06539890879E
        foreign key (GiftID) references casiz.gift (GiftID),
    constraint FKC75A0653C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.loan
(
    LoanID                    int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    CurrentDueDate            date            null,
    DateClosed                date            null,
    DateReceived              date            null,
    IsClosed                  bit             null,
    IsFinancialResponsibility bit             null,
    LoanDate                  date            null,
    LoanNumber                varchar(50)     not null,
    Number1                   decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    OriginalDueDate           date            null,
    OverdueNotiSetDate        date            null,
    PurposeOfLoan             varchar(64)     null,
    ReceivedComments          varchar(255)    null,
    Remarks                   text            null,
    SpecialConditions         text            null,
    SrcGeography              varchar(500)    null,
    SrcTaxonomy               varchar(500)    null,
    Text1                     text            null,
    Text2                     text            null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    DisciplineID              int             not null,
    ModifiedByAgentID         int             null,
    AddressOfRecordID         int             null,
    DivisionID                int             null,
    CreatedByAgentID          int             null,
    Contents                  text            null,
    Integer1                  int             null,
    Integer2                  int             null,
    Integer3                  int             null,
    Status                    varchar(64)     null,
    Text3                     text            null,
    Text4                     text            null,
    Text5                     text            null,
    constraint FK32C4F04CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK32C4F05327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK32C4F07699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK32C4F097C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK32C4F0DC8B4810
        foreign key (AddressOfRecordID) references casiz.addressofrecord (AddressOfRecordID)
)
    charset = utf8mb3;

create index CurrentDueDateIDX
    on casiz.loan (CurrentDueDate);

create index LoanDateIDX
    on casiz.loan (LoanDate);

create index LoanNumberIDX
    on casiz.loan (LoanNumber);

create table casiz.loanagent
(
    LoanAgentID       int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Remarks           text        null,
    Role              varchar(50) not null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    AgentID           int         not null,
    LoanID            int         not null,
    DisciplineID      int         not null,
    constraint Role
        unique (Role, LoanID, AgentID),
    constraint FK63FA1415384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK63FA14154CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK63FA14155327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK63FA14157699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK63FA1415A16D4F1E
        foreign key (LoanID) references casiz.loan (LoanID)
)
    charset = utf8mb3;

create index LoanAgDspMemIDX
    on casiz.loanagent (DisciplineID);

create table casiz.loanattachment
(
    LoanAttachmentID  int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    Ordinal           int      not null,
    Remarks           text     null,
    CreatedByAgentID  int      null,
    AttachmentID      int      not null,
    LoanID            int      not null,
    ModifiedByAgentID int      null,
    constraint FK23ECB2135327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK23ECB2137699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK23ECB213A16D4F1E
        foreign key (LoanID) references casiz.loan (LoanID),
    constraint FK23ECB213C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.paleocontext
(
    PaleoContextID    int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    Remarks           text            null,
    Text1             varchar(64)     null,
    Text2             varchar(64)     null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    LithoStratID      int             null,
    ChronosStratID    int             null,
    CreatedByAgentID  int             null,
    ModifiedByAgentID int             null,
    ChronosStratEndID int             null,
    BioStratID        int             null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    Number3           decimal(20, 10) null,
    Number4           decimal(20, 10) null,
    Number5           decimal(20, 10) null,
    PaleoContextName  varchar(80)     null,
    Text3             varchar(500)    null,
    Text4             varchar(500)    null,
    Text5             varchar(500)    null,
    YesNo3            bit             null,
    YesNo4            bit             null,
    YesNo5            bit             null,
    DisciplineID      int             null,
    constraint FK99B5438A1D72DA20
        foreign key (ChronosStratEndID) references casiz.geologictimeperiod (GeologicTimePeriodID),
    constraint FK99B5438A4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK99B5438A50D2926D
        foreign key (ChronosStratID) references casiz.geologictimeperiod (GeologicTimePeriodID),
    constraint FK99B5438A5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK99B5438A7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK99B5438A89FD3495
        foreign key (BioStratID) references casiz.geologictimeperiod (GeologicTimePeriodID),
    constraint FK99B5438A9B80EF6A
        foreign key (LithoStratID) references casiz.lithostrat (LithoStratID)
)
    charset = utf8mb3;

create table casiz.locality
(
    LocalityID            int auto_increment
        primary key,
    TimestampCreated      datetime        not null,
    TimestampModified     datetime        null,
    Version               int             null,
    Datum                 varchar(50)     null,
    ElevationAccuracy     decimal(20, 10) null,
    ElevationMethod       varchar(50)     null,
    GML                   text            null,
    GUID                  varchar(128)    null,
    Lat1Text              varchar(50)     null,
    Lat2Text              varchar(50)     null,
    LatLongAccuracy       decimal(20, 10) null,
    LatLongMethod         varchar(50)     null,
    LatLongType           varchar(50)     null,
    Latitude1             decimal(12, 10) null,
    Latitude2             decimal(12, 10) null,
    LocalityName          varchar(1024)   not null,
    Long1Text             varchar(50)     null,
    Long2Text             varchar(50)     null,
    Longitude1            decimal(13, 10) null,
    Longitude2            decimal(13, 10) null,
    MaxElevation          decimal(20, 10) null,
    MinElevation          decimal(20, 10) null,
    NamedPlace            varchar(255)    null,
    OriginalElevationUnit varchar(50)     null,
    OriginalLatLongUnit   int             null,
    RelationToNamedPlace  varchar(120)    null,
    Remarks               text            null,
    SGRStatus             tinyint         null,
    ShortName             varchar(32)     null,
    SrcLatLongUnit        tinyint         not null,
    Text1                 text            null,
    Text2                 text            null,
    VerbatimElevation     varchar(50)     null,
    Visibility            tinyint         null,
    CreatedByAgentID      int             null,
    ModifiedByAgentID     int             null,
    GeographyID           int             null,
    DisciplineID          int             not null,
    VisibilitySetByID     int             null,
    Text3                 text            null,
    Text4                 text            null,
    Text5                 text            null,
    VerbatimLatitude      varchar(50)     null,
    VerbatimLongitude     varchar(50)     null,
    PaleoContextID        int             null,
    YesNo1                bit             null,
    YesNo2                bit             null,
    YesNo3                bit             null,
    YesNo4                bit             null,
    YesNo5                bit             null,
    UniqueIdentifier      varchar(128)    null,
    constraint dispLocUniqueId
        unique (DisciplineID, UniqueIdentifier),
    constraint FK714BFD634CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK714BFD635327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK714BFD637699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK714BFD637BF1F70B
        foreign key (VisibilitySetByID) references casiz.specifyuser (SpecifyUserID),
    constraint FK714BFD6397ECD2B2
        foreign key (PaleoContextID) references casiz.paleocontext (PaleoContextID),
    constraint FK714BFD63D649F6D0
        foreign key (GeographyID) references casiz.geography (GeographyID)
)
    charset = utf8mb3;

create table casiz.geocoorddetail
(
    GeoCoordDetailID         int auto_increment
        primary key,
    TimestampCreated         datetime        not null,
    TimestampModified        datetime        null,
    Version                  int             null,
    ErrorPolygon             text            null,
    GeoRefAccuracyUnits      varchar(20)     null,
    GeoRefDetDate            datetime        null,
    GeoRefDetRef             varchar(100)    null,
    GeoRefRemarks            text            null,
    GeoRefVerificationStatus varchar(50)     null,
    MaxUncertaintyEst        decimal(20, 10) null,
    MaxUncertaintyEstUnit    varchar(8)      null,
    NamedPlaceExtent         decimal(20, 10) null,
    NoGeoRefBecause          varchar(100)    null,
    OriginalCoordSystem      varchar(32)     null,
    Protocol                 varchar(64)     null,
    Source                   varchar(64)     null,
    UncertaintyPolygon       text            null,
    Validation               varchar(64)     null,
    AgentID                  int             null,
    CreatedByAgentID         int             null,
    ModifiedByAgentID        int             null,
    LocalityID               int             null,
    GeoRefAccuracy           decimal(20, 10) null,
    Text1                    text            null,
    Text2                    text            null,
    Text3                    text            null,
    GeoRefCompiledDate       datetime        null,
    CompiledByID             int             null,
    Integer1                 int             null,
    Integer2                 int             null,
    Integer3                 int             null,
    Integer4                 int             null,
    Integer5                 int             null,
    Number1                  decimal(20, 10) null,
    Number2                  decimal(20, 10) null,
    Number3                  decimal(20, 10) null,
    Number4                  decimal(20, 10) null,
    Number5                  decimal(20, 10) null,
    Text4                    text            null,
    Text5                    text            null,
    YesNo1                   bit             null,
    YesNo2                   bit             null,
    YesNo3                   bit             null,
    YesNo4                   bit             null,
    YesNo5                   bit             null,
    constraint FKB688EB95384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKB688EB955327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB688EB957699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB688EB9580202F05
        foreign key (CompiledByID) references casiz.agent (AgentID),
    constraint FKB688EB95A666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID)
)
    charset = utf8mb3;

create table casiz.latlonpolygon
(
    LatLonPolygonID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Description       text        null,
    IsPolyline        bit         not null,
    Name              varchar(64) not null,
    ModifiedByAgentID int         null,
    SpVisualQueryID   int         null,
    LocalityID        int         null,
    CreatedByAgentID  int         null,
    constraint FKE4EEDE6E2583AF6E
        foreign key (SpVisualQueryID) references casiz.spvisualquery (SpVisualQueryID),
    constraint FKE4EEDE6E5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE4EEDE6E7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKE4EEDE6EA666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID)
)
    charset = utf8mb3;

create table casiz.latlonpolygonpnt
(
    LatLonPolygonPntID int auto_increment
        primary key,
    Elevation          int             null,
    Latitude           decimal(12, 10) not null,
    Longitude          decimal(12, 10) not null,
    Ordinal            int             not null,
    LatLonPolygonID    int             not null,
    constraint FK31701508BBAA1DB4
        foreign key (LatLonPolygonID) references casiz.latlonpolygon (LatLonPolygonID)
)
    charset = utf8mb3;

create index `Index 11`
    on casiz.locality (ShortName);

create index LocalityDisciplineIDX
    on casiz.locality (DisciplineID);

create index LocalityUniqueIdentifierIDX
    on casiz.locality (UniqueIdentifier);

create index NamedPlaceIDX
    on casiz.locality (NamedPlace);

create index RelationToNamedPlaceIDX
    on casiz.locality (RelationToNamedPlace);

create index localityNameIDX
    on casiz.locality (LocalityName);

create table casiz.localityattachment
(
    LocalityAttachmentID int auto_increment
        primary key,
    TimestampCreated     datetime not null,
    TimestampModified    datetime null,
    Version              int      null,
    Ordinal              int      not null,
    Remarks              text     null,
    LocalityID           int      not null,
    ModifiedByAgentID    int      null,
    CreatedByAgentID     int      null,
    AttachmentID         int      not null,
    constraint FKB39C36C65327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB39C36C67699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB39C36C6A666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID),
    constraint FKB39C36C6C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.localitycitation
(
    LocalityCitationID int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    Remarks            text        null,
    DisciplineID       int         not null,
    ModifiedByAgentID  int         null,
    ReferenceWorkID    int         not null,
    CreatedByAgentID   int         null,
    LocalityID         int         not null,
    FigureNumber       varchar(50) null,
    IsFigured          bit         null,
    PageNumber         varchar(50) null,
    PlateNumber        varchar(50) null,
    constraint ReferenceWorkID
        unique (ReferenceWorkID, LocalityID),
    constraint FK9877F54A4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK9877F54A5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9877F54A69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK9877F54A7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9877F54AA666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID)
)
    charset = utf8mb3;

create index LocCitDspMemIDX
    on casiz.localitycitation (DisciplineID);

create table casiz.localitydetail
(
    LocalityDetailID   int auto_increment
        primary key,
    TimestampCreated   datetime        not null,
    TimestampModified  datetime        null,
    Version            int             null,
    BaseMeridian       varchar(50)     null,
    Drainage           varchar(64)     null,
    EndDepth           decimal(20, 10) null,
    enddepthunit       varchar(23)     null,
    EndDepthVerbatim   varchar(32)     null,
    GML                text            null,
    HucCode            varchar(16)     null,
    Island             varchar(64)     null,
    IslandGroup        varchar(64)     null,
    MgrsZone           varchar(4)      null,
    NationalParkName   varchar(64)     null,
    Number1            decimal(20, 10) null,
    Number2            decimal(20, 10) null,
    RangeDesc          varchar(50)     null,
    RangeDirection     varchar(50)     null,
    Section            varchar(50)     null,
    SectionPart        varchar(50)     null,
    StartDepth         decimal(20, 10) null,
    startdepthunit     varchar(23)     null,
    StartDepthVerbatim varchar(32)     null,
    Text1              text            null,
    Text2              text            null,
    Township           varchar(50)     null,
    TownshipDirection  varchar(50)     null,
    UtmDatum           varchar(255)    null,
    UtmEasting         decimal(19, 2)  null,
    UtmFalseEasting    int             null,
    UtmFalseNorthing   int             null,
    UtmNorthing        decimal(19, 2)  null,
    UtmOrigLatitude    decimal(19, 2)  null,
    UtmOrigLongitude   decimal(19, 2)  null,
    UtmScale           decimal(20, 10) null,
    UtmZone            smallint        null,
    WaterBody          varchar(64)     null,
    YesNo1             bit             null,
    YesNo2             bit             null,
    ModifiedByAgentID  int             null,
    CreatedByAgentID   int             null,
    LocalityID         int             null,
    Number3            decimal(20, 10) null,
    Number4            decimal(20, 10) null,
    Number5            decimal(20, 10) null,
    PaleoLat           varchar(32)     null,
    PaleoLng           varchar(32)     null,
    Text3              text            null,
    Text4              text            null,
    Text5              text            null,
    YesNo3             bit             null,
    YesNo4             bit             null,
    YesNo5             bit             null,
    constraint FKBB0D3F745327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBB0D3F747699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKBB0D3F74A666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID)
)
    charset = utf8mb3;

create table casiz.localitynamealias
(
    LocalityNameAliasID int auto_increment
        primary key,
    TimestampCreated    datetime     not null,
    TimestampModified   datetime     null,
    Version             int          null,
    Name                varchar(255) not null,
    Source              varchar(64)  not null,
    ModifiedByAgentID   int          null,
    DisciplineID        int          not null,
    CreatedByAgentID    int          null,
    LocalityID          int          not null,
    constraint FK29EB5CA24CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK29EB5CA25327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK29EB5CA27699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK29EB5CA2A666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID)
)
    charset = utf8mb3;

create index LocalityNameAliasIDX
    on casiz.localitynamealias (Name);

create table casiz.picklist
(
    PickListID        int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    FieldName         varchar(64) null,
    FilterFieldName   varchar(32) null,
    FilterValue       varchar(32) null,
    Formatter         varchar(64) null,
    IsSystem          bit         not null,
    Name              varchar(64) not null,
    ReadOnly          bit         not null,
    SizeLimit         int         null,
    SortType          tinyint     null,
    TableName         varchar(64) null,
    Type              tinyint     not null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    CollectionID      int         not null,
    constraint FKD3F8383F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD3F8383F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKD3F8383F8C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create index PickListNameIDX
    on casiz.picklist (Name);

create table casiz.picklistitem
(
    PickListItemID    int auto_increment
        primary key,
    TimestampCreated  datetime      not null,
    TimestampModified datetime      null,
    Version           int           null,
    Ordinal           int           null,
    Title             varchar(1024) not null,
    Value             varchar(1024) null,
    CreatedByAgentID  int           null,
    ModifiedByAgentID int           null,
    PickListID        int           not null,
    constraint FK30C57BD25327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK30C57BD2718D489C
        foreign key (PickListID) references casiz.picklist (PickListID),
    constraint FK30C57BD27699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index `Index 5`
    on casiz.picklistitem (Title);

create table casiz.preptype
(
    PrepTypeID        int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    IsLoanable        bit         not null,
    Name              varchar(64) not null,
    ModifiedByAgentID int         null,
    CollectionID      int         not null,
    CreatedByAgentID  int         null,
    constraint FKB3C452E75327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB3C452E77699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB3C452E78C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create table casiz.attributedef
(
    AttributeDefID    int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    DataType          smallint    null,
    FieldName         varchar(32) null,
    TableType         smallint    null,
    DisciplineID      int         not null,
    PrepTypeID        int         null,
    ModifiedByAgentID int         null,
    CreatedByAgentID  int         null,
    constraint FKC36883E94CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKC36883E95327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC36883E96E8973EC
        foreign key (PrepTypeID) references casiz.preptype (PrepTypeID),
    constraint FKC36883E97699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.shipment
(
    ShipmentID        int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    InsuredForAmount  varchar(50)     null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    NumberOfPackages  smallint        null,
    Remarks           text            null,
    ShipmentDate      date            null,
    ShipmentMethod    varchar(50)     null,
    ShipmentNumber    varchar(50)     not null,
    Text1             text            null,
    Text2             text            null,
    Weight            varchar(50)     null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    ModifiedByAgentID int             null,
    ShippedToID       int             null,
    LoanID            int             null,
    ShipperID         int             null,
    GiftID            int             null,
    DisciplineID      int             not null,
    ExchangeOutID     int             null,
    ShippedByID       int             null,
    CreatedByAgentID  int             null,
    BorrowID          int             null,
    constraint FKE139719A4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKE139719A5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE139719A7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKE139719A9890879E
        foreign key (GiftID) references casiz.gift (GiftID),
    constraint FKE139719AA16D4F1E
        foreign key (LoanID) references casiz.loan (LoanID),
    constraint FKE139719AA542314E
        foreign key (ExchangeOutID) references casiz.exchangeout (ExchangeOutID),
    constraint FKE139719AB172EEC7
        foreign key (ShippedByID) references casiz.agent (AgentID),
    constraint FKE139719AB17AF7EB
        foreign key (ShippedToID) references casiz.agent (AgentID),
    constraint FKE139719ABDA7A97E
        foreign key (ShipperID) references casiz.agent (AgentID),
    constraint FKE139719AF8BF6F28
        foreign key (BorrowID) references casiz.borrow (BorrowID)
)
    charset = utf8mb3;

create index ShipmentDateIDX
    on casiz.shipment (ShipmentDate);

create index ShipmentDspMemIDX
    on casiz.shipment (DisciplineID);

create index ShipmentMethodIDX
    on casiz.shipment (ShipmentMethod);

create index ShipmentNumberIDX
    on casiz.shipment (ShipmentNumber);

create table casiz.spappresourcedir
(
    SpAppResourceDirID int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    DisciplineType     varchar(64) null,
    IsPersonal         bit         not null,
    UserType           varchar(64) null,
    ModifiedByAgentID  int         null,
    CollectionID       int         null,
    SpecifyUserID      int         null,
    DisciplineID       int         null,
    CreatedByAgentID   int         null,
    constraint FK3A2F5C9B4BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK3A2F5C9B4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK3A2F5C9B5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3A2F5C9B7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK3A2F5C9B8C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create table casiz.spappresource
(
    SpAppResourceID      int auto_increment
        primary key,
    TimestampCreated     datetime     not null,
    TimestampModified    datetime     null,
    Version              int          null,
    AllPermissionLevel   int          null,
    Description          varchar(255) null,
    GroupPermissionLevel int          null,
    Level                smallint     not null,
    MetaData             varchar(255) null,
    MimeType             varchar(255) null,
    Name                 varchar(64)  not null,
    OwnerPermissionLevel int          null,
    SpPrincipalID        int          null,
    SpAppResourceDirID   int          not null,
    SpecifyUserID        int          not null,
    ModifiedByAgentID    int          null,
    CreatedByAgentID     int          null,
    constraint FK96F9D2B21A0B1F14
        foreign key (SpAppResourceDirID) references casiz.spappresourcedir (SpAppResourceDirID),
    constraint FK96F9D2B24BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK96F9D2B25327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK96F9D2B27699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK96F9D2B299A7381A
        foreign key (SpPrincipalID) references casiz.spprincipal (SpPrincipalID)
)
    charset = utf8mb3;

create index SpAppResMimeTypeIDX
    on casiz.spappresource (MimeType);

create index SpAppResNameIDX
    on casiz.spappresource (Name);

create index SpAppResourceDirDispTypeIDX
    on casiz.spappresourcedir (DisciplineType);

create table casiz.spdataset
(
    id                 int auto_increment
        primary key,
    name               varchar(256)                 not null,
    columns            longtext collate utf8mb4_bin not null,
    data               longtext collate utf8mb4_bin not null,
    uploadplan         longtext                     null,
    uploaderstatus     longtext collate utf8mb4_bin null,
    uploadresult       longtext collate utf8mb4_bin null,
    rowresults         longtext                     null,
    collection_id      int                          not null,
    specifyuser_id     int                          not null,
    visualorder        longtext collate utf8mb4_bin null,
    importedfilename   longtext                     null,
    remarks            longtext                     null,
    timestampcreated   datetime(6)                  not null,
    timestampmodified  datetime(6)                  not null,
    createdbyagent_id  int                          null,
    modifiedbyagent_id int                          null,
    constraint spdataset_collection_id_bbef545e_fk_collection_usergroupscopeid
        foreign key (collection_id) references casiz.collection (UserGroupScopeId),
    constraint spdataset_createdbyagent_id_98dcd6bd_fk_agent_agentid
        foreign key (createdbyagent_id) references casiz.agent (AgentID),
    constraint spdataset_modifiedbyagent_id_75155aa1_fk_agent_agentid
        foreign key (modifiedbyagent_id) references casiz.agent (AgentID),
    constraint spdataset_specifyuser_id_6ca97a3c_fk_specifyuser_specifyuserid
        foreign key (specifyuser_id) references casiz.specifyuser (SpecifyUserID)
)
    charset = utf8mb3;

create table casiz.spexportschema
(
    SpExportSchemaID  int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Description       varchar(255) null,
    SchemaName        varchar(80)  null,
    SchemaVersion     varchar(80)  null,
    DisciplineID      int          not null,
    ModifiedByAgentID int          null,
    CreatedByAgentID  int          null,
    constraint FKD2861D324CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKD2861D325327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD2861D327699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.sp_schema_mapping
(
    SpExportSchemaMappingID int not null,
    SpExportSchemaID        int not null,
    primary key (SpExportSchemaMappingID, SpExportSchemaID),
    constraint FKC5EDFE525722A7A2
        foreign key (SpExportSchemaID) references casiz.spexportschema (SpExportSchemaID),
    constraint FKC5EDFE52F7C8AAB0
        foreign key (SpExportSchemaMappingID) references casiz.spexportschemamapping (SpExportSchemaMappingID)
)
    charset = utf8mb3;

create table casiz.splocalecontainer
(
    SpLocaleContainerID int auto_increment
        primary key,
    TimestampCreated    datetime    not null,
    TimestampModified   datetime    null,
    Version             int         null,
    Format              varchar(64) null,
    IsHidden            bit         not null,
    IsSystem            bit         not null,
    IsUIFormatter       bit         null,
    Name                varchar(64) not null,
    PickListName        varchar(64) null,
    Type                varchar(32) null,
    Aggregator          varchar(64) null,
    DefaultUI           varchar(64) null,
    SchemaType          tinyint     not null,
    ModifiedByAgentID   int         null,
    DisciplineID        int         not null,
    CreatedByAgentID    int         null,
    constraint FK3CC8F6A4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK3CC8F6A5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3CC8F6A7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SpLocaleContainerNameIDX
    on casiz.splocalecontainer (Name);

create table casiz.splocalecontaineritem
(
    SpLocaleContainerItemID int auto_increment
        primary key,
    TimestampCreated        datetime    not null,
    TimestampModified       datetime    null,
    Version                 int         null,
    Format                  varchar(64) null,
    IsHidden                bit         not null,
    IsSystem                bit         not null,
    IsUIFormatter           bit         null,
    Name                    varchar(64) not null,
    PickListName            varchar(64) null,
    Type                    varchar(32) null,
    IsRequired              bit         null,
    WebLinkName             varchar(32) null,
    ModifiedByAgentID       int         null,
    CreatedByAgentID        int         null,
    SpLocaleContainerID     int         not null,
    constraint FK22F4457D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK22F4457D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK22F4457DC279ADEC
        foreign key (SpLocaleContainerID) references casiz.splocalecontainer (SpLocaleContainerID)
)
    charset = utf8mb3;

create table casiz.spexportschemaitem
(
    SpExportSchemaItemID    int auto_increment
        primary key,
    TimestampCreated        datetime     not null,
    TimestampModified       datetime     null,
    Version                 int          null,
    DataType                varchar(32)  null,
    Description             varchar(255) null,
    FieldName               varchar(64)  null,
    Formatter               varchar(32)  null,
    ModifiedByAgentID       int          null,
    CreatedByAgentID        int          null,
    SpLocaleContainerItemID int          null,
    SpExportSchemaID        int          not null,
    constraint FKBB21AF455327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBB21AF455722A7A2
        foreign key (SpExportSchemaID) references casiz.spexportschema (SpExportSchemaID),
    constraint FKBB21AF45720CCEF2
        foreign key (SpLocaleContainerItemID) references casiz.splocalecontaineritem (SpLocaleContainerItemID),
    constraint FKBB21AF457699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.spexportschemaitemmapping
(
    SpExportSchemaItemMappingID int auto_increment
        primary key,
    TimestampCreated            datetime     not null,
    TimestampModified           datetime     null,
    Version                     int          null,
    ExportedFieldName           varchar(64)  null,
    Remarks                     varchar(255) null,
    SpQueryFieldID              int          null,
    SpExportSchemaMappingID     int          null,
    CreatedByAgentID            int          null,
    ExportSchemaItemID          int          null,
    ModifiedByAgentID           int          null,
    ExtensionItem               bit          null,
    RowType                     varchar(500) null,
    constraint FKCD08A1E92957EC8B
        foreign key (ExportSchemaItemID) references casiz.spexportschemaitem (SpExportSchemaItemID),
    constraint FKCD08A1E92D3E491C
        foreign key (SpQueryFieldID) references casiz.spqueryfield (SpQueryFieldID),
    constraint FKCD08A1E95327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKCD08A1E97699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKCD08A1E9F7C8AAB0
        foreign key (SpExportSchemaMappingID) references casiz.spexportschemamapping (SpExportSchemaMappingID)
)
    charset = utf8mb3;

create index SpLocaleContainerItemNameIDX
    on casiz.splocalecontaineritem (Name);

create table casiz.splocaleitemstr
(
    SpLocaleItemStrID           int auto_increment
        primary key,
    TimestampCreated            datetime      not null,
    TimestampModified           datetime      null,
    Version                     int           null,
    Country                     varchar(2)    null,
    Language                    varchar(2)    not null,
    Text                        varchar(2048) not null,
    Variant                     varchar(2)    null,
    SpLocaleContainerItemNameID int           null,
    CreatedByAgentID            int           null,
    SpLocaleContainerDescID     int           null,
    SpLocaleContainerNameID     int           null,
    SpLocaleContainerItemDescID int           null,
    ModifiedByAgentID           int           null,
    constraint FK4F03EF675327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK4F03EF677699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK4F03EF67AD36C73D
        foreign key (SpLocaleContainerDescID) references casiz.splocalecontainer (SpLocaleContainerID),
    constraint FK4F03EF67BE0C2CB7
        foreign key (SpLocaleContainerNameID) references casiz.splocalecontainer (SpLocaleContainerID),
    constraint FK4F03EF67E9D506C3
        foreign key (SpLocaleContainerItemDescID) references casiz.splocalecontaineritem (SpLocaleContainerItemID),
    constraint FK4F03EF67FAAA6C3D
        foreign key (SpLocaleContainerItemNameID) references casiz.splocalecontaineritem (SpLocaleContainerItemID)
)
    charset = utf8mb3;

create index SpLocaleCountyIDX
    on casiz.splocaleitemstr (Country);

create index SpLocaleLanguageIDX
    on casiz.splocaleitemstr (Language);

create table casiz.spmerging
(
    id                 int auto_increment
        primary key,
    name               varchar(256)                 not null,
    taskid             varchar(256)                 not null,
    mergingstatus      varchar(256)                 not null,
    response           longtext                     not null,
    `table`            varchar(256)                 not null,
    newrecordid        int                          null,
    newrecordata       longtext collate utf8mb4_bin null,
    oldrecordids       longtext collate utf8mb4_bin null,
    collection_id      int                          not null,
    specifyuser_id     int                          not null,
    timestampcreated   datetime(6)                  not null,
    timestampmodified  datetime(6)                  not null,
    createdbyagent_id  int                          null,
    modifiedbyagent_id int                          null,
    constraint spmerging_collection_id_f055b425_fk_collection_usergroupscopeid
        foreign key (collection_id) references casiz.collection (UserGroupScopeId),
    constraint spmerging_createdbyagent_id_58256271_fk_agent_agentid
        foreign key (createdbyagent_id) references casiz.agent (AgentID),
    constraint spmerging_modifiedbyagent_id_93b7aacb_fk_agent_agentid
        foreign key (modifiedbyagent_id) references casiz.agent (AgentID),
    constraint spmerging_specifyuser_id_bf7bcd71_fk_specifyuser_specifyuserid
        foreign key (specifyuser_id) references casiz.specifyuser (SpecifyUserID),
    check (json_valid(`newrecordata`)),
    check (json_valid(`oldrecordids`))
)
    charset = utf8mb3;

create table casiz.sprole
(
    id            int auto_increment
        primary key,
    name          varchar(1024) not null,
    collection_id int           not null,
    description   longtext      not null,
    constraint sprole_collection_id_4dccb6f9_fk_collection_usergroupscopeid
        foreign key (collection_id) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create table casiz.sprolepolicy
(
    id       int auto_increment
        primary key,
    resource varchar(1024) not null,
    action   varchar(1024) not null,
    role_id  int           not null,
    constraint sprolepolicy_role_id_a739517f_fk_sprole_id
        foreign key (role_id) references casiz.sprole (id)
)
    charset = utf8mb3;

create table casiz.sptasksemaphore
(
    TaskSemaphoreID   int auto_increment
        primary key,
    TimestampCreated  datetime    not null,
    TimestampModified datetime    null,
    Version           int         null,
    Context           varchar(32) null,
    IsLocked          bit         null,
    LockedTime        datetime    null,
    MachineName       varchar(64) null,
    Scope             tinyint     null,
    TaskName          varchar(32) null,
    UsageCount        int         null,
    OwnerID           int         null,
    CollectionID      int         null,
    CreatedByAgentID  int         null,
    ModifiedByAgentID int         null,
    DisciplineID      int         null,
    constraint FKF2333F224CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKF2333F2251039657
        foreign key (OwnerID) references casiz.specifyuser (SpecifyUserID),
    constraint FKF2333F225327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF2333F227699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF2333F228C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId)
)
    charset = utf8mb3;

create table casiz.spuserpolicy
(
    id             int auto_increment
        primary key,
    resource       varchar(1024) not null,
    action         varchar(1024) not null,
    collection_id  int           null,
    specifyuser_id int           null,
    constraint spuserpolicy_collection_id_5bb2151a_fk_collectio
        foreign key (collection_id) references casiz.collection (UserGroupScopeId),
    constraint spuserpolicy_specifyuser_id_3388bad7_fk_specifyus
        foreign key (specifyuser_id) references casiz.specifyuser (SpecifyUserID)
)
    charset = utf8mb3;

create table casiz.spuserrole
(
    id             int auto_increment
        primary key,
    role_id        int not null,
    specifyuser_id int not null,
    constraint spuserrole_role_id_daff537c_fk_sprole_id
        foreign key (role_id) references casiz.sprole (id),
    constraint spuserrole_specifyuser_id_9b7a3225_fk_specifyuser_specifyuserid
        foreign key (specifyuser_id) references casiz.specifyuser (SpecifyUserID)
)
    charset = utf8mb3;

create table casiz.spviewsetobj
(
    SpViewSetObjID     int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    Description        varchar(255) null,
    FileName           varchar(255) null,
    Level              smallint     not null,
    MetaData           varchar(255) null,
    Name               varchar(64)  not null,
    SpAppResourceDirID int          not null,
    CreatedByAgentID   int          null,
    ModifiedByAgentID  int          null,
    constraint FK5FA666571A0B1F14
        foreign key (SpAppResourceDirID) references casiz.spappresourcedir (SpAppResourceDirID),
    constraint FK5FA666575327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK5FA666577699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.spappresourcedata
(
    SpAppResourceDataID int auto_increment
        primary key,
    TimestampCreated    datetime   not null,
    TimestampModified   datetime   null,
    Version             int        null,
    data                mediumblob null,
    SpViewSetObjID      int        null,
    ModifiedByAgentID   int        null,
    CreatedByAgentID    int        null,
    SpAppResourceID     int        null,
    constraint FKBBC195C490F514C
        foreign key (SpViewSetObjID) references casiz.spviewsetobj (SpViewSetObjID),
    constraint FKBBC195C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKBBC195C560D9D3C
        foreign key (SpAppResourceID) references casiz.spappresource (SpAppResourceID),
    constraint FKBBC195C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index SpViewObjNameIDX
    on casiz.spviewsetobj (Name);

create table casiz.taxontreedefitem
(
    TaxonTreeDefItemID int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    FormatToken        varchar(32) null,
    FullNameSeparator  varchar(32) null,
    IsEnforced         bit         null,
    IsInFullName       bit         null,
    Name               varchar(64) not null,
    RankID             int         not null,
    Remarks            text        null,
    TextAfter          varchar(64) null,
    TextBefore         varchar(64) null,
    Title              varchar(64) null,
    CreatedByAgentID   int         null,
    ModifiedByAgentID  int         null,
    ParentItemID       int         null,
    TaxonTreeDefID     int         not null,
    constraint FKF29A82305327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF29A82306A76BE4B
        foreign key (ParentItemID) references casiz.taxontreedefitem (TaxonTreeDefItemID),
    constraint FKF29A82307699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF29A8230EFA9D5F8
        foreign key (TaxonTreeDefID) references casiz.taxontreedef (TaxonTreeDefID)
)
    charset = utf8mb3;

create table casiz.taxon
(
    TaxonID                       int auto_increment
        primary key,
    TimestampCreated              datetime        not null,
    TimestampModified             datetime        null,
    Version                       int             null,
    Author                        varchar(128)    null,
    CitesStatus                   varchar(32)     null,
    COLStatus                     varchar(32)     null,
    CommonName                    varchar(128)    null,
    CultivarName                  varchar(32)     null,
    EnvironmentalProtectionStatus varchar(64)     null,
    EsaStatus                     varchar(64)     null,
    FullName                      varchar(512)    null,
    GroupNumber                   varchar(20)     null,
    GUID                          varchar(128)    null,
    HighestChildNodeNumber        int             null,
    IsAccepted                    bit             null,
    IsHybrid                      bit             null,
    IsisNumber                    varchar(16)     null,
    LabelFormat                   varchar(64)     null,
    Name                          varchar(256)    not null,
    NcbiTaxonNumber               varchar(8)      null,
    NodeNumber                    int             null,
    Number1                       int             null,
    Number2                       int             null,
    RankID                        int             not null,
    Remarks                       text            null,
    Source                        varchar(64)     null,
    TaxonomicSerialNumber         varchar(50)     null,
    Text1                         varchar(32)     null,
    Text2                         varchar(32)     null,
    UnitInd1                      varchar(50)     null,
    UnitInd2                      varchar(50)     null,
    UnitInd3                      varchar(50)     null,
    UnitInd4                      varchar(50)     null,
    UnitName1                     varchar(50)     null,
    UnitName2                     varchar(50)     null,
    UnitName3                     varchar(50)     null,
    UnitName4                     varchar(50)     null,
    UsfwsCode                     varchar(16)     null,
    Visibility                    tinyint         null,
    VisibilitySetByID             int             null,
    TaxonTreeDefItemID            int             not null,
    HybridParent1ID               int             null,
    ParentID                      int             null,
    CreatedByAgentID              int             null,
    HybridParent2ID               int             null,
    TaxonTreeDefID                int             not null,
    AcceptedID                    int             null,
    ModifiedByAgentID             int             null,
    Number3                       decimal(20, 10) null,
    Number4                       decimal(20, 10) null,
    Number5                       decimal(20, 10) null,
    Text3                         text            null,
    Text4                         text            null,
    Text5                         text            null,
    YesNo1                        bit             null,
    YesNo2                        bit             null,
    YesNo3                        bit             null,
    Integer1                      bigint          null,
    Integer2                      bigint          null,
    Integer3                      bigint          null,
    Integer4                      int             null,
    Integer5                      int             null,
    Text10                        varchar(128)    null,
    Text11                        varchar(128)    null,
    Text12                        varchar(128)    null,
    Text13                        varchar(128)    null,
    Text14                        varchar(256)    null,
    Text15                        varchar(256)    null,
    Text16                        varchar(256)    null,
    Text17                        varchar(256)    null,
    Text18                        varchar(256)    null,
    Text19                        varchar(256)    null,
    Text20                        varchar(256)    null,
    Text6                         text            null,
    Text7                         text            null,
    Text8                         text            null,
    Text9                         text            null,
    YesNo10                       bit             null,
    YesNo11                       bit             null,
    YesNo12                       bit             null,
    YesNo13                       bit             null,
    YesNo14                       bit             null,
    YesNo15                       bit             null,
    YesNo16                       bit             null,
    YesNo17                       bit             null,
    YesNo18                       bit             null,
    YesNo19                       bit             null,
    YesNo4                        bit             null,
    YesNo5                        bit             null,
    YesNo6                        bit             null,
    YesNo7                        bit             null,
    YesNo8                        bit             null,
    YesNo9                        bit             null,
    LSID                          text            null,
    TaxonAttributeID              int             null,
    constraint FK6908ECA2F773E09
        foreign key (AcceptedID) references casiz.taxon (TaxonID),
    constraint FK6908ECA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6908ECA70B0FCAD
        foreign key (HybridParent1ID) references casiz.taxon (TaxonID),
    constraint FK6908ECA70B1006E
        foreign key (HybridParent2ID) references casiz.taxon (TaxonID),
    constraint FK6908ECA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK6908ECA7BF1F70B
        foreign key (VisibilitySetByID) references casiz.specifyuser (SpecifyUserID),
    constraint FK6908ECA83339302
        foreign key (TaxonAttributeID) references casiz.taxonattribute (TaxonAttributeID),
    constraint FK6908ECABB9210FE
        foreign key (TaxonTreeDefItemID) references casiz.taxontreedefitem (TaxonTreeDefItemID),
    constraint FK6908ECABE9D724C
        foreign key (ParentID) references casiz.taxon (TaxonID),
    constraint FK6908ECAEFA9D5F8
        foreign key (TaxonTreeDefID) references casiz.taxontreedef (TaxonTreeDefID)
)
    charset = utf8mb3;

create table casiz.collectingeventattribute
(
    CollectingEventAttributeID int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    Number1                    decimal(20, 10) null,
    Number10                   decimal(20, 10) null,
    Number11                   decimal(20, 10) null,
    Number12                   decimal(20, 10) null,
    Number13                   decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    Number3                    decimal(20, 10) null,
    Number4                    decimal(20, 10) null,
    Number5                    decimal(20, 10) null,
    Number6                    decimal(20, 10) null,
    Number7                    decimal(20, 10) null,
    Number8                    decimal(20, 10) null,
    Number9                    decimal(20, 10) null,
    Remarks                    text            null,
    Text1                      text            null,
    Text10                     mediumtext      null,
    Text11                     mediumtext      null,
    Text12                     mediumtext      null,
    Text13                     mediumtext      null,
    Text14                     mediumtext      null,
    Text15                     mediumtext      null,
    Text16                     mediumtext      null,
    Text17                     mediumtext      null,
    Text2                      text            null,
    Text3                      text            null,
    Text4                      mediumtext      null,
    Text5                      mediumtext      null,
    Text6                      mediumtext      null,
    Text7                      mediumtext      null,
    Text8                      mediumtext      null,
    Text9                      mediumtext      null,
    YesNo1                     bit             null,
    YesNo2                     bit             null,
    YesNo3                     bit             null,
    YesNo4                     bit             null,
    YesNo5                     bit             null,
    DisciplineID               int             not null,
    CreatedByAgentID           int             null,
    ModifiedByAgentID          int             null,
    HostTaxonID                int             null,
    Integer1                   int             null,
    Integer10                  int             null,
    Integer2                   int             null,
    Integer3                   int             null,
    Integer4                   int             null,
    Integer5                   int             null,
    Integer6                   int             null,
    Integer7                   int             null,
    Integer8                   int             null,
    Integer9                   int             null,
    constraint FK9AD681BA32C0CDC4
        foreign key (HostTaxonID) references casiz.taxon (TaxonID),
    constraint FK9AD681BA4CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK9AD681BA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9AD681BA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.collectingevent
(
    CollectingEventID           int auto_increment
        primary key,
    TimestampCreated            datetime     not null,
    TimestampModified           datetime     null,
    Version                     int          null,
    EndDate                     date         null,
    EndDatePrecision            tinyint      null,
    EndDateVerbatim             varchar(50)  null,
    EndTime                     smallint     null,
    GUID                        varchar(128) null,
    Method                      varchar(50)  null,
    Remarks                     text         null,
    SGRStatus                   tinyint      null,
    StartDate                   date         null,
    StartDatePrecision          tinyint      null,
    StartDateVerbatim           varchar(50)  null,
    StartTime                   smallint     null,
    StationFieldNumber          varchar(50)  null,
    VerbatimDate                varchar(50)  null,
    VerbatimLocality            text         null,
    Visibility                  tinyint      null,
    LocalityID                  int          null,
    CollectingEventAttributeID  int          null,
    ModifiedByAgentID           int          null,
    CollectingTripID            int          null,
    VisibilitySetByID           int          null,
    DisciplineID                int          not null,
    CreatedByAgentID            int          null,
    Integer1                    int          null,
    Integer2                    int          null,
    ReservedInteger3            int          null,
    ReservedInteger4            int          null,
    ReservedText1               varchar(128) null,
    ReservedText2               varchar(128) null,
    Text1                       text         null,
    Text2                       text         null,
    PaleoContextID              int          null,
    StationFieldNumberModifier1 varchar(50)  null,
    StationFieldNumberModifier2 varchar(50)  null,
    StationFieldNumberModifier3 varchar(50)  null,
    Text3                       text         null,
    Text4                       text         null,
    Text5                       text         null,
    Text6                       text         null,
    Text7                       text         null,
    Text8                       text         null,
    UniqueIdentifier            varchar(128) null,
    constraint StationFieldNumber_StationFieldNumberModifier1
        unique (StationFieldNumber, StationFieldNumberModifier1),
    constraint dispCEUniqueId
        unique (DisciplineID, UniqueIdentifier),
    constraint FKFEB30F224CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FKFEB30F225327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKFEB30F22697B3F98
        foreign key (CollectingTripID) references casiz.collectingtrip (CollectingTripID),
    constraint FKFEB30F227699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKFEB30F227BF1F70B
        foreign key (VisibilitySetByID) references casiz.specifyuser (SpecifyUserID),
    constraint FKFEB30F2297ECD2B2
        foreign key (PaleoContextID) references casiz.paleocontext (PaleoContextID),
    constraint FKFEB30F22A666A5C4
        foreign key (LocalityID) references casiz.locality (LocalityID),
    constraint FKFEB30F22FEB93AB2
        foreign key (CollectingEventAttributeID) references casiz.collectingeventattribute (CollectingEventAttributeID)
)
    charset = utf8mb3;

create index CEEndDateIDX
    on casiz.collectingevent (EndDate);

create index CEGuidIDX
    on casiz.collectingevent (GUID);

create index CEStartDateIDX
    on casiz.collectingevent (StartDate);

create index CEStationFieldNumberIDX
    on casiz.collectingevent (StationFieldNumber);

create index CEUniqueIdentifierIDX
    on casiz.collectingevent (UniqueIdentifier);

create index `Index 13`
    on casiz.collectingevent (StartDateVerbatim);

create index `Index 15`
    on casiz.collectingevent (Integer1);

create table casiz.collectingeventattachment
(
    CollectingEventAttachmentID int auto_increment
        primary key,
    TimestampCreated            datetime not null,
    TimestampModified           datetime null,
    Version                     int      null,
    CollectionMemberID          int      not null,
    Ordinal                     int      not null,
    Remarks                     text     null,
    AttachmentID                int      not null,
    ModifiedByAgentID           int      null,
    CollectingEventID           int      not null,
    CreatedByAgentID            int      null,
    constraint FK32C365C55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK32C365C57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK32C365C5B237E2BC
        foreign key (CollectingEventID) references casiz.collectingevent (CollectingEventID),
    constraint FK32C365C5C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create index CEAColMemIDX
    on casiz.collectingeventattachment (CollectionMemberID);

create table casiz.collectingeventattr
(
    AttrID             int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    CollectionMemberID int          not null,
    DoubleValue        double       null,
    StrValue           varchar(255) null,
    CollectingEventID  int          not null,
    CreatedByAgentID   int          null,
    ModifiedByAgentID  int          null,
    AttributeDefID     int          not null,
    constraint FK42A088135327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK42A088137699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK42A08813B237E2BC
        foreign key (CollectingEventID) references casiz.collectingevent (CollectingEventID),
    constraint FK42A08813E84BA7B0
        foreign key (AttributeDefID) references casiz.attributedef (AttributeDefID)
)
    charset = utf8mb3;

create index COLEVATColMemIDX
    on casiz.collectingeventattr (CollectionMemberID);

create index COLEVATSDispIDX
    on casiz.collectingeventattribute (DisciplineID);

create index `Index 7`
    on casiz.collectingeventattribute (Number1);

create table casiz.collectingeventauthorization
(
    CollectingEventAuthorizationID int auto_increment
        primary key,
    TimestampCreated               datetime not null,
    TimestampModified              datetime null,
    Version                        int      null,
    Remarks                        text     null,
    CreatedByAgentID               int      null,
    PermitID                       int      not null,
    CollectingEventID              int      null,
    ModifiedByAgentID              int      null,
    constraint FK67DBF8975327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK67DBF8977699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK67DBF897AD1F31F4
        foreign key (PermitID) references casiz.permit (PermitID),
    constraint FK67DBF897B237E2BC
        foreign key (CollectingEventID) references casiz.collectingevent (CollectingEventID)
)
    charset = utf8mb3;

create table casiz.collectionobject
(
    CollectionObjectID          int auto_increment
        primary key,
    TimestampCreated            datetime        not null,
    TimestampModified           datetime        null,
    Version                     int             null,
    CollectionMemberID          int             not null,
    AltCatalogNumber            varchar(64)     null,
    Availability                varchar(32)     null,
    CatalogNumber               varchar(32)     null,
    CatalogedDate               date            null,
    CatalogedDatePrecision      tinyint         null,
    CatalogedDateVerbatim       varchar(32)     null,
    CountAmt                    int             null,
    Deaccessioned               bit             null,
    Description                 mediumtext      null,
    FieldNumber                 varchar(50)     null,
    GUID                        varchar(128)    null,
    InventoryDate               date            null,
    Modifier                    varchar(50)     null,
    Name                        varchar(64)     null,
    Notifications               varchar(32)     null,
    Number1                     decimal(20, 10) null,
    Number2                     decimal(20, 10) null,
    ObjectCondition             varchar(64)     null,
    OCR                         text            null,
    ProjectNumber               varchar(64)     null,
    Remarks                     text            null,
    ReservedText                varchar(128)    null,
    Restrictions                varchar(32)     null,
    SGRStatus                   tinyint         null,
    Text1                       text            null,
    Text2                       text            null,
    Text3                       text            null,
    TotalValue                  decimal(12, 2)  null,
    Visibility                  tinyint         null,
    YesNo1                      bit             null,
    YesNo2                      bit             null,
    YesNo3                      bit             null,
    YesNo4                      bit             null,
    YesNo5                      bit             null,
    YesNo6                      bit             null,
    CollectingEventID           int             null,
    CatalogerID                 int             null,
    CollectionID                int             not null,
    AppraisalID                 int             null,
    ContainerID                 int             null,
    CollectionObjectAttributeID int             null,
    ModifiedByAgentID           int             null,
    FieldNotebookPageID         int             null,
    VisibilitySetByID           int             null,
    PaleoContextID              int             null,
    CreatedByAgentID            int             null,
    ContainerOwnerID            int             null,
    AccessionID                 int             null,
    Integer1                    int             null,
    Integer2                    int             null,
    ReservedInteger3            int             null,
    ReservedInteger4            int             null,
    ReservedText2               varchar(128)    null,
    ReservedText3               varchar(128)    null,
    InventorizedByID            int             null,
    Date1                       date            null,
    Date1Precision              tinyint         null,
    InventoryDatePrecision      tinyint         null,
    Agent1ID                    int             null,
    NumberOfDuplicates          int             null,
    EmbargoReason               text            null,
    EmbargoReleaseDate          date            null,
    EmbargoReleaseDatePrecision tinyint         null,
    EmbargoStartDate            date            null,
    EmbargoStartDatePrecision   tinyint         null,
    Text4                       text            null,
    Text5                       text            null,
    Text6                       text            null,
    Text7                       text            null,
    Text8                       text            null,
    UniqueIdentifier            varchar(128)    null,
    EmbargoAuthorityID          int             null,
    constraint CollectionID
        unique (CollectionID, CatalogNumber),
    constraint collCoUniqueId
        unique (CollectionID, UniqueIdentifier),
    constraint FKC1D4635D3925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FKC1D4635D3B87E163
        foreign key (CatalogerID) references casiz.agent (AgentID),
    constraint FKC1D4635D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC1D4635D73BF3AE0
        foreign key (FieldNotebookPageID) references casiz.fieldnotebookpage (FieldNotebookPageID),
    constraint FKC1D4635D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC1D4635D7BF1F70B
        foreign key (VisibilitySetByID) references casiz.specifyuser (SpecifyUserID),
    constraint FKC1D4635D8C2288BA
        foreign key (CollectionID) references casiz.collection (UserGroupScopeId),
    constraint FKC1D4635D97ECD2B2
        foreign key (PaleoContextID) references casiz.paleocontext (PaleoContextID),
    constraint FKC1D4635D9F4EE41
        foreign key (InventorizedByID) references casiz.agent (AgentID),
    constraint FKC1D4635DA141B896
        foreign key (CollectionObjectAttributeID) references casiz.collectionobjectattribute (CollectionObjectAttributeID),
    constraint FKC1D4635DA40125AB
        foreign key (ContainerOwnerID) references casiz.container (ContainerID),
    constraint FKC1D4635DB15CB762
        foreign key (AppraisalID) references casiz.appraisal (AppraisalID),
    constraint FKC1D4635DB237E2BC
        foreign key (CollectingEventID) references casiz.collectingevent (CollectingEventID),
    constraint FKC1D4635DCF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FKC1D4635DCFF5EC6D
        foreign key (EmbargoAuthorityID) references casiz.agent (AgentID),
    constraint FKC1D4635DE816739A
        foreign key (ContainerID) references casiz.container (ContainerID)
)
    charset = utf8mb3;

create index AltCatalogNumberIDX
    on casiz.collectionobject (AltCatalogNumber);

create index COColMemIDX
    on casiz.collectionobject (CollectionMemberID);

create index COUniqueIdentifierIDX
    on casiz.collectionobject (UniqueIdentifier);

create index CatalogNumberIDX
    on casiz.collectionobject (CatalogNumber);

create index CatalogedDateIDX
    on casiz.collectionobject (CatalogedDate);

create index ColObjGuidIDX
    on casiz.collectionobject (GUID);

create index FieldNumberIDX
    on casiz.collectionobject (FieldNumber);

create index `Index 21`
    on casiz.collectionobject (Number1);

create table casiz.collectionobjectattachment
(
    CollectionObjectAttachmentID int auto_increment
        primary key,
    TimestampCreated             datetime not null,
    TimestampModified            datetime null,
    Version                      int      null,
    CollectionMemberID           int      not null,
    Ordinal                      int      not null,
    Remarks                      text     null,
    CreatedByAgentID             int      null,
    CollectionObjectID           int      not null,
    AttachmentID                 int      not null,
    ModifiedByAgentID            int      null,
    constraint FK9C00EC405327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9C00EC4075E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK9C00EC407699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9C00EC40C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create index COLOBJATTColMemIDX
    on casiz.collectionobjectattachment (CollectionMemberID);

create table casiz.collectionobjectattr
(
    AttrID             int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    CollectionMemberID int          not null,
    DoubleValue        double       null,
    StrValue           varchar(255) null,
    ModifiedByAgentID  int          null,
    CreatedByAgentID   int          null,
    CollectionObjectID int          not null,
    AttributeDefID     int          not null,
    constraint FK303746CE5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK303746CE75E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK303746CE7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK303746CEE84BA7B0
        foreign key (AttributeDefID) references casiz.attributedef (AttributeDefID)
)
    charset = utf8mb3;

create index COLOBJATRSColMemIDX
    on casiz.collectionobjectattr (CollectionMemberID);

create table casiz.collectionobjectcitation
(
    CollectionObjectCitationID int auto_increment
        primary key,
    TimestampCreated           datetime    not null,
    TimestampModified          datetime    null,
    Version                    int         null,
    CollectionMemberID         int         not null,
    IsFigured                  bit         null,
    Remarks                    text        null,
    CollectionObjectID         int         not null,
    ReferenceWorkID            int         not null,
    CreatedByAgentID           int         null,
    ModifiedByAgentID          int         null,
    FigureNumber               varchar(50) null,
    PageNumber                 varchar(50) null,
    PlateNumber                varchar(50) null,
    constraint FKAB9FC1445327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKAB9FC14469734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FKAB9FC14475E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKAB9FC1447699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index COCITColMemIDX
    on casiz.collectionobjectcitation (CollectionMemberID);

create table casiz.collectionobjectproperty
(
    CollectionObjectPropertyID int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    CollectionMemberID         int             not null,
    Date1                      date            null,
    Date10                     date            null,
    Date11                     date            null,
    Date12                     date            null,
    Date13                     date            null,
    Date14                     date            null,
    Date15                     date            null,
    Date16                     date            null,
    Date17                     date            null,
    Date18                     date            null,
    Date19                     date            null,
    Date2                      date            null,
    Date20                     date            null,
    Date3                      date            null,
    Date4                      date            null,
    Date5                      date            null,
    Date6                      date            null,
    Date7                      date            null,
    Date8                      date            null,
    Date9                      date            null,
    GUID                       varchar(128)    null,
    Integer1                   smallint        null,
    Integer10                  smallint        null,
    Integer11                  smallint        null,
    Integer12                  smallint        null,
    Integer13                  smallint        null,
    Integer14                  smallint        null,
    Integer15                  smallint        null,
    Integer16                  smallint        null,
    Integer17                  smallint        null,
    Integer18                  smallint        null,
    Integer19                  smallint        null,
    Integer2                   smallint        null,
    Integer20                  smallint        null,
    Integer21                  int             null,
    Integer22                  int             null,
    Integer23                  int             null,
    Integer24                  int             null,
    Integer25                  int             null,
    Integer26                  int             null,
    Integer27                  int             null,
    Integer28                  int             null,
    Integer29                  int             null,
    Integer3                   smallint        null,
    Integer30                  int             null,
    Integer4                   smallint        null,
    Integer5                   smallint        null,
    Integer6                   smallint        null,
    Integer7                   smallint        null,
    Integer8                   smallint        null,
    Integer9                   smallint        null,
    Number1                    decimal(20, 10) null,
    Number10                   decimal(20, 10) null,
    Number11                   decimal(20, 10) null,
    Number12                   decimal(20, 10) null,
    Number13                   decimal(20, 10) null,
    Number14                   decimal(20, 10) null,
    Number15                   decimal(20, 10) null,
    Number16                   decimal(20, 10) null,
    Number17                   decimal(20, 10) null,
    Number18                   decimal(20, 10) null,
    Number19                   decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    Number20                   decimal(20, 10) null,
    Number21                   decimal(20, 10) null,
    Number22                   decimal(20, 10) null,
    Number23                   decimal(20, 10) null,
    Number24                   decimal(20, 10) null,
    Number25                   decimal(20, 10) null,
    Number26                   decimal(20, 10) null,
    Number27                   decimal(20, 10) null,
    Number28                   decimal(20, 10) null,
    Number29                   decimal(20, 10) null,
    Number3                    decimal(20, 10) null,
    Number30                   decimal(20, 10) null,
    Number4                    decimal(20, 10) null,
    Number5                    decimal(20, 10) null,
    Number6                    decimal(20, 10) null,
    Number7                    decimal(20, 10) null,
    Number8                    decimal(20, 10) null,
    Number9                    decimal(20, 10) null,
    Remarks                    text            null,
    Text1                      varchar(50)     null,
    Text10                     varchar(50)     null,
    Text11                     varchar(50)     null,
    Text12                     varchar(50)     null,
    Text13                     varchar(50)     null,
    Text14                     varchar(50)     null,
    Text15                     varchar(50)     null,
    Text16                     varchar(100)    null,
    Text17                     varchar(100)    null,
    Text18                     varchar(100)    null,
    Text19                     varchar(100)    null,
    Text2                      varchar(50)     null,
    Text20                     varchar(100)    null,
    Text21                     varchar(100)    null,
    Text22                     varchar(100)    null,
    Text23                     varchar(100)    null,
    Text24                     varchar(100)    null,
    Text25                     varchar(100)    null,
    Text26                     varchar(100)    null,
    Text27                     varchar(100)    null,
    Text28                     varchar(100)    null,
    Text29                     varchar(100)    null,
    Text3                      varchar(50)     null,
    Text30                     varchar(100)    null,
    Text31                     text            null,
    Text32                     text            null,
    Text33                     text            null,
    Text34                     text            null,
    Text35                     text            null,
    Text36                     text            null,
    Text37                     text            null,
    Text38                     text            null,
    Text39                     text            null,
    Text4                      varchar(50)     null,
    Text40                     text            null,
    Text5                      varchar(50)     null,
    Text6                      varchar(50)     null,
    Text7                      varchar(50)     null,
    Text8                      varchar(50)     null,
    Text9                      varchar(50)     null,
    YesNo1                     bit             null,
    YesNo10                    bit             null,
    YesNo11                    bit             null,
    YesNo12                    bit             null,
    YesNo13                    bit             null,
    YesNo14                    bit             null,
    YesNo15                    bit             null,
    YesNo16                    bit             null,
    YesNo17                    bit             null,
    YesNo18                    bit             null,
    YesNo19                    bit             null,
    YesNo2                     bit             null,
    YesNo20                    bit             null,
    YesNo3                     bit             null,
    YesNo4                     bit             null,
    YesNo5                     bit             null,
    YesNo6                     bit             null,
    YesNo7                     bit             null,
    YesNo8                     bit             null,
    YesNo9                     bit             null,
    Agent5ID                   int             null,
    Agent8D                    int             null,
    Agent2ID                   int             null,
    Agent3ID                   int             null,
    ModifiedByAgentID          int             null,
    Agent19ID                  int             null,
    CreatedByAgentID           int             null,
    CollectionObjectID         int             not null,
    Agent17ID                  int             null,
    Agent4ID                   int             null,
    Agent15ID                  int             null,
    Agent20ID                  int             null,
    Agent12ID                  int             null,
    Agent14ID                  int             null,
    Agent7ID                   int             null,
    Agent13ID                  int             null,
    Agent18ID                  int             null,
    Agent1ID                   int             null,
    Agent6ID                   int             null,
    Agent11ID                  int             null,
    Agent16ID                  int             null,
    Agent9ID                   int             null,
    Agent10ID                  int             null,
    constraint FKC66B94321213D341
        foreign key (Agent10ID) references casiz.agent (AgentID),
    constraint FKC66B94321213D702
        foreign key (Agent11ID) references casiz.agent (AgentID),
    constraint FKC66B94321213DAC3
        foreign key (Agent12ID) references casiz.agent (AgentID),
    constraint FKC66B94321213DE84
        foreign key (Agent13ID) references casiz.agent (AgentID),
    constraint FKC66B94321213E245
        foreign key (Agent14ID) references casiz.agent (AgentID),
    constraint FKC66B94321213E606
        foreign key (Agent15ID) references casiz.agent (AgentID),
    constraint FKC66B94321213E9C7
        foreign key (Agent16ID) references casiz.agent (AgentID),
    constraint FKC66B94321213ED88
        foreign key (Agent17ID) references casiz.agent (AgentID),
    constraint FKC66B94321213F149
        foreign key (Agent18ID) references casiz.agent (AgentID),
    constraint FKC66B94321213F50A
        foreign key (Agent19ID) references casiz.agent (AgentID),
    constraint FKC66B9432121447A0
        foreign key (Agent20ID) references casiz.agent (AgentID),
    constraint FKC66B9432384B3033
        foreign key (Agent8D) references casiz.agent (AgentID),
    constraint FKC66B94325327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC66B943275E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKC66B94327699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC66B9432CF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF197EEA
        foreign key (Agent2ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF1982AB
        foreign key (Agent3ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF19866C
        foreign key (Agent4ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF198A2D
        foreign key (Agent5ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF198DEE
        foreign key (Agent6ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF1991AF
        foreign key (Agent7ID) references casiz.agent (AgentID),
    constraint FKC66B9432CF199931
        foreign key (Agent9ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.collectionrelationship
(
    CollectionRelationshipID int auto_increment
        primary key,
    TimestampCreated         datetime    not null,
    TimestampModified        datetime    null,
    Version                  int         null,
    Text1                    varchar(32) null,
    Text2                    varchar(32) null,
    RightSideCollectionID    int         not null,
    LeftSideCollectionID     int         not null,
    ModifiedByAgentID        int         null,
    CollectionRelTypeID      int         null,
    CreatedByAgentID         int         null,
    constraint FK246327D65327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK246327D6637B3A82
        foreign key (CollectionRelTypeID) references casiz.collectionreltype (CollectionRelTypeID),
    constraint FK246327D67699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK246327D678903837
        foreign key (LeftSideCollectionID) references casiz.collectionobject (CollectionObjectID),
    constraint FK246327D68240904C
        foreign key (RightSideCollectionID) references casiz.collectionobject (CollectionObjectID)
)
    charset = utf8mb3;

create table casiz.collector
(
    CollectorID       int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    IsPrimary         bit      not null,
    OrderNumber       int      not null,
    Remarks           text     null,
    ModifiedByAgentID int      null,
    CollectingEventID int      not null,
    CreatedByAgentID  int      null,
    DivisionID        int      null,
    AgentID           int      not null,
    Text1             text     null,
    Text2             text     null,
    YesNo1            bit      null,
    YesNo2            bit      null,
    constraint AgentID
        unique (AgentID, CollectingEventID),
    constraint FK7043CC8D384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK7043CC8D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK7043CC8D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK7043CC8D97C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId),
    constraint FK7043CC8DB237E2BC
        foreign key (CollectingEventID) references casiz.collectingevent (CollectingEventID)
)
    charset = utf8mb3;

create index COLTRDivIDX
    on casiz.collector (DivisionID);

create table casiz.commonnametx
(
    CommonNameTxID    int auto_increment
        primary key,
    TimestampCreated  datetime     not null,
    TimestampModified datetime     null,
    Version           int          null,
    Author            varchar(128) null,
    Country           varchar(2)   null,
    Language          varchar(2)   null,
    Name              varchar(255) null,
    Variant           varchar(2)   null,
    TaxonID           int          not null,
    ModifiedByAgentID int          null,
    CreatedByAgentID  int          null,
    constraint FK3413DFFA1D39F06C
        foreign key (TaxonID) references casiz.taxon (TaxonID),
    constraint FK3413DFFA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK3413DFFA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index CommonNameTxCountryIDX
    on casiz.commonnametx (Country);

create index CommonNameTxNameIDX
    on casiz.commonnametx (Name);

create table casiz.commonnametxcitation
(
    CommonNameTxCitationID int auto_increment
        primary key,
    TimestampCreated       datetime        not null,
    TimestampModified      datetime        null,
    Version                int             null,
    Number1                decimal(20, 10) null,
    Number2                decimal(20, 10) null,
    Remarks                text            null,
    Text1                  text            null,
    Text2                  text            null,
    YesNo1                 bit             null,
    YesNo2                 bit             null,
    CreatedByAgentID       int             null,
    ModifiedByAgentID      int             null,
    ReferenceWorkID        int             not null,
    CommonNameTxID         int             not null,
    FigureNumber           varchar(50)     null,
    IsFigured              bit             null,
    PageNumber             varchar(50)     null,
    PlateNumber            varchar(50)     null,
    constraint FK829B50E115A0FFF2
        foreign key (CommonNameTxID) references casiz.commonnametx (CommonNameTxID),
    constraint FK829B50E15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK829B50E169734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK829B50E17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.determination
(
    DeterminationID         int auto_increment
        primary key,
    TimestampCreated        datetime        not null,
    TimestampModified       datetime        null,
    Version                 int             null,
    CollectionMemberID      int             not null,
    Addendum                varchar(16)     null,
    AlternateName           varchar(128)    null,
    Confidence              varchar(50)     null,
    DeterminedDate          date            null,
    DeterminedDatePrecision tinyint         null,
    FeatureOrBasis          varchar(250)    null,
    GUID                    varchar(128)    null,
    IsCurrent               bit             not null,
    Method                  varchar(50)     null,
    NameUsage               varchar(64)     null,
    Number1                 decimal(20, 10) null,
    Number2                 decimal(20, 10) null,
    Qualifier               varchar(16)     null,
    Remarks                 text            null,
    SubSpQualifier          varchar(16)     null,
    Text1                   text            null,
    Text2                   text            null,
    TypeStatusName          varchar(50)     null,
    VarQualifier            varchar(16)     null,
    YesNo1                  bit             null,
    YesNo2                  bit             null,
    TaxonID                 int             null,
    CreatedByAgentID        int             null,
    PreferredTaxonID        int             null,
    CollectionObjectID      int             not null,
    DeterminerID            int             null,
    ModifiedByAgentID       int             null,
    Integer1                int             null,
    Integer2                int             null,
    Integer3                int             null,
    Integer4                int             null,
    Integer5                int             null,
    Number3                 decimal(20, 10) null,
    Number4                 decimal(20, 10) null,
    Number5                 decimal(20, 10) null,
    Text3                   text            null,
    Text4                   varchar(128)    null,
    Text5                   varchar(128)    null,
    Text6                   varchar(128)    null,
    Text7                   varchar(128)    null,
    Text8                   varchar(128)    null,
    YesNo3                  bit             null,
    YesNo4                  bit             null,
    YesNo5                  bit             null,
    constraint FKC1E98FE31D39F06C
        foreign key (TaxonID) references casiz.taxon (TaxonID),
    constraint FKC1E98FE3280D00CB
        foreign key (PreferredTaxonID) references casiz.taxon (TaxonID),
    constraint FKC1E98FE35327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC1E98FE375E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKC1E98FE37699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC1E98FE3E9268B1C
        foreign key (DeterminerID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index AlterNameIDX
    on casiz.determination (AlternateName);

create index DetMemIDX
    on casiz.determination (CollectionMemberID);

create index DeterminationGuidIDX
    on casiz.determination (GUID);

create index DeterminedDateIDX
    on casiz.determination (DeterminedDate);

create index TypeStatusNameIDX
    on casiz.determination (TypeStatusName);

create table casiz.determinationcitation
(
    DeterminationCitationID int auto_increment
        primary key,
    TimestampCreated        datetime    not null,
    TimestampModified       datetime    null,
    Version                 int         null,
    CollectionMemberID      int         not null,
    Remarks                 text        null,
    ReferenceWorkID         int         not null,
    ModifiedByAgentID       int         null,
    CreatedByAgentID        int         null,
    DeterminationID         int         not null,
    FigureNumber            varchar(50) null,
    IsFigured               bit         null,
    PageNumber              varchar(50) null,
    PlateNumber             varchar(50) null,
    constraint ReferenceWorkID
        unique (ReferenceWorkID, DeterminationID),
    constraint FK259B07CA47AE835E
        foreign key (DeterminationID) references casiz.determination (DeterminationID),
    constraint FK259B07CA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK259B07CA69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK259B07CA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index DetCitColMemIDX
    on casiz.determinationcitation (CollectionMemberID);

create table casiz.determiner
(
    DeterminerID      int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    IsPrimary         bit      not null,
    OrderNumber       int      not null,
    Remarks           text     null,
    Text1             text     null,
    Text2             text     null,
    YesNo1            bit      null,
    YesNo2            bit      null,
    DeterminationID   int      not null,
    ModifiedByAgentID int      null,
    AgentID           int      not null,
    CreatedByAgentID  int      null,
    constraint AgentID
        unique (AgentID, DeterminationID),
    constraint FKA5478E7F384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKA5478E7F47AE835E
        foreign key (DeterminationID) references casiz.determination (DeterminationID),
    constraint FKA5478E7F5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKA5478E7F7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.exsiccataitem
(
    ExsiccataItemID    int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    Fascicle           varchar(16) null,
    Number             varchar(16) null,
    ExsiccataID        int         not null,
    ModifiedByAgentID  int         null,
    CreatedByAgentID   int         null,
    CollectionObjectID int         not null,
    constraint FK23150E183B4364A2
        foreign key (ExsiccataID) references casiz.exsiccata (ExsiccataID),
    constraint FK23150E185327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK23150E1875E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK23150E187699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.otheridentifier
(
    OtherIdentifierID  int auto_increment
        primary key,
    TimestampCreated   datetime    not null,
    TimestampModified  datetime    null,
    Version            int         null,
    CollectionMemberID int         not null,
    Identifier         varchar(64) not null,
    Institution        varchar(64) null,
    Remarks            text        null,
    ModifiedByAgentID  int         null,
    CreatedByAgentID   int         null,
    CollectionObjectID int         not null,
    Date1              date        null,
    Date1Precision     tinyint     null,
    Date2              date        null,
    Date2Precision     tinyint     null,
    Text1              text        null,
    Text2              text        null,
    Text3              text        null,
    Text4              text        null,
    Text5              text        null,
    YesNo1             bit         null,
    YesNo2             bit         null,
    YesNo3             bit         null,
    YesNo4             bit         null,
    YesNo5             bit         null,
    Agent2ID           int         null,
    Agent1ID           int         null,
    constraint FK2A5397B95327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK2A5397B975E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK2A5397B97699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK2A5397B9CF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FK2A5397B9CF197EEA
        foreign key (Agent2ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index OthIdColMemIDX
    on casiz.otheridentifier (CollectionMemberID);

create table casiz.preparation
(
    PreparationID          int auto_increment
        primary key,
    TimestampCreated       datetime        not null,
    TimestampModified      datetime        null,
    Version                int             null,
    CollectionMemberID     int             not null,
    CountAmt               int             null,
    Description            varchar(255)    null,
    Number1                decimal(20, 10) null,
    Number2                decimal(20, 10) null,
    PreparedDate           date            null,
    PreparedDatePrecision  tinyint         null,
    Remarks                text            null,
    SampleNumber           varchar(32)     null,
    Status                 varchar(32)     null,
    StorageLocation        varchar(50)     null,
    Text1                  text            null,
    Text2                  text            null,
    YesNo1                 bit             null,
    YesNo2                 bit             null,
    YesNo3                 bit             null,
    CollectionObjectID     int             not null,
    CreatedByAgentID       int             null,
    ModifiedByAgentID      int             null,
    PrepTypeID             int             not null,
    PreparationAttributeID int             null,
    PreparedByID           int             null,
    StorageID              int             null,
    Integer1               int             null,
    Integer2               int             null,
    ReservedInteger3       int             null,
    ReservedInteger4       int             null,
    GUID                   varchar(128)    null,
    Text3                  text            null,
    Text4                  text            null,
    Text5                  text            null,
    Date1                  date            null,
    Date1Precision         tinyint         null,
    Date2                  date            null,
    Date2Precision         tinyint         null,
    Date3                  date            null,
    Date3Precision         tinyint         null,
    Date4                  date            null,
    Date4Precision         tinyint         null,
    Text6                  text            null,
    Text7                  text            null,
    Text8                  text            null,
    Text9                  text            null,
    AlternateStorageID     int             null,
    BarCode                varchar(256)    null,
    Text10                 text            null,
    Text11                 text            null,
    Text12                 varchar(128)    null,
    Text13                 varchar(128)    null,
    constraint PrepGuidIDX
        unique (GUID),
    constraint collPrepUniqueId
        unique (CollectionMemberID, BarCode),
    constraint FKB198269745F8D1A8
        foreign key (PreparationAttributeID) references casiz.preparationattribute (PreparationAttributeID),
    constraint FKB19826975327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKB19826976E8973EC
        foreign key (PrepTypeID) references casiz.preptype (PrepTypeID),
    constraint FKB198269775E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKB19826977699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKB1982697EB48144E
        foreign key (StorageID) references casiz.storage (StorageID),
    constraint FKB1982697EBDCBD14
        foreign key (AlternateStorageID) references casiz.storage (StorageID),
    constraint FKB1982697FEE420B1
        foreign key (PreparedByID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.conservdescription
(
    ConservDescriptionID    int auto_increment
        primary key,
    TimestampCreated        datetime        not null,
    TimestampModified       datetime        null,
    Version                 int             null,
    BackgroundInfo          text            null,
    Composition             text            null,
    Description             text            null,
    DisplayRecommendations  text            null,
    Height                  decimal(20, 10) null,
    LightRecommendations    text            null,
    ObjLength               decimal(20, 10) null,
    OtherRecommendations    text            null,
    Remarks                 text            null,
    ShortDesc               varchar(128)    null,
    Source                  text            null,
    Units                   varchar(16)     null,
    Width                   decimal(20, 10) null,
    DivisionID              int             null,
    CreatedByAgentID        int             null,
    ModifiedByAgentID       int             null,
    CollectionObjectID      int             null,
    CatalogedDate           date            null,
    determinedDatePrecision tinyint         null,
    PreparationID           int             null,
    Date1                   date            null,
    Date1Precision          tinyint         null,
    Date2                   date            null,
    Date2Precision          tinyint         null,
    Date3                   date            null,
    Date3Precision          tinyint         null,
    Date4                   date            null,
    Date4Precision          tinyint         null,
    Date5                   date            null,
    Date5Precision          tinyint         null,
    Integer1                int             null,
    Integer2                int             null,
    Integer3                int             null,
    Integer4                int             null,
    Integer5                int             null,
    Number1                 decimal(20, 10) null,
    Number2                 decimal(20, 10) null,
    Number3                 decimal(20, 10) null,
    Number4                 decimal(20, 10) null,
    Number5                 decimal(20, 10) null,
    Text1                   text            null,
    Text2                   text            null,
    Text3                   text            null,
    Text4                   text            null,
    Text5                   text            null,
    YesNo1                  bit             null,
    YesNo2                  bit             null,
    YesNo3                  bit             null,
    YesNo4                  bit             null,
    YesNo5                  bit             null,
    constraint FKC040F46418627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FKC040F4645327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKC040F46475E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKC040F4647699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKC040F46497C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId)
)
    charset = utf8mb3;

create index ConservDescShortDescIDX
    on casiz.conservdescription (ShortDesc);

create table casiz.conservdescriptionattachment
(
    ConservDescriptionAttachmentID int auto_increment
        primary key,
    TimestampCreated               datetime not null,
    TimestampModified              datetime null,
    Version                        int      null,
    Ordinal                        int      not null,
    Remarks                        text     null,
    AttachmentID                   int      not null,
    ConservDescriptionID           int      not null,
    ModifiedByAgentID              int      null,
    CreatedByAgentID               int      null,
    constraint FK1EED20875327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK1EED20877699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK1EED20878FF9CFA6
        foreign key (ConservDescriptionID) references casiz.conservdescription (ConservDescriptionID),
    constraint FK1EED2087C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.conservevent
(
    ConservEventID               int auto_increment
        primary key,
    TimestampCreated             datetime          not null,
    TimestampModified            datetime          null,
    Version                      int               null,
    AdvTestingExam               text              null,
    AdvTestingExamResults        text              null,
    CompletedComments            text              null,
    CompletedDate                date              null,
    ConditionReport              text              null,
    CuratorApprovalDate          date              null,
    ExamDate                     date              null,
    Number1                      int               null,
    Number2                      int               null,
    PhotoDocs                    text              null,
    Remarks                      text              null,
    Text1                        varchar(64)       null,
    Text2                        varchar(64)       null,
    TreatmentCompDate            date              null,
    TreatmentReport              text              null,
    YesNo1                       bit               null,
    YesNo2                       bit               null,
    ConservDescriptionID         int               not null,
    CreatedByAgentID             int               null,
    TreatedByAgentID             int               null,
    ModifiedByAgentID            int               null,
    CuratorID                    int               null,
    ExaminedByAgentID            int               null,
    CompletedDatePrecision       tinyint default 1 null,
    CuratorApprovalDatePrecision tinyint default 1 null,
    ExamDatePrecision            tinyint default 1 null,
    TreatmentCompDatePrecision   tinyint default 1 null,
    constraint FK74A8510227E00C28
        foreign key (ExaminedByAgentID) references casiz.agent (AgentID),
    constraint FK74A851025327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK74A8510271496BD2
        foreign key (TreatedByAgentID) references casiz.agent (AgentID),
    constraint FK74A851027699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK74A85102828C4E73
        foreign key (CuratorID) references casiz.agent (AgentID),
    constraint FK74A851028FF9CFA6
        foreign key (ConservDescriptionID) references casiz.conservdescription (ConservDescriptionID)
)
    charset = utf8mb3;

create index ConservCompletedDateIDX
    on casiz.conservevent (CompletedDate);

create index ConservExamDateIDX
    on casiz.conservevent (ExamDate);

create table casiz.conserveventattachment
(
    ConservEventAttachmentID int auto_increment
        primary key,
    TimestampCreated         datetime not null,
    TimestampModified        datetime null,
    Version                  int      null,
    Ordinal                  int      not null,
    Remarks                  text     null,
    CreatedByAgentID         int      null,
    ConservEventID           int      not null,
    ModifiedByAgentID        int      null,
    AttachmentID             int      not null,
    constraint FKD3F7CFA55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD3F7CFA57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKD3F7CFA5C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID),
    constraint FKD3F7CFA5F849E7A2
        foreign key (ConservEventID) references casiz.conservevent (ConservEventID)
)
    charset = utf8mb3;

create table casiz.exchangeinprep
(
    ExchangeInPrepID      int auto_increment
        primary key,
    TimestampCreated      datetime     not null,
    TimestampModified     datetime     null,
    Version               int          null,
    Comments              text         null,
    DescriptionOfMaterial varchar(255) null,
    Number1               int          null,
    Quantity              int          null,
    Text1                 text         null,
    Text2                 text         null,
    PreparationID         int          null,
    ExchangeInID          int          null,
    ModifiedByAgentID     int          null,
    CreatedByAgentID      int          null,
    DisciplineID          int          not null,
    constraint FK9A0BCB518627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FK9A0BCB51E18122E
        foreign key (ExchangeInID) references casiz.exchangein (ExchangeInID),
    constraint FK9A0BCB54CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK9A0BCB55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9A0BCB57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index ExchgInPrepDspMemIDX
    on casiz.exchangeinprep (DisciplineID);

create table casiz.exchangeoutprep
(
    ExchangeOutPrepID     int auto_increment
        primary key,
    TimestampCreated      datetime     not null,
    TimestampModified     datetime     null,
    Version               int          null,
    Comments              text         null,
    DescriptionOfMaterial varchar(255) null,
    Number1               int          null,
    Quantity              int          null,
    Text1                 text         null,
    Text2                 text         null,
    PreparationID         int          null,
    ModifiedByAgentID     int          null,
    DisciplineID          int          not null,
    ExchangeOutID         int          null,
    CreatedByAgentID      int          null,
    constraint FK7405CEF818627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FK7405CEF84CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK7405CEF85327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK7405CEF87699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK7405CEF8A542314E
        foreign key (ExchangeOutID) references casiz.exchangeout (ExchangeOutID)
)
    charset = utf8mb3;

create index ExchgOutPrepDspMemIDX
    on casiz.exchangeoutprep (DisciplineID);

create table casiz.giftpreparation
(
    GiftPreparationID     int auto_increment
        primary key,
    TimestampCreated      datetime     not null,
    TimestampModified     datetime     null,
    Version               int          null,
    DescriptionOfMaterial varchar(255) null,
    InComments            text         null,
    OutComments           text         null,
    Quantity              int          null,
    ReceivedComments      text         null,
    ModifiedByAgentID     int          null,
    CreatedByAgentID      int          null,
    DisciplineID          int          not null,
    GiftID                int          null,
    PreparationID         int          null,
    Text1                 text         null,
    Text2                 text         null,
    Text3                 text         null,
    Text4                 text         null,
    Text5                 text         null,
    constraint FK18B1F6718627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FK18B1F674CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK18B1F675327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK18B1F677699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK18B1F679890879E
        foreign key (GiftID) references casiz.gift (GiftID)
)
    charset = utf8mb3;

create index GiftPrepDspMemIDX
    on casiz.giftpreparation (DisciplineID);

create table casiz.loanpreparation
(
    LoanPreparationID     int auto_increment
        primary key,
    TimestampCreated      datetime not null,
    TimestampModified     datetime null,
    Version               int      null,
    DescriptionOfMaterial text     null,
    InComments            text     null,
    IsResolved            bit      not null,
    OutComments           text     null,
    Quantity              int      null,
    QuantityResolved      int      null,
    QuantityReturned      int      null,
    ReceivedComments      text     null,
    DisciplineID          int      not null,
    PreparationID         int      null,
    CreatedByAgentID      int      null,
    LoanID                int      not null,
    ModifiedByAgentID     int      null,
    Text1                 text     null,
    Text2                 text     null,
    Text3                 text     null,
    Text4                 text     null,
    Text5                 text     null,
    constraint FK374DEBA718627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FK374DEBA74CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK374DEBA75327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK374DEBA77699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK374DEBA7A16D4F1E
        foreign key (LoanID) references casiz.loan (LoanID)
)
    charset = utf8mb3;

create index LoanPrepDspMemIDX
    on casiz.loanpreparation (DisciplineID);

create table casiz.loanreturnpreparation
(
    LoanReturnPreparationID  int auto_increment
        primary key,
    TimestampCreated         datetime not null,
    TimestampModified        datetime null,
    Version                  int      null,
    QuantityResolved         int      null,
    QuantityReturned         int      null,
    Remarks                  text     null,
    ReturnedDate             date     null,
    DisciplineID             int      not null,
    DeaccessionPreparationID int      null,
    ReceivedByID             int      null,
    CreatedByAgentID         int      null,
    LoanPreparationID        int      not null,
    ModifiedByAgentID        int      null,
    constraint FK3632847749C90455
        foreign key (ReceivedByID) references casiz.agent (AgentID),
    constraint FK363284774CE675DE
        foreign key (DisciplineID) references casiz.discipline (UserGroupScopeId),
    constraint FK363284775327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK363284777699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK36328477CD552686
        foreign key (LoanPreparationID) references casiz.loanpreparation (LoanPreparationID)
)
    charset = utf8mb3;

create table casiz.disposalpreparation
(
    DisposalPreparationID   int auto_increment
        primary key,
    TimestampCreated        datetime not null,
    TimestampModified       datetime null,
    Version                 int      null,
    Quantity                int      null,
    Remarks                 text     null,
    DisposalID              int      not null,
    LoanReturnPreparationID int      null,
    PreparationID           int      null,
    ModifiedByAgentID       int      null,
    CreatedByAgentID        int      null,
    constraint FK9F77C04618627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FK9F77C0465327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9F77C0467699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9F77C04695DEF246
        foreign key (LoanReturnPreparationID) references casiz.loanreturnpreparation (LoanReturnPreparationID),
    constraint FK9F77C046C7670AE0
        foreign key (DisposalID) references casiz.disposal (DisposalID)
)
    charset = utf8mb3;

create index FK36328477EF0E7D46
    on casiz.loanreturnpreparation (DeaccessionPreparationID);

create index LoanRetPrepDspMemIDX
    on casiz.loanreturnpreparation (DisciplineID);

create index LoanReturnedDateIDX
    on casiz.loanreturnpreparation (ReturnedDate);

create table casiz.materialsample
(
    MaterialSampleID           int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    CollectionMemberID         int             not null,
    GGBNAbsorbanceRatio260_230 decimal(20, 10) null,
    GGBNAbsorbanceRatio260_280 decimal(20, 10) null,
    GGBNRAbsorbanceRatioMethod varchar(64)     null,
    GGBNConcentration          decimal(20, 10) null,
    GGBNConcentrationUnit      varchar(64)     null,
    GGBNMaterialSampleType     varchar(64)     null,
    GGBNMedium                 varchar(64)     null,
    GGBNPurificationMethod     varchar(64)     null,
    GGBNQuality                varchar(64)     null,
    GGBNQualityCheckDate       date            null,
    GGBNQualityRemarks         text            null,
    GGBNSampleDesignation      varchar(128)    null,
    GGBNSampleSize             decimal(20, 10) null,
    GGBNVolume                 decimal(20, 10) null,
    GGBNVolumeUnit             varchar(64)     null,
    GGBNWeight                 decimal(20, 10) null,
    GGBNWeightMethod           varchar(64)     null,
    GGBNWeightUnit             varchar(64)     null,
    GUID                       varchar(128)    null,
    Integer1                   int             null,
    Integer2                   int             null,
    Number1                    decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    Remarks                    text            null,
    ReservedInteger3           int             null,
    ReservedInteger4           int             null,
    ReservedNumber3            decimal(20, 10) null,
    ReservedNumber4            decimal(20, 10) null,
    ReservedText3              text            null,
    ReservedText4              text            null,
    SRABioProjectID            varchar(64)     null,
    SRABioSampleID             varchar(64)     null,
    SRAProjectID               varchar(64)     null,
    SRASampleID                varchar(64)     null,
    Text1                      text            null,
    Text2                      text            null,
    YesNo1                     bit             null,
    YesNo2                     bit             null,
    CreatedByAgentID           int             null,
    PreparationID              int             not null,
    ModifiedByAgentID          int             null,
    ExtractionDate             date            null,
    ExtractorID                int             null,
    constraint FKD5CE219118627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FKD5CE21915327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD5CE21917699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKD5CE2191E43B7581
        foreign key (ExtractorID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.dnasequence
(
    DnaSequenceID           int auto_increment
        primary key,
    TimestampCreated        datetime        not null,
    TimestampModified       datetime        null,
    Version                 int             null,
    CollectionMemberID      int             not null,
    AmbiguousResidues       int             null,
    BOLDBarcodeID           varchar(32)     null,
    BOLDLastUpdateDate      date            null,
    BOLDSampleID            varchar(32)     null,
    BOLDTranslationMatrix   varchar(64)     null,
    CompA                   int             null,
    CompC                   int             null,
    CompG                   int             null,
    compT                   int             null,
    GenBankAccessionNumber  varchar(32)     null,
    GeneSequence            text            null,
    MoleculeType            varchar(32)     null,
    Number1                 decimal(20, 10) null,
    Number2                 decimal(20, 10) null,
    Number3                 decimal(20, 10) null,
    Remarks                 text            null,
    TargetMarker            varchar(32)     null,
    Text1                   varchar(32)     null,
    Text2                   varchar(32)     null,
    Text3                   varchar(64)     null,
    TotalResidues           int             null,
    YesNo1                  bit             null,
    YesNo2                  bit             null,
    YesNo3                  bit             null,
    CreatedByAgentID        int             null,
    AgentID                 int             null,
    ModifiedByAgentID       int             null,
    CollectionObjectID      int             null,
    MaterialSampleID        int             null,
    ExtractionDate          date            null,
    ExtractionDatePrecision tinyint         null,
    SequenceDate            date            null,
    SequenceDatePrecision   tinyint         null,
    ExtractorID             int             null,
    constraint FK9F42F5D8384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK9F42F5D85327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK9F42F5D875E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK9F42F5D87699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK9F42F5D8A1F7C080
        foreign key (MaterialSampleID) references casiz.materialsample (MaterialSampleID),
    constraint FK9F42F5D8E43B7581
        foreign key (ExtractorID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index BOLDBarcodeIDX
    on casiz.dnasequence (BOLDBarcodeID);

create index BOLDSampleIDX
    on casiz.dnasequence (BOLDSampleID);

create index GenBankAccIDX
    on casiz.dnasequence (GenBankAccessionNumber);

create table casiz.dnasequenceattachment
(
    DnaSequenceAttachmentId int auto_increment
        primary key,
    TimestampCreated        datetime not null,
    TimestampModified       datetime null,
    Version                 int      null,
    Ordinal                 int      not null,
    Remarks                 text     null,
    ModifiedByAgentID       int      null,
    DnaSequenceID           int      not null,
    CreatedByAgentID        int      null,
    AttachmentID            int      not null,
    constraint FKFFC2E0FB265FB168
        foreign key (DnaSequenceID) references casiz.dnasequence (DnaSequenceID),
    constraint FKFFC2E0FB5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKFFC2E0FB7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKFFC2E0FBC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.dnasequencingrun
(
    DNASequencingRunID        int auto_increment
        primary key,
    TimestampCreated          datetime        not null,
    TimestampModified         datetime        null,
    Version                   int             null,
    CollectionMemberID        int             not null,
    GeneSequence              text            null,
    Number1                   decimal(20, 10) null,
    Number2                   decimal(20, 10) null,
    Number3                   decimal(20, 10) null,
    Ordinal                   int             null,
    PCRCocktailPrimer         bit             null,
    PCRForwardPrimerCode      varchar(32)     null,
    PCRPrimerName             varchar(32)     null,
    PCRPrimerSequence5_3      varchar(64)     null,
    PCRReversePrimerCode      varchar(32)     null,
    ReadDirection             varchar(16)     null,
    Remarks                   text            null,
    RunDate                   date            null,
    ScoreFileName             varchar(32)     null,
    SequenceCocktailPrimer    bit             null,
    SequencePrimerCode        varchar(32)     null,
    SequencePrimerName        varchar(32)     null,
    SequencePrimerSequence5_3 varchar(64)     null,
    Text1                     varchar(32)     null,
    Text2                     varchar(32)     null,
    Text3                     varchar(64)     null,
    TraceFileName             varchar(32)     null,
    YesNo1                    bit             null,
    YesNo2                    bit             null,
    YesNo3                    bit             null,
    ModifiedByAgentID         int             null,
    PreparedByAgentID         int             null,
    RunByAgentID              int             null,
    DNASequenceID             int             not null,
    CreatedByAgentID          int             null,
    DryadDOI                  varchar(256)    null,
    SRAExperimentID           varchar(64)     null,
    SRARunID                  varchar(64)     null,
    SRASubmissionID           varchar(64)     null,
    DNAPrimerID               int             null,
    constraint FK2AF6F9D6265FB168
        foreign key (DNASequenceID) references casiz.dnasequence (DnaSequenceID),
    constraint FK2AF6F9D65327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK2AF6F9D67699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK2AF6F9D6851BDBC0
        foreign key (RunByAgentID) references casiz.agent (AgentID),
    constraint FK2AF6F9D68C3587CC
        foreign key (DNAPrimerID) references casiz.dnaprimer (DNAPrimerID),
    constraint FK2AF6F9D6D76CA4E
        foreign key (PreparedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.dnasequencerunattachment
(
    DnaSequencingRunAttachmentId int auto_increment
        primary key,
    TimestampCreated             datetime not null,
    TimestampModified            datetime null,
    Version                      int      null,
    Ordinal                      int      not null,
    Remarks                      text     null,
    AttachmentID                 int      not null,
    CreatedByAgentID             int      null,
    ModifiedByAgentID            int      null,
    DnaSequencingRunID           int      not null,
    constraint FKD0DAEB165327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKD0DAEB167699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKD0DAEB1678F036AA
        foreign key (DnaSequencingRunID) references casiz.dnasequencingrun (DNASequencingRunID),
    constraint FKD0DAEB16C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.dnasequencingruncitation
(
    DNASequencingRunCitationID int auto_increment
        primary key,
    TimestampCreated           datetime        not null,
    TimestampModified          datetime        null,
    Version                    int             null,
    Number1                    decimal(20, 10) null,
    Number2                    decimal(20, 10) null,
    Remarks                    text            null,
    Text1                      text            null,
    Text2                      text            null,
    YesNo1                     bit             null,
    YesNo2                     bit             null,
    ModifiedByAgentID          int             null,
    ReferenceWorkID            int             not null,
    CreatedByAgentID           int             null,
    DNASequencingRunID         int             not null,
    FigureNumber               varchar(50)     null,
    IsFigured                  bit             null,
    PageNumber                 varchar(50)     null,
    PlateNumber                varchar(50)     null,
    constraint FK24CEBD5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK24CEBD69734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK24CEBD7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK24CEBD78F036AA
        foreign key (DNASequencingRunID) references casiz.dnasequencingrun (DNASequencingRunID)
)
    charset = utf8mb3;

create table casiz.extractor
(
    ExtractorID       int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    OrderNumber       int      not null,
    Remarks           text     null,
    Text1             text     null,
    Text2             text     null,
    YesNo1            bit      null,
    YesNo2            bit      null,
    DNASequenceID     int      not null,
    ModifiedByAgentID int      null,
    AgentID           int      not null,
    CreatedByAgentID  int      null,
    constraint AgentID
        unique (AgentID, DNASequenceID),
    constraint FKF0EDCE24265FB168
        foreign key (DNASequenceID) references casiz.dnasequence (DnaSequenceID),
    constraint FKF0EDCE24384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FKF0EDCE245327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF0EDCE247699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index DesignationIDX
    on casiz.materialsample (GGBNSampleDesignation);

create table casiz.pcrperson
(
    PcrPersonID       int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    OrderNumber       int      not null,
    Remarks           text     null,
    Text1             text     null,
    Text2             text     null,
    YesNo1            bit      null,
    YesNo2            bit      null,
    AgentID           int      not null,
    DNASequenceID     int      not null,
    CreatedByAgentID  int      null,
    ModifiedByAgentID int      null,
    constraint AgentID
        unique (AgentID, DNASequenceID),
    constraint FK5D6EE8F4265FB168
        foreign key (DNASequenceID) references casiz.dnasequence (DnaSequenceID),
    constraint FK5D6EE8F4384B3622
        foreign key (AgentID) references casiz.agent (AgentID),
    constraint FK5D6EE8F45327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK5D6EE8F47699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index PrepBarCodeIdx
    on casiz.preparation (BarCode);

create index PrepColMemIDX
    on casiz.preparation (CollectionMemberID);

create index PrepSampleNumIDX
    on casiz.preparation (SampleNumber);

create index PreparedDateIDX
    on casiz.preparation (PreparedDate);

create table casiz.preparationattachment
(
    PreparationAttachmentID int auto_increment
        primary key,
    TimestampCreated        datetime not null,
    TimestampModified       datetime null,
    Version                 int      null,
    CollectionMemberID      int      not null,
    Ordinal                 int      not null,
    Remarks                 text     null,
    PreparationID           int      not null,
    ModifiedByAgentID       int      null,
    CreatedByAgentID        int      null,
    AttachmentID            int      not null,
    constraint FKE3FD6EFA18627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FKE3FD6EFA5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE3FD6EFA7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKE3FD6EFAC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create index PrepAttColMemIDX
    on casiz.preparationattachment (CollectionMemberID);

create table casiz.preparationattr
(
    AttrID             int auto_increment
        primary key,
    TimestampCreated   datetime     not null,
    TimestampModified  datetime     null,
    Version            int          null,
    CollectionMemberID int          not null,
    DoubleValue        double       null,
    StrValue           varchar(255) null,
    ModifiedByAgentID  int          null,
    PreparationId      int          not null,
    CreatedByAgentID   int          null,
    AttributeDefID     int          not null,
    constraint FK4592DD0818627F06
        foreign key (PreparationId) references casiz.preparation (PreparationID),
    constraint FK4592DD085327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK4592DD087699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK4592DD08E84BA7B0
        foreign key (AttributeDefID) references casiz.attributedef (AttributeDefID)
)
    charset = utf8mb3;

create index PrepAttrColMemIDX
    on casiz.preparationattr (CollectionMemberID);

create table casiz.preparationproperty
(
    PreparationPropertyID int auto_increment
        primary key,
    TimestampCreated      datetime        not null,
    TimestampModified     datetime        null,
    Version               int             null,
    CollectionMemberID    int             not null,
    Date1                 date            null,
    Date10                date            null,
    Date11                date            null,
    Date12                date            null,
    Date13                date            null,
    Date14                date            null,
    Date15                date            null,
    Date16                date            null,
    Date17                date            null,
    Date18                date            null,
    Date19                date            null,
    Date2                 date            null,
    Date20                date            null,
    Date3                 date            null,
    Date4                 date            null,
    Date5                 date            null,
    Date6                 date            null,
    Date7                 date            null,
    Date8                 date            null,
    Date9                 date            null,
    GUID                  varchar(128)    null,
    Integer1              smallint        null,
    Integer10             smallint        null,
    Integer11             smallint        null,
    Integer12             smallint        null,
    Integer13             smallint        null,
    Integer14             smallint        null,
    Integer15             smallint        null,
    Integer16             smallint        null,
    Integer17             smallint        null,
    Integer18             smallint        null,
    Integer19             smallint        null,
    Integer2              smallint        null,
    Integer20             smallint        null,
    Integer21             int             null,
    Integer22             int             null,
    Integer23             int             null,
    Integer24             int             null,
    Integer25             int             null,
    Integer26             int             null,
    Integer27             int             null,
    Integer28             int             null,
    Integer29             int             null,
    Integer3              smallint        null,
    Integer30             int             null,
    Integer4              smallint        null,
    Integer5              smallint        null,
    Integer6              smallint        null,
    Integer7              smallint        null,
    Integer8              smallint        null,
    Integer9              smallint        null,
    Number1               decimal(20, 10) null,
    Number10              decimal(20, 10) null,
    Number11              decimal(20, 10) null,
    Number12              decimal(20, 10) null,
    Number13              decimal(20, 10) null,
    Number14              decimal(20, 10) null,
    Number15              decimal(20, 10) null,
    Number16              decimal(20, 10) null,
    Number17              decimal(20, 10) null,
    Number18              decimal(20, 10) null,
    Number19              decimal(20, 10) null,
    Number2               decimal(20, 10) null,
    Number20              decimal(20, 10) null,
    Number21              decimal(20, 10) null,
    Number22              decimal(20, 10) null,
    Number23              decimal(20, 10) null,
    Number24              decimal(20, 10) null,
    Number25              decimal(20, 10) null,
    Number26              decimal(20, 10) null,
    Number27              decimal(20, 10) null,
    Number28              decimal(20, 10) null,
    Number29              decimal(20, 10) null,
    Number3               decimal(20, 10) null,
    Number30              decimal(20, 10) null,
    Number4               decimal(20, 10) null,
    Number5               decimal(20, 10) null,
    Number6               decimal(20, 10) null,
    Number7               decimal(20, 10) null,
    Number8               decimal(20, 10) null,
    Number9               decimal(20, 10) null,
    Remarks               text            null,
    Text1                 varchar(50)     null,
    Text10                varchar(50)     null,
    Text11                varchar(50)     null,
    Text12                varchar(50)     null,
    Text13                varchar(50)     null,
    Text14                varchar(50)     null,
    Text15                varchar(50)     null,
    Text16                varchar(100)    null,
    Text17                varchar(100)    null,
    Text18                varchar(100)    null,
    Text19                varchar(100)    null,
    Text2                 varchar(50)     null,
    Text20                varchar(100)    null,
    Text21                varchar(100)    null,
    Text22                varchar(100)    null,
    Text23                varchar(100)    null,
    Text24                varchar(100)    null,
    Text25                varchar(100)    null,
    Text26                varchar(100)    null,
    Text27                varchar(100)    null,
    Text28                varchar(100)    null,
    Text29                varchar(100)    null,
    Text3                 varchar(50)     null,
    Text30                varchar(100)    null,
    Text31                text            null,
    Text32                text            null,
    Text33                text            null,
    Text34                text            null,
    Text35                text            null,
    Text36                text            null,
    Text37                text            null,
    Text38                text            null,
    Text39                text            null,
    Text4                 varchar(50)     null,
    Text40                text            null,
    Text5                 varchar(50)     null,
    Text6                 varchar(50)     null,
    Text7                 varchar(50)     null,
    Text8                 varchar(50)     null,
    Text9                 varchar(50)     null,
    YesNo1                bit             null,
    YesNo10               bit             null,
    YesNo11               bit             null,
    YesNo12               bit             null,
    YesNo13               bit             null,
    YesNo14               bit             null,
    YesNo15               bit             null,
    YesNo16               bit             null,
    YesNo17               bit             null,
    YesNo18               bit             null,
    YesNo19               bit             null,
    YesNo2                bit             null,
    YesNo20               bit             null,
    YesNo3                bit             null,
    YesNo4                bit             null,
    YesNo5                bit             null,
    YesNo6                bit             null,
    YesNo7                bit             null,
    YesNo8                bit             null,
    YesNo9                bit             null,
    Agent19ID             int             null,
    CreatedByAgentID      int             null,
    Agent9ID              int             null,
    Agent8D               int             null,
    Agent3ID              int             null,
    Agent1ID              int             null,
    Agent14ID             int             null,
    Agent13ID             int             null,
    Agent7ID              int             null,
    Agent18ID             int             null,
    Agent6ID              int             null,
    Agent20ID             int             null,
    ModifiedByAgentID     int             null,
    Agent11ID             int             null,
    Agent10ID             int             null,
    Agent2ID              int             null,
    Agent5ID              int             null,
    Agent16ID             int             null,
    Agent4ID              int             null,
    Agent12ID             int             null,
    Agent17ID             int             null,
    Agent15ID             int             null,
    PreparationID         int             not null,
    constraint FKFB3D7D6C1213D341
        foreign key (Agent10ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213D702
        foreign key (Agent11ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213DAC3
        foreign key (Agent12ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213DE84
        foreign key (Agent13ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213E245
        foreign key (Agent14ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213E606
        foreign key (Agent15ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213E9C7
        foreign key (Agent16ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213ED88
        foreign key (Agent17ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213F149
        foreign key (Agent18ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C1213F50A
        foreign key (Agent19ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C121447A0
        foreign key (Agent20ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C18627F06
        foreign key (PreparationID) references casiz.preparation (PreparationID),
    constraint FKFB3D7D6C384B3033
        foreign key (Agent8D) references casiz.agent (AgentID),
    constraint FKFB3D7D6C5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKFB3D7D6C7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF197B29
        foreign key (Agent1ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF197EEA
        foreign key (Agent2ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF1982AB
        foreign key (Agent3ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF19866C
        foreign key (Agent4ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF198A2D
        foreign key (Agent5ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF198DEE
        foreign key (Agent6ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF1991AF
        foreign key (Agent7ID) references casiz.agent (AgentID),
    constraint FKFB3D7D6CCF199931
        foreign key (Agent9ID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.project_colobj
(
    ProjectID          int not null,
    CollectionObjectID int not null,
    primary key (ProjectID, CollectionObjectID),
    constraint FK1E416F5D75E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK1E416F5DAF28760A
        foreign key (ProjectID) references casiz.project (ProjectID)
)
    charset = utf8mb3;

create index EnvironmentalProtectionStatusIDX
    on casiz.taxon (EnvironmentalProtectionStatus);

create index `Index 17`
    on casiz.taxon (Number2);

create index TaxonCommonNameIDX
    on casiz.taxon (CommonName);

create index TaxonFullNameIDX
    on casiz.taxon (FullName);

create index TaxonGuidIDX
    on casiz.taxon (GUID);

create index TaxonNameIDX
    on casiz.taxon (Name);

create index TaxonomicSerialNumberIDX
    on casiz.taxon (TaxonomicSerialNumber);

create index Text15
    on casiz.taxon (Text15(255));

create table casiz.taxonattachment
(
    TaxonAttachmentID int auto_increment
        primary key,
    TimestampCreated  datetime not null,
    TimestampModified datetime null,
    Version           int      null,
    Ordinal           int      not null,
    Remarks           text     null,
    CreatedByAgentID  int      null,
    ModifiedByAgentID int      null,
    AttachmentID      int      not null,
    TaxonID           int      not null,
    constraint FKF523736D1D39F06C
        foreign key (TaxonID) references casiz.taxon (TaxonID),
    constraint FKF523736D5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKF523736D7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FKF523736DC7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.taxoncitation
(
    TaxonCitationID   int auto_increment
        primary key,
    TimestampCreated  datetime        not null,
    TimestampModified datetime        null,
    Version           int             null,
    Number1           decimal(20, 10) null,
    Number2           decimal(20, 10) null,
    Remarks           text            null,
    Text1             text            null,
    Text2             text            null,
    YesNo1            bit             null,
    YesNo2            bit             null,
    TaxonID           int             not null,
    CreatedByAgentID  int             null,
    ReferenceWorkID   int             not null,
    ModifiedByAgentID int             null,
    FigureNumber      varchar(50)     null,
    IsFigured         bit             null,
    PageNumber        varchar(50)     null,
    PlateNumber       varchar(50)     null,
    constraint FK14242FB11D39F06C
        foreign key (TaxonID) references casiz.taxon (TaxonID),
    constraint FK14242FB15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK14242FB169734F30
        foreign key (ReferenceWorkID) references casiz.referencework (ReferenceWorkID),
    constraint FK14242FB17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create index `Index 6`
    on casiz.taxontreedefitem (RankID);

create index `Index 7`
    on casiz.taxontreedefitem (Name);

create table casiz.treatmentevent
(
    TreatmentEventID     int auto_increment
        primary key,
    TimestampCreated     datetime        not null,
    TimestampModified    datetime        null,
    Version              int             null,
    DateBoxed            date            null,
    DateCleaned          date            null,
    DateCompleted        date            null,
    DateReceived         date            null,
    DateToIsolation      date            null,
    DateTreatmentEnded   date            null,
    DateTreatmentStarted date            null,
    FieldNumber          varchar(50)     null,
    Storage              varchar(64)     null,
    Remarks              text            null,
    TreatmentNumber      varchar(32)     null,
    Type                 varchar(128)    null,
    CollectionObjectID   int             null,
    CreatedByAgentID     int             null,
    ModifiedByAgentID    int             null,
    DivisionID           int             null,
    AccessionID          int             null,
    Number1              int             null,
    Number2              int             null,
    Number3              decimal(20, 10) null,
    Number4              decimal(20, 10) null,
    Number5              decimal(20, 10) null,
    Text1                text            null,
    Text2                text            null,
    Text3                text            null,
    Text4                text            null,
    Text5                text            null,
    YesNo1               bit             null,
    YesNo2               bit             null,
    YesNo3               bit             null,
    PerformedByID        int             null,
    AuthorizedByID       int             null,
    constraint FK577D85223925EE20
        foreign key (AccessionID) references casiz.accession (AccessionID),
    constraint FK577D8522410EB2B4
        foreign key (PerformedByID) references casiz.agent (AgentID),
    constraint FK577D85225327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK577D852275E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FK577D85227699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK577D85227D49A30F
        foreign key (AuthorizedByID) references casiz.agent (AgentID),
    constraint FK577D852297C961D8
        foreign key (DivisionID) references casiz.division (UserGroupScopeId)
)
    charset = utf8mb3;

create index TEDateReceivedIDX
    on casiz.treatmentevent (DateReceived);

create index TEDateTreatmentStartedIDX
    on casiz.treatmentevent (DateTreatmentStarted);

create index TEFieldNumberIDX
    on casiz.treatmentevent (FieldNumber);

create index TETreatmentNumberIDX
    on casiz.treatmentevent (TreatmentNumber);

create table casiz.treatmenteventattachment
(
    TreatmentEventAttachmentID int auto_increment
        primary key,
    TimestampCreated           datetime not null,
    TimestampModified          datetime null,
    Version                    int      null,
    Ordinal                    int      not null,
    Remarks                    text     null,
    CreatedByAgentID           int      null,
    ModifiedByAgentID          int      null,
    TreatmentEventID           int      not null,
    AttachmentID               int      not null,
    constraint FK1725BC52BE40B22
        foreign key (TreatmentEventID) references casiz.treatmentevent (TreatmentEventID),
    constraint FK1725BC55327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK1725BC57699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK1725BC5C7E55084
        foreign key (AttachmentID) references casiz.attachment (AttachmentID)
)
    charset = utf8mb3;

create table casiz.visit
(
    VisitNo          int                                 not null
        primary key,
    TimestampCreated timestamp default CURRENT_TIMESTAMP not null,
    AgentID          int                                 null,
    BegVisitDate     date                                null,
    EndVisitDate     date                                null,
    Taxa             varchar(120)                        null,
    Consult          varchar(80)                         null,
    TaxonID          int                                 null
)
    charset = utf8mb3
    row_format = COMPACT;

create index Person
    on casiz.visit (AgentID);

create index Taxon
    on casiz.visit (TaxonID);

create table casiz.voucherrelationship
(
    VoucherRelationshipID int auto_increment
        primary key,
    TimestampCreated      datetime        not null,
    TimestampModified     datetime        null,
    Version               int             null,
    CollectionMemberID    int             not null,
    CollectionCode        varchar(64)     null,
    InstitutionCode       varchar(64)     null,
    Integer1              int             null,
    Integer2              int             null,
    Integer3              int             null,
    Number1               decimal(20, 10) null,
    Number2               decimal(20, 10) null,
    Number3               decimal(20, 10) null,
    Remarks               text            null,
    Text1                 text            null,
    Text2                 text            null,
    Text3                 text            null,
    UrlLink               varchar(1024)   null,
    VoucherNumber         varchar(256)    null,
    YesNo1                bit             null,
    YesNo2                bit             null,
    YesNo3                bit             null,
    ModifiedByAgentID     int             null,
    CollectionObjectID    int             not null,
    CreatedByAgentID      int             null,
    constraint FKE5366FE65327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FKE5366FE675E37458
        foreign key (CollectionObjectID) references casiz.collectionobject (CollectionObjectID),
    constraint FKE5366FE67699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.workbenchtemplate
(
    WorkbenchTemplateID int auto_increment
        primary key,
    TimestampCreated    datetime     not null,
    TimestampModified   datetime     null,
    Version             int          null,
    Name                varchar(256) null,
    Remarks             text         null,
    SrcFilePath         varchar(255) null,
    ModifiedByAgentID   int          null,
    CreatedByAgentID    int          null,
    SpecifyUserID       int          not null,
    constraint FK6F902B394BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK6F902B395327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6F902B397699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID)
)
    charset = utf8mb3;

create table casiz.spreport
(
    SpReportId          int auto_increment
        primary key,
    TimestampCreated    datetime     not null,
    TimestampModified   datetime     null,
    Version             int          null,
    Name                varchar(64)  not null,
    Remarks             text         null,
    RepeatCount         int          null,
    RepeatField         varchar(255) null,
    ModifiedByAgentID   int          null,
    AppResourceID       int          not null,
    SpecifyUserID       int          not null,
    WorkbenchTemplateID int          null,
    SpQueryID           int          null,
    CreatedByAgentID    int          null,
    constraint FK972D69D12774AC79
        foreign key (AppResourceID) references casiz.spappresource (SpAppResourceID),
    constraint FK972D69D14BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK972D69D15327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK972D69D17699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK972D69D17F5EBA2A
        foreign key (WorkbenchTemplateID) references casiz.workbenchtemplate (WorkbenchTemplateID),
    constraint FK972D69D1B273544E
        foreign key (SpQueryID) references casiz.spquery (SpQueryID)
)
    charset = utf8mb3;

create index SpReportNameIDX
    on casiz.spreport (Name);

create table casiz.workbench
(
    WorkbenchID           int auto_increment
        primary key,
    TimestampCreated      datetime     not null,
    TimestampModified     datetime     null,
    Version               int          null,
    AllPermissionLevel    int          null,
    TableID               int          null,
    ExportInstitutionName varchar(128) null,
    ExportedFromTableName varchar(128) null,
    FormId                int          null,
    GroupPermissionLevel  int          null,
    LockedByUserName      varchar(64)  null,
    Name                  varchar(256) null,
    OwnerPermissionLevel  int          null,
    Remarks               text         null,
    SrcFilePath           varchar(255) null,
    CreatedByAgentID      int          null,
    WorkbenchTemplateID   int          not null,
    SpecifyUserID         int          not null,
    SpPrincipalID         int          null,
    ModifiedByAgentID     int          null,
    constraint FK41238DBF4BDD9E10
        foreign key (SpecifyUserID) references casiz.specifyuser (SpecifyUserID),
    constraint FK41238DBF5327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK41238DBF7699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK41238DBF7F5EBA2A
        foreign key (WorkbenchTemplateID) references casiz.workbenchtemplate (WorkbenchTemplateID),
    constraint FK41238DBF99A7381A
        foreign key (SpPrincipalID) references casiz.spprincipal (SpPrincipalID)
)
    charset = utf8mb3;

create index WorkbenchNameIDX
    on casiz.workbench (Name);

create table casiz.workbenchrow
(
    WorkbenchRowID      int auto_increment
        primary key,
    BioGeomancerResults text            null,
    CardImageData       mediumblob      null,
    CardImageFullPath   varchar(255)    null,
    Lat1Text            varchar(50)     null,
    Lat2Text            varchar(50)     null,
    Long1Text           varchar(50)     null,
    Long2Text           varchar(50)     null,
    RecordID            int             null,
    RowNumber           smallint        null,
    SGRStatus           tinyint         null,
    UploadStatus        tinyint         null,
    WorkbenchID         int             not null,
    ErrorEstimate       decimal(20, 10) null,
    ErrorPolygon        text            null,
    constraint FK486DDFBBBBCF9E96
        foreign key (WorkbenchID) references casiz.workbench (WorkbenchID)
)
    charset = utf8mb3;

create index RowNumberIDX
    on casiz.workbenchrow (RowNumber);

create table casiz.workbenchrowexportedrelationship
(
    WorkbenchRowExportedRelationshipID int auto_increment
        primary key,
    TimestampCreated                   datetime     not null,
    TimestampModified                  datetime     null,
    Version                            int          null,
    RecordID                           int          null,
    RelationshipName                   varchar(120) null,
    Sequence                           int          null,
    TableName                          varchar(120) null,
    WorkbenchRowID                     int          not null,
    ModifiedByAgentID                  int          null,
    CreatedByAgentID                   int          null,
    constraint FK6829C9465327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK6829C9467699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK6829C946C66EB2D4
        foreign key (WorkbenchRowID) references casiz.workbenchrow (WorkbenchRowID)
)
    charset = utf8mb3;

create table casiz.workbenchrowimage
(
    WorkbenchRowImageID int auto_increment
        primary key,
    AttachToTableName   varchar(64)  null,
    CardImageData       mediumblob   null,
    CardImageFullPath   varchar(255) null,
    ImageOrder          int          null,
    WorkbenchRowID      int          not null,
    constraint FKC17A6680C66EB2D4
        foreign key (WorkbenchRowID) references casiz.workbenchrow (WorkbenchRowID)
)
    charset = utf8mb3;

create table casiz.workbenchtemplatemappingitem
(
    WorkbenchTemplateMappingItemID int auto_increment
        primary key,
    TimestampCreated               datetime     not null,
    TimestampModified              datetime     null,
    Version                        int          null,
    XCoord                         smallint     null,
    YCoord                         smallint     null,
    Caption                        varchar(64)  null,
    CarryForward                   bit          null,
    DataFieldLength                smallint     null,
    FieldName                      varchar(255) null,
    FieldType                      smallint     null,
    ImportedColName                varchar(255) null,
    IsEditable                     bit          null,
    IsExportableToContent          bit          null,
    IsIncludedInTitle              bit          null,
    IsRequired                     bit          null,
    MetaData                       varchar(128) null,
    DataColumnIndex                smallint     null,
    TableId                        int          null,
    TableName                      varchar(64)  null,
    ViewOrder                      smallint     null,
    ModifiedByAgentID              int          null,
    CreatedByAgentID               int          null,
    WorkbenchTemplateID            int          not null,
    constraint FK7D6D44085327F942
        foreign key (ModifiedByAgentID) references casiz.agent (AgentID),
    constraint FK7D6D44087699B003
        foreign key (CreatedByAgentID) references casiz.agent (AgentID),
    constraint FK7D6D44087F5EBA2A
        foreign key (WorkbenchTemplateID) references casiz.workbenchtemplate (WorkbenchTemplateID)
)
    charset = utf8mb3;

create table casiz.workbenchdataitem
(
    WorkbenchDataItemID            int auto_increment
        primary key,
    CellData                       text     null,
    RowNumber                      smallint null,
    ValidationStatus               smallint null,
    WorkbenchTemplateMappingItemID int      not null,
    WorkbenchRowID                 int      not null,
    constraint FK2901E47C688C522E
        foreign key (WorkbenchTemplateMappingItemID) references casiz.workbenchtemplatemappingitem (WorkbenchTemplateMappingItemID),
    constraint FK2901E47CC66EB2D4
        foreign key (WorkbenchRowID) references casiz.workbenchrow (WorkbenchRowID)
)
    charset = utf8mb3;

create index DataItemRowNumberIDX
    on casiz.workbenchdataitem (RowNumber);

-- Cyclic dependencies found

alter table casiz.agent
    add constraint FK58743054834EDBB
        foreign key (InstitutionTCID) references casiz.institutionnetwork (InstitutionNetworkID);

alter table casiz.agent
    add constraint FK587430587F159B7
        foreign key (InstitutionTCID) references casiz.institution (UserGroupScopeId);

