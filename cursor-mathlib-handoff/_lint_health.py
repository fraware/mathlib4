#!/usr/bin/env python3
import subprocess
from pathlib import Path

script = r'''#!/usr/bin/env bash
set -u
cd "$HOME/mathlib4-cursor"
echo "=== process states ==="
ps -o pid,ppid,stat,etime,pcpu,pmem,rss,cmd -p 1237,$(pgrep -P 1237 | tr '\n' ',') 2>/dev/null
pgrep -af runLinter || true
echo "=== lint log ==="
ls -l .cursor-handoff/evidence/full-4-1791045690805037085.log
wc -c .cursor-handoff/evidence/full-4-1791045690805037085.log
tail -n 30 .cursor-handoff/evidence/full-4-1791045690805037085.log
echo "=== open files (runLinter) ==="
rid=$(pgrep -n runLinter || true)
if [ -n "$rid" ]; then
  ls -l /proc/$rid/fd 2>/dev/null | head -40
  echo "--- stack ---"
  # wchan / state
  cat /proc/$rid/status 2>/dev/null | grep -E 'State|VmRSS|Threads'
  cat /proc/$rid/wchan 2>/dev/null; echo
fi
echo "=== load ==="
uptime
'''

path = Path("/tmp/lint_health.sh")
path.write_text(script, encoding="utf-8", newline="\n")
path.chmod(0o755)
raise SystemExit(subprocess.call(["bash", str(path)]))
