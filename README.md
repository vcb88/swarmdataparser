# Swarm Data Dashboard

A modern analytics dashboard for your Foursquare/Swarm history. Visualize your travels, discover insights, and watch your life unfold on an interactive map.

![Swarm Dashboard](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Backend-FastAPI-blue)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind-blueviolet)

## Features

-   **Time Machine Map**: Watch your check-ins appear chronologically on a global map.
-   **Activity Timeline**: Interactive charts showing your check-in frequency over the years.
-   **Stats Overview**: Total check-ins, unique venues visited, top cities, and estimated travel distance.
-   **Privacy First**: Runs entirely locally. Your data never leaves your machine.

## Prerequisites

-   **Docker** & **Docker Compose** installed on your machine.
-   Your Foursquare/Swarm data export (JSON files).

## Quick Start

### 1. Import Your Data

1.  Place your Swarm JSON export files (`checkins.json`, `visits.json`, `users.json`, etc.) in the root directory of this project.
2.  Run the import script to generate the database:

    ```bash
    # If you have python installed locally:
    python import_data.py
    
    # OR using Docker (if you don't want to install Python locally):
    docker compose run --rm swarm-dashboard python import_data.py
    ```

    This creates a `foursquare_data.db` file.

### 2. Run the Dashboard

Start the application using Docker Compose:

```bash
docker compose up --build
```

### 3. Explore

Open your browser and navigate to:

**[http://localhost:8000](http://localhost:8000)**

## Development

-   **Backend**: FastAPI (Python) located in `./backend`.
-   **Frontend**: React (Vite + TypeScript) located in `./frontend`.
-   **Database**: SQLite (`foursquare_data.db`).

To run in development mode (without Docker):

1.  **Backend**:
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
