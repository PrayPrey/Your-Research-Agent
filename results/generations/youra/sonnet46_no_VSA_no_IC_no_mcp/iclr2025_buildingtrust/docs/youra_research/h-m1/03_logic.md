---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-25"
author: Anonymous
---

# Logic: H-M1

Applied: stratified-subset ECE pattern (Guo 2017)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `compute_ece(confidences, correct, n_bins=15) -> float` — `evaluation/ece.py:4`
- `write_json(path, data) -> None` — `results/storage.py:42`
- `write_gate_result(path, passed_cells, failed_cells, clean_sanity, gate_passed, summary) -> None` — `results/storage.py:29`
- `load_all_datasets(seed, subsample_clean, subsample_adv) -> dict` — `data/loader.py:14`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/evaluation/ece.py (ACTUAL CODE)
def compute_ece(
    confidences: np.ndarray,  # (N,) float32
    correct: np.ndarray,      # (N,) int {0,1}
    n_bins: int = 15
) -> float: ...

# From: docs/youra_research/h-e1/code/results/storage.py (ACTUAL CODE)
def write_json(path: str, data) -> None: ...

def write_gate_result(
    path: str,
    passed_cells: int,
    failed_cells: list,
    clean_sanity: bool,
    gate_passed: bool = None,
    summary: dict = None
) -> None: ...

# From: docs/youra_research/h-e1/code/data/loader.py (ACTUAL CODE)
def load_all_datasets(
    seed: int = 1,
    subsample_clean: int = 500,
    subsample_adv: int = 500
) -> dict: ...  # keys: "advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli", etc.
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: `write_gate_result` uses `passed_cells: int` and `failed_cells: list` — H-M1 maps
gate indicators to these fields as `passed_cells=int(gate_passed)` and `failed_cells=[]` on pass.

---

## A-5: ECEAnalyzer [Complexity: 11, Budget: 5 subtasks]

Applied: Standard PyTorch / numpy ECE pattern

### API Signatures

```python
# code/ece_analyzer.py
import numpy as np
from typing import Optional

def compute_stratum_ece(
    cache: dict,            # {"conf": (N,) float32, "correct": (N,) int, ...}
    mask: np.ndarray,       # (N,) bool — high-preservation stratum selector
    n_bins: int = 15
) -> float:
    """ECE for masked subset. Returns scalar ECE."""
    ...

def compute_delta_ece(
    stratum_ece: float,
    clean_ece: float        # default: CLEAN_ECE_H_E1 = 0.279
) -> float:
    """ΔECE = stratum_ece - clean_ece. Positive = calibration gap."""
    ...

def run_all_strata(
    caches: dict[str, dict],  # {split_name: {"conf": (N,), "correct": (N,), ...}}
    clean_ece: float = 0.279,
    n_bins: int = 15
) -> dict[str, dict]:
    """Per-split ECE + ΔECE. Returns {split: {"ece": float, "delta_ece": float, "n": int}}."""
    ...

def check_anli_gradient(
    stratum_results: dict[str, dict]  # output of run_all_strata
) -> bool:
    """Returns True if ΔECE(anli_r3) >= ΔECE(anli_r2) >= ΔECE(anli_r1)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `cache["conf"]` | `(N,)` float32 | max softmax confidence per example |
| `cache["correct"]` | `(N,)` int {0,1} | 1=correct prediction |
| `mask` | `(N,)` bool | stratum selector; `mask.sum()` = stratum size |
| `conf[mask]` | `(M,)` float32 | M = number of examples in stratum |

### Pseudo-code

**compute_stratum_ece:**
```
1. conf = cache["conf"][mask]      # (M,)
2. correct = cache["correct"][mask] # (M,)
3. if len(conf) == 0: raise ValueError("Empty stratum")
4. return compute_ece(conf, correct, n_bins)  # h-e1 import
```

**run_all_strata:**
```
1. results = {}
2. for split, cache in caches.items():
     a. mask = np.ones(len(cache["conf"]), dtype=bool)  # full split = stratum
     b. ece = compute_stratum_ece(cache, mask, n_bins)
     c. delta = compute_delta_ece(ece, clean_ece)
     d. results[split] = {"ece": ece, "delta_ece": delta, "n": int(mask.sum())}
3. return results
```

**check_anli_gradient:**
```
1. r1 = stratum_results.get("anli_r1", {}).get("delta_ece", None)
2. r2 = stratum_results.get("anli_r2", {}).get("delta_ece", None)
3. r3 = stratum_results.get("anli_r3", {}).get("delta_ece", None)
4. if any(x is None for x in [r1, r2, r3]): return False
5. return r3 >= r2 >= r1
```

### Subtasks [5/5 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-5-1 | compute_stratum_ece | Apply mask, delegate to h-e1 compute_ece | A-5 |
| L-5-2 | compute_delta_ece | Scalar subtraction + sign check | A-5 |
| L-5-3 | run_all_strata | Loop over splits, collect results dict | A-5 |
| L-5-4 | check_anli_gradient | Direction check R1 <= R2 <= R3 | A-5 |
| L-5-5 | Error handling | Empty mask, missing split key → ValueError/KeyError with message | A-5 |

---

## A-5 (cont.): ΔECE Computation Logic

### How ΔECE is computed per stratum vs clean baseline

```
ΔECE_stratum = ECE_stratum − ECE_clean_baseline

