"""Step 2: country-house candidates against today's listed buildings (rules fixed in NOTES.md).
Reads SCR/addresses_full.parquet and the national lists; writes SCR/candidates.parquet (with the matched listed name, for the hand
check), data/listed_match_summary.csv (no personal names; house names are historic property names) and SCR/great_houses.parquet
(England and Wales Grade I and II* great houses with their historic county)."""
import numpy as np, pandas as pd
from scipy.spatial import cKDTree
from rapidfuzz import fuzz
from common import *
from rules import distinctive, great_house, same_house

d = pd.read_parquet(f"{SCR}/addresses_full.parquet")
gb = d[d.gb & d.has_xy].copy()
urban = gb.density1801.ge(1000)
cand = gb[(gb.form == "named house") & ~gb.london & ~urban].copy()
cand["name"] = cand.street.map(lambda s: re.split(r"[,(\[]", s)[0].strip())
cand["dist_words"] = cand.name.map(distinctive)
print("candidates", len(cand), "with distinctive words", cand.dist_words.map(len).gt(0).sum())

cols = ["id", "name", "grade", "type", "lat", "lon"]
L = pd.concat([pd.read_csv(f"{LISTED}/listed_{p}.csv.gz", usecols=cols, dtype={"id": str}).assign(nation=n) for p, n in
               (("england_part1", "England"), ("england_part2", "England"), ("wales", "Wales"), ("scotland", "Scotland"))], ignore_index=True)
L = L.dropna(subset=["lat", "lon"])
L["lname"] = L.name.fillna("").str.lower().str.replace("'", "", regex=False)
print("listed entries", len(L))
coslat = np.cos(np.radians(54))
T = cKDTree(np.c_[L.lon.values * coslat * 111.2, L.lat.values * 111.2])


def match(r):
    rad = 5.0 if r.precision == "area" else 2.0
    w = r.dist_words
    if not w:
        return pd.Series({"listed_id": None, "listed_name": None, "listed_grade": None, "match_km": np.nan, "score": 0, "n_near": 0})
    idx = T.query_ball_point([r.lon * coslat * 111.2, r.lat * 111.2], rad)
    best = (0, None)
    key = " ".join(w)
    for i in idx:
        ln = L.lname.values[i]
        if w[0] not in ln:
            continue
        sc = same_house(r["name"], L.name.values[i])
        if sc >= 90:
            km = math.hypot((L.lon.values[i] - r.lon) * coslat * 111.2, (L.lat.values[i] - r.lat) * 111.2)
            k = (sc, L.type.values[i] == "house", -km)
            if best[1] is None or k > best[0]:
                best = (k, i)
    if best[1] is None:
        return pd.Series({"listed_id": None, "listed_name": None, "listed_grade": None, "match_km": np.nan, "score": 0, "n_near": len(idx)})
    i = best[1]
    return pd.Series({"listed_id": L.id.values[i], "listed_name": L.name.values[i], "listed_grade": L.grade.values[i],
                      "match_km": -best[0][2], "score": best[0][0], "n_near": len(idx)})


M = cand.apply(match, axis=1)
cand = pd.concat([cand, M], axis=1)
cand["listed"] = cand.listed_id.notna()
print("matched", cand.listed.sum(), "of", len(cand), f"{cand.listed.mean() * 100:.1f}%")
print(cand.groupby("country").listed.agg(["sum", "count", "mean"]))
print(cand.groupby("precision").listed.agg(["sum", "count", "mean"]))
cand.drop(columns=["person_ids"]).to_parquet(f"{SCR}/candidates.parquet")

# great houses, England and Wales, with historic county by nearest 1851 parish
G = L[L.nation.isin(["England", "Wales"])].copy()
G = G[[great_house(n, g, t) for n, g, t in zip(G.name, G.grade, G.type)]]
P = pd.read_csv(PARISH, usecols=["GAZ_CNTY", "lat", "lon", "density"])
pcounty = {"YORKSHIRE, WEST RIDING": "Yorkshire", "YORKSHIRE, NORTH RIDING": "Yorkshire", "YORKSHIRE, EAST RIDING": "Yorkshire",
           "ISLE OF WIGHT": "Hampshire", "CARNARVONSHIRE": "Caernarfonshire", "GLAMORGANSHIRE": "Glamorgan"}
P["county"] = P.GAZ_CNTY.map(lambda s: pcounty.get(s, s.title()))
c2 = np.cos(np.radians(52.5))
_, ix = cKDTree(np.c_[P.lon.values * c2, P.lat.values]).query(np.c_[G.lon.values * c2, G.lat.values])
G["hcounty"] = P.county.values[ix]
G["density1801"] = P.density.values[ix]
G[["id", "name", "grade", "lat", "lon", "nation", "hcounty", "density1801"]].to_parquet(f"{SCR}/great_houses.parquet")
print("great houses (E&W, I and II*)", len(G), G.grade.value_counts().to_dict())
print(G.sample(25, random_state=2).name.tolist())
