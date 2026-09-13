# Architecture: H-M3

**Type:** MECHANISM
**Applied:** SAM sharpness reuse pattern (H-M2) + SVD-based effective rank measurement (Hu et al. 2021 LoRA)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code (H-M2 finetune/sharpness pipeline reusable as-is; only effective-rank + correlation logic is new)
**Analyzed Path:** `docs/youra_research/h-m2/code/`, `docs/youra_research/h-m1/code/`
**Findings:** `h-m2/code/finetune.py::finetune_on_task` already produces per-task LoRA checkpoints via `peft.get_peft_model` on `h_m1.model.MambaWithLoRA` — reuse directly, LoRA config (r=16, alpha=32) matches PRD exactly. `h-m2/code/sharpness.py::measure_task_sharpness` wraps `h_m1.landscape.measure_sharpness_sam` (scalar-returning, epsilon param) — reuse directly for FR-4. `h-m2/code/data.py::load_task_loader` already handles gsm8k+nq — reuse directly for FR-1. New work is limited to: extracting LoRA A/B matrices from the peft-wrapped model, SVD effective-rank computation, generalization-gap eval, and Spearman correlation/visualization.

---

## External Dependencies

| Module | Import Path | File Location |
|--------|-------------|----------------|
| finetune_on_task | `from h_m2.code.finetune import finetune_on_task` | `h-m2/code/finetune.py` |
| load_task_loader | `from h_m2.code.data import load_task_loader` | `h-m2/code/data.py` |
| measure_task_sharpness | `from h_m2.code.sharpness import measure_task_sharpness` | `h-m2/code/sharpness.py` |
| measure_sharpness_sam | `from h_m1.code.landscape import measure_sharpness_sam` | `h-m1/code/landscape.py` |
| load_proposed_model | `from h_m1.code.model import load_proposed_model` | `h-m1/code/model.py` |
| MambaWithLoRA | `from h_m1.code.model import MambaWithLoRA` | `h-m1/code/model.py` |
| LORA_CONFIG, TRAIN_CONFIG, BENCHMARKS | `from h_m2.code.config import LORA_CONFIG, TRAIN_CONFIG, BENCHMARKS` | `h-m2/code/config.py` |

**Verified from**: `h-m2/03_architecture.md`, `h-m2/03_logic.md` (actual implemented interfaces — note `finetune_on_task` returns `{'model', 'loss_curve', 'checkpoint_path'}` and `measure_task_sharpness` returns `{'mean_sharpness', 'per_batch'}`, both scalar/dict not classes)

**Note on H-M2 sharpness values:** PRD lists GSM8K=1.512, NQ=2.326 from H-M2 results file (`h-m2/experiment_results.json`); H-M3 re-measures sharpness at its own LoRA convergence point rather than reusing raw numbers, since LoRA training state differs.

---

## Module Structure

```
h-m3/code/
├── config.py
├── rank.py            (NEW: LoRA effective rank via SVD)
├── evaluate.py         (NEW: train/test accuracy + generalization gap)
├── correlate.py         (NEW: Spearman correlation + gate check)
├── visualize.py
└── run_experiment.py
```

Reused unchanged: `h_m2.code.data.load_task_loader`, `h_m2.code.finetune.finetune_on_task`, `h_m2.code.sharpness.measure_task_sharpness`.

### config.py

**Dependencies**: none

```python
LORA_CONFIG = dict(r=16, lora_alpha=32, target_modules=["in_proj"])
TRAIN_CONFIG = dict(lr=1e-4, epochs=5, batch_size=4, patience=2, weight_decay=0.01, grad_clip=1.0, seed=42)
SHARPNESS_CONFIG = dict(sam_epsilon=0.05, max_batches=50)
RANK_CONFIG = dict(thresholds=[0.85, 0.90, 0.95], default_threshold=0.90)
BENCHMARKS = {
    "gsm8k": dict(hf_id="gsm8k", subset="main", split="test", num_samples=1319),
    "nq": dict(hf_id="natural_questions", subset=None, split="validation", num_samples=3610),
}
SEEDS = [42, 123, 456]
GATE_THRESHOLD = 0.5  # Spearman rho
```

### rank.py (`code/rank.py`)

**Dependencies**: config.py, torch

```python
def extract_lora_matrices(model: "nn.Module") -> dict:
    """Walks peft-wrapped MambaWithLoRA, returns {module_name: (lora_A, lora_B)} for in_proj."""
    ...

def compute_effective_rank(lora_A: "Tensor", lora_B: "Tensor", threshold: float = 0.90) -> tuple:
    """delta_W = lora_B @ lora_A; SVD; effective_rank = min k s.t. cumsum(S[:k])/sum(S)>=threshold.
    Returns (effective_rank: int, singular_values: list[float])."""
    ...

def compute_model_effective_rank(model: "nn.Module", threshold: float = 0.90) -> dict:
    """Aggregates extract_lora_matrices + compute_effective_rank across target modules.
    Returns {'effective_rank': int (max/mean across modules), 'per_module': dict, 'singular_values': dict}"""
    ...
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config.py, h_m2.code.data

```python
def evaluate_accuracy(model: "nn.Module", dataloader: "DataLoader") -> float:
    """Exact-match / token-level accuracy over dataloader, no_grad."""
    ...

