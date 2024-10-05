import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Embedding the pipe cost data directly into the app (from CSV)
B1001_data = {'cost_per_meter': 12.0}  # Assume values based on the CSV
B1003_data = {'cost_per_meter': 15.0}
B1005_data = {'cost_per_meter': 20.0}
B1008_data = {'cost_per_meter': 8.0}

# Set up a title for the app
st.title("Piping Tool with Price Calculation")

# Add instructions and explain color options
st.markdown("""
This tool allows you to:
1. Draw lines representing pipes between points on the map.
2. Display distances for lines directly on the map and in the sidebar.
3. Automatically calculate the total pipe cost based on the distance drawn on the map and the selected pipe material.
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

# Mapbox GL JS API token
mapbox_access_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# HTML and JS for Mapbox with Mapbox Draw plugin to add drawing functionalities
mapbox_map_html = f"""
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
    mapboxgl.accessToken = '{mapbox_access_token}';

    const map = new mapboxgl.Map({{
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: [{longitude}, {latitude}],
        zoom: 13,
        pitch: 45, // For 3D effect
        bearing: 0, // Rotation angle
        antialias: true
    }});

    // Add map controls for zoom, rotation, and fullscreen
    map.addControl(new mapboxgl.NavigationControl());
    map.addControl(new mapboxgl.FullscreenControl());

    // Enable rotation and pitch adjustments using right-click
    map.dragRotate.enable();
    map.touchZoomRotate.enableRotation();

    // Add the Draw control for drawing polygons, markers, lines, etc.
    const Draw = new MapboxDraw({{
        displayControlsDefault: false,
        controls: {{
            polygon: false,
            line_string: true,
            point: true,
            trash: true
        }},
    }});

    map.addControl(Draw);

    let totalDistance = 0;
    let totalCost = 0;
    const pipeCosts = {{
        'B1001': {B1001_data['cost_per_meter']},
        'B1003': {B1003_data['cost_per_meter']},
        'B1005': {B1005_data['cost_per_meter']},
        'B1008': {B1008_data['cost_per_meter']}
    }};
    
    function updateMeasurements(e) {{
        totalDistance = 0;
        let sidebarContent = "";
        const data = Draw.getAll();
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function (feature) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature); // Calculate length in km
                    totalDistance += length;

                    const pipeMaterial = prompt("Enter the pipe material (B1001, B1003, B1005, B1008):");
                    const costPerMeter = pipeCosts[pipeMaterial] || 0;

                    const costForLine = costPerMeter * length * 1000; // Convert km to meters

                    sidebarContent += `<p>Line length: {length.toFixed(2)} km</p>`;
                    sidebarContent += `<p>Cost: €{costForLine.toFixed(2)}</p>`;
                }}
            }});
        }} else {{
            sidebarContent = "<p>No lines drawn yet.</p>";
        }}

        sidebarContent += `<p>Total Distance: {totalDistance.toFixed(2)} km</p>`;
        document.getElementById('measurements').innerHTML = sidebarContent;
    }}

    // Handle feature creation and updates
    map.on('draw.create', updateMeasurements);
    map.on('draw.update', updateMeasurements);
    map.on('draw.delete', updateMeasurements);

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
"""
# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)

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
