# Config: H-M3 — Lower Delta Signals Accommodation

**Type:** MECHANISM (statistical analysis)
**Applied:** No matching KB pattern (KB hits were diffusion/inductor configs, irrelevant) — standard scipy/numpy stats config used.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new config design (no base hypothesis code, no existing src/ to inspect)
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## Config Schema (Python Dataclass)

```python
# h-m3/code/config.py
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "Anthropic/hh-rlhf"
    split: str = "train+test"
    min_turns_per_side: int = 2

    # Formality scorer
    model_name: str = "s-nlp/deberta-large-formality-ranker"
    device: str = "cuda"
    batch_size: int = 32
    cache_path: str = "h-m3/cache/formality_scores.parquet"
    reuse_h_m2_cache: bool = True
    h_m2_cache_path: str = "h-m2/cache/formality_scores.parquet"

    # Bootstrap / stats
    n_boot: int = 2000
    seed: int = 42
    alpha: float = 0.05  # p-value gate threshold

    # Gate
    min_sample_size: int = 10000

    # Output
    figures_dir: str = "h-m3/figures"
    results_path: str = "h-m3/results.json"
```

## YAML Schema

```yaml
dataset_name: "Anthropic/hh-rlhf"
split: "train+test"
min_turns_per_side: 2

model_name: "s-nlp/deberta-large-formality-ranker"
device: "cuda"
batch_size: 32
cache_path: "h-m3/cache/formality_scores.parquet"
reuse_h_m2_cache: true
h_m2_cache_path: "h-m2/cache/formality_scores.parquet"

n_boot: 2000
seed: 42
alpha: 0.05

min_sample_size: 10000

figures_dir: "h-m3/figures"
results_path: "h-m3/results.json"
```

---

## Gate Logic

```python
def check_gate(tercile_rates: dict, p_robust: float, n: int, cfg: ExperimentConfig) -> bool:
    monotonic = tercile_rates["T1"] > tercile_rates["T2"] > tercile_rates["T3"]
    significant = p_robust < cfg.alpha
    enough_data = n >= cfg.min_sample_size
    return monotonic and significant and enough_data
```

---

## Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | `ExperimentConfig` in `h-m3/code/config.py` with all fields above |
| C-2 | YAML export helper | `save_config_yaml(cfg, path)` / `load_config_yaml(path)` for run reproducibility logging |
