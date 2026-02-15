import requests
import time
import random
import json
from datetime import datetime

# Configuration
BASE_URL = "https://api-swadeshiapp.onrender.com"
# BASE_URL = "http://localhost:8000"  # Uncomment for local

# User Credentials (UPDATE THESE IF NEEDED)
PHONE = "6360091227" 
PASSWORD = "Vishwas@5610"

def main():
    print("🚗 SWADESHI TELEMETRY SIMULATOR 🚗")
    print("-" * 40)

    # 1. Login
    print(f"Logging in as {PHONE}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"phone": PHONE, "password": PASSWORD}
        )
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        user_data = response.json()
        print(f"✅ Logged in as {user_data['name']}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Select Vehicle
    vehicles = user_data.get('vehicles', [])
    if not vehicles:
        print("❌ No vehicles found for this user.")
        return

    print("\nSelect a vehicle to simulate:")
    for i, v in enumerate(vehicles):
        print(f"[{i+1}] {v['make']} {v['model']} ({v['registration_number']})")

    try:
        choice = int(input("\nEnter choice (1-{}): ".format(len(vehicles)))) - 1
        curr_vehicle = vehicles[choice]
    except (ValueError, IndexError):
        print("Invalid choice. Using first vehicle.")
        curr_vehicle = vehicles[0]

    vid = curr_vehicle['vehicle_id']
    print(f"\n✅ Simulating data for: {curr_vehicle['make']} {curr_vehicle['model']} ({vid})")
    print("Press Ctrl+C to stop.\n")

    # 3. Simulation Loop
    lat = 12.9716
    lng = 77.5946
    speed = 0.0
    battery = 80.0
    fuel = 65.0
    
    try:
        while True:
            # Simulate driving
            speed = max(0, min(120, speed + random.uniform(-10, 10))) # Change speed randomly
            lat += random.uniform(-0.0001, 0.001) # Move north/south slightly
            lng += random.uniform(-0.0001, 0.001) # Move east/west slightly
            
            if curr_vehicle['fuel_type'] == 'ELECTRIC':
                battery = max(0, battery - 0.1) # Drain battery
                fuel = 0
            else:
                fuel = max(0, fuel - 0.1) # Drain fuel
                battery = 0
                
            engine_temp = 85 + random.uniform(-5, 10)

            # Create Telemetry Payload
            # Ideally fuel_level should be optional, but old backend requires float.
            # We send 0.0 instead of None to support old backend fallback.
            telemetry = {
                "vehicle_id": vid,
                "timestamp": datetime.now().isoformat(),
                "speed": round(speed, 1),
                "latitude": lat,
                "longitude": lng,
                "battery_level": round(battery, 1) if curr_vehicle['fuel_type'] == 'ELECTRIC' else None,
                "fuel_level": round(fuel, 1) if curr_vehicle['fuel_type'] != 'ELECTRIC' else 0.0, 
                "engine_temp": round(engine_temp, 1),
                # Add dummy required fields for old backend if needed
                "rpm": 2000.0,
                "tire_pressure": 32.0,
                "location": f"{lat},{lng}"  # Old backend liked string location
            }

            # Send Telemetry
            try:
                resp = requests.post(f"{BASE_URL}/telemetry", json=telemetry)
                if resp.status_code == 200:
                    print(f"📡 Sent to /telemetry: Speed={telemetry['speed']} km/h")
                elif resp.status_code == 404:
                    # Fallback to old endpoint
                    print("⚠️ /telemetry not found (deployment pending?), trying /ingest/telemetry...")
                    resp = requests.post(f"{BASE_URL}/ingest/telemetry", json=telemetry)
                    if resp.status_code == 200 or resp.status_code == 422: # 422 might be schema mismatch but let's see
                        if resp.status_code == 200:
                             print(f"📡 Sent to /ingest/telemetry: Speed={telemetry['speed']} km/h")
                        else:
                             print(f"⚠️ /ingest/telemetry failed: {resp.text}")
                    else:
                        print(f"⚠️ Telemetry Error: {resp.status_code}")
                else:
                    print(f"⚠️ Telemetry Error: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"⚠️ Connection Error: {e}")

            # Occasionally send Alert (10% chance)
            if random.random() < 0.05:
                alert_type = random.choice(["RASH_DRIVING", "MAINTENANCE", "LOW_BATTERY"])
                alert = {
                    "alert_id": f"alert_{int(time.time())}",
                    "vehicle_id": vid,
                    "type": alert_type,
                    "severity": "High" if alert_type == "RASH_DRIVING" else "Medium",
                    "message": f"Simulated {alert_type} alert at {datetime.now().strftime('%H:%M:%S')}",
                    "timestamp": datetime.now().isoformat(),
                    "location": f"{lat:.4f}, {lng:.4f}",
                    "is_actioned": False,
                    "icon": "warning",
                    "color": "0xFFD32F2F",
                    "bg_color": "0xFFFFCDD2"
                }
                requests.post(f"{BASE_URL}/alert", json=alert)
                print(f"🚨 SENT ALERT: {alert_type}")

            time.sleep(2) # Send every 2 seconds

    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped.")

if __name__ == "__main__":
    main()
