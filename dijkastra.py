import heapq
import math
 
try:
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import Normalize
    HAS_MPL = True
except ImportError:                          
    HAS_MPL = False
 
 
ROADS = [
    ("London", "Brighton", 85),
    ("London", "Southampton", 120),
    ("London", "Leicester", 160),
    ("London", "Birmingham", 190),
    ("London", "Bristol", 190),
    ("Brighton", "Southampton", 100),
    ("Southampton", "Bournemouth", 45),
    ("Southampton", "Bristol", 130),
    ("Bristol", "Birmingham", 140),
    ("Birmingham", "Wolverhampton", 25),
    ("Birmingham", "Leicester", 65),
    ("Birmingham", "Nottingham", 80),
    ("Birmingham", "Manchester", 140),
    ("Leicester", "Nottingham", 45),
    ("Nottingham", "Sheffield", 55),
    ("Sheffield", "Manchester", 60),
    ("Sheffield", "Leeds", 55),
    ("Manchester", "Liverpool", 55),
    ("Manchester", "Leeds", 70),
    ("Leeds", "Newcastle", 160),
    ("Newcastle", "Sunderland", 20),
    ("Manchester", "Newcastle", 215),
]
 
STADIUMS = {  # city -> (stadium, club)
    "London": ("Emirates Stadium", "Arsenal"),
    "Brighton": ("Amex Stadium", "Brighton"),
    "Southampton": ("St Mary's Stadium", "Southampton"),
    "Bournemouth": ("Vitality Stadium", "Bournemouth"),
    "Bristol": ("Ashton Gate", "Bristol City"),
    "Birmingham": ("Villa Park", "Aston Villa"),
    "Wolverhampton": ("Molineux", "Wolves"),
    "Leicester": ("King Power Stadium", "Leicester City"),
    "Nottingham": ("City Ground", "Nottingham Forest"),
    "Sheffield": ("Bramall Lane", "Sheffield United"),
    "Manchester": ("Old Trafford", "Manchester United"),
    "Liverpool": ("Anfield", "Liverpool"),
    "Leeds": ("Elland Road", "Leeds United"),
    "Newcastle": ("St James' Park", "Newcastle United"),
    "Sunderland": ("Stadium of Light", "Sunderland"),
}
 
COORDS = {
    "London": (-0.12, 51.50),
    "Brighton": (-0.14, 50.82),
    "Southampton": (-1.40, 50.90),
    "Bournemouth": (-1.88, 50.72),
    "Bristol": (-2.59, 51.45),
    "Birmingham": (-1.90, 52.48),
    "Wolverhampton": (-2.13, 52.59),
    "Leicester": (-1.13, 52.64),
    "Nottingham": (-1.15, 52.95),
    "Sheffield": (-1.47, 53.38),
    "Manchester": (-2.24, 53.48),
    "Liverpool": (-2.98, 53.41),
    "Leeds": (-1.55, 53.80),
    "Newcastle": (-1.61, 54.98),
    "Sunderland": (-1.38, 54.91),
}
 
AVG_SPEED_KMH = 70      
COST_PER_KM = 0.12      
 
 
def build_graph(roads):
    """Undirected weighted graph as an adjacency dict."""
    graph = {}
    for a, b, km in roads:
        graph.setdefault(a, []).append((b, km))
        graph.setdefault(b, []).append((a, km))
    return graph
 
 
def dijkstra(graph, source):
    """Return (dist, prev). dist[city] = shortest km from source;
    prev[city] = previous city on that shortest path."""
    dist = {city: float("inf") for city in graph}
    prev = {city: None for city in graph}
    dist[source] = 0
    pq = [(0, source)]                      
 
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:                     
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:                
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev
 
 
def get_path(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]
 
 

 
def draw_map(home, dist, prev, dest=None, save_as=None):
    """Draw the road network on a map-like layout.
 
    * Cities are coloured by shortest distance from `home` (green = near).
    * If `dest` is given, the shortest route home -> dest is drawn in red.
    * If `dest` is None, the whole shortest-path tree from `home` is
      highlighted (every city's best route at once).
    """
    if not HAS_MPL:
        print("Matplotlib is not installed. Run:  pip install matplotlib")
        return
 
    # Which road segments to highlight?
    highlight = set()
    if dest is not None:
        path = get_path(prev, dest)
        highlight = {frozenset(p) for p in zip(path, path[1:])}
    else:
        for city in prev:
            if prev[city] is not None:
                highlight.add(frozenset((city, prev[city])))
 
    fig, ax = plt.subplots(figsize=(8, 11))
    ax.set_aspect(1 / math.cos(math.radians(53)))     # fix lat/lon stretching
    ax.set_facecolor("#eef3f8")
 
    for a, b, km in ROADS:
        (x1, y1), (x2, y2) = COORDS[a], COORDS[b]
        on_route = frozenset((a, b)) in highlight
        ax.plot([x1, x2], [y1, y2],
                color="#d62728" if on_route else "#b0b0b0",
                linewidth=3.2 if on_route else 1.2,
                zorder=2 if on_route else 1,
                solid_capstyle="round")
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(km), fontsize=7,
                ha="center", va="center", zorder=3,
                color="#d62728" if on_route else "#555555",
                bbox=dict(boxstyle="round,pad=0.15", fc="white",
                          ec="none", alpha=0.85))
 
    
    reachable = [d for d in dist.values() if d != float("inf")]
    norm = Normalize(vmin=0, vmax=max(reachable))
    cmap = cm.RdYlGn_r
    for city, (x, y) in COORDS.items():
        is_home = city == home
        is_dest = city == dest
        ax.scatter(x, y, s=330 if (is_home or is_dest) else 190,
                   marker="*" if is_home else "o",
                   color="gold" if is_home else cmap(norm(dist[city])),
                   edgecolors="black" if (is_home or is_dest) else "#333333",
                   linewidths=2 if is_dest else 1, zorder=4)
        club = STADIUMS[city][1]
        ax.annotate(f"{city}\n{club}" if not is_home else f"{city} (HOME)\n{club}",
                    (x, y), xytext=(10, 6), textcoords="offset points",
                    fontsize=8, fontweight="bold" if (is_home or is_dest) else "normal",
                    zorder=5)
 
    
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.02)
    cbar.set_label(f"Shortest distance from {home} (km)")
 
    if dest is not None:
        title = (f"{home}  ->  {dest}   |   {dist[dest]} km, "
                 f"{hours_text(dist[dest])}, cost {dist[dest] * COST_PER_KM:.2f}")
    else:
        title = f"Shortest-path tree from {home} (red = best roads)"
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlim(-3.9, 0.9)
    ax.set_ylim(50.4, 55.3)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
 
    if save_as:
        fig.savefig(save_as, dpi=150)
        print(f"Map saved to {save_as}")
    plt.show()
 
 

 
