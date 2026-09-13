# H-M3 Logic: Mechanism Discrimination

Applied: subprocess-runner-with-oom-retry, path-a-path-b-dispatcher

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena project activation failed; API signatures verified via direct file reads from actual code
**Analyzed Path**: `h-m2/code/load_data.py`, `h-e1/code/calibration_analysis.py`
**Relevant Symbols**:
- `load_logprob_matrices(h_e1_results_dir, h_m2_results_dir, sizes, alignments, device)` — h-m2/code/load_data.py
- `load_lmeval_samples(model_id, results_dir)` — h-e1/code/calibration_analysis.py (param: `model_id`, NOT `model_key`)
- `run_lmeval_for_model(model_key, hf_id, output_dir, device, num_fewshot, timeout)` — h-m2/code/load_data.py

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/calibration_analysis.py (ACTUAL CODE)
def load_lmeval_samples(
    model_id: str,          # ← "model_id" NOT "model_key" (verified!)
    results_dir: str = RESULTS_DIR,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns: (logprobs, y_true)
    logprobs: (N, 4) float64; y_true: (N,) int64
    Glob pattern: results_dir/{model_id}/**/samples_mmlu*.jsonl
    """

def compute_ece(probs, y_true, n_bins=15) -> float: ...
def compute_brier_decomposition(y_true, y_prob, n_bins=15) -> dict: ...

# From: h-m2/code/load_data.py (ACTUAL CODE)
def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m2_results_dir: str,  # ← second arg is h_m2_results_dir (NOT h_m3)
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple[dict, str]:      # (logprob_matrices, "Path A" | "Path B")

def run_lmeval_for_model(
    model_key: str,
    hf_id: str,
    output_dir: str,
    device: str = "cuda",
    num_fewshot: int = 4,
    timeout: int = 7200,
) -> str:                   # returns model output directory path
```

**Verified from**: `h-m2/code/load_data.py` and `h-e1/code/calibration_analysis.py` (actual implementation)

---

## A-2: Data Loading [Complexity: 9, Budget: 1 subtask]

Applied: path-a-path-b-dispatcher (mirrored from h-m2/code/load_data.py)

### API Signatures

```python
# h-m3/code/load_data.py
import sys, os, glob, json, logging
import numpy as np
from pathlib import Path

_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from calibration_analysis import load_lmeval_samples


def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m3_results_dir: str,
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple[dict, str]:
    """Dispatcher: Path A (h-e1 cache) -> Path B (re-run lm-eval for MMLU).
    Returns: ({model_key: (N,4) float64}, "Path A" | "Path B")
    model_key format: 'pythia-{size}-{alignment}'
    """

def _load_path_a(results_dir: str, sizes: list, alignments: list) -> tuple[dict, str]:
    """Load from h-e1 JSONL via load_lmeval_samples(model_id, results_dir).
    Note: load_lmeval_samples param is 'model_id', not 'model_key'.
    Returns: ({model_key: (N,4)}, "Path A")
    Raises: RuntimeError if any model returns 0 samples.
    """

def _load_path_b(
    output_dir: str,
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple[dict, str]:
    """Re-run lm-eval for all 12 models then load via load_lmeval_samples().
    Uses run_lmeval_for_model pattern from h-m2/code/load_data.py.
    Returns: ({model_key: (N,4)}, "Path B")
    """

def load_labels(
    h_e1_results_dir: str,
    sizes: list,
) -> dict[str, np.ndarray]:
    """Load y_true (N,) int64 per base model_key from h-e1 JSONL.
    Calls load_lmeval_samples(model_id=f'pythia-{size}-base', results_dir=...).
    Returns: {'pythia-{size}-base': y_true}  # (N,) int64
    """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_data.py | Path A/B dispatcher + load_labels with h-e1 sys.path injection |

---

## A-3: Spearman Analysis [Complexity: 10, Budget: 2 subtasks]

Applied: Standard scipy.stats pattern

### API Signatures

```python
# h-m3/code/spearman_analysis.py
import numpy as np
from scipy import stats


def compute_spearman_rho_per_item(
    base_logprobs: np.ndarray,      # (N, 4) float64
    aligned_logprobs: np.ndarray,   # (N, 4) float64
) -> tuple[np.ndarray, float]:
    """Per-item Spearman rho over 4-option log-prob vectors.
    Returns: (rho_per_item (N,) float64, mean_rho float)
    Uses: scipy.stats.spearmanr(base_logprobs[i], aligned_logprobs[i]).correlation
    """

def compute_all_spearman_results(
    logprob_matrices: dict,         # {model_key: (N,4) float64}
    sizes: list,
    alignments: list,
) -> dict:
    """Compute Spearman rho for all 9 base-aligned pairs.
    Returns: {
        '{size}-{alignment}': {
            'rho_per_item': np.ndarray,  # (N,) float64
            'mean_rho': float,
            'h1_pass': bool,   # mean_rho >= H1_RHO_THRESHOLD (0.9)
            'h2_flag': bool,   # mean_rho < H2_RHO_THRESHOLD (0.85)
        }
    }
    """

def assess_h1_h2_gate(
    spearman_results: dict,
    h1_threshold: float = 0.9,
    h2_threshold: float = 0.85,
) -> dict:
    """Assess H1/H2 gate: all 9 pairs must pass H1.
    Returns: {
        'gate_pass': bool,      # all 9 pairs have mean_rho >= h1_threshold
        'n_h1_pass': int,       # count of pairs with mean_rho >= h1_threshold
        'n_h2_flag': int,       # count of pairs with mean_rho < h2_threshold
        'per_pair': dict,       # {pair_key: {'mean_rho': float, 'h1_pass': bool}}
    }
    """
```

### Pseudo-code for compute_spearman_rho_per_item

```
rho_per_item = np.array([
    stats.spearmanr(base_logprobs[i], aligned_logprobs[i]).correlation
    for i in range(N)
])
mean_rho = float(np.nanmean(rho_per_item))
return rho_per_item, mean_rho
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_spearman_rho_per_item + compute_all_spearman_results | Per-item rho loop + 9-pair aggregation |
| L-3-2 | assess_h1_h2_gate | Threshold comparison, gate_pass = all(h1_pass) |

---

## A-5: TruthfulQA Analysis [Complexity: 14, Budget: 4 subtasks]

Applied: subprocess-runner-with-oom-retry (mirrored from h-m2 run_lmeval_for_model)

### API Signatures

```python
# h-m3/code/truthfulqa_analysis.py
import os, subprocess, glob, json, logging
import numpy as np
from pathlib import Path
import sys

# sys.path injection for h-e1 (same pattern as load_data.py)
_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from calibration_analysis import compute_ece


def run_lmeval_truthfulqa(
    model_key: str,
    hf_id: str,
    output_dir: str,
    device: str = "cuda",
    timeout: int = 7200,
) -> str:
    """Run lm_eval --tasks truthfulqa_mc1 --num_fewshot 0 --log_samples.
    OOM retry with --batch_size 4 (mirrors h-m2 run_lmeval_for_model pattern).
    Returns: output directory path (str)
    Raises: RuntimeError after 2 failed attempts.
    """

def load_truthfulqa_logprobs(
    model_key: str,
    results_dir: str,
) -> tuple[list, np.ndarray]:
    """Load per-item TruthfulQA MC1 log-probs from JSONL (variable options).
    Glob: results_dir/{model_key}/**/samples_truthfulqa_mc1*.jsonl
    Returns:
        logprobs_list: list of (K_i,) float64 arrays  # K_i varies per item
        y_true: (N,) int64                             # correct option index (0-based)
    Note: K_i != 4 (variable); must NOT stack into (N,4) array.
    """

def _tqa_item_to_softmax_prob(logprobs_i: np.ndarray) -> np.ndarray:
    """Softmax over variable-K log-probs -> probs (K_i,) float64."""

def compute_truthfulqa_ece_all_models(
    tqa_results_dir: str,
    h_e1_results_dir: str,
    sizes: list,
    alignments: list,
    hf_model_ids: dict,
    device: str = "cuda",
    n_bins: int = 15,
) -> dict:
    """Run or load TruthfulQA MC1 for all 12 models; compute ECE.
    Cache check: skip run_lmeval_truthfulqa if JSONL already present.
    ECE: computed item-wise using max(softmax(logprobs_i)) as confidence.
    Returns: {
        'pythia-{size}-{alignment}': {'ece': float, 'n_items': int}
    }
    """

def assess_h3_diagnostic(
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """H3 diagnostic: TruthfulQA ECE increase >> MMLU ECE increase.
    delta_tqa[alignment] = mean(tqa_ece[aligned]) - mean(tqa_ece[base])
    delta_mmlu[alignment] = mean(mmlu_ece[aligned]) - mean(mmlu_ece[base])
    h3_flag = any(delta_tqa[alignment] > 2 * delta_mmlu[alignment])
    Returns: {
        'h3_flag': bool,
        'per_alignment': {
            'sft'|'dpo'|'ppo': {
                'delta_tqa': float,
                'delta_mmlu': float,
                'ratio': float,       # delta_tqa / max(delta_mmlu, 1e-6)
                'h3_signal': bool,
            }
        }
    }
    """
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logprobs_list[i] | (K_i,) | K_i varies: TruthfulQA MC1 has variable options |
| y_true | (N,) int64 | N=817 |
| confidence_i | scalar | max(softmax(logprobs_list[i])) |

### Pseudo-code for load_truthfulqa_logprobs

```
files = glob(results_dir/{model_key}/**/samples_truthfulqa_mc1*.jsonl)
for line in files:
    doc = json.loads(line)
    lp = [resp[0][0] for resp in doc["filtered_resps"]]  # list of log-probs
    gold = doc["doc"]["mc1_targets"]["labels"].index(1)   # index of correct answer
    logprobs_list.append(np.array(lp, dtype=float64))
    y_true_list.append(gold)
return logprobs_list, np.array(y_true_list, int64)
```

### Pseudo-code for compute_truthfulqa_ece_all_models (cache check)

```
for each model_key:
    jsonl = glob(tqa_results_dir/{model_key}/**/samples_truthfulqa_mc1*.jsonl)
    if not jsonl:
        run_lmeval_truthfulqa(model_key, hf_id, tqa_results_dir, device)
    logprobs_list, y_true = load_truthfulqa_logprobs(model_key, tqa_results_dir)
    # ECE: build (N,) confidence and correct arrays
    confs = [max(softmax(lp)) for lp in logprobs_list]
    correct = [int(argmax(lp) == y) for lp, y in zip(logprobs_list, y_true)]
    ece = compute_ece_from_conf_correct(confs, correct, n_bins)
    results[model_key] = {'ece': ece, 'n_items': len(y_true)}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | run_lmeval_truthfulqa | Subprocess runner, truthfulqa_mc1 task, 0-shot, OOM retry |
| L-5-2 | load_truthfulqa_logprobs | JSONL parser for variable-K options; list-of-arrays return |
| L-5-3 | compute_truthfulqa_ece_all_models | Cache-check orchestrator; ECE from max-confidence |
| L-5-4 | assess_h3_diagnostic | delta_tqa vs delta_mmlu comparison per alignment |

---

## A-8: Orchestration + Tests [Complexity: 10, Budget: 2 subtasks]

Applied: Standard argparse + logging orchestration

### API Signatures

```python
# h-m3/code/run_experiment.py
import argparse, logging, json
from config import (
    H_E1_RESULTS_DIR, H_M3_RESULTS_DIR, H_M3_TRUTHFULQA_DIR,
    H_M3_FIGURES_DIR, H_M3_REPORT_PATH, H_M3_EXPERIMENT_RESULTS_JSON,
    VERIFICATION_STATE_PATH, SIZES, ALIGNMENTS, N_BOOTSTRAP, SEED, N_BINS,
    HF_MODEL_IDS, H1_RHO_THRESHOLD, H2_RHO_THRESHOLD,
)


def main(
    device: str = "cuda",
    smoke_test: bool = False,
) -> None:
    """Orchestrate full H-M3 experiment pipeline.
    smoke_test=True: use first 2 sizes, first 100 items only.
    Steps:
    1. load_logprob_matrices(H_E1_RESULTS_DIR, H_M3_RESULTS_DIR, sizes, alignments, device)
    2. load_labels(H_E1_RESULTS_DIR, sizes)
    3. compute_all_spearman_results(logprob_matrices, sizes, alignments)
    4. assess_h1_h2_gate(spearman_results)
    5. compute_all_partition_results(logprob_matrices, labels, sizes, alignments, N_BOOTSTRAP, SEED)
    6. compute_truthfulqa_ece_all_models(H_M3_TRUTHFULQA_DIR, H_E1_RESULTS_DIR, sizes, alignments, HF_MODEL_IDS, device, N_BINS)
    7. assess_h3_diagnostic(tqa_ece_results, mmlu_ece_results, sizes, alignments)
    8. determine_dominant_mechanism(spearman_gate, partition_results, h3_diagnostic, sizes, alignments)
    9. generate_all_figures(spearman_results, partition_results, tqa_ece, mmlu_ece, H_M3_FIGURES_DIR)
    10. write_validation_report(..., H_M3_REPORT_PATH)
    11. update_verification_state(VERIFICATION_STATE_PATH, gate_pass, dominant, key_metrics)
    12. save_experiment_results(all_results, H_M3_EXPERIMENT_RESULTS_JSON)
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--smoke_test", action="store_true")
    args = parser.parse_args()
    main(device=args.device, smoke_test=args.smoke_test)
```

```python
# h-m3/code/tests/test_spearman_analysis.py
import numpy as np
import pytest
from spearman_analysis import (
    compute_spearman_rho_per_item,
    compute_all_spearman_results,
    assess_h1_h2_gate,
)


def test_compute_spearman_rho_per_item_shape():
    """rho_per_item shape == (N,), mean_rho in [-1, 1]."""
    rng = np.random.default_rng(42)
    base = rng.normal(size=(100, 4))
    aligned = base + rng.normal(0, 0.1, size=(100, 4))
    rho_per_item, mean_rho = compute_spearman_rho_per_item(base, aligned)
    assert rho_per_item.shape == (100,)
    assert -1.0 <= mean_rho <= 1.0


def test_identical_logprobs_gives_rho_one():
    """Identical base/aligned -> rho_per_item all 1.0."""
    x = np.random.default_rng(0).normal(size=(50, 4))
    rho, mean_rho = compute_spearman_rho_per_item(x, x)
    assert np.allclose(rho, 1.0, atol=1e-6)
    assert abs(mean_rho - 1.0) < 1e-6


def test_assess_h1_h2_gate_pass():
    """gate_pass=True when all mean_rho >= 0.9."""
    results = {
        f"1.4b-{a}": {"mean_rho": 0.95, "h1_pass": True, "h2_flag": False}
        for a in ["sft", "dpo", "ppo"]
    }
    gate = assess_h1_h2_gate(results, h1_threshold=0.9)
    assert gate["gate_pass"] is True
    assert gate["n_h1_pass"] == 3


# h-m3/code/tests/test_argmax_partition.py
import numpy as np
import pytest
from argmax_partition import (
    partition_items_by_argmax,
    compute_cohens_d,
    compute_all_partition_results,
)


def test_partition_shared_changed_complement():
    """shared_mask | changed_mask == all True; no overlap."""
    rng = np.random.default_rng(1)
    base = rng.normal(size=(200, 4))
    aligned = base + rng.normal(0, 0.5, size=(200, 4))
    shared, changed = partition_items_by_argmax(base, aligned)
    assert shared.shape == (200,)
    assert changed.shape == (200,)
    assert np.all(shared | changed)
    assert not np.any(shared & changed)


def test_cohens_d_zero_for_equal_groups():
    """Cohen's d == 0 when groups are identical."""
    x = np.ones(100)
    assert abs(compute_cohens_d(x, x)) < 1e-9


def test_cohens_d_known_value():
    """Cohen's d for mean difference 1.0 and std 1.0 == 1.0."""
    rng = np.random.default_rng(42)
    g1 = rng.normal(1.0, 1.0, 10000)
    g2 = rng.normal(0.0, 1.0, 10000)
    d = compute_cohens_d(g1, g2)
    assert abs(d - 1.0) < 0.05
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | run_experiment.py main() | argparse + 12-step pipeline, smoke_test truncation |
| L-8-2 | test_spearman_analysis.py + test_argmax_partition.py | 3 test methods each, real assertions, no mocks |
