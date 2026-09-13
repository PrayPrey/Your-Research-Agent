# Logic Specification: H-E1
# Load-Time Instrumentation PoC

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** EXISTENCE (Infrastructure PoC)  
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** Green-field  
**Status:** Green-field implementation - no existing codebase analyzed  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Applied Patterns

**Applied:** Decorator-based instrumentation, SQLite telemetry backend, benchmark harness pattern (stdlib-based timing and statistics)

---

## E-1: Core Instrumentation [Complexity: 11, Budget: 1]

### API Signatures

```python
# src/loader.py
from typing import Tuple, Dict, Any
from datasets import Dataset

def instrumented_load_dataset(
    dataset_name: str,
    telemetry: 'TelemetryLogger',
    split: str = "train",
    **kwargs
) -> Tuple[Dataset, Dict[str, Any]]:
    """
    Wrap load_dataset() with timing and telemetry.
    
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

```python
# src/telemetry.py
import hashlib
import sqlite3
from typing import Dict, Any, Optional

class TelemetryLogger:
    def __init__(self, db_path: str = "telemetry.db", opt_in: bool = True):
        """Initialize SQLite backend with schema."""
        ...
    
    def log_event(self, event: Dict[str, Any]) -> bool:
        """
        Log event with hashed user ID.
        
        Args:
            event: {user_id, dataset, action, timestamp}
        
        Returns:
            Success status (True if INSERT successful)
        """
        ...
    
    def hash_user_id(self, user_id: str) -> str:
        """SHA256 hash truncated to 16 chars."""
        ...
    
    def get_capture_rate(self) -> float:
        """Calculate successful_logs / total_attempts."""
        ...
```

### Pseudo-code

```
# instrumented_load_dataset()
1. t0 = time()
2. dataset = load_dataset(dataset_name, split, **kwargs)  # baseline
3. baseline_ms = (time() - t0) * 1000

4. t1 = time()
5. success = telemetry.log_event({user_id, dataset_name, "load", timestamp})
6. telemetry_ms = (time() - t1) * 1000

7. overhead_pct = (telemetry_ms / baseline_ms) * 100 if baseline_ms > 0 else 0
8. return (dataset, {baseline_ms, telemetry_ms, overhead_pct, success})

# TelemetryLogger.log_event()
1. user_hash = hash_user_id(event['user_id'])
2. try:
3.   INSERT INTO events (user_hash, dataset, action, timestamp) VALUES (...)
4.   return True
5. except:
6.   return False
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Instrumented loader + telemetry backend | Wrapper with time.perf_counter(), SQLite schema, SHA256 hashing |

---

## E-2: Benchmark Infrastructure [Complexity: 9, Budget: 1]

### API Signatures

```python
# src/benchmark.py
from typing import List, Dict, Any
import pandas as pd
from src.loader import instrumented_load_dataset
from src.telemetry import TelemetryLogger

class BenchmarkHarness:
    def __init__(
        self, 
        datasets: List[str],
        runs_per_dataset: int = 10,
        telemetry: Optional[TelemetryLogger] = None
    ):
        """Initialize harness with dataset list."""
        ...
    
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
        Calculate statistics per dataset.
        
        Returns:
            {dataset_name: {mean: X, std: Y, min: Z, max: W}}
        """
        ...
    
    def save_results(self, df: pd.DataFrame, path: str) -> None:
        """Write CSV to path."""
        ...
```

### Pseudo-code

```
# run_benchmarks()
1. results = []
2. for dataset in datasets:
3.   for run in range(runs_per_dataset):
4.     (ds, metadata) = instrumented_load_dataset(dataset, telemetry)
5.     results.append({
         dataset: dataset,
         run: run,
         baseline_ms: metadata['baseline_ms'],
         instrumented_ms: metadata['telemetry_ms'],
         overhead_pct: metadata['overhead_pct'],
         telemetry_success: metadata['telemetry_success']
       })
6. return pd.DataFrame(results)

# aggregate_results()
1. grouped = df.groupby('dataset')['overhead_pct']
2. return {ds: {mean, std, min, max} for ds in grouped}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Benchmark harness | Loop over 3 datasets × 10 runs, DataFrame output, pandas.describe() aggregation |

---

## E-3: Simulation Generator [Complexity: 7, Budget: 1]

### API Signatures

```python
# src/simulate.py
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from src.telemetry import TelemetryLogger

