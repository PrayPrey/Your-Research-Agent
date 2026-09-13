# Logic: h-m2 — Epsilon-Threshold Robustness of MLP Activation Sparsity Variation

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Budget:** 7 subtasks (A-4: 1, A-5: 2, A-7: 2, A-9: 2)

Applied: forward-hook-measurement-pattern (accelerate.hooks layerwise casting)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: API signatures verified from actual h-e1 code (direct file read; Serena project selection unavailable)
**Analyzed Path**: `docs/youra_research/20260508_scope/h-e1/code/`
**Relevant Symbols**:
- `measure_layer_sparsity(model, dataloader, epsilon, cfg) -> np.ndarray`  shape (32,)
- `register_hooks(model, epsilon, layer_counts) -> List`  removes hooks in finally block
- `verify_mechanism(layer_sparsity, cfg) -> Tuple[bool, dict]`
- `compute_cv(layer_sparsity) -> float`
- `compute_kendall_tau(sparsity_a, sparsity_b) -> Tuple[float, float]`

---

## External Dependencies API (Base Hypothesis)

Verified from: `docs/youra_research/20260508_scope/h-e1/code/` (actual implementation)

```python
# From: h-e1/code/measure_sparsity.py (ACTUAL CODE)
def register_hooks(
    model,
    epsilon: float,
    layer_counts: List[List[float]],  # mutated in-place; shape: 32 × variable
) -> List:  # list of hook handles; removed in measure_layer_sparsity's finally block
    ...

def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,      # ← exact param name from actual code
    cfg: ExperimentConfig,
) -> np.ndarray:  # shape: (32,) per-layer mean sparsity fraction
    ...

def verify_mechanism(
    layer_sparsity: np.ndarray,  # shape: (32,)
    cfg: ExperimentConfig,
) -> Tuple[bool, dict]:  # (all_passed, {len_ok, mean_positive, std_nonzero, mean_value, std_value})
    ...

# From: h-e1/code/compute_metrics.py (ACTUAL CODE)
def compute_cv(layer_sparsity: np.ndarray) -> float:
    """std / mean; returns 0.0 if mean == 0."""
    ...

def compute_kendall_tau(
    sparsity_a: np.ndarray,
    sparsity_b: np.ndarray,
) -> Tuple[float, float]:  # (tau_statistic, p_value); NOTE: h-e1 does NOT pass variant='b'
    ...
```

**Critical note**: h-e1's `compute_kendall_tau` does NOT pass `variant='b'`. h-m2 MUST use `kendalltau(..., variant='b')` directly (FR-4.3) — do not reuse h-e1's wrapper.

---

## A-4: Multi-Epsilon Sparsity Measurement [Complexity: 9, Budget: 1 subtask]

Applied: Standard PyTorch measurement loop with hook cleanup

### API Signatures

```python
# h-m2/code/run_experiment.py
from measure_sparsity import measure_layer_sparsity
from config import ExperimentConfig
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, Tuple

def measure_all_epsilons(
    model,
    alpaca_dl: DataLoader,
    wikitext_dl: DataLoader,
    cfg: ExperimentConfig,
) -> Tuple[Dict[float, np.ndarray], Dict[float, np.ndarray]]:
    """Loop over 4 epsilons × 2 datasets = 8 measurement calls.
    Returns (alpaca_sparsity_dict, wikitext_sparsity_dict), both keyed by epsilon float."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| gate_proj output (per hook) | [B, seq_len, 14336] | B=8, seq_len=512 |
| layer_sparsity per call | (32,) | per-layer mean sparsity |
| alpaca_sparsity_dict[eps] | (32,) | 4 entries |
| wikitext_sparsity_dict[eps] | (32,) | 4 entries |

### Pseudo-code

```
alpaca_dict = {}
wikitext_dict = {}
for eps in cfg.epsilons:          # [0.001, 0.01, 0.05, 0.1]
    alpaca_dict[eps]   = measure_layer_sparsity(model, alpaca_dl, eps, cfg)   # (32,)
    wikitext_dict[eps] = measure_layer_sparsity(model, wikitext_dl, eps, cfg) # (32,)
    # hooks are registered and removed inside measure_layer_sparsity (finally block)
