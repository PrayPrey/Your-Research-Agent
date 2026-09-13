# Architecture: H-M1
# SSD Frobenius Error Scaling Gate Experiment

**Hypothesis:** H-M1 | **Type:** MECHANISM (Day 0 Gate) | **Date:** 2026-08-03

Applied: per-sample Adam optimization loop (MOHAWK Stage 1 pattern)
Applied: layer-at-a-time OOM-safe forward pass pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. All patterns sourced from `goombalab/phi-mamba/assets/mohawk_stage1.py` (official MOHAWK paper author code).

---

## Module Overview

- `data.py` — C4 sampling, tokenization, attention matrix extraction from LLaMA-3-8B
- `ssd_fitter.py` — SSD block init, 10k-step Adam fitting loop, Frobenius error measurement, Toeplitz baseline
- `analysis.py` — log-log slope regression, percentile computation, gate check
- `visualize.py` — 4 required figures
- `experiment.py` — outer orchestration loop (samples × lengths × layers), results persistence
- `config.py` — single fixed config dataclass

---

## File Organization

```
h-m1/
  code/
    config.py
    data.py
    ssd_fitter.py
    analysis.py
    visualize.py
    experiment.py
    run.py
  results/
    errors_by_N.pkl
    gate_metrics.json
  figures/
    fig1_gate_bar_loglog.png
    fig2_scaling_ssd_vs_toeplitz.png
    fig3_violin_distribution.png
    fig4_layer_heatmap.png
```

---

## Module Dependencies

```
run.py → experiment.py → data.py
                       → ssd_fitter.py
                       → analysis.py
                       → visualize.py
                       → config.py
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies:** none

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    seed: int = 42
    n_samples: int = 500
    target_lengths: List[int] = (512, 1024, 2048, 4096, 8192)
    n_layers: int = 32
    d_model: int = 4096
    d_state: int = 64
    n_heads: int = 32
    n_opt_steps: int = 10000
    lr: float = 1e-3
    teacher_model_id: str = "meta-llama/Llama-3-8B"
    dataset_id: str = "allenai/c4"
    gate_slope_threshold: float = 0.5
    gate_pct90_threshold: float = 0.3
    results_dir: str = "results"
    figures_dir: str = "figures"
```

---

### DataPipeline (`code/data.py`)

**Dependencies:** Config, transformers, datasets, torch

```python
class DataPipeline:
    def __init__(self, cfg: Config): ...

    def load_teacher(self) -> tuple:
        # Returns (model, tokenizer) — bfloat16, device_map="cuda", output_attentions=True
        ...

    def sample_sequences(self, seq_len: int) -> torch.Tensor:
        # Returns (n_samples, seq_len) token tensor; fixed seed=42
        ...

    def extract_attention_matrices(
        self,
        model,
        input_ids: torch.Tensor,
        seq_len: int,
        sample_idx: int,
    ) -> torch.Tensor:
        # Returns (n_layers, seq_len, seq_len) — 1 random head per layer
        # Processes one layer at a time to avoid OOM
        # Returns bfloat16 tensors
        ...
```

---

### SSDFitter (`code/ssd_fitter.py`)

**Dependencies:** Config, torch, mamba_ssm

```python
class SSDFitter:
    def __init__(self, cfg: Config): ...

    def fit_and_measure(
        self,
        attn_matrix: torch.Tensor,
        hidden_states: torch.Tensor,
        log_loss_curve: bool = False,
    ) -> tuple[float, list[float]]:
        # attn_matrix: (seq_len, seq_len) bfloat16 → cast to fp32 inside
        # hidden_states: (1, seq_len, d_model) from teacher
        # Returns (final_frobenius_error, loss_curve_if_requested)
        # 10k Adam steps, lr=1e-3
        ...

    def toeplitz_error(self, attn_matrix: torch.Tensor) -> float:
        # Toeplitz baseline approximation error (secondary metric FR-6)
        ...

def verify_mechanism_activated(
    transfer_matrix: torch.Tensor,
    attn_matrix: torch.Tensor,
    seq_len: int,
    loss_curve: list[float],
) -> tuple[bool, dict]:
    # shape_correct, matrix_differs, loss_decreased>=10%, loss_finite
    ...
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** numpy

```python
def compute_log_log_slope(errors_by_N: dict[int, list[float]]) -> float:
    # np.polyfit(log(Ns), log(mean_errors), 1)[0]
    ...

def compute_pct90_at_8k(errors_by_N: dict[int, list[float]]) -> float:
    # np.percentile(errors_by_N[8192], 90)
    ...

def gate_check(beta: float, pct90: float, cfg: Config) -> dict:
    # Returns {"pass": bool, "beta": float, "pct90": float, "decision": "PASS"|"STOP"}
    ...

