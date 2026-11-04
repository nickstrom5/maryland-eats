# Maryland sources (checked 2026-11-03)

Every host below was robots-checked with `pipeline/check_sources.py` (ClaudeBot, Claude-User and anthropic-ai; RFC 9309 matcher) in
its own step, before any other request. User agent on every scripted request: `MarylandEatsBuild/1.0 (+nick@eatsranked.com)`.
Raw files are in `data/raw/official/` (git-ignored, never public), written by `pipeline/fetch_official.py`; `meta.json` keeps each
source's own update date.

Maryland has no statewide restaurant inspector or list: its 24 local health departments (23 counties and Baltimore City) license and
inspect, and each county's (and Baltimore City's) liquor board licenses alcohol. The app says "county" and treats **Baltimore City as
its own county-level jurisdiction**, apart from Baltimore County (assigned by polygon, so a "Baltimore" mailing address in the County
stays in the County).

## Inspections: Montgomery's results shown, the rest linked

- **Montgomery County** "HHS - Food Inspection Data from July 2024 and onward" (`data.montgomerycountymd.gov dkrp-gr48`, Public Domain,
  updated daily, rows 2024-06-03 to 2026-10-30). 3,465,660 raw rows repeat identical inspections up to hundreds of times, so the request
  groups on every column it asks for (22,352 distinct rows: 12,800 registrations, 13,904 inspection numbers). Owner fields are never
  requested. The county's 2024 re-registration put many visits under an old ("zLegacy") and a new registration with different type
  labels: **each inspection number counts once** (the newer registration's label), and registrations sharing a number are one business.
  7 numbers carry two dates (`data/md/qa_debug.json` "mont_number_two_dates") for a hand check. **Shown:** each Montgomery place's latest
  result in the county's own words (Pass, Fail, Closed, Closed With Complaint) and its date, plus up to eight earlier visits in the
  detail screen: 2,079 app places (Pass 2,017, Fail 34, Closed 29). Cancelled and Incomplete visits have no result. No grade is
  computed; the core list carries no result column, so nothing can be sorted or filtered by inspection. Mobile food licenses carry the
  owner's base address, sometimes in another county (Frederick, Beltsville, Bowie, Oakland): a truck based outside the county that
  licensed it matches nothing (97 Montgomery, 31 Anne Arundel, 2026-11-04).
- **Anne Arundel County** "DOH Restaurant Inspection Dataset" (ArcGIS, `services2.arcgis.com/nUoGCkM6W8Wqdvvh`, hub item
  `e540546f30854288a5279898946f5ba2`, updated 2026-10-26): 8,655 inspections 2025-01-02 to 2026-09-30, 2,668 facilities, with business
  code, risk and critical items but **no facility id or overall result**: used to confirm a place is inspected (official), never shown
  as a result. The item id the prompt gave (`8a007b7d…`) no longer exists.
- **Prince George's County** "Food Inspection" (`data.princegeorgescountymd.gov umjn-t2iz`, last updated 2024-01-12): stale, so
  **calibration only**, never active or shown. princegeorgescountymd.gov answers a bot check (never worked around).
- **Baltimore City**: no inspection results published; health.baltimorecity.gov answers a bot check. Its "Recent Food Establishment
  Closures" page (baltimorecity.gov, usable) lists temporary health closures and reopenings: not used (a closure there is not a
  permanent closing).
- **Baltimore County**: the 2026 food facility PDF on baltimorecountymd.gov sits behind a bot check: not used.
- Every other place links the Maryland Department of Health's list of local health departments
  (`health.maryland.gov/pages/departments.aspx`, 200, "MDH Health Departments").

## Official records

| Source | What | Terms | Updated | Status |
|---|---|---|---|---|
| Montgomery inspections (above) | 12,800 registrations; kind food unless mobile, school/hospital/care home, non-profit, seasonal or pool snack bar, farmers market or temporary | Public Domain | daily (2026-11-03) | **used**: active = inspected since 2025-05-01; 1,823 listings matched, 368 added |
| **Montgomery ABS "Licensee Data"** (`c6rw-fazn`) | 1,085 alcohol licenses with class, type and a point; licensee and account names not requested | Public Domain | monthly (2026-11-01) | **used**: class B, D or H = on-premises. No name, so a license joins the one Montgomery food facility at its street address and zip (708 joined): 509 app places "serve alcohol" |
| **Baltimore City "Licenses"** (CityView FeatureServer, liquor board) | 2026 licenses by trade name, class and description (tavern, restaurant, package goods, **adult**…), no point; licensee names not requested | CC BY 3.0 | 2026 | **used**: tavern/restaurant/brewery/distillery = on-premises (252 app places); package goods = store; the 31 "Adult" licenses mark adult venues by address (hidden, never shown) |
| Anne Arundel inspections (above) | facilities by name, address, zip and business code | (county open data) | 2026-10-26 | **used**: confirms 1,120 listings; 149 added; 326 rows unplaced (no town in the address) |
| Prince George's inspections (above) | establishments inspected 2022 to Jan 2024 | — | 2024-01-12 | calibration only |
| Real property (opendata.maryland.gov `ed4q-f8tm`) | statewide assessments | Public Domain | monthly | not used (no building-value board in this build) |

## Statewide base and outlines

