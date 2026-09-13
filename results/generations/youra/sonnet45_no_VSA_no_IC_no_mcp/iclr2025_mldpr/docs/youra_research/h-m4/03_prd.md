# Product Requirements Document: h-m4 — Adoption Tracking Measurement Infrastructure

**Hypothesis ID:** h-m4  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-24  
**Version:** 1.0

---

## 1. Executive Summary

### 1.1 Purpose

Build load-time instrumentation to track successor adoption events for the h-m3 deprecation mechanism, enabling quantitative measurement of deprecation efficacy with performance overhead < 10% and telemetry capture rate ≥ 95%.

### 1.2 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Performance Overhead | < 10% | Benchmark (instrumented vs baseline) |
| Telemetry Capture Rate | ≥ 95% | `captured_events / expected_events` |
| Adoption Event Completeness | ≥ 95% | Ground truth validation |
| Memory Overhead | < 50 MB | Peak memory delta |
| Delivery Latency p95 | < 5s | Event timestamp diff |

### 1.3 Stakeholders

- **Research Lead:** Anonymous (yoon303@etri.re.kr)
- **Prerequisite:** h-m3 (executable policies with instrumented loader)
- **Phase:** Mechanism validation (Phase 4)

---

## 2. Problem Statement

### 2.1 Current State

h-m3 delivers deprecation warnings + successor recommendations at dataset load time. However, we lack quantitative measurement of whether users actually adopt successors, making it impossible to measure deprecation mechanism efficacy.

### 2.2 Desired State

Load-time instrumentation captures:
1. Deprecation event (user loaded D at time t1)
2. Adoption event (user loaded S at time t2, where t2 - t1 ≤ 30 days)
3. Full event trails for statistical analysis

With ≥ 95% capture rate and < 10% performance overhead.

### 2.3 Gap

Need asynchronous telemetry infrastructure that:
- Captures events with minimal overhead
- Handles network failures gracefully
- Provides ground truth validation
- Supports adoption funnel analysis

---

## 3. Functional Requirements

### 3.1 Core Requirements

#### FR-1: Async Event Queue
**Priority:** P0 (Critical)

Implement async event batching to reduce overhead:
- Background flush every 5 seconds
- Batch size: 100 events
- Non-blocking writes to main thread

**Success Metric:** Load time overhead < 5% vs synchronous writes

#### FR-2: Telemetry Logger with Retry
**Priority:** P0 (Critical)

Log events with automatic retry:
- Max 3 retries with exponential backoff
- Fallback to local file if DB unavailable
- SQLite WAL mode for concurrent writes

**Success Metric:** Capture rate ≥ 95% under simulated failures

#### FR-3: Performance Tracker
**Priority:** P0 (Critical)

Track load operation metrics:
- Latency (ms)
- Memory delta (MB)
- CPU time

**Success Metric:** Overhead measurement accuracy within 2%

#### FR-4: Ground Truth Generation
**Priority:** P0 (Critical)

Generate deterministic log for validation:
- Baseline group logs to `ground_truth.jsonl`
- Instrumented group logs to `telemetry.db`
- Comparison yields precision/recall/F1

**Success Metric:** Validation metrics computable

#### FR-5: Adoption Event Tracker
**Priority:** P0 (Critical)

Track adoption events (D → S within 30 days):
```python
query = """
SELECT e1.user_id, e1.dataset, e2.dataset AS successor,
       (e2.timestamp - e1.timestamp) AS days
FROM events e1 JOIN events e2 ON e1.user_id = e2.user_id
WHERE e1.deprecated = 1
  AND e2.dataset = e1.successor_dataset
  AND (e2.timestamp - e1.timestamp) <= 30
"""
```

**Success Metric:** Adoption trail completeness ≥ 95%

### 3.2 Baseline Requirements

#### FR-6: Baseline Performance Benchmark
**Priority:** P1 (High)

Benchmark native `load_dataset()` performance:
- 100 runs per dataset size (small/medium/large/xlarge)
- Record: mean, std, p50, p95, p99
- Output: `baseline_performance.json`

**Success Metric:** Statistical significance (n=100) for overhead comparison

#### FR-7: Instrumented Performance Benchmark
**Priority:** P1 (High)

Benchmark instrumented loader performance with same methodology.

#### FR-8: User Workload Simulation
**Priority:** P1 (High)

Simulate 1000 users over 30 days:
- 500 baseline (no telemetry)
- 500 instrumented (telemetry enabled)
- 8 loads per user (2/week)
- 40% encounter deprecated datasets

**Success Metric:** Realistic workload simulation for capture rate validation

### 3.3 Analysis Requirements

#### FR-9: Overhead Analysis
**Priority:** P1 (High)

Calculate overhead per dataset size:
```python
overhead_pct = ((t_instrumented - t_baseline) / t_baseline) * 100
```

Generate visualization showing overhead by size.

#### FR-10: Capture Rate Analysis
**Priority:** P1 (High)

Calculate capture rate with confidence interval:
```python
from statsmodels.stats.proportion import proportion_confint
ci_low, ci_high = proportion_confint(captured, expected, alpha=0.05)
```

#### FR-11: Adoption Funnel Visualization
**Priority:** P2 (Medium)

Generate adoption funnel chart:
- Deprecated dataset loads
- Deprecation notices shown
- Successor loads within 30 days
- Adoption rate by user group

---

## 4. Data Specification

### 4.1 Primary Datasets

