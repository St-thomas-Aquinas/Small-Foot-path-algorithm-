import streamlit as st
import json

# --- Route data (replace with your full path dataset) ---
ROUTES = [
    [
        [-0.7151342041984061, 37.147392541075874],
        [-0.7149994336921439, 37.14735431959939],
        [-0.7148948356847321, 37.147520616556065],
        [-0.7148606401815373, 37.14777676750759]
    ],
    [
        [-0.7159448909055013, 37.14789053584701],
        [-0.7158316653217964, 37.148081120543985],
        [-0.7157431579976851, 37.14820631634759],
        [-0.715834854773609, 37.14846228993569],
        [-0.7158149206925866, 37.14862895187662],
        [-0.7157694709863144, 37.148637723556654]
    ]
]

st.title("OpenStreetMap Route Viewer (Leaflet)")

# --- Select Start & End ---
start = st.text_input("Start (lat,lng)", "-0.7151342041984061,37.147392541075874")
end = st.text_input("End (lat,lng)", "-0.7158149206925866,37.14862895187662")

route_json = json.dumps(ROUTES)

# --- Build HTML with Leaflet ---
html_code = f"""
<!DOCTYPE html>
<html>
  <head>
    <title>Route Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
  </head>
  <body>
    <div id="map" style="height:600px; width:100%;"></div>
    <script>
      const start = [{start.split(",")[0]}, {start.split(",")[1]}];
      const end = [{end.split(",")[0]}, {end.split(",")[1]}];
      const routes = {route_json};

      const map = L.map('map').setView(start, 17);

      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        maxZoom: 20,
        attribution: '© OpenStreetMap'
      }}).addTo(map);

      // Draw routes
      routes.forEach(path => {{
        L.polyline(path, {{color: 'red', weight: 3}}).addTo(map);
      }});

      // Start marker
      L.marker(start).addTo(map).bindPopup("Start");

      // End marker
      L.marker(end).addTo(map).bindPopup("End");
    </script>
  </body>
</html>
"""

st.components.v1.html(html_code, height=600)
