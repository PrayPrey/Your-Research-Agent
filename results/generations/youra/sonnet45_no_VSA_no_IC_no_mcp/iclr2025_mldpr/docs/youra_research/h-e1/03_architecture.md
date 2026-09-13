# System Architecture: H-E1
# Load-Time Instrumentation PoC

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** EXISTENCE (Infrastructure PoC)  
**Applied:** Decorator-based instrumentation pattern, telemetry logging pattern, benchmark harness pattern

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** Green-field implementation - no existing codebase analyzed  
**Analyzed Path:** N/A  
**Findings:** New infrastructure implementation from scratch

---

## System Overview

Minimal instrumentation system wrapping HuggingFace `load_dataset()` to measure performance overhead and telemetry capture rate. Four core modules: instrumented loader, telemetry backend, benchmark harness, simulation generator.

---

## Module Architecture

### 1. Instrumented Loader (`src/loader.py`)

**Dependencies:** stdlib `time`, `functools`, `datasets.load_dataset`

```python
from typing import Tuple, Dict, Any
from datasets import Dataset

def instrumented_load_dataset(
    dataset_name: str,
    telemetry: 'TelemetryLogger',
    **kwargs
) -> Tuple[Dataset, Dict[str, Any]]:
    """
    Wrapper around load_dataset() measuring overhead.
    
    Returns:
        (dataset, metadata) where metadata = {
            'baseline_ms': float,
            'telemetry_ms': float,
            'overhead_pct': float,
            'telemetry_success': bool
        }
    """
    ...
```

### 2. Telemetry Backend (`src/telemetry.py`)

**Dependencies:** stdlib `hashlib`, `sqlite3`, `json`, `time`

```python
from typing import Dict, Optional

class TelemetryLogger:
    def __init__(self, db_path: str = "telemetry.db", opt_in: bool = True): ...
    
    def log_event(self, event: Dict[str, Any]) -> bool:
        """
        Log event with hashed user ID.
        
        Args:
            event: {dataset, action, timestamp, user_id}
        
        Returns:
            Success status
        """
        ...
    
    def hash_user_id(self, user_id: str) -> str:
        """SHA256 truncated to 16 chars"""
        ...
    
    def get_capture_rate(self) -> float:
        """Calculate successful_logs / total_attempts"""
        ...
```

### 3. Benchmark Harness (`src/benchmark.py`)

**Dependencies:** Loader, Telemetry, stdlib `statistics`, `csv`

```python
from typing import List, Dict
import pandas as pd

class BenchmarkHarness:
    def __init__(self, datasets: List[str], runs_per_dataset: int = 10): ...
    
    def run_benchmarks(self) -> pd.DataFrame:
        """
        Run benchmark suite.
        
        Returns:
            DataFrame with columns: [dataset, run, baseline_ms, 
                                    instrumented_ms, overhead_pct, 
                                    telemetry_success]
        """
        ...
    
    def aggregate_results(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Calculate mean/std/min/max per dataset.
        
        Returns:
            {dataset: {mean: X, std: Y, min: Z, max: W}}
        """
        ...
    
    def save_results(self, df: pd.DataFrame, path: str) -> None:
        """Write CSV to path"""
        ...
```

### 4. Simulation Generator (`src/simulate.py`)

**Dependencies:** Telemetry, stdlib `random`, `datetime`, `json`

```python
from datetime import datetime, timedelta
from typing import List, Dict

class SimulationGenerator:
    def __init__(
        self,
        telemetry: TelemetryLogger,
        start_date: datetime,
        duration_months: int = 6
    ): ...
    
    def generate_events(self, event_count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate deprecation events over 6-month period.
        
        30% adopt successor, 70% ignore.
        
        Returns:
            List of events: [{dataset, action, timestamp, user_hash, successor}]
        """
        ...
    
    def save_simulation(self, events: List[Dict], path: str) -> None:
        """Write JSON log to path"""
        ...
```

### 5. Evaluator (`src/evaluate.py`)

**Dependencies:** Benchmark results, simulation log, stdlib `json`

```python
from typing import Dict, Tuple

class Evaluator:
    def __init__(self, benchmark_csv: str, simulation_json: str): ...
    
    def check_overhead(self) -> Tuple[bool, float]:
        """
        Verify overhead <10% for all datasets.
        
        Returns:
            (pass, max_overhead_pct)
        """
        ...
    
    def check_capture_rate(self, telemetry: TelemetryLogger) -> Tuple[bool, float]:
        """
        Verify capture rate ≥95%.
        
        Returns:
            (pass, capture_rate_pct)
        """
        ...
    
    def check_event_count(self) -> Tuple[bool, int]:
        """
        Verify ≥100 events tracked.
        
        Returns:
            (pass, event_count)
        """
        ...
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Full evaluation report.
        
        Returns:
            {
                'overhead_pass': bool,
                'capture_rate_pass': bool,
                'event_count_pass': bool,
                'gate_status': 'PASS'|'FAIL'
            }
        """
        ...
```

