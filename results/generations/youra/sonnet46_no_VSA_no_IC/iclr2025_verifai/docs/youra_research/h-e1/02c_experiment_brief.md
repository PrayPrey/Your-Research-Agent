# Experiment Design: H-E1

**Date:** 2026-08-22
**Author:** Anonymous
**Hypothesis Statement:** The 134 h-e1 Run 2 EvalPlus failures (34 HE+ + 100 MBPP+) are recoverable as a fixed problem set with stored GPT-4o-mini incorrect outputs, enabling Conditions B and C prompt construction without new baseline API calls.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (MUST_WORK)
- **Prerequisites:** None

### Gate Condition
MUST_WORK — failure blocks H-M1, H-M2, H-C1. All 134 problem IDs + incorrect outputs must be loadable; EvalPlus API must be accessible.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous hypothesis context.

### Previous Hypothesis Results (if applicable)
None — H-E1 is the root of the dependency DAG.

> **Cross-pipeline note:** The prior h-e1 Run 2 experiment (separate pipeline) was a static-analysis oracle study that FAILED (ruff+mypy fires on only 16–32% of failures). Key lessons: (a) the 134-problem failure set itself is valid and reusable; (b) stored GPT-4o-mini solutions with `plus_fail_tests` are present in the eval_results JSON files; (c) EvalPlus API is accessible (confirmed by prior runs). The current hypothesis (H-E1 in the SpecRepair verification pipeline) verifies this data is still intact and loadable for the NEW experiment.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: EvalPlus benchmark evaluation LLM code generation**
- No relevant results in Archon KB (KB contains image diffusion content only)

**Query 2: Automated program repair LLM reprompting pass@1**
- No relevant results in Archon KB

**Query 3: Code benchmark dataset verification integrity check**
- No relevant results in Archon KB

**Summary:** Archon KB has no domain-relevant content for EvalPlus/code repair. All experiment design is grounded in Exa/GitHub findings and direct codebase inspection.

### Archon Code Examples

**Query: EvalPlus HumanEval MBPP benchmark Python evaluation**
- No relevant code examples in Archon KB (image/diffusion examples returned)

### Exa GitHub Implementations

**Query 1: `evalplus get_human_eval_plus get_mbpp_plus Python data loading verification`**

