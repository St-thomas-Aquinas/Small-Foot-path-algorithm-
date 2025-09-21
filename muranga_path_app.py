import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from geopy.distance import geodesic
import random

st.set_page_config(layout="wide")

# --- Initialize session state ---
if 'paths' not in st.session_state:
    st.session_state.paths = {}  # path_name -> list of coordinates
if 'current_path' not in st.session_state:
    st.session_state.current_path = []
if 'path_name' not in st.session_state:
    st.session_state.path_name = ''
if 'path_colors' not in st.session_state:
    st.session_state.path_colors = {}

st.title("Path Collector - Murang'a University")

# --- Path name input ---
st.session_state.path_name = st.text_input("Enter Path Name:", st.session_state.path_name)

# --- Interpolation helper ---
def interpolate_points(p1, p2, interval_m=10):
    points = [p1]
    dist = geodesic(p1, p2).meters
    if dist <= interval_m:
        return [p1, p2]
    num_points = int(dist // interval_m)
    lat1, lon1 = p1
    lat2, lon2 = p2
    for i in range(1, num_points):
        fraction = i / num_points
        lat = lat1 + (lat2 - lat1) * fraction
        lon = lon1 + (lon2 - lon1) * fraction
        points.append([lat, lon])
    points.append(p2)
    return points

# --- Create map ---
m = folium.Map(location=[-0.715917, 37.147006], zoom_start=17)

# --- Draw saved paths ---
for name, pts in st.session_state.paths.items():
    c = st.session_state.path_colors.get(name, "#0000FF")
    folium.PolyLine(pts, color=c, weight=4, opacity=0.7).add_to(m)
    for pt in pts:
        folium.CircleMarker(location=pt, radius=3, color=c).add_to(m)

# --- Draw current path ---
if st.session_state.current_path:
    color = st.session_state.path_colors.get(st.session_state.path_name, "#"+''.join([random.choice('0123456789ABCDEF') for _ in range(6)]))
    st.session_state.path_colors[st.session_state.path_name] = color
    folium.PolyLine(st.session_state.current_path, color=color, weight=5).add_to(m)
    for pt in st.session_state.current_path:
        folium.CircleMarker(location=pt, radius=3, color=color).add_to(m)

# --- Capture click ---
clicked = st_folium(m, width=800, height=500)
if clicked and clicked.get("last_clicked"):
    point = [clicked["last_clicked"]["lat"], clicked["last_clicked"]["lng"]]
    if st.session_state.current_path:
        last_point = st.session_state.current_path[-1]
        interp = interpolate_points(last_point, point)
        st.session_state.current_path.extend(interp[1:])  # avoid duplicate
    else:
        st.session_state.current_path.append(point)
    st.success(f"Point added: {point}")  # show feedback

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("Save Current Path"):
        if st.session_state.path_name and st.session_state.current_path:
            st.session_state.paths[st.session_state.path_name] = st.session_state.current_path.copy()
            st.success(f"Path '{st.session_state.path_name}' saved!")
            st.session_state.current_path = []
            st.session_state.path_name = ''
with col2:
    if st.button("Download All Paths"):
        if st.session_state.paths:
            json_str = json.dumps({"paths": st.session_state.paths}, indent=2)
            st.download_button("Download JSON", data=json_str, file_name="paths.json", mime="application/json")
        else:
            st.warning("No paths to download!")
