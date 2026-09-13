# Configuration Schemas: h-c3
# Composition Contract Validation

**Date:** 2026-07-11  
**Hypothesis:** h-c3 (MECHANISM - COMPOSITION)  
**Type:** PoC - Minimal config for "does it work?" validation  
**Complexity:** LIGHT

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-e1 data; novel composition contract framework  
**Config Files Found:** h-e1/code/config.py (DataConfig structure verified)  
**Pattern Used:** Hardcoded dict (PoC simplicity, deterministic retrospective analysis)

---

## Knowledge Base Patterns Applied

**Applied:** Deterministic retrospective analysis pattern (fixed parameters, no randomness beyond seed=1)

---

## Core Experiment Configuration

### Dataset Configuration

```python
DATASET_CONFIG = {
    # Source: h-e1 results (reused)
    "corpus_path": "docs/youra_research/h-e1/data/defect_corpus.csv",
    
    # Composition subset filter
    "category_filter": "composition",
    "expected_count": 62,
    
    # Data validation
    "checksum": "6572aa34c06ecf13",
    "validate_on_load": True,
    
    # Reproducibility
    "random_seed": 1  # Deterministic loading order
}
```

---

## Contract Configuration

### Contract Types and Execution Parameters

```python
CONTRACT_CONFIG = {
    # Contract types to test
    "types": [
        "device_placement",      # GPU/CPU consistency
        "tensor_layout",         # Shape/dtype consistency
        "cross_library_binding"  # API compatibility
    ],
    
    # Execution constraints
    "timeout_seconds": 10,  # Per-contract execution limit
    "timeout_grace_period": 1,  # Additional buffer for cleanup
    
    # Version tolerance (from h-e1 methodology)
    "version_tolerance": {
        "pytorch_minor": 2,      # ±2 minor releases
        "transformers_minor": 2,
        "cuda_compatible": True  # Use PyTorch-compatible CUDA versions
    },
    
    # Failure propagation
    "bidirectional_propagation": True,
    "propagation_modes": ["forward", "backward"],
    
    # Pipeline stages
    "pipeline_stages": [
        "dataset",
        "preprocess",
        "model",
        "output"
    ]
}
```

---

## Evaluation Configuration

### Metrics and Thresholds

```python
EVALUATION_CONFIG = {
    # Primary metric
    "target_detection_rate": 0.60,  # 60% (SHOULD_WORK gate)
    "baseline_detection_rate": 0.0,  # 0% (from h-e1)
    
    # Statistical parameters
    "confidence_level": 0.95,
    "ci_method": "wilson",  # Wilson score for proportions
    
    # Secondary metrics
    "max_execution_time": 10,  # seconds per contract
    "false_positive_threshold": 0.05,  # <5%
    "version_stability_target": 0.80,  # 80% stability across versions
    
    # Gate conditions
    "gate_pass_threshold": 0.60,
    "gate_warning_threshold": 0.40
}
```

---

## Version Testing Configuration

### Library Version Ranges

```python
VERSION_CONFIG = {
    # Version range specification (±2 minor releases)
    "test_mode": "version_stability",
    
    # Version deltas to test
    "version_deltas": [-2, -1, 0, 1, 2],  # Relative to defect version
    
    # Library version coordination
    "enforce_compatibility": True,  # Ensure PyTorch-CUDA compatibility
    
    # Version timeout
    "per_version_timeout": 10,  # seconds
    "total_stability_timeout": 3600  # 1 hour for all version combinations
}
```

---

## Visualization Configuration

### Figure Parameters

```python
VISUALIZATION_CONFIG = {
    # Output settings
    "output_dir": "docs/youra_research/h-c3/figures",
    "format": "png",
    "dpi": 300,
    
    # Figure sizes
    "figure_sizes": {
        "gate_metrics": (10, 6),
        "detection_by_type": (10, 6),
        "execution_time_dist": (10, 6),
        "version_stability_heatmap": (12, 8),
        "failure_propagation": (10, 10)
    },
    
    # Color scheme
    "colors": {
        "device_placement": "#3498db",     # Blue
        "tensor_layout": "#f39c12",        # Orange
        "cross_library_binding": "#9b59b6", # Purple
        "pass_threshold": "#2ecc71",       # Green
        "fail_threshold": "#e74c3c"        # Red
    },
    
    # Gate metrics (mandatory figure)
    "gate_threshold": 0.60,
    "show_baseline": True,
    "show_ci_bars": True,
    
    # Filenames
    "filenames": {
        "gate_metrics": "gate_metrics.png",
        "detection_by_type": "detection_by_type.png",
        "execution_time_dist": "execution_time_dist.png",
        "version_stability_heatmap": "version_stability_heatmap.png",
        "failure_propagation": "failure_propagation.png"
    }
}
```

---

## Environment Configuration

### Library and Device Requirements

