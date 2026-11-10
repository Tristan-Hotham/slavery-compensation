"""Step 4: approximate historic county outlines for England and Wales, for the map only (never used to count addresses).
Voronoi cells of the 10,699 parish centroids of 1851 (Caprettini and Voth 2020), dissolved by their county and clipped to the
coast of England and Wales (ONS local authority boundaries, December 2023, generalised; OGL v3). Writes
data/counties_ew.geojson (simplified, with the county figures from data/counties.csv) and SCR/outlines.gpkg (nation outlines
for the static figures)."""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import MultiPoint, box
from shapely.ops import voronoi_diagram, unary_union
from common import *

C = pd.read_csv(f"{DATA}/counties.csv")
P = pd.read_csv(PARISH, usecols=["GAZ_CNTY", "lat", "lon"])
pcounty = {"YORKSHIRE, WEST RIDING": "Yorkshire", "YORKSHIRE, NORTH RIDING": "Yorkshire", "YORKSHIRE, EAST RIDING": "Yorkshire",
           "ISLE OF WIGHT": "Hampshire", "CARNARVONSHIRE": "Caernarfonshire", "GLAMORGANSHIRE": "Glamorgan"}
P["county"] = P.GAZ_CNTY.map(lambda s: pcounty.get(s, s.title()))
pts = gpd.GeoDataFrame(P, geometry=gpd.points_from_xy(P.lon, P.lat), crs=4326).to_crs(27700)
pts = pts.drop_duplicates(subset=["lon", "lat"])
L = gpd.read_file(f"{GEO}/lad23_bgc.geojson").to_crs(27700)
code = [c for c in L.columns if c.upper().startswith("LAD") and c.upper().endswith("CD")][0]
ew = unary_union(L[L[code].str[0].isin(["E", "W"])].geometry.buffer(0))
sc = unary_union(L[L[code].str[0] == "S"].geometry.buffer(0))
env = box(*ew.bounds).buffer(50000)
vor = voronoi_diagram(MultiPoint(list(pts.geometry)), envelope=env)
cells = gpd.GeoDataFrame(geometry=list(vor.geoms), crs=27700)
cells = gpd.sjoin(cells, pts[["county", "geometry"]], predicate="contains", how="inner")
cty = cells.dissolve(by="county").reset_index()[["county", "geometry"]]
cty["geometry"] = cty.geometry.intersection(ew).buffer(0)
cty["geometry"] = cty.geometry.simplify(400, preserve_topology=True)
keep = ["county", "nation", "pop1831", "addresses", "people", "rate10k", "people10k", "lbs_all", "lbs_located", "coverage_pc", "great", "cand"]
cty = cty.merge(C[keep], on="county", how="left")
assert cty.pop1831.notna().all(), cty[cty.pop1831.isna()].county.tolist()
out = cty.to_crs(4326)
out["geometry"] = out.geometry.map(lambda g: g)
out.to_file(f"{DATA}/counties_ew.geojson", driver="GeoJSON", COORDINATE_PRECISION=4)
gpd.GeoDataFrame({"nation": ["England and Wales", "Scotland"]}, geometry=[ew.simplify(150), sc.simplify(150)], crs=27700).to_file(f"{SCR}/outlines.gpkg", driver="GPKG")
cty.to_file(f"{SCR}/counties_ew_bng.gpkg", driver="GPKG")
print(len(out), "counties;", os.path.getsize(f"{DATA}/counties_ew.geojson") // 1024, "KB")
