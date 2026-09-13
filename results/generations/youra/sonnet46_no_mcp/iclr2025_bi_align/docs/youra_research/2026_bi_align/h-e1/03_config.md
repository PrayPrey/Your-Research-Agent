# H-E1 Configuration
**Hypothesis**: Temporal Stylistic Coefficient Drift in RLHF Annotation
**Date**: 2026-05-03
**Tier**: EXISTENCE/FOUNDATION/MUST_WORK

Applied: statistical-analysis-config-dataclass

---

## Dataclass Definitions

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class DataConfig:
    hh_rlhf_dataset: str = "Anthropic/hh-rlhf"
    webgpt_dataset: str = "openai/webgpt_comparisons"
    cache_dir: str = "./data/cache"
    n_rounds: int = 3
    min_round1_size: int = 10000
    coverage_threshold: float = 0.95

@dataclass
class FeatureConfig:
    hedging_phrases: List[str] = field(default_factory=lambda: [
        "I think", "I believe", "perhaps", "possibly", "might", "may",
        "could", "probably", "seems", "appears", "arguably", "likely",
        "uncertain", "not sure", "unclear", "I'm not certain"
    ])
    structure_markers: List[str] = field(default_factory=lambda: [
        "First,", "Second,", "Third,", "Finally,",
        "1.", "2.", "3.", "- ", "* ",
        "In conclusion,", "To summarize,", "In summary,"
    ])
    vif_threshold: float = 10.0
    scaler_type: str = "standard"  # "standard" | "minmax"

@dataclass
class QEarlyConfig:
    lr_params: Dict[str, Any] = field(default_factory=lambda: {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "class_weight": "balanced",
        "random_state": 42,
    })
    calibration_method: str = "sigmoid"
    brier_gate_threshold: float = 0.02

@dataclass
class AnalysisConfig:
    bootstrap_iters: int = 1000
    permutation_iters: int = 1000
    alpha: float = 0.05
    bonferroni_k: int = 3
    alpha_corrected: float = 0.0167
    fleiss_kappa_threshold: float = 0.4
    min_high_ambiguity_samples: int = 500

@dataclass
class OutputConfig:
    figures_dir: str = "./h-e1/figures"
    results_file: str = "./h-e1/results/results.yaml"
    log_level: str = "INFO"

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    q_early: QEarlyConfig = field(default_factory=QEarlyConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
    n_rounds: int = 3
```

---

## YAML Schema (experiment_config.yaml)

```yaml
random_seed: 42
n_rounds: 3

data:
  hh_rlhf_dataset: "Anthropic/hh-rlhf"
  webgpt_dataset: "openai/webgpt_comparisons"
  cache_dir: "./data/cache"
  n_rounds: 3
  min_round1_size: 10000
  coverage_threshold: 0.95

features:
  hedging_phrases:
    - "I think"
    - "I believe"
    - "perhaps"
    - "possibly"
    - "might"
    - "may"
    - "could"
    - "probably"
    - "seems"
    - "appears"
    - "arguably"
    - "likely"
    - "uncertain"
    - "not sure"
    - "unclear"
    - "I'm not certain"
  structure_markers:
    - "First,"
    - "Second,"
    - "Third,"
    - "Finally,"
    - "1."
    - "2."
    - "3."
    - "- "
    - "* "
    - "In conclusion,"
    - "To summarize,"
    - "In summary,"
  vif_threshold: 10.0
  scaler_type: "standard"

q_early:
  lr_params:
    C: 1.0
    max_iter: 1000
    solver: "lbfgs"
    class_weight: "balanced"
    random_state: 42
  calibration_method: "sigmoid"
  brier_gate_threshold: 0.02

analysis:
  bootstrap_iters: 1000
  permutation_iters: 1000
  alpha: 0.05
  bonferroni_k: 3
  alpha_corrected: 0.0167
  fleiss_kappa_threshold: 0.4
  min_high_ambiguity_samples: 500

output:
  figures_dir: "./h-e1/figures"
  results_file: "./h-e1/results/results.yaml"
  log_level: "INFO"
```

---

## requirements.txt

```
python>=3.9
numpy>=1.24.0
scipy>=1.10.0
pandas>=1.5.0
scikit-learn>=1.2.0
statsmodels>=0.14.0
datasets>=2.14.0
transformers>=4.30.0
sentence-transformers>=2.2.2
matplotlib>=3.7.0
seaborn>=0.12.0
pytest>=7.3.0
pytest-cov>=4.0.0
pyyaml>=6.0
tqdm>=4.65.0
```

---

## environment.yaml

```yaml
name: h-e1-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.10
  - pip
  - pip:
    - numpy>=1.24.0
    - scipy>=1.10.0
    - pandas>=1.5.0
    - scikit-learn>=1.2.0
    - statsmodels>=0.14.0
    - datasets>=2.14.0
    - transformers>=4.30.0
    - sentence-transformers>=2.2.2
    - matplotlib>=3.7.0
    - seaborn>=0.12.0
    - pytest>=7.3.0
    - pytest-cov>=4.0.0
    - pyyaml>=6.0
    - tqdm>=4.65.0
```

---

## Configuration Loading Code

```python
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional

def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    """Load experiment config from YAML file or return defaults."""
    if config_path is None:
        return ExperimentConfig()

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    cfg = ExperimentConfig()

    if "random_seed" in raw:
        cfg.random_seed = raw["random_seed"]
    if "n_rounds" in raw:
        cfg.n_rounds = raw["n_rounds"]

    if "data" in raw:
        d = raw["data"]
        cfg.data = DataConfig(**{k: v for k, v in d.items() if hasattr(DataConfig, k) or k in DataConfig.__dataclass_fields__})

    if "features" in raw:
        f = raw["features"]
        cfg.features = FeatureConfig(**{k: v for k, v in f.items() if k in FeatureConfig.__dataclass_fields__})

    if "q_early" in raw:
        q = raw["q_early"]
        cfg.q_early = QEarlyConfig(**{k: v for k, v in q.items() if k in QEarlyConfig.__dataclass_fields__})

    if "analysis" in raw:
        a = raw["analysis"]
        cfg.analysis = AnalysisConfig(**{k: v for k, v in a.items() if k in AnalysisConfig.__dataclass_fields__})

    if "output" in raw:
        o = raw["output"]
        cfg.output = OutputConfig(**{k: v for k, v in o.items() if k in OutputConfig.__dataclass_fields__})

    return cfg


def save_config(cfg: ExperimentConfig, path: str) -> None:
    """Save config to YAML."""
    with open(path, "w") as f:
        yaml.dump(asdict(cfg), f, default_flow_style=False)
```

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1 | DataConfig | Dataset paths, cache dir, round size constraints |
| C-E1-2 | FeatureConfig + QEarlyConfig | Feature extraction params, VIF threshold, LR + calibration params |
| C-E1-3 | AnalysisConfig | Bootstrap/permutation iters, alpha, Fleiss kappa, Bonferroni correction |
| C-E1-4 | OutputConfig + load_config | Output paths, log level, YAML loader/saver |