### 6. Visualization (`src/visualize.py`)

**Dependencies:** Evaluator, `matplotlib`, benchmark/simulation data

```python
import matplotlib.pyplot as plt
from pathlib import Path

class Visualizer:
    def __init__(self, figures_dir: Path): ...
    
    def plot_gate_metrics(self, report: Dict) -> None:
        """Bar chart: target vs actual for 3 metrics"""
        ...
    
    def plot_load_time_comparison(self, df: pd.DataFrame) -> None:
        """Side-by-side bars: baseline vs instrumented"""
        ...
    
    def plot_overhead_distribution(self, df: pd.DataFrame) -> None:
        """Box plot of overhead % across runs"""
        ...
    
    def plot_capture_rate(self, events: List[Dict]) -> None:
        """Cumulative capture rate over 6 months"""
        ...
```

### 7. Main Entry Point (`main.py`)

**Dependencies:** All modules above

```python
from pathlib import Path
from src.loader import instrumented_load_dataset
from src.telemetry import TelemetryLogger
from src.benchmark import BenchmarkHarness
from src.simulate import SimulationGenerator
from src.evaluate import Evaluator
from src.visualize import Visualizer

def main():
    """Run full PoC pipeline"""
    # 1. Setup
    telemetry = TelemetryLogger("telemetry.db")
    datasets = ["cifar10", "imdb", "wikitext-103"]
    
    # 2. Benchmark
    harness = BenchmarkHarness(datasets, runs_per_dataset=10)
    results_df = harness.run_benchmarks()
    harness.save_results(results_df, "benchmark_results.csv")
    
    # 3. Simulate
    sim = SimulationGenerator(telemetry)
    events = sim.generate_events(event_count=100)
    sim.save_simulation(events, "simulation.json")
    
    # 4. Evaluate
    evaluator = Evaluator("benchmark_results.csv", "simulation.json")
    report = evaluator.generate_report()
    
    # 5. Visualize
    viz = Visualizer(Path("figures"))
    viz.plot_gate_metrics(report)
    viz.plot_load_time_comparison(results_df)
    viz.plot_overhead_distribution(results_df)
    viz.plot_capture_rate(events)
    
    print(f"Gate Status: {report['gate_status']}")

if __name__ == "__main__":
    main()
```

---

## File Structure

