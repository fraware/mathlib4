#!/usr/bin/env bash
set +e
EV="$HOME/mathlib4-cursor/.cursor-handoff/evidence"
echo "time=$(date -Iseconds)"
echo "status=$(cat "$EV/detached-gates.status")"
echo "full4_bytes=$(wc -c < "$EV/full-4-1791045690805037085.log")"
echo "full4_mtime=$(stat -c %y "$EV/full-4-1791045690805037085.log")"
echo "---cpu---"
ps -p 1379,1237,1003,682 -o pid,pcpu,pmem,etime,state,cmd 2>&1
echo "---runLinter_threads---"
ps -L -p 1379 -o pid,tid,pcpu,state,comm 2>&1 | head -40
echo "---open_lean_files---"
ls -la /proc/1379/fd 2>/dev/null | wc -l
ls -l /proc/1379/fd 2>/dev/null | grep -E '\.lean|Mathlib|olean' | head -20
echo "---probe_logs---"
for f in probe_custom_numeral.log probe_le.log probe_le2.log probe_obj3.log; do
  echo "FILE $f"
  tail -20 "$EV/$f" 2>&1
  echo
done
