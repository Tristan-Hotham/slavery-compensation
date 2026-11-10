"""Step 3: the pre-specified analysis (NOTES.md). Writes data/results.json, data/counties.csv, data/towns.csv,
data/forms.csv, data/listed_handcheck.csv, data/county_listed.csv, data/models.csv. No personal names are written anywhere."""
import numpy as np, pandas as pd, warnings
import statsmodels.api as sm
from scipy.stats import spearmanr
from common import *
from pop1831 import POP, check
import handcheck as HC

warnings.filterwarnings("ignore")
check()
R = {}
d = pd.read_parquet(f"{SCR}/addresses_full.parquet")
LP = pd.DataFrame(jload(LBS_POP))
LP["county"] = LP.county.map(unesc)
LP.loc[LP.county == "Orkney, Shetland, Fair Isle", "county"] = "Orkney and Shetland"

# ---------------- data flow ----------------
gbm = d.gb & d.has_xy
g = d[gbm].copy()
pids_gb = set(p for L in g.person_ids for p in L)
R["flow"] = {"rows": len(d), "no_point": int((~d.has_xy).sum()), "gb": int(gbm.sum()),
             "england": int((g.country == "England").sum()), "scotland": int((g.country == "Scotland").sum()), "wales": int((g.country == "Wales").sum()),
             "ireland": int(((d.country == "Ireland") & d.has_xy).sum()), "channel": int((d.country.str.endswith("Channel Islands") & d.has_xy).sum()),
             "overseas": int((d.has_xy & ~d.country.isin(GB + ["Ireland"]) & ~d.country.str.endswith("Channel Islands")).sum()),
             "links_all": int(d.n_people.sum()), "people_all": len(set(p for L in d.person_ids for p in L)),
             "links_gb": int(g.n_people.sum()), "people_gb": len(pids_gb), "zero_people_gb": int((g.n_people == 0).sum()),
             "multi_people_gb": int((g.n_people >= 2).sum()), "max_people": int(g.n_people.max()),
             "lbs_table_addresses": int(LP.addresses.sum()), "lbs_table_located": int(LP.addresses_located.sum()),
             "lbs_table_located_pc": LP.addresses_located.sum() / LP.addresses.sum() * 100,
             "county_check_n": int(((g.country != "Scotland") & (g.county_source != "point")).sum())}
assert R["flow"]["gb"] + R["flow"]["ireland"] + R["flow"]["channel"] + R["flow"]["overseas"] + R["flow"]["no_point"] == len(d)
cc = pd.read_csv(f"{DATA}/county_check.csv")
R["flow"]["county_disagree"] = len(cc)
R["flow"]["county_agree_pc"] = (1 - len(cc) / R["flow"]["county_check_n"]) * 100
R["flow"]["county_from_point"] = int((g.county_source == "point").sum())
R["flow"]["precision"] = {k: int(v) for k, v in g.precision.value_counts().items()}
R["flow"]["precision_pc"] = {k: v / len(g) * 100 for k, v in g.precision.value_counts().items()}
R["flow"]["dup_points_gb"] = int(g.duplicated(["lat", "lon"]).sum())

# ---------------- county table ----------------
C = pd.DataFrame([{"county": k, "pop1831": v[0], "pop1841": v[1], "nation": v[2]} for k, v in POP.items()])
grp = g.groupby("hcounty")
C["addresses"] = C.county.map(grp.size()).fillna(0).astype(int)
C["links"] = C.county.map(grp.n_people.sum()).fillna(0).astype(int)
C["people"] = C.county.map(grp.person_ids.apply(lambda s: len(set(p for L in s for p in L)))).fillna(0).astype(int)
C["street_addr"] = C.county.map(g[g.form == "street address"].groupby("hcounty").size()).fillna(0).astype(int)
C["named_houses"] = C.county.map(g[g.form == "named house"].groupby("hcounty").size()).fillna(0).astype(int)
lp = LP.set_index("county")
C["lbs_all"] = C.county.map(lp.addresses).fillna(0).astype(int)
C["lbs_located"] = C.county.map(lp.addresses_located).fillna(0).astype(int)
C["lbs_pop_k"] = C.county.map(lp["pop"])
C["region"] = C.county.map(lp.region).map(unesc)
# the merged LBS row "Lancashire, Merseyside" is part of Lancashire
mers = LP[LP.county == "Lancashire, Merseyside"].iloc[0]
C.loc[C.county == "Lancashire", ["lbs_all", "lbs_located"]] += [int(mers.addresses), int(mers.addresses_located)]
assert C.region.notna().all(), C[C.region.isna()]
C["coverage_pc"] = np.where(C.lbs_all > 0, C.lbs_located / C.lbs_all.replace(0, np.nan) * 100, np.nan)
C["rate10k"] = C.addresses / C.pop1831 * 1e4
C["people10k"] = C.people / C.pop1831 * 1e4
C["all10k"] = C.lbs_all / C.pop1831 * 1e4
C["rate10k_1841"] = C.addresses / C.pop1841 * 1e4

