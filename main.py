from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
import asyncio
import json
from datetime import datetime

from models import VehicleTelemetry, Alert, Vehicle, UserProfile, Trip, TripPoint
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

# --- User & Vehicle ---

@app.get("/user/{user_id}", response_model=UserProfile)
def get_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/user", response_model=UserProfile)
def create_new_user(user: UserProfile, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/vehicle/{vehicle_id}", response_model=Vehicle)
def get_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    db_vehicle = crud.get_vehicle(db, vehicle_id)
    if not db_vehicle:
         raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@app.post("/vehicle", response_model=Vehicle)
def create_new_vehicle(vehicle: Vehicle, db: Session = Depends(get_db)):
    return crud.create_vehicle(db, vehicle)

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
