# Architecture: H-M3 Sparsity-Rank Sensitivity Correlation

**Generated:** 2026-05-08
**Hypothesis:** H-M3 (MECHANISM)
**Type:** Incremental (depends on h-m1 + h-m2)

Applied: LoRA rank_pattern API (HF PEFT conceptual guide)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-m2)
**Status**: Analyzed via direct file reads (Serena MCP had no active project; files read directly)
**Analyzed Path**: `docs/youra_research/20260508_scope/h-m2/code/` and `h-m1/code/`

**Findings**:
- h-m2 has: `config.py`, `data_utils.py`, `measure_sparsity.py`, `compute_metrics.py`, `visualize.py`, `run_experiment.py`, `tests/`
- h-m2 `data_utils.py` provides `load_alpaca_dataloader`, `load_wikitext_dataloader` (Alpaca/WikiText only, NOT GLUE)
- h-m2 `measure_sparsity.py` provides `measure_layer_sparsity`, `register_hooks`, `measure_all_epsilons` — forward-pass based measurement
- h-m2 `config.py` defines `ExperimentConfig` dataclass (model_name, n_layers=32, epsilons, etc.)
- h-m2 `run_experiment.py` uses `from config import ExperimentConfig` (local import within code/ dir)
- **GLUE loading is NOT in h-m2 data_utils** — must be implemented in h-m3

---

## External Dependencies (Base Hypothesis)

| Module | Function/Class | File Location | Import Path |
|--------|---------------|---------------|-------------|
| load_sparsity_profiles | load sparsity from JSON | h-m2/experiment_results.json | (data file, not import) |
| measure_layer_sparsity | sparsity forward pass | h-m2/code/measure_sparsity.py | `sys.path` + `from measure_sparsity import measure_layer_sparsity` |
| ExperimentConfig (reference) | dataclass config | h-m2/code/config.py | Not reused — h-m3 defines own config |

**Verified from**: `/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/code/`

**Note**: h-m2 `data_utils.py` does NOT contain GLUE loading. h-m3 must implement its own GLUE data utilities. Only `measure_sparsity.py` (sparsity loading helper) is partially reusable.

---

## File Structure

```
h-m3/code/
├── config.py                    # H-M3 ExperimentConfig dataclass
├── data_utils.py                # GLUE SST-2 + MNLI loading/tokenization + sparsity loader
├── lora_trainer.py              # Uniform LoRA training + gradient norm + ΔW extraction
├── sensitivity_sweep.py         # Stream 1: joint rank perturbation engine (320 runs)
├── adalora_runner.py            # Stream 2: AdaLoRA reference training + rank_pattern extraction
├── spectral_analysis.py         # Stream 3: ΔW SVD + multiple regression + semipartial r²
├── correlation_analysis.py      # Pearson r, Kendall tau, gate evaluation, R6 fallback
├── visualize.py                 # All 6 required figures → h-m3/figures/
├── results_logger.py            # JSON results aggregation + 04_validation.md generation
├── run_experiment.py            # Top-level orchestrator: runs streams 1→2→3→gate
└── tests/
    ├── conftest.py
    ├── test_config.py
    ├── test_data_utils.py
    ├── test_lora_trainer.py
    ├── test_sensitivity_sweep.py
    ├── test_adalora_runner.py
    ├── test_spectral_analysis.py
    ├── test_correlation_analysis.py
    └── test_visualize.py
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: None (stdlib only)

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "meta-llama/Llama-3.1-8B"
    n_layers: int = 32
    torch_dtype: str = "bfloat16"

    # Training
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])
    lora_r: int = 16
    lora_alpha: int = 16
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])
    lr: float = 2e-4
    weight_decay: float = 0.01
    batch_size: int = 16
    num_epochs: int = 3
    warmup_ratio: float = 0.03
    delta_r: int = 2

    # AdaLoRA
    adalora_target_r: int = 9
    adalora_init_r: int = 16
    adalora_tinit: int = 100
    adalora_tfinal: int = 1500
    adalora_deltaT: int = 10
    adalora_beta1: float = 0.85
    adalora_beta2: float = 0.85
    adalora_orth_reg_weight: float = 0.5

    # Spectral
    top_k_svs: int = 4

    # Paths
    h_m2_results_path: str = "..."   # absolute path to h-m2/experiment_results.json
    figures_dir: str = "..."
    results_path: str = "..."
    validation_report_path: str = "..."

    # Gate thresholds
    pearson_r_threshold: float = -0.4
    kendall_tau_threshold: float = 0.4
    unique_var_threshold: float = 0.20
    p_value_threshold: float = 0.05
    sensitive_drop_threshold: float = 0.005
    r6_min_sensitive_layers: int = 5

    def __post_init__(self): ...
```