# county centres: England and Wales, 1801-population-weighted mean of 1851 parish centroids; Scotland, the county town
P = pd.read_csv(PARISH, usecols=["GAZ_CNTY", "lat", "lon", "density", "AREA_m2"])
pcounty = {"YORKSHIRE, WEST RIDING": "Yorkshire", "YORKSHIRE, NORTH RIDING": "Yorkshire", "YORKSHIRE, EAST RIDING": "Yorkshire",
           "ISLE OF WIGHT": "Hampshire", "CARNARVONSHIRE": "Caernarfonshire", "GLAMORGANSHIRE": "Glamorgan"}
P["county"] = P.GAZ_CNTY.map(lambda s: pcounty.get(s, s.title()))
P["w"] = P.density.fillna(P.density.median()) * P.AREA_m2 / 1e6
cen = P.groupby("county").apply(lambda x: pd.Series({"lon": np.average(x.lon, weights=x.w), "lat": np.average(x.lat, weights=x.w)}))
TOWN = {"Aberdeenshire": "Aberdeen", "Argyll": "Inveraray", "Ayrshire": "Ayr", "Banffshire": "Banff", "Berwickshire": "Duns", "Bute": "Rothesay",
        "Caithness": "Wick", "Clackmannanshire": "Clackmannan", "Dumfriesshire": "Dumfries", "Dunbartonshire": "Dumbarton",
        "Midlothian (Edinburgh)": "Edinburgh", "Fife": "Cupar", "Haddingtonshire (East Lothian)": "Haddington", "Kinross-shire": "Kinross",
        "Kirkcudbrightshire": "Kirkcudbright", "Lanarkshire": "Lanark", "Linlithgowshire (West Lothian)": "Linlithgow", "Peeblesshire": "Peebles",
        "Renfrewshire": "Renfrew", "Roxburghshire": "Jedburgh", "Selkirkshire": "Selkirk", "Stirlingshire": "Stirling", "Wigtownshire": "Wigtown",
        "Moray": "Elgin", "Forfarshire": "Forfar", "Inverness-shire": "Inverness", "Kincardineshire": "Stonehaven", "Nairnshire": "Nairn",
        "Orkney and Shetland": "Kirkwall", "Perthshire": "Perth", "Ross & Cromarty": "Dingwall", "Sutherland": "Dornoch"}
S = pd.read_csv(SETT, sep="\t", quoting=3)
S["name"] = S["?pl"].str.extract(r'^"(.*)"@en')[0]
S[["lon", "lat"]] = S["?coord"].str.extract(r"POINT\(([-\d.]+) ([-\d.]+)\)").astype(float)
S = S[(S.lat > 54.6) & S["?pop"].notna()].sort_values("?pop", ascending=False).drop_duplicates("name")
st = S.set_index("name")
for k, t in TOWN.items():
    cen.loc[k, ["lon", "lat"]] = st.loc[t, ["lon", "lat"]].values
C["cen_lon"] = C.county.map(cen.lon); C["cen_lat"] = C.county.map(cen.lat)
assert C.cen_lon.notna().all(), C[C.cen_lon.isna()].county.tolist()
dist = np.vstack([gc_km(C.cen_lat.values, C.cen_lon.values, la, lo) for lo, la in PORTS.values()]).T
C["port_km"] = dist.min(1)
C["nearest_port"] = np.array(list(PORTS))[dist.argmin(1)]
C["port"] = C.county.isin(PORT_COUNTIES).astype(int)
C["log_port_km"] = np.log(np.maximum(C.port_km, 5.0))
C["wales"] = (C.nation == "Wales").astype(int); C["scotland"] = (C.nation == "Scotland").astype(int)