return alpaca_dict, wikitext_dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-4-ST1 | measure_all_epsilons + hook cleanup | Implement loop; assert hooks removed after each call; verify all 8 arrays shape (32,) |

---

## A-5: Cross-Epsilon Tau Computation [Complexity: 12, Budget: 2 subtasks]

Applied: scipy.stats.kendalltau variant='b' pairwise sweep

### API Signatures

```python
# h-m2/code/compute_metrics.py
from scipy.stats import kendalltau
import numpy as np
from typing import Dict, List, Tuple

ADJACENT_PAIRS = [(0.001, 0.01), (0.01, 0.05), (0.05, 0.1)]

def compute_cv_per_epsilon(
    sparsity_dict: Dict[float, np.ndarray],  # {eps: (32,)}
    epsilons: List[float],
) -> Dict[float, float]:
    """CV = std/mean for each 32-layer sparsity vector. Guard: return 0.0 if mean==0."""
    ...

def count_cv_pass(
    cv_per_epsilon: Dict[float, float],
    threshold: float = 0.3,
) -> Tuple[int, Dict[float, bool]]:
    """Count epsilons with CV > threshold.
    Returns (count: int, pass_flags: {eps: bool})."""
    ...

def compute_cross_epsilon_tau(
    sparsity_dict: Dict[float, np.ndarray],  # {eps: (32,)}
    epsilons: List[float],
) -> Dict[str, Dict[str, float]]:
    """All C(4,2)=6 pairwise Kendall's tau_b.
    Key format: '{e1}_vs_{e2}' where e1 < e2 (float comparison).
    Returns: {'0.001_vs_0.01': {'tau': float, 'p_value': float}, ...} × 6"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sparsity_dict[eps] | (32,) | input to each pair |
| tau_matrix | dict of 6 str keys | each value: {tau, p_value} |

### Pseudo-code for compute_cross_epsilon_tau

```
pairs = [(e1, e2) for i, e1 in enumerate(epsilons)
                  for e2 in epsilons[i+1:]]  # 6 pairs, e1 < e2
result = {}
for e1, e2 in pairs:
    key = f"{e1}_vs_{e2}"
    tau_stat, pval = kendalltau(sparsity_dict[e1], sparsity_dict[e2], variant='b')
    result[key] = {"tau": float(tau_stat), "p_value": float(pval)}
return result
# Pairs: 0.001_vs_0.01, 0.001_vs_0.05, 0.001_vs_0.1, 0.01_vs_0.05, 0.01_vs_0.1, 0.05_vs_0.1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-5-ST1 | compute_cv_per_epsilon + count_cv_pass | CV computation with zero-guard; count_cv_pass with threshold=0.3 default |
| A-5-ST2 | compute_cross_epsilon_tau 6-pair kendalltau_b | All 6 pairs; key format f"{e1}_vs_{e2}"; variant='b' required |

---

## A-7: Gate Evaluation [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch

### API Signatures

```python
# h-m2/code/compute_metrics.py

def evaluate_gate(
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Tuple[bool, Dict]:
    """Combined gate: PASS iff count_cv_pass >= cfg.cv_pass_min_count (3)
    AND max_adjacent_tau >= cfg.cross_epsilon_tau_threshold (0.7).
    gate_details keys: gate_result, cv_pass_count, cv_pass_epsilons,
                       max_adjacent_tau, adjacent_pair_results, failed_conditions."""
    ...

def verify_mechanism_activated(
    sparsity_dict: Dict[float, np.ndarray],
    tau_matrix: Dict[str, Dict[str, float]],
    epsilons: List[float],
) -> Tuple[bool, Dict]:
    """Pre-flight checks before gate evaluation.
    Checks: len(sparsity_dict[eps])==32 for all eps,
            len(tau_matrix)==6, all sparsity values in (0,1).
    Returns (all_ok: bool, check_details: dict)."""
    ...
```

### Pseudo-code for evaluate_gate