---

### DataUtils (`data_utils.py`)

**Dependencies**: config.py

```python
import torch
from torch.utils.data import DataLoader
from typing import Dict, List
import numpy as np

class GlueDataset(torch.utils.data.Dataset):
    def __init__(self, encodings: dict, labels: List[int]): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def load_sparsity_profiles(h_m2_results_path: str) -> np.ndarray:
    """Load sparsity[layer_name→float] from h-m2/experiment_results.json["sparsity_profiles"]["0.01"].
    Returns: np.ndarray shape (32,), ordered by layer index."""
    ...

def load_glue_dataloader(
    task: str,          # "sst2" or "mnli"
    split: str,         # "train" or "validation"
    tokenizer,
    cfg: "ExperimentConfig",
) -> DataLoader:
    """Load GLUE SST-2 or MNLI, tokenize, return DataLoader."""
    ...

def get_num_labels(task: str) -> int:
    """Returns 2 for sst2, 3 for mnli."""
    ...
```

---

### LoraTrainer (`lora_trainer.py`)

**Dependencies**: config.py, data_utils.py

```python
import torch
from typing import Dict, Tuple
import numpy as np
from peft import LoraConfig, get_peft_model

def load_base_model(cfg: "ExperimentConfig", num_labels: int):
    """Load LLaMA-3.1-8B from local cache with local_files_only=True, bfloat16."""
    ...

def load_tokenizer(cfg: "ExperimentConfig"):
    """Load LlamaTokenizer from local cache."""
    ...

def train_uniform_lora(
    task: str,
    seed: int,
    cfg: "ExperimentConfig",
    return_delta_w: bool = True,
    return_grad_norms: bool = True,
) -> Dict:
    """Fine-tune uniform r=16 LoRA on task with seed.
    Returns: {
        "accuracy": float,
        "delta_w": Dict[str, torch.Tensor],   # layer_name → ΔW = B@A
        "grad_norms": Dict[str, float],        # layer_name → Frobenius norm
    }"""
    ...

def compute_delta_w(model) -> Dict[str, torch.Tensor]:
    """Extract ΔW = B @ A for each LoRA adapter layer post-training."""
    ...

def compute_grad_norms(model) -> Dict[str, float]:
    """Compute Frobenius norm of gradients per MLP layer during/after training."""
    ...

def evaluate_model(model, dataloader, task: str, cfg: "ExperimentConfig") -> float:
    """Evaluate on validation set; return accuracy."""
    ...
```

---

### SensitivitySweep (`sensitivity_sweep.py`)

**Dependencies**: config.py, data_utils.py, lora_trainer.py

```python
import numpy as np
from typing import Dict, List
from peft import LoraConfig

def build_joint_rank_pattern(
    perturbed_layer_idx: int,
    delta_r: int,
    r_base: int,
    n_layers: int,
    target_modules: List[str],
) -> Dict[str, int]:
    """Build budget-neutral rank_pattern: reduce layer_idx by delta_r,
    redistribute 2*cost proportionally to remaining 31 layers."""
    ...

def run_sensitivity_sweep(
    task: str,
    cfg: "ExperimentConfig",
    baseline_accs: Dict[int, float],
) -> np.ndarray:
    """Run 32 × 5 = 160 perturbed fine-tuning runs for one task.
    Returns: accuracy_drop[32] averaged over 5 seeds."""
    ...

def run_all_sensitivity_sweeps(
    cfg: "ExperimentConfig",
    baseline_accs: Dict[str, Dict[int, float]],
) -> Dict[str, np.ndarray]:
    """Run sweeps for both sst2 and mnli.
    Returns: {"sst2": np.ndarray(32,), "mnli": np.ndarray(32,)}"""
    ...

def identify_sensitive_layers(
    accuracy_drops: np.ndarray,
    threshold: float,
) -> np.ndarray:
    """Returns boolean mask of sensitive layers (drop >= threshold)."""
    ...

def check_delta_r_fallback(
    accuracy_drops: np.ndarray,
    threshold: float,
    cfg: "ExperimentConfig",
) -> int:
    """Return delta_r=4 if no sensitive layers found, else delta_r from config."""
    ...
```

