#!/usr/bin/env python3
"""
Quick API Test - Uses onboarded user from onboard_users.py
Run this for a quick test of vehicle CRUD, telemetry, and alerts
"""

import requests
import json
from datetime import datetime
import random

BASE_URL = "https://api-swadeshiapp.onrender.com"
# BASE_URL = "http://localhost:8000"  # Uncomment for local

# Use the onboarded user credentials
PHONE = "6360091227"
PASSWORD = "Vishwas@5610"

def print_step(step, title):
    print(f"\n{'='*60}")
    print(f"[{step}] {title}")
    print(f"{'='*60}")

def print_result(success, data=None):
    if success:
        print(f"✅ SUCCESS")
        if data:
            print(json.dumps(data, indent=2))
    else:
        print(f"❌ FAILED: {data}")

# Step 1: Login
print_step(1, "LOGIN OR REGISTER")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": PHONE, "password": PASSWORD}
    )
    if response.status_code == 200:
        print("Logged in successfully")
    else:
        print("Login failed, registering new user...")
        reg_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "user_id": f"u_{int(datetime.now().timestamp() * 1000)}",
                "phone": PHONE,
                "password": PASSWORD,
                "name": "Quick Test User",
                "email": f"test_{int(datetime.now().timestamp())}@example.com"
            }
        )
        if reg_response.status_code == 200:
             print("Registered successfully")
             # Login again to get token/user object if needed (though register returns user object)
             response = reg_response
        else:
             print_result(False, reg_response.text)
             exit(1)
except Exception as e:
    print_result(False, str(e))
    exit(1)

user_data = response.json()
user_id = user_data['user_id']
existing_vehicles = user_data.get('vehicles', [])
print_result(True, {"user_id": user_id, "vehicle_count": len(existing_vehicles)})

# Get first vehicle ID if exists
vehicle_id = existing_vehicles[0]['vehicle_id'] if existing_vehicles else None

# Step 2: Add New Vehicle
print_step(2, "ADD NEW VEHICLE")
new_vehicle = {
    "vehicle_id": f"test_veh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "owner_id": user_id,
    "make": "Maruti",
    "model": "Swift",
    "year": 2023,
    "registration_number": f"KA 02 TEST {random.randint(1000, 9999)}",
    "fuel_type": "PETROL",
    "insurance_expiry": "2025-12-31",
    "last_service": "2024-01-15"
}
response = requests.post(f"{BASE_URL}/vehicle", json=new_vehicle)
if response.status_code == 200:
    test_vehicle = response.json()
    test_vehicle_id = test_vehicle['vehicle_id']
    print_result(True, test_vehicle)
else:
    print_result(False, response.text)
    test_vehicle_id = vehicle_id

# Step 3: Get Vehicle Details
print_step(3, "GET VEHICLE DETAILS")
response = requests.get(f"{BASE_URL}/vehicle/{test_vehicle_id}")
print_result(response.status_code == 200, response.json() if response.status_code == 200 else response.text)

# Step 4: Update Vehicle
print_step(4, "UPDATE VEHICLE")
update_data = response.json() if response.status_code == 200 else new_vehicle
update_data['insurance_expiry'] = "2026-12-31"
update_data['last_service'] = datetime.now().strftime("%Y-%m-%d")
response = requests.put(f"{BASE_URL}/vehicle/{test_vehicle_id}", json=update_data)
print_result(response.status_code == 200, response.json() if response.status_code == 200 else response.text)

# Step 5: Upload Telemetry (Single)
print_step(5, "UPLOAD TELEMETRY")
telemetry = {
    "vehicle_id": test_vehicle_id,
    "timestamp": datetime.now().isoformat(),
    "speed": round(random.uniform(40, 120), 2),
    "latitude": 12.9716 + random.uniform(-0.1, 0.1),
    "longitude": 77.5946 + random.uniform(-0.1, 0.1),
    "battery_level": round(random.uniform(20, 100), 2)
}
response = requests.post(f"{BASE_URL}/telemetry", json=telemetry)
print_result(response.status_code == 200, response.json() if response.status_code == 200 else response.text)

# Step 6: Upload Bulk Telemetry
print_step(6, "UPLOAD BULK TELEMETRY (5 records)")
success_count = 0
for i in range(5):
    telemetry = {
        "vehicle_id": test_vehicle_id,
        "timestamp": datetime.now().isoformat(),
        "speed": round(random.uniform(40, 120), 2),
        "latitude": 12.9716 + random.uniform(-0.1, 0.1),
        "longitude": 77.5946 + random.uniform(-0.1, 0.1),
        "battery_level": round(random.uniform(20, 100), 2)
    }
    response = requests.post(f"{BASE_URL}/telemetry", json=telemetry)
    if response.status_code == 200:
        success_count += 1
print(f"✅ Uploaded {success_count}/5 telemetry records")

# Step 7: Create Alerts
print_step(7, "CREATE ALERTS")
alert_types = [
    ("RASH_DRIVING", "High", "Harsh braking detected at 85 km/h"),
    ("MAINTENANCE", "Medium", "Service due in 500 km"),
    ("INFO", "Low", "Battery level normal - 85%")
]

for alert_type, severity, message in alert_types:
    alert = {
        "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
        "vehicle_id": test_vehicle_id,
        "type": alert_type,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "location": "Bangalore, India",
        "is_actioned": False,
        "icon": "warning",
        "color": "0xFFD32F2F",
        "bg_color": "0xFFFFCDD2"
    }
    response = requests.post(f"{BASE_URL}/alert", json=alert)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"{status} {alert_type}: {message}")

# Step 8: Get All Alerts
print_step(8, "GET ALL ALERTS")
response = requests.get(f"{BASE_URL}/alerts/{test_vehicle_id}")
if response.status_code == 200:
    alerts = response.json()
    print(f"✅ Found {len(alerts)} alerts")
    for alert in alerts[:3]:  # Show first 3
        print(f"  - [{alert['severity']}] {alert['type']}: {alert['message']}")
else:
    print_result(False, response.text)

# Step 9: List All Vehicles
print_step(9, "LIST ALL USER VEHICLES")
response = requests.get(f"{BASE_URL}/user/{user_id}")
if response.status_code == 200:
    user_data = response.json()
    vehicles = user_data.get('vehicles', [])
    print(f"✅ User has {len(vehicles)} vehicle(s)")
    for v in vehicles:
        print(f"  - {v['make']} {v['model']} ({v['registration_number']})")
else:
    print_result(False, response.text)

# Step 10: Delete Test Vehicle
# print_step(10, "DELETE TEST VEHICLE")
# response = requests.delete(f"{BASE_URL}/vehicle/{test_vehicle_id}")
# print_result(response.status_code == 200, {"message": "Vehicle deleted"} if response.status_code == 200 else response.text)

# Step 11: Final Vehicle Count
print_step(11, "FINAL VEHICLE COUNT")
response = requests.get(f"{BASE_URL}/user/{user_id}")
if response.status_code == 200:
    user_data = response.json()
    vehicles = user_data.get('vehicles', [])
    print(f"✅ User now has {len(vehicles)} vehicle(s)")
else:
    print_result(False, response.text)

print("\n" + "="*60)
print("  ✅ ALL TESTS COMPLETED!")
print("="*60 + "\n")
