# Configuration Specification
# Hypothesis H-E1: Data Quality Metrics Correlation Study

**Version**: 1.0
**Created**: 2026-08-28
**Hypothesis ID**: h-e1
**Type**: EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New config design - no existing patterns to analyze
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (EXISTENCE hypothesis pattern)

---

## Applied Patterns

Applied: EXISTENCE PoC config (minimal hardcoded dict, single seed, no hyperparameter grid)

---

## Configuration (Hardcoded Dict)

```python
# config.py
CONFIG = {
    # Dataset
    "dataset_name": "allenai/c4",
    "dataset_split": "en",
    "subset_size_gb": 10,
    "num_subsets": 12,
    
    # Quality dimensions (3 levels per dimension)
    "quality_dimensions": {
        "deduplication": ["low", "medium", "high"],
        "domain_diversity": ["low", "medium", "high"],
        "perplexity": ["low", "medium", "high"],
        "token_efficiency": ["low", "medium", "high"]
    },
    
    # Quality metrics computation
    "ngram_size": 13,
    "perplexity_model": "gpt2",
    "perplexity_batch_size": 128,
    
    # Density metrics computation
    "embedder_model": "all-MiniLM-L6-v2",
    "semantic_sample_size": 1000,
    
    # Statistical analysis
    "correlation_threshold_r": 0.5,
    "significance_threshold_p": 0.01,
    "reproducibility_cv_threshold": 0.10,
    
    # Reproducibility
    "seed": 42,
    "num_reproducibility_samples": 3,
    
    # Compute
    "device": "cuda",
    
    # Output paths
    "output_dir": "results/",
    "data_dir": "data/subsets/",
    "plots_dir": "results/plots/"
}
```

---

## Gate Decision Logic

```python
# Embedded in run_experiment.py
def check_gate(correlation_results):
    """MUST_WORK gate for EXISTENCE hypothesis."""
    passing = 0
    
    for component in ['dedup', 'diversity', 'perplexity', 'efficiency']:
        r = correlation_results.loc[component, 'pearson_r']
        p = correlation_results.loc[component, 'p_value']
        rho = correlation_results.loc[component, 'spearman_rho']
        
        if r > 0.5 and p < 0.01 and rho > 0.5:
            passing += 1
    
    if passing >= 4:
        return "PASS"
    elif passing >= 2:
        return "PARTIAL"
    else:
        return "FAIL"
```

---

## Rationale (Non-Standard Values Only)

**ngram_size=13**: Matches research baseline for deduplication (Lee et al. 2021).
**semantic_sample_size=1000**: Balance between diversity measurement accuracy and compute cost.

---

**END OF CONFIG**