**Repository 1**: evalplus/evalplus (⭐ 1798)
- **URL**: https://github.com/evalplus/evalplus
- **Relevance**: Official EvalPlus benchmark — the exact API used by h-e1 Run 2
- **Key API**:
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus, write_jsonl

  # Load full HumanEval+ dataset
  he_problems = get_human_eval_plus()          # dict: task_id -> problem
  mbpp_problems = get_mbpp_plus()              # dict: task_id -> problem

  # Problem schema:
  # - task_id: str ("HumanEval/0", "Mbpp/1")
  # - prompt: function signature + docstring
  # - entry_point: function name
  # - canonical_solution: ground-truth code
  # - base_input: original test inputs
  # - plus_input: EvalPlus augmented test inputs (80x / 35x more)
  ```
- **Eval results schema** (from actual h-e1 Run 2 files):
  ```python
  # Per-task eval result record:
  {
    "task_id": "HumanEval/10",
    "solution": "<GPT-4o-mini generated code>",
    "base_status": "pass|fail",
    "plus_status": "pass|fail",
    "base_fail_tests": [...],   # empty if pass
    "plus_fail_tests": [...]    # failing test inputs (first entry = first failing test)
  }
  ```
- **Dataset**: HumanEval+ (164 tasks) + MBPP+ (378 tasks)
- **Install**: `pip install evalplus`

**Repository 2**: axolotl-ai-cloud/grpo_code — eval_plus/convert_data.py
- **Relevance**: Shows how to access `plus_input` and `base_input` programmatically
- **Key pattern**: `get_human_eval_plus()` returns dict with `.values()` iterable
- **Used for**: Confirming how to iterate over all tasks and filter by failure

**Repository 3**: NVIDIA-NeMo/Gym — resources_servers/evalplus/app.py
- **Relevance**: Production-grade EvalPlus server showing `get_human_eval_plus_hash`, `get_groundtruth`, `check_correctness` API
- **Key loading pattern**:
  ```python
  from evalplus.data import get_human_eval_plus, get_human_eval_plus_hash
  from evalplus.data import get_mbpp_plus, get_mbpp_plus_hash
  from evalplus.evaluate import get_groundtruth

  problems = get_human_eval_plus(version="default")
  problems_hash = get_human_eval_plus_hash()
  expected_output = get_groundtruth(problems, problems_hash, [])
  ```

**Query 2: LLM code repair reprompting EvalPlus failure verification Python**
- evalplus/evalplus issues #148, #157: Confirmed deterministic test ordering; `plus_fail_tests` lists are ordered lists of failing inputs
- Fix rate: Known from literature (FeedbackEval: 21.1pp avg repair; Haeri & Ghelichi 2026: +38pp with spec grounding)

**Serena Analysis Needed**: false — data format clear from actual h-e1 Run 2 files

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is a DATA VERIFICATION experiment, not a model implementation experiment. There is no "mechanism" to implement — only a verification script to load and check existing files.

**Recommended Implementation Path:**
- Primary: Direct Python script using `evalplus.data` API + `json` loading of h-e1 Run 2 eval_results JSON files
- Fallback: Re-run h-e1 Run 2 from scratch using `evalplus.codegen` with GPT-4o-mini (expensive, ~$0.025, avoid)
- Justification: The stored eval_results JSON files (`humaneval_samples_eval_results.json`, `mbpp_samples_eval_results.json`) already contain all 134 failure records with solutions and `plus_fail_tests`. Verification only requires loading and counting.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. The data format is confirmed by direct inspection of h-e1 Run 2 eval_results files: JSON with `eval` dict mapping task_id to list of solution records with `plus_status` and `plus_fail_tests` fields.

---

## Experiment Specification

### Dataset

**Dataset Specification:**

| Field | Value |
|-------|-------|
| Name | EvalPlus HumanEval+ + MBPP+ (h-e1 Run 2 failure subset) |
| Type | programmatic-api (real data via `evalplus` package) |
| HumanEval+ total | 164 tasks (164 problems from OpenAI HumanEval × 80x tests) |
| MBPP+ total | 378 tasks (MBPP subset × 35x tests) |
| H-E1 target | 34 HumanEval+ failures + 100 MBPP+ failures = **134 failures** |
| Stored outputs | `humaneval_samples_eval_results.json` + `mbpp_samples_eval_results.json` |
| Archive path | `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/` |
| Confirmed | ✅ 34 HE+ failures + 100 MBPP+ failures verified by direct Python count |

**What H-E1 verifies:**
1. 134 problem IDs loadable (34 HumanEval+ + 100 MBPP+)
2. `solution` field (GPT-4o-mini incorrect output) present for all 134
3. `plus_fail_tests` non-empty for all 134 (first failing test case accessible)
4. `evalplus.data.get_human_eval_plus()` and `get_mbpp_plus()` callable (API accessible)
5. All 134 task IDs present in EvalPlus datasets (problem prompt + docstring retrievable)

**Synthetic data policy:** Not applicable — this is a real existing dataset (stored API outputs + standard benchmark).

**Loading Information** (for Phase 4 download):
- Method: Python `json` + `evalplus` package
- Identifier: Archive path (local) + `pip install evalplus` (package)
- Code:
  ```python
  import json
  from evalplus.data import get_human_eval_plus, get_mbpp_plus

  # Load stored h-e1 Run 2 results
  ARCHIVE = "docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results"
  with open(f"{ARCHIVE}/humaneval_samples_eval_results.json") as f:
      he_results = json.load(f)["eval"]
  with open(f"{ARCHIVE}/mbpp_samples_eval_results.json") as f:
      mbpp_results = json.load(f)["eval"]

  # Extract failures
  he_failures = {tid: sols[0] for tid, sols in he_results.items()
                 if sols[0]["plus_status"] == "fail"}
  mbpp_failures = {tid: sols[0] for tid, sols in mbpp_results.items()
                   if sols[0]["plus_status"] == "fail"}

  # Load EvalPlus API datasets
  he_problems = get_human_eval_plus()
  mbpp_problems = get_mbpp_plus()
  ```

### Models

#### Baseline Model

**H-E1 does not involve a model.** This is a data existence/integrity verification experiment. The "model" is GPT-4o-mini, but only its stored outputs are accessed — no new API calls are made.

**Stored Model Outputs:**
- Model: GPT-4o-mini (OpenAI)
- Temperature: 0.0 (greedy, from h-e1 Run 2)
- Stored in: `humaneval_samples_eval_results.json` and `mbpp_samples_eval_results.json`
- Field: `solution` (full Python function including prompt prefix)

**Loading Information** (for Phase 4 download):
- Method: Local JSON file (no download required)
- Identifier: Archive path (already on disk)
- Code:
  ```python
  # No API call needed — stored outputs already on disk
  incorrect_solution = he_failures["HumanEval/10"]["solution"]
  first_failing_test = he_failures["HumanEval/10"]["plus_fail_tests"][0]
  ```

#### Proposed Model

**Architecture:** N/A — H-E1 is existence verification, not a model comparison experiment.

**Core Mechanism Implementation:**

```python
# Core Mechanism: H-E1 Data Verification
# Based on: h-e1 Run 2 eval_results JSON schema + evalplus.data API
# This is not a ML model — it is a verification script

