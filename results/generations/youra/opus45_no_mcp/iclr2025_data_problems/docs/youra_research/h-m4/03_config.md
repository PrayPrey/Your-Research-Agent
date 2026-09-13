# H-M4 Configuration: SSI Captures Invariance as Contamination Signal

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: config classes verified from base code (`docs/youra_research/h-m1/code/config.py`, `ssi.py`)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`, `docs/youra_research/h-m1/code/ssi.py`
**Pattern Used**: dataclass
**Notes**: `SSI_EPSILON = 1e-8` verified as module-level constant in `ssi.py` (not a config field). `contamination_levels` in base is `(0.0, 0.10, 0.50)` — H-M4 extends to 5 levels per allocated task.

---

## Applied

Standard PyTorch/dataclass defaults; reused H-M1 checkpoint/model conventions.

---

## Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field


@dataclass
class Config:
    # Model (inherited from H-M1)
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    # Dataset
    dataset_name: str = "cais/mmlu"
    n_items: int = 14042  # full MMLU test set
    k_paraphrases: int = 20

    # SSI
    ssi_epsilon: float = 1e-8

    # Experiment grid
    contamination_levels: tuple = (0, 5, 10, 20, 50)  # percent
    seeds: tuple = (42, 123, 456)

    # Thresholds
    auc_threshold: float = 0.7
    pearson_r_threshold: float = 0.6
    effect_size_threshold: float = 0.5

    # Paths (see Path Templates below)
    checkpoint_dir: str = "docs/youra_research/h-m1/code/checkpoints"
    output_dir: str = "docs/youra_research/h-m4/code/results"
    figure_dir: str = "docs/youra_research/h-m4/code/figures"
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M4-1 | Load checkpoints | Resolve checkpoint path per contamination level from `checkpoint_dir` template |
| C-M4-2 | Compute SSI | Run SSI over K=20 paraphrases per item using `ssi_epsilon` |
| C-M4-3 | Threshold validation | Compare AUC/Pearson r/effect size against config thresholds |
| C-M4-4 | Path resolution | Resolve output/figure paths per level+seed for result artifacts |

---

## Path Templates

Variables resolved at runtime: `{level}` (int, from `contamination_levels`), `{seed}` (int, from `seeds`).

```python
CHECKPOINT_PATH_TEMPLATE = "{checkpoint_dir}/contam_{level}pct/adapter_model.safetensors"
RESULTS_PATH_TEMPLATE = "{output_dir}/ssi_level{level}_seed{seed}.json"
FIGURE_PATH_TEMPLATE = "{figure_dir}/ssi_vs_contamination_seed{seed}.png"
SUMMARY_PATH = "{output_dir}/summary.csv"


def resolve_checkpoint_path(cfg: Config, level: int) -> str:
    return CHECKPOINT_PATH_TEMPLATE.format(checkpoint_dir=cfg.checkpoint_dir, level=level)


def resolve_results_path(cfg: Config, level: int, seed: int) -> str:
    return RESULTS_PATH_TEMPLATE.format(output_dir=cfg.output_dir, level=level, seed=seed)


def resolve_figure_path(cfg: Config, seed: int) -> str:
    return FIGURE_PATH_TEMPLATE.format(figure_dir=cfg.figure_dir, seed=seed)
```

**Checkpoint level mapping** (from H-M1 contamination training runs, 5 levels required by H-M4 vs. 3 available in H-M1 PoC):
| level | H-M1 checkpoint available? |
|-------|------------------------------|
| 0 | yes (`contam_0pct`) |
| 5 | **new — requires H-M1 retrain at 5%** |
| 10 | yes (`contam_10pct`) |
| 20 | **new — requires H-M1 retrain at 20%** |
| 50 | yes (`contam_50pct`) |

---

## YAML Schema

```yaml
model:
  model_id: mistralai/Mistral-7B-v0.1
  dtype: bfloat16
  device_map: auto

dataset:
  name: cais/mmlu
  n_items: 14042
  k_paraphrases: 20

ssi:
  epsilon: 1.0e-8

experiment:
  contamination_levels: [0, 5, 10, 20, 50]
  seeds: [42, 123, 456]

thresholds:
  auc: 0.7
  pearson_r: 0.6
  effect_size: 0.5

paths:
  checkpoint_dir: docs/youra_research/h-m1/code/checkpoints
  output_dir: docs/youra_research/h-m4/code/results
  figure_dir: docs/youra_research/h-m4/code/figures
```

---

## Validation Rules

```python
def validate_config(cfg: Config) -> None:
    assert cfg.n_items > 0, "n_items must be positive"
    assert cfg.k_paraphrases >= 1, "k_paraphrases must be >= 1"
    assert cfg.ssi_epsilon > 0, "ssi_epsilon must be > 0 (avoid div-by-zero)"
    assert all(0 <= lvl <= 100 for lvl in cfg.contamination_levels), \
        "contamination_levels must be in [0, 100]"
    assert len(cfg.contamination_levels) == len(set(cfg.contamination_levels)), \
        "contamination_levels must be unique"
    assert len(cfg.seeds) >= 1, "at least one seed required"
    assert 0.0 <= cfg.auc_threshold <= 1.0, "auc_threshold must be in [0, 1]"
    assert -1.0 <= cfg.pearson_r_threshold <= 1.0, "pearson_r_threshold must be in [-1, 1]"
    assert cfg.effect_size_threshold >= 0, "effect_size_threshold must be >= 0"
```

---

## Inherited Configuration (Base Hypothesis: H-M1)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
@dataclass
class Config:  # H-M1 base
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")
    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    contamination_levels: tuple = (0.0, 0.10, 0.50)  # H-M4 extends to 5 levels
    seeds: tuple = (42,)  # H-M4 extends to 3 seeds
```

`SSI_EPSILON = 1e-8` is a module-level constant in `docs/youra_research/h-m1/code/ssi.py` (line 7) — carried forward unchanged as `Config.ssi_epsilon` field in H-M4.

**Verified from**: `docs/youra_research/h-m1/code/config.py`, `docs/youra_research/h-m1/code/ssi.py`
