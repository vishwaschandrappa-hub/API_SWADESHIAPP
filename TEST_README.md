# API Test Script Usage Guide

## Overview
`test_api.py` is a comprehensive test script to verify all backend API functionality including:
- User authentication (login/register)
- Vehicle CRUD operations (Create, Read, Update, Delete)
- Telemetry data upload (single and bulk)
- Alert creation and retrieval

## Quick Start

### 1. Run with Existing User
If you already have a registered user, edit `test_api.py` line 401-402:

```python
phone = "+91 98765 43210"  # Your registered phone
password = "password123"    # Your actual password
```

### 2. Run with New User
To create a new test user, change the phone number to something unique:

```python
phone = "+91 99999 12345"  # New unique number
password = "test123"
```

### 3. Execute the Test
```bash
cd backend
python3 test_api.py
```

## Test Cases Covered

### Authentication Tests
- ✅ **TEST 1**: User Login/Registration

### Vehicle Management Tests
- ✅ **TEST 2**: Add Vehicle
- ✅ **TEST 3**: Get Vehicle Details
- ✅ **TEST 4**: Update Vehicle (insurance, service dates)
- ✅ **TEST 5**: List All User Vehicles
- ✅ **TEST 10**: Add Second Vehicle
- ✅ **TEST 12**: Delete Vehicle
- ✅ **TEST 13**: Final Vehicle List

### Telemetry Tests
- ✅ **TEST 6**: Upload Single Telemetry Record
- ✅ **TEST 7**: Upload Bulk Telemetry (5 records)

### Alert Tests
- ✅ **TEST 8**: Create Multiple Alerts (RASH_DRIVING, MAINTENANCE, INFO)
- ✅ **TEST 9**: Get All Vehicle Alerts

## Using the Tester Class Programmatically

You can also use the `SwadeshiAPITester` class in your own scripts:

```python
from test_api import SwadeshiAPITester

# Initialize
tester = SwadeshiAPITester("https://api-swadeshiapp.onrender.com")

# Login
tester.login_user("+91 98765 43210", "password123")

# Add vehicle
vehicle = tester.add_vehicle("Honda", "City", 2023, "KA 01 AB 1234")

# Upload telemetry
tester.upload_telemetry(speed=75.5, lat=12.9716, lng=77.5946, battery=85.0)

# Create alert
tester.create_alert("RASH_DRIVING", "High", "Harsh braking detected")

# Get alerts
alerts = tester.get_alerts()
```

## Individual Test Methods

### Vehicle Operations
```python
# Add vehicle
tester.add_vehicle(make, model, year, reg_number, fuel_type)

# Get vehicle
tester.get_vehicle(vehicle_id)

# Update vehicle
tester.update_vehicle(vehicle_id, insurance_expiry="2026-12-31")

# Delete vehicle
tester.delete_vehicle(vehicle_id)

# List all user vehicles
tester.list_user_vehicles()
```

### Telemetry Operations
```python
# Single upload
tester.upload_telemetry(speed=75, lat=12.97, lng=77.59, battery=85)

# Bulk upload
tester.upload_bulk_telemetry(count=10)
```

### Alert Operations
```python
# Create alert
tester.create_alert(
    alert_type="RASH_DRIVING",
    severity="High",
    message="Harsh braking detected"
)

# Get all alerts
tester.get_alerts(vehicle_id)
```

## Configuration

### Switch Between Production and Local
Edit line 12-13 in `test_api.py`:

```python
# For production (Render)
BASE_URL = "https://api-swadeshiapp.onrender.com"

# For local testing
# BASE_URL = "http://localhost:8000"
```

## Expected Output

When successful, you'll see output like:

```
============================================================
  SWADESHI SMART VEHICLE API TEST SUITE
============================================================

[TEST 1] User Authentication
✅ SUCCESS: Login User
Response: {
  "user_id": "user_123",
  "name": "Test User",
  ...
}

[TEST 2] Add Vehicle
✅ SUCCESS: Add Vehicle
Response: {
  "vehicle_id": "veh_20260215_133000",
  "make": "Honda",
  "model": "City",
  ...
}

...

============================================================
  ✅ ALL TESTS COMPLETED!
============================================================
```

## Troubleshooting

### "Phone number already registered"
- Use a different phone number, or
- Use the correct password for the existing account

### "User not logged in"
- Ensure TEST 1 (authentication) passes first
- Check that `self.user_id` is set after login

### "No vehicle ID"
- Ensure TEST 2 (add vehicle) passes first
- Check that `self.vehicle_id` is set after adding vehicle

### Connection errors
- Verify backend is running (local or Render)
- Check BASE_URL is correct
- Ensure internet connection for Render deployment
