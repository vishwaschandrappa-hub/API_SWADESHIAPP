# Swadeshi Smart Vehicle Backend API 🚗💨

A robust, AI-powered backend for the Swadeshi Smart Vehicle application. Built with **FastAPI**, **SQLAlchemy**, and **Python**, this API manages user profiles, vehicle telemetry, trip tracking, and intelligent alerts.

## 🌟 Features

*   **User & Vehicle Management**: Full CRUD operations for user profiles and vehicle details.
*   **Trip Tracking**: automated trip logging, route point storage, and scoring.
*   **Intelligent Alerts**: Real-time detection of Rash Driving and Maintenance needs using an AI Engine.
*   **Persistent Storage**: SQLite database integration for data durability.
*   **Live Telemetry**: WebSocket support for real-time dashboard updates.
*   **Actionable Alerts**: Mark alerts as "actioned" to track resolution status.

## 🛠️ Tech Stack

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (High performance, easy to learn)
*   **Database**: SQLite (via SQLAlchemy ORM)
*   **AI Engine**: Custom logic for analyzing telemetry data.
*   **Deployment**: Ready for Render.com / Docker.

## 🚀 Getting Started

### Prerequisites

*   Python 3.9+
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/vishwaschandrappa-hub/API_SWADESHIAPP.git
    cd API_SWADESHIAPP
    ```

2.  **Create a virtual environment (Optional but Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running Locally

Start the server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

*   **Interactive Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
*   **ReDoc**: `http://127.0.0.1:8000/redoc`

## 📡 API Endpoints

### 👤 User & Vehicle
*   `GET /user/{user_id}` - Get user profile
*   `POST /user` - Create new user
*   `GET /vehicle/{vehicle_id}` - Get vehicle details
*   `POST /vehicle` - Register new vehicle

### 📍 Trips
*   `GET /trips/{vehicle_id}` - Get trip history
*   `POST /trips` - Start a new trip
*   `PUT /trips/{trip_id}/end` - End a trip

### ⚠️ Alerts
*   `GET /alerts/{vehicle_id}` - Fetch alerts (filter by `actioned`)
*   `POST /alerts/{alert_id}/action` - Mark alert as actioned
*   `POST /ingest/telemetry` - Ingest live data & generate alerts

### 🔌 Live Stream
*   `WS /ws/telemetry/{vehicle_id}` - WebSocket for real-time updates

## ☁️ Deployment

This project is configured for **Render.com**.

1.  Push code to GitHub.
2.  Create a **Web Service** on Render.
3.  Connect your repo.
4.  Render will automatically use the `render.yaml` configuration.

See [DEPLOY.md](DEPLOY.md) for more details.

## 📄 License

This project is licensed under the MIT License.
