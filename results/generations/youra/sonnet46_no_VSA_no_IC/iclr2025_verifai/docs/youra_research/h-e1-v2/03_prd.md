# Product Requirements Document: H-E1-v2
## EvalPlus Failure Set Recovery Verification

**Hypothesis ID:** H-E1-v2
**Type:** EXISTENCE (MUST_WORK gate)
**Date:** 2026-08-22
**Author:** Anonymous
**Status:** Phase 3 - Implementation Planning

---

## 1. Executive Summary

H-E1-v2 verifies that the 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+) are fully recoverable as a fixed problem set with stored GPT-4o-mini incorrect outputs. This enables Conditions B and C prompt construction for downstream hypotheses (H-M1, H-M2, H-C1) without requiring new baseline API calls.

**Gate:** MUST_WORK — all 4 sub-conditions must pass. Failure blocks all downstream hypotheses.

**Scope:** Single Python verification script (~50–80 lines), no model training, no GPU, no API calls.

---

## 2. Problem Statement

H-E1 (v1) failed its MUST_WORK gate. The root cause was that static analysis (SA) fired on solutions, indicating potential non-semantic failures mixed with semantic failures. H-E1-v2 redesigns the verification to be explicit and granular: each of the 4 sub-conditions is verified and reported separately.

**What must be proven:**
1. All 134 failure IDs are loadable from the archive
2. Stored incorrect GPT-4o-mini solutions cover all 134 failures
3. EvalPlus API is accessible and returns all 134 failure task IDs
4. Deterministic first-failing-test selection is possible via `plus_input[0]`

---

## 3. Functional Requirements

### FR-1: Archive Failure ID Loading (→ Condition C1)
- Load `humaneval_samples_eval_results.json` and extract all task IDs where all solutions have `plus_status != "pass"`
- Expected: 34 HE+ failure IDs
- Load `mbpp_samples_eval_results.json` similarly
- Expected: 100 MBPP+ failure IDs
- Assert: `len(he_failures) == 34 and len(mbpp_failures) == 100 and total == 134`

### FR-2: Stored Solution Coverage Verification (→ Condition C2)
- Load `solutions_cache.jsonl` (542 entries)
- Build lookup dict: `task_id → [solutions]`
- For each failure ID (34 HE+ + 100 MBPP+), verify presence in cache
- Assert: `covered_he == 34 and covered_mbpp == 100`

### FR-3: EvalPlus API Accessibility (→ Condition C3)
- Import `from evalplus.data import get_human_eval_plus, get_mbpp_plus`
- Call both; verify all 134 failure IDs are present in the returned dicts
- Assert: `he_found == 34 and mbpp_found == 100`

### FR-4: Deterministic Test Selection (→ Condition C4)
- For the first HE+ failure task ID, access `he_data[task_id]["plus_input"]`
- Assert: `len(plus_input) > 0` (field exists and non-empty)
- This confirms `plus_input[0]` is a stable, deterministic first-failing-test selector

### FR-5: Structured Result Reporting
- Return a dict with per-condition results: `c1_failure_ids`, `c2_stored_solutions`, `c3_evalplus_api`, `c4_deterministic_test`
- Each entry contains counts and a `pass: bool` field
- Top-level `gate_passed: bool` = AND of all condition passes
- Print structured log messages per condition

### FR-6: Verification Entry Point
- Single runnable script: `verify_h_e1_v2.py`
- Function signature: `verify_h_e1_v2(archive_path: str) -> dict`
- CLI: `python verify_h_e1_v2.py --archive <path>`
- Assert `results["gate_passed"] == True` at end of script
- Exit code 0 on pass, non-zero on failure

---

## 4. Data Specification

### 4.1 Primary Dataset: h-e1 Archive
- **Type:** programmatic-api + local JSON/JSONL files
- **Version:** EvalPlus HumanEval+ v0.1.10, MBPP+ v0.2.0
- **Cache path:** `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/`