```
cv_pass_count, cv_pass_flags = count_cv_pass(cv_per_epsilon, threshold=cfg.cv_threshold)

adjacent_pair_results = {}
for (e1, e2) in ADJACENT_PAIRS:  # [(0.001,0.01),(0.01,0.05),(0.05,0.1)]
    key = f"{e1}_vs_{e2}"
    adjacent_pair_results[key] = tau_matrix[key]["tau"]
max_adjacent_tau = max(adjacent_pair_results.values())

cv_gate_pass  = cv_pass_count >= cfg.cv_pass_min_count   # >= 3
tau_gate_pass = max_adjacent_tau >= cfg.cross_epsilon_tau_threshold  # >= 0.7
gate_result   = cv_gate_pass and tau_gate_pass

failed_conditions = []
if not cv_gate_pass:  failed_conditions.append(f"cv_pass_count={cv_pass_count} < {cfg.cv_pass_min_count}")
if not tau_gate_pass: failed_conditions.append(f"max_adjacent_tau={max_adjacent_tau:.4f} < {cfg.cross_epsilon_tau_threshold}")

gate_details = {
    "gate_result": gate_result,
    "cv_pass_count": cv_pass_count,
    "cv_pass_epsilons": [e for e, ok in cv_pass_flags.items() if ok],
    "max_adjacent_tau": max_adjacent_tau,
    "adjacent_pair_results": adjacent_pair_results,
    "failed_conditions": failed_conditions,
}
return gate_result, gate_details
```

### Pseudo-code for verify_mechanism_activated

```
checks = {}
checks["all_epsilons_32_layers"] = all(len(sparsity_dict[e]) == 32 for e in epsilons)
checks["tau_matrix_6_pairs"]     = len(tau_matrix) == 6
checks["sparsity_in_0_1"]        = all(
    np.all((sparsity_dict[e] > 0) & (sparsity_dict[e] < 1)) for e in epsilons
)
return all(checks.values()), checks
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-7-ST1 | evaluate_gate with adjacent-pair filtering | Implement ADJACENT_PAIRS loop; max_adjacent_tau; failed_conditions list |
| A-7-ST2 | verify_mechanism_activated pre-flight checks | 3 checks: 32 layers, 6 pairs, sparsity in (0,1) |

---

## A-9: Main Runner Integration [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch

### API Signatures

```python
# h-m2/code/run_experiment.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, json
from pathlib import Path
from config import ExperimentConfig
from data_utils import load_alpaca_dataloader, load_wikitext_dataloader
from measure_sparsity import measure_layer_sparsity, verify_mechanism
from compute_metrics import (
    compute_cv_per_epsilon, count_cv_pass,
    compute_cross_epsilon_tau, compute_cross_dist_tau,
    evaluate_gate, verify_mechanism_activated,
)
from visualize import generate_all_figures

def load_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> Tuple:  # (model, tokenizer)
    """Load meta-llama/Meta-Llama-3-8B float16 auto device_map.
    Sets model.eval(); tokenizer.pad_token = tokenizer.eos_token if None."""
    ...

def measure_all_epsilons(
    model,
    alpaca_dl: DataLoader,
    wikitext_dl: DataLoader,
    cfg: ExperimentConfig,
) -> Tuple[Dict[float, np.ndarray], Dict[float, np.ndarray]]:
    """Returns (alpaca_sparsity_dict, wikitext_sparsity_dict) keyed by epsilon float."""
    ...

def save_results(
    cv_per_epsilon: Dict[float, float],
    tau_matrix: Dict[str, Dict[str, float]],
    cross_dist_tau: Dict[float, Dict[str, float]],
    gate_result: bool,
    gate_details: Dict,
    cfg: ExperimentConfig,
) -> None:
    """Write experiment_results.json to cfg.results_dir."""
    ...

def main() -> None:
    """Entry point: setup → load → measure → compute_metrics → gate → visualize → save → stdout."""
    ...
