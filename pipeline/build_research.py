"""Writes data/research/app/*.json (hand-checked Maryland guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from la-eats/pipeline/build_research.py.

Each entry cites the 2025-26 page that names it (robots-checked host: check_sources.py), read through Claude's web fetcher on
2026-11-03. Every page below is dated on its face, or is an official tourism listing (Visit Howard County, Visit Montgomery, Visit
Annapolis, Talbot County's oyster trail, Visit Baltimore). The address comes from the map listing we already hold for that name in that
town (site/maryland.json), never from memory; a name that isn't found exactly once in its town (or at the street number given) is left
out and listed in data/research/app/LEADS.md. A place the map data lacks is added only when the dated page prints its street address (ADDR).
Usage: ../.venv/bin/python build_research.py   (then maryland.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "maryland.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("\u2019", ""))).strip()

# each dated on its face, or an official tourism listing (read 2026-11-03)
TT_CRAB = "https://www.tastingtable.com/1459035/best-spots-crab-cakes-baltimore/"                              # updated 2025-04-11
VB_CRAB = "https://baltimore.org/what-to-do/where-to-eat/top-eateries-to-enjoy-authentic-baltimore-crab-cakes/"   # Visit Baltimore, (c) 2026
BM_BEST26 = "https://www.baltimoremagazine.com/section/fooddrink/best-of-baltimore-2026-food-drink/"            # August 2026 issue
BM_BEST25 = "https://www.baltimoremagazine.com/section/bestof/best-of-baltimore-2025-food-drink/"               # August 2025 issue
BM_SNOW = "https://www.baltimoremagazine.com/section/fooddrink/the-ultimate-baltimore-snowball-guide/"          # 2026-05-21
TT_CHAPS = "https://www.tastingtable.com/1963169/best-sandwich-shop-baltimore-maryland-local-chaps-pit-beef/"  # 2025-09-14
WASH_ETH = "https://washingtonian.com/guide/food/where-to-eat-ethiopian-food-around-the-dc-area-right-now/"     # 2026-08-31
WASH_CHEAP = "https://washingtonian.com/2026/08/27/best-cheap-eats-around-the-dc-area/"                         # 2026-08-27
WASH_VIEJO = "https://washingtonian.com/100-very-best-restaurants-2026/el-viejo-central-american-kitchen/"      # 2026-01-20
VM_COMALITO = "https://visitmontgomery.com/moco-eats-directory/pupuseria-el-comalito/"                          # modified 2026-05-03
VHC_CHOSUN = "https://www.visithowardcounty.com/listings/chosun-hwaro/8768/"
VHC_HANGARI = "https://www.visithowardcounty.com/listings/hang-ari/8774/"
VHC_DJG = "https://www.visithowardcounty.com/listings/dae-jang-geum/10356/"
VHC_TIAN = "https://www.visithowardcounty.com/listings/tian-chinese-&-korean-restaurant/10391/"
TALBOT_OYSTER = "https://tourtalbot.org/crack-open-the-talbot-county-oyster-trail/"                             # Talbot County tourism, 2025-26
VA_SAILOR = "https://www.visitannapolis.org/listing/sailor-oyster-bar/3674/"
TT_OLDEST = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"                    # 2025-09-23
TT_OLDBAR = "https://www.tastingtable.com/1786324/oldest-bar-every-state/"                                      # 2025-02-17
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                               # 2026-01-21
JBF25W = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-winners"                                # 2025-06-16

# (name as the source writes it or as our listing spells it, town as our listing has it, street number to pick the location (or
# None), note, founded, founded_note, [sources])
GUIDES = {
 "crab cakes": [   # Tasting Table's 15 crab-cake spots (April 2025), most also on Visit Baltimore's crab-cake page
  ("Faidley's", "Baltimore", "203", "Crab cakes at Lexington Market since 1886: jumbo lump and backfin.", None, None, [TT_CRAB, VB_CRAB]),
  ("Koco's Pub", "Baltimore", "4301", "Lauraville's pub with baseball-size crab cakes.", None, None, [TT_CRAB, VB_CRAB]),
  ("Pappas Restaurant and Sports Bar", "Parkville", None, "The Parkville original of Pappas' broiled crab cakes.", None, None, [TT_CRAB, VB_CRAB]),
  ("G & M Restaurant", "Linthicum Heights", "804", "Big crab cakes near BWI; a pizza place turned crab-cake house.", None, None, [TT_CRAB]),
  ("Costas Inn", "Dundalk", "4100", "Crab cakes and steamed crabs on North Point Boulevard.", None, None, [TT_CRAB]),
  ("Jimmy's Famous Seafood", "Baltimore", "6526", "Holabird Avenue's crab cakes, open since 1974.", None, None, [TT_CRAB, VB_CRAB]),
  ("Nick's Fish House", "Baltimore", "2600", "Crab cakes on the Middle Branch.", None, None, [TT_CRAB]),
  ("L.P. Steamers", "Baltimore", "1100", "A Locust Point crab house: steamed crabs and crab cakes.", None, None, [TT_CRAB]),
  ("Gertrude's", "Baltimore", "10", "John Shields' Chesapeake kitchen at the Baltimore Museum of Art.", None, None, [TT_CRAB, VB_CRAB]),
  ("Kooper's Tavern", "Baltimore", "1702", "Fells Point crab cakes on Thames Street.", None, None, [TT_CRAB, VB_CRAB]),
  ("Avenue Kitchen & Bar", "Baltimore", "911", "Crab cakes in Hampden.", None, None, [TT_CRAB, VB_CRAB]),
 ],
 "pit beef": [   # Tasting Table, September 2025: Chaps' three Maryland stands
  ("Chaps Pit Beef", "Baltimore", "720", "The Pulaski Highway original: charcoal-grilled bottom round, sliced thin, tiger sauce.", None, None, [TT_CHAPS]),
  ("Chaps Pit Beef", "Aberdeen", "1013", "Chaps' larger Aberdeen stand.", None, None, [TT_CHAPS]),
  ("Chaps Pit Beef", "Glen Burnie", "6714", "Chaps on Ritchie Highway.", None, None, [TT_CHAPS]),
 ],
 "oyster bar": [
  ("Thames Street Oyster House", "Baltimore", "1728", "Raw oysters and a raw bar in Fells Point (Best of Baltimore 2025 and 2026).", None, None, [BM_BEST26, BM_BEST25, TT_CRAB]),
  ("True Chesapeake", "Baltimore", "3300", "Roasted oysters from its own Chesapeake farm, at Clipper Mill (Best of Baltimore 2026).", None, None, [BM_BEST26]),
  ("Loch Bar", "Baltimore", "240", "Oysters Rockefeller in Harbor East (Best of Baltimore 2026).", None, None, [BM_BEST26]),
  ("Sailor Oyster Bar", "Annapolis", "196", "An Annapolis raw bar on West Street: local oysters and crudo.", None, None, [VA_SAILOR]),
  ("Tickler's Crab Shack & Restaurant", "Tilghman", None, "Tilghman Island's raw bar and an oyster po'boy.", None, None, [TALBOT_OYSTER]),
  ("Ruse", "St. Michaels", "209", "A St. Michaels oyster bar with its own oyster menu.", None, None, [TALBOT_OYSTER]),
  ("Harrison's Harbour Lights", "St. Michaels", "101", "An all-you-care-to-eat oyster buffet, eight ways.", None, None, [TALBOT_OYSTER]),
  ("Bas Rouge", "Easton", "19", "Oysters on the half shell and the chef's oyster stew.", None, None, [TALBOT_OYSTER]),
 ],
 "pupuseria": [
  ("El Viejo Central American Kitchen", "Silver Spring", None, "Pupusas, tamales and Salvadoran breakfasts (Washingtonian's 100 Very Best, 2026).", None, None, [WASH_VIEJO, WASH_CHEAP]),
  ("Pupuseria El Comalito", "Takoma Park", "1167", "A Salvadoran pupuseria founded in 2005.", None, None, [VM_COMALITO]),
  ("Pupuseria El Comalito", "Gaithersburg", "18749", "El Comalito's Gaithersburg pupuseria.", None, None, [VM_COMALITO]),
  ("Pupuseria El Comalito", "Riverdale", "6100", "El Comalito's Riverdale Park pupuseria.", None, None, [VM_COMALITO]),
 ],
 "ethiopian": [   # Washingtonian's DC-area Ethiopian guide, August 2026 (its Maryland rooms)
  ("Beteseb Restaurant", "Silver Spring", "8201", "Beef tibs sizzling in cast iron; chef Darmyelesh Alemu, a 2026 James Beard semifinalist.", None, None, [WASH_ETH, JBF26]),
  ("CherCher Ethiopian Cuisine", "Bethesda", "4921", "Ethiopian on Bethesda Avenue.", None, None, [WASH_ETH]),
  ("Effoi Restaurant", "Silver Spring", "8233", "A Tigrayan gathering place: hlbet and bula genfo.", None, None, [WASH_ETH]),
  ("Shagga Coffee & Restaurant", "Hyattsville", "6040", "Ethiopian food and coffee on Baltimore Avenue.", None, None, [WASH_ETH]),
 ],
 "route 40 korean": [   # Koreatown Maryland on Route 40 (Baltimore National Pike), Ellicott City
  ("ChoSun Hwaro", "Ellicott City", "9445", "Table-grill Korean barbecue (Best of Baltimore 2026's Korean BBQ).", None, None, [BM_BEST26, VHC_CHOSUN]),
  ("Hang Ari", "Ellicott City", "9380", "Korean home cooking on Baltimore National Pike.", None, None, [VHC_HANGARI]),
  ("Dae Jang Geum", "Ellicott City", "10194", "Korean barbecue at the Bethany 40 center.", None, None, [VHC_DJG]),
  ("Tian Chinese and Korean Restaurant", "Ellicott City", "8801", "Chinese-style Korean cooking at Golden Triangle.", None, None, [VHC_TIAN]),
 ],
 "snowballs": [   # Baltimore Magazine's snowball guide, May 2026 (seasonal stands; their own addresses)
  ("The Bus Stop", "Upperco", "15513", "A snowball stand on Hanover Pike.", None, None, [BM_SNOW]),
  ("Chill Snowballs & Ice Cream", "Reisterstown", "249", "Main Street snowballs; the brothers have run stands since the 1980s.", None, None, [BM_SNOW]),
  ("Emmorton Snowballs & Ice Cream", "Bel Air", "101", "A Bel Air institution since 1981.", None, None, [BM_SNOW]),
  ("Friendly Snowballs", "Parkville", "2025", "On Joppa Road since 1984.", None, None, [BM_SNOW]),
  ("Go Melvo Sno-balls", "Severna Park", "104", "A 30-year-old stand on Maple Avenue.", None, None, [BM_SNOW]),
  ("Ice Queens Snowball Shop", "Baltimore", "1648", "Fluffy, finely shaved snowballs in Locust Point.", None, None, [BM_SNOW]),
  ("Icy Delights", "Baltimore", "3930", "Brewers Hill's Icy Delights, around since the 1990s.", None, None, [BM_SNOW]),
  ("One Sweet Moment", "Baltimore", "2914", "Hamilton snowballs for more than 30 years.", None, None, [BM_SNOW]),
  ("Opies Soft Serve and Snowballs", "Catonsville", "1603", "Snowballs and soft serve on Edmondson Avenue.", None, None, [BM_SNOW]),
  ("The Original Hawaiian Island Snowball", "Randallstown", "10636", "Liberty Road snowballs for decades.", None, None, [BM_SNOW]),
  ("The Peggy", "Baltimore", "3501", "The old Walther Gardens stand in Hamilton-Lauraville, renamed.", None, None, [BM_SNOW]),
  ("Quality Snowballs", "Baltimore", "1014", "Hampden snowballs from a 10-foot shipping container.", None, None, [BM_SNOW]),
  ("Snoasis", "Lutherville-Timonium", None, "On Padonia Road since 1977.", None, None, [BM_SNOW]),
  ("Stouten's Marina and Snowball Stop", "Dundalk", "817", "Snowballs at a Wise Avenue marina.", None, None, [BM_SNOW]),
  ("Summer Shack Snowballs", "Lutherville-Timonium", "2339", "A West Joppa Road snowball stand.", None, None, [BM_SNOW]),
  ("The Snowball Stand", "Woodstock", "1970", "Woodstock Road snowballs since the summer of 1974.", None, None, [BM_SNOW]),
 ],
 "oldest": [
  ("Middleton Tavern", "Annapolis", "2", "On the City Dock; Washington and Jefferson drank here.", 1750, "Tasting Table (February and September 2025) names it Maryland's oldest restaurant, open since 1750.", [TT_OLDEST, TT_OLDBAR]),
  ("Faidley's", "Baltimore", "203", "Lexington Market's crab-cake counter.", 1886, "Founded in 1886 by John W. Faidley, Sr. (Tasting Table, April 2025); still in Lexington Market.", [TT_CRAB, VB_CRAB]),
 ],
}
# the dated pages print these street addresses; placed by maryland.py when the map data lacks the place
ADDR = {("Pappas Restaurant and Sports Bar", "Parkville"): "1725 Taylor Ave", ("L.P. Steamers", "Baltimore"): "1100 E Fort Ave",
        ("El Viejo Central American Kitchen", "Silver Spring"): "9224 Warren St", ("Go Melvo Sno-balls", "Severna Park"): "104 Maple Ave",
        ("The Peggy", "Baltimore"): "3501 Southern Ave", ("Quality Snowballs", "Baltimore"): "1014 W 36th St",
        ("Stouten's Marina and Snowball Stop", "Dundalk"): "817 Wise Ave", ("Summer Shack Snowballs", "Lutherville-Timonium"): "2339 W Joppa Rd",
        ("The Snowball Stand", "Woodstock"): "1970 Woodstock Rd"}
CUISINE = {("Beteseb Restaurant", "Silver Spring"): "African", ("Effoi Restaurant", "Silver Spring"): "African",
           ("Shagga Coffee & Restaurant", "Hyattsville"): "African", ("El Viejo Central American Kitchen", "Silver Spring"): "Latin & Caribbean",
           ("ChoSun Hwaro", "Ellicott City"): "Korean", ("Hang Ari", "Ellicott City"): "Korean", ("Dae Jang Geum", "Ellicott City"): "Korean",
           ("Gertrude's", "Baltimore"): "Seafood", ("True Chesapeake", "Baltimore"): "Seafood", ("Loch Bar", "Baltimore"): "Seafood",
           ("Ruse", "St. Michaels"): "Seafood", ("Harrison's Harbour Lights", "St. Michaels"): "Seafood", ("Koco's Pub", "Baltimore"): "Seafood",
           ("Kooper's Tavern", "Baltimore"): "Seafood", ("L.P. Steamers", "Baltimore"): "Seafood", ("Costas Inn", "Dundalk"): "Seafood",
           ("G & M Restaurant", "Linthicum Heights"): "Seafood", ("Pappas Restaurant and Sports Bar", "Parkville"): "Seafood",
           ("The Bus Stop", "Upperco"): "Bakery & Sweets", ("The Peggy", "Baltimore"): "Bakery & Sweets", ("One Sweet Moment", "Baltimore"): "Bakery & Sweets",
           ("Stouten's Marina and Snowball Stop", "Dundalk"): "Bakery & Sweets", ("Snoasis", "Lutherville-Timonium"): "Bakery & Sweets"}
KINDS = {"crab cakes": ["crab cakes"], "pit beef": ["pit beef"], "oyster bar": ["oyster bar"], "pupuseria": ["pupuseria"],
         "ethiopian": ["ethiopian"], "route 40 korean": ["route 40 korean"], "snowballs": ["snowballs"], "oldest": ["oldest"]}

# MICHELIN: no Maryland guide (guide.michelin.com's District of Columbia selection stops at the District line, 2026-09-27 and 2026-11-03)
MICHELIN = []
MI_MATCH = {}
# James Beard (facts with sources)
JBF = [{"name": "Charleston", "city": "Baltimore", "address": "1000 Lancaster St", "honors": ["Outstanding Wine and Other Beverages Program winner 2025"], "sources": [JBF25W, BM_BEST26]},
       {"name": "Beteseb Restaurant", "city": "Silver Spring", "address": "8201 Georgia Ave", "honors": ["Best Chef: Mid-Atlantic semifinalist 2026 (Darmyelesh Alemu)"], "sources": [JBF26, WASH_ETH], "match_names": ["BETESEB"]},
       {"name": "Marta Fine Food and Spirits", "city": "Baltimore", "address": "2127 E Pratt St", "honors": ["Best Chef: Mid-Atlantic semifinalist 2026 (Matthew Oetting)"], "sources": [JBF26], "match_names": ["MARTA"]},
       {"name": "Café Dear Leon", "city": "Baltimore", "address": "2929 O'Donnell St", "honors": ["Outstanding Bakery semifinalist 2026"], "sources": [JBF26], "match_names": ["CAFE DEAR LEON"]}]
# closed, each with a source (none verified this pass)
CLOSED = []


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

json.dump({"restaurants": []}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# Maryland research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a 2025-26 source we may use
- Pit beef beyond Chaps: Pioneer Pit Beef (Catonsville), Big Bad Wolf's House of Barbecue, Jake's Grill (Cockeysville), Charcoal Grill
  (Parkville), Bullhead Pit Beef (Cross Street Market), Hungry Andy's (Fells Point): only undated or pre-2025 Baltimore Magazine pages.
- Pupuserias: Irene's Pupusas (Wheaton, Langley Park), La Casita (Silver Spring), Pupuseria La Familiar (Wheaton, College Park): 2023 and
  older pages only.
- Route 40 Korean: Shin Chon Garden, Honey Pig, Kimko Seafood, K Pocha, Hyeban: Visit Howard County's Koreatown guide is from March 2023;
  each needs its own current listing or a 2025-26 page.
- Oysters: Washington Street Pub (Easton's raw bar, on Talbot County's oyster trail) has no street address there and isn't in our map data.
- Smith Island cake: Smith Island Baking Co. (45 W Chesapeake Ave, Crisfield) is for sale (Chesapeake Bay Magazine, July 2025) and the
  "cake lady" Mary Ada Marshall retired (February 2026); no 2025-26 page names a place to eat a slice yet. Berger cookies: Visit Baltimore
  names Berger's Bakery (a production plant) and Lexington Market's Market Bakery.
- Oldest: The Horse You Came In On (Fells Point) dates its building to 1775, but the saloon took that name in 1972 (Baltimore Magazine);
  Attman's (1915, Corned Beef Row) and Thrasher's (1929, Ocean City's pier) have dated pages without a street address. Reynolds Tavern
  (Annapolis, a 1747 building) has no founding year for the restaurant. The guide shows once it has three.
- James Beard: Pink Flamingo (Best New Bar semifinalist 2026) isn't in our map data; Spike Gjerde (Woodberry Kitchen, Best Chef:
  Mid-Atlantic 2015) cooks at the Tavern at Woodberry Kitchen, with no 2025-26 page; Maison Marconi (America's Classic 2002) closed.
- Blocked or unusable hosts: baltimoresun.com, capitalgazette.com, dc.eater.com, wypr.org, wbaltv.com, whatsupmag.com, marylandmatters.org,
  foodandwine.com, seriouseats.com, bonappetit.com (robots); visitmaryland.org, atlasobscura.com, geodata.md.gov, baltimorecountymd.gov,
  princegeorgescountymd.gov (bot checks); visitworcester.org, somersetcountytourism.com, dorchestertourism.com (unreachable).
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
