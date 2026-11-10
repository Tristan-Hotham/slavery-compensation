# Where slavery money came home

The British addresses of people recorded as slave-owners and compensation claimants when Britain abolished colonial slavery in the 1830s, from the Legacies of British Slavery (LBS) database at UCL, set against the 1831 census. Parliament paid £20 million in compensation to the slave-owners. The people they had enslaved received nothing.

**Interactive version:** https://maps.tristanhotham.com/slavery-compensation/
**Paper:** https://doi.org/10.5281/zenodo.24113858
**Blog post:** https://blog.tristanhotham.com/2026/10/31/slavery-compensation/

This repository holds the interactive page, the derived data and the analysis code for the data study *Where slavery money came home: the British addresses of slave-owners compensated in the 1830s* by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Read this first

The LBS team say of their map: "This map is a search tool and a general guide. More work is needed to produce data for statistical analysis." This study describes the located (geocoded) addresses only: 3,115 of the 5,138 addresses in the LBS county table (61%). An address is where a person lived at some point, not necessarily in 1834, and the file holds no compensation amounts. No personal names are used or republished.

## Headline results

- 3,187 located addresses in Great Britain, linked 5,331 times to 4,004 people. London has 1,158 (36.3%). Middlesex has 33.4% of the addresses and had 8.4% of the 1831 population; county Gini 0.51 (95% CI 0.50 to 0.53).
- After London: Edinburgh 121, Bristol 106, Liverpool 100, Bath 66, Glasgow 32, Brighton 26, Cheltenham 18.
- Per 10,000 people in 1831: Great Britain 1.96; England 2.04, Scotland 2.06, Wales 0.51. Highest (counties of 10,000+): Middlesex 7.83, Midlothian 5.65, Moray 5.51.
- Pre-specified test: each doubling of distance to the nearest of London, Bristol, Liverpool and Glasgow goes with a 37% lower rate (95% CI 25 to 46%; Poisson, 84 counties). The port-county term is not supported (0.83, CI 0.44 to 1.57). The gradient is carried by street addresses and depends on London and the South-East (not robust to leaving out the South-East region: 0.78, CI 0.58 to 1.03); named houses (0.94) and a placebo of listed great houses (0.98) show none. Distance to London alone fits better (exploratory).
- Address forms: London 89% street addresses; outside London 32% street addresses, 28% named houses, 39% town or village only.
- Of 553 country-house candidates, 267 (48.3%) match a listed building today; corrected by a hand check of 100 cases, about 44% (interval 38 to 49%); 62 matched houses are Grade I or Category A.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js`, `img/` | The interactive page (MapLibre, OpenFreeMap Positron base map; layers panel, search, full-screen button). |
| `header.png` | Social card, 1200 x 630. |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `data/counties.csv` | The 84 historic counties of Great Britain: 1831 and 1841 population, located addresses, linked people, all LBS addresses, coverage, rates, centre and distance to the nearest port, listed great houses, country-house candidates. |
| `data/towns.csv` | Located addresses by town. |
| `data/forms.csv`, `data/models.csv`, `data/county_listed.csv` | Address forms by area; every model; country houses against listed great houses by county. |
| `data/listed_handcheck.csv` | The 100 hand-checked listed-building matches and non-matches (house names and list entries only). |
| `data/county_check.csv` | England and Wales addresses whose LBS county differs from the nearest 1851 parish's county. |
| `data/points.json` | Located addresses for the map: LBS map address id, point, address type, number of linked people, geocode precision, town, county, country and the LBS person id of one linked record (for the link to UCL). No names or street text. |
| `data/counties_ew.geojson`, `data/site.json` | Approximate England and Wales county outlines (rebuilt from 1851 parishes); Scottish county circles and the search list. |
| `code/` | Numbered scripts (below), rules, templates, QA. |
| `release/` | Paper (PDF, LaTeX, cover note), blog post, figures and meta, Zenodo files. |
| `reddit/` | Collage, its script, the post text and a GIF. |

## Method in brief

Addresses: the LBS map address file; county names mapped by hand to the historic counties of 1831 (97% agree with the nearest 1851 parish in England and Wales). Population: 1831 county totals from the 1851 census Population Tables, checked against the printed national totals. Address forms from the address text. Model: Poisson regression of county counts with offset log population and HC1 errors, with planned checks (negative binomial, people, all addresses, without Middlesex, by nation, 1841 population, address forms, leave one region out, placebo). Listed buildings: name and place match to the national lists, with a frozen rule and a hand check. The plan is in `NOTES.md`, written before the analysis.

## Rerun

Python 3 with pandas, numpy, geopandas, shapely, scipy, statsmodels, rapidfuzz, matplotlib, Pillow; xelatex. Raw paths are in `code/common.py` (the LBS file is not redistributed). Run in order: `01_prepare.py`, `02_listed.py`, `03_analysis.py`, `04_geo.py`, `05_figures.py`, `06_site.py`, `07_paper.py` (set `DOI` to fill the DOI), `09_header.py`, `reddit/collage.py`, `08_release.py`, `10_readme.py`. QA: `node code/qa.js`.

## Sources and licences

- Legacies of British Slavery database, Centre for the Study of the Legacies of British Slavery, UCL Department of History, https://www.ucl.ac.uk/lbs/ (map address data, retrieved 2026). © LBS, UCL. Only counts and unnamed points with LBS ids are reproduced.
- Census of Great Britain, 1851, Population Tables I, Vol. I, Tables XXX and X (county totals 1801 to 1851), transcribed by Ditto Books (dittobooks.co.uk).
- Listed buildings: Historic England, Historic Environment Scotland, Cadw (Open Government Licence v3.0), via The Listed Kingdom (Hotham 2026, doi:10.5281/zenodo.23761429).
- 1851 parishes: Caprettini, B. and Voth, H.-J. (2020) replication data, openICPSR E117044 (CC BY 4.0). Coast: ONS local authority boundaries, December 2023 (OGL v3.0). Scottish county towns: Wikidata (CC0).
- Base map: OpenFreeMap Positron, OpenStreetMap contributors (ODbL). MapLibre GL JS (BSD 3-Clause).

Text, figures and derived data: CC BY 4.0. Code: MIT. See `LICENSE`.

## Citation

Hotham, T. (2026) Where slavery money came home: the British addresses of slave-owners compensated in the 1830s. Zenodo. https://doi.org/10.5281/zenodo.24113858

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
