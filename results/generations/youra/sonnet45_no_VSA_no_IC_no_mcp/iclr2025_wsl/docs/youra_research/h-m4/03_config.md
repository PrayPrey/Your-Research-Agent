# Configuration Schema: h-m4 Post-Hoc Experimental Validation

**Hypothesis:** h-m4 (≥65% of "testable" hypotheses yield p < 0.05)
**Type:** MECHANISM (meta-research validation)
**Gate:** MUST_WORK (success_rate ≥ 0.65)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase
**Status**: Extending h-m3 confound detection + h-m1 KB lookup
**Config Files Found**: h-m3/src/confound_db.py, h-m1/code/extract_kb.py
**Pattern Used**: Hardcoded dict (no training, deterministic pipeline)

## Inherited Configuration (Base Hypothesis)

### h-m3 Confound Patterns (From Actual Code)

```python
# From: h-m3/src/confound_db.py (ACTUAL CODE)
CONFOUND_PATTERNS = {
    "nlp": [
        {"keywords": ["tokenizer", "vocab", "BLEU"], "description": "tokenizer-BLEU confound"},
        {"keywords": ["sequence length", "accuracy"], "description": "length-metric confound"},
        {"keywords": ["vocabulary size", "perplexity"], "description": "vocab-perplexity confound"},
        {"keywords": ["subword", "tokenization", "F1"], "description": "tokenization-F1 confound"},
        {"keywords": ["max length", "truncation", "score"], "description": "truncation-score confound"},
    ],
    "vision": [
        {"keywords": ["resolution", "architecture"], "description": "resolution-architecture confound"},
        {"keywords": ["augmentation", "model capacity"], "description": "augmentation-capacity confound"},
        {"keywords": ["image size", "depth"], "description": "size-depth confound"},
        {"keywords": ["color depth", "network size"], "description": "color-network confound"},
        {"keywords": ["crop size", "model complexity"], "description": "crop-complexity confound"},
    ],
    "training": [
        {"keywords": ["batch size", "learning rate"], "description": "batch-LR confound"},
        {"keywords": ["optimizer", "weight decay"], "description": "optimizer-regularization confound"},
        {"keywords": ["epochs", "dataset size"], "description": "epochs-data confound"},
        {"keywords": ["batch", "LR"], "description": "batch-LR confound (abbrev)"},
        {"keywords": ["momentum", "learning rate schedule"], "description": "momentum-schedule confound"},
    ],
}
```

### h-m1 KB Structure (From Actual Code)

```python
# From: h-m1/code/extract_kb.py (ACTUAL CODE)
# KB format: YAML triples
# kb.yaml structure:
# metadata:
#   triple_count: N
# triples:
#   - dataset: "CIFAR-10"
#     benchmark: "image-classification"
#     metric: "Accuracy"
```

**Verified from**: h-m3/src/confound_db.py, h-m1/code/extract_kb.py

## Configuration

Applied: Hardcoded dict pattern (Archon KB - meta-research config standard)

```python
# config.py
CONFIG = {
    # Paths (External Dependencies)
    "kb_path": "../h-m1/data/pwc_cache/kb.yaml",
    "output_dir": "data/",
    "figures_dir": "figures/",
    
    # Random Seeds
    "seed": 42,
    "generator_seed": 42,
    "sampler_seed": 42,
    "experiment_seed": 42,
    
    # Hypothesis Pool Generation (FR-1)
    "n_hypothesis_pool": 100,
    "domains": ["nlp", "vision", "training", "multimodal"],
    "complexity_levels": ["simple", "moderate", "complex"],
    "domain_balance_target": 25,
    "complexity_balance_target": 33,
    
    # Sampling (FR-3)
    "n_sample_size": 20,
    
    # Gate Thresholds (FR-5)
    "gate_threshold": 0.65,
    "baseline_threshold": 0.50,
    "alpha": 0.05,
    
    # Experiment Settings (FR-4)
    "control_epochs": 10,
    "treatment_epochs": 10,
    "control_batch_size": 32,
    "treatment_batch_size": 32,
    
    # Visualization (FR-7)
    "figures": [
        "gate_metrics_comparison",
        "success_rate_by_domain",
        "classification_distribution",
        "pvalue_distribution"
    ],
    "format": "png",
    "dpi": 300,
    
    # LLM API (Hypothesis Generation)
    "llm_api_endpoint": "https://api.anthropic.com/v1/messages",
    "llm_model": "claude-3-5-sonnet-20241022",
    "llm_max_tokens": 1024,
    "llm_temperature": 0.7,
    
    # Confound Patterns (Inherited from h-m3)
    "confound_patterns": CONFOUND_PATTERNS,
    
    # Evaluation Metrics
    "metrics": ["success_rate", "precision", "binomial_p"],
    "primary_metric": "success_rate"
}
```

## Rationale

**Hardcoded dict over dataclass**: No hyperparameter tuning (deterministic pipeline). Single fixed config sufficient for EXISTENCE validation.

**n_hypothesis_pool = 100**: From PRD requirement (FR-1).

**n_sample_size = 20**: From PRD requirement (FR-3).

**gate_threshold = 0.65**: Direct from hypothesis statement (MUST_WORK gate).

**baseline_threshold = 0.50**: Random classification baseline.

**control_epochs = 10**: Simplified PoC experiments (not full training), sufficient to detect effect.

**llm_temperature = 0.7**: Balance diversity (100 diverse hypotheses) vs coherence.

## File Paths Referenced

- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m4/03_architecture.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m4/03_prd.md
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m3/src/confound_db.py (base reference)
- /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_wsl/docs/youra_research/h-m1/code/extract_kb.py (base reference)
