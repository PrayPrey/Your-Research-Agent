# System Architecture: H-M4
# Adoption Tracking Measurement Infrastructure

**Version:** 1.0  
**Date:** 2026-08-24  
**Type:** MECHANISM (SHOULD_WORK gate)  
**Prerequisites:** h-m3 (Instrumented Loader)  
**Applied:** Async batching pattern, retry queue pattern, performance profiling pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m3 instrumentation infrastructure  
**Analyzed Path:** `docs/youra_research/h-m3/code/`  
**Findings:** Extend h-m3 instrumented loader, reuse telemetry.db schema, add async queue for overhead reduction

---

## System Overview

Load-time telemetry infrastructure that captures adoption events (deprecated dataset D → successor S within 30 days) with < 10% performance overhead and ≥ 95% capture rate. Extends h-m3 instrumented loader with async event batching, retry logic, and performance tracking to enable quantitative measurement of deprecation mechanism efficacy.

---

## Module Architecture

### 1. Async Telemetry Queue (`src/async_queue.py`)

**Dependencies:** `asyncio`, `queue.Queue`, `sqlite3`

```python
import asyncio
from queue import Queue
from typing import Dict, Any, Optional
import sqlite3

class AsyncTelemetryQueue:
    def __init__(
        self,
        db_path: str,
        batch_size: int = 100,
        flush_interval: float = 5.0
    ): ...
    
    async def start(self) -> None:
        """Start background flush task"""
        ...
    
    async def stop(self) -> None:
        """Flush remaining events and stop"""
        ...
    
    def put(self, event: Dict[str, Any]) -> bool:
        """Non-blocking queue insert"""
        ...
    
    async def _background_flush(self) -> None:
        """Periodic batch write to DB"""
        ...
    
    def _write_batch(self, events: list) -> None:
        """Write batch with WAL mode"""
        ...
```

### 2. Telemetry Logger with Retry (`src/telemetry_logger.py`)

**Dependencies:** AsyncTelemetryQueue, `time`, `json`

```python
from typing import Dict, Any, Optional
import time
import json
from pathlib import Path

class TelemetryLogger:
    def __init__(
        self,
        async_queue: 'AsyncTelemetryQueue',
        fallback_dir: str = "logs/fallback"
    ): ...
    
    def log_event(
        self,
        event: Dict[str, Any],
        max_retries: int = 3
    ) -> bool:
        """Log with exponential backoff retry"""
        ...
    
    def _write_to_fallback(self, event: Dict[str, Any]) -> None:
        """Write to local JSONL file if queue fails"""
        ...
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate backoff delay: 2^attempt seconds"""
        ...
```

### 3. Performance Tracker (`src/performance_tracker.py`)

**Dependencies:** `psutil`, `time`, `statistics`

```python
import time
import psutil
from typing import Callable, Any, Dict, List
from statistics import mean, stdev

class PerformanceTracker:
    def __init__(self): ...
    
    def track_operation(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple:
        """
        Track load operation metrics.
        
        Returns:
            (result, metrics_dict)
        """
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Return:
            {
                'latency_ms': {'mean': float, 'std': float, 'p50': float, 'p95': float},
                'memory_delta_mb': {'mean': float, 'std': float},
                'cpu_percent': {'mean': float}
            }
        """
        ...
    
    def _measure_memory(self) -> int:
        """Current process memory in bytes"""
        ...
    
    def _compute_percentile(self, values: List[float], percentile: int) -> float:
        """Compute percentile without numpy"""
        ...
```

### 4. Ground Truth Generator (`src/ground_truth_generator.py`)

**Dependencies:** `json`, `datetime`

```python
from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

class GroundTruthGenerator:
    def __init__(self, output_path: str = "data/ground_truth.jsonl"): ...
    
    def log_baseline_event(self, event: Dict[str, Any]) -> None:
        """Write to deterministic log for validation"""
        ...
    
    def load_ground_truth(self) -> List[Dict[str, Any]]:
        """Load all ground truth events"""
        ...
    
    def validate_capture(
        self,
        telemetry_events: List[Dict],
        ground_truth_events: List[Dict]
    ) -> Dict[str, float]:
        """
        Return:
            {
                'precision': float,
                'recall': float,
                'f1': float
            }
        """
        ...
```