# ---------------- Q1 concentration ----------------
N = len(g); popGB = C.pop1831.sum()
lon_n = int(g.london.sum())
R["q1"] = {"gb": N, "pop_gb": int(popGB), "london": lon_n, "london_pc": lon_n / N * 100,
           "london_region": int(g.region.eq("London").sum()), "london_extra": int((g.london & ~g.region.eq("London")).sum()),
           "middlesex": int(C.loc[C.county == "Middlesex", "addresses"].iloc[0]),
           "middlesex_pc": C.loc[C.county == "Middlesex", "addresses"].iloc[0] / N * 100,
           "middlesex_pop_pc": C.loc[C.county == "Middlesex", "pop1831"].iloc[0] / popGB * 100,
           "gb_rate10k": N / popGB * 1e4}
R["q1"]["middlesex_ratio"] = R["q1"]["middlesex_pc"] / R["q1"]["middlesex_pop_pc"]
for nat in GB:
    x = C[C.nation == nat]
    R["q1"][f"{nat.lower()}_n"] = int(x.addresses.sum()); R["q1"][f"{nat.lower()}_rate10k"] = x.addresses.sum() / x.pop1831.sum() * 1e4
    R["q1"][f"{nat.lower()}_pc"] = x.addresses.sum() / N * 100; R["q1"][f"{nat.lower()}_pop_pc"] = x.pop1831.sum() / popGB * 100


def gini(counts, pops):
    r = counts / pops; o = np.argsort(r)
    p = np.r_[0, np.cumsum(pops[o]) / pops.sum()]; c = np.r_[0, np.cumsum(counts[o]) / counts.sum()]
    return 1 - np.sum((p[1:] - p[:-1]) * (c[1:] + c[:-1]))


cnt, pops = C.addresses.values.astype(float), C.pop1831.values.astype(float)
R["q1"]["gini"] = gini(cnt, pops)
rng = np.random.default_rng(2026)
boot = [gini(rng.multinomial(int(cnt.sum()), cnt / cnt.sum()).astype(float), pops) for _ in range(2000)]
R["q1"]["gini_lo"], R["q1"]["gini_hi"] = np.percentile(boot, [2.5, 97.5])
R["q1"]["gini_people"] = gini(C.people.values.astype(float), pops)
R["q1"]["gini_all"] = gini(C.lbs_all.values.astype(float), pops)
R["q1"]["gini_excl_mx"] = gini(C[C.county != "Middlesex"].addresses.values.astype(float), C[C.county != "Middlesex"].pop1831.values.astype(float))
# Lorenz points for the figure
o = np.argsort(cnt / pops)
R["lorenz"] = {"pop": list(np.r_[0, np.cumsum(pops[o]) / pops.sum()]), "addr": list(np.r_[0, np.cumsum(cnt[o]) / cnt.sum()])}
# half the addresses: how many counties, what share of people
oc = np.argsort(-cnt); cs = np.cumsum(cnt[oc]) / cnt.sum(); k = int(np.searchsorted(cs, 0.5) + 1)
R["q1"]["half_counties"] = k; R["q1"]["half_pop_pc"] = pops[oc][:k].sum() / pops.sum() * 100
R["q1"]["zero_counties"] = int((C.addresses == 0).sum())

# ranking of counties by rate (counties with at least 10,000 people)
Ck = C[C.pop1831 >= 10000].sort_values("rate10k", ascending=False)
R["top_rate"] = [{"county": r.county, "rate": r.rate10k, "n": int(r.addresses), "pop": int(r.pop1831)} for r in Ck.head(12).itertuples()]
R["bottom_rate"] = [{"county": r.county, "rate": r.rate10k, "n": int(r.addresses)} for r in Ck.tail(8).itertuples()]
R["county_n"] = len(C)
for nm in ("Middlesex", "Gloucestershire", "Somerset", "Midlothian (Edinburgh)", "Lancashire", "Lanarkshire", "Yorkshire", "Surrey", "Kent",
           "Nairnshire", "Moray", "Devon", "Durham", "Glamorgan", "Staffordshire", "Renfrewshire", "Inverness-shire"):
    r = C[C.county == nm].iloc[0]
    R.setdefault("c", {})[nm.split(" (")[0]] = {"n": int(r.addresses), "rate": r.rate10k, "pop": int(r.pop1831), "cov": r.coverage_pc,
                                                 "all": int(r.lbs_all), "people": int(r.people), "port_km": r.port_km}
