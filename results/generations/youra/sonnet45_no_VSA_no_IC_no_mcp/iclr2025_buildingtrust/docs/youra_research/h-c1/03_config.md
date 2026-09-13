# Configuration Schema: h-c1

**Date:** 2026-08-24  
**Hypothesis ID:** h-c1  
**Type:** CONDITION (Validation Experiment)  
**Author:** Phase 3 Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: green-field - new config design  
**Config Files Found**: None - new config  
**Pattern Used**: Python dict (hardcoded)

---

## Configuration Design

**Applied**: Standard validation config pattern (fixed parameters, no tuning)

### Complete Configuration (Python Dict)

```python
# h-c1/code/config.py
# Validation experiment config - all parameters fixed

CONFIG = {
    # Data Configuration
    "data": {
        "dataset_name": "truthful_qa",
        "dataset_split": "generation",
        "total_samples": 100,
        "entity_error_samples": 50,
        "non_entity_error_samples": 50,
        "data_path": "./data/truthfulqa_entity_subset/",
        "gold_annotations_file": "gold_annotations.jsonl"
    },
    
    # NER Model Configuration
    "ner": {
        "model_name": "en_core_web_lg",  # spaCy model
        "entity_types": ["PERSON", "ORG", "GPE", "PRODUCT"],
        "confidence_threshold": 0.0  # No filtering - evaluate all predictions
    },
    
    # Wikipedia Configuration
    "wikipedia": {
        "language": "en",
        "user_agent": "h-c1-validator/1.0",
        "api_workers": 10,  # Rate limit compliance
        "api_timeout": 30,
        "retry_attempts": 1,
        "min_content_length": 100  # Non-stub filter
    },
    
    # Validation Thresholds
    "validation": {
        "ner_f1_threshold": 0.90,
        "coverage_threshold": 0.90
    },
    
    # Output Configuration
    "output": {
        "figures_dir": "./figures/",
        "report_file": "04_validation.md",
        "figure_dpi": 300,
        "figure_format": "png"
    }
}
```

---

## Configuration Rationale

**Non-standard values only:**

- `api_workers: 10` - Wikipedia API rate limit compliance (per NFR-2)
- `min_content_length: 100` - Non-stub filter (from experiment brief)
- `retry_attempts: 1` - Single retry on API failure (per NFR-3)

All other values are standard defaults from spaCy/Wikipedia API documentation.

---

## Validation Rules

### Data Configuration
```python
assert CONFIG["data"]["total_samples"] == 100
assert CONFIG["data"]["entity_error_samples"] == 50
assert CONFIG["data"]["non_entity_error_samples"] == 50
```

### Model Configuration
```python
import spacy
assert CONFIG["ner"]["model_name"] in spacy.util.get_installed_models()
```

### Wikipedia Configuration
```python
assert 1 <= CONFIG["wikipedia"]["api_workers"] <= 10  # Rate limit
assert CONFIG["wikipedia"]["api_timeout"] > 0
assert CONFIG["wikipedia"]["min_content_length"] >= 50
```

### Validation Thresholds
```python
assert 0.0 <= CONFIG["validation"]["ner_f1_threshold"] <= 1.0
assert 0.0 <= CONFIG["validation"]["coverage_threshold"] <= 1.0
```

---

## No Ablation Studies

**Reason**: CONDITION validation experiment - fixed thresholds from PRD.

**No hyperparameter variations.**

---

## Environment Dependencies

```python
# requirements.txt
spacy>=3.0.0,<4.0.0
wikipedia-api>=0.5.0
datasets>=2.0.0
matplotlib>=3.5.0
scikit-learn>=1.0.0
```

**Model download:**
```bash
python -m spacy download en_core_web_lg
```

---

## Usage

```python
from config import CONFIG

# Load configuration
data_config = CONFIG["data"]
ner_config = CONFIG["ner"]
wiki_config = CONFIG["wikipedia"]

# Run validation
validator = PreConditionValidator(ner_model=ner_config["model_name"])
ner_f1 = validator.validate_ner_accuracy(gold_data)
coverage = validator.validate_wikipedia_coverage(entities)

# Check gate
gate_pass = (
    ner_f1 >= CONFIG["validation"]["ner_f1_threshold"] and
    coverage >= CONFIG["validation"]["coverage_threshold"]
)
```

---

*Configuration for validation experiment - no hyperparameter tuning required*  
*All parameters are fixed from PRD requirements*
