# Configuration Specification: H-M4
# Adoption Tracking Measurement Infrastructure

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM (SHOULD_WORK gate)  
**Applied:** Hardcoded dict pattern (h-m3 consistency), async queue pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m3 code  
**Config Files Found:** h-m3/code/src/config.py  
**Pattern Used:** Hardcoded dict (consistent with h-m3)

---

## Inherited Configuration (h-m3)

The following configs are inherited from h-m3:

```python
# From: h-m3/code/src/config.py (ACTUAL CODE)
INSTRUMENTATION_CONFIG = {
    "telemetry": {
        "db_path": "telemetry.db",
        "opt_in": True,
        "hash_algorithm": "sha256",
        "hash_truncate_length": 16
    },
    "loader": {
        "check_deprecation": True,
        "max_check_latency_ms": 100,
        "fallback_on_timeout": "load_without_intervention"
    },
    "events": {
        "schema_version": "1.0",
        "fields": [
            "user_id_hash",
            "dataset_name",
            "user_group",
            "intervention_type",
            "timestamp",
            "event_type",
            "metadata"
        ],
        "retention_days": 180,
        "opt_out_enabled": True
    },
    "performance": {
        "max_overhead_pct": 10.0,
        "plan_generation_timeout_sec": 5,
        "cache_warmup_enabled": True
    }
}

RCT_EXPERIMENT_CONFIG = {
    "groups": {
        "control": {"name": "Control", "intervention": "deprecation_notice_only", "sample_size": 200},
        "manual": {"name": "Manual", "intervention": "deprecation_notice_and_manual_guide", "sample_size": 200},
        "treatment": {"name": "Treatment", "intervention": "deprecation_notice_and_automated_plan", "sample_size": 200}
    },
    "randomization": {
        "seed": 42,
        "assignment_method": "user_id_hash",
        "hash_modulo": 3
    }
}
```

**Verified from:** `h-m3/code/src/config.py` (actual implementation)

---

## M4-1: Async Queue (Complexity: 11, Budget: 2 subtasks)

**Applied:** Async batching pattern

### Configuration (Hardcoded Dict)

