"""Step 1: clean the LBS address file and classify every row.
Writes SCR/addresses_full.parquet (with street text and person ids, kept outside the repository; no names are kept even there),
data/county_check.csv (England and Wales: LBS county against the county of the nearest 1851 parish) and prints the data flow.
"""
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from common import *
from rules import COUNTY, SCOT_BY_PLACE, CREE_LON, precision, address_form
from pop1831 import POP

d = pd.read_csv(LBS_ADDR)
n_raw = len(d)
for c in ("street", "district", "town_city", "county", "region", "country"):
    d[c] = d[c].map(unesc).map(lambda s: s.strip() if isinstance(s, str) else s)
occ = d.occupancies.map(json.loads)
d["n_people"] = occ.map(len)
d["person_ids"] = occ.map(lambda L: [str(p["id"]) for p in L])
yrs = occ.map(lambda L: [int(y) for p in L for y in (p.get("start"), p.get("end")) if isinstance(y, str) and y.isdigit()])
d["year_min"] = yrs.map(lambda v: min(v) if v else np.nan)
d["year_max"] = yrs.map(lambda v: max(v) if v else np.nan)
d = d.drop(columns=["occupancies"])
d["has_xy"] = d.lat.notna() & d.lon.notna()
# Reviewer fixes (logged in NOTES.md). (1) Two rows in St Peter Port have country "England" and county "Guernsey": they are in the
# Channel Islands, not Great Britain. (2) Two British rows were geocoded to namesakes abroad (Ipswich to Queensland, Bath to
# Kentucky); they are moved to the median point of the other LBS addresses in the same town and county and treated as area geocodes.
d.loc[d.county.eq("Guernsey"), "country"] = "Guernsey, Channel Islands"
d.loc[d.country.str.startswith("Jersey", na=False), "country"] = "Jersey, Channel Islands"
_gbrow = d.country.isin(GB) & d.has_xy
_out = _gbrow & ~(d.lat.between(49.8, 61.0) & d.lon.between(-8.7, 2.0))
for i in d.index[_out]:
    same = d[_gbrow & ~_out & d.town_city.eq(d.at[i, "town_city"]) & d.county.eq(d.at[i, "county"])]
    assert len(same) >= 1, d.loc[i, ["town_city", "county"]]
    d.loc[i, ["lat", "lon", "class"]] = [same.lat.median(), same.lon.median(), "place"]
print("geocodes moved from abroad to their town:", int(_out.sum()))
GEOFIX = int(_out.sum())
d["gb"] = d.country.isin(GB)
d["precision"] = d["class"].map(precision)
d["form"] = [address_form(s, c) for s, c in zip(d.street, d["class"])]
d["london"] = d.region.eq("London") | d.town_city.isin(["London", "City of London"])

# nearest 1851 parish (England and Wales): county check, 1801 density, urban flag
P = pd.read_csv(PARISH, usecols=["GAZ_CNTY", "PARISH", "lat", "lon", "density", "AREA_m2", "urban"])
pcounty = {"YORKSHIRE, WEST RIDING": "Yorkshire", "YORKSHIRE, NORTH RIDING": "Yorkshire", "YORKSHIRE, EAST RIDING": "Yorkshire",
           "ISLE OF WIGHT": "Hampshire", "CARNARVONSHIRE": "Caernarfonshire", "GLAMORGANSHIRE": "Glamorgan"}
P["county"] = P.GAZ_CNTY.map(lambda s: pcounty.get(s, s.title()))
assert set(P.county) <= set(POP), set(P.county) - set(POP)
coslat = np.cos(np.radians(52.5))
tree = cKDTree(np.c_[P.lon.values * coslat, P.lat.values])
ew = d.has_xy & d.country.isin(["England", "Wales"])
dist, ix = tree.query(np.c_[d.loc[ew, "lon"].values * coslat, d.loc[ew, "lat"].values])
d.loc[ew, "parish_county"] = P.county.values[ix]
d.loc[ew, "parish_km"] = dist * 111.2
d.loc[ew, "density1801"] = P.density.values[ix]
d.loc[ew, "cv_urban"] = P.urban.values[ix]


def hist_county(r):
    c = r.county
    if r.country not in GB:
        return None
    if isinstance(c, str) and c in POP:
        return c
    if isinstance(c, str) and c in COUNTY and COUNTY[c]:
        return COUNTY[c]
    if r.country in ("England", "Wales"):
        return r.parish_county if isinstance(r.parish_county, str) else None
    for k, v in SCOT_BY_PLACE.items():
        if k in (r.region, r.district, r.town_city):
            return v
    if c == "Galloway":
        return "Wigtownshire" if r.lon < CREE_LON else "Kirkcudbrightshire"
    return None


d["hcounty"] = d.apply(hist_county, axis=1)
gbx = d.gb & d.has_xy
miss = d[gbx & d.hcounty.isna()]
assert miss.empty, miss[["street", "town_city", "county", "region"]]
d["county_source"] = np.where(d.county.isin(POP), "LBS", np.where(d.county.map(lambda c: bool(COUNTY.get(c))), "LBS (renamed)", "point"))
# England and Wales: LBS county against the nearest parish's county
chk = d[gbx & d.country.isin(["England", "Wales"]) & (d.county_source != "point")]
chk = chk.assign(agree=chk.hcounty.eq(chk.parish_county))
dis = chk[~chk.agree]
dis[["address_id", "hcounty", "parish_county", "parish_km", "precision", "town_city"]].sort_values("hcounty").to_csv(f"{DATA}/county_check.csv", index=False)
print(f"rows {n_raw}; no point {(~d.has_xy).sum()}; GB with point {gbx.sum()}; Ireland {(d.country == 'Ireland').sum()}; "
      f"Channel Islands {d.country.str.endswith('Channel Islands', na=False).sum()}; overseas {(~d.country.isin(GB + ['Ireland']) & ~d.country.str.endswith('Channel Islands', na=False)).sum()}")
print(f"E&W county agreement {chk.agree.mean() * 100:.1f}% of {len(chk)}; disagreements {len(dis)}")
print(dis.groupby(["hcounty", "parish_county"]).size().sort_values(ascending=False).head(20).to_string())
print(d[gbx].groupby(["country", "form"]).size().unstack())
print(d[gbx].groupby(["form", "precision"]).size().unstack())
d.to_parquet(f"{SCR}/addresses_full.parquet")
