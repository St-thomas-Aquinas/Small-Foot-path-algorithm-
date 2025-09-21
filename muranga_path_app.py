import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import json
import random

# --- Initialize session state ---
if 'paths' not in st.session_state:
    st.session_state.paths = {}  # path_name: list of points
if 'current_path' not in st.session_state:
    st.session_state.current_path = []
if 'path_name' not in st.session_state:
    st.session_state.path_name = ''
if 'path_colors' not in st.session_state:
    st.session_state.path_colors = {}  # path_name: color

# --- Interpolation function ---
def interpolate_points(p1, p2, distance_m=10):
    total_distance = geodesic(p1, p2).meters
    num_points = int(total_distance // distance_m)
    if num_points == 0:
        return [p2]
    lat_step = (p2[0] - p1[0]) / (num_points + 1)
    lon_step = (p2[1] - p1[1]) / (num_points + 1)
    points = []
    for i in range(1, num_points + 1):
        points.append([p1[0] + lat_step * i, p1[1] + lon_step * i])
    points.append(p2)
    return points

# --- Sidebar: Enter path name ---
st.sidebar.title("Path Collector - Murang'a University")
path_name_input = st.sidebar.text_input("Enter Path Name", st.session_state.path_name)
st.session_state.path_name = path_name_input

# --- Main Map ---
m = folium.Map(location=[-0.7159, 37.1470], zoom_start=18)

# Draw all saved paths
for name, path_points in st.session_state.paths.items():
    color = st.session_state.path_colors.get(name, "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]))
    st.session_state.path_colors[name] = color
    folium.PolyLine(path_points, color=color, weight=4).add_to(m)
    # Label the first point of the path
    folium.Marker(location=path_points[0], popup=name, icon=folium.DivIcon(html=f"""<div style="font-size: 12pt; color:{color}; font-weight:bold">{name}</div>""")).add_to(m)

# Draw the currently collected path
if st.session_state.current_path:
    for i in range(len(st.session_state.current_path)-1):
        segment = interpolate_points(st.session_state.current_path[i], st.session_state.current_path[i+1])
        folium.PolyLine(segment, color="blue").add_to(m)
    for point in st.session_state.current_path:
        folium.CircleMarker(location=point, radius=3, color="red").add_to(m)

# Display the map
map_data = st_folium(m, width=700, height=500, returned_objects=[])

# --- Handle clicks ---
if map_data and map_data.get('last_clicked'):
    new_point = [map_data['last_clicked']['lat'], map_data['last_clicked']['lng']]
    st.session_state.current_path.append(new_point)

# --- Save current path ---
if st.button("Save Current Path"):
    if st.session_state.path_name:
        # Interpolate points for the entire path
        full_path = []
        for i in range(len(st.session_state.current_path)-1):
            full_path.extend(interpolate_points(st.session_state.current_path[i], st.session_state.current_path[i+1]))
        full_path.insert(0, st.session_state.current_path[0])
        
        st.session_state.paths[st.session_state.path_name] = full_path
        st.session_state.current_path = []
        st.success(f"Path '{st.session_state.path_name}' saved!")
    else:
        st.warning("Please enter a path name before saving.")

# --- Download all paths ---
if st.session_state.paths:
    json_data = json.dumps(st.session_state.paths, indent=2)
    st.download_button("Download All Paths JSON", json_data, file_name="paths.json")
