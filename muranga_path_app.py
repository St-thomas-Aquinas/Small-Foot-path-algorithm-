import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from collections import deque

st.set_page_config(layout="wide")
st.title("Murang'a University Path Routing")

# Full path data
data = {
  "path_segments": [
    {"id": 1, "coordinates": [[-0.7159173329483964, 37.1470061058908],
                               [-0.7158174284628951, 37.14693972121571],
                               [-0.715769152469106, 37.146941062320245],
                               [-0.715749037471556, 37.14698867153169],
                               [-0.7157295929738374, 37.14701549362263]]},
    {"id": 2, "coordinates": [[-0.7156289064120767, 37.14770603387747],
                               [-0.7155464349190112, 37.14772279768338],
                               [-0.7154726799239701, 37.14772816210127]]},
    {"id": 3, "coordinates": [[-0.7151593339897789, 37.14730315395433],
                               [-0.7151398894895541, 37.14741848893893],
                               [-0.7151123989891006, 37.147484873610296],
                               [-0.7150956364876797, 37.14752242453748],
                               [-0.7150621114867844, 37.14759685583568],
                               [-0.7150091419794686, 37.14759551473958],
                               [-0.7149742759778673, 37.147702803097346],
                               [-0.7149407509760816, 37.14775778838071],
                               [-0.7149025324737585, 37.147796680410394],
                               [-0.7148623024709488, 37.1478060681417]]},
    {"id": 4, "coordinates": [[-0.7151050234833092, 37.147429888327835],
                               [-0.7150259044809658, 37.14735948034305],
                               [-0.7149675709758258, 37.14734472819352],
                               [-0.7149105784723714, 37.14748017974782],
                               [-0.7148759749861965, 37.147669032233495],
                               [-0.7148551894846676, 37.14777967335244],
                               [-0.7148451319840161, 37.14780716599618],
                               [-0.7148397679835966, 37.14785946907059]]},
    {"id": 5, "coordinates": [[-0.7166485179316855, 37.1473719887538],
                               [-0.7164627894856782, 37.14752554521619],
                               [-0.7163226550205727, 37.14766367897693],
                               [-0.7162395130364033, 37.147847410295974],
                               [-0.7161831910480342, 37.147952686997165]]},
    {"id": 6, "coordinates": [[-0.7164414558818964, 37.147293068328466],
                               [-0.7164381033827903, 37.147371522940084],
                               [-0.7164159768884178, 37.14745936528369],
                               [-0.7163703410713396, 37.14755953954871],
                               [-0.7163046320870738, 37.14767085122006],
                               [-0.7162375821027, 37.147708402145284],
                               [-0.71615913361833, 37.14768895613207],
                               [-0.7160867196328624, 37.14764671134121],
                               [-0.7160605701371224, 37.147680909505546],
                               [-0.7160230221429892, 37.14774997638707],
                               [-0.7159941906470713, 37.14779959725336]]},
    {"id": 7, "coordinates": [[-0.716133654619241, 37.14758636163903],
                               [-0.7160431371367479, 37.147526682490025],
                               [-0.7160337501384468, 37.147434816833695],
                               [-0.7160853786287977, 37.14734362172959]]},
    {"id": 8, "coordinates": [[-0.7156133466874832, 37.14711630451362],
                               [-0.7157280021757636, 37.14721554624455],
                               [-0.7157952879594769, 37.14725913078142],
                               [-0.7158502689527123, 37.147304057781724]]},
    {"id": 9, "coordinates": [[-0.7167094736209859, 37.14738780402697],
                               [-0.7166967341244566, 37.1475467249106],
                               [-0.716643094140362, 37.14777605378032],
                               [-0.7165941476549472, 37.147957773440375],
                               [-0.7165552586654131, 37.14811065935458],
                               [-0.7165565996639691, 37.14827829741657],
                               [-0.7165800671564269, 37.14829103791316]]},
    {"id": 10, "coordinates": [[-0.7162825168596509, 37.14856698101218],
                                [-0.7162268653724236, 37.1484724331469],
                                [-0.7161993748779878, 37.14837520306884],
                                [-0.7161591448851905, 37.14826925581244],
                                [-0.7162060798755638, 37.148125087076735],
                                [-0.7159392209226174, 37.14794940238767]]},
    {"id": 11, "coordinates": [[-0.7161351101733997, 37.148238060655466],
                                [-0.7158689217157937, 37.14807109314646]]}
  ]
}

# Build adjacency graph of coordinates
graph = {}
for seg in data["path_segments"]:
    coords = [tuple(c) for c in seg["coordinates"]]
    for i in range(len(coords)-1):
        graph.setdefault(coords[i], []).append(coords[i+1])
        graph.setdefault(coords[i+1], []).append(coords[i])

# Initialize map
center = [-0.7159, 37.1475]
m = folium.Map(location=center, zoom_start=17)

# Draw all path segments in blue
for seg in data["path_segments"]:
    folium.PolyLine(seg["coordinates"], color="blue", weight=4).add_to(m)

# Streamlit map click selection
st.markdown("Click on the map to select your start and end points.")
map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])

# Store clicked points
if 'points' not in st.session_state:
    st.session_state.points = []

if map_data["last_clicked"]:
    st.session_state.points.append(map_data["last_clicked"])
    if len(st.session_state.points) > 2:
        st.session_state.points = st.session_state.points[-2:]

# Function to find closest path coordinate
def closest_point(coord):
    min_dist = float('inf')
    closest = None
    for point in graph.keys():
        dist = geodesic(coord, point).meters
        if dist < min_dist:
            min_dist = dist
            closest = point
    return closest

# BFS pathfinding along segments
def bfs_path(start, end):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == end:
            return path
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph.get(node, []):
            new_path = list(path)
            new_path.append(neighbor)
            queue.append(new_path)
    return None

# Highlight route
if len(st.session_state.points) == 2:
    start_click = (st.session_state.points[0]['lat'], st.session_state.points[0]['lng'])
    end_click = (st.session_state.points[1]['lat'], st.session_state.points[1]['lng'])

    start = closest_point(start_click)
    end = closest_point(end_click)

    route = bfs_path(start, end)

    if route:
        folium.PolyLine(route, color="red", weight=5, opacity=0.8).add_to(m)
        folium.Marker(location=start, tooltip="Start", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(location=end, tooltip="End", icon=folium.Icon(color='red')).add_to(m)
        st.success("Route plotted along path segments!")
    else:
        st.error("No path found along segments!")

# Redisplay map
st_folium(m, width=700, height=500)