---

### AdaLoraRunner (`adalora_runner.py`)

**Dependencies**: config.py, data_utils.py, lora_trainer.py

```python
from typing import Dict, List
import numpy as np
from peft import AdaLoraConfig, get_peft_model

def run_adalora(
    task: str,
    seed: int,
    cfg: "ExperimentConfig",
) -> Dict[str, int]:
    """Train AdaLoRA at 60% budget; return model.base_model.rank_pattern."""
    ...

def run_all_adalora(
    cfg: "ExperimentConfig",
) -> Dict[str, Dict[str, int]]:
    """Run AdaLoRA for sst2 + mnli, 5 seeds each.
    Returns: {"sst2": rank_pattern_avg, "mnli": rank_pattern_avg}"""
    ...

def extract_rank_pattern(model) -> Dict[str, int]:
    """Extract per-layer effective rank from model.base_model.rank_pattern."""
    ...

def rank_pattern_to_array(
    rank_pattern: Dict[str, int],
    n_layers: int,
) -> np.ndarray:
    """Convert rank_pattern dict to ordered (32,) array by layer index."""
    ...

def check_uniform_allocation(rank_pattern_array: np.ndarray) -> bool:
    """Returns True if all allocations equal — AdaLoRA failed to learn heterogeneous."""
    ...
```

---

### SpectralAnalysis (`spectral_analysis.py`)

**Dependencies**: config.py

```python
import torch
import numpy as np
from typing import Dict, Tuple
from sklearn.linear_model import LinearRegression

def compute_spectral_decay_ratio(
    delta_w: torch.Tensor,
    top_k: int = 4,
) -> float:
    """Covariance-based SVD via eigvalsh on smaller dim of WᵀW or WWᵀ.
    Returns: sum(top-k SVs) / Frobenius norm."""
    ...

def compute_all_spectral_decays(
    delta_w_dict: Dict[str, torch.Tensor],
    cfg: "ExperimentConfig",
) -> np.ndarray:
    """Compute spectral_decay_ratio for all 32 MLP layers.
    Returns: np.ndarray shape (32,)"""
    ...

def run_multiple_regression(
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    spectral_decay: np.ndarray,
) -> Dict:
    """Fit [sparsity, grad_norm] → spectral_decay via LinearRegression.
    Returns: {
        "r2_full": float,
        "r2_grad_only": float,
        "unique_var_sparsity": float,    # semipartial r² for sparsity
        "p_value_sparsity_beta": float,
        "coef_sparsity": float,
        "coef_grad_norm": float,
    }"""
    ...

def compute_semipartial_r2(
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    spectral_decay: np.ndarray,
) -> Tuple[float, float]:
    """Returns (unique_var_sparsity, p_value_sparsity_beta)."""
    ...
```

---

### CorrelationAnalysis (`correlation_analysis.py`)

**Dependencies**: config.py