def hours_text(km):
    minutes = round(km / AVG_SPEED_KMH * 60)
    return f"{minutes // 60}h {minutes % 60:02d}m"
 
 
def print_all_trips(home, dist, prev):
    print(f"\nAWAY TRIPS FROM {home.upper()}  (sorted nearest -> farthest)")
    print("=" * 96)
    print(f"{'Club':<19}{'Stadium':<21}{'City':<14}{'km':>5}{'Time':>9}{'Cost':>8}  Route")
    print("-" * 96)
    rows = sorted((c for c in STADIUMS if c != home), key=lambda c: dist[c])
    for city in rows:
        stadium, club = STADIUMS[city]
        km = dist[city]
        route = " > ".join(get_path(prev, city))
        print(f"{club:<19}{stadium:<21}{city:<14}{km:>5}{hours_text(km):>9}"
              f"{km * COST_PER_KM:>8.2f}  {route}")
    print("-" * 96)
 
 
def print_one_trip(home, dest, dist, prev):
    stadium, club = STADIUMS[dest]
    path = get_path(prev, dest)
    print(f"\n{club} - {stadium}, {dest}")
    print(f"Shortest distance : {dist[dest]} km")
    print(f"Travel time       : {hours_text(dist[dest])} at {AVG_SPEED_KMH} km/h")
    print(f"Estimated cost    : {dist[dest] * COST_PER_KM:.2f}")
    print("Route             : " + " > ".join(path))
 
 
def pick_city(prompt, cities):
    for i, c in enumerate(cities, 1):
        print(f"  {i:>2}. {c}")
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(cities):
            return cities[int(raw) - 1]
        match = [c for c in cities if c.lower() == raw.lower()]
        if match:
            return match[0]
        print("Invalid choice, try again.")
 
 
def main():
    graph = build_graph(ROADS)
    cities = sorted(graph)
    print("=" * 50)
    print("  FOOTBALL MONK - AWAY-TRIP ROUTE PLANNER")
    print("  (Dijkstra shortest-path algorithm)")
    print("=" * 50)
 
    print("\nSelect your HOME city:")
    home = pick_city("Enter number or name: ", cities)
    dist, prev = dijkstra(graph, home)
 
    while True:
        print(f"\nHome city: {home}")
        print("1. Show shortest trip to ALL away stadiums")
        print("2. Plan a trip to ONE stadium")
        print("3. Change home city")
        print("4. Show MAP of all best routes from home")
        print("5. Save MAP of all best routes as PNG")
        print("6. Exit")
        choice = input("Choose: ").strip()
 
        if choice == "1":
            print_all_trips(home, dist, prev)
        elif choice == "2":
            dest = pick_city("Destination (number or name): ", cities)
            if dest == home:
                print("That is your home city - no travel needed!")
            else:
                print_one_trip(home, dest, dist, prev)
                if input("Show this route on the map? (y/n): ").strip().lower() == "y":
                    draw_map(home, dist, prev, dest=dest)
        elif choice == "3":
            home = pick_city("New home city (number or name): ", cities)
            dist, prev = dijkstra(graph, home)
        elif choice == "4":
            draw_map(home, dist, prev)
        elif choice == "5":
            draw_map(home, dist, prev, save_as=f"routes_from_{home.lower()}.png")
        elif choice == "6":
            print("Enjoy the away day!")
            break
        else:
            print("Please enter 1-6.")
 
 
if __name__ == "__main__":
    main()