import streamlit as st
import folium
from streamlit_folium import st_folium
import math

# --------- Your PATH DATA (from your JSON) ----------
paths = {
    "path_1": [[-0.7167694762790855, 37.1473851799965], [-0.7166970623018618, 37.14736372232438], [-0.7165938053312044, 37.147318124771125]],
    "path_2": [[-0.7164905483605469, 37.14727252721787], [-0.7164476363713693, 37.14738920331002], [-0.7164047243821917, 37.14750587940217]],
    # 👆 Add all your other paths here...
}

# --------- Helper Functions ----------
def haversine(coord1, coord2):
    """Calculate distance (m) between two coordinates."""
    R = 6371000
    lat1, lon1 = math.radians(coord1[1]), math.radians(coord1[0])
    lat2, lon2 = math.radians(coord2[1]), math.radians(coord2[0])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

def find_route(start, end, paths):
    """Greedy path selection: connect closest path ends towards destination."""
    route = [start]
    current = start
    visited = set()

    while True:
        best_path, best_point, best_dist = None, None, float("inf")

        for name, coords in paths.items():
            if name in visited:
                continue
            for point in [coords[0], coords[-1]]:
                dist = haversine(current, point) + haversine(point, end)
                if dist < best_dist:
                    best_path, best_point, best_dist = name, point, dist

        if not best_path:
            break

        route.extend(paths[best_path])
        current = paths[best_path][-1]
        visited.add(best_path)

        if haversine(current, end) < 15:  # within 15m of destination
            break

    route.append(end)
    return route

# --------- Streamlit App ----------
st.title("Path Finder (Static Map)")

# Input coordinates
start_lat = st.number_input("Start Latitude", value=37.14738)
start_lon = st.number_input("Start Longitude", value=-0.71676)
end_lat = st.number_input("End Latitude", value=37.14930)
end_lon = st.number_input("End Longitude", value=-0.71543)

start = [start_lon, start_lat]
end = [end_lon, end_lat]

if st.button("Compute Path"):
    route = find_route(start, end, paths)

    # Create folium map
    m = folium.Map(location=[start[1], start[0]], zoom_start=18)

    # Draw all paths in gray
    for coords in paths.values():
        folium.PolyLine(coords, color="gray", weight=2).add_to(m)

    # Draw computed route in red
    folium.PolyLine(route, color="red", weight=5).add_to(m)

    # Markers
    folium.Marker(location=[start[1], start[0]], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=[end[1], end[0]], popup="End", icon=folium.Icon(color="red")).add_to(m)

    # Show map ONCE, stays static
    st_data = st_folium(m, width=800, height=600)
