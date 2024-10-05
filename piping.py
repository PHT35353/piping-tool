import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
import json  # New import for passing Python data to JS

# B1001 embedded data
B1001_data = [
    {"Nominal diameter (inches)": 0.5, "External diameter (mm)": 21.3, "Wall thickness (mm)": 2.77, "Weight (kg/m)": 1.2, "Cost per 100 m (Euro)": 300, "Pressure (bar)": 20},
    {"Nominal diameter (inches)": 1.0, "External diameter (mm)": 33.4, "Wall thickness (mm)": 3.38, "Weight (kg/m)": 2.4, "Cost per 100 m (Euro)": 450, "Pressure (bar)": 25},
    # Add more rows from B1001 CSV
]
B1001_df = pd.DataFrame(B1001_data)

# B1003 embedded data
B1003_data = [
    {"Nominal diameter (inches)": 0.5, "External diameter (mm)": 21.3, "Wall thickness (mm)": 2.77, "Weight (kg/m)": 1.5, "Cost per 100 m (Euro)": 320, "Pressure (bar)": 22},
    {"Nominal diameter (inches)": 1.0, "External diameter (mm)": 33.4, "Wall thickness (mm)": 3.38, "Weight (kg/m)": 2.7, "Cost per 100 m (Euro)": 470, "Pressure (bar)": 27},
    # Add more rows from B1003 CSV
]
B1003_df = pd.DataFrame(B1003_data)

# B1005 embedded data
B1005_data = [
    {"Nominal diameter (inches)": 0.5, "External diameter (mm)": 21.34, "Wall thickness (mm)": 2.11, "Weight (kg/m)": 1.7, "Cost per m (304 Euro)": 3.0, "Pressure (bar)": 18},
    {"Nominal diameter (inches)": 1.0, "External diameter (mm)": 33.4, "Wall thickness (mm)": 2.77, "Weight (kg/m)": 2.9, "Cost per m (304 Euro)": 4.5, "Pressure (bar)": 22},
    # Add more rows from B1005 CSV
]
B1005_df = pd.DataFrame(B1005_data)

# B1008 embedded data
B1008_data = [
    {"External diameter (mm)": 25, "Wall thickness (mm)": 1.5, "Pressure (bar)": 15, "Cost per 100 m (Euro)": 208},
    {"External diameter (mm)": 32, "Wall thickness (mm)": 1.8, "Pressure (bar)": 18, "Cost per 100 m (Euro)": 243},
    # Add more rows from B1008 CSV
]
B1008_df = pd.DataFrame(B1008_data)

# Set up a title for the app
st.title("Piping Tool with Price Calculation")

# Add instructions and explain color options
st.markdown("""
This tool allows you to:
1. Draw rectangles (polygons), lines, and markers (landmarks) on the map.
2. Assign names and choose specific colors for each feature individually upon creation.
3. Display distances for lines and dimensions for polygons both on the map and in the sidebar.
4. Show relationships between landmarks and lines (e.g., a line belongs to two landmarks).
5. Automatically calculate the pipe cost based on the distance drawn on the map and the pipe material.
""")

# Sidebar to manage the map interactions
st.sidebar.title("Map Controls")

# Default location set to Amsterdam, Netherlands
default_location = [52.3676, 4.9041]

# Input fields for latitude and longitude
latitude = st.sidebar.number_input("Latitude", value=default_location[0])
longitude = st.sidebar.number_input("Longitude", value=default_location[1])

# Search bar for address search
address_search = st.sidebar.text_input("Search for address (requires internet connection)")

# Button to search for a location
if st.sidebar.button("Search Location"):
    default_location = [latitude, longitude]

# Function to calculate pipe cost based on the material and distance
def calculate_pipe_cost(material, distance_km):
    try:
        if material == 'B1001':
            df = B1001_df
        elif material == 'B1003':
            df = B1003_df
        elif material == 'B1005':
            df = B1005_df
        elif material == 'B1008':
            df = B1008_df
        else:
            st.sidebar.write("Invalid pipe material entered.")
            return 0

        total_cost = df['Cost per 100 m (Euro)'].mean() * distance_km * 1000 / 100  # Convert km to meters
        return total_cost
    except Exception as e:
        st.sidebar.write(f"Error calculating pipe cost: {e}")
        return 0