| Dataset | Size | Purpose | Auto-download |
|---------|------|---------|---------------|
| `glue/cola` | 8.5 MB | Small dataset baseline | Yes (HF Hub) |
| `squad` | 35 MB | Medium dataset | Yes (HF Hub) |
| `c4` (en subset) | 300 MB | Large dataset | Yes (HF Hub) |
| `imagenet-1k` (validation) | 6.3 GB | Very large dataset | **Manual** |

**Manual Download Required:** imagenet-1k validation split (register + download from official site)

### 4.2 Static Baselines

N/A — this is infrastructure measurement, not ML model evaluation.

### 4.3 Preprocessing

Deprecation simulation:
- Mark `glue/cola` → `glue/cola_v2` (deprecated)
- Mark `squad` → `squad_v2` (deprecated)
- Track user adoption within 30-day window

---

## 5. Models / Algorithms

### 5.1 Core Algorithms

#### Algorithm 1: Async Event Batching
```python
class AsyncTelemetryQueue:
    async def _background_flush(self):
        while True:
            await asyncio.sleep(self.flush_interval)
            events = self._get_batch()
            self._write_to_db(events)
```

#### Algorithm 2: Exponential Backoff Retry
```python
def log_event(event, max_retries=3):
    for attempt in range(max_retries):
        try:
            queue.put(event)
            return True
        except Exception:
            time.sleep(2 ** attempt)
    return False
```

#### Algorithm 3: Adoption Event Detection
SQL query joins deprecation events with successor loads within 30-day window (see FR-5).

### 5.2 Baselines

N/A — this is measurement infrastructure.

### 5.3 Proposed Approach

See Section 5.1 algorithms.

---

## 6. Evaluation Metrics

### 6.1 Standard Metrics

- **Performance Overhead (%)**: `(t_instrumented - t_baseline) / t_baseline × 100`
- **Telemetry Capture Rate (%)**: `captured_events / expected_events × 100`
- **Memory Overhead (MB)**: `peak_memory_instrumented - peak_memory_baseline`

### 6.2 Hypothesis-Specific Metrics

- **Adoption Event Completeness (%)**: `events_with_full_trail / total_adoption_events × 100`
- **Delivery Latency p95 (s)**: 95th percentile of event timestamp diff (client → DB)

### 6.3 Statistical Tests

- **Performance Overhead:** `scipy.stats.ttest_ind(baseline, instrumented)` — reject H0 if p < 0.05
- **Capture Rate:** Wilson score confidence interval — PASS if CI lower bound ≥ 95%

---

## 7. Dependencies

### 7.1 Python Packages

```
# Async telemetry
aiofiles==24.1.0
asyncio==3.4.3

# Performance profiling
psutil==6.1.0
memory_profiler==0.61.0
pytest-benchmark==4.0.0

# Statistical analysis
scipy==1.14.1
statsmodels==0.14.4

# Visualization
matplotlib==3.9.2

# Database
sqlite3 (built-in)
```

### 7.2 External Repositories

Reference implementations:
- OpenTelemetry Python SDK (async batching patterns)
- Sentry Python SDK (retry logic)

### 7.3 Base Hypothesis Code

**Prerequisite:** h-m3

Required components:
- `InstrumentedLoader` class
- `TelemetryLogger` integration
- `load_dataset_with_migration()` method
- SQLite `telemetry.db` schema

Import path: `from h_m3.instrumentation import InstrumentedLoader`

---

## 8. Non-Functional Requirements

### 8.1 Performance

- Load time overhead < 10% (target: < 5%)
- Memory overhead < 50 MB
- CPU overhead < 5%
- p95 latency < 5s

### 8.2 Scalability

- Support 1000 concurrent users
- Handle 4000 events over 30 days
- Batch processing for 10k+ events

### 8.3 Reliability

- Capture rate ≥ 95% under network failures
- Graceful degradation (fallback to local file)
- No data loss during DB locks

### 8.4 Privacy

- No PII in telemetry logs
- Anonymized user IDs
- Compliance with GDPR/CCPA (opt-in required)

---

## 9. Constraints & Assumptions

### 9.1 Technical Constraints

- SQLite write locks limit concurrent throughput
- Network failures affect real-time capture rate
- Clock skew affects adoption window accuracy

### 9.2 Assumptions

- Users consent to telemetry collection
- 30-day observation window is sufficient for adoption measurement
- Simulated users approximate real user behavior

---

## 10. Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Async queue adds overhead | Medium | High | Benchmark async vs sync early |
| SQLite write locks fail | High | Medium | Use WAL mode + connection pooling |
| Simulated users ≠ real users | High | Medium | Validate with small real-user pilot |

---

## 11. Timeline & Milestones

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Implementation | Async queue, performance tracker |
| 2 | Baseline | `baseline_performance.json` |
| 3 | Instrumented | `instrumented_performance.json` |
| 4-6 | Simulation | `telemetry.db` (4000 events) |
| 7 | Analysis | Overhead + capture rate reports |
| 8 | Validation | Gate decision (PASS/FAIL) |

---

## Appendix A: Data Schema

### telemetry.db Schema

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_type TEXT CHECK(event_type IN ('load_dataset', 'deprecation_shown')),
    dataset_name TEXT NOT NULL,
    deprecated BOOLEAN,
    successor_dataset TEXT,
    group_assignment TEXT CHECK(group_assignment IN ('Control', 'Manual', 'Treatment')),
    timestamp INTEGER NOT NULL
);
CREATE INDEX idx_user_timestamp ON events(user_id, timestamp);
```

### ground_truth.jsonl Format

```json
{
  "user_id": "u123",
  "event_type": "load_dataset",
  "dataset_name": "squad",
  "deprecated": true,
  "successor_recommended": "squad_v2",
  "timestamp": "2026-09-15T10:30:00Z"
}
```

---

**End of PRD**
