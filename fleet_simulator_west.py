import psycopg2
import random
import math
import time
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Function to establish database connection
def connect_to_database():
    try:
        connection = psycopg2.connect(
            database="",
            user="",
            password="",
            host="",
            port="26257"
        )
        return connection
    except Exception as e:
        print("Error:", e)
        return None

# Function to close database connection
def close_connection(connection):
    if connection:
        connection.close()

# Function to generate random latitude and longitude within the continental United States
def generate_latitude_longitude():
    min_lat, max_lat = 24.396308, 49.384358  # Range for latitude (continental U.S.)
    min_long, max_long = -125.0, -110.0    # Range for longitude (continental U.S.)
    latitude = random.uniform(min_lat, max_lat)
    longitude = random.uniform(min_long, max_long)
    return latitude, longitude

# Function to calculate the distance between two points using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance

# Function to simulate vehicle movement and update data in the database
def simulate_vehicle_movement(connection, cursor, vehicle, start_time, end_time):
    current_time = start_time
    last_lat = vehicle['Latitude']
    last_long = vehicle['Longitude']
    while current_time <= end_time:
        # Generate new latitude and longitude
        new_lat, new_long = generate_latitude_longitude()

        # Calculate distance from last location
        last_lat_float = float(last_lat)
        last_long_float = float(last_long)
        new_lat_float = float(new_lat)
        new_long_float = float(new_long)

        distance = calculate_distance(last_lat_float, last_long_float, new_lat_float, new_long_float)


        # If distance exceeds 25 miles, limit movement to 25 miles
        if distance > 25:
            ratio = 25 / distance
            new_lat = last_lat + (new_lat - last_lat) * ratio
            new_long = last_long + (new_long - last_long) * ratio

        # Limit movement to the continental United States
        min_lat, max_lat = 24.396308, 49.384358  # Range for latitude (continental U.S.)
        min_long, max_long = -125.0, -110.0    # Range for longitude (continental U.S.)
        new_lat = max(min(new_lat, max_lat), min_lat)
        new_long = max(min(new_long, max_long), min_long)
        
        # Update last location
        last_lat = new_lat
        last_long = new_long

        # Simulate diagnostic data
        vehicle['Timestamp'] = current_time
        vehicle['Latitude'] = new_lat
        vehicle['Longitude'] = new_long
        vehicle['EngineTemperature'] = random.uniform(50, 120)
        vehicle['OilPressure'] = random.uniform(10, 80)
        vehicle['FuelLevel'] = random.uniform(0, 100)
        vehicle['TirePressure'] = random.uniform(25, 40)
        vehicle['EngineRPM'] = random.randint(500, 4000)
        vehicle['TransmissionFluidLevel'] = random.uniform(0, 100)
        vehicle['BatteryVoltage'] = random.uniform(10, 16)

        # Update database with simulated data
        update_vehicle_data(connection, cursor, vehicle)

        # Update LocationHistory table
        update_location_history(connection, cursor, vehicle)

        # Print updated data
        print("Time:", current_time)
        print("Vehicle ID:", vehicle['VehicleID'])
        print("Location: Lat={}, Long={}".format(vehicle['Latitude'], vehicle['Longitude']))
        print("Diagnostics:", vehicle['EngineTemperature'], vehicle['OilPressure'], vehicle['FuelLevel'], vehicle['TirePressure'],
              vehicle['EngineRPM'], vehicle['TransmissionFluidLevel'], vehicle['BatteryVoltage'])
        print()

        # Sleep for a random interval to simulate time passing
        time.sleep(random.uniform(0.75, 2))

        # Increment current time
        current_time += timedelta(minutes=random.randint(5, 30))

# Function to update vehicle data in the database
def update_vehicle_data(connection, cursor, vehicle):
    try:
        # Update Vehicle table
        cursor.execute("""
            UPDATE Vehicle 
            SET Latitude = %s, Longitude = %s 
            WHERE VehicleID = %s
        """, (vehicle['Latitude'], vehicle['Longitude'], vehicle['VehicleID']))

        # Insert into Diagnostic table
        cursor.execute("""
            INSERT INTO Diagnostic (VehicleID, Timestamp, EngineTemperature, OilPressure, FuelLevel, TirePressure, 
                                   EngineRPM, TransmissionFluidLevel, BatteryVoltage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (vehicle['VehicleID'], vehicle['Timestamp'], vehicle['EngineTemperature'], vehicle['OilPressure'],
              vehicle['FuelLevel'], vehicle['TirePressure'], vehicle['EngineRPM'],
              vehicle['TransmissionFluidLevel'], vehicle['BatteryVoltage']))

        # Commit the transaction
        connection.commit()

    except Exception as e:
        print("Error:", e)
        connection.rollback()

# Function to update LocationHistory table
def update_location_history(connection, cursor, vehicle):
    try:
        # Insert into LocationHistory table
        cursor.execute("""
            INSERT INTO LocationHistory (VehicleID, Timestamp, Latitude, Longitude)
            VALUES (%s, %s, %s, %s)
        """, (vehicle['VehicleID'], vehicle['Timestamp'], vehicle['Latitude'], vehicle['Longitude']))

        # Commit the transaction
        connection.commit()

    except Exception as e:
        print("Error:", e)
        connection.rollback()

# Function to fetch vehicles from the database
def fetch_vehicles(connection, cursor):
    try:
        cursor.execute("SELECT * FROM Vehicle where FleetID = '9e3f2a0f-e8c6-4f04-acce-718975fce43d'")
        vehicles = cursor.fetchall()
        
        # Convert fetched data into list of dictionaries
        vehicles_list = []
        for vehicle_tuple in vehicles:
            vehicle_dict = {
            'VehicleID': vehicle_tuple[0],
            'FleetID': vehicle_tuple[1],
            'VIN': vehicle_tuple[2],
            'Make': vehicle_tuple[3],
            'Model': vehicle_tuple[4],
            'Year': vehicle_tuple[5],
            'LastServiceDate': vehicle_tuple[6],
            'NextServiceDate': vehicle_tuple[7],
            'LastMaintenanceTask': vehicle_tuple[8],
            'LastMaintenanceDate': vehicle_tuple[9],
            'CurrentOdometerReading': vehicle_tuple[10],
            'Latitude': vehicle_tuple[11],
            'Longitude': vehicle_tuple[12],
            # Add other attributes as needed
        }

            vehicles_list.append(vehicle_dict)
            
        return vehicles_list
    except Exception as e:
        print("Error:", e)
        return []

# Start and end time for simulation
start_time = datetime(2024, 1, 5, 8, 0, 0)
end_time = datetime(2024, 1, 5, 17, 0, 0)

# Connect to the database
connection = connect_to_database()
cursor = connection.cursor()

# Fetch vehicles from the database
vehicles = fetch_vehicles(connection, cursor)

# Run simulation for each vehicle
for vehicle in vehicles:
    simulate_vehicle_movement(connection, cursor, vehicle, start_time, end_time)

# Close database connection
close_connection(connection)