def compute_mean_errors(errors_by_N: dict[int, list[float]]) -> dict[int, float]:
    # mean Frobenius error per N across all samples × layers
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy, analysis

```python
def plot_gate_metrics(
    errors_by_N: dict[int, list[float]],
    gate_result: dict,
    out_dir: str,
) -> None:
    # Fig 1: bar chart pct90 per N vs 0.3 threshold + log-log curve with slope annotation
    ...

def plot_scaling_comparison(
    ssd_errors_by_N: dict[int, list[float]],
    toeplitz_errors_by_N: dict[int, list[float]],
    beta: float,
    out_dir: str,
) -> None:
    # Fig 2: log-log plot SSD vs Toeplitz lines + regression line + slope annotation
    ...

def plot_violin_distribution(
    errors_by_N: dict[int, list[float]],
    out_dir: str,
) -> None:
    # Fig 3: violin per N, 90th pct threshold line
    ...

def plot_layer_heatmap(
    layer_errors_8k: list[float],
    out_dir: str,
) -> None:
    # Fig 4: per-layer mean Frobenius error at N=8k (32 layers)
    ...
```

---

### Experiment (`code/experiment.py`)

**Dependencies:** Config, DataPipeline, SSDFitter, analysis, visualize, pickle, json, tqdm

```python
class Experiment:
    def __init__(self, cfg: Config): ...

    def run(self) -> dict:
        # Outer loop: for seq_len in target_lengths:
        #   for sample_idx in range(n_samples):
        #     extract attention matrices (all layers at once per sample but layer-by-layer in memory)
        #     for layer_idx in range(n_layers):
        #       fit SSD, record frobenius error, toeplitz error
        # Returns {"errors_by_N": ..., "toeplitz_by_N": ..., "layer_errors_8k": ...}
        ...

    def _save_results(self, errors_by_N: dict, gate_result: dict) -> None:
        # pickle errors_by_N → results/errors_by_N.pkl
        # json gate_metrics → results/gate_metrics.json
        ...

    def _report_gate(self, gate_result: dict) -> None:
        # Print "GATE: PASS" or "GATE: STOP" with beta and pct90 values
        ...
```

---

### Entry Point (`code/run.py`)

**Dependencies:** Config, Experiment

```python
def main() -> None:
    cfg = Config()
    exp = Experiment(cfg)
    results = exp.run()
    # gate check, save, visualize, print decision
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup & Config | File structure, dependencies, Config dataclass, run.py entry point | 5 | 1+1+1+2 |
| A-2 | Data Pipeline: C4 Sampling | C4 streaming load, tokenization, truncate/pad to each N, fixed seed=42 | 8 | 2+2+2+2 |
| A-3 | Teacher Attention Extraction | LLaMA-3-8B bfloat16 load, forward pass, per-layer attention extraction, 1 head random select, OOM handling | 14 | 3+3+4+4 |
| A-4 | SSD Fitter Core | Mamba-2 SSD block init, 10k Adam loop, Frobenius loss, fp32 precision, loss curve logging | 15 | 4+3+4+4 |
| A-5 | Mechanism Verification | Shape checks, loss-decrease ≥10% guard, finite-loss guard, fail-fast on mismatch | 9 | 2+2+3+2 |
| A-6 | Toeplitz Baseline | Toeplitz approximation error computation for secondary metric (FR-6) | 9 | 2+2+3+2 |
| A-7 | Experiment Orchestration | Outer loop (samples × lengths × layers), tqdm progress, intermediate checkpointing | 13 | 3+3+3+4 |
| A-8 | Scaling Analysis & Gate | log-log slope via np.polyfit, pct90 computation, gate decision logic, print PASS/STOP | 9 | 2+2+3+2 |
| A-9 | Results Persistence | pickle errors_by_N, JSON gate_metrics, directory creation | 5 | 1+1+1+2 |
| A-10 | Visualization (4 Figures) | Bar chart, log-log scaling plot, violin distributions, per-layer heatmap; all saved to figures/ | 12 | 3+2+4+3 |

**Distribution**: High(14-17): [A-3, A-4], Medium(9-13): [A-5, A-6, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-9]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.1.0 | Tensor ops, Adam, linalg.matrix_norm |
| transformers | >=4.40.0 | LLaMA-3-8B load + tokenizer |
| datasets | >=2.18.0 | C4 streaming |
| mamba_ssm | >=1.2.0 | Mamba2 SSD block + transfer matrix |
| numpy | >=1.24.0 | polyfit, percentile |
| matplotlib | >=3.7.0 | Figures 1-4 |
| seaborn | >=0.12.0 | Violin plots (Fig 3) |
| tqdm | >=4.65.0 | Progress bars |

**Reference implementation:** `goombalab/phi-mamba/assets/mohawk_stage1.py`
