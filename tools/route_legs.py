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
