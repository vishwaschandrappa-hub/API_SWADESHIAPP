#!/usr/bin/env python3
"""
API Test Script for Swadeshi Smart Vehicle Backend
Tests vehicle CRUD operations, telemetry upload, and alert creation
"""

import requests
import json
from datetime import datetime
import random

# Configuration
BASE_URL = "https://api-swadeshiapp.onrender.com"
# BASE_URL = "http://localhost:8000"  # Uncomment for local testing

class SwadeshiAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.user_id = None
        self.vehicle_id = None
        self.session_token = None
    
    def print_section(self, title):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    
    def print_result(self, operation, success, data=None, error=None):
        """Print operation result"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {operation}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        if error:
            print(f"Error: {error}")
        print()
    
    # ==================== AUTH OPERATIONS ====================
    
    def register_user(self, phone, password, name, email):
        """Register a new user"""
        self.print_section("USER REGISTRATION")
        
        user_data = {
            "user_id": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "name": name,
            "email": email,
            "phone": phone,
            "avatar_url": "https://i.pravatar.cc/300",
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data['user_id']
                self.print_result("Register User", True, data)
                return data
            else:
                self.print_result("Register User", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Register User", False, error=str(e))
            return None
    
    def login_user(self, phone, password):
        """Login existing user"""
        self.print_section("USER LOGIN")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"phone": phone, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data['user_id']
                self.print_result("Login User", True, data)
                return data
            else:
                self.print_result("Login User", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Login User", False, error=str(e))
            return None
    
    # ==================== VEHICLE OPERATIONS ====================
    
    def add_vehicle(self, make, model, year, reg_number, fuel_type="PETROL"):
        """Add a new vehicle"""
        self.print_section("ADD VEHICLE")
        
        if not self.user_id:
            self.print_result("Add Vehicle", False, error="User not logged in")
            return None
        
        vehicle_data = {
            "vehicle_id": f"veh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "owner_id": self.user_id,
            "make": make,
            "model": model,
            "year": year,
            "registration_number": reg_number,
            "fuel_type": fuel_type,
            "insurance_expiry": "2025-12-31",
            "last_service": "2024-01-15"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/vehicle",
                json=vehicle_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.vehicle_id = data['vehicle_id']
                self.print_result("Add Vehicle", True, data)
                return data
            else:
                self.print_result("Add Vehicle", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Add Vehicle", False, error=str(e))
            return None
    
    def get_vehicle(self, vehicle_id=None):
        """Get vehicle details"""
        self.print_section("GET VEHICLE DETAILS")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Get Vehicle", False, error="No vehicle ID")
            return None
        
        try:
            response = requests.get(f"{self.base_url}/vehicle/{vid}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Get Vehicle", True, data)
                return data
            else:
                self.print_result("Get Vehicle", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Get Vehicle", False, error=str(e))
            return None
    
    def update_vehicle(self, vehicle_id=None, **updates):
        """Update vehicle details"""
        self.print_section("UPDATE VEHICLE")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Update Vehicle", False, error="No vehicle ID")
            return None
        
        # Get current vehicle data
        current = self.get_vehicle(vid)
        if not current:
            return None
        
        # Merge updates
        updated_data = {**current, **updates}
        
        try:
            response = requests.put(
                f"{self.base_url}/vehicle/{vid}",
                json=updated_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Update Vehicle", True, data)
                return data
            else:
                self.print_result("Update Vehicle", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Update Vehicle", False, error=str(e))
            return None
    
    def delete_vehicle(self, vehicle_id=None):
        """Delete a vehicle"""
        self.print_section("DELETE VEHICLE")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Delete Vehicle", False, error="No vehicle ID")
            return None
        
        try:
            response = requests.delete(f"{self.base_url}/vehicle/{vid}")
            
            if response.status_code == 200:
                self.print_result("Delete Vehicle", True, {"message": "Vehicle deleted"})
                if vid == self.vehicle_id:
                    self.vehicle_id = None
                return True
            else:
                self.print_result("Delete Vehicle", False, error=response.text)
                return False
        except Exception as e:
            self.print_result("Delete Vehicle", False, error=str(e))
            return False
    
    def list_user_vehicles(self):
        """List all vehicles for current user"""
        self.print_section("LIST USER VEHICLES")
        
        if not self.user_id:
            self.print_result("List Vehicles", False, error="User not logged in")
            return None
        
        try:
            response = requests.get(f"{self.base_url}/user/{self.user_id}")
            
            if response.status_code == 200:
                data = response.json()
                vehicles = data.get('vehicles', [])
                self.print_result("List Vehicles", True, {"count": len(vehicles), "vehicles": vehicles})
                return vehicles
            else:
                self.print_result("List Vehicles", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("List Vehicles", False, error=str(e))
            return None
    
    # ==================== TELEMETRY OPERATIONS ====================
    
    def upload_telemetry(self, vehicle_id=None, speed=None, lat=None, lng=None, battery=None):
        """Upload telemetry data"""
        self.print_section("UPLOAD TELEMETRY")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Upload Telemetry", False, error="No vehicle ID")
            return None
        
        telemetry_data = {
            "vehicle_id": vid,
            "timestamp": datetime.now().isoformat(),
            "speed": speed or random.uniform(40, 120),
            "latitude": lat or 12.9716 + random.uniform(-0.1, 0.1),
            "longitude": lng or 77.5946 + random.uniform(-0.1, 0.1),
            "battery_level": battery or random.uniform(20, 100)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/telemetry",
                json=telemetry_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Upload Telemetry", True, data)
                return data
            else:
                self.print_result("Upload Telemetry", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Upload Telemetry", False, error=str(e))
            return None
    
    def upload_bulk_telemetry(self, vehicle_id=None, count=10):
        """Upload multiple telemetry records"""
        self.print_section(f"UPLOAD BULK TELEMETRY ({count} records)")
        
        success_count = 0
        for i in range(count):
            result = self.upload_telemetry(vehicle_id)
            if result:
                success_count += 1
        
        print(f"✅ Successfully uploaded {success_count}/{count} telemetry records\n")
        return success_count
    
    # ==================== ALERT OPERATIONS ====================
    
    def create_alert(self, vehicle_id=None, alert_type="INFO", severity="Low", message=None):
        """Create a new alert"""
        self.print_section("CREATE ALERT")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Create Alert", False, error="No vehicle ID")
            return None
        
        alert_data = {
            "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "vehicle_id": vid,
            "type": alert_type,
            "severity": severity,
            "message": message or f"Test {alert_type} alert created at {datetime.now().strftime('%H:%M:%S')}",
            "timestamp": datetime.now().isoformat(),
            "location": "Test Location",
            "is_actioned": False,
            "icon": "warning",
            "color": "0xFFD32F2F",
            "bg_color": "0xFFFFCDD2"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/alert",
                json=alert_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Create Alert", True, data)
                return data
            else:
                self.print_result("Create Alert", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Create Alert", False, error=str(e))
            return None
    
    def get_alerts(self, vehicle_id=None):
        """Get all alerts for a vehicle"""
        self.print_section("GET VEHICLE ALERTS")
        
        vid = vehicle_id or self.vehicle_id
        if not vid:
            self.print_result("Get Alerts", False, error="No vehicle ID")
            return None
        
        try:
            response = requests.get(f"{self.base_url}/alerts/{vid}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Get Alerts", True, {"count": len(data), "alerts": data})
                return data
            else:
                self.print_result("Get Alerts", False, error=response.text)
                return None
        except Exception as e:
            self.print_result("Get Alerts", False, error=str(e))
            return None


# ==================== MAIN TEST EXECUTION ====================

def run_full_test():
    """Run comprehensive test suite"""
    print("\n" + "="*60)
    print("  SWADESHI SMART VEHICLE API TEST SUITE")
    print("="*60)
    
    tester = SwadeshiAPITester(BASE_URL)
    
    # Test 1: Register or Login
    print("\n[TEST 1] User Authentication")
    phone = "+91 98765 43210"
    password = "test123"
    
    # Try login first, if fails then register
    user = tester.login_user(phone, password)
    if not user:
        user = tester.register_user(phone, password, "Test User", "test@example.com")
    
    if not user:
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test 2: Add Vehicle
    print("\n[TEST 2] Add Vehicle")
    vehicle = tester.add_vehicle("Honda", "City", 2023, "KA 01 AB 1234", "PETROL")
    
    if not vehicle:
        print("❌ Vehicle creation failed. Exiting.")
        return
    
    # Test 3: Get Vehicle
    print("\n[TEST 3] Get Vehicle Details")
    tester.get_vehicle()
    
    # Test 4: Update Vehicle
    print("\n[TEST 4] Update Vehicle")
    tester.update_vehicle(
        insurance_expiry="2026-12-31",
        last_service="2024-02-15"
    )
    
    # Test 5: List User Vehicles
    print("\n[TEST 5] List All User Vehicles")
    vehicles = tester.list_user_vehicles()
    
    # Test 6: Upload Telemetry
    print("\n[TEST 6] Upload Single Telemetry Record")
    tester.upload_telemetry(speed=75.5, lat=12.9716, lng=77.5946, battery=85.0)
    
    # Test 7: Upload Bulk Telemetry
    print("\n[TEST 7] Upload Bulk Telemetry")
    tester.upload_bulk_telemetry(count=5)
    
    # Test 8: Create Alerts
    print("\n[TEST 8] Create Alerts")
    tester.create_alert("RASH_DRIVING", "High", "Harsh braking detected")
    tester.create_alert("MAINTENANCE", "Medium", "Service due soon")
    tester.create_alert("INFO", "Low", "Battery level normal")
    
    # Test 9: Get Alerts
    print("\n[TEST 9] Get All Alerts")
    tester.get_alerts()
    
    # Test 10: Add Another Vehicle
    print("\n[TEST 10] Add Second Vehicle")
    vehicle2 = tester.add_vehicle("Tata", "Nexon EV", 2024, "KA 05 MN 2024", "ELECTRIC")
    
    # Test 11: List All Vehicles Again
    print("\n[TEST 11] List All Vehicles (Should show 2)")
    tester.list_user_vehicles()
    
    # Test 12: Delete Second Vehicle
    print("\n[TEST 12] Delete Second Vehicle")
    if vehicle2:
        tester.delete_vehicle(vehicle2['vehicle_id'])
    
    # Test 13: Final Vehicle List
    print("\n[TEST 13] Final Vehicle List (Should show 1)")
    tester.list_user_vehicles()
    
    print("\n" + "="*60)
    print("  ✅ ALL TESTS COMPLETED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_full_test()