# Assuming some default totalDistance and totalCost as an example for passing to JavaScript
totalDistance = 1.5  # in km
pipeMaterial = "B1003"
totalCost = calculate_pipe_cost(pipeMaterial, totalDistance)

# Convert Python variables to JSON for passing to JS
data_to_js = {
    "totalDistance": totalDistance,
    "totalCost": totalCost,
}

# Pass data to JavaScript via HTML
components.html(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Mapbox GL JS Drawing Tool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css" rel="stylesheet" />
    <script src="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.3.0/mapbox-gl-draw.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.3.0/mapbox-gl-draw.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/@turf/turf/turf.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        #map {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 100%;
        }}
        .mapboxgl-ctrl {{
            margin: 10px;
        }}
        #sidebar {{
            position: absolute;
            top: 0;
            left: 0;
            width: 300px;
            height: 100%;
            background-color: white;
            border-right: 1px solid #ccc;
            z-index: 1;
            padding: 10px;
            transition: all 0.3s ease;
        }}
        #sidebar.collapsed {{
            width: 0;
            padding: 0;
            overflow: hidden;
        }}
        #toggleSidebar {{
            position: absolute;
            bottom: 290px;
            right: 10px;
            z-index: 2;
            background-color: white;
            color: black;
            border: 1px solid #ccc;
            padding: 10px 15px;
            cursor: pointer;
            margin-bottom: 10px;
        }}
        #sidebarContent {{
            max-height: 90%;
            overflow-y: auto;
        }}
        h3 {{
            margin-top: 0;
        }}
    </style>
</head>
<body>
<div id="sidebar" class="sidebar">
    <div id="sidebarContent">
        <h3>Measurements</h3>
        <div id="measurements"></div>
    </div>
</div>
<button id="toggleSidebar" onclick="toggleSidebar()">Close Sidebar</button>
<div id="map"></div>
<script>
    mapboxgl.accessToken = 'pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw';

    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [{longitude}, {latitude}],
        zoom: 13,
        pitch: 45,
        bearing: 0,
        antialias: true
    }});

    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());

    map.dragRotate.enable();
    map.touchZoomRotate.enableRotation();

    const Draw = new MapboxDraw({{
        displayControlsDefault: false,
        controls: {{
            polygon: true,
            line_string: true,
            point: true,
            trash: true
        }},
    }});

    map.addControl(Draw);

    let landmarkCount = 0;
    let landmarks = [];
    let featureColors = {{}};
    let featureNames = {{}};
    let totalDistance = 0;
    let totalCost = 0;

    const pythonData = {json.dumps(data_to_js)};  // Pass Python data to JS as a JSON object

    // Use Python data in the JavaScript code
    document.getElementById('measurements').innerHTML = `
        <p>Total Pipe Distance: ${pythonData.totalDistance.toFixed(2)} km</p>
        <p>Total Pipe Cost: €${pythonData.totalCost.toFixed(2)}</p>
    `;

    function toggleSidebar() {{
        var sidebar = document.getElementById('sidebar');
        if (sidebar.classList.contains('collapsed')) {{
            sidebar.classList.remove('collapsed');
            document.getElementById('toggleSidebar').innerText = "Close Sidebar";
        }} else {{
            sidebar.classList.add('collapsed');
            document.getElementById('toggleSidebar').innerText = "Open Sidebar";
        }}
    }}
</script>
</body>
</html>
""", height=600)

# Address search using Mapbox Geocoding API
if address_search:
    geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address_search}.json?access_token={mapbox_access_token}"
    try:
        response = requests.get(geocode_url)
        if response.status_code == 200:
            geo_data = response.json()
            if len(geo_data['features']) > 0:
                coordinates = geo_data['features'][0]['center']
                latitude, longitude = coordinates[1], coordinates[0]
                st.sidebar.success(f"Address found: {geo_data['features'][0]['place_name']}")
                st.sidebar.write(f"Coordinates: Latitude {latitude}, Longitude {longitude}")
            else:
                st.sidebar.error("Address not found.")
        else:
            st.sidebar.error("Error connecting to the Mapbox API.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
