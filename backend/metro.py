import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


class Graph_M:
    class Vertex:
        def __init__(self):
            self.nbrs = {}

    def __init__(self):
        self.vtces = {}

    def num_vertex(self):
        return len(self.vtces)

    def contains_vertex(self, v_name):
        return v_name in self.vtces

    def add_vertex(self, v_name):
        self.vtces[v_name] = self.Vertex()

    def remove_vertex(self, v_name):
        vtx = self.vtces[v_name]
        for key in vtx.nbrs:
            nbr_vtx = self.vtces[key]
            nbr_vtx.nbrs.pop(v_name)
        self.vtces.pop(v_name)

    def num_edges(self):
        count = 0
        for key in self.vtces:
            vtx = self.vtces[key]
            count += len(vtx.nbrs)
        return count // 2

    def contains_edge(self, v_name1, v_name2):
        return (
            v_name1 in self.vtces
            and v_name2 in self.vtces
            and v_name2 in self.vtces[v_name1].nbrs
        )

    def add_edge(self, v_name1, v_name2, value):
        if (
            v_name1 not in self.vtces
            or v_name2 not in self.vtces
            or v_name2 in self.vtces[v_name1].nbrs
        ):
            return
        self.vtces[v_name1].nbrs[v_name2] = value
        self.vtces[v_name2].nbrs[v_name1] = value

    def remove_edge(self, v_name1, v_name2):
        if not self.contains_edge(v_name1, v_name2):
            return
        self.vtces[v_name1].nbrs.pop(v_name2)
        self.vtces[v_name2].nbrs.pop(v_name1)

    def display_map(self):
        print("\t Hyderabad Metro Map")
        print("\t------------------")
        print("----------------------------------------------------\n")
        for key in self.vtces:
            strn = f"{key} =>\n"
            vtx = self.vtces[key]
            for nbr in vtx.nbrs:
                strn += f"\t{nbr}\t"
                if len(nbr) < 16:
                    strn += "\t"
                if len(nbr) < 8:
                    strn += "\t"
                strn += f"{str(vtx.nbrs[nbr])}\n"
            print(strn)
        print("\t------------------")
        print("---------------------------------------------------\n")

    def display_stations(self):
        print(
            "\n***********************************************************************\n"
        )
        i = 1
        for key in self.vtces:
            print(f"{i}. {key}")
            i += 1
        print(
            "\n***********************************************************************\n"
        )

    def has_path(self, v_name1, v_name2, processed):
        if self.contains_edge(v_name1, v_name2):
            return True
        processed[v_name1] = True
        vtx = self.vtces[v_name1]
        for nbr in vtx.nbrs:
            if nbr not in processed and self.has_path(nbr, v_name2, processed):
                return True
        return False

    class DijkstraPair:
        def __init__(self):
            self.vname = ""
            self.psf = ""
            self.cost = 0

        def __lt__(self, other):
            return self.cost < other.cost

    class Pair:
        def __init__(self):
            self.v_name = ""
            self.psf = ""
            self.min_dis = 0
            self.min_time = 0

    def get_minimum_distance(self, src, dst):
        mini = float("inf")
        ans = ""
        processed = {}
        stack = []
        sp = self.Pair()
        sp.v_name = src
        sp.psf = src + "  "
        sp.min_dis = 0
        sp.min_time = 0
        stack.append(sp)
        while stack:
            rp = stack.pop(0)
            if rp.v_name in processed:
                continue
            processed[rp.v_name] = True
            if rp.v_name == dst:
                temp = rp.min_dis
                if temp < mini:
                    ans = rp.psf
                    mini = temp
                continue
            rpvtx = self.vtces[rp.v_name]
            nbrs = list(rpvtx.nbrs.keys())
            for nbr in nbrs:
                if nbr not in processed:
                    np = self.Pair()
                    np.v_name = nbr
                    np.psf = rp.psf + nbr + "  "
                    np.min_dis = rp.min_dis + rpvtx.nbrs[nbr]
                    stack.append(np)
        ans += str(mini)
        return ans

    def get_interchanges(self, s):
        arr = []
        res = s.split("  ")
        if not res or len(res) < 2:
            return arr
        
        arr.append(res[0])
        count = 0
        i = 1
        while i < len(res) - 1:
            station = res[i]
            
            # Safety check: ensure station contains "~"
            if "~" not in station:
                # If no "~" found, treat as regular station
                arr.append(station)
                i += 1
                continue
                
            try:
                index = station.index("~")
                line_color = station[index + 1:]
                
                if len(line_color) == 2:  # Valid line color (like "B", "R", "G")
                    # Check previous and next stations for line colors
                    prev_station = res[i - 1]
                    next_station = res[i + 1] if i + 1 < len(res) - 1 else None
                    
                    if "~" in prev_station and next_station and "~" in next_station:
                        prev_color = prev_station[prev_station.index("~") + 1:]
                        next_color = next_station[next_station.index("~") + 1:]
                        
                        if prev_color == next_color:
                            arr.append(station)
                        else:
                            # Line change detected
                            arr.append(f"{station} ==> {next_station}")
                            i += 1  # Skip next station as it's part of interchange
                            count += 1
                    else:
                        arr.append(station)
                else:
                    arr.append(station)
                    
            except (ValueError, IndexError) as e:
                # If any error occurs with parsing, just add the station as-is
                arr.append(station)
                
            i += 1
            
        arr.append(str(count))
        arr.append(res[len(res) - 1])
        return arr

    def cost(self, d):
        if 0 <= d < 2:
            return 10
        elif 2 <= d < 4:
            return 15
        elif 4 <= d < 6:
            return 25
        elif 6 <= d < 8:
            return 30
        elif 8 <= d < 10:
            return 35
        elif 10 <= d < 14:
            return 40
        elif 14 <= d < 18:
            return 45
        elif 18 <= d < 22:
            return 50
        elif 22 <= d < 26:
            return 55
        else:
            return 60

    def create_metro_map(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        stations_file_path = os.path.join(current_directory, "stations.csv")
        edges_file_path = os.path.join(current_directory, "edges.csv")

        with open(stations_file_path, "r") as fptr:
            for row in fptr:
                self.add_vertex(row.strip())

        with open(edges_file_path, "r") as fptr:
            prev = fptr.readline().strip()
            flag = False
            for row in fptr:
                row = row.strip()
                if row == "":
                    flag = True
                    continue
                if flag:
                    prev = row
                    flag = False
                    continue
                lis = row.split(",")
                cur, val = lis[0], float(lis[1])
                self.add_edge(prev, cur, val)
                prev = cur


@app.route("/get_elements", methods=["GET"])
def get_elements():
    try:
        lis = [[]]
        current_directory = os.path.dirname(os.path.realpath(__file__))
        edges_file_path = os.path.join(current_directory, "edges.csv")

        with open(edges_file_path, "r") as fptr:
            for row in fptr:
                row = row.strip()
                if row == "":
                    lis.append([])
                    continue
                lis[-1].append(row.split(",")[0].split("~")[0])
        data = {"BlueLine": lis[0], "RedLine": lis[1], "GreenLine": lis[2]}
        return jsonify(elements=data)
    except Exception as e:
        return jsonify(error=str(e))


@app.route("/", methods=["POST"])
def calculate_sum():
    g = Graph_M()
    g.create_metro_map()
    try:
        data = request.get_json()
        lis = list(g.vtces.keys())
        st1 = ""
        for st in lis:
            # Extract station name (part before ~)
            station_name = st.split("~")[0] if "~" in st else st
            if data["source_station"].strip().lower() == station_name.lower():
                st1 = st
                break
        st2 = ""
        for st in lis:
            # Extract station name (part before ~)
            station_name = st.split("~")[0] if "~" in st else st
            if data["destination_station"].strip().lower() == station_name.lower():
                st2 = st
                break
        
        # Validate that both stations were found
        if not st1:
            return jsonify(error=f"Source station '{data['source_station']}' not found. Please check the spelling.")
        if not st2:
            return jsonify(error=f"Destination station '{data['destination_station']}' not found. Please check the spelling.")
        
        path_result = g.get_minimum_distance(st1, st2)
        arr = g.get_interchanges(path_result)
        print(f"get_interchanges returned: {arr}")  # Debug print
        print(f"Length of arr: {len(arr)}")  # Debug print
        length = len(arr)
        dis = round(float(arr[length - 1]), 1)
        ts = dis * 109
        tm = ts // 60
        th = tm // 60
        tm, ts = tm - th * 60, ts - tm * 60
        time = ""
        if th > 0:
            if th == 1:
                time += "1 Hr "
            else:
                time += f"{round(th)} Hrs "
        if tm > 0:
            if tm == 1:
                time += "1 Min "
            else:
                time += f"{round(tm)} Mins "
        if ts > 0:
            if ts == 1:
                time += "1 Sec "
            else:
                time += f"{round(ts)} Secs "
        print(f"Number of Interchanges : {arr[length - 2]}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"Start  ==>  {arr[0]}")
        for i in range(1, length - 3):
            print(arr[i])
        print(f"{arr[length - 3]}  ==>  End")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        if not time:
            time = "0 Secs"
        
        # Extract intermediate stations (clean station names without ~line)
        intermediate_stations = []
        for i in range(1, length - 3):
            station_name = arr[i].split("~")[0] if "~" in arr[i] else arr[i]
            # Remove " ==> " if present (for interchange stations)
            if " ==> " in station_name:
                parts = station_name.split(" ==> ")
                intermediate_stations.extend([part.strip() for part in parts])
            else:
                intermediate_stations.append(station_name)
        
        return jsonify(
            {
                "res": {
                    "source_station": st1.split("~")[0],
                    "destination_station": st2.split("~")[0],
                    "distance": f"{dis} KM",
                    "time": time,
                    "cost": f"Rs. {g.cost(dis)}",
                    "intermediate_stations": intermediate_stations
                }
            }
        )
    except Exception as e:
        return jsonify(error=str(e))


if __name__ == "__main__":
    app.run(debug=True)