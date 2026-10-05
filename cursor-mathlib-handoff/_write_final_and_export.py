#!/usr/bin/env python3
"""Write FINAL_REPORT from verified facts, export ZIP, mirror to Windows."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/home/mateo/mathlib4-cursor")
EV = REPO / ".cursor-handoff" / "evidence"
WIN = Path("/mnt/c/Users/mateo/mathlib4-1/cursor-mathlib-handoff")
OLD_ZIP = "66484dfc1f5f3c8d571b243c9817602a3296dda531994a4466fbfa47848ffd03"
FP_EXPECTED = "cb331cdbe71ce68329a6a2b7450a3acddc5b708a598ef6f72b2d2add68949cf0"


def load_wf():
    spec = importlib.util.spec_from_file_location("wf", REPO / ".cursor-handoff" / "workflow.py")
    wf = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(wf)
    return wf


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exits(rec: dict) -> list:
    return [c.get("exit_code") for c in rec.get("commands", [])]


def build_report(wf, fp: str, files: dict, gates: dict, full3: dict, full3_text: str,
                 supp_latest: str, supp_meta: dict, spot_name: str, adv_ts: str,
                 zip_sha: str | None, zip_bytes: int | None) -> str:
    full = gates["full"]
    zip_section = """
## Export hashes
Computed after `workflow.py export`; see also `EXPORT_HASHES.txt`.
"""
    if zip_sha is not None:
        zip_section = f"""
## Export hashes (verified from ZIP bytes)
- WSL ZIP: `/home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip`
- Windows ZIP: `C:/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip`
- ZIP sha256: `{zip_sha}`
- ZIP bytes: {zip_bytes}
- Supersedes older ZIP `{OLD_ZIP}` (that archive matched its own hash but contained
  empty official full-3 log `full-3-1791085799857013292.log`).
"""

    detail_rows = ""
    for c in full["commands"]:
        log = EV / c["log"]
        detail_rows += (
            f"| `{' '.join(c['argv'])}` | {c['exit_code']} | `{c['log']}` | "
            f"{log.stat().st_size if log.exists() else 'MISSING'} |\n"
        )

    return f"""# ComposableArrows handoff — FINAL REPORT

Generated from live verification on the WSL preferred checkout. Claims below are
tied to files under `.cursor-handoff/evidence/`. Nothing here authorizes remote writes.

## Selection
- Candidate: preferred
- Base HEAD: `a3cfff85f9dfe0b1c6b6e92899febc338687fcc3`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Final source fingerprint: `{fp}`
- Fallback used: no
- `sorry` / `admit` / new axioms in Basic + ReduceMap + IntegratedProbe: none found
- Linter disables (`set_option linter.*`) in those files: none found
- Integrated probe byte-identical to HEAD: yes (`{files[wf.INTEGRATED]}`)
- Preferred expectation shape in ReduceMap: 15 `example`s; 11 visit + 1 decline
  check tactics and 3 `rfl` baselines (not fallback counts)

## File hashes
| path | sha256 |
| --- | --- |
| `{wf.BASIC}` | `{files[wf.BASIC]}` |
| `{wf.TEST}` | `{files[wf.TEST]}` |
| `{wf.INTEGRATED}` | `{files[wf.INTEGRATED]}` |

## Gate statuses (fingerprint `{fp}`)
| stage | status | fingerprint match | command exits |
| --- | --- | --- | --- |
| baseline | passed (pre-candidate clean tree) | n/a (clean-tree fp `{gates['baseline']['source_sha256']}`) | {exits(gates['baseline'])} |
| focused | {gates['focused']['status']} | {gates['focused']['source_sha256'] == fp} | {exits(gates['focused'])} |
| downstream | {gates['downstream']['status']} | {gates['downstream']['source_sha256'] == fp} | {exits(gates['downstream'])} |
| full | {full['status']} | {full['source_sha256'] == fp} | {exits(full)} |

### Full command detail (current official marker)
| step | exit | log | log_size |
| --- | --- | --- | --- |
{detail_rows}
### Official full-3 test log (non-empty)
Log `{full3['log']}` ({(EV / full3['log']).stat().st_size} bytes), exit {full3['exit_code']}:

```
{full3_text.strip()}
```

How this log was obtained: deleted lake artifacts for
`MathlibTest.ComposableArrowsReduceMap` and `MathlibTest.ComposableArrowsIntegratedProbe`,
then ran `python3 .cursor-handoff/workflow.py run full`. Other MathlibTest targets were
already up-to-date (cache hits, not rebuilt). `ClickSuggestions.Benchmark.olean` was
left intact because a prior broad rebuild failed that wall-clock guard
(`full-3-1791084123470358418.log`).

### Supplemental (labeled supplemental; not a substitute marker)
- `lake --iofail test` after the same candidate artifact clean:
  `{supp_latest}` size={(EV / supp_latest).stat().st_size} exit={supp_meta.get('exit_code')}
  fingerprint={supp_meta.get('fingerprint')}
