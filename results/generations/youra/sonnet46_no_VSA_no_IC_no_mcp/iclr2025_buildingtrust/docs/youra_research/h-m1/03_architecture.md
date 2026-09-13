---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-25"
author: Anonymous
---

# Architecture: H-M1

Applied: stratified-subset ECE pattern (Guo 2017 / construction-guarantee stratification)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `evaluation/ece.py` exports `compute_ece(confidences, correct, n_bins=15) -> float` and `compute_both()`. `results/storage.py` exports `write_json`, `write_gate_result`, `write_cell_jsonl`. `data/loader.py` exports `load_all_datasets(seed, subsample_clean, subsample_adv)` returning dict keyed by split name (`"advglue_mnli"`, `"anli_r1"`, `"mnli"`, etc.).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_ece | `sys.path.insert(0, h_e1_code); from evaluation.ece import compute_ece` | `h-e1/code/evaluation/ece.py` |
| write_json | `from results.storage import write_json, write_gate_result` | `h-e1/code/results/storage.py` |
| load_all_datasets | `from data.loader import load_all_datasets` | `h-e1/code/data/loader.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Structure

- `docs/youra_research/h-m1/code/`
  - `config.py` — paths, constants, seed
  - `cache_loader.py` — load H-E1 per-example JSONL outputs
  - `dataset_meta.py` — HuggingFace dataset metadata loader
  - `stratifier.py` — assign examples to preservation strata
  - `ece_analyzer.py` — per-stratum ECE + ΔECE computation
  - `ablations.py` — 3 ablation variants
  - `gate_verifier.py` — preservation_rate + ΔECE gate check
  - `visualizer.py` — bar charts, reliability diagrams
  - `results_writer.py` — JSON output + summary
  - `run_analysis.py` — entry point

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
H_E1_CODE_PATH: str = "docs/youra_research/h-e1/code"
H_E1_RESULTS_DIR: str = "docs/youra_research/h-e1/results"
RESULTS_DIR: str = "docs/youra_research/h-m1/results"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"
SEED: int = 1
N_BINS: int = 15
CLEAN_ECE_H_E1: float = 0.279   # measured in H-E1
DELTA_ECE_H_E1: float = 0.071   # H-E1 overall NLI delta
PRESERVE_RATE_GATE: float = 0.80
SUBSAMPLE_CLEAN: int = 2000
SPLITS: list = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3", "mnli"]
```

---

### CacheLoader (`code/cache_loader.py`)

**Dependencies**: Config

```python
import numpy as np

def load_split_cache(split: str, results_dir: str) -> dict:
    """
    Load H-E1 per-example JSONL for one split.
    Returns {"conf": np.ndarray, "correct": np.ndarray,
             "pred": np.ndarray, "label": np.ndarray}
    Raises FileNotFoundError with fallback message if missing.
    """
    ...

def load_all_caches(results_dir: str, splits: list) -> dict[str, dict]:
    """Returns {split_name: per_example_dict} for all splits."""
    ...

def verify_cache_integrity(caches: dict[str, dict], expected_counts: dict) -> None:
    """Assert all fields present; log warnings for count mismatches."""
    ...
```

---

### DatasetMeta (`code/dataset_meta.py`)

**Dependencies**: Config

```python
from datasets import Dataset

def load_adv_mnli_meta() -> Dataset:
    """load_dataset("adv_glue", "adv_mnli", split="validation")"""
    ...

def load_anli_meta(round_id: int) -> Dataset:
    """load_dataset("anli", split=f"test_r{round_id}")"""
    ...

def load_glue_mnli_meta(seed: int = 1, n: int = 2000) -> Dataset:
    """load_dataset("glue", "mnli", split="validation_matched"), subsample n."""
    ...
```

---

### Stratifier (`code/stratifier.py`)

**Dependencies**: Config

```python
import numpy as np

def build_strata(split: str, n: int) -> dict[str, np.ndarray]:
    """
    Returns {stratum_label: boolean mask (n,)}.
    advglue_mnli -> {"high_pres_all": ones}
    anli_rN      -> {f"anli_r{N}_high_pres": ones}
    mnli         -> {"clean_baseline": ones}
    """
    ...

def compute_preservation_rate(strata: dict[str, np.ndarray]) -> float:
    """Fraction of examples in any high-preservation stratum (1.0 by construction)."""
    ...
```

---

### ECEAnalyzer (`code/ece_analyzer.py`)

**Dependencies**: CacheLoader, Stratifier, h-e1 compute_ece

```python
import numpy as np

def compute_stratum_ece(
    cache: dict, mask: np.ndarray, n_bins: int = 15
) -> float:
    """compute_ece(cache["conf"][mask], cache["correct"][mask], n_bins)"""
    ...

def compute_delta_ece(stratum_ece: float, clean_ece: float) -> float: ...

def run_all_strata(
    caches: dict[str, dict], n_bins: int = 15
) -> dict[str, dict]:
    """
    Returns {split: {"ece": float, "delta_ece": float, "n": int}}
    for all splits and strata.
    """
    ...

def check_anli_gradient(stratum_results: dict) -> bool:
    """Returns True if ΔECE(R3) >= ΔECE(R2) >= ΔECE(R1)."""
    ...
```

