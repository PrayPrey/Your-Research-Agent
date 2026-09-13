# Product Requirements Document: Health Metrics Deprecation Detection (h-m1)

**Date:** 2026-08-24
**Author:** Anonymous
**Hypothesis:** h-m1 (MECHANISM)
**Phase:** 3 - Implementation Planning

---

## Executive Summary

Build health metrics computation system to automatically surface dataset deprecation candidates by analyzing usage velocity, successor emergence, and issue ratio. Validate that computed metrics predict maintainer deprecation decisions with ≥60% precision and ≥80% recall.

**Core Value Proposition:** Reduce maintainer cognitive burden by automatically flagging datasets that show deprecation signals (declining usage, emerging successors, high issue burden).

**Success Criteria:** Precision ≥60%, Recall ≥80% against 6-month ground-truth deprecation decisions.

---

## Problem Statement

### Background

Dataset deprecation currently relies on informal mechanisms. Maintainers lack systematic tools to identify deprecation candidates, leading to outdated datasets persisting without clear successor guidance.

### Pain Points

1. No automated detection of deprecation candidates
2. Maintainers must manually monitor usage patterns
3. High cognitive burden to track successor emergence
4. Inconsistent deprecation decisions across datasets

### Target Users

- Dataset maintainers (HuggingFace Hub, Papers with Code)
- Repository administrators
- Research platform operators

---

## Functional Requirements

### FR-1: Data Collection

**Priority:** P0 (Critical)
**Description:** Collect dataset metadata from multiple APIs for health metric computation.

**Acceptance Criteria:**
- Query HuggingFace API for download logs (6-month history per dataset)
- Query Papers with Code API for citation graph (predecessor/successor relationships)
- Query GitHub API for issue tracker data (open vs closed issues)
- Handle API rate limits gracefully
- Cache API responses to minimize redundant calls
- Support ~100,000+ datasets from HuggingFace Hub

**Dependencies:** HuggingFace API, Papers with Code API, GitHub API

---

### FR-2: Usage Velocity Computation

**Priority:** P0 (Critical)
**Description:** Compute usage velocity (download trend slope) for each dataset.

**Acceptance Criteria:**
- Linear regression on 6-month daily download logs
- Return slope value (negative = declining usage)
- Handle missing data points gracefully
- Flag datasets with velocity < 0.3

**Algorithm:**
```python
def compute_usage_velocity(download_history: List[int]) -> float:
    timestamps = np.arange(len(download_history))
    velocity = np.polyfit(timestamps, download_history, deg=1)[0]
    return velocity
```

---

### FR-3: Successor Emergence Computation

**Priority:** P0 (Critical)
**Description:** Count datasets citing this dataset as a predecessor.

**Acceptance Criteria:**
- Parse citation graph from Papers with Code API
- Count successor datasets
- Flag datasets with emergence > 3

**Algorithm:**
```python
def compute_successor_emergence(dataset_id: str, citation_graph: Dict) -> int:
    return len(citation_graph.get(dataset_id, []))
```

---

### FR-4: Issue Ratio Computation

**Priority:** P0 (Critical)
**Description:** Compute ratio of open issues to total issues.

**Acceptance Criteria:**
- Query GitHub API for issue tracker data
- Compute open_issues / total_issues
- Handle repositories with zero issues (return 0.0)
- Flag datasets with issue_ratio > 0.6

**Algorithm:**
```python
def compute_issue_ratio(issues: List[Dict]) -> float:
    open_count = sum(1 for i in issues if i['state'] == 'open')
    return open_count / len(issues) if issues else 0.0
```

---

### FR-5: Deprecation Candidate Flagging

**Priority:** P0 (Critical)
**Description:** Flag top 30 datasets exceeding all three health metric thresholds.

**Acceptance Criteria:**
- Combine velocity, emergence, and issue_ratio metrics
- Flag datasets where velocity < 0.3 AND emergence > 3 AND issue_ratio > 0.6
- Return top 30 flagged candidates

**Algorithm:**
```python
def flag_deprecation_candidate(metrics: Dict) -> bool:
    return (metrics['velocity'] < 0.3 and
            metrics['emergence'] > 3 and
            metrics['issue_ratio'] > 0.6)
```

---

### FR-6: Ground-Truth Collection