- Earlier candidate-only rebuild:
  `supplemental-iofail-candidate-1791088555137648473.log` (266 bytes, EXIT:0)

## What was false or incomplete before
1. Official full-gate test log `full-3-1791085799857013292.log` was **0 bytes**.
   Exit 0 was real; rebuild evidence for the candidate was not in that official log.
2. Prior ZIP `{OLD_ZIP}` matched its bytes (verified) but packaged that empty full-3.
3. Export `SUMMARY.json` scope text still said baseline discrimination needed a
   separate report even though adversarial artifacts were already present.
4. Preferred adversarial success logs are only `EXIT:0` (lean silent on success).
   Not fabricated, but weak as transcripts; original-failure logs hold the errors.

## What was fixed (evidence paths)
1. Forced non-cached candidate rebuild through official full gate:
   - `full-rerun-clean-note-*.json`, `full-rerun-wrapper.log`
   - new `full.json` with non-empty `{full3['log']}`
2. Supplemental non-empty `lake --iofail test`: `{supp_latest}`
3. Live adversarial spot-check after full rerun (fingerprint unchanged): `{spot_name}`
   preferred custom_ofnat_first / wrong_sem exit 0; original both exit 1.
4. FINAL_REPORT rewritten to verified facts only.

## Adversarial matrix (`~/mathlib4-cursor-adv`)
Source matrix: `advsuite_matrix.json` (timestamp {adv_ts}).
Live confirmation: `{spot_name}`.

| probe | original exit | preferred exit |
| --- | --- | --- |
| standard_visit | 0 | 0 |
| custom_ofnat_first | 1 | 0 |
| custom_ofnat_first_wrong_sem | 1 | 0 |
| custom_ofnat_second | 1 | 0 |
| custom_ofnat_second_wrong_sem | 1 | 0 |
| equivalent_ofnat | 0 | 0 |
| shadow_le | 1 | 0 |
| opaque_decline | 0 | 0 |
| successor_constructors | 1 | 0 |

## Push safeguards
- failing `pre-push` via `core.hooksPath` mateo-local-hooks
- `remote.origin.pushurl=disabled://mateo-approval-required`
- No remote mutations performed.

## Residual risks / what was NOT proven
- Official full-3 proves rebuild of the **two candidate MathlibTest modules** under
  `lake --iofail test` exit 0. It does **not** prove a cold rebuild of all MathlibTest
  modules in that run.
- Prior broader MathlibTest rebuild failed on `MathlibTest.ClickSuggestions.Benchmark`
  (`full-3-1791084123470358418.log`). Full-suite cold test under this host is not proven.
