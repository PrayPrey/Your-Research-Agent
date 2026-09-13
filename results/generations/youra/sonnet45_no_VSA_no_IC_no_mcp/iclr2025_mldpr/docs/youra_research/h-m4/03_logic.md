# Logic Design: Adoption Tracking Measurement Infrastructure (h-m4)

**Hypothesis ID:** h-m4  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-24  
**Author:** Phase 3 Logic Agent

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m3 code  
**Analyzed Path:** `docs/youra_research/h-m3/code/src/`  
**Relevant Symbols:**
- `MigrationPlanner.generate_plan(deprecated_id: str, successor_id: str) -> Dict`
- `UserGroupAssigner.assign_group(user_id: str, complexity: str = None) -> str`
- `UserGroupAssigner.get_complexity_stratum(impact_summary: Dict) -> str`

**Integration:** Extend h-m3 loader with async telemetry queue and performance tracking.

---

## External Dependencies API (h-m3)

Signatures verified from actual code at `docs/youra_research/h-m3/code/src/`:

```python
# From: migration_planner.py
class MigrationPlanner:
    def __init__(self, graph: nx.DiGraph, analyzer: ImpactAnalyzer, detector: SchemaCompatibilityDetector):
        ...
    
    def generate_plan(self, deprecated_id: str, successor_id: str) -> Dict[str, Any]:
        """Generate migration plan. Returns: plan dict with impact_radius, compatibility, breaking_changes, migration_steps, adapters, verification_checklist."""
        ...

def display_migration_plan(plan: Dict[str, Any]):
    """Print migration plan to console."""
    ...

# From: user_group_assigner.py
class UserGroupAssigner:
    def __init__(self, seed: int = 42):
        ...
    
    def assign_group(self, user_id: str, complexity: str = None) -> str:
        """Assign user to group. Returns: 'Control' | 'Manual' | 'Treatment'"""
        ...
    
    def get_complexity_stratum(self, impact_summary: Dict[str, Any]) -> str:
        """Classify complexity. Returns: 'low' | 'medium' | 'high'"""
        ...
```

---

## A-1: Async Telemetry Queue [Complexity: 11, Budget: 5]

**Applied:** asyncio.Queue with WAL SQLite batching

### API Signatures

```python
class AsyncTelemetryQueue:
    def __init__(self, db_path: str, batch_size: int = 100, flush_interval: float = 5.0):
        """Initialize queue. db_path: SQLite DB, batch_size: events per write."""
        ...
    
    async def start(self) -> None:
        """Start background flush task."""
        ...
    
    async def stop(self) -> None:
        """Flush remaining events, stop task."""
        ...
    
    def put(self, event: Dict[str, Any]) -> bool:
        """Non-blocking insert. Returns: success status."""
        ...
    
    async def _background_flush(self) -> None:
        """Flush every flush_interval seconds."""
        while True:
            await asyncio.sleep(self.flush_interval)
            batch = self._get_batch()
            if batch:
                self._write_batch(batch)
    
    def _write_batch(self, events: List[Dict]) -> None:
        """Write batch with WAL mode. events: [{user_id, dataset_name, timestamp, ...}]"""
        ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-1-1 | Queue impl | asyncio.Queue + batch accumulation (2 subtasks) |
| A-1-2 | SQLite WAL | Enable WAL mode, batch INSERT (2 subtasks) |
| A-1-3 | Error handling | Retry on write failure (1 subtask) |

---

## A-2: Telemetry Logger with Retry [Complexity: 9, Budget: 5]

**Applied:** Exponential backoff with JSONL fallback

### API Signatures

```python
class TelemetryLogger:
    def __init__(self, async_queue: AsyncTelemetryQueue, fallback_dir: str = "logs/fallback"):
        """Initialize logger."""
        ...
    
    def log_event(self, event: Dict[str, Any], max_retries: int = 3) -> bool:
        """Log event with retry. Returns: success status."""
        for attempt in range(max_retries):
            if self.async_queue.put(event):
                return True
            time.sleep(2 ** attempt)
        
        self._write_to_fallback(event)
        return False
    
    def _write_to_fallback(self, event: Dict[str, Any]) -> None:
        """Append to JSONL file."""
        ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-2-1 | Retry logic | Exponential backoff (2 subtasks) |
