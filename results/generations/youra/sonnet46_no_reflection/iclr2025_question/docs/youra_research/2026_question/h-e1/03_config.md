# Configuration: h-e1 — Semantic-Structural UQ Existence Verification

**Hypothesis**: EXISTENCE (PoC)
**Date**: 2026-05-20

Applied: YAML-dataclass nested config pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new config schema
**Config Files Found**: None - new config
**Pattern Used**: dataclass + YAML loader

---

## Config Dataclass Hierarchy (`h-e1/code/config.py`)

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import yaml


@dataclass
class SamplingConfig:
    n_samples: int = 10
    temperature: float = 1.0
    top_p: float = 0.9
    seed: int = 42
    max_new_tokens: int = 50
    n_few_shot: int = 5


@dataclass
class ModelConfig:
    hf_id: str = ""
    dtype: str = "bfloat16"
    quantization: Optional[str] = None  # "8bit", "4bit", or None
    device_map: str = "auto"


@dataclass
class DatasetConfig:
    name: str = ""
    hf_id: str = ""
    config: str = "default"
    split: str = "validation"
    size: int = 0


@dataclass
class EvaluationConfig:
    bootstrap_resamples: int = 1000
    alpha: float = 0.05
    batch_size_8b: int = 16
    batch_size_70b: int = 4
    checkpoint_every: int = 500  # Non-standard: TriviaQA=17944 queries, checkpoint prevents data loss


@dataclass
class OutputConfig:
    base_dir: str = "h-e1"
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
    code_dir: str = "h-e1/code"


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    hypothesis_type: str = "EXISTENCE"
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    models: Dict[str, ModelConfig] = field(default_factory=dict)
    datasets_primary: List[DatasetConfig] = field(default_factory=list)
    datasets_secondary: List[DatasetConfig] = field(default_factory=list)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def load_config(path: str) -> ExperimentConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    sampling = SamplingConfig(**raw["sampling"])

    models = {
        key: ModelConfig(**{k: v for k, v in val.items()})
        for key, val in raw["models"].items()
        if key != "entailment"  # entailment model has minimal config
    }
    # Add entailment model separately (no dtype/quantization keys)
    if "entailment" in raw["models"]:
        models["entailment"] = ModelConfig(hf_id=raw["models"]["entailment"]["hf_id"])

    datasets_primary = [DatasetConfig(**d) for d in raw["datasets"]["primary"]]
    datasets_secondary = [DatasetConfig(**d) for d in raw["datasets"]["secondary"]]

    evaluation = EvaluationConfig(**raw["evaluation"])
    output = OutputConfig(**raw["output"])

    return ExperimentConfig(
        hypothesis_id=raw["hypothesis_id"],
        hypothesis_type=raw["hypothesis_type"],
        sampling=sampling,
        models=models,
        datasets_primary=datasets_primary,
        datasets_secondary=datasets_secondary,
        evaluation=evaluation,
        output=output,
    )
```

---

## YAML Config File (`h-e1/config/h-e1.yaml`)

```yaml
hypothesis_id: "h-e1"
hypothesis_type: "EXISTENCE"

sampling:
  n_samples: 10          # Farquhar et al. 2024 standard
  temperature: 1.0       # Diversity for semantic clustering
  top_p: 0.9
  seed: 42
  max_new_tokens: 50     # Short-phrase QA generation
  n_few_shot: 5          # Farquhar 2024 5-shot format

models:
  small:
    hf_id: "meta-llama/Meta-Llama-3-8B"
    dtype: "bfloat16"
    device_map: "auto"
  large:
    hf_id: "meta-llama/Meta-Llama-3-70B"
    dtype: "bfloat16"
    quantization: "8bit"  # ~40GB VRAM; bitsandbytes 8-bit
    device_map: "auto"
  entailment:
    hf_id: "microsoft/deberta-large-mnli"

datasets:
  primary:
    - name: "trivia_qa"
      hf_id: "mandarjoshi/trivia_qa"
      config: "rc.nocontext"
      split: "test"
      size: 17944
    - name: "natural_questions"
      hf_id: "google-research-datasets/natural_questions"
      config: "default"
      split: "validation"
      size: 3610
  secondary:
    - name: "truthful_qa"
      hf_id: "truthful_qa"
      config: "mc1_targets"
      split: "validation"
      size: 817

evaluation:
  bootstrap_resamples: 1000  # Standard for stable 95% CI
  alpha: 0.05
  batch_size_8b: 16
  batch_size_70b: 4
  checkpoint_every: 500

output:
  base_dir: "h-e1"
  figures_dir: "h-e1/figures"
  results_dir: "h-e1/results"
  code_dir: "h-e1/code"
```

---

## Hyperparameter Justifications (Non-Standard Values Only)

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `n_samples` | 10 | Farquhar et al. 2024 standard for SE computation |
| `temperature` | 1.0 | Maximizes sample diversity for semantic cluster separation |
| `bootstrap_resamples` | 1000 | Standard threshold for stable 95% CI estimation |
| `checkpoint_every` | 500 | TriviaQA=17,944 queries; prevents data loss on long GPU runs |
| `batch_size_70b` | 4 | 70B with 8-bit quantization; conservative to avoid OOM |
| `quantization` | "8bit" | Llama-3-70B requires ~40GB VRAM; 8-bit reduces to ~35-40GB |

---

## Subtasks

Budget: 0 dedicated config subtasks — config is merged into Epic E1 per architecture design.

Epic E1 covers: `config.py`, `data_loader.py`, `h-e1/config/h-e1.yaml`

---

*Generated by Configuration Agent — Phase 3 step-04*
*Hypothesis: h-e1 | Type: EXISTENCE (PoC) | Tier: LIGHT*