---

### Ablations (`code/ablations.py`)

**Dependencies**: ECEAnalyzer, CacheLoader

```python
def ablation_criterion_sensitivity(caches: dict) -> dict:
    """
    A: all examples unstratified
    B: advglue_mnli only
    C: anli R1/R2/R3 separately
    Returns {variant: delta_ece}
    """
    ...

def ablation_bin_count(cache: dict, mask, bin_counts=(10, 15, 20)) -> dict:
    """Returns {n_bins: ece} for high-preservation stratum."""
    ...

def ablation_task_scope(caches: dict) -> dict:
    """
    NLI only vs NLI + QQP + SST-2.
    Returns {scope: {"ece": float, "delta_ece": float}}
    """
    ...
```

---

### GateVerifier (`code/gate_verifier.py`)

**Dependencies**: Config

```python
def verify_gate(
    preservation_rate: float,
    stratum_ece: float,
    clean_ece: float,
    h_e1_delta: float = 0.071,
) -> tuple[bool, dict]:
    """
    Returns (passed, indicators) where indicators has keys:
      preservation_rate_ok, delta_ece_positive, consistent_with_h_e1
    Gate passes iff preservation_rate_ok AND delta_ece_positive.
    """
    ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: Config

```python
def plot_preservation_rate(rates: dict[str, float], out_path: str) -> None:
    """Bar chart: preservation rate by benchmark vs 0.80 threshold."""
    ...

def plot_stratum_ece(stratum_results: dict, out_path: str) -> None:
    """Bar chart: ECE_clean vs ECE_adv per stratum."""
    ...

def plot_anli_gradient(stratum_results: dict, out_path: str) -> None:
    """Line chart: ΔECE vs ANLI round R1/R2/R3."""
    ...

def plot_reliability_diagrams(caches: dict, strata: dict, out_path: str) -> None:
    """Per-stratum confidence vs accuracy per bin."""
    ...
```

---

### ResultsWriter (`code/results_writer.py`)

**Dependencies**: h-e1 write_json, write_gate_result

```python
def write_main_results(stratum_results: dict, out_dir: str) -> None:
    """write_json(h_m1_results.json)"""
    ...

def write_gate_report(passed: bool, indicators: dict, out_dir: str) -> None:
    """write_gate_result(h_m1_gate_report.json, ...)"""
    ...

def write_ablation_results(ablation_data: dict, out_dir: str) -> None:
    """write_json(ablation_results.json)"""
    ...
```

---

### RunAnalysis (`code/run_analysis.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """
    1. load_all_caches -> verify_cache_integrity
    2. load dataset metadata (for label field verification)
    3. build_strata per split -> compute_preservation_rate
    4. run_all_strata -> check_anli_gradient
    5. ablation_criterion_sensitivity, ablation_bin_count, ablation_task_scope
    6. verify_gate -> write_gate_report
    7. plot_* figures
    8. write_main_results, write_ablation_results
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | File structure, config.py, h-e1 sys.path injection, verify imports | 6 | 1+1+2+2 |
| A-2 | Cache Loader | load_split_cache, load_all_caches, verify_cache_integrity with fallback message | 9 | 2+2+3+2 |
| A-3 | Dataset Metadata | load_adv_mnli_meta, load_anli_meta x3, load_glue_mnli_meta with subsample | 8 | 2+2+2+2 |
| A-4 | Stratifier | build_strata per split, compute_preservation_rate, document construction-guarantee finding | 9 | 2+2+3+2 |
| A-5 | ECE Analyzer | compute_stratum_ece (reuse h-e1 compute_ece), run_all_strata, check_anli_gradient | 11 | 3+3+3+2 |
| A-6 | Ablations | All 3 ablations: criterion sensitivity, bin count, task scope | 13 | 3+3+4+3 |
| A-7 | Gate Verifier | verify_gate with all 3 indicators, PIVOT branch logging | 8 | 2+2+2+2 |
| A-8 | Visualizer | 4 figures: preservation_rate bar, stratum ECE bar, ANLI gradient line, reliability diagrams | 12 | 3+2+4+3 |
| A-9 | Results Writer | write_main_results, write_gate_report, write_ablation_results (reuse h-e1 write_json) | 7 | 2+2+2+1 |
| A-10 | Integration & run_analysis.py | Wire all modules in main(), end-to-end test on cached outputs | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-6, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-4, A-7, A-9]

---

## Notes

- H-M1 is analysis-only; no GPU/model inference unless H-E1 cache missing.
- `compute_ece` imported from h-e1 via `sys.path.insert` — do not copy-paste.
- `write_json` and `write_gate_result` similarly reused from h-e1 storage module.
- Preservation rate will be ~1.0 by dataset construction; document this as a positive finding, not a trivial result.
- ANLI round gradient (A-5) is a direction check, not a strict gate condition.
