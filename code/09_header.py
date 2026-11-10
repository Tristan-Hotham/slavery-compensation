"""Step 9: header.png, the 1200 x 630 social card."""
import numpy as np, pandas as pd, geopandas as gpd
from pyproj import Transformer
from figstyle import *

R = jload(f"{DATA}/results.json")
C = pd.read_csv(f"{DATA}/counties.csv")
CE = gpd.read_file(f"{SCR}/counties_ew_bng.gpkg"); OUT = gpd.read_file(f"{SCR}/outlines.gpkg")
d = pd.read_parquet(f"{SCR}/addresses_full.parquet"); g = d[d.gb & d.has_xy]
TR = Transformer.from_crs(4326, 27700, always_xy=True)
x, y = TR.transform(g.lon.values, g.lat.values)
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)
ax = fig.add_axes([0.6, 0.02, 0.38, 0.96]); ax.set_facecolor(PAPER)
OUT.plot(ax=ax, color=LAND, edgecolor="none")
CE.plot(ax=ax, color=[rate_col(r) for r in CE.rate10k], edgecolor="white", lw=0.4)
S = C[C.nation == "Scotland"]; sx, sy = TR.transform(S.cen_lon.values, S.cen_lat.values)
ax.scatter(sx, sy, s=12 + S.addresses * 0.8, c=[rate_col(r) for r in S.rate10k], edgecolor="#5C4A3A", lw=0.6, zorder=3)
ax.scatter(x, y, s=1.2, c=FG, alpha=0.5, lw=0, zorder=4)
ax.set_xlim(-10000, 680000); ax.set_ylim(0, 1000000); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.05, 0.86, "DATA STUDY · 2026", fontsize=13, color=HOT)
fig.text(0.05, 0.80, "Where slavery\nmoney came home", fontproperties=DISP, fontsize=50, color=FG, va="top", linespacing=1.0)
fig.text(0.05, 0.47, f"{R['q1']['gb']:,} British addresses of slave-owners\nand claimants at abolition, 1830s.\nThe owners were paid £20 million.\nThe enslaved received nothing.",
         fontproperties=SERP, fontsize=17, color=MUT, va="top", linespacing=1.15)
fig.text(0.05, 0.11, f"{R['q1']['london_pc']:.0f}%", fontproperties=DISP, fontsize=44, color=HOT, va="bottom")
fig.text(0.165, 0.125, "of them in London", fontproperties=SERP, fontsize=20, color=FG, va="bottom")
fig.text(0.05, 0.05, "Dr Tristan Hotham  ·  maps.tristanhotham.com/slavery-compensation", fontsize=11.5, color=MUT)
fig.savefig(f"{ROOT}/header.png", dpi=100, facecolor=PAPER)
from PIL import Image
im = Image.open(f"{ROOT}/header.png"); assert im.size == (1200, 630), im.size
im.convert("RGB").save(f"{ROOT}/header.png", optimize=True)
print("header ok")
