# Architecture: H-M1

**Type:** MECHANISM
**Applied:** Pre/post-conversion landscape comparison pattern (SAM sharpness + Hessian eigenspectrum + KL divergence)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code (H-E1 code matches its 03_architecture.md spec exactly - no drift)
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** `model.py` provides `load_baseline_model`, `MambaWithLoRA`, `load_proposed_model` — reusable as-is for landscape measurement. `data.py` provides `load_benchmark`/`format_for_causal_lm` — reusable for GSM8K/NQ loading. `config.py` LORA_CONFIG_* and BENCHMARKS dicts reusable.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_baseline_model | `from h_e1.code.model import load_baseline_model` | `h-e1/code/model.py` |
| load_proposed_model | `from h_e1.code.model import load_proposed_model` | `h-e1/code/model.py` |
| MambaWithLoRA | `from h_e1.code.model import MambaWithLoRA` | `h-e1/code/model.py` |
| load_benchmark | `from h_e1.code.data import load_benchmark` | `h-e1/code/data.py` |
| format_for_causal_lm | `from h_e1.code.data import format_for_causal_lm` | `h-e1/code/data.py` |
| LORA_CONFIG_TRANSFORMER/MAMBA | `from h_e1.code.config import LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA` | `h-e1/code/config.py` |

**Verified from**: `h-e1/code/` (actual implementation, matches spec)

---

## Module Structure

```
h-m1/code/
├── config.py
├── data.py         (thin re-export/subset wrapper over h-e1 data.py)
├── landscape.py     (SAM sharpness + Hessian eigen analysis)
├── metrics.py        (KL divergence, spectral norm/trace ratios)
├── run_experiment.py
└── visualize.py
```

### config.py

**Dependencies**: none

```python
LANDSCAPE_CONFIG = dict(sam_epsilon=0.05, hessian_top_k=50,
    num_bins=50, kl_eps=1e-10, batch_size=16, grad_accum=4, seed=42)
DATASETS = {
    "gsm8k": dict(hf_id="gsm8k", subset="main", split="test[:500]"),
    "nq": dict(hf_id="natural_questions", subset=None, split="validation[:500]"),
}
```

### data.py (`code/data.py`)

**Dependencies**: config.py, h_e1.code.data

```python
def load_landscape_eval_set(name: str, tokenizer, max_length: int = 512) -> "DataLoader":
    """Wraps h_e1.code.data.load_benchmark + format_for_causal_lm; batch_size=16"""
    ...
```

### landscape.py (`code/landscape.py`)

**Dependencies**: config.py

```python
def compute_loss(model: "nn.Module", dataloader: "DataLoader") -> "Tensor": ...

def measure_sharpness_sam(model: "nn.Module", dataloader: "DataLoader",
                           epsilon: float = 0.05) -> float:
    """SAM perturbation: L(w+eps*grad/||grad||) - L(w). Restores original params."""
    ...

def compute_hessian_eigenvalues(model: "nn.Module", dataloader: "DataLoader",
                                 top_k: int = 50) -> dict:
    """PyHessian power iteration. Returns {'eigenvalues': list, 'trace': float, 'spectral_norm': float}"""
    ...
```

### metrics.py (`code/metrics.py`)

**Dependencies**: config.py

```python
def compute_kl_divergence(eig_pre: "np.ndarray", eig_post: "np.ndarray",
                           num_bins: int = 50, eps: float = 1e-10) -> float:
    """Bins eigenvalues, computes scipy.stats.entropy(hist_pre, hist_post)"""
    ...

def spectral_norm_ratio(eig_pre: dict, eig_post: dict) -> float: ...
def trace_ratio(eig_pre: dict, eig_post: dict) -> float: ...

def check_gate_conditions(sharpness_transformer: float, sharpness_mamba: float,
                           kl_div: float) -> dict:
    """primary_pass: |delta|/sharpness_transformer > 0.10; secondary_pass: kl_div > 0.1"""
    ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: metrics.py

```python
def plot_eigenvalue_distribution(eig_transformer: list, eig_mamba: list, out_path: str) -> None: ...
def plot_sharpness_comparison(sharpness_transformer: dict, sharpness_mamba: dict, out_path: str) -> None: ...
def plot_eigenvalue_spectrum(eig_transformer: list, eig_mamba: list, out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config.py, data.py, landscape.py, metrics.py, visualize.py, h_e1.code.model

```python
def main() -> dict:
    """Load transformer+mamba models via h_e1 loaders, load GSM8K+NQ eval sets,
    measure sharpness+hessian per model per dataset, compute KL/gate, save figures+report"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup & data loading | Wrap h-e1 data.py for GSM8K/NQ 500-sample landscape eval sets, batch=16 | 6 | 2+2+1+1 |
| M-2 | Load transformer + mamba models | Reuse h-e1 load_baseline_model/load_proposed_model, verify both loadable with LoRA configs | 5 | 1+3+0+1 |
| M-3 | SAM sharpness measurement | Implement measure_sharpness_sam: grad-direction perturbation, base/perturbed loss, param restore | 9 | 3+1+3+2 |
| M-4 | Hessian eigenvalue analysis | Integrate PyHessian, compute top-50 eigenvalues + trace via power iteration | 10 | 3+3+3+1 |
| M-5 | KL divergence + secondary metrics | Bin eigenvalues, compute KL divergence, spectral norm ratio, trace ratio | 6 | 2+1+2+1 |
| M-6 | Gate check logic | Implement check_gate_conditions per PRD formula (sharpness_delta_pct, kl_div thresholds) | 4 | 1+1+1+1 |
| M-7 | Visualization | 3 figures: eigenvalue histogram overlay, sharpness bar chart, log-scale eigenvalue spectrum | 5 | 2+1+1+1 |
| M-8 | End-to-end integration run | Wire config->data->model(h-e1)->landscape->metrics->visualize->gate report for both datasets x both models | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-4, M-8], Low(4-8): [M-1, M-2, M-5, M-6, M-7]