### 5. Adoption Event Tracker (`src/adoption_tracker.py`)

**Dependencies:** `sqlite3`, `datetime`

```python
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class AdoptionTracker:
    def __init__(self, db_path: str): ...
    
    def query_adoption_events(
        self,
        window_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        SQL query for D → S adoption within window.
        
        Returns:
            [{user_id, deprecated, successor, days_to_adoption}]
        """
        ...
    
    def compute_adoption_funnel(self) -> Dict[str, int]:
        """
        Return:
            {
                'deprecated_loads': int,
                'successor_loads': int,
                'adoptions_within_window': int,
                'adoption_rate': float
            }
        """
        ...
    
    def get_adoption_trail(self, user_id: str) -> List[Dict]:
        """Full event trail for single user"""
        ...
```

### 6. Performance Benchmarker (`src/benchmarker.py`)

**Dependencies:** PerformanceTracker, `datasets`, `json`

```python
from typing import Dict, List, Any
from datasets import load_dataset
import json

class PerformanceBenchmarker:
    def __init__(
        self,
        tracker: 'PerformanceTracker',
        num_runs: int = 100
    ): ...
    
    def benchmark_baseline(
        self,
        dataset_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Benchmark native load_dataset()"""
        ...
    
    def benchmark_instrumented(
        self,
        instrumented_loader: 'InstrumentedLoader',
        dataset_name: str,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Benchmark instrumented loader"""
        ...
    
    def compute_overhead(
        self,
        baseline_metrics: Dict,
        instrumented_metrics: Dict
    ) -> Dict[str, float]:
        """
        Return:
            {
                'latency_overhead_pct': float,
                'memory_overhead_mb': float,
                'cpu_overhead_pct': float
            }
        """
        ...
    
    def save_results(self, results: Dict, output_path: str) -> None:
        """Save to JSON"""
        ...
```

### 7. User Workload Simulator (`src/user_simulator.py`)

**Dependencies:** `random`, `datetime`, `uuid`

```python
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

class UserWorkloadSimulator:
    def __init__(
        self,
        num_users: int = 1000,
        days: int = 30,
        loads_per_user: int = 8,
        deprecated_encounter_rate: float = 0.4
    ): ...
    
    def generate_workload(self) -> List[Dict[str, Any]]:
        """
        Generate simulated user actions.
        
        Returns:
            [{user_id, dataset_name, timestamp, is_deprecated}]
        """
        ...
    
    def _assign_group(self, user_id: str) -> str:
        """Baseline or Instrumented group"""
        ...
    
    def _generate_user_timeline(
        self,
        user_id: str,
        start_date: datetime
    ) -> List[Dict]:
        """Generate 8 loads over 30 days (2/week)"""
        ...
```

### 8. Capture Rate Analyzer (`src/capture_analyzer.py`)

**Dependencies:** `sqlite3`, `statsmodels`

```python
import sqlite3
from typing import Dict, Tuple
from statsmodels.stats.proportion import proportion_confint

class CaptureRateAnalyzer:
    def __init__(self, db_path: str): ...
    
    def compute_capture_rate(
        self,
        expected_events: int
    ) -> Dict[str, Any]:
        """
        Return:
            {
                'captured': int,
                'expected': int,
                'rate': float,
                'ci_low': float,
                'ci_high': float
            }
        """
        ...
    
    def compute_completeness(self) -> float:
        """% events with full context (user_id, timestamp, dataset)"""
        ...
    
    def compute_delivery_latency(self) -> Dict[str, float]:
        """
        Return:
            {'p50': float, 'p95': float, 'p99': float}
        """
        ...
```

### 9. Overhead Analyzer (`src/overhead_analyzer.py`)

**Dependencies:** `json`, `scipy.stats`, `matplotlib`

```python
from typing import Dict, List, Any
import json
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

class OverheadAnalyzer:
    def __init__(
        self,
        baseline_path: str,
        instrumented_path: str
    ): ...
    
    def load_results(self) -> Tuple[Dict, Dict]:
        """Load baseline and instrumented benchmark results"""
        ...
    
    def compute_overhead_by_size(self) -> Dict[str, float]:
        """
        Return:
            {'small': 3.2, 'medium': 2.1, 'large': 1.5, 'xlarge': 0.8}
        """
        ...
    
    def statistical_test(self) -> Dict[str, Any]:
        """
        T-test for overhead significance.
        
        Return:
            {'t_stat': float, 'p_value': float, 'significant': bool}
        """
        ...
    
    def visualize_overhead(self, output_path: str) -> None:
        """Bar chart with 10% threshold line"""
        ...
```

