-- AgentDemo.dbo.PatientMLDataset definition

-- Drop table

-- DROP TABLE AgentDemo.dbo.PatientMLDataset;

CREATE TABLE AgentDemo.dbo.PatientMLDataset (
	patient_id int IDENTITY(1,1) NOT NULL,
	age tinyint NOT NULL,
	sex tinyint NOT NULL,
	heart_rate smallint NULL,
	bp_systolic smallint NULL,
	bp_diastolic smallint NULL,
	wbc int NULL,
	platelets int NULL,
	fever bit NULL,
	muscle_pain bit NULL,
	jaundice bit NULL,
	vomiting bit NULL,
	confusion bit NULL,
	headache bit NULL,
	chills bit NULL,
	rigors bit NULL,
	nausea bit NULL,
	diarrhea bit NULL,
	cough bit NULL,
	bleeding bit NULL,
	prostration bit NULL,
	oliguria bit NULL,
	anuria bit NULL,
	conjunctival_suffusion bit NULL,
	muscle_tenderness bit NULL,
	diagnosis tinyint NOT NULL,
	CONSTRAINT PK_PatientMLDataset PRIMARY KEY (patient_id)
);