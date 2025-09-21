import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.title("Path Collector - Murang'a University")

# Initialize session state
if "coords" not in st.session_state:
    st.session_state.coords = []

if "paths" not in st.session_state:
    st.session_state.paths = []

# Input for current path name
path_name = st.text_input("Enter Path Name:")

st.write("Click points on the map to collect coordinates:")

# Create map centered at Murang'a University
m = folium.Map(location=[-0.716, 37.147], zoom_start=18)

# Add markers for current path
for coord in st.session_state.coords:
    folium.Marker(coord, icon=folium.Icon(color="blue")).add_to(m)

# Draw current path polyline
if len(st.session_state.coords) >= 2:
    folium.PolyLine(st.session_state.coords, color="blue", weight=4).add_to(m)

# Draw previously saved paths
for path in st.session_state.paths:
    if len(path["coordinates"]) >= 2:
        folium.PolyLine(path["coordinates"], color="green", weight=3, opacity=0.6).add_to(m)
    for c in path["coordinates"]:
        folium.CircleMarker(location=c, radius=3, color="green", fill=True).add_to(m)

# Display the map and capture clicks
map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

# Capture single click without refreshing
if map_data and map_data["last_clicked"]:
    click = map_data["last_clicked"]
    coord = [click["lat"], click["lng"]]
    if coord not in st.session_state.coords:
        st.session_state.coords.append(coord)
        st.success(f"Point added: {coord}")

# Button to save current path
if st.button("Save Current Path"):
    if path_name and st.session_state.coords:
        path_data = {
            "path_name": path_name,
            "coordinates": st.session_state.coords
        }
        st.session_state.paths.append(path_data)
        st.success(f"Path '{path_name}' saved!")
        st.session_state.coords = []  # Clear for next path
    else:
        st.warning("Add points and enter a path name before saving.")

# Show all saved paths
if st.session_state.paths:
    st.subheader("Saved Paths")
    st.json(st.session_state.paths)

# Button to download all paths as JSON
if st.session_state.paths:
    paths_json = json.dumps(st.session_state.paths, indent=4)
    st.download_button(
        label="Download All Paths",
        data=paths_json,
        file_name="paths.json",
        mime="application/json"
    )