Where:
  ECE_clean_baseline = CLEAN_ECE_H_E1 = 0.279  (measured in H-E1 on GLUE MNLI, N=2000)
  ECE_stratum        = compute_stratum_ece(cache[split], mask=all_ones, n_bins=15)

For each split:
  - "advglue_mnli" → ΔECE = ECE_advglue − 0.279
  - "anli_r1"      → ΔECE = ECE_anli_r1 − 0.279
  - "anli_r2"      → ΔECE = ECE_anli_r2 − 0.279
  - "anli_r3"      → ΔECE = ECE_anli_r3 − 0.279
  - "mnli"         → ΔECE = 0.0  (this IS the clean baseline, sanity check)

Gate condition: ΔECE_advglue_mnli > 0  (primary gate)
Direction check: ΔECE_r3 >= ΔECE_r2 >= ΔECE_r1  (non-gate, logged only)
```

---

## A-6: Ablations [Complexity: 13, Budget: 5 subtasks]

Applied: Standard PyTorch / numpy

### API Signatures

```python
# code/ablations.py
import numpy as np

def ablation_criterion_sensitivity(
    caches: dict[str, dict],  # {split: {"conf": (N,), "correct": (N,), ...}}
    clean_ece: float = 0.279,
    n_bins: int = 15
) -> dict[str, float]:
    """
    Returns {"variant_A": delta_ece, "variant_B": delta_ece,
             "variant_C_r1": delta_ece, "variant_C_r2": delta_ece, "variant_C_r3": delta_ece}
    """
    ...

def ablation_bin_count(
    cache: dict,              # single split cache {"conf": (N,), "correct": (N,)}
    mask: np.ndarray,         # (N,) bool — high-preservation stratum
    bin_counts: tuple = (10, 15, 20),
    clean_eces: dict = None   # {n_bins: clean_ece} if different per bin count
) -> dict[int, float]:
    """Returns {10: ece, 15: ece, 20: ece} for the masked stratum."""
    ...

def ablation_task_scope(
    caches: dict[str, dict],  # must contain "advglue_mnli", "mnli", optionally qqp/sst2 splits
    clean_ece: float = 0.279,
    n_bins: int = 15
) -> dict[str, dict]:
    """
    Returns {"nli_only": {"ece": float, "delta_ece": float},
             "nli_qqp_sst2": {"ece": float, "delta_ece": float}}
    """
    ...
```

### Pseudo-code

**ablation_criterion_sensitivity:**
```
Variant A — all examples, no stratification:
  1. pool_conf = np.concatenate([cache["conf"] for cache in caches.values() if cache])
  2. pool_correct = np.concatenate([cache["correct"] for cache in caches.values() if cache])
  3. variant_A_delta = compute_ece(pool_conf, pool_correct, n_bins) - clean_ece

Variant B — AdvGLUE MNLI only:
  4. cache_b = caches["advglue_mnli"]
  5. variant_B_delta = compute_ece(cache_b["conf"], cache_b["correct"], n_bins) - clean_ece

Variant C — ANLI per-round:
  6. for r in [1, 2, 3]:
       cache_r = caches[f"anli_r{r}"]
       variant_C_r{r}_delta = compute_ece(cache_r["conf"], cache_r["correct"], n_bins) - clean_ece

7. return {"variant_A": A_delta, "variant_B": B_delta,
           "variant_C_r1": C_r1_delta, "variant_C_r2": C_r2_delta, "variant_C_r3": C_r3_delta}
```

**ablation_bin_count:**
```
1. conf = cache["conf"][mask]      # (M,)
2. correct = cache["correct"][mask] # (M,)
3. return {b: compute_ece(conf, correct, b) for b in bin_counts}
```

**ablation_task_scope:**
```
NLI only:
  1. nli_splits = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]
  2. pool conf + correct from nli_splits (skip None)
  3. nli_ece = compute_ece(pool_conf, pool_correct, n_bins)
  4. nli_delta = nli_ece - clean_ece

NLI + QQP + SST-2:
  5. all_splits = nli_splits + ["advglue_qqp", "advglue_sst2"]
  6. pool conf + correct from all_splits (skip None — qqp/sst2 may be absent)
  7. all_ece = compute_ece(pool_conf, pool_correct, n_bins)
  8. all_delta = all_ece - clean_ece

9. return {"nli_only": {"ece": nli_ece, "delta_ece": nli_delta},
           "nli_qqp_sst2": {"ece": all_ece, "delta_ece": all_delta}}
```

### Subtasks [5/5 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-6-1 | ablation_criterion_sensitivity variant A | Pooled unstratified ΔECE | A-6 |
| L-6-2 | ablation_criterion_sensitivity variants B+C | AdvGLUE-only + ANLI per-round | A-6 |
| L-6-3 | ablation_bin_count | ECE over {10,15,20} bins, masked stratum | A-6 |
| L-6-4 | ablation_task_scope | NLI-only vs NLI+QQP+SST-2 pooling | A-6 |
| L-6-5 | None-safety | Skip missing splits (None) in all pooling loops | A-6 |

---

## A-10: Integration [Complexity: 10, Budget: 5 subtasks]

Applied: Standard PyTorch / numpy

### API Signatures

```python
# code/run_analysis.py
import sys
from pathlib import Path

