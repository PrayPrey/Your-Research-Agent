# Configuration Schema: h-m3 Confound Detection

**Hypothesis:** h-m3 (Precision >40% on confound flagging)
**Type:** MECHANISM (rule-based pattern detection)
**Gate:** SHOULD_WORK (precision > 0.40)

## Codebase Analysis (Serena)

**Project Type**: green-field (extends h-m2 evaluation pipeline)
**Status**: New config design for confound detection system
**Config Files Found**: None - new config (h-m2 used hardcoded dict)
**Pattern Used**: Hardcoded dict (no training, deterministic rule-based)

**Base Hypothesis**: h-m2 used hardcoded dict for rule-based verification (no hyperparameters).

## Configuration

Applied: Hardcoded dict pattern (Archon KB - rule-based config standard)

```python
CONFIG = {
    # Paths
    "output_dir": "h-m3/figures/",
    
    # Experiment Parameters
    "seed": 42,
    "n_test_hypotheses": 30,
    "n_confounded": 15,
    "n_unconfounded": 15,
    "n_patterns_min": 15,
    
    # Gate Thresholds
    "target_precision": 0.40,
    "baseline_precision_expected": 0.50,
    
    # Evaluation Settings
    "metrics": ["precision", "recall", "accuracy", "f1"],
    "primary_metric": "precision",
    "pos_label": "confounded",
    
    # Visualization Settings
    "figures": ["gate_comparison", "confusion_matrix", "domain_breakdown"],
    "format": "png",
    "dpi": 300
}
```

## Rationale

**Hardcoded dict over dataclass**: No hyperparameters (deterministic keyword matching). Single fixed config sufficient.

**n_test_hypotheses = 30**: Balanced test set (15 confounded, 15 unconfounded) from PRD.

**target_precision = 0.40**: Direct from hypothesis statement (SHOULD_WORK gate).

**baseline_precision_expected = 0.50**: Random flagging baseline (50/50 chance).

**n_patterns_min = 15**: Architecture requirement (5 patterns × 3 domains).

## File Paths Referenced

- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m3/03_architecture.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m3/03_prd.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m2/03_config.md (base reference)
