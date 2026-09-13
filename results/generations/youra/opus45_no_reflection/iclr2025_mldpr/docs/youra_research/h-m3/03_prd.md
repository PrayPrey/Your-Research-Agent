# Product Requirements Document: H-M3

**Hypothesis:** Researcher Attention Shift
**Statement:** Paper counts on MMLU/BIG-Bench/HumanEval leaderboards increased relative to traditional benchmarks post-2021
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-18
**Author:** Anonymous

---

## 1. Executive Summary

This experiment validates H-M3 by analyzing researcher attention shift from traditional benchmarks (ImageNet, CIFAR, SQuAD, GLUE) to emergent-capability benchmarks (MMLU, BIG-Bench, HumanEval) post-2021. The hypothesis tests the demand side of benchmark adoption following H-M2's confirmation that 85.13% of emergent benchmarks were created post-2020.

**Success Criteria:**
- Emergent benchmark share increases post-2021
- Chi-square test p-value < 0.05
- Secondary: Emergent paper counts exceed traditional by 2024

---

## 2. Problem Statement

Following the supply-side confirmation (H-M2: emergent benchmarks created post-2020), we need to verify the demand side: did researchers actually shift their evaluation practices toward these new benchmarks?

**Predecessor Results:**
- H-M2 PASS: 85.13% emergent benchmarks post-2020
- 1,225 emergent benchmarks post-2020 vs 214 pre-2020
- 19x acceleration in emergent benchmark creation rate

---

## 3. Functional Requirements

### FR-1: Data Collection Pipeline
- **FR-1.1:** Fetch benchmark leaderboard data from Papers With Code API via `paperswithcode-client` library
- **FR-1.2:** Fallback to HuggingFace `pwc-archive/datasets` if API unavailable
- **FR-1.3:** Collect paper counts per benchmark aggregated monthly (2018-01 to 2024-12)
- **FR-1.4:** Categorize benchmarks as emergent or traditional

### FR-2: Benchmark Classification
- **FR-2.1:** Emergent benchmarks: MMLU, BIG-Bench, HumanEval, GSM8K, MATH, ARC, HellaSwag, WinoGrande, TruthfulQA, LAMBADA
- **FR-2.2:** Traditional benchmarks: ImageNet, CIFAR-10, CIFAR-100, MNIST, SQuAD, GLUE, CoNLL, Penn Treebank
- **FR-2.3:** Allow extensible categorization via config file

### FR-3: Statistical Analysis
- **FR-3.1:** Compute emergent share per period (pre-2021 vs post-2021)
- **FR-3.2:** Perform chi-square test for independence
- **FR-3.3:** Calculate share change (post - pre)
- **FR-3.4:** Compare 2024 absolute counts

### FR-4: Visualization
- **FR-4.1:** Gate metrics bar chart (pre vs post share)
- **FR-4.2:** Share timeline line plot
- **FR-4.3:** Absolute counts stacked area chart
- **FR-4.4:** Benchmark heatmap (top 20 by year)

---

## 4. Data Specification

### 4.1 Primary Dataset
| Attribute | Value |
|-----------|-------|
| Name | Papers With Code Leaderboard Data |
| Type | programmatic-api |
| Source | Papers With Code API + HuggingFace `pwc-archive/datasets` |
| Time Range | 2018-01 to 2024-12 (monthly) |
| Download | Programmatic via `paperswithcode-client` |

### 4.2 Benchmark Categories
```yaml
emergent_benchmarks:
  - MMLU
  - BIG-Bench
  - HumanEval
  - GSM8K
  - MATH
  - ARC
  - HellaSwag
  - WinoGrande
  - TruthfulQA
  - LAMBADA

traditional_benchmarks:
  - ImageNet
  - CIFAR-10
  - CIFAR-100
  - MNIST
  - SQuAD
  - GLUE
  - CoNLL
  - Penn Treebank
```

### 4.3 Expected Data Schema
```python
@dataclass
class PaperCountRecord:
    benchmark: str
    category: Literal["emergent", "traditional"]
    year_month: str  # "YYYY-MM"
    paper_count: int
```

---

## 5. Evaluation Metrics

### 5.1 Primary Metrics (Gate Determination)
| Metric | Threshold | Description |
|--------|-----------|-------------|
| emergent_share_increase | > 0 | post_2021_share - pre_2021_share |
| chi2_p_value | < 0.05 | Statistical significance |

### 5.2 Secondary Metrics (Informative)
| Metric | Threshold | Description |
|--------|-----------|-------------|
| emergent_exceeds_traditional_2024 | True | Absolute count comparison |

### 5.3 Metric Calculation
```python
from scipy.stats import chi2_contingency

contingency = np.array([
    [pre_emergent, pre_traditional],
    [post_emergent, post_traditional]
])
chi2, p_value, dof, expected = chi2_contingency(contingency)
```

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Data collection: Complete within 30 minutes
- Analysis: Complete within 5 minutes
- Memory usage: < 8GB

### NFR-2: Reliability
- API retry with exponential backoff (3 attempts)
- Fallback to HuggingFace dataset on API failure
- Graceful degradation with partial data

### NFR-3: Reproducibility
- Fixed random seed where applicable
- Versioned dependencies
- Logged API response timestamps

---

## 7. Dependencies

### 7.1 Python Packages
```
paperswithcode-client>=0.3.0
datasets>=2.14.0
scipy>=1.10.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
```

### 7.2 External APIs
- Papers With Code API (https://paperswithcode.com/api/v1/)
- HuggingFace Datasets (pwc-archive/datasets)

---

## 8. Success Criteria

### 8.1 PoC Pass Condition
1. Code executes without error
2. `post_2021_emergent_share > pre_2021_emergent_share`
3. Chi-square p-value < 0.05

### 8.2 Gate Decision
- **PASS:** Both primary metrics satisfied
- **FAIL:** Either primary metric not satisfied (document limitation per SHOULD_WORK gate)

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PWC API rate limits | Use HuggingFace fallback |
| Incomplete paper counts | Document data completeness in results |
| Volume confound (R5) | Dual reporting: raw + normalized counts |

---

## 10. Ablation Variants

### 10.1 Time Window Sensitivity
- Pre/post split at 2020-01 vs 2021-01 vs 2022-01

### 10.2 Benchmark Set Sensitivity
- Exclude newest benchmarks (post-2022)
- Include only top-10 most cited per category

---

*Generated from Phase 2C Experiment Brief*
*Next Phase: Phase 3 - Architecture Agent*
