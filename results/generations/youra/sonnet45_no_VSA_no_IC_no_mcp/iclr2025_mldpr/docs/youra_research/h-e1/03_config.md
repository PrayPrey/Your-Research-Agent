# Configuration Specification: H-E1
# Load-Time Instrumentation PoC

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** EXISTENCE (Infrastructure PoC)  
**Applied:** Minimal config pattern, telemetry privacy defaults

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** Green-field project - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (minimal PoC)

---

## E-1: Core Instrumentation (Complexity: 11, Budget: 1 subtask)

**Applied:** Privacy-preserving telemetry pattern

### Configuration (Hardcoded Dict)

```python
# src/config.py
INSTRUMENTATION_CONFIG = {
    # Telemetry Backend
    "telemetry": {
        "db_path": "telemetry.db",
        "opt_in": True,
        "hash_algorithm": "sha256",
        "hash_truncate_length": 16
    },
    
    # Benchmark Settings
    "benchmark": {
        "datasets": ["cifar10", "imdb", "wikitext-103"],
        "runs_per_dataset": 10,
        "output_csv_path": "benchmark_results.csv"
    },
    
    # Evaluation Thresholds
    "evaluation": {
        "overhead_threshold_pct": 10.0,
        "capture_rate_threshold_pct": 95.0,
        "min_event_count": 100
    },
    
    # Simulation Parameters
    "simulation": {
        "event_count": 100,
        "duration_months": 6,
        "successor_adoption_rate": 0.3,
        "output_json_path": "simulation.json"
    },
    
    # Visualization
    "visualization": {
        "figures_dir": "figures/",
        "dpi": 100,
        "figsize": (10, 6)
    }
}
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| E-1-1 | Config module | Single dict with all defaults for instrumentation, benchmark, evaluation |

---

## Configuration Access Pattern

```python
# Usage in modules
from src.config import INSTRUMENTATION_CONFIG

# Telemetry initialization
telemetry = TelemetryLogger(
    db_path=INSTRUMENTATION_CONFIG["telemetry"]["db_path"],
    opt_in=INSTRUMENTATION_CONFIG["telemetry"]["opt_in"]
)

# Benchmark setup
harness = BenchmarkHarness(
    datasets=INSTRUMENTATION_CONFIG["benchmark"]["datasets"],
    runs_per_dataset=INSTRUMENTATION_CONFIG["benchmark"]["runs_per_dataset"]
)

# Evaluation gates
evaluator = Evaluator(
    overhead_threshold=INSTRUMENTATION_CONFIG["evaluation"]["overhead_threshold_pct"],
    capture_threshold=INSTRUMENTATION_CONFIG["evaluation"]["capture_rate_threshold_pct"],
    min_events=INSTRUMENTATION_CONFIG["evaluation"]["min_event_count"]
)
```

---

## Configuration Validation

No runtime validation needed - PoC uses defaults from PRD requirements (overhead <10%, capture ≥95%, ≥100 events).

---

**End of Configuration Specification**
