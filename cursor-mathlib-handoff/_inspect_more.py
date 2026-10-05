#!/usr/bin/env python3
from pathlib import Path
import zipfile

repo = Path("/home/mateo/mathlib4-cursor")
ev = repo / ".cursor-handoff" / "evidence"

print("=== HARNESS ===")
print((repo / "MathlibTest/ComposableArrowsReduceMap.lean").read_text())

print("\n=== PRIOR NON-EMPTY full-3 KEY LINES ===")
log = ev / "full-3-1791084123470358418.log"
text = log.read_text(errors="replace")
for line in text.splitlines():
    if any(k in line for k in [
        "ComposableArrows", "error", "FAIL", "Benchmark",
        "Built MathlibTest", "error:", "wall",
    ]):
        print(line)
print("---LOG SIZE---", len(text))
print("---LAST 40---")
print("\n".join(text.splitlines()[-40:]))

print("\n=== ZIP SELECTED ENTRIES ===")
z = zipfile.ZipFile(repo / ".cursor-handoff" / "cursor-validation-evidence.zip")
print("ZIP entries", len(z.namelist()))
for n in z.namelist():
    if any(k in n for k in [
        "full-3-179108579", "supplemental", "FINAL", "SUMMARY",
        "full.json", "focused.json", "downstream.json",
    ]):
        print(n, z.getinfo(n).file_size)

print("\n=== LAKEFILE TEST TARGET SNIPPET ===")
lf = (repo / "lakefile.lean").read_text()
for i, line in enumerate(lf.splitlines(), 1):
    if "test" in line.lower() or "MathlibTest" in line:
        print(f"{i}:{line}")
