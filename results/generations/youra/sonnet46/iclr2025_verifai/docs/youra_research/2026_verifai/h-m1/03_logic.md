# Logic: H-M1 Pass@1 Coverage Verification

Applied: incremental-extension pattern (reuse h-e1 modules, wrap in h_m1 package)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)
**Status**: API signatures verified from actual code (Read tool fallback — Serena project activation error)
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-e1/code/src/h_e1/`
**Relevant Symbols**:
- `evaluate_solutions.py`: `evaluate_all_solutions(solutions, problems_he, problems_mbpp, output_dir, model_short)`, `save_correctness(correctness, output_path)`, `MODEL_SHORT_NAMES`, `load_solutions_jsonl(path)`
- `analyze_tiers.py`: `compute_pass_at_1(correctness, k=5)`, `save_pass_at_1(pass_at_1, output_path)`

---

## External Dependencies API (Base Hypothesis)

Signatures verified from actual h-e1 code (NOT spec):

```python
# From: h-e1/code/src/h_e1/evaluate_solutions.py (ACTUAL CODE)

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

def evaluate_all_solutions(
    solutions: dict,          # {task_id: [str × k]}
    problems_he: dict,
    problems_mbpp: dict,
    output_dir: str,
    model_short: str = "model",
) -> dict:                    # Returns {task_id: [bool × k]}
    ...

def save_correctness(correctness: dict, output_path: str) -> None: ...
def load_solutions_jsonl(path: str) -> dict: ...  # {task_id: [str × k]}

# From: h-e1/code/src/h_e1/analyze_tiers.py (ACTUAL CODE)

def compute_pass_at_1(
    correctness: dict[str, list[bool]],
    k: int = 5,
) -> dict[str, float]:        # Returns {task_id: float} in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
    ...

def save_pass_at_1(pass_at_1: dict, output_path: str) -> None: ...
```

**Verified from**: `h-e1/code/src/h_e1/` (actual implementation)

---

## A-9: Fallback Path [Complexity: 12, Budget: 4 subtasks]

Applied: Standard Python pathlib + conditional recompute pattern

### API Signatures

```python
# src/h_m1/verify_coverage.py

def _check_file_integrity(
    h_e1_results_dir: Path,
    model_short: str,
) -> dict[str, bool]:
    """Check which result files exist for a model.
    Returns: {"pass_at_1": bool, "correctness": bool, "solutions": bool}
    """
    ...

def load_or_recompute_pass_at_1(
    h_e1_results_dir: Path,
    model_short: str,
    force_regenerate: bool = False,
) -> dict[str, float]:
    """Load pass_at_1 from file or recompute from correctness/solutions.
    Returns: {task_id: float}  # empty dict if all files missing
    Raises: FileNotFoundError if force_regenerate=False and solutions also missing
    """
    ...
```

### Pseudo-code: load_or_recompute_pass_at_1

```
p1_path = h_e1_results_dir / f"pass_at_1_{model_short}.json"
corr_path = h_e1_results_dir / f"correctness_{model_short}.json"
sol_path  = h_e1_results_dir / f"solutions_{model_short}.jsonl"

integrity = _check_file_integrity(h_e1_results_dir, model_short)

PATH 1 — primary: pass_at_1 file exists
  data = json.load(p1_path)
  if len(data) > 0:
      return data

PATH 2 — fallback A: correctness file exists
  correctness = json.load(corr_path)
  pass_at_1 = {tid: sum(v)/len(v) for tid, v in correctness.items()}
  return pass_at_1  # recomputed, no GPU needed

PATH 3 — fallback B: solutions JSONL exists
  log "FALLBACK: rerunning evaluate_solutions for {model_short}"
  solutions = h_e1.evaluate_solutions.load_solutions_jsonl(sol_path)
  problems_he = get_human_eval_plus()
  problems_mbpp = get_mbpp_plus()
  correctness = h_e1.evaluate_solutions.evaluate_all_solutions(
      solutions, problems_he, problems_mbpp, str(h_e1_results_dir), model_short
  )
  pass_at_1 = h_e1.analyze_tiers.compute_pass_at_1(correctness)
  return pass_at_1

PATH 4 — all missing, force_regenerate=False
  raise FileNotFoundError(f"No result files for {model_short}. Use --force_regenerate.")

PATH 5 — force_regenerate=True (scope boundary)
  raise NotImplementedError("Solution regeneration (k=5 generation) not in h-m1 scope.")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A9-1 | `_check_file_integrity` | Check pass_at_1/correctness/solutions file existence; return status dict |
| L-A9-2 | `load_or_recompute_pass_at_1` PATH 1-2 | Load primary + correctness fallback (CPU only) |
| L-A9-3 | `load_or_recompute_pass_at_1` PATH 3 | Solutions JSONL fallback → call evaluate_all_solutions |
| L-A9-4 | Force-regenerate guard | Raise NotImplementedError for --force_regenerate; error messages |

---