### 10. Extended Instrumented Loader (`src/instrumented_loader_extended.py`)

**Dependencies:** h-m3 InstrumentedLoader, TelemetryLogger, PerformanceTracker

```python
import sys
sys.path.insert(0, '../../h-m3/code')
from src.migration_planner import MigrationPlanner
from typing import Dict, Any, Tuple
from datasets import Dataset

class ExtendedInstrumentedLoader:
    def __init__(
        self,
        telemetry_logger: 'TelemetryLogger',
        migration_planner: 'MigrationPlanner',
        performance_tracker: 'PerformanceTracker',
        deprecation_registry: Dict[str, str]
    ): ...
    
    def load_dataset_with_tracking(
        self,
        dataset_name: str,
        user_id: str,
        **kwargs
    ) -> Tuple[Dataset, Dict[str, Any]]:
        """
        Load with h-m3 deprecation check + h-m4 performance tracking.
        
        Flow:
        1. Start performance tracking
        2. Check deprecation (reuse h-m3 logic)
        3. Log event (async via h-m4 queue)
        4. Load dataset
        5. Stop tracking, return result + metrics
        """
        ...
    
    def _assign_user_group(self, user_id: str) -> str:
        """Reuse h-m3 hash-based assignment"""
        ...
    
    def _log_load_event(
        self,
        user_id: str,
        dataset_name: str,
        deprecated: bool,
        successor: Optional[str],
        group: str
    ) -> None:
        """Async log via TelemetryLogger"""
        ...
```

### 11. Main Experiment Runner (`main.py`)

**Dependencies:** All modules above

```python
import asyncio
import json
from pathlib import Path
from src.async_queue import AsyncTelemetryQueue
from src.telemetry_logger import TelemetryLogger
from src.performance_tracker import PerformanceTracker
from src.benchmarker import PerformanceBenchmarker
from src.user_simulator import UserWorkloadSimulator
from src.capture_analyzer import CaptureRateAnalyzer
from src.overhead_analyzer import OverheadAnalyzer
from src.adoption_tracker import AdoptionTracker
from src.ground_truth_generator import GroundTruthGenerator
from src.instrumented_loader_extended import ExtendedInstrumentedLoader

async def main():
    """Run h-m4 experiment"""
    # Phase 1: Baseline benchmarks
    tracker = PerformanceTracker()
    benchmarker = PerformanceBenchmarker(tracker, num_runs=100)
    
    baseline_results = {}
    for dataset_size in ['small', 'medium', 'large', 'xlarge']:
        dataset_name = DATASET_MAP[dataset_size]
        baseline_results[dataset_size] = benchmarker.benchmark_baseline(dataset_name)
    
    benchmarker.save_results(baseline_results, 'baseline_performance.json')
    
    # Phase 2: Instrumented benchmarks
    queue = AsyncTelemetryQueue('telemetry.db', batch_size=100, flush_interval=5.0)
    await queue.start()
    
    telemetry = TelemetryLogger(queue, fallback_dir='logs/fallback')
    loader = ExtendedInstrumentedLoader(telemetry, None, tracker, DEPRECATION_REGISTRY)
    
    instrumented_results = {}
    for dataset_size in ['small', 'medium', 'large', 'xlarge']:
        dataset_name = DATASET_MAP[dataset_size]
        instrumented_results[dataset_size] = benchmarker.benchmark_instrumented(
            loader, dataset_name, user_id='benchmark_user'
        )
    
    benchmarker.save_results(instrumented_results, 'instrumented_performance.json')
    
    # Phase 3: User simulation
    simulator = UserWorkloadSimulator(num_users=1000, days=30)
    workload = simulator.generate_workload()
    
    gt_generator = GroundTruthGenerator('data/ground_truth.jsonl')
    
    for action in workload:
        if action['group'] == 'baseline':
            gt_generator.log_baseline_event(action)
        else:
            loader.load_dataset_with_tracking(
                action['dataset_name'],
                action['user_id']
            )
    
    await queue.stop()
    
    # Phase 4: Analysis
    overhead_analyzer = OverheadAnalyzer(
        'baseline_performance.json',
        'instrumented_performance.json'
    )
    overhead_results = overhead_analyzer.compute_overhead_by_size()
    overhead_analyzer.visualize_overhead('figures/overhead_by_size.png')
    
    capture_analyzer = CaptureRateAnalyzer('telemetry.db')
    capture_results = capture_analyzer.compute_capture_rate(expected_events=4000)
    
    adoption_tracker = AdoptionTracker('telemetry.db')
    adoption_funnel = adoption_tracker.compute_adoption_funnel()
    
    # Phase 5: Gate evaluation
    gate_pass = (
        all(v < 10.0 for v in overhead_results.values()) and
        capture_results['ci_low'] >= 0.95 and
        adoption_funnel['adoption_rate'] >= 0.95
    )
    
    print(f"Gate Result: {'PASS' if gate_pass else 'FAIL'}")
    
    return {
        'overhead': overhead_results,
        'capture_rate': capture_results,
        'adoption_funnel': adoption_funnel,
        'gate_result': 'PASS' if gate_pass else 'FAIL'
    }

if __name__ == '__main__':
    asyncio.run(main())
```

