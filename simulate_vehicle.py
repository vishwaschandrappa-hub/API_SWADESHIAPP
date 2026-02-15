import requests
import time
import random
from datetime import datetime

BACKEND_URL = "http://localhost:8000/ingest/telemetry"
VEHICLE_ID = "KA05MN2024"

def generate_telemetry():
    return {
        "vehicle_id": VEHICLE_ID,
        "timestamp": datetime.now().isoformat(),
        "speed": random.uniform(0, 140), # Simulate occasional overspeeding
        "rpm": random.uniform(1000, 4000),
        "latitude": 12.9716 + random.uniform(-0.01, 0.01),
        "longitude": 77.5946 + random.uniform(-0.01, 0.01),
        "fuel_level": random.uniform(10, 100),
        "battery_level": random.uniform(10, 100),
        "engine_temp": random.uniform(80, 110), # Simulate overheating
        "accelerometer": {
            "x": random.uniform(-2, 2),
            "y": random.uniform(-2, 2),
            "z": random.uniform(8, 20) # Simulate harsh bumps
        }
    }

def main():
    print(f"Starting simulation for vehicle: {VEHICLE_ID}")
    while True:
        data = generate_telemetry()
        try:
            response = requests.post(BACKEND_URL, json=data)
            if response.status_code == 200:
                print(f"Sent data: Speed={data['speed']:.1f} | Alerts={response.json().get('alerts_generated')}")
            else:
                print(f"Failed to send data: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to backend: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    main()
