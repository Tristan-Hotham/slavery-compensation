"""Step 8: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24113858, https://doi.org/10.5281/zenodo.24113858 and https://blog.tristanhotham.com/2026/10/31/slavery-compensation/ are left for the publisher to fill."""
import json as _json, shutil, zipfile
from PIL import Image
from common import *

R = jload(f"{DATA}/results.json")
NAME = "Hotham_Slavery_Compensation_Addresses"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}
post = fill(open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read(), R, KEEP)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in BAD:
    assert bad not in vis, bad
assert AI in post and LBS_CAVEAT in post
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
q = R["q1"]
meta = {"title": "Where slavery money came home",
        "slug": "slavery-compensation",
        "excerpt": f"When Britain ended colonial slavery it paid £20 million to the slave-owners and nothing to the people they had enslaved. I mapped {q['gb']:,} British addresses of the owners and claimants: {q['london_pc']:.0f}% of them in London.",
        "seo_description": f"Mapping {q['gb']:,} British addresses of slave-owners compensated at abolition in the 1830s: {q['london_pc']:.0f}% in London, by county per head.",
        "tags": ["maps", "data visualisation", "history", "slavery", "abolition", "Legacies of British Slavery", "country houses", "historical geography"],
        "header_alt": f"Title card on cream paper reading 'Where slavery money came home' beside a map of Great Britain with counties shaded brown, darkest around London, and the figure {q['london_pc']:.0f}% in London."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
_json.dump(meta, open(f"{REL}/blog/meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith((".pyc", ".png")) or fn == "__pycache__":
            continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in sorted(os.listdir(DATA)):
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "NOTES.md"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(REL, "paper", "cover_note.md"), f"{SLUG}/release/paper/cover_note.md")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("$", "").replace("``", "\"").replace("''", "\"").replace("\\pounds ", "£")
zmeta = {"title": "Where Slavery Money Came Home: The British Addresses of Slave-Owners and Compensation Claimants at Abolition, Mapped from the Legacies of British Slavery Database",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/slavery-compensation/}}.</p>"
                        "<p>Sources: Legacies of British Slavery database, Centre for the Study of the Legacies of British Slavery, UCL (map address data, retrieved 2026; only counts and unnamed points are redistributed, no personal names); "
                        "Census of Great Britain 1851, Population Tables I (1831 county totals); national lists of listed buildings (Historic England, Historic Environment Scotland, Cadw; Open Government Licence v3.0) via The Listed Kingdom (doi:10.5281/zenodo.23761429); "
                        "1851 parishes from Caprettini and Voth (2020) replication data (openICPSR E117044, CC BY 4.0); ONS boundaries (OGL v3.0). Text, figures and derived data CC BY 4.0; code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["slavery compensation", "slave-ownership", "abolition", "Legacies of British Slavery", "historical geography", "country houses", "listed buildings", "Great Britain"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "10.5281/zenodo.23761429", "relation": "isDerivedFrom", "resource_type": "publication"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
for bad in ("\u2014", "\u2013", "--", "D" "SIT", "D" "CMS"):
    assert bad not in sj, bad
_json.dump(zmeta, open(f"{Z}/metadata.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
