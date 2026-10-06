#!/usr/bin/env bash
set -euo pipefail
EV=/home/mateo/mathlib4-handoff/.handoff/evidence
LOG=$EV/full-3-1791213939582217433.log
date -Is
echo ===TMUX===
tmux ls 2>&1 || true
echo ===PROCS===
ps -eo pid,etime,cmd | grep -E 'workflow.py|lake |lean ' | grep -v grep || echo none
echo ===LOG_SIZE===
wc -c "$LOG"
echo ===LOG_TAIL===
tail -c 4000 "$LOG" | tr '\r' '\n' | tail -60
echo ===GREP_FAIL===
grep -E 'Benchmark|error:|build failed|Killed|✔ \[92' "$LOG" | tail -40
echo ===WRAPPER_END===
tail -20 "$EV/full-official-detached.wrapper.log"
echo ===DMESG_OOM===
dmesg -T 2>/dev/null | grep -iE 'kill|oom|out of memory' | tail -10 || echo no_dmesg
echo ===FULLJSON===
cat "$EV/full.json"
