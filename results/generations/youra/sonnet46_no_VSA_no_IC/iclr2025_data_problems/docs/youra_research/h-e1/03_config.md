---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
phase: "Phase 3"
generated_at: "2026-08-20"
---

# Config: h-e1 — Domain Exposure Trajectory Pipeline

Applied: Standard Python dataclass pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## E6: CLI Runner & PoC Run [Complexity: 10, Budget: 2 subtasks]

---

## C-E6-1: ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    # --- Paths ---
    idxmaps_dir: Path = Path("data/index_maps")
    """Root dir containing per-model MMapIndexedDataset prefix subdirs."""

    domain_cache_path: Path = Path("data/domain_lookup.pkl")
    """Pickle cache for doc→domain lookup built from EleutherAI/pile."""

    figures_dir: Path = Path("figures")
    """Output directory for generated PNG figures."""

    # --- Pipeline constants ---
    tokens_per_step: int = 2_097_152
    seq_len: int = 2049
    n_checkpoints: int = 154
    n_domains: int = 22

    # --- Model size selection ---
    poc_model_sizes: list[str] = field(
        default_factory=lambda: ["70m", "1b", "6.9b"]
    )
    """Subset used for PoC run."""

    all_model_sizes: list[str] = field(
        default_factory=lambda: [
            "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
            "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
            "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
        ]
    )

    # --- Statistical thresholds ---
    std_threshold: float = 0.001
    """Domains with std below this are considered flat/unlearned."""

    min_domains_passing: int = 10
    """Gate: minimum domains that must pass std_threshold."""

    min_model_sizes_for_gate: int = 8
    """Gate: minimum model sizes required to pass analysis gate."""

    # --- Run mode ---
    poc_mode: bool = True
    """If True, use poc_model_sizes; if False, use all_model_sizes."""

    seed: int = 42
```

### Validation Rules

- `idxmaps_dir` must exist (checked at runtime before dataset load)
- `domain_cache_path` parent dir must exist or be creatable
- `figures_dir` created with `mkdir(parents=True, exist_ok=True)` at startup
- `tokens_per_step > 0`, `seq_len > 0`, `n_checkpoints > 0`
- `std_threshold > 0.0`
- `min_domains_passing <= n_domains`
- `poc_model_sizes` must be non-empty subset of `all_model_sizes`

---

## C-E6-2: CLI Argument Schema + YAML Format

### CLI Flags (map to ExperimentConfig fields)

```
--idxmaps-dir       PATH    default: data/index_maps
--domain-cache      PATH    default: data/domain_lookup.pkl
--figures-dir       PATH    default: figures
--tokens-per-step   INT     default: 2097152
--seq-len           INT     default: 2049
--std-threshold     FLOAT   default: 0.001
--min-domains       INT     default: 10
--min-models        INT     default: 8
--poc               FLAG    enables poc_mode (default: True)
--all               FLAG    disables poc_mode, runs all model sizes
--seed              INT     default: 42
--config            PATH    load YAML config file (overrides other flags)
```

### YAML Config Format

```yaml
# h-e1 experiment config
idxmaps_dir: data/index_maps
domain_cache_path: data/domain_lookup.pkl
figures_dir: figures

tokens_per_step: 2097152
seq_len: 2049
n_checkpoints: 154
n_domains: 22

poc_model_sizes: ["70m", "1b", "6.9b"]
all_model_sizes: ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
                  "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
                  "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped"]

std_threshold: 0.001
min_domains_passing: 10
min_model_sizes_for_gate: 8

poc_mode: true
seed: 42
```

### Loading Logic (in `run.py`)

```python
import argparse
import yaml
from dataclasses import asdict, replace
from pathlib import Path


def load_config(argv=None) -> ExperimentConfig:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--idxmaps-dir", type=Path)
    parser.add_argument("--domain-cache", type=Path)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--tokens-per-step", type=int)
    parser.add_argument("--seq-len", type=int)
    parser.add_argument("--std-threshold", type=float)
    parser.add_argument("--min-domains", type=int)
    parser.add_argument("--min-models", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--all", dest="poc_mode", action="store_false")
    parser.add_argument("--poc", dest="poc_mode", action="store_true")
    parser.set_defaults(poc_mode=True)
    args = parser.parse_args(argv)

    cfg = ExperimentConfig()

    # YAML overrides dataclass defaults
    if args.config:
        with open(args.config) as f:
            overrides = yaml.safe_load(f)
        cfg = replace(cfg, **{k: v for k, v in overrides.items()})

    # CLI overrides YAML
    cli_map = {
        "idxmaps_dir": args.idxmaps_dir,
        "domain_cache_path": args.domain_cache,
        "figures_dir": args.figures_dir,
        "tokens_per_step": args.tokens_per_step,
        "seq_len": args.seq_len,
        "std_threshold": args.std_threshold,
        "min_domains_passing": args.min_domains,
        "min_model_sizes_for_gate": args.min_models,
        "seed": args.seed,
        "poc_mode": args.poc_mode,
    }
    overrides = {k: v for k, v in cli_map.items() if v is not None}
    if overrides:
        cfg = replace(cfg, **overrides)

    return cfg
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-E6-1 | ExperimentConfig dataclass | Dataclass with all fields, types, defaults |
| C-E6-2 | CLI + YAML schema | argparse flags, YAML format, load_config() |
