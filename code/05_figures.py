"""Step 5: figures for the paper (release/paper/f_*.pdf), the blog (release/blog/b_*.png, 1800 px) and the page (img/*.jpg).
Every number drawn comes from data/results.json or the derived CSVs."""
import numpy as np, pandas as pd, geopandas as gpd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pyproj import Transformer
from figstyle import *

R = jload(f"{DATA}/results.json")
C = pd.read_csv(f"{DATA}/counties.csv")
d = pd.read_parquet(f"{SCR}/addresses_full.parquet")
g = d[d.gb & d.has_xy].copy()
TR = Transformer.from_crs(4326, 27700, always_xy=True)
g["x"], g["y"] = TR.transform(g.lon.values, g.lat.values)
CE = gpd.read_file(f"{SCR}/counties_ew_bng.gpkg")
OUT = gpd.read_file(f"{SCR}/outlines.gpkg")
SRC = "Data: Legacies of British Slavery database, UCL (retrieved 2026); 1831 census"
FOOT = f"maps.tristanhotham.com/{SLUG}"


def frame(fig, title, sub, src=SRC, top=0.955):
    fig.text(0.04, top, title, fontproperties=DISP, fontsize=22, color=FG, va="top")
    fig.text(0.04, top - 0.56 / fig.get_figheight(), sub, fontproperties=SERP, fontsize=12.5, color=MUT, va="top")
    fig.text(0.04, 0.022, f"{src}\n{FOOT}", fontsize=8.2, color=MUT, va="bottom")


# ---------------- map ----------------
def gb_map(ax, dots=True, legend=True):
    ax.set_facecolor(SEA)
    OUT.plot(ax=ax, color=LAND, edgecolor="none", zorder=1)
    CE.plot(ax=ax, color=[rate_col(r) for r in CE.rate10k], edgecolor="#FFFFFF", lw=0.5, zorder=2)
    S = C[C.nation == "Scotland"].copy()
    S["x"], S["y"] = TR.transform(S.cen_lon.values, S.cen_lat.values)
    ax.scatter(S.x, S.y, s=30 + S.addresses * 1.4, c=[rate_col(r) for r in S.rate10k], edgecolor="#5C4A3A", lw=0.8, zorder=3)
    if dots:
        ax.scatter(g.x, g.y, s=1.6, c=FG, alpha=0.55, lw=0, zorder=4, rasterized=True)
    ax.set_xlim(-10000, 680000); ax.set_ylim(0, 1000000)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
    for s in ax.spines.values():
        s.set_visible(False)


fig = plt.figure(figsize=(10, 11.6), facecolor=PAPER)
frame(fig, "Where Britain's slave-owners lived", "Addresses in Great Britain linked to slave-owners in the LBS database (dots), and addresses per 10,000\npeople in 1831 by historic county. England and Wales shaded; Scotland's counties drawn as circles.", top=0.965)
ax = fig.add_axes([0.02, 0.05, 0.62, 0.84]); gb_map(ax)
# London inset
ax2 = fig.add_axes([0.60, 0.43, 0.37, 0.30]); ax2.set_facecolor(LAND)
lon_ = g[g.london]
ax2.scatter(lon_.x, lon_.y, s=4, c=FG, alpha=0.5, lw=0, rasterized=True)
ax2.set_xlim(518000, 541000); ax2.set_ylim(170000, 190000); ax2.set_aspect("equal"); ax2.set_xticks([]); ax2.set_yticks([])
for s in ax2.spines.values():
    s.set_color(MUT)
ax2.set_title(f"London: {R['q1']['london']:,} addresses ({R['q1']['london_pc']:.0f}%)", fontproperties=DISPB, fontsize=12, color=FG, loc="left")
ax2.text(0.02, 0.02, "about 23 by 20 km around the City and the West End", transform=ax2.transAxes, fontsize=8.5, color=MUT)
leg = [Patch(facecolor=c, edgecolor="#B9AE98", label=l) for c, l in zip(RCOL, RLAB)]
L1 = fig.legend(handles=leg, title="Addresses per 10,000\npeople (1831)", loc="upper left", bbox_to_anchor=(0.62, 0.36), frameon=False, fontsize=10, title_fontsize=10.5)
L1._legend_box.align = "left"
fig.legend(handles=[Line2D([], [], ls="", marker="o", ms=3, color=FG, label="one geocoded address"),
                    Line2D([], [], ls="", marker="o", ms=11, mfc=RCOL[3], mec="#5C4A3A", label="Scottish county\n(size: addresses)")],
           loc="upper left", bbox_to_anchor=(0.62, 0.16), frameon=False, fontsize=10)
savefig(fig, "map", blog="map", img="map")