R["coverage"] = {"min": C[C.lbs_all >= 10].coverage_pc.min(), "max": C[C.lbs_all >= 10].coverage_pc.max(),
                 "min_county": C[C.lbs_all >= 10].sort_values("coverage_pc").county.iloc[0],
                 "max_county": C[C.lbs_all >= 10].sort_values("coverage_pc").county.iloc[-1],
                 "n10": int((C.lbs_all >= 10).sum()), "median": C[C.lbs_all >= 10].coverage_pc.median(),
                 "rho_cov_rate": spearmanr(C[C.lbs_all >= 10].coverage_pc, C[C.lbs_all >= 10].rate10k)[0],
                 "our_vs_lbs_located_abs": int((C.addresses - C.lbs_located).abs().sum())}
# LBS population column vs census
lbsdiff = C[C.lbs_pop_k.notna() & (C.pop1841 > 0)].copy()
lbsdiff["rel"] = lbsdiff.lbs_pop_k * 1000 / lbsdiff.pop1841 - 1
R["lbs_pop"] = {"n": len(lbsdiff), "within5_1841": int((lbsdiff.rel.abs() <= 0.05).sum()),
                "off": [{"county": r.county, "lbs_k": float(r.lbs_pop_k), "census1841": int(r.pop1841), "census1831": int(r.pop1831)}
                        for r in lbsdiff[lbsdiff.rel.abs() > 0.05].itertuples()]}

# towns
def town(r):
    if r.london:
        return "London"
    t = r.town_city if isinstance(r.town_city, str) else (r.district if isinstance(r.district, str) else None)
    if not t:
        return None
    t = re.sub(r"\s*\(near\)|,\s*Isle of Wight", "", t).strip()
    return {"City of London": "London", "Clifton": "Bristol", "Leith": "Edinburgh", "West Derby": "Liverpool"}.get(t, t)


g["town"] = [town(r) for r in g.itertuples()]
T = g.groupby("town").agg(addresses=("address_id", "size"), links=("n_people", "sum"), county=("hcounty", lambda s: s.mode().iloc[0])).sort_values("addresses", ascending=False)
T["street_pc"] = g[g.form == "street address"].groupby("town").size().reindex(T.index).fillna(0) / T.addresses * 100
T.reset_index().to_csv(f"{DATA}/towns.csv", index=False)
R["towns"] = [{"town": t, "n": int(r.addresses), "county": r.county} for t, r in T.drop(index=["Isle of Wight"], errors="ignore").head(15).iterrows()]
R["top5_pc"] = T.addresses.head(5).sum() / N * 100
R["n_towns"] = int(len(T)); R["towns_one"] = int((T.addresses == 1).sum())
R["no_town"] = int(g.town.isna().sum())
R["town"] = {t: int(T.loc[t, "addresses"]) for t in ("London", "Bristol", "Edinburgh", "Liverpool", "Bath", "Glasgow", "Brighton", "Cheltenham",
                                                      "Exeter", "Tunbridge Wells", "Inverness", "Aberdeen") if t in T.index}

# ---------------- H2 models ----------------
M = C[C.pop1831 > 0].copy()
X0 = ["port", "log_port_km", "wales", "scotland"]
rows = []


def fit(df, y, xs=X0, fam="poisson", label="", group=""):
    xs = [x for x in xs if df[x].nunique() > 1]
    X = sm.add_constant(df[xs].astype(float))
    off = np.log(df.pop1831.astype(float))
    if fam == "poisson":
        m = sm.GLM(df[y].astype(float), X, family=sm.families.Poisson(), offset=off).fit(cov_type="HC1")
    else:
        m = sm.NegativeBinomial(df[y].astype(float), X, offset=off).fit(disp=0, maxiter=200, cov_type="HC1")
    out = {"label": label, "group": group, "n": int(len(df)), "y": y, "fam": fam}
    for x in ("port", "log_port_km"):
        if x in m.params:
            b, se = m.params[x], m.bse[x]
            out[x] = {"irr": float(np.exp(b)), "lo": float(np.exp(b - 1.96 * se)), "hi": float(np.exp(b + 1.96 * se)), "p": float(m.pvalues[x])}
    rows.append(out)
    return out


