# Product Requirements Document: H-M4

**Hypothesis:** Traditional Benchmark Persistence with Reduced Dominance
**Statement:** ImageNet/CIFAR share of total benchmark usage decreases while absolute paper counts remain stable
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This experiment validates H-M4 by analyzing traditional benchmark usage patterns from 2018-2024. The hypothesis tests whether established benchmarks (ImageNet, CIFAR-10, CIFAR-100) persist in absolute terms while losing relative market share to emergent benchmarks.

**Success Criteria:**
- Traditional benchmark share decreases post-2020
- Absolute paper counts remain within ±20% of pre-2020 levels
- Both conditions must be satisfied for gate PASS

**Continuation from H-M3:**
H-M3 confirmed researcher attention shift to emergent benchmarks (7.53% → 26.54% share). H-M4 tests the complementary hypothesis: traditional benchmarks persist but with reduced dominance.

---

## 2. Problem Statement

Following H-M3's confirmation of attention shift toward emergent benchmarks, we need to verify the persistence pattern: do traditional benchmarks maintain absolute usage while losing relative dominance? This distinguishes between two scenarios:
1. **Persistence with reduced dominance** (H-M4 hypothesis): Traditional benchmarks remain stable, market growth absorbed by new benchmarks
2. **Active decline**: Traditional benchmarks losing absolute ground

**Predecessor Results:**
- H-M3 PASS: Emergent share increased from 7.53% to 26.54% post-2021
- Chi-square = 1025.23, p < 10^-224
- Data source: pwc-archive/datasets

---

## 3. Functional Requirements

### FR-1: Data Collection Pipeline
- **FR-1.1:** Load evaluation tables from HuggingFace `pwc-archive/evaluation-tables`
- **FR-1.2:** Load dataset metadata from HuggingFace `pwc-archive/datasets`
- **FR-1.3:** Extract paper-benchmark associations with submission dates (2018-2024)
- **FR-1.4:** Aggregate monthly paper counts per benchmark

### FR-2: Traditional Benchmark Filtering
- **FR-2.1:** Filter to ImageNet, ImageNet-1k, CIFAR-10, CIFAR-100 (case-insensitive)
- **FR-2.2:** Compute unique paper counts per month for traditional benchmarks
- **FR-2.3:** Compute total benchmark paper counts per month

### FR-3: Share and Count Analysis
- **FR-3.1:** Compute monthly share: `traditional_papers / total_papers`
- **FR-3.2:** Split data at 2020-01 boundary
- **FR-3.3:** Calculate pre-2020 and post-2020 mean shares
- **FR-3.4:** Calculate pre-2020 and post-2020 mean absolute counts
- **FR-3.5:** Compute count ratio: `post_2020_count_mean / pre_2020_count_mean`

### FR-4: Gate Criteria Evaluation
- **FR-4.1:** Share decrease test: `post_2020_share < pre_2020_share`
- **FR-4.2:** Count stability test: `0.8 <= count_ratio <= 1.2`
- **FR-4.3:** Gate PASS requires both conditions satisfied

### FR-5: Visualization
- **FR-5.1:** Gate metrics bar chart (pre vs post share + normalized counts)
- **FR-5.2:** Monthly share time series with 2020 vertical marker
- **FR-5.3:** Stacked area chart: traditional vs emergent paper counts
- **FR-5.4:** Per-benchmark breakdown (ImageNet, CIFAR-10, CIFAR-100 lines)

---

## 4. Data Specification

### 4.1 Primary Dataset
| Attribute | Value |
|-----------|-------|
| Name | Papers With Code Evaluation Tables + Datasets Archive |
| Type | programmatic-api |
| Source | HuggingFace Hub |
| Identifiers | `pwc-archive/evaluation-tables`, `pwc-archive/datasets` |
| Time Range | 2018-01 to 2024-12 (monthly) |
| Sample Size | Full archive (~175k papers, ~2.8k datasets) |

### 4.2 Traditional Benchmarks
```yaml
traditional_benchmarks:
  - imagenet
  - imagenet-1k
  - cifar-10
  - cifar-100
```

### 4.3 Expected Data Schema
```python
@dataclass
class BenchmarkRecord:
    paper_id: str
    dataset_name: str
    date: str  # YYYY-MM-DD
    month: str  # YYYY-MM (derived)

@dataclass
class MonthlyMetrics:
    month: str
    traditional_count: int
    total_count: int
    share: float
```

### 4.4 Loading Code
```python
from datasets import load_dataset

eval_tables = load_dataset("pwc-archive/evaluation-tables", split="train")
datasets_meta = load_dataset("pwc-archive/datasets", split="train")
```

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Process full PWC archive within 5 minutes
- Memory usage < 8GB RAM

### NFR-2: Reproducibility
- Fixed random seed where applicable
- All data from versioned HuggingFace datasets
- No API calls to external services during analysis

### NFR-3: Output Format
- Results in YAML format for verification_state.yaml integration
- Figures saved as PNG to `{hypothesis_folder}/figures/`

---

## 6. Success Criteria

### Primary Gate Criteria
| Metric | Threshold | Priority |
|--------|-----------|----------|
| Share Decrease | post_share < pre_share | P0 |
| Count Stability | 0.8 ≤ count_ratio ≤ 1.2 | P0 |

### Secondary Metrics (Informational)
| Metric | Expected | Priority |
|--------|----------|----------|
| Mann-Whitney U p-value | < 0.05 | P1 |
| Per-benchmark stability | Each within ±30% | P2 |

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
pandas>=2.0.0
scipy>=1.10.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### 7.2 Data Sources
- HuggingFace Hub: `pwc-archive/evaluation-tables`
- HuggingFace Hub: `pwc-archive/datasets`

### 7.3 Predecessor Hypotheses
- H-M3: Researcher Attention Shift (PASS required)

---

## 8. Assumptions and Constraints

### Assumptions
- A1: PWC evaluation tables contain representative paper-benchmark associations
- A2: Date fields in PWC data are reasonably accurate
- A3: "Traditional" benchmark set captures majority of CV benchmark usage

### Constraints
- C1: Analysis limited to 2018-2024 window
- C2: Uses existing PWC categorization (no manual labeling)
- C3: Monthly granularity (no daily breakdown)

---

## 9. Out of Scope

- Real-time API integration with Papers With Code
- Manual benchmark categorization beyond predefined list
- Citation-weighted analysis (simple paper counts only)
- Sub-benchmark granularity (e.g., ImageNet validation vs test)

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
