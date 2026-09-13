# Configuration Schema: h-m2 Formal Verification

**Hypothesis:** h-m2 (FPR < 25% for ∃(D,B,M) verification)
**Type:** MECHANISM (rule-based symbolic system)
**Gate:** MUST_WORK (FPR < 0.25)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New config design for rule-based verification system
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (no training parameters needed)

## Configuration

```python
CONFIG = {
    # Paths
    "kb_path": "h-m1/data/pwc_cache/kb.yaml",
    "test_set_path": "h-m2/data/test_hypotheses.json",
    "output_dir": "h-m2/results/",
    "figures_dir": "h-m2/figures/",
    
    # Experiment Parameters
    "seed": 42,
    "test_set_size": 20,
    "test_set_balance": 0.5,  # 50/50 testable/untestable
    
    # Gate Thresholds
    "target_fpr": 0.25,
    "baseline_fpr": 0.5,  # Random classifier
    
    # Evaluation Settings
    "metrics": ["fpr", "precision", "accuracy"],
    "primary_metric": "fpr",
    "comparison_baseline": "random",
    
    # Visualization Settings
    "figures": ["confusion_matrix", "metrics_comparison"],
    "format": "png",
    "dpi": 300
}
```

## Rationale

**Hardcoded dict over dataclass**: No hyperparameters to tune (deterministic rule-based system). Single fixed config is sufficient.

**test_set_size = 20**: Minimum for balanced evaluation (10 testable, 10 untestable). From experiment brief.

**target_fpr = 0.25**: Direct from hypothesis statement.

**baseline_fpr = 0.5**: Random classifier expected FPR (no knowledge).
