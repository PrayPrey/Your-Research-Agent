# Experiment Design Brief: h-m4 — Adoption Tracking Measurement Infrastructure

**Hypothesis ID:** h-m4  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-m3 (executable policies with instrumented loader)  
**Date:** 2026-08-24  
**Version:** 1.0

---

## 1. Hypothesis Statement

**Full Statement:**  
Load-time instrumentation tracks successor adoption events, enabling quantitative measurement of deprecation mechanism efficacy with < 10% performance overhead and ≥ 95% telemetry capture rate.

**Operationalized:**  
When users load datasets via the h-m3 instrumented loader at scale (1000+ users over 30 days), the telemetry system will:
1. Maintain performance overhead < 10% vs. native `load_dataset()` calls
2. Capture ≥ 95% of adoption events (deprecated dataset D → successor S within 30 days)
3. Provide complete event trails for quantitative efficacy measurement

**Variables:**
- **IV:** Successor adoption event tracking via instrumented loaders
- **DV1:** Performance overhead (%) = (instrumented_load_time - baseline_load_time) / baseline_load_time × 100
- **DV2:** Telemetry capture rate (%) = captured_events / expected_events × 100
- **DV3:** Adoption event completeness = events_with_full_trail / total_adoption_events × 100
- **CV:** Privacy-preserving telemetry design, user opt-in requirements, network reliability

---

## 2. Research Context

### 2.1 Prior Work (from Phase 1 Research)

From `01_targeted_research.md`:

**Telemetry Best Practices:**
- **OpenTelemetry Python SDK:** Industry standard for distributed tracing with <5% overhead targets
- **Sentry Performance Monitoring:** Async batching reduces overhead to 2-8%
- **Google Analytics Measurement Protocol:** Guaranteed 95%+ delivery via retry queues

**Key Insights:**
1. **Async batching** is critical — synchronous telemetry adds 15-30% overhead
2. **Local queuing** with background upload ensures 95%+ capture even with network failures
3. **Sampling strategies** can reduce volume while maintaining statistical validity

### 2.2 Built-On Foundations (h-m3)

From h-m3 `03_architecture.md`:

**Existing Infrastructure:**
- `InstrumentedLoader` with `TelemetryLogger` integration (from h-e1)
- `load_dataset_with_migration()` already logs deprecation events
- SQLite telemetry.db backend supports event querying

**What h-m3 Provides:**
- User group assignment (Control/Manual/Treatment)
- Deprecation event logging
- Successor recommendation delivery

**What h-m4 Must Validate:**
- Performance overhead at scale (1000+ users, diverse dataset sizes)
- Telemetry capture rate under real-world network conditions
- Adoption event trail completeness (D → S within 30 days)

---

## 3. Experimental Design

### 3.1 Dataset Selection

**Type:** `programmatic-api` (real data from HuggingFace Hub via API)  
**Rationale:** Need real dataset load operations with realistic size/network variability

**Datasets:**

| Dataset | Size | Purpose | Load Time (baseline) |
|---------|------|---------|---------------------|
| `glue/cola` | 8.5 MB | Small dataset | ~2s |
| `squad` | 35 MB | Medium dataset | ~8s |
| `c4` (en subset) | 300 MB | Large dataset | ~60s |
| `imagenet-1k` (validation) | 6.3 GB | Very large dataset | ~15 min |

**Sample Size:** 1000 simulated users × 4 datasets = 4000 load operations

**Deprecation Simulation:**
- Mark `glue/cola` → `glue/cola_v2` (deprecated)
- Mark `squad` → `squad_v2` (deprecated)
- Track whether users load successor within 30-day window

### 3.2 Experimental Conditions

**Two-Group Comparison:**

| Group | Loader | Telemetry | Sample Size |
|-------|--------|-----------|-------------|
| **Baseline** | Native `datasets.load_dataset()` | None | 500 users |
| **Instrumented** | `InstrumentedLoader.load_dataset_with_migration()` | Enabled | 500 users |

**Workload Simulation:**
- Each simulated user performs 8 dataset loads over 30 days
- 2 loads per week (realistic research cadence)
- Random dataset selection from 4 test datasets
- 40% of users encounter deprecated datasets

### 3.3 Performance Overhead Measurement

**Metrics:**

1. **Load Time Overhead:**
   ```python
   overhead_pct = ((t_instrumented - t_baseline) / t_baseline) * 100
   ```

