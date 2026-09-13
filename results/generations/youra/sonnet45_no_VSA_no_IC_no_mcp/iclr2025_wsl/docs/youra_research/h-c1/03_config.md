# Configuration Schema: h-c1 Domain Boundary Detection

**Hypothesis:** h-c1 (CONDITION - boundary case classification)
**Type:** CONDITION
**Gate:** SHOULD_WORK (accuracy ≥ 0.80)

---

## Codebase Analysis (Serena)

**Project Type**: incremental_extension
**Status**: Extending h-m4 verifier (rule-based, no training)
**Config Files Found**: h-m4/src/config.py (hardcoded dict pattern)
**Pattern Used**: Hardcoded dict (no hyperparameter tuning, deterministic boundary detector)

---

## Inherited Configuration (Base Hypothesis)

### h-m4 Configuration Pattern (From Actual Code)

```python
# From: h-m4/src/config.py (ACTUAL CODE)
# Pattern: Hardcoded dict for deterministic pipelines (no training)
CONFIG = {
    "seed": 42,
    "kb_path": "../h-m1/data/pwc_cache/kb.yaml",
    "output_dir": "data/",
    "figures_dir": "figures/",
    # ... other fixed parameters
}
```

**h-c1 follows same pattern**: Rule-based boundary detector (no training loop).

**Verified from**: h-m4/src/config.py actual implementation

---

## Configuration

Applied: Hardcoded dict pattern (Archon KB - deterministic experiment config)

```python
# config.py
CONFIG = {
    # Paths (External Dependencies)
    "kb_path": "../h-m1/data/pwc_cache/kb.yaml",
    "boundary_test_path": "data/boundary_hypotheses.json",
    "validation_set_path": "data/validation_set.json",
    "output_dir": "data/",
    "figures_dir": "figures/",
    
    # Random Seeds
    "seed": 42,
    "tfidf_seed": 42,
    
    # Domain Boundary Detector (FR-1)
    "similarity_threshold": 0.7,  # Jaccard similarity threshold
    "max_keywords": 5,  # TF-IDF top-k keywords
    "tfidf_max_features": 100,
    "tfidf_min_df": 1,
    "tfidf_max_df": 0.9,
    
    # Gate Thresholds (FR-6)
    "gate_threshold": 0.80,  # Accuracy threshold (SHOULD_WORK)
    "precision_threshold": 0.75,
    "recall_threshold": 0.80,
    
    # Threshold Tuning (FR-7, optional)
    "threshold_range": [0.5, 0.6, 0.7, 0.8, 0.9],
    "n_folds": 5,  # 5-fold CV
    
    # Visualization (FR-8)
    "figures": [
        "gate_metrics_comparison",
        "confusion_matrix",
        "threshold_sensitivity_curve",
        "domain_coverage_heatmap"
    ],
    "format": "png",
    "dpi": 300,
    
    # Evaluation Metrics
    "metrics": ["accuracy", "precision", "recall", "f1"],
    "primary_metric": "accuracy",
    
    # Dataset
    "n_boundary_test_cases": 10,
    "n_validation_set": 100,
    "validation_split": {
        "in_scope": 50,
        "boundary": 50
    },
    
    # Domain-Specific Terms (ML Vocabulary Filter)
    "ml_vocabulary": [
        "vision", "nlp", "rl", "speech", "multimodal",
        "CNN", "BERT", "transformer", "ResNet", "LSTM",
        "image", "text", "agent", "audio", "video",
        "classification", "detection", "segmentation", "generation",
        "accuracy", "F1", "BLEU", "reward", "perplexity"
    ]
}
```

---

## Rationale

**Hardcoded dict over dataclass**: No training loop (rule-based system). Single fixed config sufficient for CONDITION validation.

**similarity_threshold = 0.7**: From Phase 2C research (GitHub repo B.1 - OOD detection threshold).

**gate_threshold = 0.80**: From PRD success criteria (≥80% accuracy).

**precision_threshold = 0.75, recall_threshold = 0.80**: From PRD secondary criteria.

**max_keywords = 5**: Balance coverage (enough keywords) vs noise (too many generic terms).

**tfidf_max_features = 100**: Standard vocabulary size for domain classification.

**threshold_range = [0.5-0.9]**: Grid search range from Phase 2C research.

**n_folds = 5**: Standard cross-validation for small validation set (100 hypotheses).

**n_boundary_test_cases = 10**: From PRD requirement (FR-5).

**n_validation_set = 100**: 50 in-scope + 50 boundary for threshold tuning.

**ml_vocabulary**: Domain-specific terms to filter generic tokens (e.g., "performance", "method").

---

## Hyperparameters (No Tuning Required)

| Parameter | Value | Source |
|-----------|-------|--------|
| similarity_threshold | 0.7 | Phase 2C (GitHub B.1) |
| max_keywords | 5 | Standard TF-IDF practice |
| tfidf_max_features | 100 | Domain keyword vocabulary size |
| gate_threshold | 0.80 | PRD success criteria |

**Note**: Threshold tuning (FR-7) is optional - default 0.7 used for main experiment.

---

## File Paths Referenced

- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-c1/03_architecture.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-c1/03_prd.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m4/src/config.py (base reference)
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m1/data/pwc_cache/kb.yaml (external dependency)

---

*Applied Archon KB pattern: Hardcoded dict for deterministic pipelines*
*Inherited pattern: h-m4 config structure (no training loop)*
*Codebase analysis completed (h-m4/src/config.py verified)*