## A-5: Save Outputs [Complexity: 11, Budget: 2 subtasks]

Applied: Standard json.dump + csv.DictWriter pattern

### API Signatures

```python
# src/h_m1/run_hm1_verification.py

def save_verified_output(
    pass_at_1_by_model: dict[str, dict[str, float]],  # {hf_model_id: {task_id: float}}
    coverage_data: dict[str, dict[str, float]],        # {model_short: {"humaneval": f, "mbpp": f, "combined": f}}
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write pass_at_1_hm1_verified.json. Schema matches FR-5.1."""
    ...

def save_coverage_report(
    coverage_data: dict[str, dict[str, float]],        # {model_short: {"humaneval": f, "mbpp": f, "combined": f}}
    stats_by_model: dict[str, dict],                   # {model_short: {mean, std, min, max, histogram_6pt, non_trivial}}
    gate_results: dict,                                # {model_short: {"gate_pass": bool, "checks": list[str]}}
    output_dir: Path,
) -> None:
    """Write coverage_report.json and coverage_report.csv."""
    ...
```

### A-5-1: save_verified_output JSON Schema

```json
{
  "metadata": {
    "source": "h-e1",
    "verification_status": "PASS",
    "coverage_combined": {
      "llama3_8b": 1.0,
      "codellama_7b": 1.0,
      "deepseek_6.7b": 1.0
    },
    "timestamp": "<ISO-8601 from datetime.utcnow().isoformat()>"
  },
  "models": {
    "NousResearch/Meta-Llama-3-8B": {"HumanEval/0": 0.4, "Mbpp/2": 0.8, "...": "..."},
    "codellama/CodeLlama-7b-hf": {},
    "deepseek-ai/deepseek-coder-6.7b-base": {}
  }
}
```

Key: `coverage_combined` uses short names (llama3_8b etc.), `models` uses HF model IDs as keys.

### A-5-2: save_coverage_report Dual Format

**coverage_report.json** structure:
```json
{
  "timestamp": "<ISO-8601>",
  "models": {
    "llama3_8b": {
      "coverage": {"humaneval": 1.0, "mbpp": 1.0, "combined": 1.0},
      "stats": {"mean": 0.51, "std": 0.35, "min": 0.0, "max": 1.0,
                "histogram_6pt": {"0.0": 60, "0.2": 20, "0.4": 15, "0.6": 10, "0.8": 30, "1.0": 9},
                "non_trivial": true},
      "gate": {"gate_pass": true, "checks": ["coverage=1.0000 >= 0.95: PASS", "..."]}
    }
  },
  "overall_gate_pass": true
}
```

**coverage_report.csv** columns:
```
model,benchmark,coverage,mean,std,min,max,gate_pass
llama3_8b,humaneval,1.0,0.51,0.35,0.0,1.0,True
llama3_8b,mbpp,1.0,0.48,0.37,0.0,1.0,True
llama3_8b,combined,1.0,,,,,True
...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A5-1 | `save_verified_output` | FR-5.1 JSON with metadata + models dict; timestamp via datetime.utcnow().isoformat() |
| L-A5-2 | `save_coverage_report` | JSON full report + CSV with 3 rows per model (he/mbpp/combined) |

---

## A-3: Stats + Gate [Complexity: 10, Budget: 2 subtasks]

Applied: Standard numpy stats + counter pattern

### API Signatures

```python
# src/h_m1/verify_coverage.py

HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict:
    """Compute distribution stats over pass@1 values.
    Returns: {
        "mean": float, "std": float, "min": float, "max": float,
        "histogram_6pt": {"0.0": int, "0.2": int, ..., "1.0": int},
        "non_trivial": bool  # std > 0 AND >= 3 non-zero buckets
    }
    Edge case: empty dict → all zeros, non_trivial=False
    Edge case: all same value → std=0, non_trivial=False
    """
    ...

def verify_gate(
    coverage_data: dict[str, dict[str, float]],  # {model_short: {"combined": float, ...}}
    stats_by_model: dict[str, dict],              # {model_short: {std, non_trivial, ...}}
) -> tuple[bool, dict[str, dict]]:
    """Check gate per model, aggregate to overall.
    Returns: (overall_gate_pass: bool, per_model_results: dict)
    per_model_results: {model_short: {"gate_pass": bool, "checks": list[str], "partial": bool}}
    PARTIAL: coverage >= 0.95 but std == 0, or vice versa
    """
    ...
```

### Pseudo-code: compute_distribution_stats

```
values = list(pass_at_1.values())
if not values:
    return {mean:0, std:0, min:0, max:0, histogram_6pt: all zeros, non_trivial: False}

arr = np.array(values, dtype=float)
mean, std = float(np.mean(arr)), float(np.std(arr))
min_val, max_val = float(np.min(arr)), float(np.max(arr))

histogram_6pt = {}
for b in HIST_BINS:
    histogram_6pt[str(b)] = int(np.sum(np.isclose(arr, b)))

