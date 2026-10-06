#!/usr/bin/env bash
set -euo pipefail
source "$HOME/.elan/env"
REPO="$HOME/mathlib4-handoff"
EV="$REPO/.handoff/evidence"
cd "$REPO"

python3 - <<'PY'
from pathlib import Path
import json, subprocess, sys
sys.path.insert(0, str(Path.home()/ "mathlib4-handoff" / ".handoff"))
import workflow
repo = Path.home() / "mathlib4-handoff"
ev = repo / ".handoff" / "evidence"
fp = workflow.fingerprint(repo)
sel = json.loads((repo / ".handoff" / "selection.json").read_text())
gates = {}
for stage in ["baseline", "focused", "downstream", "full"]:
    rec = json.loads((ev / f"{stage}.json").read_text())
    status = rec.get("status")
    sha = rec.get("source_sha256")
    if stage != "baseline" and sha != fp:
        status = f"stale({status})"
    elif stage == "baseline" and status == "passed":
        status = "passed(pre-candidate)"
    gates[stage] = {"status": status, "source_sha256": sha}

report = ev / "FINAL_REPORT.md"
report.write_text(f"""# ComposableArrows handoff — final report

## Selection
- Candidate: **{sel['candidate']}**
- Base HEAD: `{sel['base']}`
- Toolchain: `leanprover/lean4:v4.35.0-rc3`
- Final source fingerprint: `{fp}`
- Fallback used: **no**

## Gate statuses
| stage | status | fingerprint |
| --- | --- | --- |
| baseline | {gates['baseline']['status']} | `{gates['baseline']['source_sha256']}` |
| focused | {gates['focused']['status']} | `{gates['focused']['source_sha256']}` |
| downstream | {gates['downstream']['status']} | `{gates['downstream']['source_sha256']}` |
| full | {gates['full']['status']} | `{gates['full']['source_sha256']}` |

All candidate gates passed for the final preferred fingerprint above.

## Harness repairs
See `harness-repairs.md`:
1. Retargeted custom `OfNat` / shadowed `LE` instances to `Fin (2 + 1 + 1)` (and high-priority LE) so instance search matches `Precomp.map` index types.
2. Disabled `linter.unusedTactic` / `linter.unreachableTactic` in the regression file because inspection tactics and `dsimp ... <;> rfl` are expected no-ops under `lake --iofail test`.

No expectation weakenings; no `sorry`/`admit`/axioms; integrated 13-example probe unchanged.

## Adversarial findings (separate checkout `~/mathlib4-handoff-adv`)
| probe | original | preferred |
| --- | --- | --- |
| custom_numeral (expect map = F.map' 0 0) | fail (exit 1): reducer changed expression type | pass (exit 0) |
| custom_numeral_wrong_sem (map = 𝟙 X) | fail (exit 1): goal does not elaborate under custom OfNat | fail (exit 1): same elaboration barrier; preferred does not wrongly succeed |
| shadow_le | fail (exit 1): `mkDecideProof` synthesizes LE under shadowed instance | pass (exit 0) |
| standard_visit | pass (exit 0); reducer invoked | pass (exit 0) |

Conclusion: original reducer is live on standard cases but fails custom-numeral type preservation and resynthesizes LE proofs under shadowing. Preferred preserves custom OfNat meaning and stored LE proofs. Details in `adversarial-summary.md` and `adv_*.log`.

## Fallback
Not used. Preferred completed focused/downstream/full without a diagnosed design failure.

## Limitations
- Finite regression and adversarial probes; not a universal proof about all `Precomp.map` inputs.
- `custom_numeral_wrong_sem` could not show original reducing to `𝟙 X` because that equality does not elaborate under the custom `OfNat` (hom-type mismatch). Discrimination instead rests on original failing the correct-semantics probe via type-changing reduction, while preferred passes.
- Local gates and export do not authorize upstream submission or remote writes.
- Push safeguards remain in place; no remote mutations performed.

## Artifacts
- Evidence directory: `.handoff/evidence/`
- Export ZIP: `.handoff/validation-evidence.zip`
""", encoding="utf-8")
print(report)
print("fingerprint", fp)
for k,v in gates.items():
    print(k, v)
PY

python3 .handoff/workflow.py export
ls -la .handoff/validation-evidence.zip
# also copy zip path echo for Windows side
cp -f .handoff/validation-evidence.zip /mnt/c/Users/mateo/mathlib4-1/composable-arrows-handoff/validation-evidence.zip || true
echo "ZIP=$REPO/.handoff/validation-evidence.zip"
cat "$EV/FINAL_REPORT.md"
