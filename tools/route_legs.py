"""Route geometry and text anchors for the map prototype (used by build_proto_data.py).

- anchors(): orders stops and text waypoints by their place in the book (passage, char offset), so every
  waypoint falls between the right two stops and every person mention gets the nearest preceding anchor
  (date + place). Nothing is book-specific: offsets come from the quotes stored with stops and waypoints.
- fill_coords(): a waypoint known only by latitude (or longitude) gets the missing value interpolated
  between the neighbouring fully known points; marked "interp" so the map can say so.
- sea_leg(): densified great circle; if it crosses land (Natural Earth 50m), searoute (Apache-2.0,
  modern shipping network) with Suez and Panama closed, as in the 1850s.
"""
import json
import math
import os
import re
import urllib.request

LAND_URL = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/ne_50m_land.geojson"


def norm(s):
    return " ".join((s or "").split())


def find_offset(body, quote):
    """Char offset of a quote in a normalised body; quotes with '...' are matched by their longest piece."""
    q = norm(quote)
    if not q:
        return -1
    i = body.find(q)
    if i >= 0:
        return i
    for part in sorted(re.split(r"\s*(?:\.\.\.|…)\s*", q), key=len, reverse=True):
        if len(part) >= 8:
            i = body.find(part)
            if i >= 0:
                return i
    return -1


# ---------- geometry ----------
def gc_dist(a, b):  # (lon, lat) → km
    l1, p1, l2, p2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(h)))


def gc_line(a, b, step_km=40):
    d = gc_dist(a, b)
    n = max(2, math.ceil(d / step_km))
    l1, p1, l2, p2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    D = d / 6371
    out = []
    for i in range(n + 1):
        f = i / n
        if D < 1e-9:
            out.append([a[0], a[1]])
            continue
        A, B = math.sin((1 - f) * D) / math.sin(D), math.sin(f * D) / math.sin(D)
        x = A * math.cos(p1) * math.cos(l1) + B * math.cos(p2) * math.cos(l2)
        y = A * math.cos(p1) * math.sin(l1) + B * math.cos(p2) * math.sin(l2)
        z = A * math.sin(p1) + B * math.sin(p2)
        out.append([math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))])
    return out


class Land:
    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(LAND_URL, path)
        self.rings = []  # (minx, miny, maxx, maxy, ring)
        for f in json.load(open(path, encoding="utf-8"))["features"]:
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for p in polys:
                r = p[0]
                xs, ys = [c[0] for c in r], [c[1] for c in r]
                self.rings.append((min(xs), min(ys), max(xs), max(ys), r))

    def inland(self, lon, lat, km=40):
        """On land and farther than km from any coast vertex."""
        if not self.has(lon, lat):
            return False
        d = 1e9
        for x0, y0, x1, y1, r in self.rings:
            if x0 - 2 <= lon <= x1 + 2 and y0 - 2 <= lat <= y1 + 2:
                for c in r:
                    if abs(c[1] - lat) < 1 and abs(c[0] - lon) < 2:
                        d = min(d, gc_dist((lon, lat), c))
        return d > km

    def has(self, lon, lat):
        inside = False
        for x0, y0, x1, y1, r in self.rings:
            if x0 <= lon <= x1 and y0 <= lat <= y1:
                c = False
                for i in range(len(r)):
                    (xa, ya), (xb, yb) = r[i - 1][:2], r[i][:2]
                    if (ya > lat) != (yb > lat) and lon < (xb - xa) * (lat - ya) / (yb - ya) + xa:
                        c = not c
                inside ^= c  # lakes are separate holes in ne_land only as rings[1:], ignored
        return inside


def crosses_land(land, line, skip_km=15):
    """True if an inner point of the line is on land (ends near ports are skipped)."""
    a, b = line[0], line[-1]
    for p in line[1:-1]:
        if gc_dist(p, a) < skip_km or gc_dist(p, b) < skip_km:
            continue
        if land.has(p[0], p[1]):
            return True
    return False


