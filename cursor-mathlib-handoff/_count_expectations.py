#!/usr/bin/env python3
from pathlib import Path
text = Path("/home/mateo/mathlib4-cursor/MathlibTest/ComposableArrowsReduceMap.lean").read_text()
visits = text.count("check_reduce_map_visit")
declines = text.count("check_reduce_map_declines")
examples = text.count("\nexample ")
# baseline = equality proved by rfl only (no check tactic) inside sections
baselines = 0
for block in text.split("section"):
    if "example" in block and ":= by\n  rfl" in block.replace("\r\n", "\n"):
        baselines += block.replace("\r\n", "\n").count(":= by\n  rfl")
print("examples", examples)
print("visits", visits)
print("declines", declines)
print("rfl_baselines_rough", baselines)
print("visit+decline+baseline", visits + declines + baselines)

# Also verify adversarial preferred logs nonempty or at least exit recorded
import json
from pathlib import Path
ev = Path("/home/mateo/mathlib4-cursor/.cursor-handoff/evidence")
m = json.loads((ev / "advsuite_matrix.json").read_text())
print("\nadvsuite counts")
for tag in ("preferred", "original"):
    rows = [r for r in m["results"] if r["tag"] == tag]
    print(tag, "n=", len(rows), "exits=", [r["exit_code"] for r in rows])
    for r in rows:
        log = ev / r["log"]
        # flattened copies also exist
        flat = ev / f"advsuite_{r['tag']}_{r['probe']}.log"
        size = log.stat().st_size if log.exists() else None
        fsize = flat.stat().st_size if flat.exists() else None
        print(f"  {r['probe']}: exit={r['exit_code']} nested_size={size} flat_size={fsize}")