main = fit(M, "addresses", label="Main: Poisson, geocoded addresses", group="main")
R["h2"] = {"main": main}
# doubling of distance: IRR^(ln 2)
R["h2"]["double"] = main["log_port_km"]["irr"] ** np.log(2)
R["h2"]["double_lo"] = main["log_port_km"]["lo"] ** np.log(2); R["h2"]["double_hi"] = main["log_port_km"]["hi"] ** np.log(2)
R["h2"]["nb"] = fit(M, "addresses", fam="nb", label="Negative binomial", group="alt")
R["h2"]["people"] = fit(M, "people", label="Linked people (distinct) instead of addresses", group="alt")
R["h2"]["all"] = fit(M, "lbs_all", label="All LBS addresses, located or not", group="alt")
R["h2"]["no_mx"] = fit(M[M.county != "Middlesex"], "addresses", label="Middlesex left out", group="alt")
R["h2"]["england"] = fit(M[M.nation == "England"], "addresses", label="England only", group="alt")
R["h2"]["scotland"] = fit(M[M.nation == "Scotland"], "addresses", label="Scotland only", group="alt")
R["h2"]["pop1841"] = fit(M.assign(pop1831=M.pop1841), "addresses", label="1841 population as the offset", group="alt")
R["h2"]["named"] = fit(M, "named_houses", label="Named houses only", group="alt")
R["h2"]["street"] = fit(M, "street_addr", label="Street addresses only", group="alt")
loro = []
for reg in sorted(M.region.unique()):
    o_ = fit(M[M.region != reg], "addresses", label=f"Without {reg}", group="loro")
    loro.append(o_)
R["h2"]["loro"] = {"n": len(loro), "dist_min": min(o["log_port_km"]["irr"] for o in loro), "dist_max": max(o["log_port_km"]["irr"] for o in loro),
                   "dist_hi_max": max(o["log_port_km"]["hi"] for o in loro),
                   "port_min": min(o["port"]["irr"] for o in loro if "port" in o), "port_max": max(o["port"]["irr"] for o in loro if "port" in o),
                   "port_lo_min": min(o["port"]["lo"] for o in loro if "port" in o),
                   "fail": [o["label"].replace("Without ", "") for o in loro if o["log_port_km"]["hi"] >= 1],
                   "se": [o for o in loro if o["label"] == "Without South-East England"][0]}
# exploratory (not in the plan): distance to London alone instead of the nearest of the four ports
M["log_london_km"] = np.log(np.maximum(gc_km(M.cen_lat.values, M.cen_lon.values, PORTS["London"][1], PORTS["London"][0]), 5.0))
M["log_port_km_main"] = M.log_port_km
ex = fit(M.assign(log_port_km=M.log_london_km), "addresses", label="Exploratory: distance to London instead of the nearest port", group="exploratory")
R["h2"]["london_only"] = ex
m1 = sm.GLM(M.addresses, sm.add_constant(M[X0].astype(float)), family=sm.families.Poisson(), offset=np.log(M.pop1831)).fit()
m2 = sm.GLM(M.addresses, sm.add_constant(M[["port", "log_london_km", "wales", "scotland"]].astype(float)), family=sm.families.Poisson(), offset=np.log(M.pop1831)).fit()
R["h2"]["aic_ports"], R["h2"]["aic_london"] = m1.aic, m2.aic
R["h2"]["pseudo_r2"] = 1 - m1.deviance / m1.null_deviance

# placebo: listed great houses (England and Wales, outside 1801-urban parishes) with the same model
G = pd.read_parquet(f"{SCR}/great_houses.parquet")
G = G[~G.density1801.ge(1000)]
C["great"] = C.county.map(G.groupby("hcounty").size()).fillna(0).astype(int)
C.loc[C.nation == "Scotland", "great"] = np.nan
M["great"] = C.great
EW = M[M.nation != "Scotland"].copy()
R["h2"]["ew"] = fit(EW, "addresses", label="England and Wales only (placebo comparison)", group="placebo")
R["h2"]["placebo"] = fit(EW, "great", label="Placebo: listed great houses (Grade I and II*)", group="placebo")
R["h2"]["placebo_gini"] = gini(EW.great.values.astype(float), EW.pop1831.values.astype(float))
R["h2"]["ew_gini"] = gini(EW.addresses.values.astype(float), EW.pop1831.values.astype(float))
pd.DataFrame([{**{k: v for k, v in o.items() if not isinstance(v, dict)}, **{f"{x}_{s}": o[x][s] for x in ("port", "log_port_km") if x in o for s in ("irr", "lo", "hi", "p")}} for o in rows]).to_csv(f"{DATA}/models.csv", index=False)

