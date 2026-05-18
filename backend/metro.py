import os
import heapq
from collections import defaultdict
from flask import Flask, jsonify, request
from flask_cors import CORS                        # FIX 1: CORS import

app = Flask(__name__)
CORS(app)                                          # FIX 1: allow React to call Flask


# ─────────────────────────────────────────────────────────────
# STATION DATA
# Ameerpet split into (Red) and (Blue) so interchange is modeled
# properly as a real edge with real walking time
# ─────────────────────────────────────────────────────────────
SAMPLE_DATA = [
    # Red Line ──────────────────────────────────────────────
    {"station": "Miyapur",          "line": "Red",   "prev_station": "-",              "distance_km": 0.0, "time_min": 0},
    {"station": "JNTU College",     "line": "Red",   "prev_station": "Miyapur",         "distance_km": 1.5, "time_min": 2},
    {"station": "KPHB Colony",      "line": "Red",   "prev_station": "JNTU College",    "distance_km": 1.2, "time_min": 2},
    {"station": "Kukatpally",       "line": "Red",   "prev_station": "KPHB Colony",     "distance_km": 1.0, "time_min": 2},
    {"station": "Balanagar",        "line": "Red",   "prev_station": "Kukatpally",      "distance_km": 1.8, "time_min": 3},
    {"station": "Moosapet",         "line": "Red",   "prev_station": "Balanagar",       "distance_km": 1.3, "time_min": 2},
    {"station": "Bharat Nagar",     "line": "Red",   "prev_station": "Moosapet",        "distance_km": 1.1, "time_min": 2},
    {"station": "Erragadda",        "line": "Red",   "prev_station": "Bharat Nagar",    "distance_km": 1.2, "time_min": 2},
    {"station": "ESI Hospital",     "line": "Red",   "prev_station": "Erragadda",       "distance_km": 1.0, "time_min": 2},
    {"station": "SR Nagar",         "line": "Red",   "prev_station": "ESI Hospital",    "distance_km": 1.1, "time_min": 2},
    {"station": "Yusufguda",        "line": "Red",   "prev_station": "SR Nagar",        "distance_km": 1.3, "time_min": 2},
    {"station": "Ameerpet (Red)",   "line": "Red",   "prev_station": "Yusufguda",       "distance_km": 2.0, "time_min": 3},  # FIX 3
    {"station": "Panjagutta",       "line": "Red",   "prev_station": "Ameerpet (Red)",  "distance_km": 1.8, "time_min": 3},
    {"station": "Irrum Manzil",     "line": "Red",   "prev_station": "Panjagutta",      "distance_km": 1.0, "time_min": 2},
    {"station": "Khairatabad",      "line": "Red",   "prev_station": "Irrum Manzil",    "distance_km": 1.1, "time_min": 2},
    {"station": "Lakdi Ka Pul",     "line": "Red",   "prev_station": "Khairatabad",     "distance_km": 1.2, "time_min": 2},
    {"station": "Assembly",         "line": "Red",   "prev_station": "Lakdi Ka Pul",    "distance_km": 0.9, "time_min": 2},
    {"station": "Nampally",         "line": "Red",   "prev_station": "Assembly",        "distance_km": 0.8, "time_min": 2},
    {"station": "Gandhi Bhavan",    "line": "Red",   "prev_station": "Nampally",        "distance_km": 0.9, "time_min": 2},
    {"station": "Osmania Medical",  "line": "Red",   "prev_station": "Gandhi Bhavan",   "distance_km": 1.0, "time_min": 2},
    {"station": "MG Bus Station",   "line": "Red",   "prev_station": "Osmania Medical", "distance_km": 0.8, "time_min": 2},
    {"station": "Malakpet",         "line": "Red",   "prev_station": "MG Bus Station",  "distance_km": 1.2, "time_min": 2},
    {"station": "New Market",       "line": "Red",   "prev_station": "Malakpet",        "distance_km": 1.0, "time_min": 2},
    {"station": "Musarambagh",      "line": "Red",   "prev_station": "New Market",      "distance_km": 1.1, "time_min": 2},
    {"station": "Dilsukhnagar",     "line": "Red",   "prev_station": "Musarambagh",     "distance_km": 1.3, "time_min": 2},
    {"station": "Chaitanyapuri",    "line": "Red",   "prev_station": "Dilsukhnagar",    "distance_km": 1.4, "time_min": 2},
    {"station": "Victoria Memorial","line": "Red",   "prev_station": "Chaitanyapuri",   "distance_km": 1.2, "time_min": 2},
    {"station": "LB Nagar",         "line": "Red",   "prev_station": "Victoria Memorial","distance_km": 1.5, "time_min": 3},

    # Blue Line ─────────────────────────────────────────────
    {"station": "Nagole",           "line": "Blue",  "prev_station": "-",              "distance_km": 0.0, "time_min": 0},
    {"station": "Uppal",            "line": "Blue",  "prev_station": "Nagole",          "distance_km": 2.1, "time_min": 3},
    {"station": "Stadium",          "line": "Blue",  "prev_station": "Uppal",           "distance_km": 1.8, "time_min": 3},
    {"station": "NGRI",             "line": "Blue",  "prev_station": "Stadium",         "distance_km": 1.5, "time_min": 2},
    {"station": "Habsiguda",        "line": "Blue",  "prev_station": "NGRI",            "distance_km": 1.3, "time_min": 2},
    {"station": "Tarnaka",          "line": "Blue",  "prev_station": "Habsiguda",       "distance_km": 1.2, "time_min": 2},
    {"station": "Mettuguda",        "line": "Blue",  "prev_station": "Tarnaka",         "distance_km": 1.4, "time_min": 2},
    {"station": "Secunderabad East","line": "Blue",  "prev_station": "Mettuguda",       "distance_km": 1.6, "time_min": 3},
    {"station": "Parade Grounds",   "line": "Blue",  "prev_station": "Secunderabad East","distance_km": 1.3, "time_min": 2},
    {"station": "Paradise",         "line": "Blue",  "prev_station": "Parade Grounds",  "distance_km": 1.5, "time_min": 2},
    {"station": "Rasoolpura",       "line": "Blue",  "prev_station": "Paradise",        "distance_km": 1.1, "time_min": 2},
    {"station": "Prakash Nagar",    "line": "Blue",  "prev_station": "Rasoolpura",      "distance_km": 1.0, "time_min": 2},
    {"station": "Begumpet",         "line": "Blue",  "prev_station": "Prakash Nagar",   "distance_km": 1.2, "time_min": 2},
    {"station": "Ameerpet (Blue)",  "line": "Blue",  "prev_station": "Begumpet",        "distance_km": 1.4, "time_min": 2},  # FIX 3
    {"station": "Punjagutta",       "line": "Blue",  "prev_station": "Ameerpet (Blue)", "distance_km": 1.3, "time_min": 2},
    {"station": "Erramanzil",       "line": "Blue",  "prev_station": "Punjagutta",      "distance_km": 1.1, "time_min": 2},
    {"station": "Jubilee Hills",    "line": "Blue",  "prev_station": "Erramanzil",      "distance_km": 1.5, "time_min": 2},
    {"station": "Peddamma Gudi",    "line": "Blue",  "prev_station": "Jubilee Hills",   "distance_km": 1.4, "time_min": 2},
    {"station": "Madhapur",         "line": "Blue",  "prev_station": "Peddamma Gudi",   "distance_km": 1.6, "time_min": 3},
    {"station": "Durgam Cheruvu",   "line": "Blue",  "prev_station": "Madhapur",        "distance_km": 1.3, "time_min": 2},
    {"station": "HITEC City",       "line": "Blue",  "prev_station": "Durgam Cheruvu",  "distance_km": 1.2, "time_min": 2},
    {"station": "Raidurg",          "line": "Blue",  "prev_station": "HITEC City",      "distance_km": 1.5, "time_min": 3},

    # Green Line ────────────────────────────────────────────
    {"station": "JBS Parade Grounds","line": "Green","prev_station": "-",              "distance_km": 0.0, "time_min": 0},
    {"station": "Secunderabad West", "line": "Green","prev_station": "JBS Parade Grounds","distance_km": 1.2, "time_min": 2},
    {"station": "Gandhi Hospital",   "line": "Green","prev_station": "Secunderabad West","distance_km": 1.0, "time_min": 2},
    {"station": "Musheerabad",       "line": "Green","prev_station": "Gandhi Hospital",  "distance_km": 1.1, "time_min": 2},
    {"station": "RTC X Roads",       "line": "Green","prev_station": "Musheerabad",      "distance_km": 1.3, "time_min": 2},
    {"station": "Chikkadpally",      "line": "Green","prev_station": "RTC X Roads",      "distance_km": 1.0, "time_min": 2},
    {"station": "Narayanguda",       "line": "Green","prev_station": "Chikkadpally",     "distance_km": 1.2, "time_min": 2},
    {"station": "Sultan Bazar",      "line": "Green","prev_station": "Narayanguda",      "distance_km": 1.1, "time_min": 2},
    {"station": "MG Bus Station (Green)","line":"Green","prev_station":"Sultan Bazar",   "distance_km": 0.9, "time_min": 2},
]