```
h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── loader.py          # Instrumented dataset loader
│   │   ├── telemetry.py       # Privacy-preserving logger
│   │   ├── benchmark.py       # Benchmark harness
│   │   ├── simulate.py        # 6-month event generator
│   │   ├── evaluate.py        # Gate metrics validator
│   │   └── visualize.py       # Figure generation
│   ├── main.py                # Entry point
│   ├── requirements.txt       # datasets, pandas, matplotlib
│   └── README.md              # Setup/run instructions
├── data/                      # HuggingFace cache (auto-created)
├── figures/                   # Generated plots
├── benchmark_results.csv      # Performance data
├── simulation.json            # 6-month event log
└── telemetry.db              # SQLite telemetry store
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Core Instrumentation | Implement `loader.py` (wrapper) + `telemetry.py` (SQLite logger with SHA256 hashing) | 11 | 3+2+4+2 |
| E-2 | Benchmark Infrastructure | Implement `benchmark.py` (3 datasets × 10 runs, CSV output, aggregation) | 9 | 2+2+3+2 |
| E-3 | Simulation Generator | Implement `simulate.py` (6-month event log, 30/70 adoption split, JSON output) | 7 | 2+1+2+2 |
| E-4 | Evaluation Pipeline | Implement `evaluate.py` (3 gate checks) + `visualize.py` (4 plots) + `main.py` orchestration | 13 | 3+2+5+3 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [E-1, E-2, E-4]
- Low (4-8): [E-3]

**Total:** 4 Epic tasks (EXISTENCE PoC scope)

---

## Task Decomposition

### E-1: Core Instrumentation (Complexity: 11)

**Files:** `src/loader.py`, `src/telemetry.py`

**Subtasks:**
1. `instrumented_load_dataset()` wrapper with time measurement (loader.py)
2. `TelemetryLogger` class with SQLite backend (telemetry.py)
3. SHA256 user ID hashing with 16-char truncation (telemetry.py)
4. Event schema: `{user_hash, dataset, action, timestamp}` (telemetry.py)

**Acceptance:**
- Wrapper runs without error on cifar10
- Telemetry DB created with correct schema
- No plaintext user IDs in DB

### E-2: Benchmark Infrastructure (Complexity: 9)

**Files:** `src/benchmark.py`

**Subtasks:**
1. `BenchmarkHarness` class loading 3 datasets
2. 10-run loop per dataset with time tracking
3. Results aggregation (mean/std/min/max)
4. CSV export with schema: `[dataset, run, baseline_ms, instrumented_ms, overhead_pct, telemetry_success]`

**Acceptance:**
- 30 total runs complete (3 datasets × 10)
- CSV contains 30 rows with valid numeric data
- Aggregation calculates correct statistics

### E-3: Simulation Generator (Complexity: 7)

**Files:** `src/simulate.py`

**Subtasks:**
1. `SimulationGenerator` class with datetime logic
2. Event generation with 30% successor adoption rate
3. JSON export with event list
4. 6-month timestamp distribution

**Acceptance:**
- ≥100 events generated
- 30% have `action="adopt_successor"`
- Timestamps span 6-month period
- JSON schema matches telemetry schema

### E-4: Evaluation Pipeline (Complexity: 13)

**Files:** `src/evaluate.py`, `src/visualize.py`, `main.py`

**Subtasks:**
1. `Evaluator` class with 3 gate checks (evaluate.py)
2. `Visualizer` class with 4 plot functions (visualize.py)
3. `main()` orchestration pipeline (main.py)
4. Gate report generation with PASS/FAIL status (evaluate.py)

**Acceptance:**
- All 3 gate checks execute without error
- 4 figures saved to `figures/` directory
- `main.py` completes full pipeline
- Report shows gate status for each metric

---

## Data Flow

```
1. Benchmark Phase
   └─> BenchmarkHarness
       └─> instrumented_load_dataset() [calls HF datasets.load_dataset()]
           └─> TelemetryLogger.log_event()
       └─> CSV output

2. Simulation Phase
   └─> SimulationGenerator
       └─> generate_events() [synthetic 6-month log]
       └─> JSON output

3. Evaluation Phase
   └─> Evaluator
       └─> check_overhead() [reads CSV]
       └─> check_capture_rate() [queries SQLite]
       └─> check_event_count() [reads JSON]
       └─> Report output

4. Visualization Phase
   └─> Visualizer
       └─> plot_* functions [reads CSV + JSON + Report]
       └─> PNG figures
```

---

## Success Criteria Mapping

| Gate Metric | Target | Implementation | Validation |
|-------------|--------|----------------|------------|
| Overhead | <10% | `instrumented_load_dataset()` time delta | `Evaluator.check_overhead()` |
| Capture Rate | ≥95% | `TelemetryLogger.get_capture_rate()` | `Evaluator.check_capture_rate()` |
| Event Count | ≥100 | `SimulationGenerator.generate_events()` | `Evaluator.check_event_count()` |

---

## Dependencies

**External:**
- `datasets` (HuggingFace)
- `pandas` (CSV handling)
- `matplotlib` (visualization)
- Python 3.8+ stdlib: `time`, `hashlib`, `sqlite3`, `json`, `statistics`, `random`, `datetime`

**Internal:**
- None (green-field foundation hypothesis)

---

## Privacy Compliance

**User ID Hashing:**
```python
# src/telemetry.py
def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]
```

**No Dataset Content Capture:**
- Only dataset name logged, no samples/features
- No reverse-engineering path from hash to user

---

## Performance Targets

| Dataset Size | Baseline Load (ms) | Max Instrumented Overhead (ms) | Max Overhead % |
|--------------|-------------------|-------------------------------|----------------|
| Small (cifar10) | ~50 | ~5 | <10% |
| Medium (imdb) | ~500 | ~50 | <10% |
| Large (wikitext-103) | ~5000 | ~500 | <10% |

---

## Validation Checklist

- [ ] All 4 modules implement interface signatures
- [ ] `main.py` orchestrates full pipeline
- [ ] 30 benchmark runs complete (3 datasets × 10)
- [ ] ≥100 simulation events generated
- [ ] 3 gate checks pass (overhead, capture rate, event count)
- [ ] 4 figures generated
- [ ] No plaintext user IDs in telemetry DB
- [ ] Total implementation <500 LOC

---

**End of Architecture Specification**