2. **Memory Overhead:**
   ```python
   memory_delta = peak_memory_instrumented - peak_memory_baseline
   ```

3. **CPU Overhead:**
   ```python
   cpu_delta = cpu_time_instrumented - cpu_time_baseline
   ```

**Success Criteria:**
- Load time overhead < 10% across all dataset sizes
- Memory overhead < 50 MB
- CPU overhead < 5%

**Measurement Approach:**
- Use `pytest-benchmark` for latency measurement
- Use `memory_profiler` for peak memory tracking
- Use `cProfile` for CPU profiling
- 100 runs per dataset size for statistical significance

### 3.4 Telemetry Capture Rate Measurement

**Metrics:**

1. **Event Capture Rate:**
   ```python
   capture_rate = (events_in_db / expected_events) * 100
   ```

2. **Event Trail Completeness:**
   ```python
   completeness = (events_with_full_context / total_events) * 100
   ```

3. **Delivery Latency:**
   ```python
   latency_p95 = percentile(event_timestamp_db - event_timestamp_client, 95)
   ```

**Expected Events:**
- 500 instrumented users × 8 loads = 4000 total load events
- 40% encounter deprecated datasets = 1600 deprecation events
- 50% load successor within 30 days = 800 adoption events

**Success Criteria:**
- Capture rate ≥ 95% (≥3800 / 4000 load events captured)
- Event trail completeness ≥ 95% (full context for adoption tracking)
- Delivery latency p95 < 5 seconds

**Failure Scenarios to Simulate:**
- Network failures (10% of operations)
- Database locks (5% of operations)
- Client crashes mid-operation (2% of operations)

### 3.5 Adoption Event Tracking

**Adoption Event Definition:**
```python
# User loads deprecated dataset D at time t1
event1 = {"user_id": "u123", "dataset": "squad", "deprecated": True, "timestamp": t1}

# User loads successor S at time t2, where t2 - t1 ≤ 30 days
event2 = {"user_id": "u123", "dataset": "squad_v2", "deprecated": False, "timestamp": t2}

# Adoption event captured if both events present in telemetry.db
adoption = (event1, event2) where (t2 - t1) ≤ 30 days
```

**Metrics:**
- **Adoption Rate:** `users_who_loaded_successor / users_who_saw_deprecation_notice`
- **Time to Adoption:** Median of `(t2 - t1)` for users who adopted
- **Bypass Rate:** `users_who_continued_deprecated / users_who_saw_notice`

**Success Criteria:**
- ≥ 95% of true adoption events captured (validated via ground truth log)
- No false positives (successor loaded for unrelated reasons counted as adoption)
- Event timestamps accurate within 1 second

---

## 4. Implementation Specifications

### 4.1 Telemetry Architecture Enhancements

**Current h-m3 Implementation (from `03_architecture.md`):**

```python
class InstrumentedLoader:
    def load_dataset_with_migration(self, dataset_name, user_id, **kwargs):
        # Existing: deprecation check, group assignment, intervention display
        self.log_deprecation_event(user_id, dataset_name, group, "loaded")
        return load_dataset(dataset_name, **kwargs)
```

**Required h-m4 Enhancements:**

1. **Async Event Queue:**
   ```python
   import asyncio
   from queue import Queue
   
   class AsyncTelemetryQueue:
       def __init__(self, db_path, batch_size=100, flush_interval=5.0):
           self.queue = Queue()
           self.db_path = db_path
           self.batch_size = batch_size
           self.flush_interval = flush_interval
           asyncio.create_task(self._background_flush())
       
       async def _background_flush(self):
           while True:
               await asyncio.sleep(self.flush_interval)
               self._flush_batch()
       
       def _flush_batch(self):
           events = []
           while not self.queue.empty() and len(events) < self.batch_size:
               events.append(self.queue.get())
           if events:
               self._write_to_db(events)
   ```

2. **Retry Logic:**
   ```python
   class TelemetryLogger:
       def log_event(self, event, max_retries=3):
           for attempt in range(max_retries):
               try:
                   self.async_queue.put(event)
                   return True
               except Exception as e:
                   if attempt == max_retries - 1:
                       self._log_to_local_file(event)  # Fallback
                   time.sleep(2 ** attempt)
           return False
   ```

