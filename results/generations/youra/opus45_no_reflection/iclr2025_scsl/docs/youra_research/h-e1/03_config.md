# Configuration: H-E1 (EXISTENCE PoC)

Applied: existence-single-fixed-config pattern (no hyperparameter grid, no ablations, 1 seed)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dataclass (dataclasses.dataclass, loaded from YAML)

---

## YAML Config Schema (`code/config.yaml`)

```yaml
seed: 42

data:
  data_dir: "./data/waterbirds"
  download_url: "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
  splits: ["train", "val", "test"]

features:
  clip_model: "ViT-B/16"
  device: "cuda"          # falls back to cpu if unavailable
  batch_size: 100
  feature_dim: 512
  cache_path: "./data/features_cache.npz"

cv_probe:
  n_subsets: 5
  subset_frac: 0.2
  n_epochs: 10             # C-sweep checkpoints, not gradient epochs
  c_range: [0.001, 100.0]  # LogisticRegression C sweep, log-spaced
  solver: "lbfgs"
  max_iter: 1000

evaluate:
  auc_threshold: 0.75

output:
  figures_dir: "./figures"
  results_path: "./results.yaml"
```

---

## Python Dataclass (`code/config.py`)

```python
from dataclasses import dataclass, field
import yaml


@dataclass
class DataConfig:
    data_dir: str = "./data/waterbirds"
    download_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    splits: tuple = ("train", "val", "test")


@dataclass
class FeatureConfig:
    clip_model: str = "ViT-B/16"
    device: str = "cuda"
    batch_size: int = 100
    feature_dim: int = 512
    cache_path: str = "./data/features_cache.npz"


@dataclass
class CVProbeConfig:
    n_subsets: int = 5
    subset_frac: float = 0.2
    n_epochs: int = 10
    c_range: tuple = (0.001, 100.0)
    solver: str = "lbfgs"
    max_iter: int = 1000


@dataclass
class EvaluateConfig:
    auc_threshold: float = 0.75


@dataclass
class OutputConfig:
    figures_dir: str = "./figures"
    results_path: str = "./results.yaml"


@dataclass
class ExperimentConfig:
    seed: int = 42
    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    cv_probe: CVProbeConfig = field(default_factory=CVProbeConfig)
    evaluate: EvaluateConfig = field(default_factory=EvaluateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "ExperimentConfig":
        with open(path) as f:
            raw = yaml.safe_load(f)
        return cls(
            seed=raw.get("seed", 42),
            data=DataConfig(**raw.get("data", {})),
            features=FeatureConfig(**raw.get("features", {})),
            cv_probe=CVProbeConfig(**raw.get("cv_probe", {})),
            evaluate=EvaluateConfig(**raw.get("evaluate", {})),
            output=OutputConfig(**raw.get("output", {})),
        )
```

Default values match PRD FR-1..FR-5 and architecture `config.yaml` spec exactly (5 subsets, 20% frac, C in [1e-3, 1e2], threshold 0.75, seed 42, batch 100). No non-standard values — all pulled directly from PRD/architecture, no tuning performed (EXISTENCE PoC).

---

## Environment / Path Configuration

- `device`: auto-detect at runtime — `"cuda" if torch.cuda.is_available() else "cpu"` (config value is preferred default, code overrides if CUDA unavailable).
- All paths relative to hypothesis `code/` working directory; no env vars required.
- Dataset download is manual/one-time via `download_waterbirds(data_dir)`; config just stores target dir + URL.

---

## Subtasks [3/3 used — within A-6 budget]

| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Define dataclasses | Implement `ExperimentConfig` + nested dataclasses in `config.py` |
| C-6-2 | YAML loader | `from_yaml` classmethod, wire into `run_experiment.main(config_path)` |
| C-6-3 | Write default `config.yaml` | Populate file with defaults above, used as single fixed PoC run |
