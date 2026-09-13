# Configuration Schema: h-e1

**Date:** 2026-08-24  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC pattern detection)  
**Author:** Phase 3 Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-c1)  
**Status**: config inherited from h-c1 data/output patterns  
**Config Files Found**: h-c1/03_config.md (reference only - no code yet)  
**Pattern Used**: Python dict (hardcoded)

---

## Configuration Design

**Applied**: Standard inference config pattern (fixed parameters, no training)

### Complete Configuration (Python Dict)

```python
# h-e1/code/config.py
# Attention entropy experiment config - inference only

CONFIG = {
    # Model Configuration
    "model": {
        "name": "meta-llama/Llama-2-7b-hf",
        "output_attentions": True,
        "torch_dtype": "float16",
        "device_map": "auto",
        "attention_layer": -1,  # Last layer
        "aggregate_heads": True  # Average across attention heads
    },
    
    # NER Configuration (inherited from h-c1)
    "ner": {
        "model_name": "en_core_web_lg",  # Validated F1=0.96 in h-c1
        "entity_types": ["PERSON", "ORG", "GPE", "PRODUCT"]
    },
    
    # Data Configuration
    "data": {
        "dataset_path": "./data/truthfulqa_entity_subset/",
        "entity_error_samples": 50,
        "non_entity_error_samples": 50,
        "total_samples": 100,
        "annotations_file": "gold_annotations.jsonl"  # From h-c1
    },
    
    # Entropy Configuration
    "entropy": {
        "epsilon": 1e-10,  # Smoothing for log(0)
        "span_aggregation": "mean"  # Average entropy across entity tokens
    },
    
    # Statistical Testing
    "statistics": {
        "alpha": 0.05,  # Significance threshold
        "test_type": "one_tailed",  # entity < non-entity
        "effect_size": "cohens_d"
    },
    
    # Output Configuration
    "output": {
        "figures_dir": "./figures/",
        "results_file": "entropy_results.json",
        "scores_file": "entropy_scores.csv",
        "validation_report": "04_validation.md",
        "figure_dpi": 300,
        "figure_format": "png"
    },
    
    # Reproducibility
    "seed": 42
}
```

---

## Configuration Rationale

**Non-standard values only:**

- `epsilon: 1e-10` - Log smoothing for zero-attention edge case (standard practice)
- `attention_layer: -1` - Last layer most task-relevant (from experiment brief)

All other values are standard defaults from HuggingFace/scipy documentation.

---

## Validation Rules

### Model Configuration
```python
assert CONFIG["model"]["name"] == "meta-llama/Llama-2-7b-hf"
assert CONFIG["model"]["output_attentions"] == True
assert CONFIG["model"]["attention_layer"] == -1
```

### Data Configuration
```python
assert CONFIG["data"]["entity_error_samples"] == 50
assert CONFIG["data"]["non_entity_error_samples"] == 50
assert CONFIG["data"]["total_samples"] == 100
```

### Statistical Configuration
```python
assert CONFIG["statistics"]["alpha"] == 0.05
assert CONFIG["statistics"]["test_type"] in ["one_tailed", "two_tailed"]
```

### Entropy Configuration
```python
assert 0 < CONFIG["entropy"]["epsilon"] < 1e-6
assert CONFIG["entropy"]["span_aggregation"] in ["mean", "median"]
```

---

## No Ablation Studies

**Reason**: EXISTENCE PoC - fixed config to test "does it work?"

**No hyperparameter variations.**

---

## Environment Dependencies

```python
# requirements.txt
transformers>=4.30.0
torch>=2.0.0
spacy>=3.5.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.5.0
datasets>=2.0.0
```

**Model downloads:**
```bash
# NER model (from h-c1)
python -m spacy download en_core_web_lg

# Llama-2 (via HuggingFace, requires auth token if gated)
# Automatically downloaded on first run
```

---

## Usage

```python
from config import CONFIG

# Load model
model = AutoModelForCausalLM.from_pretrained(
    CONFIG["model"]["name"],
    output_attentions=CONFIG["model"]["output_attentions"],
    torch_dtype=torch.float16,
    device_map=CONFIG["model"]["device_map"]
)

# Load NER
nlp = spacy.load(CONFIG["ner"]["model_name"])

# Run experiment
experiment = AttentionEntropyExperiment(model, nlp, CONFIG)
results = experiment.run()

# Check gate
gate_pass = (
    results["p_value"] < CONFIG["statistics"]["alpha"] and
    results["mean_entity"] < results["mean_non_entity"]
)
```

---

*Configuration for inference experiment - no training required*  
*All parameters fixed from PRD and experiment brief*
