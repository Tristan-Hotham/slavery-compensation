"""Step 7: the paper. Fills code/paper_template.tex from data/results.json, adds tables, compiles with xelatex.
Output: release/paper/Hotham_Slavery_Compensation_Addresses.pdf and .tex. https://doi.org/10.5281/zenodo.24113858 stays a placeholder unless the
environment variable DOI is set:  DOI=10.5281/zenodo.N python3 code/07_paper.py"""
import subprocess, numpy as np, pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
C = pd.read_csv(f"{DATA}/counties.csv")
Mo = pd.read_csv(f"{DATA}/models.csv")
OUT = os.path.join(REL, "paper"); NAME = "Hotham_Slavery_Compensation_Addresses"
assert R["q4"]["county"]["p"] < 0.001
def tex(s): return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
F = R["flow"]
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{Data flow.}\\label{tab:flow}\\begin{tabular}{lr}\\toprule Item & Number\\\\\\midrule\n"
      f"Rows in the LBS map address file & {F['rows']:,}\\\\\n\\quad without coordinates & {F['no_point']:,}\\\\\n"
      f"\\quad Great Britain & {F['gb']:,}\\\\\n\\qquad England & {F['england']:,}\\\\\n\\qquad Scotland & {F['scotland']:,}\\\\\n\\qquad Wales & {F['wales']:,}\\\\\n"
      f"\\quad Ireland & {F['ireland']:,}\\\\\n\\quad Channel Islands & {F['channel']:,}\\\\\n\\quad elsewhere & {F['overseas']:,}\\\\\\midrule\n"
      f"Person links, Great Britain & {F['links_gb']:,}\\\\\nDistinct people, Great Britain & {F['people_gb']:,}\\\\\n"
      f"LBS county table: all addresses & {F['lbs_table_addresses']:,}\\\\\n\\quad located & {F['lbs_table_located']:,}\\\\\\midrule\n"
      f"Country-house candidates & {R['q4']['cand']:,}\\\\\n\\quad matched to a listed building & {R['q4']['matched']:,}\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
K = C[C.pop1831 >= 10000].sort_values("rate10k", ascending=False)
rows = "".join(f"{tex(r.county)} & {r.nation} & {r.pop1831:,} & {r.addresses:,} & {r.rate10k:.2f} & {r.people:,} & {'' if r.coverage_pc != r.coverage_pc else f'{r.coverage_pc:.0f}'}\\\\\n" for r in K.head(15).itertuples())
TT = ("\\begin{table}[tbp]\\centering\\small\\caption{The 15 historic counties (of at least 10,000 people) with the most geocoded LBS addresses per 10,000 people in 1831. Coverage: located share of all addresses in the LBS county table.}\\label{tab:top}"
      "\\begin{tabular}{llrrrrr}\\toprule County & Nation & Population 1831 & Addresses & Per 10,000 & People & Coverage \\%\\\\\\midrule\n" + rows +
      f"\\midrule Great Britain & & {R['q1']['pop_gb']:,} & {R['q1']['gb']:,} & {R['q1']['gb_rate10k']:.2f} & {F['people_gb']:,} & {F['lbs_table_located_pc']:.0f}\\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
ln2 = np.log(2)
def cell(r, x):
    if r[f"{x}_irr"] != r[f"{x}_irr"]:
        return ""
    if x == "log_port_km":
        return f"{r[x + '_irr'] ** ln2:.2f} [{r[x + '_lo'] ** ln2:.2f}, {r[x + '_hi'] ** ln2:.2f}]"
    return f"{r[x + '_irr']:.2f} [{r[x + '_lo']:.2f}, {r[x + '_hi']:.2f}]"
sel = Mo[Mo.group.isin(["main", "alt", "placebo", "exploratory"])]
rows = "".join(f"{tex(r['label'])} & {cell(r, 'log_port_km')} & {cell(r, 'port')} & {int(r['n'])}\\\\\n" for _, r in sel.iterrows())
TM = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Poisson models of county address counts with offset log population (1831), HC1 standard errors. Distance: rate ratio per doubling of distance to the nearest of the four ports; port: rate ratio for a port county. All models include Wales and Scotland indicators where both vary. 95\\% CIs in brackets.}\\label{tab:models}"
      "\\begin{tabular}{p{7.2cm}llr}\\toprule Model & Distance (per doubling) & Port county & N\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
