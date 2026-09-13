# Configuration: H-E1 Verification Script

**Hypothesis:** H-E1
**Type:** EXISTENCE (MUST_WORK)
**Date:** 2026-08-22

Applied: Python constants + dataclass pattern (standard; no specialized KB pattern matched)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: module-level constants (no dataclass needed for this scale)

---

## A-1: Script Constants [Complexity: 1, Budget: 0 dedicated]

Single constants block at top of `verify.py`. No separate config file needed — the script is one file.

### Configuration (Python Constants)

```python
# --- H-E1 Configuration ---
import os
from pathlib import Path

# Root of the repo (two levels up from h-e1/code/)
_REPO_ROOT = Path(__file__).resolve().parents[3]

ARCHIVE = Path(
    os.environ.get(
        "H_E1_ARCHIVE_DIR",
        _REPO_ROOT / "docs/youra_research/_archive"
        / "20260822T150921_routing_recovery/h-e1/results"
    )
)

HE_FILE   = ARCHIVE / "humaneval_samples_eval_results.json"
MBPP_FILE = ARCHIVE / "mbpp_samples_eval_results.json"

HE_EXPECTED   = 34
MBPP_EXPECTED = 100
TOTAL_EXPECTED = HE_EXPECTED + MBPP_EXPECTED  # 134

FIGURES_DIR = Path(__file__).parent.parent / "figures"
RESULTS_DIR = Path(__file__).parent.parent / "results"
```

**Non-standard**: `H_E1_ARCHIVE_DIR` env-var override lets CI or other machines point to a relocated archive without editing source.

---

## A-2: Verification Report Schema

Output written to `RESULTS_DIR / "verification_report.json"`.

### Schema (JSON)

```json
{
  "gate": "PASS",
  "timestamp": "2026-08-22T15:09:21Z",
  "checks": {
    "he_failure_count":        {"expected": 34,  "actual": 34,  "pass": true},
    "mbpp_failure_count":      {"expected": 100, "actual": 100, "pass": true},
    "total_failure_count":     {"expected": 134, "actual": 134, "pass": true},
    "solution_present":        {"expected": 134, "actual": 134, "pass": true},
    "plus_fail_tests_present": {"expected": 134, "actual": 134, "pass": true},
    "evalplus_api_accessible": {"pass": true},
    "task_ids_in_evalplus":    {"expected": 134, "actual": 134, "pass": true}
  },
  "summary": {
    "he_failures": 34,
    "mbpp_failures": 100,
    "total": 134
  }
}
```

### Python struct to write it

```python
import json, datetime

def write_report(checks: dict, he_count: int, mbpp_count: int) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "gate": "PASS" if all(c["pass"] for c in checks.values()) else "FAIL",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "checks": checks,
        "summary": {
            "he_failures": he_count,
            "mbpp_failures": mbpp_count,
            "total": he_count + mbpp_count,
        },
    }
    out = RESULTS_DIR / "verification_report.json"
    out.write_text(json.dumps(report, indent=2))
```

---

## Subtasks [0/0 used — config merged into script epics]

No dedicated config subtasks. Constants are inlined at the top of `verify.py`.
