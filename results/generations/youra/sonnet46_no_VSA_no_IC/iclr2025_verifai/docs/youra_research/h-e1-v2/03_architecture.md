# Architecture: H-E1-v2
**EvalPlus Failure Set Recovery Verification**

Applied: N/A — no relevant KB patterns found (CV-domain KB, unrelated to EvalPlus/code verification)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no code to analyze
**Analyzed Path**: N/A
**Findings**: New single-script implementation from scratch. No existing codebase.

---

## Overview

Single Python script (~80 lines). No training, no GPU, no model. Verifies 134 EvalPlus failures
are recoverable from archive via 4 sub-condition checks.

---

## File Organization

- `docs/youra_research/h-e1-v2/code/verify_h_e1_v2.py` — main verification script (all logic)
- `docs/youra_research/h-e1-v2/figures/gate_conditions.png` — required output figure
- `docs/youra_research/h-e1-v2/results.json` — structured verification results

---

## Module Structure

### VerificationScript (`code/verify_h_e1_v2.py`)

**Dependencies**: `evalplus==0.3.1`, stdlib (`json`, `pathlib`, `argparse`, `sys`)

```python
def verify_h_e1_v2(archive_path: str) -> dict:
    """
    Run all 4 sub-condition checks against the h-e1 archive.
    Returns structured results dict with per-condition pass/fail and gate_passed bool.
    Exit: sys.exit(0) on pass, sys.exit(1) on fail.
    """
    ...

def _check_c1_failure_ids(archive: pathlib.Path) -> tuple[dict, list, list]:
    """Load HE+/MBPP+ eval results; return condition result + he_failures + mbpp_failures."""
    ...

def _check_c2_stored_solutions(archive: pathlib.Path, he_failures: list, mbpp_failures: list) -> dict:
    """Load solutions_cache.jsonl; verify 134/134 coverage."""
    ...

def _check_c3_evalplus_api(he_failures: list, mbpp_failures: list) -> tuple[dict, dict, dict]:
    """Import evalplus; call get_human_eval_plus/get_mbpp_plus; verify IDs present."""
    ...

def _check_c4_deterministic_test(he_failures: list, he_data: dict) -> dict:
    """Access plus_input[0] on first HE+ failure; assert len > 0."""
    ...

def _generate_figure(results: dict, out_path: pathlib.Path) -> None:
    """Bar chart: pass/fail per condition C1–C4. Uses matplotlib."""
    ...

if __name__ == "__main__":
    # argparse: --archive <path> [--output <results.json>] [--figures <dir>]
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create code/ dir, verify evalplus==0.3.1 installable, confirm archive path exists | 4 | 1+1+1+1 |
| A-2 | C1+C2 Logic | Implement `_check_c1_failure_ids` and `_check_c2_stored_solutions`; load JSON/JSONL, filter plus_status, cross-ref cache | 7 | 2+1+2+2 |
| A-3 | C3+C4 Logic | Implement `_check_c3_evalplus_api` and `_check_c4_deterministic_test`; call evalplus API, verify IDs and plus_input field | 7 | 2+2+2+1 |
| A-4 | Entry Point + Reporting | Wire `verify_h_e1_v2()`, structured log output, results.json write, argparse CLI, sys.exit codes | 6 | 1+1+2+2 |
| A-5 | Figure Generation | `_generate_figure`: 4-bar chart (C1–C4 pass/fail), save to figures/gate_conditions.png | 5 | 1+1+2+1 |
| A-6 | End-to-End Integration Test | Run script against actual archive; assert gate_passed==True; capture stdout log | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6]

**Total estimated complexity**: 34 (appropriate for EXISTENCE/LIGHT tier single-script experiment)

---

## Dependency Notes

- `matplotlib` required for figure generation (likely already installed; if not, `pip install matplotlib`)
- All other deps: stdlib + `evalplus==0.3.1`
- Archive must exist at: `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/`