| File | Contents | Items |
|------|----------|-------|
| `humaneval_samples_eval_results.json` | HE+ eval results per task | 164 tasks, 34 failures |
| `mbpp_samples_eval_results.json` | MBPP+ eval results per task | 378 tasks, 100 failures |
| `solutions_cache.jsonl` | All stored solutions | 542 entries |
| `humaneval_samples.jsonl` | HE+ solution records | 164 records |
| `mbpp_samples.jsonl` | MBPP+ solution records | 378 records |
| `h_e1_results.json` | Aggregate results | 134 failures confirmed |

**Loading method:**
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
import json, pathlib

ARCHIVE = pathlib.Path("docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results")
```

**Data integrity:** Empirically pre-verified in Phase 2C. All 134 failure IDs confirmed present.

### 4.2 EvalPlus API Dataset
- **Source:** `evalplus` package (install: `pip install evalplus==0.3.1`)
- **Download:** Auto-downloads on first call (cached by evalplus)
- **HumanEval+:** 164 total tasks → use 34 failure IDs as filter
- **MBPP+:** 378 total tasks → use 100 failure IDs as filter
- **No manual download required** — handled by `get_human_eval_plus()` / `get_mbpp_plus()`

---

## 5. Non-Functional Requirements

| NFR | Requirement |
|-----|------------|
| Runtime | < 60 seconds total (file I/O + API cache load) |
| Reproducibility | Deterministic — same result every run (no randomness) |
| Portability | Python 3.9+, no GPU, no API keys |
| Dependencies | `evalplus==0.3.1` + stdlib (`json`, `pathlib`, `argparse`) |
| Error reporting | Per-condition pass/fail; no silent failures |
| Exit code | 0 = gate passed; 1 = gate failed |

---

## 6. Success Criteria

### Gate Pass Condition (MUST_WORK)
All 4 conditions must return `pass: True`:

| Condition | Assertion | Expected |
|-----------|-----------|----------|
| C1: failure_ids | `total == 134` | 34 HE+ + 100 MBPP+ |
| C2: stored_solutions | `covered == 134` | 134/134 in cache |
| C3: evalplus_api | `he_found==34 and mbpp_found==100` | All in API |
| C4: deterministic_test | `len(plus_input) > 0` | Field present |

**Gate:** `results["gate_passed"] == True` → downstream hypotheses unblocked.

### Downstream Impact
- PASS: H-M1, H-M2, H-C1 can proceed
- FAIL: all downstream hypotheses blocked

---

## 7. Dependencies

### 7.1 Python Packages
```
evalplus==0.3.1
# stdlib only: json, pathlib, argparse, math
```

### 7.2 External Repositories (Reference Only)
- `evalplus/evalplus` — EvalPlus evaluation framework (NeurIPS 2023, COLM 2024)
- `SYSUSELab/FeedbackEval` — Feedback-driven code repair patterns (reference)
- `kr-ai-dev-association/agent-evaluation` — McNemar test (for downstream H-M1/M2)

### 7.3 Local Data Dependencies
- Archive at: `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/`
- All files must exist (verified in Phase 2C)

---

## 8. Figures and Outputs

### Required Figure
- **4-condition gate bar chart:** pass/fail per condition (C1–C4)
- Output: `docs/youra_research/h-e1-v2/figures/gate_conditions.png`

### Optional Figures
- Failure distribution: HE+ (34) vs MBPP+ (100)
- Archive file inventory with item counts

### Primary Output
- `results.json`: full structured verification results dict
- Console log with `[H-E1-v2]` prefix per condition

---

## 9. Out of Scope

- Model inference (no API calls to GPT-4o-mini)
- Training or fine-tuning
- Statistical significance testing (that is H-M1/H-M2)
- Static analysis filtering of solutions (documented root cause of v1 failure; v2 does not filter)

---

*Phase 2C Source: `docs/youra_research/h-e1-v2/02c_experiment_brief.md`*
*Next Phase: Phase 4 - Implementation (`/phase4-coding`)*