# ---------------- towns ----------------
T = pd.DataFrame(R["towns"]).head(12)[::-1]
fig, ax = plt.subplots(figsize=(10, 6.6), facecolor=PAPER); fig.subplots_adjust(left=0.2, right=0.93, top=0.8, bottom=0.17)
frame(fig, "London first, then the Atlantic ports and the spas", f"Geocoded LBS addresses by town, Great Britain (top 12 of {R['n_towns']:,} places named).")
ax.barh(T.town, T.n, color=[HOT if t == "London" else "#8C5634" for t in T.town], height=0.7)
for i, r in enumerate(T.itertuples()):
    ax.text(r.n * 1.08, i, f"{r.n:,}", va="center", fontsize=10.5, color=FG)
ax.set_xscale("log"); ax.set_xlim(5, 3000)
from matplotlib.ticker import FuncFormatter, NullFormatter
PLAIN = FuncFormatter(lambda v, _: f"{v:g}")
ax.xaxis.set_major_formatter(PLAIN); ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xlabel("Addresses (log scale)", fontproperties=SERP, fontsize=12)
style_axes(ax, grid="x")
for t in ax.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(12.5)
savefig(fig, "towns", blog="towns", img="towns")

# ---------------- shares ----------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 5.6), facecolor=PAPER, gridspec_kw={"width_ratios": [1.15, 1]})
fig.subplots_adjust(left=0.15, right=0.97, top=0.78, bottom=0.2, wspace=0.35)
frame(fig, "A third of the addresses, a twelfth of the people", "Left: shares of Great Britain's geocoded LBS addresses and of its 1831 population. Right: Lorenz curve across counties.")
q = R["q1"]
groups = [("Middlesex", q["middlesex_pc"], q["middlesex_pop_pc"]),
          ("Rest of England", q["england_pc"] - q["middlesex_pc"], q["england_pop_pc"] - q["middlesex_pop_pc"]),
          ("Wales", q["wales_pc"], q["wales_pop_pc"]), ("Scotland", q["scotland_pc"], q["scotland_pop_pc"])]
yy = np.arange(len(groups))[::-1]
a1.barh(yy + 0.2, [x[1] for x in groups], height=0.38, color=HOT, label="LBS addresses")
a1.barh(yy - 0.2, [x[2] for x in groups], height=0.38, color="#C9B79A", label="People, 1831")
for y_, (lab, a, b) in zip(yy, groups):
    a1.text(a + 1, y_ + 0.2, f"{a:.0f}%", va="center", fontsize=10, color=FG)
    a1.text(b + 1, y_ - 0.2, f"{b:.0f}%", va="center", fontsize=10, color=MUT)
a1.set_yticks(yy); a1.set_yticklabels([x[0] for x in groups], fontproperties=SERP, fontsize=12)
a1.set_xlim(0, 85); a1.set_xlabel("Share of Great Britain (%)", fontproperties=SERP, fontsize=11.5)
a1.legend(frameon=False, fontsize=10, loc="lower right"); style_axes(a1, grid="x")
lz = R["lorenz"]
a2.plot([0, 1], [0, 1], color=MUT, ls="--", lw=1)
a2.plot(lz["pop"], lz["addr"], color=HOT, lw=2.4)
a2.fill_between(lz["pop"], lz["addr"], lz["pop"], color=HOT, alpha=0.08)
a2.text(0.05, 0.86, f"Gini {q['gini']:.2f}\n(95% CI {q['gini_lo']:.2f} to {q['gini_hi']:.2f})", fontsize=10.5, color=FG, transform=a2.transAxes)
a2.set_xlabel("Cumulative share of 1831 population", fontproperties=SERP, fontsize=11.5)
a2.set_ylabel("Cumulative share of addresses", fontproperties=SERP, fontsize=11.5)
a2.set_xlim(0, 1); a2.set_ylim(0, 1); style_axes(a2, grid="both")
savefig(fig, "shares", blog="shares", img="shares")

# ---------------- county rates ----------------
K = C[C.pop1831 >= 10000].sort_values("rate10k", ascending=False).head(24)[::-1]
fig, ax = plt.subplots(figsize=(10, 9), facecolor=PAPER); fig.subplots_adjust(left=0.3, right=0.95, top=0.86, bottom=0.13)
frame(fig, "Per head, Middlesex and Edinburgh lead", f"Geocoded LBS addresses per 10,000 people in 1831, the 24 highest of {R['county_n']} historic counties. Great Britain: {q['gb_rate10k']:.1f}.", top=0.965)
ax.barh(K.county.str.replace(" (Edinburgh)", " (Edinburgh)"), K.rate10k, color=[NATC[n] for n in K.nation], height=0.72)
for i, r in enumerate(K.itertuples()):
    ax.text(r.rate10k + 0.08, i, f"{r.rate10k:.1f}  ({r.addresses:,})", va="center", fontsize=9.5, color=FG)
