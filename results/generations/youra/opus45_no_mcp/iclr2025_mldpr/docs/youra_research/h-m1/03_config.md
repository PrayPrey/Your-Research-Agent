# Configuration: H-M1 (Bibliometric Study)

**Applied**: dataclass-config-pattern — single frozen dataclass instance, env-var overrides via `os.environ.get`, no CLI/grid needed (fixed pipeline, not model training).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new config schema (no MCP; confirmed via architecture doc that h-e1/code/ has no reusable config).
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Config + Project Scaffold [Complexity: 4, Budget: 4]

**Applied**: dataclass-config-pattern (single `ExperimentConfig`, env overrides, dir bootstrap)

### Configuration (Python Dataclass)

```python
# config.py
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExperimentConfig:
    # Dataset selection (FR-1, 4.3)
    vision_keywords: tuple[str, ...] = ("cifar", "mnist", "imagenet", "svhn", "fashion")
    n_high: int = 10
    n_low: int = 10

    # Semantic Scholar query (FR-2)
    s2_api_url: str = "https://api.semanticscholar.org/graph/v1/paper/search"
    s2_query_terms: tuple[str, ...] = ("architecture", "NAS", "hyperparameter", "tuning")
    s2_rate_limit_sleep: float = 3.1  # sec, ~100 req/5min free tier
    s2_max_retries: int = 5
    s2_backoff_base: float = 2.0      # exponential backoff: base ** attempt

    # Gate thresholds (FR-3, FR-5)
    ratio_threshold: float = 3.0
    p_threshold: float = 0.05

    # Reproducibility (NFR-2)
    seed: int = 42

    # Paths
    cache_dir: str = "cache/"
    results_dir: str = "results/"
    figures_dir: str = "figures/"

    def __post_init__(self):
        for d in (self.cache_dir, self.results_dir, self.figures_dir):
            os.makedirs(d, exist_ok=True)


def load_config() -> ExperimentConfig:
    """Build config with env-var overrides."""
    return ExperimentConfig(
        n_high=int(os.environ.get("HM1_N_HIGH", 10)),
        n_low=int(os.environ.get("HM1_N_LOW", 10)),
        s2_rate_limit_sleep=float(os.environ.get("HM1_S2_SLEEP", 3.1)),
        ratio_threshold=float(os.environ.get("HM1_RATIO_THRESHOLD", 3.0)),
        p_threshold=float(os.environ.get("HM1_P_THRESHOLD", 0.05)),
        seed=int(os.environ.get("HM1_SEED", 42)),
    )


CONFIG = load_config()
```

### Environment Variable Overrides

| Env Var | Default | Maps To |
|---------|---------|---------|
| `HM1_N_HIGH` | 10 | `n_high` |
| `HM1_N_LOW` | 10 | `n_low` |
| `HM1_S2_SLEEP` | 3.1 | `s2_rate_limit_sleep` |
| `HM1_RATIO_THRESHOLD` | 3.0 | `ratio_threshold` |
| `HM1_P_THRESHOLD` | 0.05 | `p_threshold` |
| `HM1_SEED` | 42 | `seed` |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | `ExperimentConfig` dataclass | Define fields, defaults, `__post_init__` dir bootstrap |
| C-1-2 | `load_config()` + env overrides | Env-var parsing, module-level `CONFIG` singleton |

---

## YAML Schema (Reference / Optional Override File)

Not required by pipeline (dataclass is source of truth), but supported if `config.yaml` present — loaded via `pyyaml` (already in deps) and merged over dataclass defaults before instantiation.

```yaml
# config.yaml (optional, all fields optional)
n_high: 10
n_low: 10
ratio_threshold: 3.0
p_threshold: 0.05
seed: 42
s2_rate_limit_sleep: 3.1
```

skipped: YAML loader wiring into `load_config()` — add only if a real need for file-based overrides arises; env vars cover current NFR-2 reproducibility need.
