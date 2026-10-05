#!/usr/bin/env python3
import zipfile
z = zipfile.ZipFile("/home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip")
names = z.namelist()
print("count", len(names))
keys = ("FINAL", "adversarial", "selection", "focused.json", "full.json", "harness", "summary")
for n in names:
    if any(k in n for k in keys):
        print(n)
