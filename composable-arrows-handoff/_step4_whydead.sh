#!/usr/bin/env bash
set -euo pipefail
echo "=== nohup out ==="
cat /home/mateo/mathlib4-handoff/.handoff/evidence/full-official-detached.nohup.out 2>/dev/null || echo none
echo "=== dmesg oom ==="
dmesg -T 2>/dev/null | tail -30 || true
echo "=== tmux/screen ==="
command -v tmux; command -v screen; command -v systemd-run
echo "=== wsl uptime ==="
uptime
echo "=== pid 778/805 ==="
ps -p 778,805,846 -o pid,cmd 2>/dev/null || true
ls -l /proc/778 2>/dev/null || echo 778 gone
echo "=== python any ==="
pgrep -af python || true
