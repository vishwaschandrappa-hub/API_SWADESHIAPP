from datetime import datetime
from models import VehicleTelemetry, Alert

class AIEngine:
    def detect_rash_driving(self, telemetry: VehicleTelemetry) -> list[Alert]:
        alerts = []
        
        # 1. Harsh Braking / Acceleration (Mock Logic)
        # Real implementation would use sliding window on accelerometer z-axis
        if telemetry.accelerometer:
            accel = telemetry.accelerometer
            total_force = (accel.x**2 + accel.y**2 + accel.z**2)**0.5
            if total_force > 15.0: # Threshold for harsh event
                alerts.append(Alert(
                    alert_id=f"RD-{int(datetime.now().timestamp())}",
                    vehicle_id=telemetry.vehicle_id,
                    type="RASH_DRIVING",
                    severity="HIGH",
                    message="Harsh driving maneuver detected!",
                    timestamp=datetime.now(),
                    location=f"{telemetry.latitude}, {telemetry.longitude}"
                ))

        # 2. Overspeeding
        if telemetry.speed > 120.0:
            alerts.append(Alert(
                alert_id=f"OS-{int(datetime.now().timestamp())}",
                vehicle_id=telemetry.vehicle_id,
                type="RASH_DRIVING",
                severity="MEDIUM",
                message=f"Overspeeding detected: {telemetry.speed} km/h",
                timestamp=datetime.now()
            ))
            
        return alerts

    def predict_maintenance(self, telemetry: VehicleTelemetry) -> list[Alert]:
        alerts = []
        
        # Mock Predictive Logic
        # 1. Battery Health (for EVs)
        if telemetry.battery_level is not None and telemetry.battery_level < 20.0:
             alerts.append(Alert(
                alert_id=f"MNT-{int(datetime.now().timestamp())}",
                vehicle_id=telemetry.vehicle_id,
                type="MAINTENANCE",
                severity="MEDIUM",
                message="Battery critically low. Recharge required soon.",
                timestamp=datetime.now()
            ))
            
        # 2. Engine Temp
        if telemetry.engine_temp is not None and telemetry.engine_temp > 100.0:
             alerts.append(Alert(
                alert_id=f"ENG-{int(datetime.now().timestamp())}",
                vehicle_id=telemetry.vehicle_id,
                type="MAINTENANCE",
                severity="CRITICAL",
                message="Engine overheating! Stop immediately.",
                timestamp=datetime.now()
            ))

        return alerts
