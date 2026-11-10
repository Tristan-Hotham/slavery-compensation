"""Shared paths, constants and helpers for the slavery-compensation study ("Where slavery money came home").

Inputs (read in place, never modified or copied into the repository):
  LBS_ADDR   /home/claude/newdata/raw_new14/slavery/lbs_addresses.csv   Legacies of British Slavery database (UCL Centre for the Study
             of the Legacies of British Slavery), geocoded addresses with linked people (retrieved 2026). Personal names in this file
             are never written to any output.
  LBS_POP    /home/claude/newdata/raw_new14/slavery/lbs_populations.json  the LBS map's county table (located and all addresses).
  PARISH     /home/claude/src6/captain-swing/data/parishes.csv   1851 parishes of England and Wales with county, centroid and 1801
             density, from Caprettini and Voth (2020), openICPSR E117044 (CC BY 4.0).
  LISTED     /home/claude/newdata/raw2/listed-buildings/data/listed_{england_part1,england_part2,wales,scotland}.csv.gz
             (Hotham 2026, The Listed Kingdom, doi:10.5281/zenodo.23761429; Historic England, HES, Cadw; OGL v3).
  GEO        /home/claude/newdata/raw/geo/ (Natural Earth 10m land for the coast clip).
  SETT       /home/claude/newdata/raw_new8/uk_settlements.tsv (Wikidata, CC0): county towns of Scotland for map points.
1831 county populations are hard-coded in pop1831.py (Census of Great Britain 1851, Population Tables I).
Scratch goes to SCR, outside the repository, and is deleted at the end.
"""
import json, gzip, os, re, math, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("SC_RAW", "/home/claude/newdata/raw_new14/slavery")
LBS_ADDR = f"{RAW}/lbs_addresses.csv"
LBS_POP = f"{RAW}/lbs_populations.json"
PARISH = os.environ.get("SC_PARISH", "/home/claude/src6/captain-swing/data/parishes.csv")
LISTED = os.environ.get("SC_LISTED", "/home/claude/newdata/raw2/listed-buildings/data")
GEO = os.environ.get("SC_GEO", "/home/claude/newdata/raw/geo")
SETT = os.environ.get("SC_SETT", "/home/claude/newdata/raw_new8/uk_settlements.tsv")
FONTS = os.environ.get("SC_FONTS", "/home/claude/ref/fonts")
SCR = os.environ.get("SC_SCRATCH", "/home/claude/scratch/slavery-compensation")
DATA = os.path.join(ROOT, "data")
IMG = os.path.join(ROOT, "img")
REL = os.path.join(ROOT, "release")
for d in (DATA, IMG, SCR):
    os.makedirs(d, exist_ok=True)

SLUG = "slavery-compensation"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
LBS_URL = "https://www.ucl.ac.uk/lbs/"
LBS_PERSON_URL = "https://www.ucl.ac.uk/lbs/person/view/{}"  # LBS address pages need an address id the map file does not carry
LBS_CAVEAT = "This map is a search tool and a general guide. More work is needed to produce data for statistical analysis."
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
BYLINE = "Dr Tristan Hotham · Independent researcher · 2026"
GB = ["England", "Wales", "Scotland"]
# the four great West India ports of the 1830s (city centres) for H2
PORTS = {"London": (-0.0877, 51.5101), "Bristol": (-2.5970, 51.4510), "Liverpool": (-2.9916, 53.4084), "Glasgow": (-4.2518, 55.8642)}
PORT_COUNTIES = ["Middlesex", "Gloucestershire", "Lancashire", "Lanarkshire", "Renfrewshire"]
BAD = ("—", "–", "--", "D" "SIT", "D" "CMS", "civil" " serv", "pre-" "registered")


def unesc(s):
    return html.unescape(s) if isinstance(s, str) else s


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return None
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, allow_nan=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for p in path.split("."):
        v = v[int(p)] if isinstance(v, list) else v[p]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f0": return f"{float(v):.0f}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "f3": return f"{float(v):.3f}"
    if f == "words":
        w = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
        n = int(round(float(v))); return w[n] if 0 <= n < len(w) else f"{n:,}"
    raise ValueError(f)


def fill(t, R, keep=("DOI", "DOI_URL", "BLOG_URL")):
    """{{path|fmt}} placeholders from results; IMG tokens and the publisher's placeholders are left alone"""
    return re.sub(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in keep else fmt(get(R, m.group(1)), m.group(3)), t)


def gc_km(lat1, lon1, lat2, lon2):
    import numpy as np
    p1, p2, l1, l2 = map(np.radians, (lat1, lat2, lon1, lon2))
    return 6371.0 * 2 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin((l2 - l1) / 2) ** 2))
