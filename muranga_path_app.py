import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import math

# -------------------
# Example paths (replace with yours)
# -------------------
paths = [
    [
        (-0.714814546364534, 37.147957642222316),
        (-0.7148564526163115, 37.14779771550067),
        (-0.7149047286196931, 37.14779100997859),
        (-0.7149496521223785, 37.14775144739825),
    ],
    [
        (-0.7151342041984061, 37.147392541075874),
        (-0.7149994336921439, 37.14735431959939),
        (-0.7148948356847321, 37.147520616556065),
        (-0.7148606401815373, 37.14777676750759),
    ],
]

# -------------------
# Helpers
# -------------------
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi/2)**2 +
         math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2)
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_nearest_point(coord, paths):
    nearest = None
    min_dist = float("inf")
    for path in paths:
        for pt in path:
            d = haversine(coord, pt)
            if d < min_dist:
                min_dist = d
                nearest = pt
    return nearest

# -------------------
# Session state init
# -------------------
if "m" not in st.session_state:
    # Initialize folium map only once!
    st.session_state.m = folium.Map(
        location=[37.1479, -0.7150],
        zoom_start=18,
        tiles="Esri.WorldImagery"
    )

if "route" not in st.session_state:
    st.session_state.route = None

# -------------------
# Sidebar inputs
# -------------------
st.sidebar.header("Route Finder")
current = st.sidebar.text_input("Current Location (lat,lon)", "-0.7149,37.1479")
destination = st.sidebar.text_input("Destination (lat,lon)", "-0.7151,37.1473")

if st.sidebar.button("Compute Route"):
    try:
        current = tuple(map(float, current.split(",")))
        destination = tuple(map(float, destination.split(",")))

        start = find_nearest_point(current, paths)
        end = find_nearest_point(destination, paths)

        # For demo: just connect start → end directly
        st.session_state.route = [current, start, end, destination]

        # Add to map
        folium.Marker(location=current, popup="Current", icon=folium.Icon(color="green")).add_to(st.session_state.m)
        folium.Marker(location=destination, popup="Destination", icon=folium.Icon(color="red")).add_to(st.session_state.m)
        folium.PolyLine(st.session_state.route, color="blue", weight=5).add_to(st.session_state.m)

    except Exception as e:
        st.error(f"Error: {e}")

# -------------------
# Show map without flicker
# -------------------
st_folium(st.session_state.m, width=700, height=500)

# -------------------
# Show & download route JSON
# -------------------
if st.session_state.route:
    st.json(st.session_state.route)
    st.download_button(
        "Download Route JSON",
        json.dumps(st.session_state.route, indent=2),
        file_name="route.json",
        mime="application/json"
    )
