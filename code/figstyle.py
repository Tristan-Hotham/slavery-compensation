"""House style for the static figures: light paper, Fraunces titles, Source Serif and IBM Plex Mono text. A sober palette for a
sensitive subject: ink, a warm umber sequence for rates, and four quiet colours for the address forms."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np
from common import *

_FD = os.path.join(SCR, "fonts")
os.makedirs(_FD, exist_ok=True)
if not os.path.exists(f"{_FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold"), (600, "Semi")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{_FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{_FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{_FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERI = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-It.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 11, "axes.edgecolor": "#636A72", "axes.labelcolor": "#1D2128",
                     "xtick.color": "#636A72", "ytick.color": "#636A72", "axes.unicode_minus": False, "pdf.fonttype": 42})
PAPER, FG, MUT, RULE = "#F7F0E1", "#231C16", "#6A5F52", "#E2D6BD"
SEA, LAND, EDGE = "#E7EDF0", "#ECE6DA", "#B9AE98"
HOT = "#9E2A2B"
# rate per 10,000 people in 1831
RBINS = [0, 0.5, 1, 2, 3, 5, 100]
RCOL = ["#F3EBDD", "#E6D2B5", "#D2AE83", "#B5835A", "#8C5634", "#5C2E1B"]
RLAB = ["under 0.5", "0.5 to 1", "1 to 2", "2 to 3", "3 to 5", "5 or more"]
FORMC = {"street address": "#24425E", "named house": "#B7712A", "settlement only": "#8A8F96", "institution": "#6E5596"}
FORML = {"street address": "Street address", "named house": "Named house", "settlement only": "Town or village only", "institution": "Institution"}
NATC = {"England": "#24425E", "Wales": "#3B7D5A", "Scotland": "#B7712A"}


def rate_col(r):
    i = int(np.clip(np.searchsorted(RBINS, r, side="right") - 1, 0, len(RCOL) - 1))
    return RCOL[i]


def style_axes(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=RULE, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_facecolor(PAPER)


def savefig(fig, stem, blog=None, img=None, pdf=True):
    """f_<stem>.pdf for the paper, release/blog/b_<blog>.png at 1800 px wide, img/<img>.jpg for the page"""
    os.makedirs(f"{REL}/paper", exist_ok=True); os.makedirs(f"{REL}/blog", exist_ok=True)
    if pdf:
        fig.savefig(f"{REL}/paper/f_{stem}.pdf", facecolor=fig.get_facecolor())
    w = fig.get_figwidth()
    if blog:
        fig.savefig(f"{REL}/blog/b_{blog}.png", dpi=1800 / w, facecolor=fig.get_facecolor())
    if img:
        tmp = f"{SCR}/_tmp.png"
        fig.savefig(tmp, dpi=1400 / w, facecolor=fig.get_facecolor())
        from PIL import Image
        Image.open(tmp).convert("RGB").save(f"{IMG}/{img}.jpg", quality=86, optimize=True)
        os.remove(tmp)
    plt.close(fig)
