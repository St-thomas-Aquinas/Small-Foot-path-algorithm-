import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from geopy.distance import geodesic

st.set_page_config(layout="wide")
st.title("Murang'a University Path Collector")

# Initialize session state
if "paths" not in st.session_state:
    st.session_state.paths = {}  # stores all paths
if "current_path" not in st.session_state:
    st.session_state.current_path = []  # stores points for current path
if "path_name" not in st.session_state:
    st.session_state.path_name = ""

# Input path name
st.session_state.path_name = st.text_input("Enter Path Name:", value=st.session_state.path_name)

# Buttons
col1, col2, col3 = st.columns(3)
with col1:
    add_point = st.button("Add Point Manually")  # optional manual add
with col2:
    undo = st.button("Undo Last Point")
with col3:
    save_path = st.button("Save Current Path")

download = st.button("Download All Paths")

# Initialize map
start_coords = [-0.715917, 37.147006]
m = folium.Map(location=start_coords, zoom_start=18, tiles=None)

# Satellite as default
folium.TileLayer('Esri.WorldImagery', name="Satellite", control=True, show=True).add_to(m)
# Street map
folium.TileLayer('OpenStreetMap', name="Street Map", control=True, show=False).add_to(m)
folium.LayerControl().add_to(m)

# Function to interpolate points every 10 meters
def interpolate_points(points, interval=10):
    if len(points) < 2:
        return points
    result = [points[0]]
    for i in range(1, len(points)):
        start, end = points[i-1], points[i]
        dist = geodesic(start, end).meters
        if dist <= interval:
            result.append(end)
            continue
        num = int(dist // interval)
        lat_step = (end[0] - start[0]) / num
        lon_step = (end[1] - start[1]) / num
        for j in range(1, num+1):
            result.append([start[0] + lat_step*j, start[1] + lon_step*j])
    return result

# Handle undo
if undo and st.session_state.current_path:
    st.session_state.current_path.pop()

# Handle save
if save_path and st.session_state.path_name:
    if st.session_state.current_path:
        st.session_state.paths[st.session_state.path_name] = st.session_state.current_path.copy()
        st.session_state.current_path = []
        st.session_state.path_name = ""
        st.success("Path saved!")

# Handle download
if download and st.session_state.paths:
    json_data = json.dumps(st.session_state.paths, indent=4)
    st.download_button("Download JSON", data=json_data, file_name="paths.json")

# Display existing paths
for name, path in st.session_state.paths.items():
    folium.PolyLine(interpolate_points(path), color="blue", weight=3).add_to(m)
    for pt in path:
        folium.Marker(location=pt, popup=name).add_to(m)

# Display current path
for pt in st.session_state.current_path:
    folium.CircleMarker(location=pt, radius=5, color="red").add_to(m)
if st.session_state.current_path:
    folium.PolyLine(interpolate_points(st.session_state.current_path), color="red", weight=3).add_to(m)

# Capture clicks
map_data = st_folium(m, height=600, width=1000)
if map_data and map_data.get("last_clicked"):
    click_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
    if not st.session_state.current_path or st.session_state.current_path[-1] != click_coords:
        st.session_state.current_path.append(click_coords)

st.markdown("**Current Path Points:**")
st.write(st.session_state.current_path)