3. **Performance Instrumentation:**
   ```python
   import time
   import psutil
   
   class PerformanceTracker:
       def __init__(self):
           self.metrics = []
       
       def track_load(self, func, *args, **kwargs):
           t0 = time.perf_counter()
           mem0 = psutil.Process().memory_info().rss
           
           result = func(*args, **kwargs)
           
           t1 = time.perf_counter()
           mem1 = psutil.Process().memory_info().rss
           
           self.metrics.append({
               "latency_ms": (t1 - t0) * 1000,
               "memory_delta_mb": (mem1 - mem0) / 1024 / 1024
           })
           
           return result
   ```

### 4.2 Ground Truth Generation

**Approach:**
1. Run baseline group with **deterministic logging** (all events to ground_truth.jsonl)
2. Run instrumented group with standard telemetry
3. Compare instrumented telemetry.db against ground_truth.jsonl

**Ground Truth Log Format:**
```json
{
  "user_id": "u123",
  "event_type": "load_dataset",
  "dataset_name": "squad",
  "deprecated": true,
  "timestamp": "2026-09-15T10:30:00Z",
  "group": "Treatment",
  "successor_recommended": "squad_v2"
}
```

**Validation Metrics:**
- **Precision:** `true_positives / (true_positives + false_positives)`
- **Recall:** `true_positives / (true_positives + false_negatives)`
- **F1 Score:** `2 * (precision * recall) / (precision + recall)`

### 4.3 Statistical Power Analysis

**Effect Size:** Detect 10% overhead difference with 80% power

**Sample Size Calculation:**
```python
from statsmodels.stats.power import ttest_power

# Parameters
effect_size = 0.1  # 10% overhead
alpha = 0.05
power = 0.8

# Required sample size per group
n = ttest_power(effect_size, nobs=None, alpha=alpha, power=power)
# Result: ~500 samples per group
```

**Total Operations:**
- 500 users × 8 loads = 4000 operations per group
- Well above minimum required sample size

---

## 5. Success Criteria & Gate Evaluation

### 5.1 SHOULD_WORK Gate Criteria

| Metric | Target | Measurement Method | Pass/Fail Threshold |
|--------|--------|-------------------|---------------------|
| **Performance Overhead** | < 10% | Benchmark comparison (instrumented vs baseline) | FAIL if ≥ 10% for any dataset size |
| **Telemetry Capture Rate** | ≥ 95% | `captured_events / expected_events` | FAIL if < 95% |
| **Adoption Event Completeness** | ≥ 95% | Ground truth validation | FAIL if < 95% |
| **Memory Overhead** | < 50 MB | `memory_profiler` peak delta | Secondary (warn if > 50 MB) |
| **Delivery Latency p95** | < 5s | Event timestamp diff (client → DB) | Secondary (warn if > 5s) |

### 5.2 Pass Scenarios

**PASS Conditions:**
1. All 3 primary metrics meet targets
2. No catastrophic failures (crashes, data loss)
3. Privacy compliance verified (no PII in logs)

**PARTIAL PASS Conditions:**
1. Performance overhead 10-15% (marginal)
2. Capture rate 90-95% (acceptable with retry improvements)

**FAIL Conditions:**
1. Performance overhead ≥ 15%
2. Capture rate < 90%
3. Adoption event completeness < 90%

### 5.3 If Gate Fails

**Mitigation Strategies:**

| Failure Mode | Root Cause | Mitigation |
|--------------|------------|------------|
| High overhead | Synchronous DB writes | Implement async queue (already planned) |
| Low capture rate | Network failures | Add local file fallback + retry logic |
| Incomplete events | Race conditions | Add transaction locks, event sequencing |
| High memory usage | Event queue bloat | Add queue size limits, flush thresholds |

**Fallback Approach:**
- If quantitative measurement fails, fall back to **qualitative assessment** (user surveys, manual log analysis)
- Update Phase 6 paper to acknowledge measurement limitations
- Document as "measurement infrastructure validated at small scale only"

---

## 6. Data Processing Pipeline

### 6.1 Data Collection

**Phase 1: Baseline Benchmark (Week 1)**
```bash
# Run native load_dataset() 100 times per dataset size
pytest tests/test_baseline_performance.py --benchmark-only

# Output: baseline_performance.json
{
  "small": {"mean_ms": 2000, "std_ms": 50},
  "medium": {"mean_ms": 8000, "std_ms": 200},
  "large": {"mean_ms": 60000, "std_ms": 1500},
  "xlarge": {"mean_ms": 900000, "std_ms": 20000}
}
```

