from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    avatar_url = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False, default="not_set") # Default for migration safety, though we will wipe DB

    vehicles = relationship("Vehicle", back_populates="owner")

class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.user_id"))
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    registration_number = Column(String)
    fuel_type = Column(String)
    insurance_expiry = Column(String, nullable=True)
    last_service = Column(String, nullable=True)

    owner = relationship("User", back_populates="vehicles")
    trips = relationship("Trip", back_populates="vehicle")
    alerts = relationship("Alert", back_populates="vehicle")
    telemetry_logs = relationship("TelemetryLog", back_populates="vehicle")

class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"))
    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    distance_km = Column(Float)
    score = Column(Integer)
    score_color = Column(String, nullable=True)
    status = Column(String, default="COMPLETED")
    
    # Store route points as JSON for simplicity in SQLite 
    # (In Production Postgres, use JSONB or separate table)
    route_points_json = Column(String, default="[]") 

    vehicle = relationship("Vehicle", back_populates="trips")

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"))
    type = Column(String)
    severity = Column(String)
    message = Column(String)
    timestamp = Column(DateTime)
    location = Column(String, nullable=True)
    is_actioned = Column(Boolean, default=False)
    icon = Column(String, default="circle-info")
    color = Column(String, default="0xFF90A4AE")
    bg_color = Column(String, default="0xFFECEFF1")

    vehicle = relationship("Vehicle", back_populates="alerts")

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicle_id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    speed = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    battery_level = Column(Float, nullable=True)
    
    vehicle = relationship("Vehicle", back_populates="telemetry_logs")