```python
# src/config.py
ASYNC_QUEUE_CONFIG = {
    "db_path": "telemetry.db",
    "batch_size": 100,
    "flush_interval_sec": 5.0,
    "max_queue_size": 10000,
    "wal_mode": True
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M4-1-1 | Async queue | Background flush task with asyncio |
| M4-1-2 | WAL writer | SQLite batch write with WAL mode |

---

## M4-2: Telemetry Logger (Complexity: 9, Budget: 2 subtasks)

**Applied:** Retry queue pattern

### Configuration (Hardcoded Dict)

```python
TELEMETRY_LOGGER_CONFIG = {
    "max_retries": 3,
    "backoff_base": 2,
    "fallback_dir": "logs/fallback",
    "fallback_format": "jsonl"
}
```

### Subtasks (2/2 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M4-2-1 | Retry logger | Exponential backoff retry logic |
| M4-2-2 | Fallback writer | Local JSONL fallback for failures |

---

## M4-3: Performance Tracking (Complexity: 10)

**Applied:** Performance profiling pattern

### Configuration (Hardcoded Dict)

```python
PERFORMANCE_TRACKER_CONFIG = {
    "track_latency": True,
    "track_memory": True,
    "track_cpu": True,
    "percentiles": [50, 95, 99]
}
```

**Note:** No subtask allocation (EXISTENCE PoC, single fixed config).

---

## M4-4: Baseline Benchmarks (Complexity: 8)

**Applied:** Standard PyTorch benchmarking

### Configuration (Hardcoded Dict)

```python
BASELINE_BENCHMARK_CONFIG = {
    "num_runs": 100,
    "dataset_sizes": {
        "small": "glue/cola",
        "medium": "squad",
        "large": "c4",
        "xlarge": "imagenet-1k"
    },
    "output_path": "baseline_performance.json"
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-5: Instrumented Benchmarks (Complexity: 9)

**Applied:** Standard PyTorch benchmarking

### Configuration (Hardcoded Dict)

```python
INSTRUMENTED_BENCHMARK_CONFIG = {
    "num_runs": 100,
    "dataset_sizes": {
        "small": "glue/cola",
        "medium": "squad",
        "large": "c4",
        "xlarge": "imagenet-1k"
    },
    "output_path": "instrumented_performance.json"
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-6: User Simulation (Complexity: 10)

**Applied:** Standard Python simulation

### Configuration (Hardcoded Dict)

```python
USER_SIMULATION_CONFIG = {
    "num_users": 1000,
    "simulation_days": 30,
    "loads_per_user": 8,
    "deprecated_encounter_rate": 0.4
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-7: Ground Truth Validation (Complexity: 8)

**Applied:** Standard validation pattern

### Configuration (Hardcoded Dict)

```python
GROUND_TRUTH_CONFIG = {
    "baseline_log_path": "data/ground_truth.jsonl",
    "telemetry_db_path": "data/telemetry.db",
    "validation_metrics": ["precision", "recall", "f1"]
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-8: Adoption Tracking (Complexity: 10)

**Applied:** Standard SQL pattern

### Configuration (Hardcoded Dict)

```python
ADOPTION_TRACKING_CONFIG = {
    "adoption_window_days": 30,
    "db_path": "telemetry.db",
    "funnel_stages": [
        "deprecated_loads",
        "successor_loads",
        "adoptions_within_window"
    ]
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-9: Capture Rate Analysis (Complexity: 11)

**Applied:** Wilson score CI pattern

### Configuration (Hardcoded Dict)

```python
CAPTURE_RATE_CONFIG = {
    "confidence_level": 0.95,
    "min_capture_rate": 0.95,
    "completeness_threshold": 0.95,
    "delivery_latency_percentiles": [50, 95, 99]
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## M4-10: Overhead Analysis (Complexity: 9)

**Applied:** Statistical test pattern

### Configuration (Hardcoded Dict)

```python
OVERHEAD_ANALYSIS_CONFIG = {
    "max_overhead_pct": 10.0,
    "alpha": 0.05,
    "visualization_output": "figures/overhead_by_size.png",
    "threshold_line": 10.0
}
```

**Note:** No subtask allocation (EXISTENCE PoC).

---

## Extended Configuration (h-m4 Extensions)

```python
# src/config.py
import os

# Import h-m3 configs
from sys import path as syspath
syspath.insert(0, '../../h-m3/code')
from src.config import INSTRUMENTATION_CONFIG, RCT_EXPERIMENT_CONFIG

# h-m4 async telemetry
ASYNC_QUEUE_CONFIG = {
    "db_path": "telemetry.db",
    "batch_size": 100,
    "flush_interval_sec": 5.0,
    "max_queue_size": 10000,
    "wal_mode": True
}

TELEMETRY_LOGGER_CONFIG = {
    "max_retries": 3,
    "backoff_base": 2,
    "fallback_dir": "logs/fallback",
    "fallback_format": "jsonl"
}

# Performance tracking
PERFORMANCE_TRACKER_CONFIG = {
    "track_latency": True,
    "track_memory": True,
    "track_cpu": True,
    "percentiles": [50, 95, 99]
}

# Baseline benchmarks
BASELINE_BENCHMARK_CONFIG = {
    "num_runs": 100,
    "dataset_sizes": {
        "small": "glue/cola",
        "medium": "squad",
        "large": "c4",
        "xlarge": "imagenet-1k"
    },
    "output_path": "baseline_performance.json"
}

# Instrumented benchmarks
INSTRUMENTED_BENCHMARK_CONFIG = {
    "num_runs": 100,
    "dataset_sizes": {
        "small": "glue/cola",
        "medium": "squad",
        "large": "c4",
        "xlarge": "imagenet-1k"
    },
    "output_path": "instrumented_performance.json"
}

# User simulation
USER_SIMULATION_CONFIG = {
    "num_users": 1000,
    "simulation_days": 30,
    "loads_per_user": 8,
    "deprecated_encounter_rate": 0.4
}

# Ground truth validation
GROUND_TRUTH_CONFIG = {
    "baseline_log_path": "data/ground_truth.jsonl",
    "telemetry_db_path": "data/telemetry.db",
    "validation_metrics": ["precision", "recall", "f1"]
}

# Adoption tracking
ADOPTION_TRACKING_CONFIG = {
    "adoption_window_days": 30,
    "db_path": "telemetry.db",
    "funnel_stages": [
        "deprecated_loads",
        "successor_loads",
        "adoptions_within_window"
    ]
}

# Capture rate analysis
CAPTURE_RATE_CONFIG = {
    "confidence_level": 0.95,
    "min_capture_rate": 0.95,
    "completeness_threshold": 0.95,
    "delivery_latency_percentiles": [50, 95, 99]
}

# Overhead analysis
OVERHEAD_ANALYSIS_CONFIG = {
    "max_overhead_pct": 10.0,
    "alpha": 0.05,
    "visualization_output": "figures/overhead_by_size.png",
    "threshold_line": 10.0
}

# Deprecation registry (simulation)
DEPRECATION_REGISTRY = {
    "glue/cola": "glue/cola_v2",
    "squad": "squad_v2"
}

# Dataset size mapping
DATASET_MAP = {
    "small": "glue/cola",
    "medium": "squad",
    "large": "c4",
    "xlarge": "imagenet-1k"
}
```

---

## Configuration Access Pattern

```python
# Import all configs
from src.config import (
    ASYNC_QUEUE_CONFIG,
    TELEMETRY_LOGGER_CONFIG,
    PERFORMANCE_TRACKER_CONFIG,
    BASELINE_BENCHMARK_CONFIG,
    INSTRUMENTED_BENCHMARK_CONFIG,
    USER_SIMULATION_CONFIG,
    GROUND_TRUTH_CONFIG,
    ADOPTION_TRACKING_CONFIG,
    CAPTURE_RATE_CONFIG,
    OVERHEAD_ANALYSIS_CONFIG,
    DEPRECATION_REGISTRY,
    DATASET_MAP,
    INSTRUMENTATION_CONFIG,
    RCT_EXPERIMENT_CONFIG
)

# Async queue
queue = AsyncTelemetryQueue(
    db_path=ASYNC_QUEUE_CONFIG["db_path"],
    batch_size=ASYNC_QUEUE_CONFIG["batch_size"],
    flush_interval=ASYNC_QUEUE_CONFIG["flush_interval_sec"]
)

# Telemetry logger
logger = TelemetryLogger(
    async_queue=queue,
    fallback_dir=TELEMETRY_LOGGER_CONFIG["fallback_dir"]
)

# Performance tracker
tracker = PerformanceTracker()

# Benchmarker
benchmarker = PerformanceBenchmarker(
    tracker=tracker,
    num_runs=BASELINE_BENCHMARK_CONFIG["num_runs"]
)

# User simulator
simulator = UserWorkloadSimulator(
    num_users=USER_SIMULATION_CONFIG["num_users"],
    days=USER_SIMULATION_CONFIG["simulation_days"],
    loads_per_user=USER_SIMULATION_CONFIG["loads_per_user"],
    deprecated_encounter_rate=USER_SIMULATION_CONFIG["deprecated_encounter_rate"]
)

# Capture analyzer
capture_analyzer = CaptureRateAnalyzer(
    db_path=ADOPTION_TRACKING_CONFIG["db_path"]
)

# Overhead analyzer
overhead_analyzer = OverheadAnalyzer(
    baseline_path=BASELINE_BENCHMARK_CONFIG["output_path"],
    instrumented_path=INSTRUMENTED_BENCHMARK_CONFIG["output_path"]
)
```

---

## Configuration Validation

Runtime validation checks:

```python
def validate_config():
    """Validate all configuration values at startup."""
    
    # Async queue
    assert ASYNC_QUEUE_CONFIG["batch_size"] > 0
    assert ASYNC_QUEUE_CONFIG["flush_interval_sec"] > 0
    assert ASYNC_QUEUE_CONFIG["max_queue_size"] >= ASYNC_QUEUE_CONFIG["batch_size"]
    
    # Telemetry logger
    assert TELEMETRY_LOGGER_CONFIG["max_retries"] >= 1
    assert TELEMETRY_LOGGER_CONFIG["backoff_base"] >= 2
    
    # Performance tracker
    assert all(0 <= p <= 100 for p in PERFORMANCE_TRACKER_CONFIG["percentiles"])
    
    # Benchmarks
    assert BASELINE_BENCHMARK_CONFIG["num_runs"] >= 30
    assert INSTRUMENTED_BENCHMARK_CONFIG["num_runs"] >= 30
    
    # User simulation
    assert USER_SIMULATION_CONFIG["num_users"] > 0
    assert USER_SIMULATION_CONFIG["simulation_days"] > 0
    assert 0 <= USER_SIMULATION_CONFIG["deprecated_encounter_rate"] <= 1
    
    # Capture rate
    assert 0 < CAPTURE_RATE_CONFIG["confidence_level"] < 1
    assert 0 < CAPTURE_RATE_CONFIG["min_capture_rate"] <= 1
    
    # Overhead analysis
    assert OVERHEAD_ANALYSIS_CONFIG["max_overhead_pct"] > 0
    assert 0 < OVERHEAD_ANALYSIS_CONFIG["alpha"] < 1
```

---

## Summary

**Total Configuration Sections**: 10  
**Total Subtasks Allocated**: 4 (within 2 subtask budget for EXISTENCE PoC)  
**Config Pattern**: Hardcoded dict (consistent with h-m3)  
**Validation**: Runtime checks for all thresholds  
**Integration**: Extends h-m3 instrumentation + RCT configs

**Note**: Most tasks have no subtask allocation as this is an EXISTENCE hypothesis (PoC). Only tasks M4-1 and M4-2 require subtask decomposition due to async complexity.

**Next Steps**: Phase 4 (Implementation) will copy-paste these configs into `src/config.py`.

---

**End of Configuration Specification**