| A-2-2 | Fallback writer | JSONL append (2 subtasks) |
| A-2-3 | Testing | Simulate queue failure (1 subtask) |

---

## A-3: Performance Tracker [Complexity: 10, Budget: 5]

**Applied:** psutil process metrics with percentile computation

### API Signatures

```python
class PerformanceTracker:
    def __init__(self):
        """Initialize tracker."""
        self.metrics = []
    
    def track_operation(self, func: Callable, *args, **kwargs) -> Tuple[Any, Dict]:
        """Track operation. Returns: (result, {latency_ms, memory_delta_mb, cpu_percent})"""
        mem_before = self._measure_memory()
        start = time.time()
        
        result = func(*args, **kwargs)
        
        latency = (time.time() - start) * 1000
        mem_after = self._measure_memory()
        
        metrics = {
            'latency_ms': latency,
            'memory_delta_mb': (mem_after - mem_before) / 1024 / 1024,
            'cpu_percent': psutil.cpu_percent(interval=0.1)
        }
        self.metrics.append(metrics)
        
        return result, metrics
    
    def get_metrics(self) -> Dict[str, Dict]:
        """Returns: {latency_ms: {mean, std, p50, p95}, memory_delta_mb: {mean, std}, cpu_percent: {mean}}"""
        ...
    
    def _compute_percentile(self, values: List[float], percentile: int) -> float:
        """Compute percentile. values: sorted list, percentile: 0-100."""
        sorted_vals = sorted(values)
        idx = int(len(sorted_vals) * percentile / 100)
        return sorted_vals[idx]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-3-1 | psutil integration | Memory, CPU measurement (2 subtasks) |
| A-3-2 | Percentile computation | p50, p95 without numpy (2 subtasks) |
| A-3-3 | Aggregation | mean/std/percentiles (1 subtask) |

---

## A-4: Extended Instrumented Loader [Complexity: 9, Budget: 5]

**Applied:** Hook h-m3 loader with h-m4 telemetry

### API Signatures

```python
class ExtendedInstrumentedLoader:
    def __init__(
        self,
        telemetry_logger: TelemetryLogger,
        migration_planner: MigrationPlanner,
        performance_tracker: PerformanceTracker,
        deprecation_registry: Dict[str, str]
    ):
        """Initialize loader. deprecation_registry: {deprecated_name: successor_name}"""
        ...
    
    def load_dataset_with_tracking(
        self,
        dataset_name: str,
        user_id: str,
        **kwargs
    ) -> Tuple[Any, Dict[str, Any]]:
        """Load dataset with telemetry. Returns: (dataset, {latency_ms, memory_delta_mb, group, deprecated})"""
        
        # 1. Check deprecation
        deprecated = dataset_name in self.deprecation_registry
        successor = self.deprecation_registry.get(dataset_name)
        
        # 2. Assign group (reuse h-m3)
        group = self._assign_user_group(user_id)
        
        # 3. Track load performance
        dataset, perf_metrics = self.performance_tracker.track_operation(
            datasets.load_dataset, dataset_name, **kwargs
        )
        
        # 4. Log event (async)
        self._log_load_event(user_id, dataset_name, deprecated, successor, group)
        
        return dataset, {**perf_metrics, 'group': group, 'deprecated': deprecated}
    
    def _assign_user_group(self, user_id: str) -> str:
        """Hash-based assignment. Returns: 'baseline' | 'instrumented'"""
        hash_val = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
        return 'baseline' if hash_val % 2 == 0 else 'instrumented'
    
    def _log_load_event(
        self,
        user_id: str,
        dataset_name: str,
        deprecated: bool,
        successor: str,
        group: str
    ) -> None:
        """Log event via async queue."""
        event = {
            'user_id': user_id,
            'dataset_name': dataset_name,
            'deprecated': deprecated,
            'successor': successor,
            'group': group,
            'timestamp': time.time()
        }
        self.telemetry_logger.log_event(event)
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-4-1 | Deprecation check | Query registry (1 subtask) |
| A-4-2 | Performance tracking | Wrap load with tracker (2 subtasks) |
| A-4-3 | Async logging | Queue event (1 subtask) |
| A-4-4 | Integration test | End-to-end load (1 subtask) |

