import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
from geopy.distance import geodesic
import random
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
        ],
        "path3": [
            [-0.715629937051089, 37.14766494952171],
            [-0.7154801166920283, 37.147742710452036]
        ],
        "path4": [
            [-0.7155711467841884, 37.147652621569335],
            [-0.7153653808441333, 37.147627965664604],
            [-0.7151118452974426, 37.14755611289417],
            [-0.7150919112127436, 37.147599173868905]
        ],
        "path5": [
            [-0.7159448909055013, 37.14789053584701],
            [-0.7158316653217964, 37.148081120543985],
            [-0.7157431579976851, 37.14820631634759],
            [-0.715834854773609, 37.14846228993569],
            [-0.7158149206925866, 37.14862895187662],
            [-0.7157694709863144, 37.148637723556654]
        ],
        "path6": [
            [-0.7160191315032673, 37.14880272867365],
            [-0.7158564693981494, 37.1486583946657]
        ],
        "path7": [
            [-0.7157639752576376, 37.14854516024594],
            [-0.7155439148734409, 37.14831401249866],
            [-0.7153860369315764, 37.148204765208476],
            [-0.7152209827141457, 37.148170475912195],
            [-0.7148175168261874, 37.14798786547217]
        ],
        "path8": [
            [-0.7146644577932663, 37.14844453949386],
            [-0.7146293738007091, 37.14861279626549]
        ],
        "path9": [
            [-0.7157269782570342, 37.14997082391014],
            [-0.7149009222772399, 37.150788897605175]
        ]
    }
}

paths = list(paths_data["paths"].values())

# -------------------------
# Build routing graph
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
for key in ["current", "destination", "route", "map"]:
    if key not in st.session_state:
        st.session_state[key] = None

# -------------------------
# Build map once and store in session
# -------------------------
if st.session_state["map"] is None:
    m = folium.Map(
        location=[-0.715917, 37.147006],
        zoom_start=17,
        tiles="Esri.WorldImagery"
    )
    # Draw all paths initially
    for path in paths:
        color = "#" + ''.join(random.choices("0123456789ABCDEF", k=6))
        folium.PolyLine(path, color=color, weight=3, opacity=0.6).add_to(m)
    st.session_state["map"] = m

# Work with the saved map
m = st.session_state["map"]

# Draw markers and route dynamically
if st.session_state.current:
    folium.Marker(st.session_state.current, popup="Current", icon=folium.Icon(color="green")).add_to(m)
if st.session_state.destination:
    folium.Marker(st.session_state.destination, popup="Destination", icon=folium.Icon(color="red")).add_to(m)
if st.session_state.route:
    folium.PolyLine(st.session_state.route, color="blue", weight=6, opacity=0.9).add_to(m)

# Show map without forcing rerender
clicked = st_folium(m, width=800, height=500, returned_objects=[])

# Handle clicks only when not both selected
if clicked and clicked.get("last_clicked"):
    point = [clicked["last_clicked"]["lat"], clicked["last_clicked"]["lng"]]
    if not st.session_state.current:
        st.session_state.current = point
        st.success(f"✅ Selected Current Location: {point}")
    elif not st.session_state.destination:
        st.session_state.destination = point
        st.success(f"✅ Selected Destination: {point}")

# -------------------------
# Buttons
# -------------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("Compute Route"):
        if st.session_state.current and st.session_state.destination:
            st.session_state.route = find_route(paths, st.session_state.current, st.session_state.destination)
            if st.session_state.route:
                st.success("🚀 Route computed successfully!")
            else:
                st.error("❌ No path found between these points.")
        else:
            st.warning("⚠️ Please click two points on the map.")

with col2:
    if st.button("Reset"):
        for key in ["current", "destination", "route", "map"]:
            st.session_state[key] = None
        st.success("🔄 Reset complete!")

# -------------------------
# Show Route JSON + Download
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
