"""Official records for Maryland -> one table of licensed and inspected food and drink businesses (playbook/12-sources.md).

Maryland's 24 local health departments (23 counties and Baltimore City) license and inspect restaurants; the Maryland Department of
Health's Office of Food Protection covers processors, not restaurants, and there is no statewide food license or inspection list.
Alcohol is licensed by each county's (and Baltimore City's) own board. What a script may read (data/raw/official, fetch_official.py):
- "mont":    Montgomery County "HHS - Food Inspection Data from July 2024 and onward" (dkrp-gr48, Public Domain, daily): every food
             service facility inspected since 2024-06, with each inspection's official result (Pass, Fail, Closed...). One row per
             registration; registrations that share an inspection number are one business (the county re-registered its facilities
             in 2024, so an old "zLegacy" registration and a new one carry the same visit). Owner fields are never requested.
- "abs":     Montgomery County Alcohol Beverage Services "Licensee Data" (c6rw-fazn, Public Domain, monthly): class and type at a
             street address. No business name is requested (the list names the licensee company), so a license joins the one
             Montgomery food facility at its street address and zip, or nothing.
- "baltliq": Baltimore City "Licenses" (CityView, CC BY 3.0): the liquor board's 2026 licenses by trade name, class and description
             (tavern, restaurant, package goods, adult...), no point. Licensee names are never requested.
- "aa":      Anne Arundel County Department of Health "DOH Restaurant Inspection Dataset" (ArcGIS, updated 2026-10-26): inspections
             2025-01 to 2026-09 by facility name, address and business code; no facility id or overall result, so it confirms that a
             place is inspected and nothing more.
- "pg":      Prince George's County "Food Inspection" (umjn-t2iz): stale (last updated 2024-01-12), so never active: calibration only.
Elsewhere a place with no matched record is unknown, never "no".

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
kind: food (a place to eat or drink) | retail (stores, package sales) | truck | other (schools, caterers, hotels, clubs, events) |
adult (Baltimore City's adult entertainment licenses: never shown, used to hide the venue).
insp (Montgomery only): the business's inspections, latest first, one per inspection number: [date, result, type, number].
"""
import os, re, json, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Maryland writes one road as 'Route 40', 'US 40', 'Rt 2', 'MD 2' or 'MD Route 2', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|MD|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|MARYLAND (?:ROUTE|RTE|HIGHWAY|HWY)|MD (?:ROUTE|RTE|RT|HIGHWAY|HWY)|MD|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Montgomery writes its addresses this way)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out






LIST_DATE = None   # set by load(): the day Montgomery's inspection data was last updated, from its own metadata
META = json.load(open(os.path.join(OFF, "meta.json")))
MONT_FILE, ABS_FILE = os.path.join(OFF, "mont", "inspections.json"), os.path.join(OFF, "mont", "abs.json")
BALT_FILE, AA_FILE, PG_FILE = os.path.join(OFF, "balt", "liquor.json"), os.path.join(OFF, "aa", "inspections.json"), os.path.join(OFF, "pg", "establishments.json")
MONT_PAGE = META["dkrp-gr48"]["url"]
# no statewide inspection search: the Maryland Department of Health's page of the 24 local health departments, each with its own
# food program (checked 2026-11-03: 200, "MDH Health Departments")
INSPECTIONS_URL = "https://health.maryland.gov/pages/departments.aspx"
# Montgomery's results, as the county words them; an inspection that was cancelled or left incomplete has no result
RESULTS = ("Pass", "Fail", "Closed", "Closed With Complaint")
ONPREM_T = ("Montgomery County on-premises alcohol license", "Baltimore City on-premises liquor license")


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "package" in t or "off-premises" in t else None


def _zip(z):
    z = re.sub(r"\D", "", str(int(z)) if isinstance(z, float) and z == z else str(z or ""))
    return z[:5] if len(z) >= 5 else ""


OTHER = re.compile(r"\b(?:SCHOOL|ELEMENTARY|ACADEMY|HOSPITAL|JAIL|DETENTION|SENIOR|NURSING|FOOD TRUCK|CATERING|CATERER|COMMISSARY|"
                   r"CONCESSION|CHURCH|PARISH|CAMP|CORRECTION(?:AL)?|CAMPUS|WAREHOUSE|COLLEGE|UNIVERSITY|DISTRIBUT\w*|WHOLESALE)\b", re.I)


def _row(jur, lic, name, addr, city, z, la, lo, kind, active=True, ltype=None, holder=None):
    num, st = street_key(addr)
    if kind == "food" and OTHER.search(name or ""):
        kind = "other"
    return {"jur": jur, "lic": lic, "name": name, "dba": name, "holder": holder, "keys": _names(name), "addr": addr, "city": city,
            "zip": _zip(z), "num": num, "street": st, "lat": la, "lon": lo, "kind": kind, "active": active, "ltype": ltype}


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def _f(x):
    try:
        v = float(x)
        return v if v == v and v != 0 else np.nan
    except (TypeError, ValueError):
        return np.nan


