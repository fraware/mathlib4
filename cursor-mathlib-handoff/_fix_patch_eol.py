#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
cd "$HOME/mathlib4-cursor"
patch=".cursor-handoff/patches/preferred.patch"
echo "file eol check:"
python3 - <<'PY'
from pathlib import Path
p = Path(".cursor-handoff/patches/preferred.patch")
data = p.read_bytes()
print("size", len(data))
print("crlf_count", data.count(b"\r\n"))
print("lf_only_approx", data.count(b"\n") - data.count(b"\r\n"))
print("has_cr", b"\r" in data)
# Rewrite LF-only copy and try apply --check
lf = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
Path("/tmp/preferred.lf.patch").write_bytes(lf)
print("wrote /tmp/preferred.lf.patch", len(lf))
PY
git apply --check /tmp/preferred.lf.patch && echo APPLY_CHECK_OK
# Also convert handoff patches in place to LF for future applies
python3 - <<'PY'
from pathlib import Path
root = Path(".cursor-handoff/patches")
for p in root.glob("*.patch"):
    data = p.read_bytes()
    lf = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if lf != data:
        p.write_bytes(lf)
        print("normalized", p)
    else:
        print("already lf", p)
# templates too
for p in Path(".cursor-handoff/templates").glob("*.lean"):
    data = p.read_bytes()
    lf = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if lf != data:
        p.write_bytes(lf)
        print("normalized", p)
PY
'''

path = Path("/tmp/fix_patch_eol.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
