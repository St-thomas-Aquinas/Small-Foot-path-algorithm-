import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from geopy.distance import geodesic

st.set_page_config(layout="wide")
st.title("Path Collector - Murang'a University (Satellite View)")

# Initialize session state
if "paths" not in st.session_state:
    st.session_state.paths = {}
if "current_path_name" not in st.session_state:
    st.session_state.current_path_name = ""
if "coords" not in st.session_state:
    st.session_state.coords = []

# Input path name
path_name = st.text_input("Enter Path Name:", value=st.session_state.current_path_name)
st.session_state.current_path_name = path_name

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    save_btn = st.button("Save Current Path")
with col2:
    undo_btn = st.button("Undo Last Point")
with col3:
    download_btn = st.button("Download All Paths")

# Undo last point
if undo_btn and st.session_state.coords:
    st.session_state.coords.pop()

# Save current path
if save_btn and path_name:
    if st.session_state.coords:
        st.session_state.paths[path_name] = st.session_state.coords.copy()
        st.session_state.coords = []
        st.success(f"Path '{path_name}' saved!")
    else:
        st.warning("No points to save!")

# Download all paths
if download_btn:
    if st.session_state.paths:
        json_data = json.dumps(st.session_state.paths, indent=2)
        st.download_button("Download Paths JSON", data=json_data, file_name="paths.json")
    else:
        st.warning("No paths to download!")

# --- Create satellite map ---
m = folium.Map(location=[-0.715917, 37.147006], zoom_start=17, tiles=None)
folium.TileLayer('Esri.WorldImagery', name="Satellite").add_to(m)
folium.TileLayer('OpenStreetMap', name="Street Map").add_to(m)
folium.LayerControl().add_to(m)

# Add existing points
for name, path_points in st.session_state.paths.items():
    folium.PolyLine(path_points, color="blue", weight=3).add_to(m)
    for i, p in enumerate(path_points):
        folium.Marker(p, popup=f"{name} Point {i+1}").add_to(m)

# Add current points
if st.session_state.coords:
    folium.PolyLine(st.session_state.coords, color="red", weight=3).add_to(m)
    for i, p in enumerate(st.session_state.coords):
        folium.Marker(p, popup=f"Current Point {i+1}").add_to(m)

# Capture clicks
map_data = st_folium(m, width=800, height=600, returned_objects=["last_clicked"])
clicked = map_data["last_clicked"]
if clicked:
    point = [clicked["lat"], clicked["lng"]]
    
    # Optional: interpolate points every 10 meters
    if st.session_state.coords:
        last = st.session_state.coords[-1]
        distance = geodesic(last, point).meters
        if distance > 10:
            # Insert intermediate points
            num_points = int(distance // 10)
            for i in range(1, num_points + 1):
                lat = last[0] + (point[0] - last[0]) * (i / (num_points + 1))
                lng = last[1] + (point[1] - last[1]) * (i / (num_points + 1))
                st.session_state.coords.append([lat, lng])
    st.session_state.coords.append(point)
