# Logic: H-M2 Difficulty Tier Stratification — Cross-Model Jaccard Analysis

**Hypothesis:** h-m2
**Type:** MECHANISM (SHOULD_WORK gate)
**Date:** 2026-03-18

Applied: pipeline-orchestrator + domain-module pattern (from h-m1 verify_coverage.py style)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from base code (direct file reads; Serena project connection unavailable but filesystem reads succeeded)
**Analyzed Path:** `docs/youra_research/20260316_verifia/h-m1/code/src/h_m1/`
**Relevant Symbols:**
- `split_by_benchmark(pass_at_1: dict[str, float]) -> tuple[dict[str, float], dict[str, float]]`
- `compute_distribution_stats(pass_at_1: dict[str, float]) -> dict` — uses `np.isclose` for 6-bin histogram
- `MODEL_IDS`, `MODEL_SHORT_NAMES`, `BENCHMARK_PREFIXES`, `HIST_BINS` — constants in `verify_coverage.py`
- `save_verified_output()` — writes `{"metadata": {...}, "models": {hf_model_id: {task_id: float}}}` (CONFIRMED flat float)

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

Verified from `docs/youra_research/20260316_verifia/h-m1/code/src/h_m1/verify_coverage.py`

```python
# From: h-m1/code/src/h_m1/verify_coverage.py (ACTUAL CODE)

# Constants — copy-reference into h-m2/stratify.py
MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]
MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}
BENCHMARK_PREFIXES: dict[str, str] = {"HumanEval/": "humaneval", "Mbpp/": "mbpp"}
HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def split_by_benchmark(
    pass_at_1: dict[str, float],          # {task_id: float}
) -> tuple[dict[str, float], dict[str, float]]:
    """Returns: (he_dict, mbpp_dict) — splits on task_id prefix."""
    ...

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict:
    """Returns: {mean, std, min, max, histogram_6pt: {bin_str: count}, non_trivial: bool}
    Uses np.isclose for exact 6-point bin matching."""
    ...
```

**Verified JSON schema from `save_verified_output()` in `run_hm1_verification.py`:**
```python
# pass_at_1_hm1_verified.json — CONFIRMED schema
{
    "metadata": {
        "source": "h-e1",
        "verification_status": "PASS",
        "coverage_combined": {model_short: float},
        "timestamp": "<ISO-8601>"
    },
    "models": {
        "<hf_model_id>": {           # full HF ID (e.g. "NousResearch/Meta-Llama-3-8B")
            "<task_id>": float       # flat float — NOT a nested dict!
        }
    }
}
# h-m2 loader: data["models"][hf_model_id][task_id] = float
```

---

## A-3: Tier Stratification [Complexity: 9, Budget: 3 subtasks]

Applied: Standard Python dict/set operations

### API Signatures

```python
# h-m2/code/src/h_m2/stratify.py

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
HE_PREFIX: str = "HumanEval/"
MBPP_PREFIX: str = "Mbpp/"
HM1_VERIFIED_FILENAME: str = "pass_at_1_hm1_verified.json"

def load_hm1_pass_at_1(
    hm1_results_dir: Path,
) -> dict[str, dict[str, float]]:
    """Load pass_at_1_hm1_verified.json.
    Returns: {hf_model_id: {task_id: float}}
    Raises: FileNotFoundError, KeyError (missing 'models'), ValueError (< 3 models or < 500 tasks)
    """
    ...

def split_by_benchmark(
    pass_at_1: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Split task dict by prefix.
    Returns: (he_dict, mbpp_dict)
    Note: Replicates h-m1 logic exactly — copy implementation directly.
    """
    ...

def compute_difficulty_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, set]]:
    """Assign hard/easy/medium tiers per model on combined task set.
    Returns: {hf_model_id: {"hard": set[str], "easy": set[str], "medium": set[str]}}
    """
    ...

def compute_per_benchmark_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, dict[str, set]]]:
    """Compute tiers split by benchmark.
    Returns: {hf_model_id: {"humaneval": {"hard": set, "easy": set, "medium": set},
                             "mbpp":      {"hard": set, "easy": set, "medium": set}}}
    """
    ...

def validate_tier_sizes(
    tiers: dict[str, dict[str, set]],
    min_size: int = 20,
) -> dict[str, dict[str, bool]]:
    """Validate n_hard >= min_size and n_easy >= min_size per model.
    Returns: {hf_model_id: {"hard_ok": bool, "easy_ok": bool}}
    Note: CodeLlama n_easy on HumanEval may be 0 — expected, not an error.
    """
    ...
```

