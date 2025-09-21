import streamlit as st
import folium
from streamlit_folium import st_folium
import json

st.title("Path Collector - Murang'a University")

# Input for path name
path_name = st.text_input("Enter Path Name:")

# Initialize session state for coordinates
if "coords" not in st.session_state:
    st.session_state.coords = []

st.write("Click points on the map to collect coordinates:")

# Create map centered at Murang'a University
m = folium.Map(location=[-0.716, 37.147], zoom_start=18)

# Add existing coordinates as markers
for coord in st.session_state.coords:
    folium.Marker(coord).add_to(m)

# Only draw polyline if there are 2 or more points
if len(st.session_state.coords) >= 2:
    folium.PolyLine(st.session_state.coords, color="blue").add_to(m)

# Display map
map_data = st_folium(m, width=700, height=500)

# Capture click
if map_data and map_data.get("last_clicked"):
    click = map_data["last_clicked"]
    coord = [click["lat"], click["lng"]]
    if coord not in st.session_state.coords:
        st.session_state.coords.append(coord)
        st.experimental_rerun()  # Refresh map with new point

# Save button
if st.button("Save Path"):
    if path_name and st.session_state.coords:
        path_data = {
            "path_name": path_name,
            "coordinates": st.session_state.coords
        }
        st.code(json.dumps(path_data, indent=4))
        st.success("Path saved!")
        st.session_state.coords = []  # clear for next path
    else:
        st.warning("Add points and enter a path name before saving.")