def compute_generalization_gap(model: "nn.Module", train_loader: "DataLoader",
                                test_loader: "DataLoader") -> dict:
    """Returns {'train_acc', 'test_acc', 'gen_gap': train_acc - test_acc}"""
    ...
```

### correlate.py (`code/correlate.py`)

**Dependencies**: config.py, scipy.stats

```python
def compute_spearman(sharpness_vals: list, rank_vals: list) -> dict:
    """scipy.stats.spearmanr; returns {'rho', 'p_value', 'gate_pass': rho > GATE_THRESHOLD}"""
    ...

def compute_gap_correlation(sharpness_vals: list, gap_vals: list) -> dict:
    """Secondary Spearman corr(sharpness, gen_gap); returns {'rho', 'p_value'}"""
    ...

def run_threshold_sensitivity(task_results: dict, thresholds: list) -> dict:
    """A-1 ablation: recompute effective_rank + rho at each threshold. Returns {threshold: rho}"""
    ...

def run_seed_sensitivity(seeds: list, run_fn: "Callable") -> dict:
    """A-2 ablation: repeat full pipeline per seed. Returns {'mean_rho', 'std_rho', 'per_seed': dict}"""
    ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: correlate.py, rank.py

```python
def plot_sharpness_vs_rank(task_metrics: dict, rho: float, out_path: str) -> None:
    """Required: scatter (sharpness, effective_rank) per task, rho annotated."""
    ...

def plot_singular_values(singular_values: dict, out_path: str) -> None:
    """Per-task SVD spectrum overlay."""
    ...

def plot_generalization_gap(task_metrics: dict, out_path: str) -> None:
    """Scatter sharpness vs gen_gap."""
    ...

def plot_training_curves(loss_curves: dict, out_path: str) -> None:
    """Per-task loss curve over epochs."""
    ...

def plot_correlation_matrix(task_metrics: dict, out_path: str) -> None:
    """Heatmap: sharpness, effective_rank, gen_gap, train_acc, test_acc pairwise corr."""
    ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config.py, h_m2.code.{data,finetune,sharpness}, rank.py, evaluate.py, correlate.py, visualize.py

```python
def main() -> dict:
    """For each task in BENCHMARKS:
       1. finetune_on_task (h_m2.finetune) to convergence
       2. measure_task_sharpness (h_m2.sharpness, 50 batches)
       3. compute_model_effective_rank (rank.py, threshold=0.90)
       4. compute_generalization_gap (evaluate.py)
       Then: compute_spearman + compute_gap_correlation (correlate.py),
       save all figures (visualize.py) to h-m3/figures/.
       Returns {'spearman_result': dict, 'task_metrics': dict, 'figures': list[str]}"""
    ...
```

---

## Proposed Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Setup & config | config.py with LORA/TRAIN/SHARPNESS/RANK configs, BENCHMARKS, seeds | 3 | 1+0+1+1 |
| M3-2 | LoRA fine-tune both tasks | Reuse h_m2.finetune_on_task for gsm8k + nq to convergence, save checkpoints | 6 | 1+2+1+2 |
| M3-3 | Sharpness measurement | Reuse h_m2.measure_task_sharpness (50 batches, eps=0.05) per task | 3 | 1+2+0+0 |
| M3-4 | LoRA matrix extraction | extract_lora_matrices from peft-wrapped model, locate in_proj A/B | 6 | 2+2+1+1 |
| M3-5 | Effective rank computation | compute_effective_rank via SVD + cumsum threshold; compute_model_effective_rank aggregation | 8 | 2+1+3+2 |
| M3-6 | Generalization gap eval | evaluate_accuracy on train/test splits, compute_generalization_gap | 6 | 2+1+2+1 |
| M3-7 | Spearman correlation + gate | compute_spearman (primary gate), compute_gap_correlation (secondary) | 5 | 1+1+2+1 |
| M3-8 | Ablations (threshold + seed) | run_threshold_sensitivity [0.85,0.90,0.95], run_seed_sensitivity [42,123,456] | 9 | 2+2+2+3 |
| M3-9 | Visualization suite | 5 plots: sharpness-vs-rank (required), SV distribution, gen gap, training curves, corr matrix | 7 | 3+1+1+2 |
| M3-10 | End-to-end integration run | Wire finetune->sharpness->rank->gap->correlate->visualize per task, orchestrate ablations | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-5(borderline low-med), M3-8, M3-10], Low(4-8): [M3-1, M3-2, M3-3, M3-4, M3-6, M3-7, M3-9]
