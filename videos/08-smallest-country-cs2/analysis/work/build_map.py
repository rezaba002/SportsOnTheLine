"""Projects Natural Earth 1:50m countries (Europe to Mongolia) into SVG paths for the video08 map scene.
Mercator, 1920x1080 frame. Writes sotl-graphics/public/data/video08_map.json: {countries: [{iso, d, cx, cy}], baltic: {x, y}}."""
import json, math, pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "research" / "raw" / "ne_50m_countries.geojson"
OUT = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data\video08_map.json")
LON0, LON1, LAT0, LAT1 = -12, 122, 33, 72          # Portugal to Mongolia
W, H = 1920, 1080

def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

my0, my1 = merc(LAT0), merc(LAT1)
sx = W / (LON1 - LON0)
sy = H / (my1 - my0)
s = min(sx, sy * 1.0)
# keep aspect: same px per unit in x (degrees->radians) and y
k = W / math.radians(LON1 - LON0)
ox = 0
oy = (H - k * (my1 - my0)) / 2

def xy(lon, lat):
    lat = max(min(lat, 84), -84)
    return (k * math.radians(lon - LON0) + ox, H - (k * (merc(lat) - my0) + oy))

def ring_path(ring):
    pts, last = [], None
    for lon, lat in ring:
        x, y = xy(lon, lat)
        p = (round(x, 1), round(y, 1))
        if p != last:
            pts.append(p); last = p
    if len(pts) < 3:
        return "", 0
    area = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
    return "M" + "L".join(f"{x},{y}" for x, y in pts) + "Z", area

g = json.load(open(SRC, encoding="utf8"))
out = []
for f in g["features"]:
    p = f["properties"]
    iso = p.get("ADM0_A3") or p.get("ISO_A3")
    if iso == "KOS": iso = "XKX"
    geom = f["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    parts, total, best = [], 0, (0, 0, 0)
    for poly in polys:
        ring = poly[0]
        lons = [c[0] for c in ring]; lats = [c[1] for c in ring]
        if max(lons) < LON0 - 5 or min(lons) > LON1 + 5 or max(lats) < LAT0 - 5 or min(lats) > LAT1 + 8:
            continue
        d, a = ring_path(ring)
        if a < 6:          # drop tiny islands
            continue
        parts.append(d); total += a
        if a > best[0]:
            xs = [xy(*c)[0] for c in ring]; ys = [xy(*c)[1] for c in ring]
            best = (a, sum(xs) / len(xs), sum(ys) / len(ys))
    if parts:
        out.append({"iso": iso, "d": "".join(parts), "cx": round(best[1], 1), "cy": round(best[2], 1)})

bx, by = xy(19.5, 58.3)        # Baltic Sea label
OUT.write_text(json.dumps({"w": W, "h": H, "countries": out, "baltic": {"x": round(bx), "y": round(by)}}), encoding="utf8")
print(len(out), "countries", OUT.stat().st_size // 1024, "KB; Baltic label at", round(bx), round(by))
for iso in ("EST", "LVA", "DNK", "MNG", "FIN", "XKX", "SWE", "LTU"):
    c = next((c for c in out if c["iso"] == iso), None)
    print(iso, (c["cx"], c["cy"]) if c else "MISSING")
