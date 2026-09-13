# Configuration Design: h-e1

**Hypothesis:** Semantic Entropy vs Ensemble Baseline
**Type:** EXISTENCE (PoC)
**Date:** 2026-04-22
**Author:** Configuration Agent

Applied: Hardcoded dict pattern (minimal PoC config)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - new config design
**Config Files Found:** None - new config
**Pattern Used:** Hardcoded dict (minimal PoC)

---

## Configuration Strategy

For EXISTENCE hypothesis, using **single fixed config** (hardcoded dict) with defaults from research.

No configuration subtasks needed - all values are standard from Kuhn et al. 2023 paper.

---

## Experiment Configuration

```python
# config.py
CONFIG = {
    # Data
    "dataset": "natural_questions",
    "split": "validation",
    "num_samples": 100,
    "filter_unanswerable": True,
    
    # Model
    "model_name": "mistralai/Mistral-7B-v0.1",
    "device": "cuda",
    "dtype": "float16",
    
    # Generation
    "k_samples": 10,  # K=10 from hypothesis
    "temperature": 0.7,  # Standard for diverse sampling
    "max_new_tokens": 50,  # Short answer format
    
    # Semantic Entropy
    "embedding_model": "all-MiniLM-L6-v2",  # From Kuhn et al. 2023
    "clustering_threshold": 0.5,  # Cosine similarity threshold
    
    # Experiment
    "seed": 42,
    "output_dir": "./figures",
    
    # Gate Thresholds
    "gate_auroc_min": 0.70,  # Absolute AUROC threshold
    "gate_difference_min": 0.07,  # AUROC_semantic - AUROC_ensemble threshold
}
```

---

## Configuration Rationale

All values use defaults from research:
- **K=10:** Standard in semantic entropy papers (Kuhn et al. 2023)
- **Temperature=0.7:** Standard for diverse sampling
- **Embedding model:** all-MiniLM-L6-v2 from Kuhn et al. 2023 implementation
- **Clustering threshold=0.5:** Cosine similarity threshold from reference implementation
- **100 samples:** Sufficient for PoC direction validation
- **Seed=42:** Reproducibility

No hyperparameter tuning required for EXISTENCE hypothesis.

---

## Summary

**Configuration Type:** Single fixed dict
**Subtasks:** 0 (no decomposition needed for minimal PoC)
**Budget Compliance:** Within LIGHT tier (no config subtasks allocated)
