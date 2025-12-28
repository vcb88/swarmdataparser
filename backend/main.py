from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import pandas as pd
import os
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Swarm Data Dashboard API")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the database (in the parent directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'foursquare_data.db')
FRONTEND_PATH = os.path.join(BASE_DIR, 'frontend', 'dist')

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database not found. Please run import_data.py first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Models ---
class StatSummary(BaseModel):
    total_checkins: int
    unique_venues: int
    top_city: Optional[str]
    total_distance_km: float

class CheckinGeo(BaseModel):
    id: str
    venue_name: Optional[str]
    lat: float
    lng: float
    timestamp: int
    shout: Optional[str]

class WeeklyCount(BaseModel):
    week: str
    count: int

# --- Endpoints ---

@app.get("/api/stats", response_model=StatSummary)
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM checkins")
    total_checkins = cursor.fetchone()[0]
    cursor.execute("SELECT count(DISTINCT venueId) FROM checkins")
    unique_venues = cursor.fetchone()[0]
    cursor.execute("SELECT city, count(*) as cnt FROM visits WHERE city IS NOT NULL GROUP BY city ORDER BY cnt DESC LIMIT 1")
    top_city_row = cursor.fetchone()
    top_city = top_city_row[0] if top_city_row else "Unknown"
    conn.close()
    return StatSummary(total_checkins=total_checkins, unique_venues=unique_venues, top_city=top_city, total_distance_km=0.0)

@app.get("/api/checkins/geo", response_model=List[CheckinGeo])
def get_checkins_geo():
    conn = get_db_connection()
    query = """
    SELECT c.id, c.createdAt, c.shout, v.name as venue_name, v.lat, v.lng
    FROM checkins c
    LEFT JOIN venues v ON c.venueId = v.id
    WHERE v.lat IS NOT NULL AND v.lng IS NOT NULL
    ORDER BY c.createdAt ASC
    """
    cursor = conn.execute(query)
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        try:
            ts = int(row['createdAt'])
            results.append(CheckinGeo(id=row['id'], venue_name=row['venue_name'], lat=row['lat'], lng=row['lng'], timestamp=ts, shout=row['shout']))
        except: continue
    return results

@app.get("/api/timeline/weekly", response_model=List[WeeklyCount])
def get_weekly_timeline():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT createdAt FROM checkins ORDER BY createdAt ASC", conn)
    conn.close()
    if df.empty: return []
    df['createdAt'] = pd.to_numeric(df['createdAt'], errors='coerce')
    df.dropna(subset=['createdAt'], inplace=True)
    df['datetime'] = pd.to_datetime(df['createdAt'], unit='s')
    weekly = df.set_index('datetime').resample('W').size().reset_index(name='count')
    return [WeeklyCount(week=row['datetime'].strftime('%Y-%m-%d'), count=int(row['count'])) for _, row in weekly.iterrows()]

# --- Serve Frontend ---
if os.path.exists(FRONTEND_PATH):
    app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    index_path = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "API is running. Frontend build not found."}