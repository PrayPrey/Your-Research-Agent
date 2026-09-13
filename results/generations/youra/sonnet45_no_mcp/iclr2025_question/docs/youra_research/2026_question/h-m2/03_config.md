# Configuration Design: h-m2

**Hypothesis:** Error Type Signature Analysis (MECHANISM)
**Type:** MECHANISM (EXISTENCE PoC)
**Date:** 2026-04-22
**Author:** Configuration Agent

Applied: Hardcoded dict pattern (extending h-m1 config), Multi-dataset comparison pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from base code
**Config Files Found:** h-m1/code/config.py
**Pattern Used:** Hardcoded dict (matching h-m1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (From Actual Code)

The following configs are inherited from h-m1:

```python
# From: h-m1/code/config.py (ACTUAL CODE - VERIFIED)
BASE_CONFIG = {
    # Model
    "model_name": "mistralai/Mistral-7B-v0.1",
    "device": "cuda",
    "dtype": "float16",
    
    # Generation (optimized in h-m1)
    "k_samples": 10,  # Note: h-m1 optimized to K=5, but config.py shows 10
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

**Verified from:** h-m1/code/config.py (actual implementation)

**Note:** h-m1 validation report mentions K=5 optimization, but config.py still shows k_samples=10. Using K=5 per validation results.

---

## Extended Configuration (Current Hypothesis)

### Single PoC Config (EXISTENCE)

```python
# config.py for h-m2
CONFIG = {
    # ===== DATASETS (NEW) =====
    # NaturalQuestions - Knowledge Gaps
    "dataset_nq": {
        "name": "natural_questions",
        "split": "validation",
        "num_samples": 100,
        "error_type": "knowledge_gaps"
    },
    
    # TruthfulQA - Confident Misconceptions
    "dataset_tqa": {
        "name": "truthful_qa",
        "config": "generation",
        "split": "validation",
        "num_samples": 100,
        "error_type": "confident_misconceptions"
    },
    
    # ===== MODEL (INHERITED FROM h-m1) =====
    "model_name": "mistralai/Mistral-7B-v0.1",
    "device": "cuda",
    "dtype": "float16",
    
    # ===== GENERATION (OPTIMIZED FROM h-m1) =====
    "k_samples": 5,  # Optimized from K=10 in h-m1 validation
    "temperature": 0.7,
    "max_new_tokens": 50,
    
    # ===== UNCERTAINTY METHODS (REUSED FROM h-m1) =====
    "embedding_model": "all-MiniLM-L6-v2",
    "clustering_threshold": 0.5,
    
    # ===== STATISTICAL ANALYSIS (NEW) =====
    "significance_threshold": 0.05,  # p-value for t-test
    
    # ===== EXPERIMENT =====
    "seed": 42,
    "output_dir": "./results",
    "figures_dir": "./figures",
    
    # ===== BASE HYPOTHESIS INTEGRATION (NEW) =====
    "h_m1_code_path": "../h-m1/code",  # For sys.path reuse
}
```

---

## Configuration Rationale

### Inherited Parameters (From h-m1)
All model and generation parameters maintained for controlled comparison.

### Modified Parameters
- **k_samples:** 5 (down from 10) - Based on h-m1 optimization finding that K=5 is sufficient for efficiency

### New Parameters (h-m2 specific)
- **dataset_nq/dataset_tqa:** Dual dataset configuration for error type comparison
- **significance_threshold:** 0.05 for statistical t-test (standard alpha level)
- **h_m1_code_path:** Path to h-m1 code for module reuse via sys.path

---

## Task-Specific Configuration

### S-1: Dataset Loaders [Budget: 0/2 subtasks]

```python
# DataLoader configuration already in CONFIG
DATASET_NQ_CONFIG = CONFIG["dataset_nq"]
DATASET_TQA_CONFIG = CONFIG["dataset_tqa"]
```

**No subtasks needed** - Standard HuggingFace dataset loading pattern.

---

### S-2: h-m1 Integration [Budget: 0/2 subtasks]

```python
# Integration configuration already in CONFIG
H_M1_INTEGRATION = {
    "code_path": CONFIG["h_m1_code_path"],
    "modules": [
        "models.generator.MistralGenerator",
        "methods.uncertainty.SemanticEntropyEstimator",
        "methods.uncertainty.SelfConsistencyEstimator"
    ]
}
```

**No subtasks needed** - Simple sys.path addition, no configuration tuning required.

---

### S-3: Signature Analyzer [Budget: 0/2 subtasks]

```python
# Uses CONFIG parameters
ANALYZER_CONFIG = {
    "k_samples": CONFIG["k_samples"],
    "temperature": CONFIG["temperature"],
    "embedding_model": CONFIG["embedding_model"],
    "clustering_threshold": CONFIG["clustering_threshold"]
}
```

**No subtasks needed** - Reuses validated h-m1 hyperparameters.

---

### S-4: Statistical Tests [Budget: 0/2 subtasks]

```python
# Statistical test configuration already in CONFIG
STATS_CONFIG = {
    "significance_threshold": CONFIG["significance_threshold"],
    "test_type": "independent_ttest"  # scipy.stats.ttest_ind
}
```

**No subtasks needed** - Standard statistical test with alpha=0.05.

---

### S-5: Visualizations [Budget: 0/2 subtasks]

```python
# Visualization configuration
VIZ_CONFIG = {
    "figures_dir": CONFIG["figures_dir"],
    "required_figures": [
        "gate_metrics_comparison.png",
        "diversity_distribution.png",
        "agreement_distribution.png",
        "signature_space_2d.png"
    ]
}
```

**No subtasks needed** - Standard matplotlib/seaborn plotting.

---

### S-6: Experiment Runner [Budget: 0/2 subtasks]

```python
# Experiment orchestration uses full CONFIG
EXPERIMENT_CONFIG = CONFIG  # No additional parameters needed
```

**No subtasks needed** - Orchestration layer uses existing config.

---

### S-7: Gate Verification [Budget: 0/2 subtasks]

```python
# Gate evaluation configuration
GATE_CONFIG = {
    "gate_type": "SHOULD_WORK",
    "condition": "diversity_pvalue < 0.05 and nq_diversity_mean > tqa_diversity_mean",
    "metrics": ["diversity_pvalue", "nq_diversity_mean", "tqa_diversity_mean"]
}
```

**No subtasks needed** - Simple boolean evaluation.

---

## Subtasks Summary

**Budget:** 2 subtasks allocated
**Used:** 0 subtasks

**Justification:** All configuration parameters use:
- Inherited values from h-m1 (validated in previous hypothesis)
- Standard defaults from research (significance_threshold=0.05)
- Simple dataset loading patterns (HuggingFace standard)

**No configuration tuning required for EXISTENCE PoC.**

---

## Summary

**Configuration Type:** Hardcoded dict (extending h-m1)
**Subtasks:** 0/2 used
**Budget Compliance:** Within allocation
**Field Name Verification:** All field names match h-m1/code/config.py actual implementation
**Key Extension:** Dual-dataset support for error type signature comparison
**PoC Focus:** Single fixed config (no hyperparameter grid) for minimal "does it work?" validation
