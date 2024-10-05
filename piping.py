import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

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

# Mapbox GL JS API token
mapbox_access_token = "pk.eyJ1IjoicGFyc2ExMzgzIiwiYSI6ImNtMWRqZmZreDB6MHMyaXNianJpYWNhcGQifQ.hot5D26TtggHFx9IFM-9Vw"

# Global totalDistance variable to persist
totalDistance = 0

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

    map.on('draw.create', updateMeasurements);
    map.on('draw.update', updateMeasurements);
    map.on('draw.delete', deleteFeature);

    function updateMeasurements(e) {{
        totalDistance = 0;  // Reset total distance before starting new calculations        
        const data = Draw.getAll();
        let sidebarContent = "";
        if (data.features.length > 0) {{
            const features = data.features;
            features.forEach(function (feature, index) {{
                if (feature.geometry.type === 'LineString') {{
                    const length = turf.length(feature);
                    
                    // Accumulate the length of the line into totalDistance
                    totalDistance += length;

                    let distanceUnit = length >= 1 ? 'km' : 'm';
                    let distanceValue = length >= 1 ? length.toFixed(2) : (length * 1000).toFixed(2);
                    
                    const startCoord = feature.geometry.coordinates[0];
                    const endCoord = feature.geometry.coordinates[feature.geometry.coordinates.length - 1];

                    let startLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, startCoord) < 0.01);
                    let endLandmark = landmarks.find(lm => turf.distance(lm.geometry.coordinates, endCoord) < 0.01);
                    
                    if (!featureNames[feature.id]) {{
                        const name = prompt("Enter a name for this line:");
                        featureNames[feature.id] = name || "Line " + (index + 1);
                    }}

                    if (!featureColors[feature.id]) {{
                        const lineColor = prompt("Enter a color for this line (e.g., red, purple, cyan, pink):");
                        featureColors[feature.id] = lineColor || 'blue';
                    }}

                    map.addLayer({{
                        id: 'line-' + feature.id,
                        type: 'line',
                        source: {{
                            type: 'geojson',
                            data: feature
                        }},
                        layout: {{}},
                        paint: {{
                            'line-color': featureColors[feature.id],
                            'line-width': 4
                        }}
                    }});

                    sidebarContent += '<p>Line ' + featureNames[feature.id] + ' belongs to ' + (startLandmark?.properties.name || 'Unknown') + ' - ' + (endLandmark?.properties.name || 'Unknown') + ': ' + distanceValue + ' ' + distanceUnit + '</p>';
                }} else if (feature.geometry.type === 'Polygon') {{
                    if (!feature.properties.name) {{
                        if (!featureNames[feature.id]) {{
                            const name = prompt("Enter a name for this polygon:");
                            feature.properties.name = name || "Polygon " + (index + 1);
                            featureNames[feature.id] = feature.properties.name;
                        }} else {{
                            feature.properties.name = featureNames[feature.id];
                        }}
                    }}

                    if (!featureColors[feature.id]) {{
                        const polygonColor = prompt("Enter a color for this polygon (e.g., green, yellow):");
                        featureColors[feature.id] = polygonColor || 'yellow';
                    }}

                    map.addLayer({{
                        id: 'polygon-' + feature.id,
                        type: 'fill',
                        source: {{
                            type: 'geojson',
                            data: feature
                        }},
                        paint: {{
                            'fill-color': featureColors[feature.id],
                            'fill-opacity': 0.6
                        }}
                    }});

                    const bbox = turf.bbox(feature);
                    const width = turf.distance([bbox[0], bbox[1]], [bbox[2], bbox[1]]);
                    const height = turf.distance([bbox[0], bbox[1]], [bbox[0], bbox[3]]);

                    let widthUnit = width >= 1 ? 'km' : 'm';
                    let heightUnit = height >= 1 ? 'km' : 'm';
                    let widthValue = width >= 1 ? width.toFixed(2) : (width * 1000).toFixed(2);
                    let heightValue = height >= 1 ? height.toFixed(2) : (height * 1000).toFixed(2);

                    sidebarContent += '<p>Polygon ' + feature.properties.name + ': Width = ' + widthValue + ' ' + widthUnit + ', Height = ' + heightValue + ' ' + heightUnit + '</p>';
                }} else if (feature.geometry.type === 'Point') {{
                    if (!feature.properties.name) {{
                        if (!featureNames[feature.id]) {{
                            const name = prompt("Enter a name for this landmark:");
                            feature.properties.name = name || "Landmark " + (landmarkCount + 1);
                            featureNames[feature.id] = feature.properties.name;
                            landmarks.push(feature);
                            landmarkCount++;
                        }} else {{
                            feature.properties.name = featureNames[feature.id];
                        }}
                    }}

                    if (!featureColors[feature.id]) {{
                        const markerColor = prompt("Enter a color for this landmark (e.g., black, white):");
                        featureColors[feature.id] = markerColor || 'black';
                    }}

                    map.addLayer({{
                        id: 'marker-' + feature.id,
                        type: 'circle',
                        source: {{
                            type: 'geojson',
                            data: feature
                        }},
                        paint: {{
                            'circle-radius': 8,
                            'circle-color': featureColors[feature.id]
                        }}
                    }});

                    sidebarContent += '<p>Landmark ' + feature.properties.name + '</p>';
                }}
            }});
        }} else {{
            sidebarContent = "<p>No features drawn yet.</p>";
        }}

        // Call function to calculate pipe cost based on total distance
        let pipeMaterial = prompt("Enter the pipe material (e.g., B1001, B1003, B1005, B1008):");
        totalCost = calculate_pipe_cost(pipeMaterial, totalDistance);

        // Display total distance and cost in the sidebar using JavaScript's toFixed
        sidebarContent += `<p>Total Pipe Distance: ${totalDistance.toFixed(2)} km</p>`;
        sidebarContent += `<p>Total Pipe Cost: €${totalCost.toFixed(2)}</p>`;
        document.getElementById('measurements').innerHTML = sidebarContent;
    }}

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

    function deleteFeature(e) {{
        const features = e.features;
        features.forEach(function (feature) {{
            delete featureColors[feature.id];
            delete featureNames[feature.id];

            map.removeLayer('line-' + feature.id);
            map.removeLayer('polygon-' + feature.id);
            map.removeLayer('marker-' + feature.id);
        }});
        updateMeasurements();
    }}
</script>
</body>
</html>
"""

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

# Render the Mapbox 3D Satellite map with drawing functionality and custom features
components.html(mapbox_map_html, height=600)