```

### JSON Structure for save_results

```json
{
  "hypothesis": "h-m2",
  "gate_result": true,
  "cv_per_epsilon": {"0.001": 0.52, "0.01": 0.544, "0.05": 0.48, "0.1": 0.41},
  "cv_pass_count": 4,
  "tau_matrix": {
    "0.001_vs_0.01":  {"tau": 0.91, "p_value": 1e-10},
    "0.001_vs_0.05":  {"tau": 0.88, "p_value": 2e-10},
    "0.001_vs_0.1":   {"tau": 0.82, "p_value": 5e-10},
    "0.01_vs_0.05":   {"tau": 0.94, "p_value": 1e-11},
    "0.01_vs_0.1":    {"tau": 0.87, "p_value": 3e-10},
    "0.05_vs_0.1":    {"tau": 0.93, "p_value": 1e-11}
  },
  "cross_dist_tau": {
    "0.001": {"tau": 0.72, "p_value": 1e-8},
    "0.01":  {"tau": 0.78, "p_value": 1e-9},
    "0.05":  {"tau": 0.75, "p_value": 1e-8},
    "0.1":   {"tau": 0.69, "p_value": 2e-8}
  },
  "gate_details": {...},
  "sparsity_profiles": {
    "alpaca":   {"0.001": [...], "0.01": [...], "0.05": [...], "0.1": [...]},
    "wikitext": {"0.001": [...], "0.01": [...], "0.05": [...], "0.1": [...]}
  }
}
```

### Pseudo-code for main()

```
cfg = ExperimentConfig()
Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)
np.random.seed(cfg.seed); torch.manual_seed(cfg.seed)

model, tokenizer = load_model_and_tokenizer(cfg)
alpaca_dl   = load_alpaca_dataloader(tokenizer, cfg, max_length=cfg.max_length)
wikitext_dl = load_wikitext_dataloader(tokenizer, cfg, max_length=cfg.max_length)

alpaca_sparsity, wikitext_sparsity = measure_all_epsilons(model, alpaca_dl, wikitext_dl, cfg)

cv_per_epsilon  = compute_cv_per_epsilon(alpaca_sparsity, cfg.epsilons)
tau_matrix      = compute_cross_epsilon_tau(alpaca_sparsity, cfg.epsilons)
cross_dist_tau  = compute_cross_dist_tau(alpaca_sparsity, wikitext_sparsity, cfg.epsilons)

ok, checks = verify_mechanism_activated(alpaca_sparsity, tau_matrix, cfg.epsilons)
assert ok, f"Pre-flight checks failed: {checks}"

gate_result, gate_details = evaluate_gate(cv_per_epsilon, tau_matrix, cfg)

generate_all_figures(alpaca_sparsity, cv_per_epsilon, tau_matrix, cfg)
save_results(cv_per_epsilon, tau_matrix, cross_dist_tau, gate_result, gate_details, cfg)

# stdout summary
status = "PASS" if gate_result else "FAIL"
print(f"\n=== H-M2 GATE: {status} ===")
print(f"CV pass count: {gate_details['cv_pass_count']}/4 (need >= {cfg.cv_pass_min_count})")
print(f"Max adjacent tau: {gate_details['max_adjacent_tau']:.4f} (need >= {cfg.cross_epsilon_tau_threshold})")
if not gate_result:
    for cond in gate_details['failed_conditions']:
        print(f"  FAILED: {cond}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-9-ST1 | load_model_and_tokenizer + measure_all_epsilons integration | AutoModelForCausalLM float16 auto; pad_token guard; 8-call epsilon loop |
| A-9-ST2 | save_results JSON structure + main() stdout gate summary | JSON with sparsity_profiles arrays; stdout PASS/FAIL with numeric gaps |

---

## Subtask Summary

| ID | Epic | Subtask | Budget Used |
|----|------|---------|-------------|
| A-4-ST1 | A-4 | measure_all_epsilons + hook cleanup | 1 |
| A-5-ST1 | A-5 | compute_cv_per_epsilon + count_cv_pass | 2 |
| A-5-ST2 | A-5 | compute_cross_epsilon_tau 6-pair kendalltau_b | 2 |
| A-7-ST1 | A-7 | evaluate_gate with adjacent-pair filtering | 4 |
| A-7-ST2 | A-7 | verify_mechanism_activated pre-flight checks | 4 |
| A-9-ST1 | A-9 | load_model_and_tokenizer + measure_all_epsilons | 6 |
| A-9-ST2 | A-9 | save_results JSON + main() stdout gate summary | 6 |

**Total: 7/7 subtasks used**
