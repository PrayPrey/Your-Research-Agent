# Configuration Design: h-m1

**Hypothesis:** Uncertainty Method Mechanism Analysis (MECHANISM)
**Type:** MECHANISM
**Date:** 2026-04-22
**Author:** Configuration Agent

Applied: Hardcoded dict pattern (extending h-e1 config)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from base code
**Config Files Found:** h-e1/code/config.py
**Pattern Used:** Hardcoded dict (matching h-e1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (From Actual Code)

The following configs are inherited from h-e1:

```python
# From: h-e1/code/config.py (ACTUAL CODE - VERIFIED)
BASE_CONFIG = {
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
    "k_samples": 10,
    "temperature": 0.7,
    "max_new_tokens": 50,
    
    # Semantic Entropy
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,
    
    # Experiment
    "seed": 42,
    "output_dir": "./figures",
}
```

**Verified from:** h-e1/code/config.py (actual implementation)

---

## Extended Configuration (Current Hypothesis)

```python
# config.py for h-m1
CONFIG = {
    # ===== INHERITED FROM h-e1 (DO NOT MODIFY) =====
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
    "k_samples": 10,
    "temperature": 0.7,
    "max_new_tokens": 50,
    
    # Semantic Entropy (reused from h-e1)
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,
    
    # Experiment
    "seed": 42,
    "output_dir": "./figures",
    
    # ===== NEW: Multi-Method Configuration =====
    # Methods to evaluate
    "methods": [
        "semantic_entropy",
        "self_consistency",
        "token_variance",
        "verbalized_confidence"
    ],
    
    # Verbalized Confidence Elicitation
    "vce_prompt_template": "{question}\n\nProvide your answer and confidence (0-100%):",
    "vce_max_new_tokens": 100,
    
    # Correlation Analysis
    "correlation_threshold": 0.7,  # Gate condition: all correlations < 0.7
    "correlation_method": "pearson",
    
    # Output
    "results_dir": "./results",
    "figures_dir": "./figures",
}
```

---

## Configuration Rationale

### Inherited Parameters (Unchanged from h-e1)
All base parameters (data, model, generation) maintained for controlled comparison.

### New Parameters (h-m1 specific)
- **methods:** List of 4 uncertainty methods to evaluate
- **vce_prompt_template:** Prompt format for verbalized confidence (from arXiv:2306.13063)
- **vce_max_new_tokens:** 100 tokens to capture answer + confidence percentage
- **correlation_threshold:** 0.7 threshold for orthogonality gate (from PRD)
- **correlation_method:** Pearson correlation (standard for linear relationships)

---

## Method-Specific Configuration

### M-1: Environment Setup
No additional config needed (reuses h-e1 modules).

### M-2: Self-Consistency Estimator
Uses inherited `k_samples=10` and `temperature=0.7` for majority voting.

### M-3: Token Variance Estimator
Uses inherited `k_samples=10` to compute variance across samples.

### M-4: Verbalized Confidence Estimator
```python
# Additional fields already in CONFIG
"vce_prompt_template": "{question}\n\nProvide your answer and confidence (0-100%):"
"vce_max_new_tokens": 100
```

### M-5: Correlation Analysis
```python
# Additional fields already in CONFIG
"correlation_threshold": 0.7
"correlation_method": "pearson"
```

### M-6: Visualization
Uses `figures_dir` from CONFIG.

### M-7: Experiment Runner
Orchestrates all methods using CONFIG dictionary.

### M-8: Gate Verification
Uses `correlation_threshold=0.7` for pass/fail decision.

---

## Subtasks

**Budget:** 0 subtasks allocated

No configuration subtasks needed. All parameters use:
- Inherited values from h-e1 (validated in previous hypothesis)
- Standard defaults from research papers (VCE, correlation analysis)

---

## Summary

**Configuration Type:** Hardcoded dict (extending h-e1)
**Subtasks:** 0/0 used
**Budget Compliance:** Within allocation
**Field Name Verification:** All field names match h-e1/code/config.py actual implementation
**Key Extension:** Multi-method support with 4 uncertainty quantification methods
