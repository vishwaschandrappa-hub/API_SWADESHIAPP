from sqlalchemy.orm import Session
import sql_models
import models
import json

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, user_id: str):
    return db.query(sql_models.User).filter(sql_models.User.user_id == user_id).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(sql_models.User).filter(sql_models.User.phone == phone).first()

def create_user(db: Session, user: models.UserCreate):
    hashed_password = get_password_hash(user.password)
    # Exclude password from dict, add hashed_password
    user_data = user.dict()
    del user_data['password']
    
    db_user = sql_models.User(**user_data, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_vehicle(db: Session, vehicle_id: str):
    return db.query(sql_models.Vehicle).filter(sql_models.Vehicle.vehicle_id == vehicle_id).first()

def create_vehicle(db: Session, vehicle: models.Vehicle):
    db_vehicle = sql_models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: str, vehicle_update: dict):
    db_vehicle = db.query(sql_models.Vehicle).filter(sql_models.Vehicle.vehicle_id == vehicle_id).first()
    if db_vehicle:
        for key, value in vehicle_update.items():
            setattr(db_vehicle, key, value)
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: str):
    db_vehicle = db.query(sql_models.Vehicle).filter(sql_models.Vehicle.vehicle_id == vehicle_id).first()
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
    return db_vehicle

def get_alerts(db: Session, vehicle_id: str, actioned: bool = None):
    query = db.query(sql_models.Alert).filter(sql_models.Alert.vehicle_id == vehicle_id)
    if actioned is not None:
        query = query.filter(sql_models.Alert.is_actioned == actioned)
    return query.all()

def create_alert(db: Session, alert: models.Alert):
    db_alert = sql_models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def action_alert(db: Session, alert_id: str):
    alert = db.query(sql_models.Alert).filter(sql_models.Alert.alert_id == alert_id).first()
    if alert:
        alert.is_actioned = True
        db.commit()
        db.refresh(alert)
    return alert

def get_trips(db: Session, vehicle_id: str):
    trips = db.query(sql_models.Trip).filter(sql_models.Trip.vehicle_id == vehicle_id).all()
    # Convert JSON string back to list of dicts for response if needed, 
    # but Pydantic might expect object. We need to handle this mapping.
    return trips

def create_trip(db: Session, trip: models.Trip):
    trip_data = trip.dict()
    # Convert route_points to JSON string
    trip_data['route_points_json'] = json.dumps([p.dict() for p in trip.route_points], default=str)
    del trip_data['route_points'] # Remove list
    
    db_trip = sql_models.Trip(**trip_data)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def create_telemetry(db: Session, telemetry: models.VehicleTelemetry):
    # Only store fields that exist in sql_models.TelemetryLog
    telemetry_data = {
        "vehicle_id": telemetry.vehicle_id,
        "timestamp": telemetry.timestamp,
        "speed": telemetry.speed,
        "latitude": telemetry.latitude,
        "longitude": telemetry.longitude,
        "battery_level": telemetry.battery_level
    }
    
    db_telemetry = sql_models.TelemetryLog(**telemetry_data)
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

def get_telemetry(db: Session, vehicle_id: str, limit: int = 100):
    return db.query(sql_models.TelemetryLog).filter(
        sql_models.TelemetryLog.vehicle_id == vehicle_id
    ).order_by(sql_models.TelemetryLog.timestamp.desc()).limit(limit).all()
