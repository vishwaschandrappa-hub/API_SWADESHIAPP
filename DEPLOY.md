# Deployment Guide 🚀

The backend is configured for easy deployment on **Render.com**.

## Option 1: Deploy with Render (Recommended)

1.  **Push your code** to a GitHub repository.
2.  **Sign up/Login** to [Render.com](https://render.com/).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  Render will automatically detect `render.yaml` if it's in the root, but since it's in a subfolder, you might need to configure manually:
    *   **Root Directory**: Leave empty (since your repo starts inside `backend`)
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
    *   **Runtime**: Python 3

## Option 2: Run Locally

To run the server on your machine:

1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the server:
    ```bash
    uvicorn main:app --reload
    ```
    *Note: If you are running from the root folder, use `uvicorn backend.main:app --reload`*

API Docs will be available at: http://127.0.0.1:8000/docs
