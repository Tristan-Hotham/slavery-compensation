"""Reddit collage (r/dataisbeautiful style), light background, 2700 x 2025 px: the map of addresses and county rates, the top
towns, shares of addresses against population, and town houses against country seats. Run after code/05_figures.py:
python3 reddit/collage.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import numpy as np, pandas as pd, geopandas as gpd
from pyproj import Transformer
from figstyle import *

R = jload(f"{DATA}/results.json"); q = R["q1"]
C = pd.read_csv(f"{DATA}/counties.csv")
CE = gpd.read_file(f"{SCR}/counties_ew_bng.gpkg"); OUT = gpd.read_file(f"{SCR}/outlines.gpkg")
d = pd.read_parquet(f"{SCR}/addresses_full.parquet"); g = d[d.gb & d.has_xy]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
gx, gy = TR.transform(g.lon.values, g.lat.values)
HALO = [pe.withStroke(linewidth=4, foreground=SEA)]
HALOP = [pe.withStroke(linewidth=4, foreground=PAPER)]

fig = plt.figure(figsize=(13.5, 10.125), dpi=200, facecolor=PAPER)
fig.text(0.035, 0.962, "Where slavery money came home", fontproperties=DISP, fontsize=34, color=FG, va="top")
fig.text(0.035, 0.902, f"When Britain abolished colonial slavery in the 1830s it paid £20 million to the slave-owners. The people they had enslaved received nothing.\n"
         f"These are the {q['gb']:,} British addresses of owners and claimants located by the Legacies of British Slavery database (UCL).",
         fontproperties=SERP, fontsize=13.5, color=MUT, va="top", linespacing=1.3)

# map
ax = fig.add_axes([0.0, 0.075, 0.53, 0.76]); ax.set_facecolor(SEA)
OUT.plot(ax=ax, color=LAND, edgecolor="none")
CE.plot(ax=ax, color=[rate_col(r) for r in CE.rate10k], edgecolor="white", lw=0.5)
S = C[C.nation == "Scotland"]; sx, sy = TR.transform(S.cen_lon.values, S.cen_lat.values)
ax.scatter(sx, sy, s=14 + S.addresses * 1.0, c=[rate_col(r) for r in S.rate10k], edgecolor="#5C4A3A", lw=0.7, zorder=3)
ax.scatter(gx, gy, s=1.4, c=FG, alpha=0.55, lw=0, zorder=4, rasterized=True)
ax.set_xlim(-250000, 700000); ax.set_ylim(0, 1000000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
ax.set_xlabel(""); ax.set_ylabel("")
for s in ax.spines.values():
    s.set_visible(False)
# labels on the sea, with straight leaders that cross nothing
lab = [("London", (530000, 181000), (600000, 40000), f"London\n{q['london']:,} addresses"),
       ("Bristol", (359000, 173000), (110000, 235000), f"Bristol {R['town']['Bristol']}"),
       ("Bath", (375000, 165000), (385000, 35000), f"Bath {R['town']['Bath']}"),
       ("Liverpool", (339000, 390000), (120000, 450000), f"Liverpool {R['town']['Liverpool']}"),
       ("Edinburgh", (325000, 673000), (470000, 760000), f"Edinburgh {R['town']['Edinburgh']}"),
       ("Glasgow", (259000, 665000), (20000, 690000), f"Glasgow {R['town']['Glasgow']}")]
for _, (x0, y0), (x1, y1), t in lab:
    ax.annotate(t, xy=(x0, y0), xytext=(x1, y1), fontsize=11, color=FG, ha="center", va="center", zorder=6, path_effects=HALO,
                fontproperties=SERP, arrowprops=dict(arrowstyle="-", color=FG, lw=0.7, shrinkA=3, shrinkB=0))
leg = [Patch(facecolor=c, edgecolor="#B9AE98", label=l) for c, l in zip(RCOL, RLAB)]
L1 = ax.legend(handles=leg + [Line2D([], [], ls="", marker="o", ms=3, color=FG, label="one address"),
                              Line2D([], [], ls="", marker="o", ms=9, mfc=RCOL[3], mec="#5C4A3A", label="Scottish county")],
               title="Addresses per 10,000\npeople in 1831", loc="lower left", bbox_to_anchor=(0.0, 0.0), frameon=True, fontsize=9.5, title_fontsize=10)
L1.get_frame().set_facecolor(SEA); L1.get_frame().set_edgecolor(SEA)

# towns
a1 = fig.add_axes([0.62, 0.555, 0.35, 0.235])
T = pd.DataFrame(R["towns"]).head(8)[::-1]
a1.barh(T.town, T.n, color=[HOT if t == "London" else "#8C5634" for t in T.town], height=0.7)
for i, r in enumerate(T.itertuples()):
    a1.text(r.n * 1.08, i, f"{r.n:,}", va="center", fontsize=10.5, color=FG)
a1.set_xscale("log"); a1.set_xlim(8, 4000); a1.set_xticks([])
for s in ("top", "right", "bottom"):
    a1.spines[s].set_visible(False)
for t in a1.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(12)
a1.set_facecolor(PAPER)
a1.set_title("London first, then the ports and the spa towns", fontproperties=DISPB, fontsize=15, color=FG, loc="left", pad=8)
a1.text(0.0, -0.08, "Addresses by town (log scale)", transform=a1.transAxes, fontsize=9.5, color=MUT)

# shares
a2 = fig.add_axes([0.62, 0.30, 0.35, 0.17])
groups = [("Middlesex", q["middlesex_pc"], q["middlesex_pop_pc"]), ("Rest of England", q["england_pc"] - q["middlesex_pc"], q["england_pop_pc"] - q["middlesex_pop_pc"]),
          ("Wales", q["wales_pc"], q["wales_pop_pc"]), ("Scotland", q["scotland_pc"], q["scotland_pop_pc"])]
yy = np.arange(4)[::-1]
a2.barh(yy + 0.2, [x[1] for x in groups], height=0.38, color=HOT, label="share of addresses")
a2.barh(yy - 0.2, [x[2] for x in groups], height=0.38, color="#C9B79A", label="share of people, 1831")
for y_, (l, a, b) in zip(yy, groups):
    a2.text(a + 1, y_ + 0.2, f"{a:.0f}%", va="center", fontsize=10, color=FG); a2.text(b + 1, y_ - 0.2, f"{b:.0f}%", va="center", fontsize=10, color=MUT)
a2.set_yticks(yy); a2.set_yticklabels([x[0] for x in groups], fontproperties=SERP, fontsize=12); a2.set_xlim(0, 95); a2.set_xticks([])
for s in ("top", "right", "bottom"):
    a2.spines[s].set_visible(False)
a2.set_facecolor(PAPER)
a2.legend(frameon=False, fontsize=9.5, loc="lower right")
a2.set_title("A third of the addresses, a twelfth of the people", fontproperties=DISPB, fontsize=15, color=FG, loc="left", pad=8)

# forms
a3 = fig.add_axes([0.62, 0.12, 0.35, 0.11])
order = ["London", "England outside London", "Scotland"]
left = np.zeros(3)
for f in ("street address", "named house", "settlement only", "institution"):
    v = np.array([R["q3"][o][f] for o in order])
    a3.barh(["London", "Rest of England", "Scotland"][::-1], v[::-1], left=left[::-1], color=FORMC[f], height=0.62, label=FORML[f])
    for i, (vv, ll) in enumerate(zip(v[::-1], left[::-1])):
        if vv >= 9:
            a3.text(ll + vv / 2, i, f"{vv:.0f}%", ha="center", va="center", color="white", fontsize=9.5)
    left += v
a3.set_xlim(0, 100); a3.set_xticks([])
for s in ("top", "right", "bottom"):
    a3.spines[s].set_visible(False)
for t in a3.get_yticklabels():
    t.set_fontproperties(SERP); t.set_fontsize(12)
a3.set_facecolor(PAPER)
a3.legend(frameon=False, ncol=4, fontsize=9, loc="upper left", bbox_to_anchor=(-0.32, -0.08))
a3.set_title("Town houses in London, country seats elsewhere", fontproperties=DISPB, fontsize=15, color=FG, loc="left", pad=8)

fig.text(0.035, 0.022, "Source: Legacies of British Slavery database, UCL (map addresses, retrieved 2026; only located addresses, no names); 1831 census. "
         "\nCounties: England and Wales rebuilt from 1851 parishes (Caprettini and Voth 2020); Scotland as circles.  "
         "Dr Tristan Hotham  ·  maps.tristanhotham.com/slavery-compensation", fontsize=9, color=MUT, va="bottom", linespacing=1.4)
fig.savefig(os.path.join(HERE, "slavery_compensation_collage.png"), dpi=200, facecolor=PAPER)
print("collage saved")
