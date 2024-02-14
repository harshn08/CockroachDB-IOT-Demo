import psycopg2
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta

# Connect to CockroachDB
conn = psycopg2.connect(
    database="",
    user="",
    password="",
    host="",
    port="26257"
)

# Create a cursor object
cursor = conn.cursor()

fake = Faker('en_US')

# Function to generate a random UUID
def generate_uuid():
    return str(uuid.uuid4())

# Function to generate random latitude and longitude within the continental United States
def generate_latitude_longitude():
    # Continental United States bounds
    min_lat, max_lat = 24.396308, 49.384358
    min_lon, max_lon = -125.0, -66.93457
    return random.uniform(min_lat, max_lat), random.uniform(min_lon, max_lon)


# Function to generate random date within the last 6 months
def generate_random_date(start_date, end_date):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 6 months ago
    return fake.date_time_between_dates(datetime_start=start_date, datetime_end=end_date)

# Function to generate data for Fleet table
def generate_fleet_data(num_fleets):
    fleets = []
    for _ in range(num_fleets):
        fleet_id = generate_uuid()
        fleet_name = fake.company()
        fleet_size = random.randint(10, 100)
        fleets.append((fleet_id, fleet_name, fleet_size))
    return fleets

# Function to generate data for Vehicle table
def generate_vehicle_data(num_vehicles, fleets):
    vehicles = []
    vehicle_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 'Audi', 'Volkswagen', 'Tesla']
    maintenance_tasks = ["Oil Change", "Brake Replacement", "Transmission Service", "Tire Rotation", "Engine Tune-up"]
    for _ in range(num_vehicles):
        vehicle_id = generate_uuid()
        fleet_id = random.choice(fleets)[0]
        vin = fake.hexify(text='^^^^^^^######')
        make = random.choice(vehicle_makes)
        model = fake.random_element(elements=('car', 'truck', 'van'))
        year = random.randint(2000, 2023)
        last_service_date = generate_random_date(datetime(2019, 1, 1), datetime.now())
        next_service_date = last_service_date + timedelta(days=random.randint(30, 180))
        last_maintenance_task = random.choice(maintenance_tasks)
        last_maintenance_date = generate_random_date(datetime(2019, 1, 1), datetime.now())
        current_odometer_reading = random.uniform(0, 200000)
        latitude, longitude = generate_latitude_longitude()
        vehicles.append((vehicle_id, fleet_id, vin, make, model, year, last_service_date, next_service_date,
                         last_maintenance_task, last_maintenance_date, current_odometer_reading, latitude, longitude))
    return vehicles

# Function to generate data for Diagnostic table
def generate_diagnostic_data(num_diagnostics, vehicles):
    diagnostics = []
    for _ in range(num_diagnostics):
        diagnostic_id = generate_uuid()
        vehicle_id = random.choice(vehicles)[0]
        timestamp = generate_random_date(datetime(2020, 1, 1), datetime.now())
        engine_temperature = random.uniform(50, 120)
        oil_pressure = random.uniform(10, 80)
        fuel_level = random.uniform(0, 100)
        tire_pressure = random.uniform(25, 40)
        engine_rpm = random.randint(500, 4000)
        transmission_fluid_level = random.uniform(0, 100)
        battery_voltage = random.uniform(10, 16)
        diagnostics.append((diagnostic_id, vehicle_id, timestamp, engine_temperature, oil_pressure, fuel_level,
                            tire_pressure, engine_rpm, transmission_fluid_level, battery_voltage))
    return diagnostics

# Function to generate data for MaintenanceSchedule table
def generate_maintenance_schedule_data(vehicles):
    maintenance_schedules = []
    maintenance_tasks = ["Oil Change", "Brake Replacement", "Transmission Service", "Tire Rotation", "Engine Tune-up"]
    for vehicle in vehicles:
        schedule_id = generate_uuid()
        vehicle_id = vehicle[0]
        task = random.choice(maintenance_tasks)
        frequency = timedelta(days=random.randint(30, 180))
        last_performed = generate_random_date(datetime(2019, 1, 1), datetime.now())
        next_due = last_performed + frequency
        maintenance_schedules.append((schedule_id, vehicle_id, task, frequency, last_performed, next_due))
    return maintenance_schedules

# Sample data generation
num_fleets = 3
num_vehicles = 50
num_diagnostics = 500

fleets = generate_fleet_data(num_fleets)
vehicles = generate_vehicle_data(num_vehicles, fleets)
diagnostics = generate_diagnostic_data(num_diagnostics, vehicles)
maintenance_schedules = generate_maintenance_schedule_data(vehicles)

# Insert data into Fleet table
cursor.executemany("INSERT INTO movr_demo.public.Fleet (FleetID, FleetName, FleetSize) VALUES (%s, %s, %s)", fleets)

# Insert data into Vehicle table
cursor.executemany("INSERT INTO movr_demo.public.Vehicle (VehicleID, FleetID, VIN, Make, Model, Year, LastServiceDate, NextServiceDate, LastMaintenanceTask, LastMaintenanceDate, CurrentOdometerReading, Latitude, Longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", vehicles)

# Insert data into Diagnostic table
cursor.executemany("INSERT INTO movr_demo.public.Diagnostic (DiagnosticID, VehicleID, Timestamp, EngineTemperature, OilPressure, FuelLevel, TirePressure, EngineRPM, TransmissionFluidLevel, BatteryVoltage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", diagnostics)

# Insert data into MaintenanceSchedule table
cursor.executemany("INSERT INTO movr_demo.public.MaintenanceSchedule (ScheduleID, VehicleID, Task, Frequency, LastPerformed, NextDue) VALUES (%s, %s, %s, %s, %s, %s)", maintenance_schedules)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
