# Architecture: H-E1 — Effective Rank as Zero-Shot LoRA Rank Predictor

**Version**: 1.0
**Date**: 2026-08-05
**Hypothesis**: H-E1 (EXISTENCE / PoC)

Applied: HuggingFace PEFT `get_peft_model` + `LoraConfig` per-layer wrapping pattern
Applied: `torch.linalg.svdvals` + Shannon entropy erank computation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field (with archives)
**Status**: Previous archived attempts found in `docs/youra_research/_archive/`; no active `src/` or `code/` directory to reuse
**Analyzed Path**: `docs/youra_research/_archive/20260805T150802_routing_recovery/h-e1/code/`
**Findings**: Most recent archive uses flat structure (config, data_loader, model_setup, compute_importance, visualize, run_experiment). This architecture adopts a similar flat layout — proven sufficient for the task — but reorganizes responsibilities around the PARA oracle sweep as the core scaling concern.

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── config.py          # ExperimentConfig dataclass + model/dataset constants
│   ├── data.py            # MNLI + CIFAR-10 loaders, preprocessing, DataLoader factory
│   ├── erank.py           # erank(W₀) computation over all 2D weight matrices
│   ├── oracle.py          # PARA oracle sweep: per-layer rank training loop
│   ├── train.py           # Single oracle training run (one layer, one rank, one seed)
│   ├── analyze.py         # Pearson r, bootstrap CI, PR correlation, mechanism verify
│   ├── visualize.py       # Scatter plots, heatmaps, histograms, CI bar plots
│   └── run_experiment.py  # Entry point: orchestrate erank → oracle → analyze → visualize
├── results/               # JSON/CSV outputs from oracle sweep (auto-created)
├── figures/               # Saved plots (auto-created)
└── checkpoints/           # Per-(model, layer, rank, seed) checkpoint state (auto-created)
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies**: dataclasses, pathlib

```python
MODEL_CONFIGS = {
    "bert-base-uncased":           {"task": "mnli", "num_labels": 3, "target_modules": ["query", "key", "value", "dense"]},
    "microsoft/deberta-v3-base":   {"task": "mnli", "num_labels": 3, "target_modules": ["query_proj", "key_proj", "value_proj", "pos_proj"]},
    "google/vit-base-patch16-224": {"task": "cifar10", "num_labels": 10, "target_modules": ["query", "key", "value", "dense"]},
}

ORACLE_RANKS = [4, 8, 16, 32, 64]
BASELINE_RANK = 8
SEEDS = [42, 137]

@dataclass
class ExperimentConfig:
    model_name: str
    output_dir: Path
    results_dir: Path
    figures_dir: Path
    checkpoint_dir: Path
    # Training
    epochs_nlp: int = 3
    epochs_vit: int = 5
    batch_size_nlp: int = 32
    batch_size_vit: int = 128
    lr_nlp: float = 2e-5
    lr_vit: float = 1e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    max_length: int = 128
    # Oracle
    oracle_ranks: list = field(default_factory=lambda: ORACLE_RANKS)
    baseline_rank: int = BASELINE_RANK
    seeds: list = field(default_factory=lambda: SEEDS)
    # Precision
    fp32_models: tuple = ("microsoft/deberta-v3-base",)

    @classmethod
    def from_model(cls, model_name: str, base_dir: Path) -> "ExperimentConfig": ...
```

---

### Data (`code/data.py`)

**Dependencies**: config, datasets, transformers, torchvision, torch

```python
def load_mnli(tokenizer, max_length: int = 128, batch_size: int = 32) -> tuple[DataLoader, DataLoader]:
    """Returns (train_loader, val_matched_loader)."""
    ...

def load_cifar10(batch_size: int = 128) -> tuple[DataLoader, DataLoader]:
    """Returns (train_loader, test_loader). Applies 224x224 resize + ImageNet norm."""
    ...

def get_data_loaders(model_name: str, tokenizer, cfg: ExperimentConfig) -> tuple[DataLoader, DataLoader]:
    """Dispatch to load_mnli or load_cifar10 based on model_name."""
    ...
```

---

### Erank (`code/erank.py`)

**Dependencies**: torch, transformers, config

