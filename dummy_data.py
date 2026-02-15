from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
import sql_models
import crud
import json

def populate_dummy_data(db: Session):
    # Check if data exists
    if db.query(sql_models.User).first():
        return

    # User
    # User
    user = models.UserCreate(
        user_id="user_123",
        name="Vishwas C",
        email="vishwas@example.com",
        phone="+91 98765 43210",
        avatar_url="https://i.pravatar.cc/300",
        password="password123"
    )
    crud.create_user(db, user)

    # Vehicle
    vehicle = models.Vehicle(
        vehicle_id="v_101",
        owner_id="user_123",
        make="Tata",
        model="Nexon EV",
        year=2024,
        registration_number="KA 05 MN 2024",
        fuel_type="ELECTRIC",
        insurance_expiry="2025-08-15",
        last_service="2024-01-20"
    )
    crud.create_vehicle(db, vehicle)

    # Alerts
    alerts = [
        models.Alert(
            alert_id="a_1",
            vehicle_id="v_101",
            type="RASH_DRIVING",
            severity="High",
            message="Harsh braking event recorded at MG Road signal.",
            timestamp=datetime.now(),
            icon="warning",
            color="0xFFD32F2F",
            bg_color="0xFFFFCDD2"
        ),
        models.Alert(
            alert_id="a_2",
            vehicle_id="v_101",
            type="MAINTENANCE",
            severity="Medium",
            message="Regular maintenance service is due soon.",
            timestamp=datetime.now() - timedelta(hours=2),
            icon="service",
            color="0xFFF57C00",
            bg_color="0xFFFFE0B2"
        )
    ]
    for alert in alerts:
        crud.create_alert(db, alert)

    # Trips
    trips = [
        models.Trip(
            trip_id="t_1",
            vehicle_id="v_101",
            title="Trip to MG Road",
            start_time=datetime.now() - timedelta(minutes=45),
            end_time=datetime.now(),
            distance_km=12.5,
            score=85,
            score_color="0xFF388E3C",
            route_points=[
                models.TripPoint(lat=12.9716, lng=77.5946),
                models.TripPoint(lat=12.9725, lng=77.5955),
                models.TripPoint(lat=12.9735, lng=77.5965),
                models.TripPoint(lat=12.9745, lng=77.5975)
            ]
        ),
        models.Trip(
            trip_id="t_2",
            vehicle_id="v_101",
            title="Commute to Office",
            start_time=datetime.now() - timedelta(days=1, hours=2),
            end_time=datetime.now() - timedelta(days=1, hours=1),
            distance_km=18.2,
            score=72,
            score_color="0xFFFBC02D",
            route_points=[
                models.TripPoint(lat=12.9279, lng=77.6271),
                models.TripPoint(lat=12.9352, lng=77.6245),
                models.TripPoint(lat=12.9461, lng=77.6189)
            ]
        )
    ]
    for trip in trips:
        crud.create_trip(db, trip)