### Pseudo-code (compute_difficulty_tiers)

```
for each hf_model_id, task_scores in pass_at_1_data:
    hard = {tid for tid, v in task_scores.items() if v == hard_threshold}   # pass@1 == 0.0
    easy = {tid for tid, v in task_scores.items() if v >= easy_threshold}   # pass@1 >= 0.6
    medium = set(task_scores.keys()) - hard - easy                           # remainder
    tiers[hf_model_id] = {"hard": hard, "easy": easy, "medium": medium}
```

### Pseudo-code (compute_per_benchmark_tiers)

```
for each hf_model_id, task_scores in pass_at_1_data:
    he_scores, mbpp_scores = split_by_benchmark(task_scores)
    per_benchmark_tiers[hf_model_id] = {}
    for bench_name, scores in [("humaneval", he_scores), ("mbpp", mbpp_scores)]:
        hard = {tid for tid, v in scores.items() if v == hard_threshold}
        easy = {tid for tid, v in scores.items() if v >= easy_threshold}
        medium = set(scores.keys()) - hard - easy
        per_benchmark_tiers[hf_model_id][bench_name] = {"hard": hard, "easy": easy, "medium": medium}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_hm1_pass_at_1 | Read JSON, validate `data["models"]` key, check 3 model IDs, check >= 500 tasks per model |
| L-3-2 | compute_difficulty_tiers + compute_per_benchmark_tiers | Set assignment per threshold (hard/easy/medium), combined and per-benchmark variants |
| L-3-3 | validate_tier_sizes | Per-model size check, return bool dict; log warning for CodeLlama HumanEval n_easy=0 |

---

## A-4: Jaccard Module [Complexity: 10, Budget: 3 subtasks]

Applied: Standard Python set operations + itertools.combinations

### API Signatures

```python
# h-m2/code/src/h_m2/jaccard.py

import itertools

def jaccard_similarity(
    set_a: set,
    set_b: set,
) -> float:
    """Jaccard: |A ∩ B| / |A ∪ B|. Returns 0.0 if both empty."""
    ...

def compute_cross_model_jaccard(
    tiers: dict[str, dict[str, set]],    # {hf_model_id: {"hard": set, ...}}
    tier_name: str = "hard",
) -> dict[tuple[str, str], float]:
    """Compute Jaccard for all 3 model pairs on specified tier.
    Returns: {(model_a, model_b): float}  — 3 entries
    Pair order: sorted(model_ids) → consistent keys
    """
    ...

def compute_per_benchmark_jaccard(
    per_benchmark_tiers: dict[str, dict[str, dict[str, set]]],
    tier_name: str = "hard",
) -> dict[str, dict[tuple[str, str], float]]:
    """Per-benchmark Jaccard for all pairs.
    Returns: {"humaneval": {(a, b): float}, "mbpp": {(a, b): float}}
    """
    ...