**Priority:** P0 (Critical)
**Description:** Monitor actual maintainer deprecation decisions over 6 months.

**Acceptance Criteria:**
- Track HuggingFace dataset status changes (Month 0 → Month 6)
- Record deprecation events with timestamps
- Label datasets as DEPRECATED or NOT_DEPRECATED
- Store ground-truth labels for precision/recall validation

---

### FR-7: Precision/Recall Evaluation

**Priority:** P0 (Critical)
**Description:** Validate flagged candidates against ground-truth deprecations.

**Acceptance Criteria:**
- True Positives: Flagged datasets that were deprecated
- False Positives: Flagged datasets that were NOT deprecated
- False Negatives: Deprecated datasets that were NOT flagged
- Compute Precision = TP / (TP + FP)
- Compute Recall = TP / (TP + FN)
- Gate check: Precision ≥ 60% AND Recall ≥ 80%

**Evaluation Code:**
```python
from sklearn.metrics import precision_score, recall_score
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
```

---

### FR-8: Visualization

**Priority:** P1 (High)
**Description:** Generate figures for analysis and validation.

**Required Figures:**
1. **Gate Metrics Comparison** (precision/recall bar chart)
2. **Health Metrics Distribution** (scatter: velocity vs emergence, color by issue_ratio)
3. **Confusion Matrix** (TP, FP, FN, TN)
4. **Threshold Sensitivity** (precision/recall curves as thresholds vary)
5. **Deprecation Timeline** (Month 0 → Month 6 cumulative deprecations)

**Acceptance Criteria:**
- All figures saved to `h-m1/figures/`
- Figure generation integrated into experiment code
- PNG format, readable labels, legend included

---

## Non-Functional Requirements

### NFR-1: Performance

- API query latency: < 30 seconds per dataset (with caching)
- Total computation time: < 2 hours for 100,000 datasets
- Memory usage: < 4GB RAM

### NFR-2: Reliability

- Handle API failures gracefully (retry with exponential backoff)
- Cache API responses to avoid redundant calls
- Log all API errors for debugging

### NFR-3: Reproducibility

- Random seed: 42 (for reproducible API sampling if rate-limited)
- Store API response timestamps
- Version all API endpoints used

### NFR-4: Code Quality

- Unit tests for metric computation functions
- Integration tests for API clients
- Code coverage ≥ 80%

---

## Dependencies

### External Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| HuggingFace Hub API | Download logs | latest |
| Papers with Code API | Citation graph | latest |
| GitHub API | Issue tracking | v3 |
| numpy | Linear regression | ≥1.20 |
| sklearn | Precision/recall | ≥0.24 |
| matplotlib | Visualization | ≥3.3 |

### Internal Dependencies

| Dependency | Status |
|------------|--------|
| h-e1 (Instrumentation) | VALIDATED ✓ |

---

## Success Criteria

### Must-Have (Gate Condition)

- **Precision ≥ 60%**: At least 18/30 flagged datasets actually deprecated
- **Recall ≥ 80%**: Health metrics catch at least 80% of actual deprecations

### Nice-to-Have

- Precision ≥ 70%
- Recall ≥ 90%
- Computation time < 1 hour

---

## Out of Scope

- Real-time deprecation detection (batch computation only)
- Automated deprecation actions (flagging only, no auto-deprecation)
- Multi-platform support (HuggingFace only for this hypothesis)
- Model training (infrastructure research, no ML models)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API rate limits | Implement caching + exponential backoff |
| Missing citation data | Fallback to 0 for emergence metric |
| Ground-truth labels unavailable | Extend observation window to 12 months |
| Low precision/recall | Adjust thresholds via sensitivity analysis |

---

## Timeline Estimate

- Data Collection: 1-2 days
- Metric Computation: 1 day
- Evaluation: 1 day
- Visualization: 0.5 day
- **Total: 3-5 days**

---

## Appendix: Baseline Comparison

| Baseline | Precision | Recall | Notes |
|----------|-----------|--------|-------|
| Random | 1-5% | Unknown | Deprecations are rare events |
| Heuristic (manual) | 40-50% | 60% | From software package mgmt literature |
| **h-m1 Target** | **≥60%** | **≥80%** | Automated health metrics |

---

**Document Status:** COMPLETE
**Phase 3 Step:** 2/10
**Next Step:** Architecture Design