```python
def compute_erank(W: torch.Tensor, eps: float = 1e-10) -> float:
    """erank(W) = exp(-sum(p * log(p))), p = svdvals / sum(svdvals). fp32 only."""
    ...

def compute_erank_map(model_name: str) -> dict[str, float]:
    """
    Load pretrained model (no task head), iterate named_parameters(),
    skip non-2D / embedding / norm layers, return {param_name: erank}.
    Expected: ≥60 entries per model.
    """
    ...

def save_erank_map(erank_map: dict[str, float], path: Path) -> None: ...
def load_erank_map(path: Path) -> dict[str, float]: ...
```

---

### Train (`code/train.py`)

**Dependencies**: config, data, torch, transformers, peft

```python
def build_oracle_model(
    model_name: str,
    target_layer: str,
    target_rank: int,
    baseline_rank: int = 8,
    cfg: ExperimentConfig = None,
) -> tuple[nn.Module, object]:
    """
    Wrap pretrained model with PEFT LoRA:
      - target_layer at target_rank (trainable)
      - all other target_modules at baseline_rank (frozen)
    Returns (peft_model, tokenizer_or_processor).
    DeBERTa: force fp32. BERT/ViT: fp16 acceptable.
    """
    ...

def train_one_run(
    model_name: str,
    target_layer: str,
    target_rank: int,
    seed: int,
    cfg: ExperimentConfig,
) -> float:
    """
    Full training run for one (model, layer, rank, seed) point.
    Returns val_accuracy. Saves checkpoint on completion.
    Skips if checkpoint already exists (resume support).
    """
    ...
```

---

### Oracle (`code/oracle.py`)

**Dependencies**: config, train, pathlib, json, tqdm, concurrent.futures

```python
def get_checkpoint_path(cfg: ExperimentConfig, layer: str, rank: int, seed: int) -> Path:
    """Deterministic checkpoint path for resume logic."""
    ...

def is_done(cfg: ExperimentConfig, layer: str, rank: int, seed: int) -> bool:
    """Check if result JSON already exists — skip on resume."""
    ...

def run_oracle_sweep(
    cfg: ExperimentConfig,
    erank_map: dict[str, float],
    max_workers: int = 1,
) -> dict[str, int]:
    """
    For each layer in erank_map × ORACLE_RANKS × SEEDS:
      - Skip if checkpoint exists
      - Call train_one_run(layer, rank, seed)
      - Save result to checkpoints/
    After sweep: oracle_rank[layer] = argmax_r(mean_acc over seeds).
    Returns oracle_rank_map {layer_name: int}.
    Sequential by default (max_workers=1); set >1 for multi-GPU parallelism.
    # ponytail: sequential sweep, switch max_workers to GPU count for parallel oracle runs
    """
    ...

def load_or_resume_oracle(cfg: ExperimentConfig) -> dict[str, dict]:
    """Load all completed oracle run results from checkpoints/."""
    ...

def compute_oracle_rank_map(all_results: dict, oracle_ranks: list) -> dict[str, int]:
    """Aggregate seed mean accuracies → argmax per layer."""
    ...
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: scipy, numpy, config

```python
def pearson_one_tailed(x: list[float], y: list[float]) -> tuple[float, float]:
    """Returns (r, one_tailed_p). one_tailed_p = pearsonr().pvalue / 2."""
    ...

def bootstrap_ci(
    x: list[float], y: list[float], n_resamples: int = 1000, seed: int = 42
) -> tuple[float, float]:
    """Returns (ci_low, ci_high) for Pearson r at 95% confidence."""
    ...

def participation_ratio(W: torch.Tensor) -> float:
    """PR(W) = (sum(s))^2 / sum(s^2) — secondary metric, no gate."""
    ...

def compute_pr_map(model_name: str) -> dict[str, float]: ...

def run_correlation_analysis(
    erank_map: dict[str, float],
    oracle_rank_map: dict[str, int],
    pr_map: dict[str, float] = None,
) -> dict:
    """
    Returns {
        "r": float, "p_one_tailed": float, "p_two_tailed": float,
        "ci_low": float, "ci_high": float,
        "pr_r": float,  # participation ratio correlation (no gate)
        "n_layers": int,
        "pass": bool,   # r >= 0.65 AND p_one_tailed < 0.05
    }
    """
    ...

def verify_mechanism(
    erank_map: dict[str, float], oracle_rank_map: dict[str, int], model_name: str
) -> tuple[bool, dict]:
    """
    Checks: erank_map len >= 60, oracle varies (>1 unique rank), r > 0.
    Returns (all_pass, indicators_dict).
    """
    ...

def check_global_success(results_per_model: dict[str, dict]) -> bool:
    """True if >= 2/3 model families have pass=True."""
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, pathlib

