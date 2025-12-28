import sqlite3
import pandas as pd
import folium
from folium.plugins import HeatMap, TimestampedGeoJson, MarkerCluster
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
from datetime import datetime
import math

# --- Configuration ---
DB_NAME = 'foursquare_data.db'
OUTPUT_DIR = 'visualizations'

def load_data():
    """
    Connects to the SQLite database and returns key DataFrames.
    """
    if not os.path.exists(DB_NAME):
        print(f"Error: Database '{DB_NAME}' not found. Please run import_data.py first.")
        return None, None, None

    conn = sqlite3.connect(DB_NAME)
    
    # Checkins with Venue Data
    print("Loading Checkins and Venues...")
    query_checkins = """
    SELECT 
        c.id, c.createdAt, c.shout, c.timeZone,
        v.name as venue_name, v.lat, v.lng, v.address, v.id as venue_id
    FROM checkins c
    LEFT JOIN venues v ON c.venueId = v.id
    """
    df_checkins = pd.read_sql_query(query_checkins, conn)
    
    # Convert createdAt to datetime (assuming it's a unix timestamp in seconds)
    # If it's stored as a string literal of a number, pandas handles it gracefully usually, 
    # but let's be safe.
    df_checkins['createdAt'] = pd.to_numeric(df_checkins['createdAt'])
    df_checkins['datetime'] = pd.to_datetime(df_checkins['createdAt'], unit='s')
    
    # Visits Data
    print("Loading Visits...")
    query_visits = """SELECT * FROM visits
    """
    df_visits = pd.read_sql_query(query_visits, conn)
    # Visits often have timeArrived as unix timestamp
    if not df_visits.empty:
        df_visits['timeArrived'] = pd.to_numeric(df_visits['timeArrived'])
        df_visits['datetime'] = pd.to_datetime(df_visits['timeArrived'], unit='s')

    conn.close()
    
    return df_checkins, df_visits

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

# --- 1. Timeline Visualization ---
def plot_weekly_checkins(df):
    print("Generating Weekly Checkins Timeline...")
    # Resample by week
    weekly_counts = df.set_index('datetime').resample('W').size()
    
    plt.figure(figsize=(12, 6))
    weekly_counts.plot(kind='line', color='#2c3e50', linewidth=2)
    plt.title('Check-ins Over Time (Weekly)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Check-ins', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/1_weekly_checkins_timeline.png")
    plt.close()

# --- 2. Map Animation (Time-lapse) ---
def plot_map_animation(df):
    print("Generating Map Animation (Time-lapse)...")
    # Filter out checkins without location
    df_geo = df.dropna(subset=['lat', 'lng']).sort_values('datetime')
    
    if df_geo.empty:
        print("No geolocation data found for animation.")
        return

    # Base map centered on the mean location
    m = folium.Map(location=[df_geo['lat'].mean(), df_geo['lng'].mean()], zoom_start=3, tiles='CartoDB dark_matter')

    # Prepare data for TimestampedGeoJson
    features = []
    for _, row in df_geo.iterrows():
        # Create a feature for each checkin
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['lng'], row['lat']],
            },
            'properties': {
                'time': row['datetime'].isoformat(),
                'style': {'color': '#3498db'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': '#3498db',
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': 5
                },
                'popup': f"{row['venue_name']} ({row['datetime'].strftime('%Y-%m-%d')})"
            }
        }
        features.append(feature)

    TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': features},
        period='P1W', # 1 Week steps
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY-MM-DD',
        time_slider_drag_update=True,
        duration='P1D' # Display duration
    ).add_to(m)

    m.save(f"{OUTPUT_DIR}/2_checkin_history_animated.html")

# --- 3. Heatmap ---
def plot_heatmap(df):
    print("Generating Global Heatmap...")
    df_geo = df.dropna(subset=['lat', 'lng'])
    
    if df_geo.empty:
        return

    m = folium.Map(location=[df_geo['lat'].mean(), df_geo['lng'].mean()], zoom_start=3)
    
    heat_data = [[row['lat'], row['lng']] for index, row in df_geo.iterrows()]
    
    HeatMap(heat_data, radius=10, blur=15).add_to(m)
    m.save(f"{OUTPUT_DIR}/3_global_heatmap.html")

# --- 4. Activity Heatmap (Day vs Hour) ---
def plot_activity_matrix(df):
    print("Generating Activity Heatmap (Day vs Hour)...")
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_name()
    
    # Order of days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    pivot_table = df.pivot_table(index='day_of_week', columns='hour', values='id', aggfunc='count', fill_value=0)
    pivot_table = pivot_table.reindex(days_order)
    
    plt.figure(figsize=(14, 6))
    sns.heatmap(pivot_table, cmap="YlGnBu", annot=False, fmt="d")
    plt.title('Check-in Activity: Day vs Hour', fontsize=16)
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Day of Week', fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/4_activity_matrix.png")
    plt.close()