ax.axvline(q["gb_rate10k"], color=MUT, ls="--", lw=1)
ax.set_xlim(0, 9.6); ax.set_xlabel("Addresses per 10,000 people in 1831 (count in brackets)", fontproperties=SERP, fontsize=11.5)
for t in ax.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(11)
ax.legend(handles=[Patch(color=c, label=n) for n, c in NATC.items()], frameon=False, loc="lower right", fontsize=10.5)
style_axes(ax, grid="x")
savefig(fig, "counties", blog="counties", img="counties")

# ---------------- distance ----------------
M = C[C.pop1831 > 0].copy()
fig, ax = plt.subplots(figsize=(10, 6.6), facecolor=PAPER); fig.subplots_adjust(left=0.1, right=0.96, top=0.8, bottom=0.18)
h = R["h2"]["main"]["log_port_km"]
frame(fig, "Further from the ports and London, fewer addresses", f"County rate per 10,000 people (1831) against distance to the nearest of London, Bristol, Liverpool and Glasgow.\nEach doubling of distance goes with a rate {100 * (1 - R['h2']['double']):.0f}% lower (95% CI {100 * (1 - R['h2']['double_hi']):.0f} to {100 * (1 - R['h2']['double_lo']):.0f}%).")
for n, c in NATC.items():
    x = M[M.nation == n]
    ax.scatter(x.port_km.clip(lower=5), x.rate10k.clip(lower=0.06), s=18 + np.sqrt(x.pop1831) / 9, color=c, alpha=0.8, edgecolor="white", lw=0.6, label=n)
for nm in ("Middlesex", "Midlothian (Edinburgh)", "Moray", "Gloucestershire", "Lancashire", "Lanarkshire", "Shropshire", "Somerset", "Sussex", "Yorkshire"):
    r = M[M.county == nm].iloc[0]
    off = {"Lancashire": (6, -12), "Lanarkshire": (-70, 6), "Somerset": (-58, 4), "Sussex": (6, -12)}.get(nm, (6, 4))
    ax.annotate(nm.replace(" (Edinburgh)", ""), (max(r.port_km, 5), r.rate10k), xytext=off, textcoords="offset points", fontsize=9, color=FG)
xs = np.exp(np.linspace(np.log(5), np.log(800), 50))
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 12)
ax.xaxis.set_major_formatter(PLAIN); ax.yaxis.set_major_formatter(PLAIN); ax.xaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_formatter(NullFormatter())
ax.text(0.99, 0.02, "Counties with no addresses drawn at 0.06", transform=ax.transAxes, ha="right", fontsize=8.5, color=MUT)
ax.set_xlabel("Distance from the county's centre to the nearest of the four ports (km, log scale)", fontproperties=SERP, fontsize=11.5)
ax.set_ylabel("Addresses per 10,000 (log)", fontproperties=SERP, fontsize=11.5)
ax.legend(frameon=False, fontsize=10.5, loc="lower left")
style_axes(ax, grid="both")
savefig(fig, "distance", blog="distance", img="distance")

# ---------------- forms ----------------
order = ["London", "England outside London", "Wales", "Scotland"]
forms = ["street address", "named house", "settlement only", "institution"]
fig, ax = plt.subplots(figsize=(10, 5.4), facecolor=PAPER); fig.subplots_adjust(left=0.24, right=0.96, top=0.74, bottom=0.25)
frame(fig, "Town houses in London, country seats elsewhere", "What the address record names, by area: a street address, a named house, or only a town or village.")
left = np.zeros(len(order))
for f in forms:
    v = np.array([R["q3"][o][f] for o in order])
    ax.barh(order[::-1], v[::-1], left=left[::-1], color=FORMC[f], label=FORML[f], height=0.62)
    for i, (vv, ll) in enumerate(zip(v[::-1], left[::-1])):
        if vv >= 7:
            ax.text(ll + vv / 2, i, f"{vv:.0f}%", ha="center", va="center", color="white", fontsize=10)
    left += v
for i, o in enumerate(order[::-1]):
    ax.text(101, i, f"n = {R['q3'][o]['n']:,}", va="center", fontsize=9.5, color=MUT)
ax.set_xlim(0, 112); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xlabel("Share of addresses (%)", fontproperties=SERP, fontsize=11.5)
for t in ax.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(12)
ax.legend(frameon=False, ncol=4, fontsize=10, loc="upper left", bbox_to_anchor=(-0.2, -0.16))
style_axes(ax, grid=None)
savefig(fig, "forms", blog="forms", img="forms")