def verify_h_e1_data(archive_dir, he_results_file, mbpp_results_file):
    """
    Args:
        archive_dir: path to h-e1 Run 2 results directory
        he_results_file: humaneval_samples_eval_results.json
        mbpp_results_file: mbpp_samples_eval_results.json
    Returns:
        dict with verification results (pass/fail per check)
    """
    import json
    from evalplus.data import get_human_eval_plus, get_mbpp_plus

    # Step 1: Load stored eval results
    with open(f"{archive_dir}/{he_results_file}") as f:
        he_eval = json.load(f)["eval"]
    with open(f"{archive_dir}/{mbpp_results_file}") as f:
        mbpp_eval = json.load(f)["eval"]

    # Step 2: Extract failures
    he_fails = {tid: r[0] for tid, r in he_eval.items()
                if r[0]["plus_status"] == "fail"}
    mbpp_fails = {tid: r[0] for tid, r in mbpp_eval.items()
                  if r[0]["plus_status"] == "fail"}

    # Step 3: Verify counts
    assert len(he_fails) == 34, f"Expected 34 HE+ failures, got {len(he_fails)}"
    assert len(mbpp_fails) == 100, f"Expected 100 MBPP+ failures, got {len(mbpp_fails)}"

    # Step 4: Verify stored outputs present
    for tid, rec in {**he_fails, **mbpp_fails}.items():
        assert rec["solution"], f"Missing solution for {tid}"
        assert rec["plus_fail_tests"], f"No failing tests for {tid}"

    # Step 5: Verify EvalPlus API accessible + task IDs present
    he_problems = get_human_eval_plus()
    mbpp_problems = get_mbpp_plus()
    for tid in he_fails:
        assert tid in he_problems, f"{tid} not in EvalPlus HE+ dataset"
    for tid in mbpp_fails:
        assert tid in mbpp_problems, f"{tid} not in EvalPlus MBPP+ dataset"

    return {"gate": "PASS", "he_failures": len(he_fails),
            "mbpp_failures": len(mbpp_fails), "total": len(he_fails) + len(mbpp_fails)}
