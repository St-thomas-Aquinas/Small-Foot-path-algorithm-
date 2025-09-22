import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
from geopy.distance import geodesic
import json

st.set_page_config(layout="wide")
st.title("Smart Path Router - Murang'a University")

# -------------------------
# Path data (hardcoded)
# -------------------------
paths_data = {
    "paths": {
        "path1": [
            [-0.714814546364534, 37.147957642222316],
            [-0.7148564526163115, 37.14779771550067],
            [-0.7149047286196931, 37.14779100997859],
            [-0.7149496521223785, 37.14775144739825],
            [-0.7149516636224961, 37.1477548001593],
            [-0.7150167021255684, 37.14758917376366],
            [-0.7150678246986607, 37.14758230736107],
            [-0.7151683997013337, 37.147318780328476]
        ],
        "path2": [
            [-0.7151342041984061, 37.147392541075874],
            [-0.7149994336921439, 37.14735431959939],
            [-0.7148948356847321, 37.147520616556065],
            [-0.7148606401815373, 37.14777676750759]
        ]
    }
}
paths = list(paths_data["paths"].values())

# -------------------------
# Graph utilities
# -------------------------
def build_graph(paths):
    G = nx.Graph()
    for path in paths:
        for i in range(len(path) - 1):
            p1, p2 = tuple(path[i]), tuple(path[i + 1])
            dist = geodesic(p1, p2).meters
            G.add_edge(p1, p2, weight=dist)
    return G

def nearest_node(point, graph):
    return min(graph.nodes, key=lambda n: geodesic(point, n).meters)

def find_route(paths, current, destination):
    G = build_graph(paths)
    start = nearest_node(current, G)
    end = nearest_node(destination, G)
    try:
        route = nx.shortest_path(G, start, end, weight="weight")
        return [current] + route + [destination]
    except nx.NetworkXNoPath:
        return None

# -------------------------
# Session state
# -------------------------
if "route" not in st.session_state:
    st.session_state.route = None
if "current" not in st.session_state:
    st.session_state.current = None
if "destination" not in st.session_state:
    st.session_state.destination = None
if "map" not in st.session_state:   # ✅ persist the map itself
    st.session_state.map = None

# -------------------------
# User Input
# -------------------------
st.subheader("Enter Coordinates")

current_input = st.text_input("Current Location (lat, lng)", "-0.7151, 37.1474")
destination_input = st.text_input("Destination Location (lat, lng)", "-0.7149, 37.1507")

try:
    current = [float(x.strip()) for x in current_input.split(",")]
    destination = [float(x.strip()) for x in destination_input.split(",")]
except:
    current, destination = None, None

# -------------------------
# Buttons
# -------------------------
if st.button("Compute Route"):
    if current and destination:
        st.session_state.current = current
        st.session_state.destination = destination
        st.session_state.route = find_route(paths, current, destination)

        # Build map ONCE
        m = folium.Map(location=[-0.715917, 37.147006], zoom_start=17, tiles="OpenStreetMap")

        # Draw paths (fixed colors, no random)
        colors = ["red", "green", "orange", "purple", "brown"]
        for idx, path in enumerate(paths):
            folium.PolyLine(path, color=colors[idx % len(colors)], weight=3, opacity=0.6).add_to(m)

        # Add markers
        folium.Marker(current, popup="Current", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(destination, popup="Destination", icon=folium.Icon(color="red")).add_to(m)

        # Add route if found
        if st.session_state.route:
            folium.PolyLine(st.session_state.route, color="blue", weight=6, opacity=0.9).add_to(m)

        st.session_state.map = m  # ✅ save map so it doesn’t redraw randomly

if st.button("Reset"):
    st.session_state.current = None
    st.session_state.destination = None
    st.session_state.route = None
    st.session_state.map = None

# -------------------------
# Show Map
# -------------------------
if st.session_state.map:
    st_folium(st.session_state.map, width=800, height=500)

# -------------------------
# Show Route JSON
# -------------------------
if st.session_state.route:
    route_json = json.dumps({"route": st.session_state.route}, indent=2)
    st.subheader("📍 Computed Route (JSON)")
    st.code(route_json, language="json")
    st.download_button(
        label="⬇️ Download Route JSON",
        data=route_json,
        file_name="route.json",
        mime="application/json"
    )
