# Config: H-E1 (EXISTENCE)

**Type**: EXISTENCE (PoC) — single fixed config, no variants
**Applied**: measurement-pipeline-config pattern (flat dataclass, no hyperparameter search)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## ExperimentConfig (config.py)

```python
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Model collection
    n_models_target: int = 100
    n_models_fetch: int = 150          # buffer for load failures
    search_query: str = "vit"
    pipeline_tag: str = "image-classification"
    model_families: tuple[str, ...] = ("google/vit", "facebook/deit", "microsoft/swin")

    # Weight analysis
    attention_name_pattern: str = "attention|qkv|query|key|value"

    # Gate
    sigma_gate_threshold: float = 0.5

    # Reproducibility
    seed: int = 42                      # unused by Hill estimator; kept for HF sampling determinism

    # Output paths
    results_path: str = "results.json"
    figures_dir: str = "figures/"

    # Runtime budget
    max_runtime_hours: float = 4.0


CONFIG = ExperimentConfig()
```

No hyperparameter grid, no ablation variants — single deterministic pass per EXISTENCE gate rules.

---

## results.json Schema (YAML-style)

```yaml
# results.json structure
per_model:                     # list[dict], one entry per successfully measured model
  - model_id: str              # e.g. "google/vit-base-patch16-224"
    family: str                # prefix-derived, e.g. "google/vit"
    n_params: int
    alpha_mean: float          # mean Hill-estimator alpha across attention layers
    alpha_per_layer: list[float]
    layer_names: list[str]

aggregate:                     # dict, single entry
  mean_alpha: float
  median_alpha: float
  sigma_alpha: float           # GATE metric
  range: [float, float]        # [min, max]
  n_models_processed: int
  n_models_failed: int
  gate_passed: bool            # sigma_alpha < sigma_gate_threshold
  by_family:                   # dict[str, dict]
    google/vit:
      mean_alpha: float
      sigma_alpha: float
      n: int
    facebook/deit: {...}
    microsoft/swin: {...}

failed_models: list[str]       # model_ids that failed to load/analyze
```

---

## Subtasks

None — 0 subtask budget per EXISTENCE PoC rules; A-1..A-6 remain undecomposed epic tasks per architecture.