# ─────────────────────────────────────────────────────────────
# INTERCHANGE DATA                                   FIX 3
# These model the physical walk between platforms
# at stations where multiple lines meet
# ─────────────────────────────────────────────────────────────
INTERCHANGE_DATA = [
    {
        "station_a":     "Ameerpet (Red)",
        "station_b":     "Ameerpet (Blue)",
        "walk_time_min": 3,
        "distance_km":   0.1
    },
    {
        "station_a":     "MG Bus Station",
        "station_b":     "MG Bus Station (Green)",
        "walk_time_min": 3,
        "distance_km":   0.1
    },
    {
        "station_a":     "Secunderabad East",
        "station_b":     "Secunderabad West",
        "walk_time_min": 4,
        "distance_km":   0.2
    },
]


# ─────────────────────────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────────────────────────
def load_metro_graph():
    graph = defaultdict(lambda: {"edges": []})

    # Step 1 — normal line edges
    for entry in SAMPLE_DATA:
        station = entry["station"]
        line    = entry["line"]
        prev    = entry.get("prev_station")
        dist    = float(entry.get("distance_km", 0))
        t       = float(entry.get("time_min", 0))

        if prev and prev not in ["-", ""]:
            graph[prev]["edges"].append({
                "to":             station,
                "line":           line,
                "distance_km":    dist,
                "time_min":       t,
                "is_interchange": False          # normal track edge
            })
            graph[station]["edges"].append({
                "to":             prev,
                "line":           line,
                "distance_km":    dist,
                "time_min":       t,
                "is_interchange": False
            })
        else:
            graph[station]                       # make sure station exists in graph

    # Step 2 — interchange (platform walk) edges        FIX 3
    for ic in INTERCHANGE_DATA:
        a         = ic["station_a"]
        b         = ic["station_b"]
        walk_time = float(ic["walk_time_min"])
        walk_dist = float(ic["distance_km"])

        graph[a]["edges"].append({
            "to":             b,
            "line":           "INTERCHANGE",
            "distance_km":    walk_dist,
            "time_min":       walk_time,
            "is_interchange": True               # platform walk edge
        })
        graph[b]["edges"].append({
            "to":             a,
            "line":           "INTERCHANGE",
            "distance_km":    walk_dist,
            "time_min":       walk_time,
            "is_interchange": True
        })

    return dict(graph)


