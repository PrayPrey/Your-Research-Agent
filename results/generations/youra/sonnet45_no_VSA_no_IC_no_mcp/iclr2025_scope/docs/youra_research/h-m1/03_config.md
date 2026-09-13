# Configuration Specification: H-M1

**Date:** 2026-08-25  
**Hypothesis:** Feature Extraction Protocol Inter-Rater Agreement  
**Type:** MECHANISM (Annotation Study)  
**Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Patterns found - nested dataclass pattern from h-e1 experiment config  
**Config Files Found:** `experiments/h-e1/src/config/experiment_config.py`  
**Pattern Used:** dataclass (Python)

---

## Applied Patterns

**Applied:** Standard Python dataclass pattern for study parameters (no ML training config needed)

---

## M1-7: Configuration & Data [Complexity: 6, Budget: 2]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StudyConfig:
    """H-M1 inter-rater agreement study configuration."""
    
    # Study Parameters
    hypothesis_id: str = "h-m1"
    protocol_version: str = "1.0.0"
    n_benchmarks: int = 20
    random_seed: int = 42
    
    # Agreement Thresholds
    kappa_threshold: float = 0.80
    kappa_fail_threshold: float = 0.70
    
    # API Settings
    pwc_api_url: str = "https://paperswithcode.com/api/v1/datasets/"
    api_timeout: int = 30
    
    # File Paths
    taxonomy_path: str = "data/h-m1/taxonomy.json"
    metrics_patterns_path: str = "data/h-m1/metrics_patterns.json"
    output_dir: str = "data/h-m1"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    
    # Annotation Workflow
    calibration_samples: int = 3
    time_limit_minutes: int = 120
    
    def __post_init__(self):
        """Create output directories if needed."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
```

### Data Files

#### taxonomy.json
```python
# PWC task type taxonomy mapping
{
    "image_classification": ["Image Classification", "Object Recognition"],
    "object_detection": ["Object Detection", "Instance Segmentation"],
    "semantic_segmentation": ["Semantic Segmentation", "Scene Parsing"],
    "language_modeling": ["Language Modelling", "Text Generation"],
    "machine_translation": ["Machine Translation", "Neural MT"],
    "question_answering": ["Question Answering", "Reading Comprehension"],
    "speech_recognition": ["Speech Recognition", "ASR"],
    "multimodal": ["Visual Question Answering", "Image Captioning"]
}
```

#### metrics_patterns.json
```python
# Regex patterns for common metrics
{
    "accuracy": r"accuracy|acc\s*[:=]?\s*([\d.]+)",
    "f1": r"f1[-\s]?score|f1\s*[:=]?\s*([\d.]+)",
    "precision": r"precision\s*[:=]?\s*([\d.]+)",
    "recall": r"recall\s*[:=]?\s*([\d.]+)",
    "map": r"mAP|mean\s+average\s+precision\s*[:=]?\s*([\d.]+)",
    "bleu": r"BLEU[-\s]?\d*\s*[:=]?\s*([\d.]+)",
    "perplexity": r"perplexity|PPL\s*[:=]?\s*([\d.]+)",
    "wer": r"WER|word\s+error\s+rate\s*[:=]?\s*([\d.]+)",
    "cer": r"CER|character\s+error\s+rate\s*[:=]?\s*([\d.]+)"
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Config Dataclass | StudyConfig with API settings, thresholds, paths |
| C-7-2 | Data Files | taxonomy.json, metrics_patterns.json |

---

## Configuration Usage

### In Main Script
```python
from h_m1.config import StudyConfig

config = StudyConfig()

# Override defaults if needed
config.n_benchmarks = 30
config.random_seed = 123

# Use in modules
sampler = BenchmarkSampler(api_url=config.pwc_api_url)
extractor = FeatureExtractor(
    taxonomy_path=config.taxonomy_path,
    metrics_config=config.metrics_patterns_path
)
evaluator = Evaluator(threshold=config.kappa_threshold)
```

### Gate Logic
```python
def check_gate(kappa_scores: dict, config: StudyConfig) -> str:
    all_scores = [
        kappa_scores['task_type'],
        kappa_scores['modality'],
        kappa_scores['metrics'],
        kappa_scores['dataset_size_icc']
    ]
    
    if all(k >= config.kappa_threshold for k in all_scores):
        return "PASS"
    elif any(k < config.kappa_fail_threshold for k in all_scores):
        return "FAIL"
    else:
        return "PARTIAL"
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field data files (taxonomy, patterns) documented