# --- 5. Top Venues ---
def plot_top_venues(df):
    print("Generating Top Venues Chart...")
    top_venues = df['venue_name'].value_counts().head(15).sort_values(ascending=True)
    
    plt.figure(figsize=(10, 8))
    top_venues.plot(kind='barh', color='#8e44ad')
    plt.title('Top 15 Most Visited Venues', fontsize=16)
    plt.xlabel('Number of Check-ins', fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/5_top_venues.png")
    plt.close()

# --- 6. Top Cities (from Visits) ---
def plot_top_cities(df_visits):
    if df_visits is None or df_visits.empty:
        print("No visit data available for Top Cities.")
        return

    print("Generating Top Cities Chart...")
    if 'city' in df_visits.columns:
        top_cities = df_visits['city'].value_counts().head(15).sort_values(ascending=True)
        
        plt.figure(figsize=(10, 8))
        top_cities.plot(kind='barh', color='#16a085')
        plt.title('Top 15 Most Visited Cities', fontsize=16)
        plt.xlabel('Number of Visits', fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{OUTPUT_DIR}/6_top_cities.png")
        plt.close()

# --- 7. Shout Word Cloud ---
def plot_shout_wordcloud(df):
    print("Generating Shout Word Cloud...")
    text = " ".join(shout for shout in df['shout'].dropna())
    
    if not text:
        print("No shouts found.")
        return

    wordcloud = WordCloud(width=800, height=400, background_color ='white', colormap='viridis').generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/7_shout_wordcloud.png")
    plt.close()

# --- 8. Where I've Been (Unique Locations) ---
def plot_unique_locations_map(df):
    print("Generating 'Where I've Been' Map...")
    df_geo = df.dropna(subset=['lat', 'lng'])
    unique_venues = df_geo.drop_duplicates(subset=['venue_id'])
    
    if unique_venues.empty:
        return

    m = folium.Map(location=[unique_venues['lat'].mean(), unique_venues['lng'].mean()], zoom_start=2, tiles='CartoDB positron')
    
    # Use MarkerCluster for better performance with many points
    marker_cluster = MarkerCluster().add_to(m)
    
    for _, row in unique_venues.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=4,
            popup=row['venue_name'],
            color='#e74c3c',
            fill=True,
            fill_color='#e74c3c'
        ).add_to(marker_cluster)
        
    m.save(f"{OUTPUT_DIR}/8_unique_locations_map.html")

# --- 9. Travel Distance Calculation (Approx) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def calculate_stats(df):
    print("Calculating Basic Stats...")
    total_checkins = len(df)
    unique_venues = df['venue_id'].nunique()
    
    # Calculate approx distance
    df_geo = df.dropna(subset=['lat', 'lng']).sort_values('datetime')
    total_distance = 0
    prev_row = None
    
    for _, row in df_geo.iterrows():
        if prev_row is not None:
            dist = haversine(prev_row['lat'], prev_row['lng'], row['lat'], row['lng'])
            # Filter out huge jumps (e.g. GPS errors) or keep them? Let's keep reasonable ones.
            if dist < 20000: # Max 20,000 km jump
                total_distance += dist
        prev_row = row
        
    print(f"--- Statistics ---")
    print(f"Total Check-ins: {total_checkins}")
    print(f"Unique Venues: {unique_venues}")
    print(f"Estimated Total Travel Distance: {total_distance:.2f} km")
    
    # Save stats to text file
    with open(f"{OUTPUT_DIR}/stats.txt", "w") as f:
        f.write(f"Total Check-ins: {total_checkins}\n")
        f.write(f"Unique Venues: {unique_venues}\n")
        f.write(f"Estimated Total Travel Distance: {total_distance:.2f} km\n")

def main():
    ensure_output_dir()
    
    df_checkins, df_visits = load_data()
    
    if df_checkins is not None and not df_checkins.empty:
        plot_weekly_checkins(df_checkins)
        plot_map_animation(df_checkins)
        plot_heatmap(df_checkins)
        plot_activity_matrix(df_checkins)
        plot_top_venues(df_checkins)
        plot_shout_wordcloud(df_checkins)
        plot_unique_locations_map(df_checkins)
        calculate_stats(df_checkins)
    else:
        print("No checkin data found.")

    if df_visits is not None and not df_visits.empty:
        plot_top_cities(df_visits)
    
    print(f"\nAll visualizations saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
