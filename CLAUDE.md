# Maryland Eats (md-eats) — notes for Claude Code sessions

Built 2026-11-03 by a side session while Nick was away, after Rhode Island and Louisiana, ported from `../la-eats/` with every fix of
that day (the 10-29 all-states QA P0/P1s, Nevada's `name_key()` ids, the narrowed loan rule, the private-dining exceptions, the web
map frame and Back key). Local only: no git repo, no remote, nothing published. Sources and calibration: `playbook/12-sources.md`.
Brand: `playbook/05-naming.md` — **provisional**, every choice waits for Nick ("Maryland Eats: Restaurants", Home Screen "MD Eats";
steamed-crab icon A on Calvert black; the flag palette: Calvert black #1A1A1A, Crossland red #C8102E, Calvert gold #F2B705 fill only,
warm white #FAF6EC; the Calvert quarters as the header band).

## Maryland is different
- **Counties, with Baltimore City its own.** 24 county-level jurisdictions from Overture's land division areas (renamed to Baltimore
  City and St. Mary's County). Kent Island, Tilghman, Smith Island, Hooper and Deal islands and Solomons are checked inside the outline
  (`fetch_overture.py`). The in-state test widens the outline ~300 m over the water only (the neighbours' land is cut back out), and a
  pin just over the water takes the nearest county within ~1 km (`calibrate.py county_of`, `maryland.py county_at`).
- **Regions** (6, by county list, `maryland.py`): Baltimore (City and County; the main one), Capital Region (Montgomery, Prince
  George's, Frederick), Annapolis & Central, Southern Maryland, Western Maryland, Eastern Shore.
- **Official records** (`pipeline/fetch_official.py` downloads, `official.py` loads): Montgomery's food inspections (`mont`, results
  shown), Montgomery's alcohol licenses (`abs`, no name: joined to the one facility at the address), Baltimore City's liquor licenses
  (`baltliq`; "Adult" licenses hide the venue at that address), Anne Arundel's inspected facilities (`aa`, confirmation only), Prince
  George's stale list (`pg`, calibration only). `road()` treats Route/US/MD/Rt numbers as one road; `street_key()` reads "20940-A".
- **Inspections:** Montgomery places show the county's latest result (Pass, Fail, Closed, Closed With Complaint) and date in the app
  (`Place.inspection`, detail `in`) and on the site (detail `ins`); never in a list, a sort or a grade. Everyone else links MDH's list
  of health departments.
- **No MICHELIN.** Honors are James Beard only (4). The Bib Gourmand switch hides itself; `BibGourmandFilterTests` was removed.

## Rebuild
```bash
cd pipeline
../.venv/bin/python check_sources.py URL...   # a new host first
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python maryland.py && ../.venv/bin/python build_research.py && ../.venv/bin/python maryland.py
MD_APP=1 ../.venv/bin/python maryland.py && cd .. && cp data/app/places.json data/app/detail-*.json MarylandEats/Resources/
.venv/bin/python pipeline/check_websites.py --retry-transient   # link verification; re-export after
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
(`listings.py` must run before `calibrate.py`, and `maryland.py` once before `build_research.py`, which matches names against
`site/maryland.json`.)

## App, site, screenshots
- App: `MarylandEats/` (XcodeGen `project.yml`, bundle `com.marylandeats.ios`), tests in `MarylandEatsTests/` (data guards: adult venues,
  blocklisted and multi-URL websites, bad and legal names, non-restaurants, listed twice, no Google data; Montgomery results; the
  outline with its islands). Run tests: `DEVELOPER_DIR="/Applications/Xcode 1.app/Contents/Developer" xcodebuild test ...
  CODE_SIGNING_ALLOWED=NO` on a temporary simulator. Archive only with Xcode 1.app (27.1, 27A9275); Xcode.app is a beta.
  Run `xcodegen generate` after the export whenever the set of `Resources/*.json` files changes: the project lists the files it
  found when it was generated, and an app built without them still compiles but opens on "Couldn't open the list" (2026-11-04).
- Site: `scripts/make-site.py` writes `docs/` (16 pages) and `playbook/site-numbers.json`; `scripts/explore.js` is the web app;
  `scripts/qa-site.py` the QA. Site URL for now: nickstrom5.github.io/maryland-eats (no CNAME).
- OTA data: `docs/data/app/` via `scripts/publish_app_data.py` (`../OTA-DATA.md`).
- Screenshots: `scripts/capture-screenshots.sh <sim>` (ScreenshotMode pins the Inner Harbor; Silver Spring for pupusas and
  ethiopian, Ellicott City for korean), then `scripts/site-images.sh`, then make-site + qa-site. App Store frames:
  `scripts/appstore-screenshots.py`. Rebuild the site before the unit tests: `ShareLinkTests` reads the web app's ids from `docs/`.
- Last run 2026-11-04: 49 unit tests passed (temporary iPhone 17 Pro Max, iOS 27.0, Xcode 1.app); screenshots from the same data.
- Not ported: the App Store listing writer and the private Google-2021 leaderboard. `site/` holds the leaderboard's data and is
  git-ignored with `data/`.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