# ─────────────────────────────────────────────────────────────
# CACHE THE GRAPH ONCE AT STARTUP                    FIX 2
# Instead of rebuilding on every request, build once here.
# All API calls reuse this same object.
# ─────────────────────────────────────────────────────────────
graph = load_metro_graph()


# ─────────────────────────────────────────────────────────────
# DIJKSTRA'S ALGORITHM WITH LINE PENALTY
# State = (station, line) because the same station on two
# different lines has different future costs
# ─────────────────────────────────────────────────────────────
def dijkstra(start, target, interchange_penalty=5.0):
    if start not in graph or target not in graph:
        return None

    # priority queue: (time_so_far, dist_so_far, station, current_line)
    pq = []
    heapq.heappush(pq, (0.0, 0.0, start, None))

    best_time = defaultdict(lambda: float("inf"))
    best_dist = defaultdict(lambda: float("inf"))
    parent    = {}

    best_time[(start, None)] = 0.0
    best_dist[(start, None)] = 0.0

    while pq:
        time_so_far, dist_so_far, station, cur_line = heapq.heappop(pq)

        # skip if we already found a better way to reach this (station, line)
        if time_so_far > best_time[(station, cur_line)]:
            continue

        for edge in graph.get(station, {}).get("edges", []):
            nxt            = edge["to"]
            edge_line      = edge["line"]
            travel_time    = edge.get("time_min", 0.0)
            travel_dist    = edge.get("distance_km", 0.0)
            is_interchange = edge.get("is_interchange", False)

            # penalty logic:
            # - interchange edge: walk time already included, no extra penalty
            # - switching lines on a normal edge: add interchange_penalty       FIX 4
            if is_interchange:
                penalty = 0.0
            elif cur_line is not None and edge_line != cur_line:
                penalty = interchange_penalty
            else:
                penalty = 0.0

            nt = time_so_far + travel_time + penalty
            nd = dist_so_far + travel_dist

            if nt < best_time[(nxt, edge_line)] or (
                nt == best_time[(nxt, edge_line)] and nd < best_dist[(nxt, edge_line)]
            ):
                best_time[(nxt, edge_line)] = nt
                best_dist[(nxt, edge_line)] = nd
                parent[(nxt, edge_line)]    = (station, cur_line, travel_dist, travel_time, penalty)
                heapq.heappush(pq, (nt, nd, nxt, edge_line))

    # pick the best line to arrive at target on
    candidates = [
        (best_time[(target, l)], best_dist[(target, l)], l)
        for (s, l) in best_time.keys()
        if s == target
    ]
    if not candidates:
        return None

    best_time_val, best_dist_val, best_line = min(candidates, key=lambda x: x[0])
    if best_time_val == float("inf"):
        return None

    # reconstruct path by following parent breadcrumbs backward
    route   = []
    st_line = (target, best_line)
    while True:
        station_name, line_name = st_line
        route.append({"station": station_name, "line": line_name})
        if station_name == start and line_name is None:
            break
        if st_line not in parent:
            break
        prev_station, prev_line, _, _, _ = parent[st_line]
        st_line = (prev_station, prev_line)

    route.reverse()

    # count transfers — ignore INTERCHANGE edges, they are not "transfers"
    # a transfer is when the metro line color changes
    transfers = 0
    prev_line = None
    for item in route:
        if item["line"] not in [None, "INTERCHANGE"]:
            if prev_line is not None and item["line"] != prev_line:
                transfers += 1
            prev_line = item["line"]

    return {
        "source":             start,
        "target":             target,
        "route":              route,
        "total_time_min":     round(best_time_val, 1),
        "total_distance_km":  round(best_dist_val, 2),
        "transfers":          transfers,
        "interchange_penalty": interchange_penalty,
    }


