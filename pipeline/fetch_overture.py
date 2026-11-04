"""Download the Overture Maps extracts that maryland.py reads -> data/md/

- overture_md_bbox.parquet     every place in Maryland's bounding box (name, category, address, point)
- overture_md_sources.parquet  which datasets each Maryland eating/drinking listing came from (Meta, Foursquare, ...)
- md_shapes.json               simplified state and county outlines for the map
- md_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Adapted from wi-eats/pipeline/fetch_overture.py
Maryland: land division areas, so the Chesapeake shore and its islands (Kent Island, Tilghman, Smith Island, Hooper, Deal, Solomons)
and Assateague follow the shore; the "counties" are the 23 counties plus Baltimore City, a county-level jurisdiction of its own
(Overture files it as a county; it is not Baltimore County). Small islands are kept (min area 0.000005 deg2, about 5 ha), and the
script checks that Kent Island, Tilghman and Smith Island fall inside the state outline.
"""
import os, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "md")
# Maryland (37.89°N–39.72°N, 75.05°W–79.49°W) plus a margin for border towns (DC, Delmar, Ocean City)
BBOX = "bbox.xmin BETWEEN -79.6 AND -74.9 AND bbox.ymin BETWEEN 37.8 AND 39.8"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_md_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_md_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_md_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_md_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-MD' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -79.7 AND bbox.xmax < -74.8 AND bbox.ymin > 37.7 AND bbox.ymax < 39.9""").fetchall()


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


# Overture's names -> the official ones: the City is "Baltimore" there, and St. Mary's is spelled out
COUNTY_NAME = {"Baltimore": "Baltimore City", "Saint Mary's County": "St. Mary's County"}
rows = [(sub, COUNTY_NAME.get(name, name) if sub == "county" else name, g) for sub, name, g in rows]
out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/md_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/md_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/md_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# the Chesapeake islands the QA of 2026-10-29 warned about: each must be inside the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/md_state_detail.geojson")))
for nm, lon, lat in [("Kent Island (Stevensville)", -76.3141, 38.9807), ("Tilghman Island", -76.3383, 38.7107),
                     ("Smith Island (Tylerton)", -76.0237, 37.9667), ("Solomons", -76.4566, 38.3218),
                     ("Hooper Island (Fishing Creek)", -76.2296, 38.3176), ("Deal Island", -75.9466, 38.1567)]:
    print(f"  {nm}: {'inside' if st.contains(Point(lon, lat)) else 'OUTSIDE'}")
print("counties:", sorted(c["name"] for c in out["counties"]))

# the neighbours' land (DC, Virginia, West Virginia, Pennsylvania, Delaware): listings.py widens Maryland's outline ~300 m for piers and
# marsh edges, but only over water, so a Chevy Chase, DC or Takoma Park, DC listing on the far side of the line stays out (the prompt)
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region IN ('US-DC', 'US-VA', 'US-WV', 'US-PA', 'US-DE') AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-79.7, 37.7, -74.8, 39.9)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/md_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