```python
import numpy as np
from typing import Dict, Tuple
from scipy.stats import pearsonr, kendalltau

def compute_pearson_r(
    sparsity: np.ndarray,
    accuracy_drops: np.ndarray,
    sensitive_mask: np.ndarray,
) -> Tuple[float, float]:
    """Pearson r on sensitive layers only. Returns (r, p_value)."""
    ...

def compute_kendall_tau(
    sparsity: np.ndarray,
    adalora_ranks: np.ndarray,
) -> Tuple[float, float]:
    """Kendall's tau (variant='b') across all 32 layers.
    Sparsity ascending = rank 1 (highest sparsity); AdaLoRA descending = rank 1 (highest rank).
    Returns (tau, p_value)."""
    ...

def evaluate_gate(
    pearson_r_sst2: float,
    pearson_r_mnli: float,
    kendall_tau_sst2: float,
    kendall_tau_mnli: float,
    unique_var_sparsity: float,
    p_value_sparsity_beta: float,
    n_sensitive_sst2: int,
    cfg: "ExperimentConfig",
) -> Dict:
    """Evaluate all gate conditions including R6 fallback.
    Returns: {
        "gate_pearson": bool,
        "gate_tau": bool,
        "gate_spectral": bool,
        "gate_pass": bool,
        "r6_fallback": bool,
        "all_metrics": dict,
    }"""
    ...

def check_r6_fallback(n_sensitive_sst2: int, cfg: "ExperimentConfig") -> bool:
    """Returns True if SST-2 < 5 sensitive layers."""
    ...
```

---

### Visualize (`visualize.py`)

**Dependencies**: config.py

```python
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict

def plot_gate_metrics_comparison(
    pearson_r: Dict[str, float],
    kendall_tau: Dict[str, float],
    unique_var: float,
    thresholds: Dict,
    output_dir: str,
) -> None:
    """Bar chart: gate metrics vs. thresholds for SST-2 and MNLI. (Mandatory)"""
    ...

def plot_sparsity_vs_sensitivity(
    sparsity: np.ndarray,
    accuracy_drops: Dict[str, np.ndarray],
    sensitive_masks: Dict[str, np.ndarray],
    pearson_results: Dict,
    output_dir: str,
) -> None:
    """Scatter: per-layer sparsity vs. sensitivity; highlight sensitive layers."""
    ...

def plot_sensitivity_heatmap(
    accuracy_drops: Dict[str, np.ndarray],
    sparsity: np.ndarray,
    output_dir: str,
) -> None:
    """32 × 2 heatmap (layers × tasks) with sparsity overlay."""
    ...

def plot_adalora_allocation(
    adalora_ranks: Dict[str, np.ndarray],
    sparsity: np.ndarray,
    kendall_tau: Dict[str, float],
    output_dir: str,
) -> None:
    """Bar chart: AdaLoRA allocation vs. sparsity-predicted allocation."""
    ...

def plot_spectral_vs_sparsity(
    spectral_decay: np.ndarray,
    sparsity: np.ndarray,
    grad_norms: np.ndarray,
    regression_results: Dict,
    output_dir: str,
) -> None:
    """Scatter: ΔW spectral decay vs. sparsity; regression line + 95% CI."""
    ...

def plot_sensitivity_histogram(
    accuracy_drops: Dict[str, np.ndarray],
    threshold: float,
    output_dir: str,
) -> None:
    """Histogram of per-layer accuracy drops with ≥0.5% threshold line."""
    ...

def generate_all_figures(
    results: Dict,
    cfg: "ExperimentConfig",
) -> None:
    """Call all 6 plot functions. Save to cfg.figures_dir."""
    ...
```

---

### ResultsLogger (`results_logger.py`)

**Dependencies**: config.py

```python
import json
from typing import Dict

def save_results_json(results: Dict, path: str) -> None:
    """Save all experiment results to h-m3/experiment_results.json."""
    ...

def generate_validation_report(
    results: Dict,
    gate_result: Dict,
    cfg: "ExperimentConfig",
    output_path: str,
) -> None:
    """Generate 04_validation.md with gate evaluation, metrics, and PASS/FAIL status."""
    ...

def log_sensitivity_indicators(
    layer_idx: int,
    accuracy_drop: float,
    sensitive_threshold: float,
) -> None:
    """Print: [SENSITIVITY] Layer {l}: accuracy_drop={drop:.4f}, sensitive={...}"""
    ...

def print_gate_summary(gate_result: Dict) -> None:
    """Print gate evaluation summary to stdout."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: All modules

```python
import sys, os
from config import ExperimentConfig
from data_utils import load_sparsity_profiles, load_glue_dataloader, load_tokenizer
from lora_trainer import train_uniform_lora
from sensitivity_sweep import run_all_sensitivity_sweeps, identify_sensitive_layers
from adalora_runner import run_all_adalora, rank_pattern_to_array
from spectral_analysis import compute_all_spectral_decays, run_multiple_regression
from correlation_analysis import compute_pearson_r, compute_kendall_tau, evaluate_gate
from visualize import generate_all_figures
from results_logger import save_results_json, generate_validation_report, print_gate_summary

