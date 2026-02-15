from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class VehicleTelemetry(BaseModel):
    vehicle_id: str
    timestamp: datetime
    speed: float  # km/h
    rpm: Optional[float] = None
    latitude: float
    longitude: float
    fuel_level: Optional[float] = None  # percentage
    battery_level: Optional[float] = None # For EVs
    engine_temp: Optional[float] = None
    tire_pressure: Optional[float] = None
    accelerometer: Optional[AccelerometerData] = None

class Alert(BaseModel):
    alert_id: str
    vehicle_id: str
    type: str  # RASH_DRIVING, MAINTENANCE, GEOFENCE, THEFT
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    timestamp: datetime
    location: Optional[str] = None
    is_actioned: bool = False
    icon: Optional[str] = "circle-info"
    color: Optional[str] = "0xFF90A4AE"
    bg_color: Optional[str] = "0xFFECEFF1"

class Vehicle(BaseModel):
    vehicle_id: str
    owner_id: str
    make: str
    model: str
    year: int
    registration_number: str
    fuel_type: str # PETROL, DIESEL, ELECTRIC
    insurance_expiry: Optional[str] = None
    last_service: Optional[str] = None

class UserBase(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    avatar_url: Optional[str] = None

class UserProfile(UserBase):
    vehicles: List[Vehicle] = []

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class TripPoint(BaseModel):
    lat: float
    lng: float
    timestamp: Optional[datetime] = None

class Trip(BaseModel):
    trip_id: str
    vehicle_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    distance_km: float
    score: int # 0-100
    score_color: Optional[str] = None # Hex code
    route_points: List[TripPoint] = []
    status: str = "COMPLETED" # ACTIVE, COMPLETED