**Phase 2: Instrumented Measurement (Week 2)**
```bash
# Run instrumented loader 100 times per dataset size
pytest tests/test_instrumented_performance.py --benchmark-only

# Output: instrumented_performance.json
```

**Phase 3: Simulated User Study (Weeks 3-6)**
```python
# Simulate 1000 users over 30 days
python src/simulate_users.py --users 1000 --days 30 --output telemetry.db
```

### 6.2 Data Analysis

**Performance Overhead Analysis:**
```python
import pandas as pd

baseline = pd.read_json("baseline_performance.json")
instrumented = pd.read_json("instrumented_performance.json")

overhead = ((instrumented["mean_ms"] - baseline["mean_ms"]) / baseline["mean_ms"]) * 100

# Visualization
import matplotlib.pyplot as plt
plt.bar(["Small", "Medium", "Large", "XLarge"], overhead)
plt.axhline(y=10, color='r', linestyle='--', label='10% Threshold')
plt.ylabel("Overhead (%)")
plt.title("Load Time Overhead by Dataset Size")
plt.legend()
plt.savefig("overhead_analysis.png")
```

**Capture Rate Analysis:**
```python
import sqlite3

conn = sqlite3.connect("telemetry.db")
cursor = conn.cursor()

# Expected events
expected_events = 500 * 8  # 500 users × 8 loads

# Captured events
captured = cursor.execute("SELECT COUNT(*) FROM events").fetchone()[0]

capture_rate = (captured / expected_events) * 100
print(f"Capture Rate: {capture_rate:.2f}%")
```

**Adoption Event Trail Analysis:**
```python
# Find adoption events (D → S within 30 days)
query = """
SELECT 
    e1.user_id,
    e1.dataset AS deprecated,
    e2.dataset AS successor,
    (e2.timestamp - e1.timestamp) AS time_to_adoption_days
FROM events e1
JOIN events e2 ON e1.user_id = e2.user_id
WHERE e1.deprecated = 1
  AND e2.dataset = e1.successor_dataset
  AND (e2.timestamp - e1.timestamp) <= 30
"""

adoptions = pd.read_sql_query(query, conn)
completeness = (len(adoptions) / ground_truth_adoptions) * 100
print(f"Adoption Event Completeness: {completeness:.2f}%")
```

### 6.3 Statistical Testing

**Performance Overhead:**
```python
from scipy.stats import ttest_ind

baseline_samples = baseline["latencies"]  # List of 100 measurements
instrumented_samples = instrumented["latencies"]

t_stat, p_value = ttest_ind(baseline_samples, instrumented_samples)

if p_value < 0.05 and overhead < 10:
    print("PASS: Overhead < 10% and statistically significant")
elif overhead >= 10:
    print("FAIL: Overhead ≥ 10%")
else:
    print("PASS: No statistically significant overhead")
```

**Capture Rate:**
```python
from statsmodels.stats.proportion import proportion_confint

# Confidence interval for capture rate
ci_low, ci_high = proportion_confint(captured, expected_events, alpha=0.05, method='wilson')

if ci_low >= 0.95:
    print(f"PASS: Capture rate {capture_rate:.2f}% (95% CI: [{ci_low:.2f}, {ci_high:.2f}])")
else:
    print(f"FAIL: Lower CI bound {ci_low:.2f} < 95%")
```

---

## 7. Risks & Mitigation

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Async queue implementation adds overhead** | Medium | High | Benchmark async vs sync early; switch to sync if async > 5% overhead |
| **SQLite write locks cause capture failures** | High | Medium | Use WAL mode, connection pooling, retry logic |
| **Large datasets timeout telemetry** | Low | Low | Set telemetry timeout > dataset load time |
| **Clock skew breaks adoption tracking** | Low | Medium | Use server timestamps, not client timestamps |

### 7.2 Experimental Validity Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Simulated users ≠ real users** | High | Medium | Validate with small-scale real user pilot (50 users) |
| **Network conditions unrealistic** | Medium | Medium | Add latency/packet-loss simulation |
| **Ground truth logging affects baseline** | Low | High | Verify baseline with/without logging identical |

### 7.3 Timeline Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **30-day observation too short** | Medium | Low | Start observation immediately after h-m3 validation |
| **Data collection automation fails** | Low | High | Manual fallback, daily health checks |

---

## 8. Expected Outcomes

### 8.1 Quantitative Results

**Performance Overhead (Expected):**
- Small datasets: 3-5% overhead
- Medium datasets: 2-4% overhead
- Large datasets: 1-2% overhead
- Very large datasets: < 1% overhead