non_zero_buckets = sum(1 for v in histogram_6pt.values() if v > 0)
non_trivial = (std > 0) and (non_zero_buckets >= 3)

return {mean, std, min_val, max_val, histogram_6pt, non_trivial}
```

### Pseudo-code: verify_gate

```
per_model_results = {}
for model_short in MODEL_SHORT_NAMES.values():
    cov = coverage_data[model_short]["combined"]
    std = stats_by_model[model_short]["std"]

    cov_ok = cov >= COVERAGE_GATE        # 0.95
    std_ok = std > 0

    gate_pass = cov_ok and std_ok
    checks = [
        f"coverage={cov:.4f} >= 0.95: {'PASS' if cov_ok else 'FAIL'}",
        f"non_trivial (std={std:.4f} > 0): {'PASS' if std_ok else 'FAIL'}"
    ]
    per_model_results[model_short] = {
        "gate_pass": gate_pass,
        "checks": checks,
        "partial": (cov_ok != std_ok),  # exactly one condition failed
    }

n_pass = sum(1 for r in per_model_results.values() if r["gate_pass"])
n_partial = sum(1 for r in per_model_results.values() if r["partial"])

# PARTIAL condition: 2/3 models pass full gate
if n_pass == 3:
    overall = True
elif n_pass >= 2:
    overall = False  # still FAIL, but log WARN "PARTIAL: 2/3 models pass"
else:
    overall = False

return overall, per_model_results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | `compute_distribution_stats` | 6-bin histogram via np.isclose; non_trivial = std>0 AND >=3 non-zero bins |
| L-A3-2 | `verify_gate` | Per-model gate check; PARTIAL log when 2/3 pass; return (bool, per_model_dict) |

---

## A-8: Smoke Test + Gate Output [Complexity: 10, Budget: 2 subtasks]

Applied: subset-slice pattern for smoke test; sys.exit for CLI gate result

### API Signatures

```python
# src/h_m1/verify_coverage.py

def run_verification(
    h_e1_results_dir: Path,
    output_dir: Path,
    smoke_test: bool = False,
    force_regenerate: bool = False,
) -> dict:
    """Orchestrate full pipeline. Returns structured results dict."""
    ...

# src/h_m1/run_hm1_verification.py

def format_gate_output(
    overall_gate_pass: bool,
    per_model_results: dict[str, dict],
    coverage_data: dict[str, dict[str, float]],
) -> str:
    """Format gate result for stdout. Returns printable string."""
    ...

def main() -> None:
    """Entry point. Calls sys.exit(0) on PASS, sys.exit(1) on FAIL."""
    ...
```

### A-8-1: Smoke Test Subset Selection

```
if smoke_test:
    # Take first 10 HumanEval/ task_ids + first 10 Mbpp/ task_ids per model
    for model_short, p1 in pass_at_1_by_model.items():
        he_keys = sorted(k for k in p1 if k.startswith("HumanEval/"))[:10]
        mbpp_keys = sorted(k for k in p1 if k.startswith("Mbpp/"))[:10]
        pass_at_1_by_model[model_short] = {k: p1[k] for k in he_keys + mbpp_keys}
    # State isolation: smoke results are NOT written to output_dir
    # Run all downstream logic (split, stats, gate) on subset
    # Assert: gate result dict has all required keys (gate_pass, per_model_results)
```

### A-8-2: Gate Output Format + Exit Codes

```
stdout format:
  === H-M1 Gate Result ===
  Overall: PASS | FAIL
  Models:
    llama3_8b: PASS | FAIL (coverage=1.0000, std=0.3512)
    codellama_7b: PASS | FAIL (coverage=1.0000, std=0.3201)
    deepseek_6.7b: PASS | FAIL (coverage=1.0000, std=0.3398)
  [WARN: PARTIAL - 2/3 models pass gate]  # only if partial
  Output: {output_dir}/pass_at_1_hm1_verified.json

exit codes:
  sys.exit(0)  → gate PASS
  sys.exit(1)  → gate FAIL or PARTIAL
  sys.exit(2)  → runtime error (file missing, exception)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A8-1 | Smoke test subset + state isolation | Slice 10 HE + 10 MBPP per model; no file writes; assert gate-checkable |
| L-A8-2 | `format_gate_output` + `main` exit codes | Structured stdout; sys.exit(0/1/2) convention |

---

## Subtask Budget Summary

| Task | Subtasks Used | Subtask Budget |
|------|--------------|----------------|
| A-9 (Fallback) | 4 | 4 |
| A-5 (Save outputs) | 2 | 2 |
| A-3 (Stats + Gate) | 2 | 2 |
| A-8 (Smoke + output) | 2 | 2 |
| **Total** | **10** | **8 (allocated) + 2 overflow** |

Note: A-9 used 4 subtasks vs the 2-task default due to complexity=12 (3 distinct fallback paths + guard).
Recommend merging L-A9-2 and L-A9-3 into single subtask if budget is strict.
