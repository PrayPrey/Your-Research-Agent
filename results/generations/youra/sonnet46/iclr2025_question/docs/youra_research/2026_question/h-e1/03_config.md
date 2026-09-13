# Config: H-E1 (EXISTENCE PoC)

**Hypothesis:** DeBERTa-v3-large-mnli P(contradiction) as hallucination signal on HaluEval
**Type:** EXISTENCE PoC — single fixed config, no sweeps
**Generated:** 2026-03-16

Applied: Standard PyTorch inference-only config (dataclass, single seed, no optimizer)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Project Setup [Complexity: 5, Budget: 1 subtask]

### Configuration (`code/config.py`)

```python
from dataclasses import dataclass, field
from typing import Tuple, Dict


@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "cross-encoder/nli-deberta-v3-large"

    # Inference
    batch_size: int = 32
    batch_size_fallback: int = 16   # OOM fallback
    max_length: int = 512
    truncation: bool = True

    # Reproducibility
    seed: int = 42

    # Evaluation thresholds
    auroc_threshold: float = 0.55
    delong_alpha: float = 0.05
    cohen_d_threshold: float = 0.2
    tasks_required_to_pass: int = 2   # out of 3

    # Label audit
    label_audit_n: int = 200

    # Dataset
    halueval_hf_id: str = "pminervini/HaluEval"
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")

    # HaluEval field mappings per task
    hf_config_names: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "dialogue_data",
        "qa": "qa_data",
        "summarization": "summarization_data"
    })
    premise_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "knowledge",
        "qa": "context",
        "summarization": "document"
    })
    hypothesis_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "response",
        "qa": "answer",
        "summarization": "summary"
    })
    label_field: str = "hallucination"
    label_map: Dict[str, int] = field(default_factory=lambda: {"yes": 1, "no": 0})

    # Output
    results_dir: str = "results"
    figures_dir: str = "figures"
    save_scores: bool = True    # save full (N,3) matrix for H-M series reuse
    scores_filename: str = "h-e1_results.json"
    summary_filename: str = "h-e1_summary.json"


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig | Complete dataclass with all defaults, field mappings, and get_config() factory |

---

## config.yaml Equivalent

```yaml
# H-E1 Experiment Config
# EXISTENCE PoC — inference-only, no training

model_name: "cross-encoder/nli-deberta-v3-large"

batch_size: 32
batch_size_fallback: 16
max_length: 512
truncation: true

seed: 42

auroc_threshold: 0.55
delong_alpha: 0.05
cohen_d_threshold: 0.2
tasks_required_to_pass: 2

label_audit_n: 200

halueval_hf_id: "pminervini/HaluEval"
tasks:
  - dialogue
  - qa
  - summarization

hf_config_names:
  dialogue: dialogue_data
  qa: qa_data
  summarization: summarization_data

premise_fields:
  dialogue: knowledge
  qa: context
  summarization: document

hypothesis_fields:
  dialogue: response
  qa: answer
  summarization: summary

label_field: hallucination
label_map:
  yes: 1
  no: 0

results_dir: results
figures_dir: figures
save_scores: true
scores_filename: h-e1_results.json
summary_filename: h-e1_summary.json
```

---

## Hyperparameter Traceability Table

| Parameter | Value | Source |
|-----------|-------|--------|
| `model_name` | cross-encoder/nli-deberta-v3-large | Phase 2B Section 1.3 |
| `batch_size` | 32 | Phase 2B controlled variables |
| `batch_size_fallback` | 16 | PRD risk table (GPU OOM mitigation) |
| `max_length` | 512 | Phase 2B controlled variables |
| `truncation` | True | PRD FR-3.1 |
| `seed` | 42 | NFR-2 reproducibility |
| `auroc_threshold` | 0.55 | Phase 2B Section 2.2, H-E1 success criteria |
| `delong_alpha` | 0.05 | Phase 2B Section 2.2 |
| `cohen_d_threshold` | 0.2 | Phase 2B H-E1 verification protocol (small effect) |
| `tasks_required_to_pass` | 2 | Phase 2B Section 2.2 (>=2/3 tasks) |
| `label_audit_n` | 200 | Phase 2B H-E1 verification protocol step 4 |
| `halueval_hf_id` | pminervini/HaluEval | Phase 2C experiment brief |
| `tasks` | (dialogue, qa, summarization) | Phase 2C experiment brief |
| `hf_config_names` | per-task config strings | PRD FR-1.1 / FR-1.2 / FR-1.3 |
| `premise_fields` | knowledge / context / document | PRD Section 4.3 |
| `hypothesis_fields` | response / answer / summary | PRD Section 4.3 |
| `label_map` | yes->1, no->0 | PRD FR-1.4 |
| `save_scores` | True | PRD FR-3.3, NFR-4 (H-M series reuse) |

---

## Hardware Config

### CUDA Device Selection (`code/run_experiment.py` — `setup_gpu()`)

```python
import subprocess
import os


def setup_gpu() -> None:
    """Select GPU with lowest memory usage and set CUDA_VISIBLE_DEVICES."""
    try:
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=index,memory.used",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        rows = [line.strip().split(", ") for line in result.stdout.strip().splitlines()]
        gpu_id = min(rows, key=lambda r: int(r[1]))[0]
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id
        print(f"[GPU] Selected GPU {gpu_id} (lowest memory usage)")
    except Exception as e:
        print(f"[GPU] nvidia-smi failed ({e}), using default GPU 0")
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
```

### Batch Size Fallback (OOM Recovery)

Logic: batch_size 32 -> 16 on RuntimeError OOM.

```python
def run_with_oom_fallback(model, premises, hypotheses, config):
    batch_size = config.batch_size  # 32
    while True:
        try:
            return model.predict(premises, hypotheses, batch_size=batch_size)
        except RuntimeError as e:
            if "out of memory" in str(e).lower() and batch_size > config.batch_size_fallback:
                import torch
                torch.cuda.empty_cache()
                batch_size = config.batch_size_fallback  # 16
                print(f"[OOM] Retrying with batch_size={batch_size}")
            else:
                raise
```

Rules:
- Call `setup_gpu()` before any model load
- Single GPU only — no distributed inference
- `CUDA_VISIBLE_DEVICES` must be set before `sentence_transformers.CrossEncoder` instantiation

---

## Config Values Rationale (Non-Standard Only)

- `auroc_threshold: 0.55` — Phase 2B gate condition; not 0.5 because random baseline is exactly 0.5
- `cohen_d_threshold: 0.2` — Cohen (1988) small-effect cutoff; 0.5 (medium) would be too strict for zero-shot PoC
- `label_audit_n: 200` — Phase 2B verification protocol step 4; stratified sample for structural ceiling
- `save_scores: True` — Required for H-M series downstream reuse; non-default flag for PoC scope