**Rationale:** Async batching amortizes telemetry cost; larger datasets dominate instrumentation overhead.

**Capture Rate (Expected):**
- 97-99% under normal conditions
- 95-97% with simulated network failures

**Adoption Event Completeness (Expected):**
- 98% completeness (some users opt out mid-study)

### 8.2 Qualitative Insights

1. **Failure Mode Documentation:**
   - Which network failures cause capture loss?
   - How do database locks affect latency?

2. **Scalability Insights:**
   - Can system handle 10k users? 100k users?
   - What are bottleneck components?

3. **Privacy Compliance:**
   - Are anonymization measures sufficient?
   - Any PII leakage in logs?

### 8.3 Deliverables

1. **Code:**
   - `src/async_telemetry_queue.py` — Async event batching
   - `src/performance_tracker.py` — Overhead measurement
   - `src/simulate_users.py` — User workload simulation
   - `tests/test_telemetry_performance.py` — Benchmarks

2. **Data:**
   - `baseline_performance.json` — Native load times
   - `instrumented_performance.json` — Instrumented load times
   - `telemetry.db` — 4000 simulated user events
   - `ground_truth.jsonl` — Expected event log

3. **Analysis:**
   - `04_validation.md` — Gate evaluation report
   - `figures/overhead_by_size.png` — Performance chart
   - `figures/capture_rate_over_time.png` — Reliability chart
   - `figures/adoption_funnel.png` — Adoption event trail visualization

4. **Documentation:**
   - `03_prd.md` — Product requirements
   - `03_architecture.md` — System design
   - `03_logic.md` — Core algorithms
   - `03_config.md` — Configuration schema

---

## 9. Integration with Phase 5 (Baseline Comparison)

**Note:** Phase 5 is **SKIPPED** per pipeline config (`skip_baseline_comparison: true`).

However, h-m4 provides **measurement infrastructure** that would enable Phase 5 if run:

**How h-m4 Enables Efficacy Measurement:**
1. Adoption tracking → Measure successor adoption rates per user group
2. Performance logging → Ensure instrumentation doesn't bias results
3. Event completeness → Validate statistical analysis assumptions

**Phase 5 Baseline Comparison (hypothetical):**
```python
# Control group: No migration plans (deprecation notice only)
# Treatment group: Migration plans delivered (h-m3)

control_adoption = telemetry.query("group == 'Control'").adoption_rate
treatment_adoption = telemetry.query("group == 'Treatment'").adoption_rate

lift = ((treatment_adoption - control_adoption) / control_adoption) * 100

# Hypothesis: lift ≥ 50%
if lift >= 50:
    print("Main hypothesis VALIDATED")
else:
    print("Main hypothesis REJECTED")
```

---

## 10. Timeline & Milestones

**Total Duration:** 6 weeks (30 implementation + 12 validation)

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Implementation | Async telemetry queue, performance tracker |
| 2 | Baseline Measurement | `baseline_performance.json` |
| 3 | Instrumented Measurement | `instrumented_performance.json` |
| 4-6 | Simulated User Study | `telemetry.db` with 4000 events |
| 7 | Analysis | Overhead analysis, capture rate analysis |
| 8 | Validation | Gate evaluation, `04_validation.md` |

**Checkpoints:**
- **Week 2:** Baseline benchmarks complete → Proceed to instrumentation
- **Week 3:** Instrumented benchmarks complete → Proceed to simulation
- **Week 6:** Simulation complete → Proceed to analysis
- **Week 8:** Gate decision → PASS/FAIL/PARTIAL

---

## 11. Acceptance Criteria Summary

### 11.1 Primary Criteria (MUST Pass for Gate)

- [ ] Performance overhead < 10% across all dataset sizes
- [ ] Telemetry capture rate ≥ 95%
- [ ] Adoption event completeness ≥ 95%

### 11.2 Secondary Criteria (SHOULD Pass)

- [ ] Memory overhead < 50 MB
- [ ] Delivery latency p95 < 5s
- [ ] No privacy violations (PII in logs)
- [ ] No data loss during simulated failures

### 11.3 Documentation Criteria

- [ ] All code modules implement specified interfaces
- [ ] Performance benchmarks reproducible
- [ ] Ground truth validation scripts included
- [ ] `04_validation.md` contains gate decision with evidence

---

**End of Experiment Brief**
