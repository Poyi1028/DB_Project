CREATE DATABASE mydb;
SHOW DATABASES;
USE mydb;

SHOW TABLES;
SELECT * FROM user;

CREATE TABLE equipment(
	Equipment_ID INT NOT NULL PRIMARY KEY,
    Name Varchar(45) NOT NULL,
    Training_Detail VARCHAR(45) NOT NULL,
    Traing_Area VARCHAR(45) NOT NULL
);

CREATE TABLE daily_plan(
	Daily_Plan_ID INT NOT NULL PRIMARY KEY,
    Traing_Area VARCHAR(45) NOT NULL,
    Equipment_ID INT NOT NULL
);

CREATE TABLE equipment_training_area(
	Equipment_ID INT NOT NULL PRIMARY KEY,
    Trainging_Area VARCHAR(45) NOT NULL
);

CREATE TABLE equipment_trainging_detail(
	Equipment_ID INT NOT NULL PRIMARY KEY,
    Training_Detail VARCHAR(45) NULL DEFAULT NULL
);

CREATE TABLE fitness_goal(
	Goal_ID INT NOT NULL PRIMARY KEY,
	Fat_Weight DECIMAL(10,0) NULL DEFAULT NULL,
	Protein_Weight DECIMAL(10,0) NULL DEFAULT NULL,
	Carbohydrate_Weight DECIMAL(10,0) NULL DEFAULT NULL
);

CREATE TABLE gym(
	Gym_ID INT NOT NULL PRIMARY KEY,
	Equipment_ID INT NOT NULL,
	Address VARCHAR(45) NULL DEFAULT NULL,
	Name VARCHAR(45) NULL DEFAULT NULL
);
  
CREATE TABLE inbody_detail(
	Inbody_ID INT NOT NULL PRIMARY KEY,
	User_ID INT NULL DEFAULT NULL,
	Age INT NULL DEFAULT NULL,
	Gender INT NULL DEFAULT NULL,
	PBF DECIMAL(10,0) NULL DEFAULT NULL,
	SMM DECIMAL(10,0) NULL DEFAULT NULL, 
	Weight DECIMAL(10,0) NULL DEFAULT NULL,
	Height DECIMAL(10,0) NULL DEFAULT NULL
);

CREATE TABLE nutrient_supplement_recommendation(
	Inbody_ID INT NOT NULL,
	Goal_ID INT NOT NULL,
	User_ID INT NOT NULL,
	Date DATETIME NOT NULL,
	Protein_Intake_Suggestion DECIMAL(10,0) NOT NULL,
	Fat_Intake_Suggestion DECIMAL(10,0) NOT NULL,
	Carbonhydrate_Intake_Suggestion DECIMAL(10,0) NOT NULL,
	Calories_Intake_Suggestion DECIMAL(10,0) NOT NULL,
	Water_Intake_Suggestion DECIMAL(10,0) NOT NULL,
    PRIMARY KEY (Inbody_ID, Goal_ID)
);

CREATE TABLE nutrient_supplement_tracking(
	Nutrients_ID INT NOT NULL PRIMARY KEY,
	Protein_Intake DECIMAL(10,0) NULL DEFAULT NULL,
	Fat_Intake DECIMAL(10,0) NULL DEFAULT NULL,
	Carbonhydrate_Intake DECIMAL(10,0) NULL DEFAULT NULL,
	Water_Intake DECIMAL(10,0) NULL DEFAULT NULL,
	Calaries_Intake DECIMAL(10,0) NULL DEFAULT NULL,
	User_ID INT NULL DEFAULT NULL
);

CREATE TABLE scheduled(
	Plan_ID INT NOT NULL,
    User_ID INT NOT NULL,
    Training_Area VARCHAR(45) NOT NULL,
    Object VARCHAR(45) NOT NULL,
    PRIMARY KEY (User_ID, Plan_ID)
);

CREATE TABLE user(
	User_ID INT NOT NULL PRIMARY KEY,
    User_Type VARCHAR(45) NULL DEFAULT NULL,
    Password INT NULL DEFAULT NULL,
    Name VARCHAR(45) NULL DEFAULT NULL
);

CREATE TABLE user_plan(
	Plan_ID INT NOT NULL PRIMARY KEY,
	User_ID INT NOT NULL,
	Tracking_Date DATETIME NOT NULL,
	Training_List VARCHAR(45) NOT NULL,
	Daily_Plan_ID INT NOT NULL,
	User_Plan_Object VARCHAR(45) NULL DEFAULT NULL,
	Equipment_ID INT NOT NULL,
    INDEX Equipment_ID_idx (`Equipment_ID` ASC) VISIBLE
);

CREATE TABLE user_plan_object(
	Plan_ID INT NOT NULL PRIMARY KEY,
    Object VARCHAR(45) NULL DEFAULT NULL
);