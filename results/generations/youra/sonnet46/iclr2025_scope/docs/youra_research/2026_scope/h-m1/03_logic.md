# Logic: h-m1 — Cross-Distribution Stability of MLP Activation Sparsity Profiles

**Date:** 2026-05-08
**Hypothesis Type:** MECHANISM (INCREMENTAL — extends h-e1)
**Gate:** ICC(3,k) > 0.75 AND all 6 pairwise Kendall's tau >= 0.6

Applied: PyTorch forward hook measurement pattern (torch.nn.Module.register_forward_hook)
Applied: Standard multi-dataset measurement sweep pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: API signatures verified from actual code
**Analyzed Path**: `docs/youra_research/20260508_scope/h-e1/code/`
**Relevant Symbols**:
- `load_alpaca_dataloader(tokenizer, cfg, max_length)` — note: takes `max_length` as 3rd positional arg
- `load_wikitext_dataloader(tokenizer, cfg, max_length=512)` — note: same pattern
- `register_hooks(model, epsilon, layer_counts)` — layer_counts is `List[List[float]]`
- `measure_layer_sparsity(model, dataloader, epsilon, cfg)` — returns `np.ndarray` shape `(32,)`
- `compute_kendall_tau(sparsity_a, sparsity_b)` — returns `(float, float)` tuple
- `compute_cv(layer_sparsity)` — returns `float`
- `check_gate_conditions(metrics, cfg)` — checks `cv_threshold` and `tau_threshold`

**Key discovery**: `load_alpaca_dataloader` and `load_wikitext_dataloader` both take `max_length` as a required 3rd positional argument — NOT keyword-only. h-m1 loaders must match this pattern.

---

## External Dependencies API

### API Signatures (From Actual Code)

Verified from `/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-e1/code/`

```python
# From: h-e1/code/data_utils.py (ACTUAL CODE)
class TokenizedDataset(Dataset):
    def __init__(self, input_ids_list: list): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...  # returns {"input_ids": Tensor}

def load_alpaca_dataloader(
    tokenizer,
    cfg: ExperimentConfig,
    max_length: int,          # ← positional, NOT keyword-only!
) -> DataLoader: ...

def load_wikitext_dataloader(
    tokenizer,
    cfg: ExperimentConfig,
    max_length: int = 512,    # ← has default but positional
) -> DataLoader: ...

# From: h-e1/code/measure_sparsity.py (ACTUAL CODE)
def register_hooks(
    model,
    epsilon: float,
    layer_counts: List[List[float]],  # mutable list, modified in-place
) -> List: ...  # list of hook handles

def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray: ...  # shape: (cfg.n_layers,) = (32,)

# From: h-e1/code/compute_metrics.py (ACTUAL CODE)
def compute_kendall_tau(
    sparsity_a: np.ndarray,
    sparsity_b: np.ndarray,
) -> Tuple[float, float]: ...  # (tau_statistic, p_value)

def compute_cv(layer_sparsity: np.ndarray) -> float: ...
```

**Note**: `run_all_conditions` in h-e1 is dataset-specific; h-m1 introduces `measure_all_distributions` as its replacement wrapper.

---

## A-1: data_utils.py Extension [Complexity: 9, Budget: 2]

### API Signatures