def _date(v):
    return (v or "")[:10] or None


def load_mont():
    """One row per Montgomery registration with its latest name, address, point and license subtype, and its inspections."""
    by = {}
    for r in json.load(open(MONT_FILE)):
        reg = r.get("registration_number")
        if not reg:
            continue
        by.setdefault(reg, []).append(r)
    rows = []
    for reg, rs in by.items():
        rs.sort(key=lambda r: r.get("inspection_start_date") or "", reverse=True)
        last = rs[0]
        sub = next((r["business_subtype"] for r in rs if r.get("business_subtype") and r["business_subtype"] != "zLegacy"), last.get("business_subtype") or "")
        g = next((r["location"] for r in rs if isinstance(r.get("location"), dict) and r["location"].get("coordinates")), None)
        lo, la = (_f(g["coordinates"][0]), _f(g["coordinates"][1])) if g else (np.nan, np.nan)
        kind = ("truck" if re.search(r"Mobile", sub) else
                "other" if re.search(r"Schools|Hosp|Care Homes|Non-Profit|Seasonal|Pool|Farmers Market|Farmer|Temporary", sub) else "food")
        x = _row("mont", f"mont-{reg}", re.sub(r"\s+", " ", last.get("business_name") or "").strip(), _addr(last.get("address")),
                 _city(last.get("city")), last.get("zip"), la, lo, kind, active=(_date(last.get("inspection_start_date")) or "") >= "2025-05-01",
                 ltype="Montgomery County food service license")
        x["insp"] = [[_date(r.get("inspection_start_date")), r.get("status"), r.get("inspection_type"), r.get("inspection_number")] for r in rs]
        x["issued"] = None
        rows.append(x)
    return rows


def load_abs():
    rows = []
    for r in json.load(open(ABS_FILE)):
        g = r.get("location") or {}
        la, lo = (_f(g.get("latitude")), _f(g.get("longitude"))) if isinstance(g, dict) else (np.nan, np.nan)
        cls = (r.get("licenseclass") or "").strip()
        onprem = cls in ("B", "D", "H")   # B hotel or restaurant, D tavern, H beer and wine: on-premises; A is off-sale, C a club
        x = _row("abs", f"abs-{r.get('licensee_number')}", None, _addr(r.get("street")), _city(r.get("city")), r.get("zip"), la, lo,
                 "food" if onprem else "retail" if cls == "A" else "other", active=True,
                 ltype=ONPREM_T[0] if onprem else "Montgomery County off-premises alcohol license" if cls == "A" else f"Montgomery County alcohol license (class {cls or '?'})")
        rows.append(x)
    return rows


BALT_KIND = {"Tavern": "food", "Tavern License": "food", "Restaurant": "food", "Restaurant License": "food", "Brewery": "food",
             "Distillery": "food", "Package goods only": "retail", "Package Goods Only": "retail", "Adult": "adult"}


def load_balt():
    """The 2026 licenses of Baltimore City's liquor board, one row per license number (the layer repeats it per licensee person)."""
    best = {}
    for r in json.load(open(BALT_FILE)):
        k = r.get("LicenseNumber")
        if not k or (r.get("LicenseYear") or 0) < 2026:
            continue
        if k not in best or (r.get("LicenseStatus") == "Renewed" and best[k].get("LicenseStatus") != "Renewed"):
            best[k] = r
    rows = []
    for k, r in best.items():
        desc = (r.get("EstablishmentDesc") or "").strip()
        kind = BALT_KIND.get(desc, "other")
        x = _row("baltliq", f"baltliq-{k}", re.sub(r"\s*,?\s*\b(?:LLC|INC|L\.L\.C)\b\.?\s*$", "", re.sub(r"\s+", " ", r.get("TradeName") or "").strip(), flags=re.I),
                 _addr(r.get("AddrStreet")), "Baltimore", r.get("AddrZip"), np.nan, np.nan, kind, active=r.get("LicenseStatus") != "Closed",
                 ltype=ONPREM_T[1] if kind == "food" else "Baltimore City package goods (off-premises) license" if kind == "retail" else f"Baltimore City liquor license ({desc.lower() or 'other'})")
        rows.append(x)
    return rows


AA_KIND = {"RESTAURANT": "food", "CARRY OUT": "food", "BAKERY": "food", "CAFE/COFFEE SHOP": "food", "TAVERN": "food", "FOOD STAND": "food",
           "MOBILE UNIT": "truck", "CONVENIENCE STORE": "retail", "GROCERY": "retail"}