# ─────────────────────────────────────────────────────────────
# FARE CALCULATOR
# Distance slabs + transfer fee
# ─────────────────────────────────────────────────────────────
def compute_fare(distance_km, transfers=0, transfer_fee=5):
    d = distance_km
    if d <= 0:   base = 0
    elif d < 2:  base = 10
    elif d < 4:  base = 15
    elif d < 6:  base = 25
    elif d < 8:  base = 30
    elif d < 10: base = 35
    elif d < 14: base = 40
    elif d < 18: base = 45
    elif d < 22: base = 50
    elif d < 26: base = 55
    else:        base = 60
    return base + transfers * transfer_fee


# ─────────────────────────────────────────────────────────────
# HELPER — format seconds into "X Hrs Y Mins Z Secs"
# ─────────────────────────────────────────────────────────────
def format_time(total_minutes):
    total_seconds = int(total_minutes * 60)
    hours         = total_seconds // 3600
    minutes       = (total_seconds % 3600) // 60
    seconds       = total_seconds % 60

    parts = []
    if hours:
        parts.append(f"{hours} Hr" if hours == 1 else f"{hours} Hrs")
    if minutes:
        parts.append(f"{minutes} Min" if minutes == 1 else f"{minutes} Mins")
    if seconds:
        parts.append(f"{seconds} Sec" if seconds == 1 else f"{seconds} Secs")
    return " ".join(parts) if parts else "0 Secs"