```python
def plot_scatter_erank_vs_oracle(
    erank_maps: dict[str, dict],
    oracle_maps: dict[str, dict],
    corr_results: dict[str, dict],
    save_path: Path,
) -> None:
    """3-subplot scatter (BERT, DeBERTa, ViT), color by layer type, Pearson r annotation."""
    ...

def plot_erank_heatmap(erank_map: dict[str, float], model_name: str, save_path: Path) -> None:
    """Layer-depth heatmap of erank values."""
    ...

def plot_oracle_rank_histogram(oracle_rank_map: dict[str, int], model_name: str, save_path: Path) -> None:
    """Histogram of oracle rank distribution {4,8,16,32,64} per model."""
    ...

def plot_bootstrap_ci(corr_results: dict[str, dict], save_path: Path) -> None:
    """Bar plot of Pearson r ± 95% CI per model family."""
    ...

def generate_all_figures(
    erank_maps: dict,
    oracle_maps: dict,
    corr_results: dict,
    figures_dir: Path,
) -> None:
    """Generate and save all mandatory figures."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: all modules above, argparse, json, pathlib

```python
def main(args) -> None:
    """
    Pipeline:
    1. For each model_name:
       a. compute_erank_map() → save JSON
       b. run_oracle_sweep() → oracle_rank_map → save JSON
       c. compute_pr_map() → save JSON
       d. run_correlation_analysis() → save JSON
       e. verify_mechanism()
    2. check_global_success() → print PASS/FAIL
    3. generate_all_figures()
    """
    ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=list(MODEL_CONFIGS.keys()))
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=Path("docs/youra_research/h-e1"))
    parser.add_argument("--resume", action="store_true")
    main(parser.parse_args())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown | Type |
|----|------|-------------|------------|-----------|------|
| A-1 | Data & Config | `config.py` + `data.py`: ExperimentConfig, MNLI/CIFAR-10 loaders | 7 | 2+1+2+2 | data-pipeline |
| A-2 | Erank Computation | `erank.py`: svdvals loop, fp32 SVD, JSON save/load, mechanism count check | 8 | 2+1+3+2 | model |
| A-3 | Single Oracle Run | `train.py`: build_oracle_model (PEFT LoRA multi-rank config), train_one_run with checkpoint resume | 14 | 3+3+4+4 | training |
| A-4 | Oracle Sweep Orchestration | `oracle.py`: 2,160-run sweep loop, checkpoint resume, multi-worker dispatch, oracle_rank_map aggregation | 16 | 3+3+5+5 | training |
| A-5 | Correlation Analysis | `analyze.py`: Pearson one-tailed, bootstrap CI, PR, mechanism verify, global success check | 12 | 2+2+5+3 | evaluation |
| A-6 | Visualization | `visualize.py`: 4 figure types (scatter, heatmap, histogram, CI bar) | 8 | 2+1+3+2 | evaluation |
| A-7 | Entry Point & Integration | `run_experiment.py`: full pipeline orchestration, argparse, JSON result saving | 9 | 2+4+1+2 | evaluation |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-5, A-7], Low(4-8): [A-1, A-2, A-6]

---

## Critical Implementation Notes for Phase 4

**PARA oracle scale**: ~5 ranks × ~72 layers × 3 models × 2 seeds = ~2,160 runs. `oracle.py` MUST implement checkpoint-per-run resume. Sequential execution is the default; `--max-workers N` enables layer-parallel dispatch via `ProcessPoolExecutor` when multiple GPUs are available.

**DeBERTa precision**: Force `torch_dtype=torch.float32` and `model.to(torch.float32)` unconditionally. FP16 causes classifier overflow (confirmed by FIM-LoRA paper).

**PEFT per-layer rank**: PEFT `LoraConfig` does not support mixed ranks in a single config. Use one `LoraConfig` per target layer with `target_modules=[target_layer]` at `target_rank`, then add a second adapter for all other modules at `baseline_rank=8` with `requires_grad=False`. Verify with `model.print_trainable_parameters()`.

**erank layer naming**: `compute_erank_map` keys must match `model.named_parameters()` names exactly. Oracle sweep iterates over `erank_map.keys()` — the intersection with PEFT `target_modules` determines valid oracle layers.

**Result paths** (for downstream H-M1/H-M2/H-M3 reuse):
- `results/erank_map_{model_slug}.json`
- `results/oracle_rank_map_{model_slug}.json`
- `results/correlation_{model_slug}.json`
- `results/summary.json` (global pass/fail + all family results)