def run_stream1_reference(cfg: ExperimentConfig) -> Dict:
    """Run uniform r=16 LoRA baseline: 2 tasks × 5 seeds = 10 runs.
    Returns baseline_accs, delta_w, grad_norms."""
    ...

def run_stream1_sweep(cfg: ExperimentConfig, baseline_accs: Dict) -> Dict:
    """Run joint rank sensitivity sweep: 32 × 2 × 5 = 320 runs."""
    ...

def run_stream2(cfg: ExperimentConfig) -> Dict:
    """Run AdaLoRA reference: 2 tasks × 5 seeds = 10 runs."""
    ...

def run_stream3(cfg: ExperimentConfig, stream1_results: Dict) -> Dict:
    """Spectral analysis + multiple regression on ΔW from stream 1."""
    ...

def main() -> None:
    """Orchestrate streams 1 → 2 → 3 → correlation → gate → visualize → report."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup + Config | Config dataclass, directory structure, sparsity loader, GLUE data utils | 8 | 2+1+2+3 |
| A-2 | Uniform LoRA Trainer | Base model loading, training loop, ΔW extraction, gradient norm storage | 16 | 4+3+5+4 |
| A-3 | Joint Rank Sensitivity Sweep (Stream 1) | Budget-neutral rank_pattern builder, 320-run sweep, accuracy_drop computation, delta_r fallback | 18 | 4+4+5+5 |
| A-4 | AdaLoRA Reference Runner (Stream 2) | AdaLoraConfig setup, training loop, rank_pattern extraction, uniform-check flag | 15 | 4+3+4+4 |
| A-5 | ΔW Spectral Analysis (Stream 3) | Covariance SVD, spectral_decay_ratio, multiple regression, semipartial r² | 17 | 4+3+5+5 |
| A-6 | Correlation Analysis + Gate | Pearson r on sensitive layers, Kendall tau, R6 fallback, gate evaluation | 13 | 3+3+4+3 |
| A-7 | Visualization | 6 required figures (gate metrics, scatter, heatmap, adalora bar, spectral scatter, histogram) | 10 | 2+2+3+3 |
| A-8 | Results Logging + Validation Report | JSON aggregation, 04_validation.md generation, stdout gate summary | 8 | 2+2+2+2 |
| A-9 | Experiment Orchestrator | Top-level run_experiment.py: stream sequencing, result passing, error handling | 12 | 3+3+3+3 |
| A-10 | Tests | pytest suite for all modules (unit + integration stubs) | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [A-3], High(14-17): [A-2, A-4, A-5], Medium(9-13): [A-6, A-9, A-10], Low(4-8): [A-1, A-7, A-8]

---

## Data Flow

- `h-m2/experiment_results.json["sparsity_profiles"]["0.01"]` → `data_utils.load_sparsity_profiles` → `np.ndarray(32,)`
- `run_stream1_reference` → `baseline_accs[task][seed]`, `delta_w[layer]`, `grad_norms[layer]`
- `run_stream1_sweep(baseline_accs)` → `accuracy_drops[task][32]`, `sensitive_masks[task][32]`
- `run_stream2` → `adalora_ranks[task][32]`
- `run_stream3(delta_w, grad_norms)` → `spectral_decay[32]`, regression metrics
- `correlation_analysis` → Pearson r, Kendall tau, gate result
- `generate_all_figures` + `save_results_json` + `generate_validation_report`

---

## Key Constants

- LLaMA MLP layers: 32 (indices 0–31)
- Seeds: [42, 43, 44, 45, 46]
- Tasks: ["sst2", "mnli"]
- Uniform r=16; AdaLoRA target_r=9 (≈60% budget)
- Sensitive threshold: 0.005 (0.5% accuracy drop)
- R6 fallback trigger: n_sensitive_sst2 < 5
- Total training runs: 10 (baseline) + 320 (sweep) + 10 (adalora) = 340
