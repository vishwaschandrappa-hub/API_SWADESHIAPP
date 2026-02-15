from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import json
from datetime import datetime

from models import (
    VehicleTelemetry, Alert, Vehicle, UserProfile, 
    Trip, TripPoint, UserCreate, UserLogin
)
from ai_engine import AIEngine
from dummy_data import populate_dummy_data
from database import SessionLocal, engine, Base, get_db
import sql_models
import crud

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Swadeshi Smart Vehicle Backend")
ai_engine = AIEngine()

# Active WebSocket Connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Initialize Dummy Data
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    populate_dummy_data(db)
    db.close()
    print("Database initialized") # Trigger redeploy

@app.get("/")
def read_root():
    return {"message": "Swadeshi Smart Vehicle Backend is Running with SQLite"}

# --- Telemetry & AI ---

@app.post("/ingest/telemetry")
async def ingest_telemetry(data: VehicleTelemetry, db: Session = Depends(get_db)):
    # Log telemetry to DB (Optional, skipping for now to keep DB small)
    
    # Run Real-time AI Analysis
    rash_alerts = ai_engine.detect_rash_driving(data)
    maintenance_alerts = ai_engine.predict_maintenance(data)
    
    new_alerts = rash_alerts + maintenance_alerts
    
    for alert in new_alerts:
        crud.create_alert(db, alert)
    
    # Broadcast to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "telemetry",
        "data": data.dict(exclude_none=True, by_alias=True)
    }, default=str))

    if new_alerts:
        await manager.broadcast(json.dumps({
            "type": "alert",
            "data": [a.dict(default=str) for a in new_alerts]
        }, default=str))

    return {
        "status": "success",
        "alerts_generated": len(new_alerts),
        "alerts": new_alerts
    }

@app.websocket("/ws/telemetry/{vehicle_id}")
async def websocket_endpoint(websocket: WebSocket, vehicle_id: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/telemetry")
def create_telemetry(telemetry: VehicleTelemetry, db: Session = Depends(get_db)):
    return crud.create_telemetry(db, telemetry)

@app.get("/telemetry/{vehicle_id}")
def get_telemetry(vehicle_id: str, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_telemetry(db, vehicle_id, limit)

# --- User & Vehicle ---

@app.get("/user/{user_id}", response_model=UserProfile)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/user", response_model=UserProfile)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/auth/register", response_model=UserProfile)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_phone(db, user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    return crud.create_user(db, user)

@app.post("/auth/login", response_model=UserProfile)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_phone(db, data.phone)
    if not user:
        # Generic error message or specific as requested ("user not found")
        raise HTTPException(status_code=404, detail="User not found")
    if not crud.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user

@app.get("/vehicle/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle(db, vehicle_id)
    if not db_vehicle:
         raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.post("/vehicle", response_model=Vehicle)
def create_new_vehicle(vehicle: Vehicle, db: Session = Depends(get_db)):
    return crud.create_vehicle(db, vehicle)

@app.delete("/vehicle/{vehicle_id}")
def delete_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    vehicle = crud.delete_vehicle(db, vehicle_id)
    if not vehicle:
         raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"status": "success", "message": "Vehicle deleted"}

@app.put("/vehicle/{vehicle_id}", response_model=Vehicle)
def update_vehicle(vehicle_id: str, vehicle_update: Dict, db: Session = Depends(get_db)):
    db_vehicle = crud.update_vehicle(db, vehicle_id, vehicle_update)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

# --- Alerts ---

@app.get("/alerts/{vehicle_id}", response_model=List[Alert])
def get_alerts(vehicle_id: str, actioned: bool = None, db: Session = Depends(get_db)):
    return crud.get_alerts(db, vehicle_id, actioned)

@app.post("/alerts/{alert_id}/action")
def action_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = crud.action_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "message": "Alert marked as actioned"}

@app.post("/alert", response_model=Alert)
def create_alert(alert: Alert, db: Session = Depends(get_db)):
    return crud.create_alert(db, alert)

# --- Trips ---

@app.get("/trips/{vehicle_id}", response_model=List[Trip])
def get_trips(vehicle_id: str, db: Session = Depends(get_db)):
    db_trips = crud.get_trips(db, vehicle_id)
    # Parse JSON route points
    trips_response = []
    for t in db_trips:
        # Create a dict from the DB model
        t_dict = {
            "trip_id": t.trip_id,
            "vehicle_id": t.vehicle_id,
            "title": t.title,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "distance_km": t.distance_km,
            "score": t.score,
            "score_color": t.score_color,
            "status": t.status,
            "route_points": json.loads(t.route_points_json)
        }
        trips_response.append(t_dict)
    return trips_response

@app.post("/trips")
def create_trip(trip: Trip, db: Session = Depends(get_db)):
    return crud.create_trip(db, trip)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