# ─────────────────────────────────────────────────────────────
# HELPER — resolve "Ameerpet" → ["Ameerpet (Red)", "Ameerpet (Blue)"]
# so users can type plain station names without the line suffix
# ─────────────────────────────────────────────────────────────
def resolve_station(name):
    name_clean = name.strip().lower()

    # exact match first
    for s in graph:
        if s.lower() == name_clean:
            return [s]

    # partial match — handles "Ameerpet" → variants
    variants = [s for s in graph if s.lower().startswith(name_clean)]
    return variants if variants else []


# ─────────────────────────────────────────────────────────────
# API ENDPOINT 1 — GET /stations
# Returns all station names grouped by line
# Frontend uses this to populate dropdowns
# ─────────────────────────────────────────────────────────────
@app.route("/stations", methods=["GET"])
def get_stations():
    lines = defaultdict(list)
    for entry in SAMPLE_DATA:
        # show clean names (strip the "(Red)"/"(Blue)" suffix for display)
        display_name = entry["station"].split(" (")[0]
        line         = entry["line"]
        if display_name not in lines[line]:
            lines[line].append(display_name)
    return jsonify({"stations": lines})


# ─────────────────────────────────────────────────────────────
# API ENDPOINT 2 — GET /route?source=X&target=Y
# Returns shortest route, time, distance, fare
# ─────────────────────────────────────────────────────────────
@app.route("/route", methods=["GET"])
def get_route():
    source       = request.args.get("source", "").strip()
    target       = request.args.get("target", "").strip()
    penalty      = float(request.args.get("penalty", 5))
    transfer_fee = float(request.args.get("transfer_fee", 5))

    # validate inputs
    if not source or not target:
        return jsonify({"error": "Both source and target station names are required."}), 400

    if source.lower() == target.lower():
        return jsonify({"error": "Source and destination cannot be the same station."}), 400

    # resolve station names to internal graph keys
    source_nodes = resolve_station(source)
    target_nodes = resolve_station(target)

    if not source_nodes:
        return jsonify({"error": f"Station '{source}' not found. Please check the spelling."}), 404
    if not target_nodes:
        return jsonify({"error": f"Station '{target}' not found. Please check the spelling."}), 404

    # try all source/target combinations (handles interchange variants)
    # pick the one with the lowest total time
    best_result = None
    for s in source_nodes:
        for t in target_nodes:
            result = dijkstra(s, t, interchange_penalty=penalty)
            if result:
                if best_result is None or result["total_time_min"] < best_result["total_time_min"]:
                    best_result = result

    if not best_result:
        return jsonify({"error": f"No route found between '{source}' and '{target}'."}), 404

    # add fare and human-readable time
    fare = compute_fare(best_result["total_distance_km"], best_result["transfers"], transfer_fee)
    best_result["fare"]           = fare
    best_result["formatted_time"] = format_time(best_result["total_time_min"])

    # clean up route for frontend — remove internal suffixes like "(Red)"
    for stop in best_result["route"]:
        stop["station"] = stop["station"].split(" (")[0]

    return jsonify(best_result)


# ─────────────────────────────────────────────────────────────
# START SERVER
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)