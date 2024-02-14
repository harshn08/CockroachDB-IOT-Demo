DROP DATABASE IF EXISTS movr_demo;
CREATE DATABASE movr_demo;

ALTER DATABASE movr_demo SET PRIMARY REGION = "gcp-us-central1";

ALTER DATABASE movr_demo SURVIVE REGION FAILURE;

CREATE TABLE IF NOT EXISTS movr_demo.public.Fleet (
    FleetID UUID PRIMARY KEY,
    FleetName VARCHAR(100),
    FleetSize INT
);

ALTER TABLE movr_demo.public.Fleet SET LOCALITY GLOBAL;

CREATE TABLE IF NOT EXISTS movr_demo.public.Vehicle (
    VehicleID UUID PRIMARY KEY,
    FleetID UUID REFERENCES movr_demo.public.Fleet(FleetID),
    VIN VARCHAR(17) UNIQUE NOT NULL,
    Make VARCHAR(50),
    Model VARCHAR(50),
    Year INT,
    LastServiceDate DATE,
    NextServiceDate DATE,
    LastMaintenanceTask VARCHAR(100),
    LastMaintenanceDate DATE,
    CurrentOdometerReading FLOAT,
    Latitude FLOAT,
    Longitude FLOAT,
    CHECK (CurrentOdometerReading >= 0)
);

ALTER TABLE movr_demo.public.Vehicle SET LOCALITY REGIONAL BY TABLE IN PRIMARY REGION;

CREATE TABLE IF NOT EXISTS movr_demo.public.LocationHistory (
    LocationID UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    VehicleID UUID REFERENCES movr_demo.public.Vehicle(VehicleID),
    Timestamp TIMESTAMP DEFAULT now(),
    Latitude FLOAT,
    Longitude FLOAT
)LOCALITY REGIONAL BY ROW;


CREATE TABLE IF NOT EXISTS movr_demo.public.Diagnostic (
    DiagnosticID UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    VehicleID UUID REFERENCES movr_demo.public.Vehicle(VehicleID),
    Timestamp TIMESTAMP DEFAULT now(),
    EngineTemperature FLOAT,
    OilPressure FLOAT,
    FuelLevel FLOAT,
    TirePressure FLOAT,
    EngineRPM INT,
    TransmissionFluidLevel FLOAT,
    BatteryVoltage FLOAT,
    CHECK (EngineTemperature >= 0 AND OilPressure >= 0 AND FuelLevel >= 0 AND TirePressure >= 0 AND EngineRPM >= 0 AND TransmissionFluidLevel >= 0 AND BatteryVoltage >= 0)
)LOCALITY REGIONAL BY ROW;

CREATE TABLE IF NOT EXISTS movr_demo.public.MaintenanceSchedule (
    ScheduleID UUID PRIMARY KEY,
    VehicleID UUID REFERENCES movr_demo.public.Vehicle(VehicleID),
    Task VARCHAR(100),
    Frequency INTERVAL,
    LastPerformed TIMESTAMP,
    NextDue TIMESTAMP
);

ALTER TABLE movr_demo.public.MaintenanceSchedule SET LOCALITY GLOBAL;