| Source | What | Terms | Rows |
|---|---|---|---|
| Overture Maps places `2026-10-21.0` | Map listings | CDLA-Permissive-2.0 / Apache-2.0 + Foursquare NOTICE | 24,718 Maryland eating/drinking listings (1,369 marked closed) |
| Overture divisions `2026-10-21.0` | State and 24 county land outlines (Baltimore City included; Overture's "Baltimore" and "Saint Mary's County" renamed Baltimore City and St. Mary's County), islands kept: **Kent Island, Tilghman, Smith Island (Tylerton), Hooper Island, Deal Island, Solomons all checked inside** (`fetch_overture.py`). The neighbours' land (DC, VA, WV, PA, DE) is cut from the ~300 m water buffer, so a Chevy Chase, DC, Takoma Park, DC or Delmar, DE listing stays out; pins just over the water take the nearest county within ~1 km | ODbL (© OpenStreetMap contributors, Overture) | 24 counties |
| Overture addresses `2026-10-21.0` | 2,608,910 Maryland address points | open address sources | placed 2,494 official rows |
| US Census batch geocoder | Address to point | Public domain | 295 more |
| UCSD Google Local 2021 (`meta-Maryland.json.gz`, mcauleylab.ucsd.edu, 17.9 MB) | 2021 ratings/reviews/price: **private web leaderboard only, never the app or site** | research dataset | 15,383 food listings (1,797 closed by 2021); 12,017 matched |
| BLS QCEW 2025 (from the prompt) | 12,053 NAICS 722 establishments | public | benchmark: the app keeps 12,501 restaurants |

## Calibration (2026-11-03, `data/md/calibration*.json`)

| Kind of listing (app grouping) | Montgomery (inspected since 2025-05) | Anne Arundel (inspected 2025-26) | Prince George's (2022-Jan 2024, stale) |
|---|---|---|---|
| Meta >= 0.95 | 84.8% of 1,484 | 73.0% of 1,084 | 57.9% of 1,287 |
| Meta 0.90-0.95 with a website | 47.0% of 200 | 46.9% of 160 | 35.8% of 173 |
| Meta 0.90-0.95, no website | 45.5% of 33 | 21.7% of 46 | 12.1% of 33 |
| Meta < 0.90 | 19.9% of 306 | 14.1% of 256 | 5.8% of 276 |
| Chain store lists (AllThePlaces, DAC) | 63.8% of 47 | 46.0% of 63 | 17.4% of 69 |
| BrightQuery >= 0.95 | 33.2% of 373 | 31.2% of 154 | 25.9% of 282 |
| Other sources | 19.3% of 1,075 | 20.3% of 523 | 19.7% of 712 |

Same order as every other state, so the same keep rules: app = Meta >= 0.95, Meta 0.90-0.95 with a website, chain store lists,
official, hand-checked; web = Meta and chain store lists minus Google-2021-closed, plus official and hand-checked. Coverage the other
way: open map listings hold 51.0% of Montgomery's 3,238 inspected food businesses and 72.2% of Anne Arundel's 1,393.

## Honors and guides

- **MICHELIN:** none. No Maryland region on guide.michelin.com; its District of Columbia selection stops at the District line.
- **James Beard** (`data/research/jbf.json`): Charleston (Baltimore), Outstanding Wine and Other Beverages Program **winner 2025**
  (jamesbeard.org, 2025-06-16); 2026 semifinalists (jamesbeard.org, 2026-01-21): Darmyelesh Alemu, Beteseb (Silver Spring) and Matthew
  Oetting, Marta (Baltimore), Best Chef: Mid-Atlantic; Café Dear Leon (Baltimore), Outstanding Bakery. Pink Flamingo (Best New Bar
  semifinalist) has no map listing. Spike Gjerde's 2015 award: Woodberry Kitchen now runs as the Tavern at Woodberry Kitchen with no
  dated page; left in LEADS. Maison Marconi (America's Classic 2002) closed.
- **Hand-checked guides** (`pipeline/build_research.py`, every page read through Claude's fetcher on 2026-11-03, robots-checked):
  crab cakes and crab houses 11 (Tasting Table 2025-04-11; Visit Baltimore), pit beef 3 (Chaps' three stands, Tasting Table
  2025-09-14), oyster bars 8 (Baltimore Magazine's Best of Baltimore, August 2025 and August 2026; Talbot County's oyster trail; Visit
  Annapolis), pupuserías 4 (Washingtonian 2026-01-20 and 2026-08-27; Visit Montgomery, modified 2026-05-03), Ethiopian 4 (Washingtonian
  2026-08-31), Route 40 Korean 4 (Best of Baltimore 2026; Visit Howard County listings), snowballs 16 (Baltimore Magazine 2026-05-21),
  oldest 2 (Middleton Tavern 1750, Tasting Table 2025-02-17 and 2025-09-23; Faidley's 1886, Tasting Table 2025-04-11). Pit beef and
  oldest have too few places for a site page; the app shows a guide from three places (pit beef yes, oldest not yet).
- Leads and blocked hosts: `data/research/app/LEADS.md`.
- Blocked or unusable: baltimoresun.com, capitalgazette.com, dc.eater.com, wypr.org, wbaltv.com, whatsupmag.com, marylandmatters.org,
  foodandwine.com, seriouseats.com, bonappetit.com (robots); visitmaryland.org, atlasobscura.com, geodata.md.gov, baltimorecountymd.gov,
  princegeorgescountymd.gov, health.baltimorecity.gov (bot checks); visitworcester.org, somersetcountytourism.com, dorchestertourism.com
  (unreachable); montgomerycountymd.gov (robots: the app links the county's open-data page instead).