# ---------------- Q3 address forms ----------------
g["group"] = np.where(g.london, "London", np.where(g.country == "England", "England outside London", g.country))
F = g.groupby(["group", "form"]).size().unstack(fill_value=0)
F["total"] = F.sum(1)
F.to_csv(f"{DATA}/forms.csv")
R["q3"] = {}
for grp_, r in F.iterrows():
    R["q3"][grp_] = {"n": int(r.total), **{f: r.get(f, 0) / r.total * 100 for f in ("street address", "named house", "settlement only", "institution")}}
R["q3"]["all"] = {"n": N, **{f: (g.form == f).mean() * 100 for f in ("street address", "named house", "settlement only", "institution")}}
R["q3"]["outside_london"] = {"n": int((~g.london).sum()), **{f: (g[~g.london].form == f).mean() * 100 for f in ("street address", "named house", "settlement only", "institution")}}
ewo = g[(g.country != "Scotland") & ~g.london & g.density1801.notna()]
R["q3"]["ew_urban"] = {"n": len(ewo), "urban_pc": ewo.density1801.ge(1000).mean() * 100,
                       "named_rural_pc": (~ewo[ewo.form == "named house"].density1801.ge(1000)).mean() * 100,
                       "street_urban_pc": ewo[ewo.form == "street address"].density1801.ge(1000).mean() * 100}
R["q3"]["prec_by_form"] = {f: {k: v * 100 for k, v in g[g.form == f].precision.value_counts(normalize=True).items()} for f in g.form.unique()}

# ---------------- Q4 listed today ----------------
K = pd.read_parquet(f"{SCR}/candidates.parquet")
nm, n = int(K.listed.sum()), len(K)
ms = K.set_index("address_id").loc[HC.MATCH_IDS].reset_index(); ns = K.set_index("address_id").loc[HC.NONMATCH_IDS].reset_index()
assert ms.listed.all() and not ns.listed.any()  # the fixed samples are still matches and non-matches
prec = 1 - len(HC.MATCH_WRONG) / HC.N; miss = len(HC.MISSED) / HC.N
corr = (prec * nm + miss * (n - nm)) / n * 100
# a simple interval: binomial sampling of the two rates
b1 = rng.binomial(HC.N, prec, 4000) / HC.N; b2 = rng.binomial(HC.N, miss, 4000) / HC.N
cb = (b1 * nm + b2 * (n - nm)) / n * 100
hc = pd.concat([ms.assign(sample="match", verdict=["wrong" if i in HC.MATCH_WRONG else "right" for i in range(HC.N)]),
                ns.assign(sample="non-match", verdict=["missed" if i in HC.MISSED else "right" for i in range(HC.N)])])
hc[["sample", "verdict", "name", "town_city", "hcounty", "precision", "listed_name", "listed_grade", "match_km"]].rename(
    columns={"name": "house_name"}).to_csv(f"{DATA}/listed_handcheck.csv", index=False)
R["q4"] = {"cand": n, "matched": nm, "matched_pc": nm / n * 100, "precision_pc": prec * 100, "miss_pc": miss * 100, "corrected_pc": corr,
           "corr_lo": np.percentile(cb, 2.5), "corr_hi": np.percentile(cb, 97.5), "hc_n": HC.N,
           "wrong": len(HC.MATCH_WRONG), "missed": len(HC.MISSED), "no_words": int(K.dist_words.map(len).eq(0).sum())}
for nat in GB:
    x = K[K.country == nat]
    R["q4"][nat.lower()] = {"n": len(x), "matched": int(x.listed.sum()), "pc": x.listed.mean() * 100 if len(x) else None}
for p_ in ("exact", "street", "area"):
    x = K[K.precision == p_]
    R["q4"][p_] = {"n": len(x), "pc": x.listed.mean() * 100}
