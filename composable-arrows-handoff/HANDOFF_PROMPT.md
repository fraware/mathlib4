Read AGENTS.md and all three handoff documents under .handoff before taking
action. Two validation campaigns are already complete:

1. Historical pin `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3` — see FINAL_REPORT.md
   and validation-evidence.zip (fingerprint `cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0`).
2. Upstream-candidate base `08c3fc3f372a6d35d18190fb26b7be083378dc38` — see
   ../upstream-candidate-evidence/ (identity
   `13281f16b7e423e506d55f180d1ce5448312dd0c47a34900d9fa4a6a5ef07a57`;
   production.patch sha256 `20c0abcda3f9f62ff463b4bb5ff8060bfdf15b7ddfffc351974a6811b4c54026`;
   ZIP sha256 `ce377c085915676c9be3cdf1e1d8b9ac515f437e5b66d2a5c4c49bf93bb6b45c`).

Do not re-run the full Lean suite unless Mateo explicitly requests it. Keep the
preferred reducer design and frozen Basic / ReduceMap / IntegratedProbe hashes
unchanged. Keep the original 13 integrated examples unchanged.

If Mateo asks for a fresh historical-pin run, use `.handoff/workflow.py` serially
(baseline → apply preferred → focused → downstream → full → export). Diagnose
and repair only actual errors; never weaken assertions to force a pass. Use the
fallback only if a diagnosed preferred-design failure justifies it.

When reporting, give ZIP checksums, exact source / validation identity hashes,
gate results, and any unresolved limitations. If execution is blocked, return the
actual error and partial evidence without claiming success.

Do not push or perform any remote repository mutation without Mateo's explicit
approval for that specific action. Preserve local push guards when present.
Do not open PRs, post comments, or run remote workflows unless authorized.
Work locally until given explicit approval for a specific remote action.
