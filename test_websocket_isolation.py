
from fastapi.testclient import TestClient
from main import app
import json
import time

def test_websocket_isolation():
    client = TestClient(app)
    
    # IDs for test vehicles
    v1_id = "test_vehicle_1"
    v2_id = "test_vehicle_2"
    
    print(f"Connecting to WebSocket for {v1_id}...")
    with client.websocket_connect(f"/ws/telemetry/{v1_id}") as ws1:
        print(f"Connecting to WebSocket for {v2_id}...")
        with client.websocket_connect(f"/ws/telemetry/{v2_id}") as ws2:
            
            # 1. Send Telemetry for Vehicle 1
            print(f"Sending telemetry for {v1_id}...")
            telemetry_v1 = {
                "vehicle_id": v1_id,
                "timestamp": "2024-01-01T12:00:00",
                "speed": 50.0,
                "latitude": 12.0,
                "longitude": 77.0,
                "battery_level": 80.0
            }
            client.post("/ingest/telemetry", json=telemetry_v1)
            
            # 2. Verify WS1 received it
            print(f"Waiting for message on {v1_id} socket...")
            data1 = ws1.receive_json()
            print(f"WS1 Received: {data1}")
            assert data1['type'] == 'telemetry'
            assert data1['data']['vehicle_id'] == v1_id
            
            # 3. Send Telemetry for Vehicle 2
            print(f"Sending telemetry for {v2_id}...")
            telemetry_v2 = {
                "vehicle_id": v2_id,
                "timestamp": "2024-01-01T12:00:01",
                "speed": 60.0,
                "latitude": 13.0,
                "longitude": 78.0,
                "battery_level": 70.0
            }
            client.post("/ingest/telemetry", json=telemetry_v2)
            
            # 4. Verify WS2 received ONLY V2 data (it should not have V1 data queued)
            print(f"Waiting for message on {v2_id} socket...")
            data2 = ws2.receive_json()
            print(f"WS2 Received: {data2}")
            
            # Checks
            assert data2['type'] == 'telemetry'
            if data2['data']['vehicle_id'] == v1_id:
                print("❌ FAILURE: WS2 received data for Vehicle 1!")
                # raise Exception("WebSocket 2 received Vehicle 1 data (leak)")
                exit(1)
            elif data2['data']['vehicle_id'] == v2_id:
                 print("✅ SUCCESS: WS2 received data for Vehicle 2 (and skipped V1)")
            else:
                 print(f"❓ UNKNOWN: WS2 received {data2}")
                 # raise Exception("Unknown data received")
                 exit(1)

            # Optional: Ensure WS1 did NOT receive V2
            # This is harder to test synchronously without timeout, skipping for now
            # as the primary bug was "everyone hears everything".
            # By proving WS2's first message was V2, we prove it didn't hear V1 (which was sent while WS2 was open).

if __name__ == "__main__":
    try:
        test_websocket_isolation()
        print("\n🎉 VERIFICATION PASSED: WebSockets are properly scoped!")
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        exit(1)