def compute_overlap_matrix(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[tuple[str, str], dict[str, int | float]]:
    """Compute n_intersection, n_union, jaccard for all pairs.
    Returns: {(a, b): {"n_intersection": int, "n_union": int, "jaccard": float}}
    """
    ...

def compute_consensus_set(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[str, object]:
    """Consensus = intersection of all 3 model tier sets.
    Returns: {"task_ids": set[str], "n": int, "percentage": float}
    percentage = n / COMBINED_TOTAL (542)
    """
    ...

def compute_overlap_counts_by_n_models(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
    total_problems: int = 542,
) -> dict[int, int]:
    """Count problems in tier for exactly n models (n = 1, 2, 3).
    Returns: {1: count, 2: count, 3: count}
    """
    ...
```

### Pseudo-code (jaccard_similarity — edge cases)

```
def jaccard_similarity(set_a, set_b):
    union = set_a | set_b
    if not union:               # both empty → avoid ZeroDivisionError
        return 0.0
    intersection = set_a & set_b
    return len(intersection) / len(union)
```

### Pseudo-code (compute_cross_model_jaccard)

```
model_ids = sorted(tiers.keys())           # consistent ordering
for (a, b) in itertools.combinations(model_ids, 2):
    set_a = tiers[a][tier_name]
    set_b = tiers[b][tier_name]
    results[(a, b)] = jaccard_similarity(set_a, set_b)
# result has exactly 3 entries for 3 models
```

### Pseudo-code (compute_overlap_counts_by_n_models)

```
counts = {1: 0, 2: 0, 3: 0}
all_task_ids = union of all tier sets across all models
for task_id in all_task_ids:
    n = sum(1 for model_id in tiers if task_id in tiers[model_id][tier_name])
    if n >= 1:
        counts[n] += 1
return counts
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | jaccard_similarity + compute_cross_model_jaccard | Core Jaccard with empty-set edge case; all-pairs using itertools.combinations |
| L-4-2 | compute_per_benchmark_jaccard + compute_overlap_matrix | Benchmark-split pairs; matrix with raw n_intersection/n_union counts |
| L-4-3 | compute_consensus_set + compute_overlap_counts_by_n_models | Triple intersection and per-count grouping |

---

## A-5: Analysis Module [Complexity: 9, Budget: 3 subtasks]

Applied: Standard numpy histogram pattern (np.isclose for 6-point bins) from h-m1

### API Signatures

```python
# h-m2/code/src/h_m2/analyze.py

import numpy as np
import pandas as pd

HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # 6-point discrete from k=5

def compute_histograms(
    pass_at_1_data: dict[str, dict[str, float]],
    per_benchmark: bool = True,
) -> dict[str, dict[str, dict[str, int]]]:
    """Compute 6-point discrete histogram per model, optionally per benchmark.
    Returns: {hf_model_id: {"combined": {bin_str: count},
                             "humaneval": {bin_str: count},   # if per_benchmark=True
                             "mbpp":      {bin_str: count}}}  # if per_benchmark=True
    bin_str: str(bin_float) e.g. "0.0", "0.2", ..., "1.0"
    Uses np.isclose for exact float matching (mirrors h-m1 compute_distribution_stats)
    """
    ...

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict[str, float]:
    """Distribution stats + tier percentage breakdown.
    Returns: {"mean": float, "std": float, "min": float, "max": float,
              "pct_hard": float, "pct_easy": float, "pct_medium": float}
    pct_hard  = count(v == 0.0) / total
    pct_easy  = count(v >= 0.6) / total
    pct_medium = 1.0 - pct_hard - pct_easy
    """
    ...

def classify_distribution_shape(
    histogram: dict[str, int],
) -> str:
    """Classify shape from 6-point histogram.
    Returns: "bimodal" | "skewed_hard" | "skewed_easy" | "uniform" | "other"
    """
    ...

def build_tier_assignments_df(
    pass_at_1_data: dict[str, dict[str, float]],
    tiers: dict[str, dict[str, set]],     # {hf_model_id: {"hard": set, "easy": set, "medium": set}}
) -> pd.DataFrame:
    """Build tier_assignments.csv dataframe.
    Columns: task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier,
             n_models_hard, n_models_easy
    benchmark: "humaneval" if task_id.startswith("HumanEval/") else "mbpp"
    *_tier: "hard" | "easy" | "medium" (per-model lookup from tiers sets)
    n_models_hard: count of models with task_id in hard set
    n_models_easy: count of models with task_id in easy set
    """
    ...
```

### Pseudo-code (compute_histograms — 6-point bins)

```
arr = np.array(list(pass_at_1.values()), dtype=float)
histogram = {}
for b in HIST_BINS:             # [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    histogram[str(b)] = int(np.sum(np.isclose(arr, b)))
# np.isclose handles float precision (e.g. 0.19999... == 0.2)
```

### Pseudo-code (classify_distribution_shape)

```
counts = [histogram[str(b)] for b in HIST_BINS]
hard_count  = counts[0]   # bin 0.0
easy_counts = counts[3:]  # bins 0.6, 0.8, 1.0
mid_counts  = counts[1:3] # bins 0.2, 0.4

total = sum(counts)
if total == 0: return "other"

# bimodal: high mass at both ends (hard + easy), low in middle
if hard_count / total > 0.2 and sum(easy_counts) / total > 0.2 and sum(mid_counts) / total < 0.3:
    return "bimodal"
# skewed_hard: majority in hard bin
if hard_count / total > 0.5:
    return "skewed_hard"
# skewed_easy: majority in easy bins
if sum(easy_counts) / total > 0.5:
    return "skewed_easy"
# uniform: no bin exceeds 30%
if max(counts) / total < 0.3:
    return "uniform"
return "other"
```

### Pseudo-code (build_tier_assignments_df)

```
all_task_ids = union of all task_ids across all models in pass_at_1_data
model_ids = [llama3_id, codellama_id, deepseek_id]  # fixed order from MODEL_IDS
short_names = ["llama3_tier", "codellama_tier", "deepseek_tier"]

rows = []
for task_id in sorted(all_task_ids):
    benchmark = "humaneval" if task_id.startswith("HumanEval/") else "mbpp"
    row = {"task_id": task_id, "benchmark": benchmark}
    n_hard = 0; n_easy = 0
    for model_id, col_name in zip(model_ids, short_names):
        t = tiers.get(model_id, {})
        if task_id in t.get("hard", set()):
            row[col_name] = "hard"; n_hard += 1
        elif task_id in t.get("easy", set()):
            row[col_name] = "easy"; n_easy += 1
        else:
            row[col_name] = "medium"
    row["n_models_hard"] = n_hard
    row["n_models_easy"] = n_easy
    rows.append(row)
return pd.DataFrame(rows)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_histograms | 6-point discrete bins using np.isclose; combined + per-benchmark split |
| L-5-2 | compute_distribution_stats + classify_distribution_shape | numpy stats + tier pct breakdown; threshold-based shape classifier |
| L-5-3 | build_tier_assignments_df | Per-task tier lookup from 3 model sets → pandas DataFrame with 7 columns |

---

## Implementation Notes

1. **JSON loader key order:** `data["models"][hf_model_id][task_id] = float` — confirmed flat float from `save_verified_output()`.
2. **Model IDs as dict keys:** Use full HF IDs (e.g. `"NousResearch/Meta-Llama-3-8B"`), not short names. Reuse `MODEL_IDS` / `MODEL_SHORT_NAMES` from h-m1 (copy-reference, no runtime import).
3. **np.isclose for histogram bins:** Pass@1 values from k=5 trials are exact multiples of 0.2, but float arithmetic may drift. Use `np.isclose` (mirrors h-m1 `compute_distribution_stats`).
4. **Pair key ordering:** Always use `sorted(model_ids)` before `itertools.combinations` to guarantee deterministic tuple keys in result dicts.
5. **No GPU, no random state** — all operations are pure set/dict/numpy. No seeding needed.
6. **PYTHONPATH:** `h-m2/code/src` only. No h-m1 runtime imports in production code.

---

*Logic generated: 2026-03-18*
*Base hypothesis code verified: h-m1/code/src/h_m1/verify_coverage.py, run_hm1_verification.py*