- Finite adversarial probes only; not a universal claim about all `Precomp.map` inputs.
- Local gates/export do not authorize upstream submission.
- WSL ~7.4Gi RAM remains an environment risk for aggressive MathlibTest parallelism.
{zip_section}
## Artifacts
- Evidence: `/home/mateo/mathlib4-cursor/.cursor-handoff/evidence/`
- WSL ZIP: `/home/mateo/mathlib4-cursor/.cursor-handoff/cursor-validation-evidence.zip`
- Windows mirror: `C:/Users/mateo/mathlib4-1/cursor-mathlib-handoff/cursor-validation-evidence.zip`
"""


def main() -> None:
    wf = load_wf()
    fp = wf.fingerprint(REPO)
    assert fp == FP_EXPECTED, fp

    files = {
        wf.BASIC: sha(REPO / wf.BASIC),
        wf.TEST: sha(REPO / wf.TEST),
        wf.INTEGRATED: sha(REPO / wf.INTEGRATED),
    }
    head_int = subprocess.check_output(["git", "-C", str(REPO), "show", f"HEAD:{wf.INTEGRATED}"])
    assert hashlib.sha256(head_int).hexdigest() == files[wf.INTEGRATED]

    gates = {s: json.loads((EV / f"{s}.json").read_text()) for s in
             ("baseline", "focused", "downstream", "full")}
    full = gates["full"]
    assert full["status"] == "passed" and full["source_sha256"] == fp
    full3 = next(c for c in full["commands"] if c["argv"] == ["lake", "--iofail", "test"])
    full3_log = EV / full3["log"]
    full3_text = full3_log.read_text(errors="replace")
    assert full3["exit_code"] == 0 and full3_log.stat().st_size > 0
    assert "ComposableArrowsReduceMap" in full3_text
    assert "ComposableArrowsIntegratedProbe" in full3_text

    supp_latest = (EV / "supplemental-iofail-mathlibtest.LATEST").read_text().strip()
    supp_meta_path = EV / supp_latest.replace(".log", ".json")
    supp_meta = json.loads(supp_meta_path.read_text())
    spot_name = sorted(EV.glob("spotcheck-adv-*.json"))[-1].name
    adv_ts = json.loads((EV / "advsuite_matrix.json").read_text()).get("timestamp")

    report = build_report(
        wf, fp, files, gates, full3, full3_text, supp_latest, supp_meta, spot_name, adv_ts,
        None, None,
    )
    (EV / "FINAL_REPORT.md").write_text(report, encoding="utf-8")

    # Export (includes FINAL_REPORT without final ZIP hash)
    r = subprocess.run(["python3", str(REPO / ".cursor-handoff" / "workflow.py"), "export"], cwd=REPO)
    print("export_exit", r.returncode)
    if r.returncode != 0:
        raise SystemExit("export failed")

    zip_path = REPO / ".cursor-handoff" / "cursor-validation-evidence.zip"
    zip_sha = sha(zip_path)
    zip_bytes = zip_path.stat().st_size
    shutil.copy2(zip_path, WIN / "cursor-validation-evidence.zip")
    assert sha(WIN / "cursor-validation-evidence.zip") == zip_sha

    auth = (
        f"ZIP_SHA256={zip_sha}\n"
        f"ZIP_BYTES={zip_bytes}\n"
        f"FINGERPRINT={fp}\n"
        f"OLD_ZIP_SHA256_SUPERSEDED={OLD_ZIP}\n"
        f"FULL_TEST_LOG={full3['log']}\n"
        f"FULL_TEST_LOG_SIZE={full3_log.stat().st_size}\n"
        f"FULL_TEST_EXIT={full3['exit_code']}\n"
    )
    (EV / "EXPORT_HASHES.txt").write_text(auth, encoding="utf-8")

    # Rewrite FINAL_REPORT with hash; re-export once so ZIP contains hash narrative.
    report2 = build_report(
        wf, fp, files, gates, full3, full3_text, supp_latest, supp_meta, spot_name, adv_ts,
        zip_sha, zip_bytes,
    )
    # Note: after re-export, ZIP bytes/hash change because FINAL_REPORT/EXPORT_HASHES change.
    # Put the pre-final hash in the report as "hash before including this hash section" is messy.
    # Instead: report says trust EXPORT_HASHES / sha256sum; then final export; then overwrite
    # EXPORT_HASHES + Windows FINAL_REPORT with authoritative post-export hash.
    report2 = build_report(
        wf, fp, files, gates, full3, full3_text, supp_latest, supp_meta, spot_name, adv_ts,
        None, None,
    )
    report2 += f"""
## Export hashes
Authoritative values are written to `EXPORT_HASHES.txt` after packaging and mirrored
on Windows. Run `sha256sum` on the ZIP bytes to confirm.
"""
    (EV / "FINAL_REPORT.md").write_text(report2, encoding="utf-8")
    (EV / "EXPORT_HASHES.txt").write_text(auth, encoding="utf-8")

    r = subprocess.run(["python3", str(REPO / ".cursor-handoff" / "workflow.py"), "export"], cwd=REPO)
    print("export2_exit", r.returncode)
    if r.returncode != 0:
        raise SystemExit("export2 failed")

    zip_sha = sha(zip_path)
    zip_bytes = zip_path.stat().st_size
    shutil.copy2(zip_path, WIN / "cursor-validation-evidence.zip")
    assert sha(WIN / "cursor-validation-evidence.zip") == zip_sha

    auth = (
        f"ZIP_SHA256={zip_sha}\n"
        f"ZIP_BYTES={zip_bytes}\n"
        f"FINGERPRINT={fp}\n"
        f"OLD_ZIP_SHA256_SUPERSEDED={OLD_ZIP}\n"
        f"FULL_TEST_LOG={full3['log']}\n"
        f"FULL_TEST_LOG_SIZE={full3_log.stat().st_size}\n"
        f"FULL_TEST_EXIT={full3['exit_code']}\n"
    )
    (EV / "EXPORT_HASHES.txt").write_text(auth, encoding="utf-8")
    (WIN / "EXPORT_HASHES.txt").write_text(auth, encoding="utf-8")

    final_report = build_report(
        wf, fp, files, gates, full3, full3_text, supp_latest, supp_meta, spot_name, adv_ts,
        zip_sha, zip_bytes,
    )
    # Windows + evidence narrative with authoritative hash (may be slightly newer than
    # FINAL_REPORT.md inside the ZIP; EXPORT_HASHES.txt and sha256sum are decisive).
    (EV / "FINAL_REPORT.md").write_text(final_report, encoding="utf-8")
    (WIN / "FINAL_REPORT.md").write_text(final_report, encoding="utf-8")

    print("AUTHORITATIVE_ZIP_SHA256", zip_sha)
    print("ZIP_BYTES", zip_bytes)
    print("FINGERPRINT", fp)
    print("FULL3", full3["log"], full3_log.stat().st_size)


if __name__ == "__main__":
    main()
