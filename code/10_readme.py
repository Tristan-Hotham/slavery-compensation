"""Step 10: README.md from code/readme_template.md and data/results.json."""
from common import *
R = jload(f"{DATA}/results.json")
t = open(f"{ROOT}/code/readme_template.md", encoding="utf-8").read().replace("{{CAVEAT}}", LBS_CAVEAT).replace("{{AI}}", AI)
t = fill(t, R)
assert set(re.findall(r"\{\{([^}]+)\}\}", t)) <= {"DOI_URL", "BLOG_URL", "DOI"}
for bad in BAD:
    assert bad not in t.replace("|---|---|", ""), bad
open(f"{ROOT}/README.md", "w", encoding="utf-8").write(t)
print("README ok")