gr = K[K.listed].listed_grade.value_counts()
R["q4"]["grades"] = {str(k): int(v) for k, v in gr.items()}
R["q4"]["top_grade"] = int(gr.reindex(["I", "A"]).fillna(0).sum()); R["q4"]["second_grade"] = int(gr.reindex(["II*", "B"]).fillna(0).sum())
# by county, England and Wales
C["cand"] = C.county.map(K.groupby("hcounty").size()).fillna(0).astype(int)
C["cand_listed"] = C.county.map(K[K.listed].groupby("hcounty").size()).fillna(0).astype(int)
C["cand_per100great"] = np.where(C.great > 0, C.cand / C.great * 100, np.nan)
CE = C[(C.nation != "Scotland") & (C.great >= 10)]
rho, pr = spearmanr(CE.cand_per100great, CE.rate10k)
R["q4"]["county"] = {"n": len(CE), "rho": rho, "p": pr, "great_total": int(C.great.sum()), "cand_ew": int(C[C.nation != "Scotland"].cand.sum()),
                     "ratio_ew": C[C.nation != "Scotland"].cand.sum() / C.great.sum() * 100,
                     "top": [{"county": r.county, "ratio": r.cand_per100great, "cand": int(r.cand), "great": int(r.great)} for r in CE.sort_values("cand_per100great", ascending=False).head(8).itertuples()],
                     "bottom": [{"county": r.county, "ratio": r.cand_per100great, "cand": int(r.cand), "great": int(r.great)} for r in CE.sort_values("cand_per100great").head(6).itertuples()]}
C[["county", "nation", "great", "cand", "cand_listed", "cand_per100great", "rate10k"]].to_csv(f"{DATA}/county_listed.csv", index=False)

# ---------------- Q5 dates ----------------
yy = g.year_min.dropna()
R["q5"] = {"with_year": int(len(yy)), "with_year_pc": len(yy) / N * 100, "median": float(yy.median()),
           "p10": float(yy.quantile(.1)), "p90": float(yy.quantile(.9)),
           "y1800_1859_pc": ((yy >= 1800) & (yy < 1860)).mean() * 100,
           "by_decade": {str(int(k)): int(v) for k, v in (yy // 10 * 10).value_counts().sort_index().items()}}

# convenience values for the text
h = R["h2"]
h["double_pc"] = 100 * (1 - h["double"]); h["double_lo_pc"] = 100 * (1 - h["double_hi"]); h["double_hi_pc"] = 100 * (1 - h["double_lo"])
ln2 = np.log(2)
for k in ("placebo", "nb", "no_mx", "people", "all", "named", "street", "london_only", "ew", "england", "scotland", "pop1841"):
    o = h[k]["log_port_km"]
    h[f"{k}_dist"], h[f"{k}_dist_lo"], h[f"{k}_dist_hi"] = o["irr"] ** ln2, o["lo"] ** ln2, o["hi"] ** ln2
o = h["loro"]["se"]["log_port_km"]; h["se_dist"], h["se_dist_lo"], h["se_dist_hi"] = o["irr"] ** ln2, o["lo"] ** ln2, o["hi"] ** ln2
h["loro_min"], h["loro_max"] = h["loro"]["dist_min"] ** ln2, h["loro"]["dist_max"] ** ln2

# ---------------- save ----------------
C.to_csv(f"{DATA}/counties.csv", index=False)
R["caveat"] = LBS_CAVEAT
jsave(R, f"{DATA}/results.json", indent=1)
print(json.dumps({k: R[k] for k in ("flow", "q1")}, indent=1, default=str)[:3500])
print("H2 main", main); print("placebo", R["h2"]["placebo"]); print("ew", R["h2"]["ew"])
print("loro", R["h2"]["loro"])
for k in ("nb", "people", "all", "no_mx", "england", "scotland", "pop1841", "named", "street"):
    o = R["h2"][k]; print(k, {x: round(o[x]["irr"], 3) if x in o else None for x in ("port", "log_port_km")}, {x: (round(o[x]["lo"], 3), round(o[x]["hi"], 3)) for x in ("port", "log_port_km") if x in o})
print("q3", json.dumps(R["q3"], indent=0)[:1500]); print("q4", R["q4"]); print("q5", R["q5"]); print("towns", R["towns"]); print(R["top_rate"]); print(R["bottom_rate"]); print(R["coverage"]); print(R["lbs_pop"])
