import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Plot Path on OpenStreetMap")

# -------------------------------
# Input coordinates as text
# -------------------------------
coord_input = st.text_area(
    "Enter your path coordinates in the format [[lon, lat], [lon, lat], ...]:",
    "[[-0.714814546364534, 37.147957642222316], [-0.7148564526163115, 37.14779771550067], [-0.7149047286196931, 37.14779100997859], [-0.7149496521223785, 37.14775144739825], [-0.7149516636224961, 37.1477548001593], [-0.7150167021255684, 37.14758917376366], [-0.7150678246986607, 37.14758230736107], [-0.7151683997013337, 37.147318780328476], [-0.7151342041984061, 37.147392541075874], [-0.7149994336921439, 37.14735431959939], [-0.7148948356847321, 37.147520616556065], [-0.7148606401815373, 37.14777676750759], [-0.7157378335958583, 37.147665690028624]]"
)

# -------------------------------
# Convert input to list of coordinates
# -------------------------------
try:
    path_coords = eval(coord_input)  # Converts string to Python list
    if not isinstance(path_coords, list) or not all(isinstance(pt, list) and len(pt) == 2 for pt in path_coords):
        st.error("Invalid format. Make sure it's a list of [lon, lat] pairs.")
        st.stop()
except Exception as e:
    st.error(f"Error parsing input: {e}")
    st.stop()

# -------------------------------
# Create Folium Map with OpenStreetMap tiles
# -------------------------------
if path_coords:
    # Center map at first coordinate
    m = folium.Map(
        location=[path_coords[0][1], path_coords[0][0]], 
        zoom_start=18, 
        tiles="OpenStreetMap"  # <- Use real-world OpenStreetMap tiles
    )

    # Plot the path as a line
    lats, lons = zip(*path_coords)
    folium.PolyLine(list(zip(lats, lons)), color="blue", weight=5, opacity=0.8).add_to(m)

    # Add markers for start and end
    folium.Marker(location=[path_coords[0][1], path_coords[0][0]], popup="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(location=[path_coords[-1][1], path_coords[-1][0]], popup="End", icon=folium.Icon(color="red")).add_to(m)

    # Display map in Streamlit
    st_folium(m, width=700, height=500)