# ---------------- listed ----------------
q4 = R["q4"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 5.6), facecolor=PAPER, gridspec_kw={"width_ratios": [1, 1.25]})
fig.subplots_adjust(left=0.09, right=0.97, top=0.76, bottom=0.2, wspace=0.42)
frame(fig, "Nearly half the country houses are listed today", f"{q4['cand']} named houses outside towns and London, matched by name and place to the national lists. Dashed line:\nall nations, corrected by a hand check of 100 cases ({q4['corrected_pc']:.0f}%).", src=SRC + "; listed buildings: Historic England, HES, Cadw (OGL)")
cats = [("England", q4["england"]), ("Scotland", q4["scotland"]), ("Wales", q4["wales"])]
a1.bar([c[0] for c in cats], [c[1]["pc"] for c in cats], color=[NATC[c[0]] for c in cats], width=0.6)
for i, (n, v) in enumerate(cats):
    a1.text(i, v["pc"] + 1.5, f"{v['pc']:.0f}%\n{v['matched']} of {v['n']}", ha="center", fontsize=10, color=FG)
a1.axhline(q4["corrected_pc"], color=MUT, ls="--", lw=1)
a1.set_ylim(0, 75); a1.set_ylabel("Matched to a listed building (%)", fontproperties=SERP, fontsize=11.5); style_axes(a1)
for t in a1.get_xticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(12)
gr = q4["grades"]
lab = [("Grade I / Category A", gr.get("I", 0) + gr.get("A", 0)), ("Grade II* / Category B", gr.get("II*", 0) + gr.get("B", 0)),
       ("Grade II / Category C", gr.get("II", 0) + gr.get("C", 0))]
a2.barh([l[0] for l in lab][::-1], [l[1] for l in lab][::-1], color=["#C9B79A", "#B5835A", "#5C2E1B"], height=0.6)
for i, (l, v) in enumerate(lab[::-1]):
    a2.text(v + 2, i, f"{v}", va="center", fontsize=10.5, color=FG)
a2.set_xlabel("Matched houses by grade", fontproperties=SERP, fontsize=11.5); a2.set_xlim(0, max(l[1] for l in lab) * 1.25)
for t in a2.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(11)
style_axes(a2, grid="x")
savefig(fig, "listed", blog="listed", img="listed")

# ---------------- robustness (paper and blog) ----------------
Mo = pd.read_csv(f"{DATA}/models.csv")
rows = Mo[Mo.group.isin(["main", "alt", "placebo", "exploratory"])].copy()
rows = rows[rows.log_port_km_irr.notna()]
fig, ax = plt.subplots(figsize=(10, 7.4), facecolor=PAPER); fig.subplots_adjust(left=0.44, right=0.95, top=0.84, bottom=0.16)
frame(fig, "The distance pattern under every check", "Rate ratio for each doubling of distance to the nearest port (95% CI). Below 1: fewer addresses further away.", top=0.965)
yy = np.arange(len(rows))[::-1]
ln2 = np.log(2)
for y_, r in zip(yy, rows.itertuples()):
    col = HOT if r.group == "main" else ("#3B7D5A" if r.group == "placebo" else ("#6E5596" if r.group == "exploratory" else FG))
    e, lo, hi = r.log_port_km_irr ** ln2, r.log_port_km_lo ** ln2, r.log_port_km_hi ** ln2
    ax.plot([lo, hi], [y_, y_], color=col, lw=2.2); ax.plot(e, y_, "o", color=col, ms=7)
    ax.text(max(hi, e) + 0.02, y_, f"{e:.2f}", va="center", fontsize=9.5, color=col)
ax.axvline(1, color=MUT, ls="--", lw=1)
ax.set_yticks(yy); ax.set_yticklabels(rows.label, fontproperties=SERP, fontsize=10.5)
ax.set_xlabel("Rate ratio per doubling of distance", fontproperties=SERP, fontsize=11.5); ax.set_xlim(0.3, 1.35)
style_axes(ax, grid="x")
savefig(fig, "robust", blog="robust", img=None)

# ---------------- dates (paper) ----------------
dd = R["q5"]["by_decade"]
ks = [k for k in sorted(dd, key=int) if int(k) >= 1720]
fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=PAPER); fig.subplots_adjust(left=0.09, right=0.97, top=0.76, bottom=0.19)
frame(fig, "When the addresses date from", f"Earliest year given for anyone linked to each address, by decade ({R['q5']['with_year']:,} of {R['q1']['gb']:,} addresses with a year).")
ax.bar([int(k) for k in ks], [dd[k] for k in ks], width=8, color=["#9E2A2B" if k == "1830" else "#B5835A" for k in ks])
ax.set_xlabel("Decade", fontproperties=SERP, fontsize=11.5); ax.set_ylabel("Addresses", fontproperties=SERP, fontsize=11.5)
style_axes(ax)
savefig(fig, "dates", blog=None, img=None)
print("figures done")