lo = Mo[Mo.group == "loro"]
rows = "".join(f"{tex(r['label'])} & {cell(r, 'log_port_km')} & {cell(r, 'port')} & {int(r['n'])}\\\\\n" for _, r in lo.iterrows())
TA = ("\\begin{table}[htbp]\\centering\\footnotesize\\caption{Leave one LBS region out (main model).}\\label{tab:loro}"
      "\\begin{tabular}{p{7.2cm}llr}\\toprule Region left out & Distance (per doubling) & Port county & N\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
Fm = pd.read_csv(f"{DATA}/forms.csv", index_col=0)
rows = ""
for g_ in ["London", "England outside London", "Wales", "Scotland"]:
    r = Fm.loc[g_]
    rows += f"{g_} & {int(r.total):,} & " + " & ".join(f"{r.get(f, 0) / r.total * 100:.1f}" for f in ("street address", "named house", "settlement only", "institution")) + "\\\\\n"
TFo = ("\\begin{table}[tbp]\\centering\\small\\caption{Address forms by area (percentages of addresses).}\\label{tab:forms}"
       "\\begin{tabular}{lrrrrr}\\toprule Area & N & Street & Named house & Settlement only & Institution\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
CL = pd.read_csv(f"{DATA}/county_listed.csv")
CL = CL[(CL.nation != "Scotland") & (CL.great >= 10)].sort_values("cand_per100great", ascending=False)
rows = "".join(f"{tex(r.county)} & {int(r.great)} & {int(r.cand)} & {int(r.cand_listed)} & {r.cand_per100great:.1f} & {r.rate10k:.2f}\\\\\n" for r in CL.head(10).itertuples())
TL = ("\\begin{table}[tbp]\\centering\\small\\caption{Country-house candidates per 100 listed great houses (Grade I and II*), England and Wales, the ten highest counties with at least 10 listed great houses.}\\label{tab:listedc}"
      "\\begin{tabular}{lrrrrr}\\toprule County & Great houses & Candidates & Matched & Per 100 & Addresses per 10,000\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(r.county)} & {r.nation[0]} & {r.pop1831:,} & {r.addresses:,} & {r.rate10k:.2f} & {r.people:,} & {r.lbs_all:,} & {r.port_km:.0f}\\\\\n" for r in C.sort_values(["nation", "county"]).itertuples())
TX = ("{\\footnotesize\\begin{longtable}{llrrrrrr}\\caption{All historic counties. E England, W Wales, S Scotland. All: all addresses in the LBS county table, located or not. Port km: distance from the county centre to the nearest of the four ports.}\\label{tab:appx}\\\\\\toprule County & & Pop. 1831 & Addresses & Per 10,000 & People & All & Port km\\\\\\midrule\\endfirsthead\\toprule County & & Pop. 1831 & Addresses & Per 10,000 & People & All & Port km\\\\\\midrule\\endhead\n"
      + rows + "\\bottomrule\\end{longtable}}\n" + TA)
t = open(f"{ROOT}/code/paper_template.tex", encoding="utf-8").read()
for k, v in {"TABLE_FLOW": TF, "TABLE_TOP": TT, "TABLE_MODELS": TM, "TABLE_FORMS": TFo, "TABLE_LISTED": TL, "TABLE_APPX": TX}.items():
    t = t.replace("{{" + k + "}}", v)
t = t.replace("{{AI}}", AI)
t = re.sub(r"\{\{([^{}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in ("DOI", "DOI_URL", "BLOG_URL") else fmt(get(R, m.group(1)), m.group(3)).replace("%", "\\%"), t)
doi = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24113858", f"https://doi.org/{doi}" if doi else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t
for bad in ("—", "–", "D" "SIT", "D" "CMS", "pre-" "registered"):
    assert bad not in t, bad
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/{NAME}.tex", "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", f"{NAME}.tex"], cwd=OUT, capture_output=True, text=True)
log = open(f"{OUT}/{NAME}.log", encoding="utf-8", errors="ignore").read()
print("undefined refs:", len(re.findall(r"undefined", log)), "| pages:", re.findall(r"Output written on .*?\((\d+) pages", log), "| errors:", log.count("\n! "))
for e in ("aux", "log", "out"):
    p = f"{OUT}/{NAME}.{e}"
    if os.path.exists(p): os.remove(p)
txt = subprocess.run(["pdftotext", f"{OUT}/{NAME}.pdf", "-"], capture_output=True, text=True).stdout
body = txt.split("\nReferences\n")[0]
print("words (whole pdf):", len(txt.split()), "| before references:", len(body.split()))
ab = re.search(r"Abstract(.*?)Keywords", txt, re.S)
print("abstract words:", len(ab.group(1).split()) if ab else None)
