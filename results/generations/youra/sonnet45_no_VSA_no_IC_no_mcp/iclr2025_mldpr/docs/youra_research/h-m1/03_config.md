# Configuration Specification: H-M1
# Health Metrics Deprecation Detection

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM  
**Applied:** API client config pattern, metric threshold pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from base code  
**Config Files Found:** h-e1/code/config.py (archived)  
**Pattern Used:** Hardcoded dict (matches h-e1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Pattern (From Actual Code)

The base hypothesis h-e1 uses hardcoded dict pattern. Continuing this pattern for consistency.

```python
# From: h-e1/code/config.py (ACTUAL CODE - archived)
CONFIG = {
    "sampling": {
        "random_seed": 42,
    },
    "cache": {
        "enabled": True,
        "cache_dir": "cache",
        "format": "json",
    },
    "api": {
        "max_retries": 3,
        "backoff_base": 1,
        "timeout_seconds": 30,
    },
    "output": {
        "figures_dir": "figures",
        "csv_export": "compliance_results.csv",
        "json_export": "compliance_summary.json",
    },
}
```

**Verified from**: h-e1/code/config.py (actual implementation)

---

## M-1: API Clients (Complexity: 12, Budget: 3 subtasks)

**Applied:** Rate-limiting pattern, file-based cache pattern

### Configuration

```python
# src/config.py
HEALTH_METRICS_CONFIG = {
    "api": {
        "hf_cache_dir": ".cache/hf",
        "pwc_cache_dir": ".cache/pwc",
        "gh_cache_dir": ".cache/gh",
        "gh_token": None,  # Optional, set via env var GITHUB_TOKEN
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "backoff_base": 2,
        "timeout_seconds": 30,
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | HuggingFaceClient | Download history endpoint with file cache |
| M-1-2 | PapersWithCodeClient | Citation graph endpoint with file cache |
| M-1-3 | GitHubClient | Issue tracker endpoint with rate limiting |

---

## M-2: Metrics Computation (Complexity: 9, Budget: 2 subtasks)

**Applied:** Threshold-based flagging pattern

### Configuration

```python
HEALTH_METRICS_CONFIG = {
    "metrics": {
        "velocity_threshold": 0.3,
        "emergence_threshold": 3,
        "issue_threshold": 0.6,
        "top_k_candidates": 30,
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | Metric functions | velocity, emergence, issue_ratio computation |
| M-2-2 | Flagging logic | Combine thresholds + top-K selection |

---

## M-3: Data Collection (Complexity: 11, Budget: 2 subtasks)

**Applied:** Batch processing pattern

### Configuration

```python
HEALTH_METRICS_CONFIG = {
    "data": {
        "observation_months": 6,
        "download_history_days": 180,
        "dataset_sample_size": 1000,
        "output_dir": "data",
        "random_seed": 42,
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | DataCollector | Batch collection with progress logging |
| M-3-2 | GroundTruthTracker | Month 0/6 snapshots + deprecation event detection |

---

## M-4: Evaluation Pipeline (Complexity: 14, Budget: 3 subtasks)

**Applied:** sklearn metrics pattern, matplotlib visualization pattern

### Configuration

```python
HEALTH_METRICS_CONFIG = {
    "evaluation": {
        "precision_target": 0.6,
        "recall_target": 0.8,
    },
    "visualization": {
        "figures_dir": "figures",
        "dpi": 100,
        "figsize": (10, 6),
    }
}
```

### Subtasks (3/3 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | HealthMetricsEvaluator | Precision/recall + confusion matrix + gate check |
| M-4-2 | HealthMetricsVisualizer | 5 plot functions (gate, distribution, confusion, sensitivity, timeline) |
| M-4-3 | Report generation | JSON report with gate status |

---

## M-5: Integration (Complexity: 8, Budget: 2 subtasks)

**Applied:** Pipeline orchestration pattern

### Configuration

```python
HEALTH_METRICS_CONFIG = {
    "pipeline": {
        "log_level": "INFO",
        "checkpoint_enabled": True,
        "checkpoint_dir": "checkpoints",
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | main.py orchestration | 10-step pipeline with error handling |
| M-5-2 | Config module | Merge all config sections into single dict |

---

## M-6: Validation (Complexity: 10, Budget: 2 subtasks)

**Applied:** Fixture-based testing pattern

### Configuration

```python
HEALTH_METRICS_CONFIG = {
    "testing": {
        "fixture_dir": "tests/fixtures",
        "synthetic_dataset_count": 100,
    }
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | Test fixtures | Synthetic download history, citation graph, issues |
| M-6-2 | Unit tests | Metric computation + precision/recall verification |

---

## Complete Configuration (Copy-Paste Ready)

```python
# src/config.py
# H-M1 Health Metrics Deprecation Detection Configuration

HEALTH_METRICS_CONFIG = {
    # API Clients
    "api": {
        "hf_cache_dir": ".cache/hf",
        "pwc_cache_dir": ".cache/pwc",
        "gh_cache_dir": ".cache/gh",
        "gh_token": None,
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "backoff_base": 2,
        "timeout_seconds": 30,
    },
    
    # Metrics Thresholds
    "metrics": {
        "velocity_threshold": 0.3,
        "emergence_threshold": 3,
        "issue_threshold": 0.6,
        "top_k_candidates": 30,
    },
    
    # Data Collection
    "data": {
        "observation_months": 6,
        "download_history_days": 180,
        "dataset_sample_size": 1000,
        "output_dir": "data",
        "random_seed": 42,
    },
    
    # Evaluation
    "evaluation": {
        "precision_target": 0.6,
        "recall_target": 0.8,
    },
    
    # Visualization
    "visualization": {
        "figures_dir": "figures",
        "dpi": 100,
        "figsize": (10, 6),
    },
    
    # Pipeline
    "pipeline": {
        "log_level": "INFO",
        "checkpoint_enabled": True,
        "checkpoint_dir": "checkpoints",
    },
    
    # Testing
    "testing": {
        "fixture_dir": "tests/fixtures",
        "synthetic_dataset_count": 100,
    }
}


def validate_config(config):
    """Validate H-M1 configuration constraints."""
    assert config["api"]["rate_limit_delay"] > 0
    assert config["api"]["max_retries"] >= 0
    assert config["api"]["timeout_seconds"] > 0
    assert config["metrics"]["velocity_threshold"] > 0
    assert config["metrics"]["emergence_threshold"] > 0
    assert 0 < config["metrics"]["issue_threshold"] < 1
    assert config["metrics"]["top_k_candidates"] > 0
    assert config["data"]["observation_months"] > 0
    assert config["data"]["download_history_days"] > 0
    assert config["data"]["dataset_sample_size"] > 0
    assert 0 < config["evaluation"]["precision_target"] <= 1
    assert 0 < config["evaluation"]["recall_target"] <= 1
    return True


validate_config(HEALTH_METRICS_CONFIG)
```

---

## Configuration Usage Pattern

```python
# Usage in modules
from src.config import HEALTH_METRICS_CONFIG

# API client initialization
hf_client = HuggingFaceClient(
    cache_dir=HEALTH_METRICS_CONFIG["api"]["hf_cache_dir"]
)

gh_client = GitHubClient(
    token=HEALTH_METRICS_CONFIG["api"]["gh_token"],
    cache_dir=HEALTH_METRICS_CONFIG["api"]["gh_cache_dir"]
)

# Metrics computation
computer = HealthMetricsComputer(
    velocity_threshold=HEALTH_METRICS_CONFIG["metrics"]["velocity_threshold"],
    emergence_threshold=HEALTH_METRICS_CONFIG["metrics"]["emergence_threshold"],
    issue_threshold=HEALTH_METRICS_CONFIG["metrics"]["issue_threshold"]
)

# Evaluation
evaluator = HealthMetricsEvaluator(
    metrics_csv="data/health_metrics.csv",
    ground_truth_json="data/ground_truth.json"
)

gate_pass = evaluator.check_gate_metrics()
```

---

## Subtask Budget Summary

| Task | Complexity | Budget | Used | Status |
|------|------------|--------|------|--------|
| M-1 | 12 | 3 | 3 | Full |
| M-2 | 9 | 2 | 2 | Full |
| M-3 | 11 | 2 | 2 | Full |
| M-4 | 14 | 3 | 3 | Full |
| M-5 | 8 | 2 | 2 | Full |
| M-6 | 10 | 2 | 2 | Full |
| **Total** | **64** | **14** | **14** | **Full** |

---

**End of Configuration Specification**