def main() -> None:
    """End-to-end orchestration. Exits 1 on gate FAIL with PIVOT log."""
    ...
```

### Pseudo-code — Exact Call Order

```
def main():
    # 1. Setup paths + h-e1 import injection
    sys.path.insert(0, H_E1_CODE_PATH)
    from evaluation.ece import compute_ece          # verify import or raise ImportError
    from results.storage import write_json, write_gate_result

    # 2. Load H-E1 caches
    try:
        caches = load_all_caches(H_E1_RESULTS_DIR, SPLITS)
    except FileNotFoundError as e:
        print(f"[FALLBACK] Cache missing: {e}. Re-run H-E1 first.")
        sys.exit(1)                                 # no auto re-run in H-M1

    # 3. Verify cache integrity
    verify_cache_integrity(caches, expected_counts={
        "advglue_mnli": 1200, "anli_r1": 1000,
        "anli_r2": 1000, "anli_r3": 1000, "mnli": 2000
    })                                              # logs warnings, does not raise

    # 4. Build strata + preservation rates
    strata = {}
    preservation_rates = {}
    for split, cache in caches.items():
        n = len(cache["conf"])
        strata[split] = build_strata(split, n)
        preservation_rates[split] = compute_preservation_rate(strata[split])
        print(f"[{split}] preservation_rate={preservation_rates[split]:.3f} n={n}")

    # 5. ECE analysis
    stratum_results = run_all_strata(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)
    gradient_ok = check_anli_gradient(stratum_results)
    print(f"ANLI gradient check: {gradient_ok}")

    # 6. Ablations
    abl_criterion = ablation_criterion_sensitivity(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)
    abl_bins = ablation_bin_count(
        caches["advglue_mnli"],
        mask=strata["advglue_mnli"]["high_pres_all"],
        bin_counts=(10, 15, 20)
    )
    abl_scope = ablation_task_scope(caches, clean_ece=CLEAN_ECE_H_E1, n_bins=N_BINS)

    # 7. Gate verification
    pres_rate = preservation_rates.get("advglue_mnli", 0.0)
    adv_ece = stratum_results["advglue_mnli"]["ece"]
    gate_passed, indicators = verify_gate(
        preservation_rate=pres_rate,
        stratum_ece=adv_ece,
        clean_ece=CLEAN_ECE_H_E1,
        h_e1_delta=DELTA_ECE_H_E1
    )

    if not gate_passed:
        print("[PIVOT] Gate FAIL — restricting ΔECE claim to AdvGLUE human-verified subset only")

    # 8. Write gate report (mapped to h-e1 write_gate_result signature)
    write_gate_report(passed=gate_passed, indicators=indicators, out_dir=RESULTS_DIR)

    # 9. Visualizations
    plot_preservation_rate(preservation_rates, out_path=f"{FIGURES_DIR}/preservation_rate_by_benchmark.png")
    plot_stratum_ece(stratum_results, out_path=f"{FIGURES_DIR}/stratum_ece_comparison.png")
    plot_anli_gradient(stratum_results, out_path=f"{FIGURES_DIR}/anli_gradient.png")
    plot_reliability_diagrams(caches, strata, out_path=f"{FIGURES_DIR}/reliability_diagrams.png")

    # 10. Write results
    write_main_results(stratum_results, out_dir=RESULTS_DIR)
    write_ablation_results(
        {"criterion": abl_criterion, "bin_count": abl_bins, "task_scope": abl_scope},
        out_dir=RESULTS_DIR
    )
    print("[DONE] H-M1 analysis complete.")
```

### Error Handling Summary

| Error | Source | Handler |
|-------|--------|---------|
| `FileNotFoundError` | `load_all_caches` | Print fallback message, `sys.exit(1)` |
| `ImportError` | h-e1 sys.path inject | Bubble up with message "Check H_E1_CODE_PATH" |
| `ValueError("Empty stratum")` | `compute_stratum_ece` | Logged, skip that split in results |
| `KeyError` (missing split) | `ablation_*` | Skip None caches with warning |
| Count mismatch | `verify_cache_integrity` | `logging.warning`, no raise |

### Subtasks [5/5 used]

| ID | Subtask | Description | Epic |
|----|---------|-------------|------|
| L-10-1 | sys.path inject + import verify | h-e1 ImportError guard at startup | A-10 |
| L-10-2 | Cache load + integrity | Steps 2-3, FileNotFoundError → exit(1) | A-10 |
| L-10-3 | Strata + ECE loop | Steps 4-5, collect preservation_rates + stratum_results | A-10 |
| L-10-4 | Ablations + gate | Steps 6-8, write gate report | A-10 |
| L-10-5 | Viz + results write | Steps 9-10, all four plots + three JSON files | A-10 |