---

## File Structure

```
h-m4/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── async_queue.py
│   │   ├── telemetry_logger.py
│   │   ├── performance_tracker.py
│   │   ├── ground_truth_generator.py
│   │   ├── adoption_tracker.py
│   │   ├── benchmarker.py
│   │   ├── user_simulator.py
│   │   ├── capture_analyzer.py
│   │   ├── overhead_analyzer.py
│   │   └── instrumented_loader_extended.py
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── data/
│   ├── ground_truth.jsonl          # Baseline event log
│   └── telemetry.db                # SQLite events
├── logs/
│   └── fallback/                   # Retry failure logs
├── figures/
│   ├── overhead_by_size.png
│   ├── capture_rate_over_time.png
│   └── adoption_funnel.png
└── results/
    ├── baseline_performance.json
    ├── instrumented_performance.json
    └── gate_evaluation.json
```

---

## External Dependencies (h-m3 Integration)

### Module Paths (From h-m3 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MigrationPlanner | `sys.path + from src.migration_planner import MigrationPlanner` | `h-m3/code/src/migration_planner.py` |
| UserGroupAssigner | `sys.path + from src.user_group_assigner import UserGroupAssigner` | `h-m3/code/src/user_group_assigner.py` |

**Verified from:** `docs/youra_research/h-m3/code/` (actual implementation)

**Note:** Use `sys.path.insert()` to access h-m3 modules, as shown in main.py pattern.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M4-1 | Async Queue | Implement async batching with background flush, WAL mode SQLite | 11 | 3+2+4+2 |
| M4-2 | Telemetry Logger | Retry logic with exponential backoff, fallback to local file | 9 | 2+2+3+2 |
| M4-3 | Performance Tracking | Track latency/memory/CPU with psutil, compute percentiles | 10 | 3+2+3+2 |
| M4-4 | Baseline Benchmarks | Run 100 native load_dataset() for 4 dataset sizes | 8 | 2+2+2+2 |
| M4-5 | Instrumented Benchmarks | Run 100 instrumented loads with telemetry enabled | 9 | 2+2+3+2 |
| M4-6 | User Simulation | Generate 1000 users × 8 loads over 30 days, deprecation encounters | 10 | 3+2+3+2 |
| M4-7 | Ground Truth Validation | Deterministic log for baseline, precision/recall computation | 8 | 2+2+2+2 |
| M4-8 | Adoption Tracking | SQL query for D → S within 30 days, funnel visualization | 10 | 3+2+3+2 |
| M4-9 | Capture Rate Analysis | Wilson score CI, delivery latency, completeness metrics | 11 | 3+2+4+2 |
| M4-10 | Overhead Analysis | Statistical test, visualization with threshold line | 9 | 2+2+3+2 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): []
- Medium (9-13): [M4-1, M4-3, M4-5, M4-6, M4-8, M4-9, M4-10]
- Low (4-8): [M4-2, M4-4, M4-7]