```

### Training Protocol

H-E1 is a verification script — no training. No optimizer, no learning rate, no epochs.

**Execution Protocol:**

| Parameter | Value |
|-----------|-------|
| Script type | Verification (assertion-based) |
| Runtime | < 10 seconds (local JSON load + API call) |
| Seeds | N/A |
| GPU | Not required |
| Dependencies | `evalplus>=0.3.1`, `json` (stdlib) |
| Expected output | All assertions pass → gate PASS |

**Install:**
```bash
pip install "evalplus" --upgrade
```

### Evaluation

**Primary Metrics (EXISTENCE PoC):**

| Check | Target | Type |
|-------|--------|------|
| HE+ failure count | == 34 | Hard assertion |
| MBPP+ failure count | == 100 | Hard assertion |
| Total failures | == 134 | Hard assertion |
| `solution` present | All 134 non-empty | Hard assertion |
| `plus_fail_tests` present | All 134 non-empty | Hard assertion |
| EvalPlus API accessible | `get_human_eval_plus()` returns dict | Hard assertion |
| Task IDs in EvalPlus | All 134 task IDs present in dataset | Hard assertion |

**Success Criteria (PoC):**
- All 7 assertions pass → gate PASS → H-M1 can proceed
- Any assertion fails → gate FAIL → pipeline stops

**Expected Baseline Performance:** N/A — this is a deterministic verification (binary pass/fail).

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: data integrity verification
- Library: `json` (stdlib) + `evalplus.data`
- Code:
  ```python
  result = verify_h_e1_data(ARCHIVE_DIR, "humaneval_samples_eval_results.json",
                             "mbpp_samples_eval_results.json")
  print(f"Gate: {result['gate']}")  # "PASS" or AssertionError
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing actual counts vs. expected counts:
  - HE+ failures: actual=34, expected=34
  - MBPP+ failures: actual=100, expected=100
  - Total: actual=134, expected=134
  - All assertions: N/7 passed (labeled)

#### Additional Figures (LLM Autonomous)

Based on the verification nature of H-E1, useful additional figures:
1. **Failure distribution by benchmark** — pie/bar chart: 34 HE+ vs. 100 MBPP+ (25.4% vs. 74.6%)
2. **Data completeness matrix** — heatmap: each of 134 tasks × {solution_present, plus_fail_tests_present, task_in_api} → all green if PASS
3. **plus_fail_tests count distribution** — histogram of how many failing tests each of the 134 problems has (shows if any have only 1 failing test, which affects first-test determinism for H-M1/H-M2)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol (CRITICAL)

> H-E1 is a data existence verification experiment, not a model experiment. The "mechanism" is data recoverability.

**Pre-conditions:**
- `mechanism_exists`: Archive JSON files exist on disk at expected path
- `mechanism_isolatable`: Each of the 7 assertions is independently checkable
- `baseline_measurable`: Ground truth is exact counts (34, 100, 134) — no ambiguity

**Architecture Compatibility:**
- No neural architecture involved
- Verification script is pure Python: `json` + `evalplus.data` API
- EvalPlus package must be installed (`pip install evalplus`)
- No GPU, no CUDA, no model weights required

**Mechanism Activation Indicators:**
- Log message: `"✅ H-E1 gate PASS: 134 failures loaded (34 HE+ + 100 MBPP+)"`
- Tensor shape change: N/A
- Metric delta expected: N/A — binary pass/fail

**Mechanism Verification Code:**
```python
# Verification activation indicator
import logging
logger = logging.getLogger(__name__)

result = verify_h_e1_data(ARCHIVE_DIR, HE_FILE, MBPP_FILE)
if result["gate"] == "PASS":
    logger.info(f"✅ H-E1 gate PASS: {result['total']} failures loaded "
                f"({result['he_failures']} HE+ + {result['mbpp_failures']} MBPP+)")
```

**Failure Detection:**
- `AssertionError` on any count mismatch → gate FAIL
- `FileNotFoundError` if archive path wrong → gate FAIL
- `ImportError` if evalplus not installed → gate FAIL (install first)
- `KeyError` on missing `plus_fail_tests` → gate FAIL

**Success Criteria:**
- `hypothesis_support_threshold`: All 7 assertions pass (0 failures)
- `hypothesis_support_metric`: gate == "PASS"

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Script runs without `AssertionError`
2. All 7 data integrity assertions pass
3. `result["gate"] == "PASS"`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB returned no relevant results for EvalPlus/code repair domain (KB contains image diffusion content). No Archon sources used in experiment design.

### B. GitHub Implementations (Exa)

**Repository 1**: evalplus/evalplus (⭐ 1798)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: `evalplus get_human_eval_plus get_mbpp_plus Python data loading verification`
- **Relevance**: Official EvalPlus benchmark — defines the API used by all h-e1 experiments
- **Key Code** (annotated):
  ```python
  from evalplus.data import get_human_eval_plus, get_mbpp_plus, write_jsonl
  # Returns dict {task_id: problem_dict}
  # problem_dict keys: task_id, entry_point, prompt, canonical_solution,
  #                    base_input, plus_input
  he_problems = get_human_eval_plus()
  mbpp_problems = get_mbpp_plus()
  ```
