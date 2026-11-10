"""Step 6: page data and index.html.
  data/points.json   every geocoded LBS address in Great Britain, Ireland and the Channel Islands WITHOUT names or street text:
                     [address_id (LBS map id), lon, lat, form, linked people, geocode precision, town, county, country,
                     lbs_person (the LBS person id of the first linked record, for the link to UCL; no names)]
  data/site.json     Scottish county circles, search list (towns and counties), headline numbers for the page
  index.html         from code/page_template.html + code/page_essay.html, filled from data/results.json
The publisher fills 10.5281/zenodo.24113858, https://doi.org/10.5281/zenodo.24113858 and https://blog.tristanhotham.com/2026/10/31/slavery-compensation/."""
import numpy as np, pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
C = pd.read_csv(f"{DATA}/counties.csv")
d = pd.read_parquet(f"{SCR}/addresses_full.parquet")
FORMS = ["street address", "named house", "settlement only", "institution"]
PRECS = ["exact", "street", "area"]
show = d[d.has_xy & (d.country.isin(GB + ["Ireland"]) | d.country.str.endswith("Channel Islands", na=False))].copy()


def town(r):
    t = r.town_city if isinstance(r.town_city, str) else (r.district if isinstance(r.district, str) else "")
    return re.sub(r"\s*\(near\)", "", t).strip()


pts = []
for r in show.itertuples():
    cty = r.hcounty if isinstance(r.hcounty, str) else (r.county if isinstance(r.county, str) else "")
    pts.append([int(r.address_id), round(r.lon, 5), round(r.lat, 5), FORMS.index(r.form), int(r.n_people), PRECS.index(r.precision),
                town(r), cty, r.country.split(", ")[-1] if r.country.endswith("Channel Islands") else r.country,
                int(r.person_ids[0]) if len(r.person_ids) else None])
jsave({"fields": ["address_id", "lon", "lat", "form", "people", "precision", "town", "county", "country", "lbs_person"], "forms": FORMS, "precisions": PRECS,
       "points": pts}, f"{DATA}/points.json")
for p in pts:  # no personal names anywhere in the page data
    assert isinstance(p[6], str)

S = C[C.nation == "Scotland"]
scot = [{"county": r.county, "lon": round(r.cen_lon, 4), "lat": round(r.cen_lat, 4), "n": int(r.addresses), "rate": round(r.rate10k, 2),
         "pop": int(r.pop1831), "people": int(r.people), "all": int(r.lbs_all), "cov": None if r.coverage_pc != r.coverage_pc else round(r.coverage_pc)}
        for r in S.itertuples()]
T = pd.read_csv(f"{DATA}/towns.csv")
g = d[d.gb & d.has_xy].copy()
search = []
for nm, x in show.assign(t=[town(r) for r in show.itertuples()]).groupby("t"):
    if nm:
        search.append([nm, round(x.lon.median(), 4), round(x.lat.median(), 4), len(x), "town"])
for r in C.itertuples():
    search.append([r.county, round(r.cen_lon, 4), round(r.cen_lat, 4), int(r.addresses), "county"])
search.sort(key=lambda s: -s[3])
site = {"scot": scot, "search": search, "gb": R["q1"]["gb"], "rate": round(R["q1"]["gb_rate10k"], 2)}
jsave(site, f"{DATA}/site.json")
print("points", len(pts), os.path.getsize(f"{DATA}/points.json") // 1024, "KB; site", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")

KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("%%ESSAY%%", open(os.path.join(ROOT, "code", "page_essay.html"), encoding="utf-8").read())
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI).replace("{{BYLINE}}", BYLINE).replace("{{VERSION}}", "2026a").replace("{{CAVEAT}}", LBS_CAVEAT)
t = fill(t, R, KEEP)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= KEEP, set(re.findall(r"\{\{([^}]+)\}\}", t))
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in BAD:
    assert bad not in vis, bad
assert t.rstrip().endswith("</html>") and 'site-nav.js" defer></script>\n</body>' in t
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
