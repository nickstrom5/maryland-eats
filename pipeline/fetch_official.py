"""Maryland's open official records -> data/raw/official/ (git-ignored, never public). Run after check_sources.py has cleared each host.

One request per page, one at a time, with an honest user agent. No owner, licensee or person name is ever requested.
- mont/inspections.json  Montgomery County "HHS - Food Inspection Data from July 2024 and onward" (data.montgomerycountymd.gov dkrp-gr48,
                         Public Domain, daily). The raw table repeats identical rows up to hundreds of times (3.4M rows), so the request
                         groups on every column it asks for: one row per distinct registration + inspection + type + status.
- mont/abs.json          Montgomery County Alcohol Beverage Services "Licensee Data" (c6rw-fazn, Public Domain, monthly): license class and
                         type at a street address with a point. The licensee and account names (companies or people) are not requested.
- pg/establishments.json Prince George's "Food Inspection" (data.princegeorgescountymd.gov umjn-t2iz, last updated 2024-01-12): stale, so
                         calibration only. Grouped to one row per establishment with its last inspection date.
- balt/liquor.json       Baltimore City "Licenses" (baltegis.baltimorecity.gov CityView/Licenses, CC BY 3.0): liquor licenses from 2025 on,
                         trade name, class, status and address only (the licensee's first and last names and the corporation are not
                         requested).
- aa/inspections.json    Anne Arundel County Department of Health "DOH Restaurant Inspection Dataset" (ArcGIS, opendata.aacounty.org):
                         dated inspections with facility name, address, ZIP, type, risk and critical items; no facility id or overall result.
- meta.json              each source's own last-update date, license and URL.
"""
import os, json, time, datetime
import requests

ROOT = os.path.join(os.path.dirname(__file__), "..")
OFF = os.path.join(ROOT, "data", "raw", "official")
UA = {"User-Agent": "MarylandEatsBuild/1.0 (+nick@eatsranked.com)"}
S = requests.Session(); S.headers.update(UA)


def get(url, **params):
    for attempt in range(3):
        r = S.get(url, params=params, timeout=120)
        if r.status_code == 200:
            return r.json()
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()


def save(rel, rows):
    p = os.path.join(OFF, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(rows, open(p, "w"))
    print(f"{rel}: {len(rows):,} rows", flush=True)


def socrata_meta(host, ds):
    m = get(f"https://{host}/api/views/{ds}.json")
    return {"host": host, "name": m.get("name"), "license": (m.get("license") or {}).get("name"),
            "rows_updated": datetime.datetime.fromtimestamp(m.get("rowsUpdatedAt", 0), datetime.UTC).date().isoformat(),
            "attribution": m.get("attribution"), "url": f"https://{host}/d/{ds}"}


def socrata(host, ds, select, group=None, where=None, page=50000):
    out, off = [], 0
    while True:
        q = {"$select": select, "$limit": page, "$offset": off, "$order": group.split(",")[0] if group else ":id"}
        if group: q["$group"] = group
        if where: q["$where"] = where
        rows = get(f"https://{host}/resource/{ds}.json", **q)
        out += rows; off += page
        if len(rows) < page:
            return out


def arcgis(layer, fields, where="1=1"):
    out, off = [], 0
    while True:
        d = get(f"{layer}/query", where=where, outFields=fields, returnGeometry="false", resultOffset=off, resultRecordCount=2000,
                orderByFields=fields.split(",")[0], f="json")
        feats = [f["attributes"] for f in d.get("features", [])]
        out += feats; off += len(feats)
        if not feats or not d.get("exceededTransferLimit"):
            return out


def arcgis_meta(layer, name, url, license_):
    m = get(layer, f="json")
    t = (m.get("editingInfo") or {}).get("dataLastEditDate")
    return {"host": layer.split("/")[2], "name": name, "license": license_, "url": url,
            "rows_updated": datetime.datetime.fromtimestamp(t / 1000, datetime.UTC).date().isoformat() if t else None}


meta = {}
MONT = "data.montgomerycountymd.gov"
cols = "registration_number,inspection_number,business_name,address,city,zip,business_type,business_subtype,inspection_type,inspection_start_date,status,location"
meta["dkrp-gr48"] = socrata_meta(MONT, "dkrp-gr48")
save("mont/inspections.json", socrata(MONT, "dkrp-gr48", cols, group=cols))
cols = "street,city,zip,licensee_number,licenseclass,licensetype,cafe,location"
meta["c6rw-fazn"] = socrata_meta(MONT, "c6rw-fazn")
save("mont/abs.json", socrata(MONT, "c6rw-fazn", cols))

PG = "data.princegeorgescountymd.gov"
meta["umjn-t2iz"] = socrata_meta(PG, "umjn-t2iz")
g = "establishment_id,name,category,address_line_1,address_line_2,city,zip,geocoded_column_1"
save("pg/establishments.json", socrata(PG, "umjn-t2iz", g + ",max(inspection_date) AS last_inspection,count(*) AS n", group=g))

BALT = "https://baltegis.baltimorecity.gov/mapping/rest/services/CityView/Licenses/FeatureServer/0"
meta["balt-liquor"] = arcgis_meta(BALT, "Baltimore City Licenses (liquor)", BALT, "CC BY 3.0")
save("balt/liquor.json", arcgis(BALT, "LicenseNumber,LicenseClass,SubClass,LicenseYear,LicenseStatus,LicenseDate,LicenseEndDate,TradeName,"
                                      "EstablishmentDesc,AddrStreet,AddrZip", where="LicenseYear >= 2025"))

AA = "https://services2.arcgis.com/nUoGCkM6W8Wqdvvh/arcgis/rest/services/DOH_Restaurant_Inspection_Dataset_/FeatureServer/0"
meta["aa-inspections"] = arcgis_meta(AA, "Anne Arundel County DOH Restaurant Inspection Dataset",
                                     "https://opendata.aacounty.org/datasets/e540546f30854288a5279898946f5ba2", None)
save("aa/inspections.json", arcgis(AA, "FID,date,facility_name,facility_address,zip_code,inspection_type,risk,closure_re_open,business_code,"
                                       "critical_item_1,critical_item_2,critical_item_3,critical_item_4,critical_item_5,critical_item_6a,"
                                       "critical_item_6b,critical_item_7a,critical_item_7b,critical_item_8,critical_item_9"))
json.dump(meta, open(os.path.join(OFF, "meta.json"), "w"), indent=1)
print(json.dumps(meta, indent=1))
