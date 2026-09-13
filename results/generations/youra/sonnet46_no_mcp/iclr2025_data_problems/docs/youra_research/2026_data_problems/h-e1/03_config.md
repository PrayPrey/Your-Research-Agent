# Config Document: H-E1
# Cross-Sub-Task Contamination Variance in The Pile v1

**Hypothesis**: H-E1 | **Type**: EXISTENCE (PoC) | **Date**: 2026-05-04

Applied: EXISTENCE-minimal-pipeline (single dataclass, no ablation, no grid search)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config design
**Pattern Used**: dataclass

---

## A-1: Project Setup Config [Complexity: 5, Budget: 0 subtasks]

### Configuration (Python Dataclass)

```python
# code/config.py
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import List


@dataclass
class Config:
    # Reproducibility
    seed: int = 1

    # N-gram settings (WIMBD standard)
    ngram_n: int = 13
    min_token_length: int = 13

    # Pile index
    pile_index: str = "pile"
    wimbd_es_host: str = field(default_factory=lambda: os.environ.get("WIMBD_ES_HOST", ""))

    # Text formatting
    text_format: str = "question_choices"   # primary; "question_only" for sensitivity

    # Query reliability
    retry_attempts: int = 3

    # Statistical gate thresholds
    gate_p_threshold: float = 0.05
    max_pair_diff_threshold: float = 0.05

    # MinHash LSH fallback (datasketch)
    minhash_num_perm: int = 128
    minhash_threshold: float = 0.5

    # Dataset identifiers
    mmlu_hf_id: str = "cais/mmlu"
    mmlu_version: str = "1.0.0"
    mmlu_split: str = "test"
    hellaswag_hf_id: str = "Rowan/hellaswag"
    hellaswag_split: str = "validation"
    bbh_hf_id: str = "lukaemon/bbh"
    bbh_split: str = "test"

    # All 57 MMLU sub-tasks (fixed list)
    mmlu_tasks: List[str] = field(default_factory=lambda: [
        "abstract_algebra", "anatomy", "astronomy", "business_ethics",
        "clinical_knowledge", "college_biology", "college_chemistry",
        "college_computer_science", "college_mathematics", "college_medicine",
        "college_physics", "computer_security", "conceptual_physics",
        "econometrics", "electrical_engineering", "elementary_mathematics",
        "formal_logic", "global_facts", "high_school_biology",
        "high_school_chemistry", "high_school_computer_science",
        "high_school_european_history", "high_school_geography",
        "high_school_government_and_politics", "high_school_macroeconomics",
        "high_school_mathematics", "high_school_microeconomics",
        "high_school_physics", "high_school_psychology",
        "high_school_statistics", "high_school_us_history",
        "high_school_world_history", "human_aging", "human_sexuality",
        "international_law", "jurisprudence", "logical_fallacies",
        "machine_learning", "management", "marketing", "medical_genetics",
        "miscellaneous", "moral_disputes", "moral_philosophy", "nutrition",
        "philosophy", "prehistory", "professional_accounting",
        "professional_law", "professional_medicine", "professional_psychology",
        "public_relations", "security_studies", "sociology",
        "us_foreign_policy", "virology", "world_religions",
    ])

    # Output directories
    results_dir: str = "results"
    figures_dir: str = "figures"


def load_config() -> Config:
    """Returns single fixed Config. No CLI args — EXISTENCE PoC."""
    return Config()
```

### Non-standard value notes

- `seed=1`: matches 02c_experiment_brief.md (not the common 42)
- `minhash_threshold=0.5`: datasketch MinHash LSH default for near-duplicate detection
- `wimbd_es_host`: read from `WIMBD_ES_HOST` env var at instantiation time; empty string triggers fallback mode in PileQuery

---

## Subtasks

Budget: 0 subtasks (EXISTENCE PoC — no config subtasks needed)