**Total:** 10 Epic tasks (SHOULD_WORK scope)

---

## Data Flow

```
PHASE 1: BASELINE BENCHMARKS
1. Native load_dataset() × 100 runs
   └─> PerformanceTracker measures latency/memory
   └─> Save to baseline_performance.json

PHASE 2: INSTRUMENTED BENCHMARKS
1. ExtendedInstrumentedLoader × 100 runs
   └─> PerformanceTracker measures overhead
   └─> TelemetryLogger logs to AsyncQueue
   └─> AsyncQueue batches to telemetry.db
   └─> Save to instrumented_performance.json

PHASE 3: USER SIMULATION
1. UserWorkloadSimulator generates 4000 actions
   └─> Baseline group → GroundTruthGenerator → ground_truth.jsonl
   └─> Instrumented group → ExtendedInstrumentedLoader → telemetry.db
2. Async background flush every 5s

PHASE 4: ANALYSIS
1. OverheadAnalyzer
   └─> Load both JSON files
   └─> Compute overhead % per dataset size
   └─> T-test for significance
   └─> Visualize with 10% threshold
2. CaptureRateAnalyzer
   └─> Query telemetry.db
   └─> Compute capture rate with Wilson CI
3. AdoptionTracker
   └─> SQL join for D → S events within 30 days
   └─> Compute adoption funnel

PHASE 5: GATE EVALUATION
1. Check overhead < 10% for all sizes
2. Check CI lower bound ≥ 95%
3. Check adoption completeness ≥ 95%
4. Output: PASS/FAIL
```

---

## Success Criteria Mapping

| Gate Metric | Target | Implementation | Validation |
|-------------|--------|----------------|------------|
| Performance overhead | < 10% | Async queue amortizes cost | `OverheadAnalyzer.compute_overhead_by_size()` |
| Capture rate | ≥ 95% | Retry + fallback | `CaptureRateAnalyzer.compute_capture_rate()` with Wilson CI |
| Adoption completeness | ≥ 95% | SQL trail validation | `GroundTruthGenerator.validate_capture()` |
| Memory overhead | < 50 MB | Track delta via psutil | `PerformanceTracker.get_metrics()` |
| Delivery latency p95 | < 5s | Async batch flush | `CaptureRateAnalyzer.compute_delivery_latency()` |

---

## Dependencies

**External:**
- `aiofiles==24.1.0` (async file I/O)
- `psutil==6.1.0` (process metrics)
- `pytest-benchmark==4.0.0` (benchmarking)
- `scipy==1.14.1` (statistical tests)
- `statsmodels==0.14.4` (confidence intervals)
- `matplotlib==3.9.2` (visualization)
- `datasets` (HuggingFace)
- Python 3.8+ stdlib: `asyncio`, `queue`, `sqlite3`, `json`, `time`, `statistics`, `datetime`, `uuid`, `random`

**Internal:**
- h-m3: `MigrationPlanner`, `UserGroupAssigner` (via sys.path)

---

## Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Event queue insert | < 1ms | Non-blocking Queue.put() |
| Batch flush | < 100ms | SQLite WAL write |
| Load overhead | < 10% | Instrumented vs baseline latency |
| Memory overhead | < 50 MB | Peak RSS delta |
| Capture rate | ≥ 95% | Events in DB / expected events |

---

## Privacy Compliance

**Inherited from h-m3:**
- User IDs hashed (SHA256, 16-char truncation)
- No PII in telemetry logs
- Opt-in/opt-out support

**Additional h-m4 measures:**
- No dataset content captured (only names)
- Fallback logs anonymized
- Simulation uses synthetic user IDs

---

## Validation Checklist

- [ ] All 10 modules implement interface signatures
- [ ] Async queue < 1ms insert latency
- [ ] Batch flush < 100ms
- [ ] Overhead < 10% for all dataset sizes
- [ ] Capture rate ≥ 95% with CI lower bound
- [ ] Adoption completeness ≥ 95%
- [ ] Memory overhead < 50 MB
- [ ] Delivery latency p95 < 5s
- [ ] Ground truth validation precision/recall computed
- [ ] Statistical tests (t-test, Wilson CI) implemented

---

**End of Architecture Specification**