def load_aa():
    """One row per Anne Arundel facility (name, address and zip), active if inspected in the dataset's span (2025-01 to 2026-09)."""
    by = {}
    for r in json.load(open(AA_FILE)):
        k = (re.sub(r"\s+", " ", r.get("facility_name") or "").strip().upper(), re.sub(r"\s+", " ", r.get("facility_address") or "").strip().upper(), str(r.get("zip_code") or ""))
        by.setdefault(k, []).append(r)
    rows = []
    for (nm, ad, z), rs in by.items():
        rs.sort(key=lambda r: r.get("date") or "", reverse=True)
        code = rs[0].get("business_code") or ""
        x = _row("aa", f"aa-{rs[0]['FID']}", re.sub(r"\s+", " ", rs[0].get("facility_name") or "").strip(), _addr(rs[0].get("facility_address")),
                 None, z, np.nan, np.nan, AA_KIND.get(code, "other"), active=True, ltype=f"Anne Arundel County inspected facility ({code.lower() or 'other'})")
        x["last_inspected"] = rs[0].get("date")
        rows.append(x)
    return rows


PG_FOOD = re.compile(r"Fast Food|Carry-out|Restaurant|Full Service|Bakery|Coffee|Ice Cream|Deli|Bar|Tavern|Snack", re.I)


def load_pg():
    """Prince George's establishments inspected since 2022 (the list stops in January 2024): never active, calibration only."""
    rows = []
    for r in json.load(open(PG_FILE)):
        if (_date(r.get("last_inspection")) or "") < "2022-01-01":
            continue
        g = r.get("geocoded_column_1") or {}
        lo, la = (_f(g["coordinates"][0]), _f(g["coordinates"][1])) if isinstance(g, dict) and g.get("coordinates") else (np.nan, np.nan)
        x = _row("pg", f"pg-{r.get('establishment_id')}", re.sub(r"\s+", " ", r.get("name") or "").strip(), _addr(r.get("address_line_1")),
                 _city(r.get("city")), r.get("zip"), la, lo, "food" if PG_FOOD.search(r.get("category") or "") else "other", active=False,
                 ltype="Prince George's County inspected establishment (2024 list)")
        x["last_inspected"] = _date(r.get("last_inspection"))
        rows.append(x)
    return rows


def load():
    global LIST_DATE
    LIST_DATE = META["dkrp-gr48"]["rows_updated"]
    df = pd.DataFrame(load_mont() + load_abs() + load_balt() + load_aa() + load_pg())
    for c_ in ("insp", "issued", "last_inspected"):
        if c_ not in df.columns:
            df[c_] = None
    df["biz"] = np.arange(len(df))

    def join(a, b):
        old, new = df.at[b, "biz"], df.at[a, "biz"]
        if old != new:
            df.loc[df.biz == old, "biz"] = new
    # Montgomery: registrations that share an inspection number are one business (the 2024 re-registration)
    first = {}
    for i in df.index[df.jur == "mont"]:
        for v in df.at[i, "insp"] or []:
            if v[3] in first:
                join(first[v[3]], i)
            else:
                first[v[3]] = i
    # one business can hold several records (a food license and an alcohol license at one address under one name)
    town = df.city.fillna("").str.upper().str.strip()
    for num, g in df[df.num.notna() & df.street.notna() & df.jur.ne("pg")].groupby("num"):
        idx = list(g.index)
        if len(idx) < 2 or len(idx) > 400:
            continue
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                a, b = idx[x], idx[y]
                if not street_compat(df.at[a, "street"], df.at[b, "street"]):
                    continue
                if not ((df.at[a, "zip"] and df.at[a, "zip"] == df.at[b, "zip"]) or (town[a] and town[a] == town[b])):
                    continue
                ka, kb = df.at[a, "keys"], df.at[b, "keys"]
                if not ka or not kb:
                    continue
                if any(name_sim(p, q) >= 85 or ((_stems(p) - GENERIC) & (_stems(q) - GENERIC)) for p in ka for q in kb):
                    join(a, b)
    # a Montgomery alcohol license (no name) joins the one Montgomery food facility at its street address and zip
    mont = df[(df.jur == "mont") & df.kind.eq("food") & df.active & df.num.notna()]
    at = mont.groupby(["num", "zip"]).groups
    joined = 0
    for i in df.index[df.jur == "abs"]:
        cand = [j for j in at.get((df.at[i, "num"], df.at[i, "zip"]), []) if street_compat(df.at[i, "street"], df.at[j, "street"])]
        if len({df.at[j, "biz"] for j in cand}) == 1:
            join(cand[0], i); joined += 1
    print("Montgomery alcohol licenses joined to a facility at their address:", joined, "of", int((df.jur == "abs").sum()))
    df["county"] = None   # set from the point (geocode_official.py, calibrate.py)
    return df
