# Config: h-e1 (EXISTENCE PoC)

**Applied**: Standard PyTorch/HuggingFace reproducibility defaults (fixed seed, deterministic inference)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (single fixed instance, no variations — PoC gate per hypothesis rules)

---

## ExperimentConfig (Python Dataclass)

```python
# config.py
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42

    # Generation
    generator_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_samples: int = 10
    temperature: float = 0.7
    max_tokens: int = 256

    # Semantic Entropy detector
    nli_model: str = "microsoft/deberta-v3-large-mnli"
    entailment_threshold: float = 0.5

    # Self-Consistency detector (BERTScore)
    bertscore_model: str = "roberta-large"
    bertscore_lang: str = "en"

    # Evaluation
    gate_threshold: float = 0.55
    n_bootstrap: int = 1000

    # Paths
    figures_dir: str = "h-e1/figures"
    results_path: str = "h-e1/results.json"

CONFIG = ExperimentConfig()
```

No hyperparameter grid, no ablations, no multi-seed — single fixed config per EXISTENCE rules.

---

## YAML Schema (Reproducibility Snapshot)

```yaml
# h-e1/config.yaml (generated at run start, logged alongside results.json)
seed: 42

generator:
  model: meta-llama/Meta-Llama-3-8B-Instruct
  n_samples: 10
  temperature: 0.7
  max_tokens: 256

semantic_entropy:
  nli_model: microsoft/deberta-v3-large-mnli
  entailment_threshold: 0.5

self_consistency:
  bertscore_model: roberta-large
  lang: en

evaluation:
  gate_threshold: 0.55
  n_bootstrap: 1000

datasets:
  - truthful_qa
  - pminervini/HaluEval

paths:
  figures_dir: h-e1/figures
  results_path: h-e1/results.json
```

`run_experiment.py` dumps `dataclasses.asdict(CONFIG)` to this YAML file at run start for logging (NFR-1: reproducibility, logged model versions).

---

## Subtasks

0/0 used — EXISTENCE PoC, no subtask decomposition per budget.