```python
ENVIRONMENT_CONFIG = {
    # Python version
    "python_min_version": "3.8",
    
    # Required libraries
    "dependencies": {
        "torch": ">=1.11",  # Base version for stability testing
        "transformers": ">=4.0",
        "pytest": ">=7.0",
        "hypothesis": ">=6.0",  # Property-based testing
        "pandas": ">=1.3",
        "numpy": ">=1.21",
        "matplotlib": ">=3.4",
        "sklearn": ">=1.0"
    },
    
    # Device configuration
    "device_priority": ["cuda", "cpu"],  # Try CUDA first, fallback to CPU
    "device_required": False,  # Allow CPU-only execution
    
    # Testing framework
    "test_framework": "pytest",
    "property_testing": "hypothesis"
}
```

---

## Output Configuration

### Result Files and Directories

```python
OUTPUT_CONFIG = {
    # Output directories
    "base_dir": "docs/youra_research/h-c3",
    "results_dir": "docs/youra_research/h-c3/results",
    "figures_dir": "docs/youra_research/h-c3/figures",
    "logs_dir": "docs/youra_research/h-c3/logs",
    
    # Result files
    "result_files": {
        "composition_results": "results/composition_results.csv",
        "version_stability": "results/version_stability.csv",
        "false_positives": "results/false_positives.csv",
        "metrics_summary": "results/metrics_summary.json"
    },
    
    # Logging configuration
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "save_logs": True
}
```

---

## Global Configuration

### Consolidated Settings

```python
GLOBAL_CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-c3",
    "experiment_name": "composition_contract_validation",
    "experiment_type": "MECHANISM",
    "gate_type": "SHOULD_WORK",
    
    # Reproducibility
    "random_seed": 1,  # Fixed seed for deterministic retrospective analysis
    "deterministic": True,
    
    # Reused from h-e1
    "baseline_corpus": "docs/youra_research/h-e1/data/defect_corpus.csv",
    "baseline_contractability": 0.0,  # 0% for composition defects
    
    # Critical constraints (from PRD)
    "max_execution_time": 10,  # seconds per contract
    "max_total_runtime": 900,  # 15 minutes for 62 defects
    "version_stability_window": 2,  # ±2 minor releases
    
    # Success criteria
    "poc_pass": {
        "detection_rate_improvement": True,  # > 0% baseline
        "all_defects_processed": True,
        "execution_time_met": True
    },
    
    "gate_pass": {
        "detection_rate": 0.60,
        "version_stability": 0.80,
        "false_positive_rate": 0.05
    }
}
```

---

## Usage Example

```python
# In run_experiment.py
from config import (
    DATASET_CONFIG,
    CONTRACT_CONFIG,
    EVALUATION_CONFIG,
    VERSION_CONFIG,
    VISUALIZATION_CONFIG,
    OUTPUT_CONFIG,
    GLOBAL_CONFIG
)
import pandas as pd
import time

# Set seed
import random
import numpy as np
random.seed(GLOBAL_CONFIG["random_seed"])
np.random.seed(GLOBAL_CONFIG["random_seed"])

# Load dataset
corpus = pd.read_csv(DATASET_CONFIG["corpus_path"])
composition_defects = corpus[corpus['category'] == DATASET_CONFIG["category_filter"]]
assert len(composition_defects) == DATASET_CONFIG["expected_count"]

# Initialize contract validator
validator = CompositionContractValidator(
    contract_types=CONTRACT_CONFIG["types"],
    timeout=CONTRACT_CONFIG["timeout_seconds"],
    pipeline_stages=CONTRACT_CONFIG["pipeline_stages"]
)

# Execute validation
results = []
for defect in composition_defects.itertuples():
    start_time = time.time()
    contractable, exec_time = validator.validate_chain(defect)
    results.append({
        "defect_id": defect.id,
        "contractable": contractable,
        "execution_time": exec_time
    })

# Calculate metrics
detection_rate = sum(r["contractable"] for r in results) / len(results)
gate_pass = detection_rate >= EVALUATION_CONFIG["gate_pass_threshold"]

print(f"Detection Rate: {detection_rate:.2%}")
print(f"Gate Status: {'PASS' if gate_pass else 'FAIL'}")
```

---

## Rationale for Non-Standard Values

**random_seed: 1**
- Minimal seed value for deterministic retrospective analysis
- Different from h-e1 (seed=42) to avoid accidental coupling

**timeout_seconds: 10**
- Same as h-e1/h-m2 constraint (lightweight probe requirement)
- Ensures contracts are practical for real-time validation

**version_tolerance.minor: 2**
- ±2 minor releases matches h-e1 version stability methodology
- Balances coverage vs combinatorial explosion

**target_detection_rate: 0.60**
- SHOULD_WORK gate threshold from Phase 2B success criteria
- Ambitious given h-e1's 0% baseline for composition defects

**bidirectional_propagation: True**
- Core hypothesis mechanism (forward + backward failure propagation)
- Novel feature distinguishing h-c3 from h-m1/h-m2

---

## Self-Validation Checks

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Base hypothesis config verified (h-e1 DataConfig structure)
- [x] EXISTENCE rules applied (minimal config, single fixed setup)
- [x] No hyperparameter grid (PoC validation only)
- [x] No subtask decomposition (config phase doesn't allocate subtasks)

---

**End of Configuration Document**

*Ready for Phase 4 - Code generation using these config schemas*