def sea_leg(land, a, b):
    """a, b = (lon, lat). Returns (coords, how)."""
    line = gc_line(a, b)
    if not crosses_land(land, line):
        return line, "gc"
    if land.inland(*a) or land.inland(*b):
        return line, "gc-land"  # river or lake: the sea network does not know this water
    try:
        import searoute
        r = searoute.searoute(list(a), list(b), append_orig_dest=True, restrictions=["suez", "panama", "northwest"])
        coords = [list(c) for c in r["geometry"]["coordinates"]]
        dense = [coords[0]]
        for p in coords[1:]:
            dense += gc_line(dense[-1], p)[1:]
        return dense, "searoute"
    except ImportError:
        return line, "gc-land"


ROUTER = "https://routing.openstreetmap.de/routed-{}/route/v1/driving/{},{};{},{}?overview=simplified&geometries=geojson"


class Roads:
    """Land legs along today's roads/paths (OSRM, OpenStreetMap). Old post roads mostly lie under modern roads,
    so this is a much better guess than a straight line. Results are cached in a committed json file, so the
    build is reproducible offline. A route that is far longer than the straight line (no road there in fact,
    e.g. Siberian rivers, the Okhotsk track) is rejected and the leg stays a straight line."""

    def __init__(self, path):
        self.path = path
        self.cache = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
        self.dirty = False

    def leg(self, a, b, mode):
        prof = "foot" if mode == "foot" else "car"
        key = f"{prof}:{a[0]:.4f},{a[1]:.4f};{b[0]:.4f},{b[1]:.4f}"
        if key not in self.cache:
            import time
            url = ROUTER.format(prof, a[0], a[1], b[0], b[1])
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ltsgo-kb/0.1"})
                r = json.load(urllib.request.urlopen(req, timeout=30))
                rt = r["routes"][0] if r.get("code") == "Ok" else None
                snap = max(w.get("distance", 0) for w in r.get("waypoints", [{}])) if rt else 0
                self.cache[key] = {"km": round(rt["distance"] / 1000, 1), "snap_m": round(snap),
                                   "coords": [[round(x, 4), round(y, 4)] for x, y in rt["geometry"]["coordinates"]]} \
                    if rt else {"km": None}
            except Exception as e:  # network down: leave uncached, straight line this time
                print("router:", key, e)
                return None
            self.dirty = True
            time.sleep(1.1)  # public server: max 1 request/second
        c = self.cache[key]
        d = gc_dist(a, b)
        if not c.get("km") or c["snap_m"] > 20000 or c["km"] > 2.2 * d + 25:
            return None
        return [list(a)] + c["coords"] + [list(b)]

    def save(self):
        if self.dirty:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(self.cache, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


RIVERS_URL = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/ne_10m_rivers_lake_centerlines.geojson"


class Rivers:
    """Natural Earth 10m river centrelines as a graph: a boat (or a sledge on winter ice) follows the river
    between two points instead of cutting across land. Lines that touch (< 2 km) are joined, so a trip can
    pass from a tributary to the main river (Maya → Aldan → Lena)."""

    def __init__(self, path):
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(RIVERS_URL, path)
        self.pts, self.adj, self.grid = [], [], {}
        idx = {}

        def node(c):
            k = (round(c[0], 4), round(c[1], 4))
            if k not in idx:
                idx[k] = len(self.pts)
                self.pts.append(k)
                self.adj.append([])
                self.grid.setdefault((int(k[0] // 0.5), int(k[1] // 0.5)), []).append(idx[k])
            return idx[k]

        ends = []
        for f in json.load(open(path, encoding="utf-8"))["features"]:
            g = f["geometry"]
            if not g:
                continue
            for line in ([g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]):
                ids = [node(c) for c in line]
                for u, v in zip(ids, ids[1:]):
                    d = gc_dist(self.pts[u], self.pts[v])
                    self.adj[u].append((v, d))
                    self.adj[v].append((u, d))
                ends += [ids[0], ids[-1]]
        for u in ends:  # join line ends to any vertex within 2 km
            v, d = self.near(self.pts[u], 2, exclude=u)
            if v is not None:
                self.adj[u].append((v, d))
                self.adj[v].append((u, d))

    def near(self, p, km, exclude=None):
        gx, gy = int(p[0] // 0.5), int(p[1] // 0.5)
        best, bd = None, km
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for i in self.grid.get((gx + dx, gy + dy), ()):
                    if i == exclude:
                        continue
                    d = gc_dist(p, self.pts[i])
                    if d < bd:
                        best, bd = i, d
        return best, bd

    def leg(self, a, b, snap_km=25):
        import heapq
        s, _ = self.near(a, snap_km)
        t, _ = self.near(b, snap_km)
        if s is None or t is None or s == t:
            return None
        dist, prev, h = {s: 0}, {}, [(0, s)]
        limit = 2.5 * gc_dist(a, b) + 30
        while h:
            d, u = heapq.heappop(h)
            if u == t:
                break
            if d > dist.get(u, 1e18) or d > limit:
                continue
            for v, w in self.adj[u]:
                nd = d + w
                if nd < dist.get(v, 1e18):
                    dist[v], prev[v] = nd, u
                    heapq.heappush(h, (nd, v))
        if t not in dist or dist[t] > limit:
            return None
        path, u = [t], t
        while u != s:
            u = prev[u]
            path.append(u)
        return [list(a)] + [list(self.pts[i]) for i in reversed(path)] + [list(b)]


def unwrap(coords):
    """Keep longitudes continuous so MapLibre does not draw a line across the whole map."""
    out = []
    for lon, lat in coords:
        if out:
            pl = out[-1][0]
            while lon - pl > 180:
                lon -= 360
            while lon - pl < -180:
                lon += 360
        out.append([round(lon, 4), round(lat, 4)])
    return out


def to_sea(land, c, step=0.05, max_deg=4):
    """An interpolated point that fell on land is moved along its unknown coordinate to the nearest water."""
    if not land.has(c["lon"], c["lat"]):
        return
    for k in range(1, int(max_deg / step) + 1):
        for sgn in (1, -1):
            lon, lat = c["lon"], c["lat"]
            if c.get("interp") == "lat":
                lat += sgn * k * step
            else:
                lon += sgn * k * step
            if not land.has(lon, lat):
                # a little off the coast, so the line does not clip it
                if c.get("interp") == "lat":
                    lat += sgn * 0.15
                else:
                    lon += sgn * 0.15
                c["lon"], c["lat"] = round(lon, 3), round(lat, 3)
                return


# ---------- anchors ----------
def fill_coords(chain):
    """chain: list of dicts with lat/lon (None where unknown). Fills gaps, sets 'interp'."""
    known = [i for i, c in enumerate(chain) if c["lat"] is not None and c["lon"] is not None]
    for i, c in enumerate(chain):
        if c["lat"] is not None and c["lon"] is not None:
            continue
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        if prev is None or nxt is None:
            continue
        P, N = chain[prev], chain[nxt]
        frac = (i - prev) / (nxt - prev)
        if c["lat"] is not None and abs(N["lat"] - P["lat"]) > 1e-6:
            f = (c["lat"] - P["lat"]) / (N["lat"] - P["lat"])
            frac = f if 0 <= f <= 1 else frac
        elif c["lon"] is not None and abs(N["lon"] - P["lon"]) > 1e-6:
            f = (c["lon"] - P["lon"]) / (N["lon"] - P["lon"])
            frac = f if 0 <= f <= 1 else frac
        if c["lat"] is None:
            c["lat"], c["interp"] = round(P["lat"] + (N["lat"] - P["lat"]) * frac, 3), "lat"
        if c["lon"] is None:
            c["lon"], c["interp"] = round(P["lon"] + (N["lon"] - P["lon"]) * frac, 3), "lon"