class SimulationGenerator:
    def __init__(
        self,
        telemetry: TelemetryLogger,
        start_date: datetime,
        duration_months: int = 6
    ):
        """Initialize 6-month simulation window."""
        ...
    
    def generate_events(
        self, 
        event_count: int = 100,
        adoption_rate: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Generate deprecation events over 6-month period.
        
        Args:
            event_count: Total events to generate
            adoption_rate: Fraction adopting successor (default 30%)
        
        Returns:
            List of events: [{user_hash, dataset, action, timestamp, successor}]
        """
        ...
    
    def save_simulation(self, events: List[Dict], path: str) -> None:
        """Write JSON log to path."""
        ...
```

### Pseudo-code

```
# generate_events()
1. events = []
2. for i in range(event_count):
3.   timestamp = start_date + random_delta(0, duration_months)
4.   action = "adopt_successor" if random() < adoption_rate else "load_deprecated"
5.   events.append({
       user_hash: random_hash(),
       dataset: random_choice(["cifar10", "imdb", "wikitext"]),
       action: action,
       timestamp: timestamp.isoformat(),
       successor: "cifar100" if action == "adopt_successor" else None
     })
6. return events
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Event generator | datetime.timedelta math, random.choices for 30/70 split, JSON serialization |

---

## E-4: Evaluation Pipeline [Complexity: 13, Budget: 1]

### API Signatures

```python
# src/evaluate.py
from typing import Dict, Tuple, Any
import pandas as pd
import json

class Evaluator:
    def __init__(self, benchmark_csv: str, simulation_json: str):
        """Load benchmark and simulation data."""
        ...
    
    def check_overhead(self) -> Tuple[bool, float]:
        """
        Verify overhead <10% for all datasets.
        
        Returns:
            (pass, max_overhead_pct)
        """
        ...
    
    def check_capture_rate(self, telemetry: 'TelemetryLogger') -> Tuple[bool, float]:
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
                'overhead_max': float,
                'capture_rate_pass': bool,
                'capture_rate': float,
                'event_count_pass': bool,
                'event_count': int,
                'gate_status': 'PASS'|'FAIL'
            }
        """
        ...
```

```python
# src/visualize.py
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
from typing import List, Dict

class Visualizer:
    def __init__(self, figures_dir: Path):
        """Initialize output directory for figures."""
        ...
    
    def plot_gate_metrics(self, report: Dict) -> None:
        """Bar chart: target vs actual for 3 metrics."""
        ...
    
    def plot_load_time_comparison(self, df: pd.DataFrame) -> None:
        """Side-by-side bars: baseline vs instrumented."""
        ...
    
    def plot_overhead_distribution(self, df: pd.DataFrame) -> None:
        """Box plot of overhead % across runs."""
        ...
    
    def plot_capture_rate(self, events: List[Dict]) -> None:
        """Cumulative capture rate over 6 months."""
        ...
```

```python
# main.py
from pathlib import Path
from src.loader import instrumented_load_dataset
from src.telemetry import TelemetryLogger
from src.benchmark import BenchmarkHarness
from src.simulate import SimulationGenerator
from src.evaluate import Evaluator
from src.visualize import Visualizer

def main():
    """Run full PoC pipeline: benchmark → simulate → evaluate → visualize."""
    # Setup
    telemetry = TelemetryLogger("telemetry.db")
    datasets = ["cifar10", "imdb", "wikitext-103"]
    
    # Benchmark
    harness = BenchmarkHarness(datasets, runs_per_dataset=10, telemetry=telemetry)
    results_df = harness.run_benchmarks()
    harness.save_results(results_df, "benchmark_results.csv")
    
    # Simulate
    sim = SimulationGenerator(telemetry, start_date=datetime.now())
    events = sim.generate_events(event_count=100)
    sim.save_simulation(events, "simulation.json")
    
    # Evaluate
    evaluator = Evaluator("benchmark_results.csv", "simulation.json")
    report = evaluator.generate_report()
    
    # Visualize
    viz = Visualizer(Path("figures"))
    viz.plot_gate_metrics(report)
    viz.plot_load_time_comparison(results_df)
    viz.plot_overhead_distribution(results_df)
    viz.plot_capture_rate(events)
    
    print(f"Gate Status: {report['gate_status']}")

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
# Evaluator.check_overhead()
1. df = pd.read_csv(benchmark_csv)
2. max_overhead = df['overhead_pct'].max()
3. return (max_overhead < 10.0, max_overhead)

# Evaluator.check_capture_rate()
1. capture_rate = telemetry.get_capture_rate()
2. return (capture_rate >= 0.95, capture_rate)

# Evaluator.check_event_count()
1. events = json.load(simulation_json)
2. count = len(events)
3. return (count >= 100, count)

# Visualizer.plot_gate_metrics()
1. fig, ax = plt.subplots()
2. metrics = ['Overhead', 'Capture Rate', 'Event Count']
3. targets = [10, 95, 100]
4. actuals = [report['overhead_max'], report['capture_rate']*100, report['event_count']]
5. ax.bar(x=metrics, height=targets, label='Target')
6. ax.bar(x=metrics, height=actuals, label='Actual', alpha=0.7)
7. plt.savefig(figures_dir / "gate_metrics.png")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Evaluation + visualization + orchestration | 3 gate checks, 4 matplotlib plots, main.py pipeline |

---

## Data Schemas

### Telemetry Event (SQLite)

| Column | Type | Description |
|--------|------|-------------|
| user_hash | TEXT | SHA256[:16] |
| dataset | TEXT | Dataset name |
| action | TEXT | "load", "adopt_successor" |
| timestamp | TEXT | ISO8601 format |

### Benchmark Results (CSV)

| Column | Type | Description |
|--------|------|-------------|
| dataset | str | Dataset name |
| run | int | Run number (0-9) |
| baseline_ms | float | Unmodified load time |
| instrumented_ms | float | Telemetry overhead |
| overhead_pct | float | (instrumented/baseline - 1) × 100 |
| telemetry_success | bool | Log insertion status |

### Simulation Events (JSON)

```json
[
  {
    "user_hash": "a1b2c3d4e5f6g7h8",
    "dataset": "cifar10",
    "action": "adopt_successor",
    "timestamp": "2026-09-15T14:23:45",
    "successor": "cifar100"
  }
]
```

---

## Error Handling

**Critical Paths:**
- `instrumented_load_dataset()`: Catch HuggingFace API errors, return empty metadata on failure
- `TelemetryLogger.log_event()`: SQLite errors return False (graceful degradation)
- `BenchmarkHarness.run_benchmarks()`: Skip failed dataset loads, log to stderr
- `Evaluator.generate_report()`: All gate checks must complete (no short-circuit)

**Pattern:**
```python
try:
    result = operation()
except Exception as e:
    logger.error(f"Failed: {e}")
    return fallback_value  # Empty dict, False, None
```

---

## Performance Notes

**Timing:** Use `time.perf_counter()` (nanosecond precision) not `time.time()` (system clock)

**SQLite:** Single-threaded writes (no WAL mode needed for PoC), `PRAGMA synchronous=NORMAL` for speed

**Memory:** Load datasets sequentially (no batching), rely on HuggingFace cache to avoid re-download

---

## Validation Checklist

- [ ] All type hints present (mypy-compatible)
- [ ] Error paths return graceful fallbacks
- [ ] No plaintext user IDs in code/DB
- [ ] CSV/JSON schemas match PRD
- [ ] Gate thresholds (<10%, ≥95%, ≥100) implemented
- [ ] 4 subtasks allocated (1 per Epic)

---

**End of Logic Specification**