---

## A-5: Capture Rate Analyzer [Complexity: 11, Budget: 5]

**Applied:** Wilson score confidence interval

### API Signatures

```python
class CaptureRateAnalyzer:
    def __init__(self, db_path: str):
        """Initialize analyzer."""
        self.db_path = db_path
    
    def compute_capture_rate(self, expected_events: int) -> Dict[str, Any]:
        """Compute capture rate. Returns: {captured, expected, rate, ci_low, ci_high}"""
        conn = sqlite3.connect(self.db_path)
        captured = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()
        
        rate = captured / expected_events if expected_events > 0 else 0
        ci_low, ci_high = proportion_confint(captured, expected_events, alpha=0.05, method='wilson')
        
        return {
            'captured': captured,
            'expected': expected_events,
            'rate': rate,
            'ci_low': ci_low,
            'ci_high': ci_high
        }
    
    def compute_completeness(self) -> float:
        """Returns: % events with full context (user_id, timestamp, dataset)."""
        conn = sqlite3.connect(self.db_path)
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        complete = conn.execute(
            "SELECT COUNT(*) FROM events WHERE user_id IS NOT NULL AND timestamp IS NOT NULL AND dataset_name IS NOT NULL"
        ).fetchone()[0]
        conn.close()
        
        return complete / total if total > 0 else 0
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| A-5-1 | SQL queries | Count captured events (1 subtask) |
| A-5-2 | Wilson CI | Confidence interval computation (2 subtasks) |
| A-5-3 | Completeness metric | Check required fields (1 subtask) |
| A-5-4 | Gate check | Verify ci_low >= 0.95 (1 subtask) |

---

## Performance Summary

| Component | Complexity | Latency | Notes |
|-----------|------------|---------|-------|
| Async queue put | O(1) | <1ms | Non-blocking |
| Batch flush | O(B) | <100ms | B=100 events |
| Performance tracking | O(1) | <5ms | psutil overhead |
| Capture rate query | O(N) | <1s | N=4000 events |
| Wilson CI | O(1) | <1ms | Closed-form formula |

**Total overhead target:** <10% per load operation.

---

## Budget Summary

| Task | Complexity | Budget Allocated | Budget Used |
|------|------------|------------------|-------------|
| A-1 Async Queue | 11 | 5 | 5 |
| A-2 Telemetry Logger | 9 | 5 | 5 |
| A-3 Performance Tracker | 10 | 5 | 5 |
| A-4 Extended Loader | 9 | 5 | 5 |
| A-5 Capture Analyzer | 11 | 5 | 5 |
| **TOTAL** | **50** | **25** | **25** |

---

## Data Flow

```
User calls load_dataset(name, user_id)
  ↓
ExtendedInstrumentedLoader.load_dataset_with_tracking()
  ↓
1. Check deprecation registry
2. Assign user group (hash-based)
3. PerformanceTracker.track_operation(load_dataset)
4. TelemetryLogger.log_event() → AsyncTelemetryQueue.put()
  ↓
AsyncTelemetryQueue background task flushes every 5s
  ↓
Batch write to SQLite (WAL mode)
  ↓
CaptureRateAnalyzer queries DB for gate validation
```

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Step:** Code generation based on these API signatures