- **Used For**: Step 5 of verification script — checking all 134 task IDs exist in EvalPlus

**Repository 2**: axolotl-ai-cloud/grpo_code — eval_plus/convert_data.py
- **URL**: https://github.com/axolotl-ai-cloud/grpo_code/blob/main/eval_plus/convert_data.py
- **Query Used**: Same query
- **Relevance**: Production use of `get_human_eval_plus()` and `get_mbpp_plus()` with full dataset iteration
- **Key Code**:
  ```python
  humaneval_data = get_human_eval_plus()
  for obj in humaneval_data.values():
      inputs = obj["base_input"] + obj["plus_input"]
  ```
- **Used For**: Understanding `plus_input` structure for deterministic test selection

**Repository 3**: NVIDIA-NeMo/Gym — resources_servers/evalplus/app.py (⭐ 1K)
- **URL**: https://github.com/NVIDIA-NeMo/Gym/blob/main/resources_servers/evalplus/app.py
- **Query Used**: Same query
- **Relevance**: Shows production-grade loading with `get_groundtruth` and `check_correctness` — confirms EvalPlus API is stable
- **Configuration Extracted**: `version="default"` parameter for `get_human_eval_plus(version=version)`
- **Used For**: Confirming API stability, `get_human_eval_plus_hash` for versioning

**Issue #148**: evalplus/evalplus (determinism)
- **URL**: https://github.com/evalplus/evalplus/issues/148
- **Relevance**: Confirms `plus_fail_tests` ordering in eval_results is deterministic (PYTHONHASHSEED risk is in generation, not in stored outputs)
- **Used For**: Confirming first failing test is deterministically selectable from stored `plus_fail_tests[0]`

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. The stored eval_results JSON schema was confirmed by direct Python inspection of h-e1 Run 2 files.

### D. Previous Hypothesis Context

**Previous Context**: Cross-pipeline prior run (separate experiment, not a predecessor in THIS pipeline).

- **Source**: `.serena/memories/failure_h-e1_run2.md` + `.serena/memories/snapshot_h-e1_20260822.md`
- **Key data reused**:
  - Failure set: 34 HE+ + 100 MBPP+ = 134 confirmed ✅
  - Stored outputs: `plus_fail_tests` field present in eval_results ✅
  - EvalPlus API: accessible in prior run ✅
  - Archive path: `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results/`
- **Why relevant**: Prior run's failure CONFIRMED the data is valid and reusable — the static analysis oracle failed, not the data

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (134 failures) | Direct inspection | h-e1 Run 2 archive JSON files |
| HE+ count (34) | Python count | `humaneval_samples_eval_results.json` |
| MBPP+ count (100) | Python count | `mbpp_samples_eval_results.json` |
| JSON schema (`solution`, `plus_fail_tests`) | Direct inspection | h-e1 Run 2 eval_results |
| EvalPlus API (`get_human_eval_plus`) | GitHub Exa B.1 | evalplus/evalplus repo |
| Archive path | Serena memory | `.serena/memories/snapshot_h-e1_20260822.md` |
| Deterministic test ordering | GitHub Exa B.4 | evalplus/evalplus issue #148 |
| Verification script pattern | Exa B.1, B.2, B.3 | evalplus repos |
| Success criteria (counts) | Phase 2B | 02b_verification_plan.md H-E1 section |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state in pipeline context)
**Date:** 2026-08-22T00:00:00+00:00

### Workflow History for This Hypothesis
- 2026-08-22: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-22: Phase 2C Steps 1–8 executed (UNATTENDED mode)
- 2026-08-22: experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (3 KB queries + 1 code query — no relevant results), Exa (2 queries — 3+ repos found), Serena (skipped — not needed)*
*All specifications grounded in direct h-e1 Run 2 file inspection + EvalPlus official API*
*Next Phase: Phase 3 - Implementation Planning*
