import streamlit as st
import folium
import json
from math import radians, cos, sin, sqrt, atan2

# ---------------------------
# Distance function (Haversine)
# ---------------------------
def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ---------------------------
# Path dataset (example routes)
# ---------------------------
paths = [
    [(-0.7160, 37.1488), (-0.7158, 37.1486)],
    [(-0.7146, 37.1484), (-0.7146, 37.1486)],
    [(-0.7157, 37.1499), (-0.7149, 37.1507)]
]

# ---------------------------
# Algorithm
# ---------------------------
def compute_route(start, dest, paths):
    route = [start]
    current = start
    visited = set()

    while True:
        # Find best path to move onto
        best_path = None
        best_dist = float("inf")
        best_end = None

        for i, path in enumerate(paths):
            if i in visited:  # don’t reuse paths
                continue
            for end in [path[0], path[-1]]:
                dist_to_path = haversine(current, end)
                dist_to_dest = haversine(end, dest)
                if dist_to_path < best_dist and dist_to_dest < haversine(current, dest):
                    best_dist = dist_to_path
                    best_path = path
                    best_end = end

        if not best_path:
            break  # no more connections

        visited.add(paths.index(best_path))

        # Choose direction
        if haversine(current, best_path[0]) < haversine(current, best_path[-1]):
            route.extend(best_path)
            current = best_path[-1]
        else:
            route.extend(reversed(best_path))
            current = best_path[0]

        if haversine(current, dest) < 0.05:  # within ~50m
            break

    route.append(dest)
    return route

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("Pathfinding Algorithm Demo")

start_lat = st.number_input("Start Latitude", value=-0.7159, format="%.6f")
start_lon = st.number_input("Start Longitude", value=37.1470, format="%.6f")
end_lat = st.number_input("End Latitude", value=-0.7200, format="%.6f")
end_lon = st.number_input("End Longitude", value=37.1500, format="%.6f")

if st.button("Compute Path"):
    start = (start_lat, start_lon)
    dest = (end_lat, end_lon)

    # Run algorithm
    route = compute_route(start, dest, paths)

    # Save JSON
    route_json = {"route": route}
    with open("route.json", "w") as f:
        json.dump(route_json, f)

    # Create static map
    m = folium.Map(location=start, zoom_start=15)
    folium.Marker(start, popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(dest, popup="End", icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine(route, color="blue", weight=4).add_to(m)

    m.save("map.html")

    st.success("✅ Path computed. Map saved as map.html")
    st.download_button("Download Route JSON", data=json.dumps(route_json), file_name="route.json", mime="application/json")
    with open("map.html", "rb") as f:
        st.download_button("Download Map (HTML)", data=f, file_name="map.html", mime="text/html")