```python
# h-m1/code/data_utils.py
# EXTENDED from h-e1 — copy h-e1/code/data_utils.py and add below

from typing import Dict
import torch
from torch.utils.data import DataLoader
from datasets import load_dataset
from config import ExperimentConfig
# TokenizedDataset, load_alpaca_dataloader, load_wikitext_dataloader — copied from h-e1


def load_sst2_dataloader(
    tokenizer,
    cfg: ExperimentConfig,
) -> DataLoader:
    """Load nyu-mll/glue sst2 validation split, 512 samples, 'sentence' field."""
    ...


def load_mnli_dataloader(
    tokenizer,
    cfg: ExperimentConfig,
) -> DataLoader:
    """Load nyu-mll/glue mnli validation_matched split, 512 samples, premise+[SEP]+hypothesis."""
    ...


def load_all_dataloaders(
    tokenizer,
    cfg: ExperimentConfig,
) -> Dict[str, DataLoader]:
    """Return {alpaca, wikitext, sst2, mnli} -> DataLoader."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids per sample | `[512]` | max_length=512 tokens |
| batch from DataLoader | `[8, 512]` | batch_size=8 |

### Pseudo-code

```
load_sst2_dataloader(tokenizer, cfg):
  ds = load_dataset("nyu-mll/glue", "sst2", split="validation")
  ds = ds.select(range(cfg.n_samples))  # first 512
  for sample in ds:
    text = sample["sentence"]
    tokens = tokenizer(text, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    input_ids_list.append(tokens["input_ids"].squeeze(0))  # [512]
  return DataLoader(TokenizedDataset(input_ids_list), batch_size=cfg.batch_size, shuffle=False)

load_mnli_dataloader(tokenizer, cfg):
  ds = load_dataset("nyu-mll/glue", "mnli", split="validation_matched")
  ds = ds.select(range(cfg.n_samples))
  for sample in ds:
    text = sample["premise"] + " [SEP] " + sample["hypothesis"]
    tokens = tokenizer(text, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
    input_ids_list.append(tokens["input_ids"].squeeze(0))
  return DataLoader(TokenizedDataset(input_ids_list), batch_size=cfg.batch_size, shuffle=False)

load_all_dataloaders(tokenizer, cfg):
  return {
    "alpaca":   load_alpaca_dataloader(tokenizer, cfg, cfg.max_length),
    "wikitext": load_wikitext_dataloader(tokenizer, cfg, cfg.max_length),
    "sst2":     load_sst2_dataloader(tokenizer, cfg),
    "mnli":     load_mnli_dataloader(tokenizer, cfg),
  }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | sst2_mnli_loaders | Implement load_sst2_dataloader and load_mnli_dataloader |
| L-1-2 | load_all_dataloaders | Implement wrapper returning 4-key dict |

---

## A-2: measure_sparsity.py Extension [Complexity: 10, Budget: 2]

### API Signatures

```python
# h-m1/code/measure_sparsity.py
# COPIED from h-e1 + new wrapper below

from typing import Dict
import numpy as np
from torch.utils.data import DataLoader
from config import ExperimentConfig
# register_hooks, measure_layer_sparsity, verify_mechanism — copied unchanged from h-e1


def measure_all_distributions(
    model,
    dataloaders: Dict[str, DataLoader],  # {alpaca, wikitext, sst2, mnli}
    epsilon: float,
    cfg: ExperimentConfig,
) -> Dict[str, np.ndarray]:
    """Measure sparsity for each distribution. Returns {dist_name: array(32,)}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| gate_proj output (per batch) | `[8, 512, 14336]` | intermediate_size=14336 |
| sparsity scalar per batch | scalar | mean of `abs < epsilon` |
| per-layer mean sparsity | `(32,)` | one value per layer |
| return value conceptually | `(4, 32)` | 4 dists × 32 layers |

### Pseudo-code

```
measure_all_distributions(model, dataloaders, epsilon, cfg):
  profiles = {}
  for dist_name, dataloader in dataloaders.items():
    print(f"Measuring: dist={dist_name}, epsilon={epsilon}")
    profiles[dist_name] = measure_layer_sparsity(model, dataloader, epsilon, cfg)
  return profiles  # {dist_name: np.ndarray(32,)}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | copy_h-e1_sparsity | Copy measure_sparsity.py from h-e1 unchanged |
| L-2-2 | measure_all_distributions | Implement 4-distribution wrapper |

---

## A-3: compute_icc.py (NEW) [Complexity: 11, Budget: 3]

### API Signatures

```python
# h-m1/code/compute_icc.py
from typing import Dict
import numpy as np
import pandas as pd
import pingouin as pg


def build_icc_dataframe(
    sparsity_profiles: Dict[str, np.ndarray],  # {dist_name: array(32,)}
) -> pd.DataFrame:
    """Build long-format DataFrame: columns [layer, distribution, sparsity], 128 rows."""
    ...


def compute_icc3k(
    sparsity_profiles: Dict[str, np.ndarray],  # {dist_name: array(32,)}
) -> Dict[str, float]:
    """Compute ICC(3,k) via pingouin. Returns {icc3k, ci_lower, ci_upper, f_value, df1, df2}."""
    ...


def compute_icc_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]],
) -> Dict[float, Dict[str, float]]:
    """Compute ICC3k for each epsilon. Returns {epsilon: icc_result_dict}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| sparsity_profiles input | `{str: (32,)}` × 4 | 4 distributions |
| ICC DataFrame | `(128, 3)` | 4 dists × 32 layers, cols=[layer, distribution, sparsity] |
| icc3k result | dict of 6 floats/ints | icc3k, ci_lower, ci_upper, f_value, df1, df2 |

### Pseudo-code

```
build_icc_dataframe(sparsity_profiles):
  rows = []
  for dist_name, profile in sparsity_profiles.items():  # profile: (32,)
    for layer_idx in range(len(profile)):
      rows.append({"layer": layer_idx, "distribution": dist_name, "sparsity": profile[layer_idx]})
  return pd.DataFrame(rows)  # shape (128, 3)

compute_icc3k(sparsity_profiles):
  df = build_icc_dataframe(sparsity_profiles)
  icc_result = pg.intraclass_corr(
    data=df, targets="layer", raters="distribution", ratings="sparsity"
  )
  row = icc_result[icc_result["Type"] == "ICC3k"].iloc[0]
  return {
    "icc3k": float(row["ICC"]),
    "ci_lower": float(row["CI95%"][0]),
    "ci_upper": float(row["CI95%"][1]),
    "f_value": float(row["F"]),
    "df1": int(row["df1"]),
    "df2": int(row["df2"]),
  }

compute_icc_sensitivity(sparsity_by_epsilon):
  return {eps: compute_icc3k(profiles) for eps, profiles in sparsity_by_epsilon.items()}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | build_icc_dataframe | Long-format DataFrame construction |
| L-3-2 | compute_icc3k | pingouin.intraclass_corr call + extract ICC3k row |
| L-3-3 | compute_icc_sensitivity | Loop over epsilon values |

---

## A-4: compute_metrics.py Extension [Complexity: 9, Budget: 2]

### API Signatures

```python
# h-m1/code/compute_metrics.py
# EXTENDED from h-e1 — copy h-e1/code/compute_metrics.py and add below
# compute_cv, compute_kendall_tau, compute_all_metrics, check_gate_conditions — copied from h-e1

from typing import Any, Dict, List
import numpy as np
from itertools import combinations
from scipy.stats import kendalltau
from config import ExperimentConfig


def compute_pairwise_tau(
    sparsity_profiles: Dict[str, np.ndarray],  # {dist_name: array(32,)}
) -> Dict[str, Dict[str, float]]:
    """Compute C(4,2)=6 pairwise Kendall's tau. Returns {pair_key: {tau, pval}}."""
    ...


def compute_tau_min(
    tau_results: Dict[str, Dict[str, float]],
) -> float:
    """Return minimum tau across all 6 pairs."""
    ...


def compute_tau_sensitivity(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]],
) -> Dict[float, Dict[str, float]]:
    """Compute pairwise tau and tau_min for each epsilon. Returns {epsilon: {pair_key: tau, tau_min: float}}."""
    ...


def evaluate_gate(
    icc3k: float,
    tau_results: Dict[str, Dict[str, float]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Evaluate gate: PASS if icc3k > 0.75 AND all 6 tau >= 0.6."""
    ...
```

### Pseudo-code

```
compute_pairwise_tau(sparsity_profiles):
  dist_names = list(sparsity_profiles.keys())
  results = {}
  for d1, d2 in combinations(dist_names, 2):
    pair_key = f"{d1}_vs_{d2}"
    tau, pval = kendalltau(sparsity_profiles[d1], sparsity_profiles[d2])
    results[pair_key] = {"tau": float(tau), "pval": float(pval)}
  return results  # 6 entries

compute_tau_min(tau_results):
  return min(v["tau"] for v in tau_results.values())

evaluate_gate(icc3k, tau_results, cfg):
  tau_min = compute_tau_min(tau_results)
  icc_passed = icc3k > cfg.icc_threshold       # > 0.75
  tau_passed = tau_min >= cfg.tau_threshold    # >= 0.6
  failed_conditions = []
  if not icc_passed:
    failed_conditions.append(f"ICC3k={icc3k:.4f} < threshold={cfg.icc_threshold} (gap={cfg.icc_threshold-icc3k:.4f})")
  if not tau_passed:
    failed_conditions.append(f"tau_min={tau_min:.4f} < threshold={cfg.tau_threshold} (gap={cfg.tau_threshold-tau_min:.4f})")
  return {
    "gate_result": "PASS" if (icc_passed and tau_passed) else "FAIL",
    "icc3k": icc3k,
    "tau_min": tau_min,
    "icc_passed": icc_passed,
    "tau_passed": tau_passed,
    "failed_conditions": failed_conditions,
    "tau_results": tau_results,
  }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | pairwise_tau | compute_pairwise_tau, compute_tau_min, compute_tau_sensitivity |
| L-4-2 | evaluate_gate | Combined gate check with failure logging |

---

## A-5: visualize.py (NEW) [Complexity: 13, Budget: 2]

### API Signatures

```python
# h-m1/code/visualize.py
from typing import Any, Dict, List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_gate_metrics_bar(
    icc3k: float,
    tau_min: float,
    output_path: str,
) -> None:
    """Bar chart: ICC3k and tau_min vs thresholds (0.75, 0.6 dashed lines)."""
    ...


def plot_sparsity_heatmap(
    sparsity_profiles: Dict[str, np.ndarray],  # {dist: (32,)}
    output_path: str,
) -> None:
    """32 layers x 4 distributions heatmap, saved as PNG."""
    ...


def plot_pairwise_tau_matrix(
    tau_results: Dict[str, Dict[str, float]],  # {pair_key: {tau, pval}}
    output_path: str,
) -> None:
    """4x4 symmetric tau heatmap (diagonal=1.0)."""
    ...


def plot_icc_confidence(
    icc3k: float,
    ci_lower: float,
    ci_upper: float,
    output_path: str,
) -> None:
    """Bar with 95% CI for ICC3k vs 0.75 threshold line."""
    ...


def plot_sparsity_profiles_overlay(
    sparsity_profiles: Dict[str, np.ndarray],  # {dist: (32,)}
    output_path: str,
) -> None:
    """4 overlaid lines: x=layer index (0-31), y=sparsity."""
    ...


def plot_epsilon_sensitivity(
    icc_sensitivity: Dict[float, Dict[str, float]],    # {eps: {icc3k, ...}}
    tau_sensitivity: Dict[float, Dict[str, float]],    # {eps: {tau_min, ...}}
    output_path: str,
) -> None:
    """Dual-line plot: ICC3k and tau_min vs 4 epsilon values."""
    ...


def generate_all_figures(
    sparsity_profiles: Dict[str, np.ndarray],
    icc_result: Dict[str, float],
    tau_results: Dict[str, Dict[str, float]],
    gate_result: Dict[str, Any],
    icc_sensitivity: Dict[float, Dict[str, float]],
    tau_sensitivity: Dict[float, Dict[str, float]],
    figures_dir: str,
) -> List[str]:
    """Generate all 6 figures. Returns list of saved file paths."""
    ...
```

### Pseudo-code (key functions)

```
plot_sparsity_heatmap(sparsity_profiles, output_path):
  dist_names = list(sparsity_profiles.keys())       # ["alpaca", "wikitext", "sst2", "mnli"]
  matrix = np.stack([sparsity_profiles[d] for d in dist_names], axis=1)  # (32, 4)
  fig, ax = plt.subplots(figsize=(8, 10))
  sns.heatmap(matrix, ax=ax, xticklabels=dist_names, yticklabels=range(32), cmap="viridis")
  ax.set_xlabel("Distribution"); ax.set_ylabel("Layer")
  plt.tight_layout(); plt.savefig(output_path, dpi=150); plt.close()

plot_pairwise_tau_matrix(tau_results, output_path):
  dists = ["alpaca", "wikitext", "sst2", "mnli"]
  mat = np.eye(4)  # diagonal = 1.0
  for i, d1 in enumerate(dists):
    for j, d2 in enumerate(dists):
      if i < j:
        key = f"{d1}_vs_{d2}"
        tau = tau_results[key]["tau"]
        mat[i, j] = mat[j, i] = tau
  sns.heatmap(mat, annot=True, xticklabels=dists, yticklabels=dists, vmin=0, vmax=1)
  plt.savefig(output_path, dpi=150); plt.close()

generate_all_figures(...):
  os.makedirs(figures_dir, exist_ok=True)
  paths = []
  paths.append(plot_gate_metrics_bar(gate_result["icc3k"], gate_result["tau_min"],
                                     f"{figures_dir}/gate_metrics.png"))
  ... (call all 6 plot functions with corresponding output paths)
  return paths  # list of 6 file paths
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | six_plot_functions | Implement all 6 plot_* functions |
| L-5-2 | generate_all_figures | Wrapper calling all 6 with correct paths |

---

## A-6: run_experiment.py (NEW) [Complexity: 14, Budget: 2]

### API Signatures

```python
# h-m1/code/run_experiment.py
from typing import Any, Dict, Tuple
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data import DataLoader
from config import ExperimentConfig
from data_utils import load_all_dataloaders
from measure_sparsity import measure_all_distributions
from compute_icc import compute_icc3k, compute_icc_sensitivity
from compute_metrics import compute_pairwise_tau, compute_tau_min, compute_tau_sensitivity, evaluate_gate
from visualize import generate_all_figures


def setup_environment(cfg: ExperimentConfig) -> None:
    """Set numpy/torch seeds=42, create figures_dir and results parent dirs."""
    ...


def load_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load meta-llama/Llama-3.1-8B float16 device_map=auto, eval mode."""
    ...


def run_sparsity_measurement(
    model,
    dataloaders: Dict[str, DataLoader],
    cfg: ExperimentConfig,
) -> Dict[float, Dict[str, np.ndarray]]:
    """Measure sparsity for 4 distributions × 4 epsilons. Returns {eps: {dist: (32,)}}."""
    ...


def run_statistical_analysis(
    sparsity_by_epsilon: Dict[float, Dict[str, np.ndarray]],
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Compute ICC3k, pairwise tau, sensitivity, gate evaluation. Returns full results dict."""
    ...


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """Serialize results to JSON (convert numpy types to native Python)."""
    ...


def main() -> None:
    """Orchestrate: setup -> load -> measure -> analyze -> visualize -> save."""
    ...


if __name__ == "__main__":
    main()
```

### Pseudo-code (main orchestration)

```
main():
  cfg = ExperimentConfig()
  setup_environment(cfg)                         # seeds, dirs

  model, tokenizer = load_model_and_tokenizer(cfg)
  dataloaders = load_all_dataloaders(tokenizer, cfg)  # 4 DataLoaders

  # 4 epsilons × 4 distributions = 16 measurements
  sparsity_by_epsilon = run_sparsity_measurement(model, dataloaders, cfg)

  results = run_statistical_analysis(sparsity_by_epsilon, cfg)
  # results contains: primary_profiles, icc_result, tau_results, gate,
  #                   icc_sensitivity, tau_sensitivity

  generate_all_figures(
    results["primary_profiles"], results["icc_result"], results["tau_results"],
    results["gate"], results["icc_sensitivity"], results["tau_sensitivity"],
    cfg.figures_dir,
  )

  save_results(results, cfg.results_path)

  # Stdout summary
  print(f"ICC(3,k) = {results['icc_result']['icc3k']:.4f}  (threshold > 0.75)")
  for pair, vals in results["tau_results"].items():
    print(f"  tau {pair} = {vals['tau']:.4f}")
  print(f"tau_min = {results['gate']['tau_min']:.4f}  (threshold >= 0.6)")
  print(f"GATE: {results['gate']['gate_result']}")
  if results["gate"]["failed_conditions"]:
    for cond in results["gate"]["failed_conditions"]:
      print(f"  FAIL: {cond}")

run_sparsity_measurement(model, dataloaders, cfg):
  sparsity_by_epsilon = {}
  for eps in cfg.epsilons:           # [0.001, 0.01, 0.05, 0.1]
    sparsity_by_epsilon[eps] = measure_all_distributions(model, dataloaders, eps, cfg)
  return sparsity_by_epsilon

run_statistical_analysis(sparsity_by_epsilon, cfg):
  primary = sparsity_by_epsilon[cfg.primary_epsilon]  # epsilon=0.01
  icc_result = compute_icc3k(primary)
  tau_results = compute_pairwise_tau(primary)
  gate = evaluate_gate(icc_result["icc3k"], tau_results, cfg)
  icc_sensitivity = compute_icc_sensitivity(sparsity_by_epsilon)
  tau_sensitivity = compute_tau_sensitivity(sparsity_by_epsilon)
  return {
    "primary_profiles": primary,
    "sparsity_by_epsilon": sparsity_by_epsilon,
    "icc_result": icc_result,
    "tau_results": tau_results,
    "gate": gate,
    "icc_sensitivity": icc_sensitivity,
    "tau_sensitivity": tau_sensitivity,
  }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | setup_load_measure | setup_environment, load_model_and_tokenizer, run_sparsity_measurement |
| L-6-2 | analyze_save_main | run_statistical_analysis, save_results, main() |

---

## Tensor Shapes Summary

| Variable | Shape | Note |
|----------|-------|------|
| input_ids (batch) | `[8, 512]` | batch_size=8, max_length=512 |
| hidden states | `[8, 512, 4096]` | LLaMA-3.1-8B hidden_size |
| gate_proj output | `[8, 512, 14336]` | intermediate_size=14336 |
| sparsity scalar per batch | scalar | mean of `abs < epsilon` over all elements |
| per-layer sparsity | `(32,)` | mean over all batches in one distribution |
| sparsity_profiles dict | `{str: (32,)}` × 4 | 4 distributions |
| sparsity_by_epsilon | `{float: {str: (32,)}}` | 4 eps × 4 dists = 16 arrays |
| ICC DataFrame | `(128, 3)` | 4 dists × 32 layers, cols=[layer, distribution, sparsity] |
| pairwise tau results | `{str: {tau, pval}}` × 6 | C(4,2)=6 pairs |

---

## Subtask Budget Summary [13/13 used]

| ID | Task | Budget Used |
|----|------|-------------|
| L-1-1 | sst2_mnli_loaders | 1 |
| L-1-2 | load_all_dataloaders | 1 |
| L-2-1 | copy_h-e1_sparsity | 1 |
| L-2-2 | measure_all_distributions | 1 |
| L-3-1 | build_icc_dataframe | 1 |
| L-3-2 | compute_icc3k | 1 |
| L-3-3 | compute_icc_sensitivity | 1 |
| L-4-1 | pairwise_tau | 1 |
| L-4-2 | evaluate_gate | 1 |
| L-5-1 | six_plot_functions | 1 |
| L-5-2 | generate_all_figures | 1 |
| L-6-1 | setup_load_measure | 1 |
| L-6-2 | analyze_save_main | 1 |
