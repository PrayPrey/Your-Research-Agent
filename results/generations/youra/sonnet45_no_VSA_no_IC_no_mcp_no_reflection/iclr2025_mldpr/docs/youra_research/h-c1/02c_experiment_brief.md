# Experiment Brief: Expert Consensus Validation (h-c1)

**Hypothesis ID:** h-c1  
**Type:** CONDITION  
**Gate:** MUST_WORK  
**Date:** 2026-08-28  

---

## 1. Hypothesis Statement

**Statement:**  
High-confidence expert responses (≥4/5 confidence) achieve >70% agreement within ±1 year for major benchmarks (ImageNet, GLUE, SQuAD) when surveyed about saturation timing.

**Rationale:**  
This hypothesis validates the foundational assumption (A1 from verification plan) that expert consensus on benchmark saturation dates exists and is measurable. Without validated ground truth, algorithmic saturation detection (H-M1, H-M2) cannot be validated. Expert consensus provides the reference standard for evaluating whether dual-metric detection (score convergence + velocity decay) aligns with community-recognized saturation events.

**Success Criteria:**
- Primary: ≥70% of high-confidence (≥4/5) responses per benchmark fall within ±1 year of modal saturation date
- Secondary: ≥30 high-confidence responses per benchmark (n≥30 statistical power threshold)
- Tertiary: Fleiss' kappa >0.60 (substantial agreement, chance-adjusted)

**Failure Response:**
- IF agreement <50%: PIVOT to citation-based validation (SOTA mention decay in published papers, per A1 assumption)
- IF n<30 high-confidence responses: EXPAND survey distribution (add conference mailing lists, Twitter outreach)

---

## 2. Dataset Specification

### 2.1 Dataset Type
**Type:** custom (user-provided survey data)  
**Source:** Expert survey via multiple distribution channels  
**Format:** Structured survey responses (CSV/JSON)  

### 2.2 Survey Design

**Target Population:**
- n≥50 ML researchers (target: 100-150 total responses to yield 30+ high-confidence per benchmark)
- Stratification:
  - Domain: 50% vision, 50% NLP
  - Seniority: 25% PhD students, 25% postdocs, 25% industry researchers, 25% faculty

**Distribution Channels:**
1. Papers With Code community forum (primary, benchmark-focused audience)
2. r/MachineLearning subreddit survey thread
3. Direct outreach: NeurIPS/ICML/ICLR mailing lists (if primary channels insufficient)

**Survey Instrument:**

For each benchmark (ImageNet, GLUE, SQuAD):
```
Question: "When did the [BENCHMARK_NAME] benchmark saturate (i.e., when did 
          performance improvements plateau, making the benchmark less useful 
          for distinguishing model capabilities)?"

Response format:
- Saturation date: [Year] [Month] dropdown
- Confidence: 1 (very uncertain) to 5 (very confident)
- Optional: Brief rationale (free text, 1-2 sentences)
```

Metadata collection:
- Research domain: [Vision | NLP | Other]
- Career stage: [PhD student | Postdoc | Industry researcher | Faculty | Other]

**Data Collection:**
- Tool: Google Forms (free, API access for programmatic download)
- Duration: 2-3 weeks data collection window
- IRB consideration: Survey classified as minimal-risk opinion research (no identifiable data beyond career metadata)

### 2.3 Dataset Validation

**Completeness checks:**
- ≥30 high-confidence (≥4/5) responses per benchmark
- Domain balance: 40-60% vision/NLP split (tolerable imbalance)
- No duplicate responses (IP-based deduplication via Google Forms)

**Quality filters:**
- Exclude responses with confidence=1 (very uncertain) from primary analysis
- Exclude responses with impossible dates (e.g., saturation date after 2024 for ImageNet/GLUE/SQuAD)
- Flag responses with <30-second completion time (potential spam)

---

## 3. Baseline Experiments

### 3.1 Null Hypothesis Baseline

**Method:** Random agreement baseline  
**Description:** Calculate expected agreement rate by chance alone  
**Implementation:**
- Shuffle saturation date responses randomly across experts
- Compute agreement rate for shuffled data (1000 permutations)
- Compare observed agreement vs. permutation distribution (p-value)

**Expected Performance:** <30% agreement (chance level for ±1 year window over 7-year range 2017-2024)

### 3.2 Raw Agreement Baseline

**Method:** Simple majority agreement (no confidence weighting)  
**Description:** Percentage of all responses (not just high-confidence) within ±1 year of modal date  
**Implementation:**
- Compute mode (most common saturation date) for each benchmark
- Count responses within ±1 year window
- Agreement rate = (responses in window) / (total responses)

**Expected Performance:** 50-60% agreement (weaker than high-confidence subset)

### 3.3 Alternative Consensus Metric: Fleiss' Kappa

**Method:** Chance-adjusted agreement for multiple raters  
**Description:** Measures agreement beyond chance for categorical judgments  
**Implementation:**
- Treat saturation date as categorical variable (year buckets: 2017, 2018, ..., 2024)
- Compute Fleiss' kappa using `statsmodels.stats.inter_rater.fleiss_kappa`
- Interpretation: κ>0.60 = substantial agreement, κ>0.80 = almost perfect agreement

**Expected Performance:** κ=0.65-0.75 (substantial agreement for high-confidence subset)

**Comparison Value:**  
Fleiss' kappa controls for chance agreement, providing stronger validation than raw percentage. If κ<0.40 (fair agreement) but raw agreement >70%, consensus may be inflated by clustering around obvious dates (e.g., everyone guesses 2020 for ImageNet due to ViT publicity).

---

## 4. Experiment Implementation Plan

### 4.1 Data Preparation Tasks

| Task ID | Description | Dependencies | Estimated Effort |
|---------|-------------|--------------|------------------|
| DP-01 | Design survey instrument (Qualtrics/Google Forms) | None | 2 hours |
| DP-02 | Pilot survey with 5-10 researchers (sanity check) | DP-01 | 3 hours |
| DP-03 | Distribute survey (PWC forum, Reddit, mailing lists) | DP-02 | 1 hour |
| DP-04 | Monitor responses, send reminders (week 1-3) | DP-03 | 2 hours |
| DP-05 | Download survey data via Google Forms API | DP-04 | 1 hour |
| DP-06 | Clean data (deduplication, quality filters) | DP-05 | 2 hours |
| DP-07 | Validate sample size (≥30 high-conf/benchmark) | DP-06 | 1 hour |

**Total Data Preparation:** ~12 hours hands-on + 2-3 weeks calendar time for collection

### 4.2 Environment Setup Tasks

| Task ID | Description | Dependencies | Estimated Effort |
|---------|-------------|--------------|------------------|
| ENV-01 | Install dependencies (pandas, scipy, statsmodels) | None | 0.5 hours |
| ENV-02 | Download Google Forms API credentials | None | 0.5 hours |
| ENV-03 | Create data/ directory structure | None | 0.25 hours |

**Total Environment Setup:** ~1.25 hours

### 4.3 Core Implementation Tasks

| Task ID | Description | Dependencies | Estimated Effort |
|---------|-------------|--------------|------------------|
| IMPL-01 | Load survey data from CSV/JSON | ENV-01, DP-06 | 1 hour |
| IMPL-02 | Filter high-confidence responses (≥4/5) | IMPL-01 | 1 hour |
| IMPL-03 | Compute modal saturation date per benchmark | IMPL-02 | 1 hour |
| IMPL-04 | Calculate raw agreement rate (±1 year window) | IMPL-03 | 2 hours |
| IMPL-05 | Compute Fleiss' kappa (statsmodels) | IMPL-02 | 2 hours |
| IMPL-06 | Bootstrap confidence intervals (1000 iterations) | IMPL-04 | 2 hours |
| IMPL-07 | Generate permutation null distribution | IMPL-03 | 2 hours |
| IMPL-08 | Visualize agreement distributions (histogram + CI) | IMPL-04, IMPL-06 | 2 hours |
| IMPL-09 | Export results table (agreement%, kappa, n per benchmark) | IMPL-04, IMPL-05 | 1 hour |

**Total Core Implementation:** ~14 hours

### 4.4 Validation Tasks

| Task ID | Description | Dependencies | Estimated Effort |
|---------|-------------|--------------|------------------|
| VAL-01 | Verify sample size meets threshold (n≥30) | IMPL-02 | 0.5 hours |
| VAL-02 | Check domain stratification balance | IMPL-01 | 0.5 hours |
| VAL-03 | Sanity check: modal dates plausible (2017-2024) | IMPL-03 | 0.5 hours |
| VAL-04 | Compare kappa vs. raw agreement (detect inflation) | IMPL-04, IMPL-05 | 1 hour |
| VAL-05 | Statistical significance test (p<0.05 vs. null) | IMPL-07 | 1 hour |

**Total Validation:** ~3.5 hours

### 4.5 Task Complexity Summary

| Category | Task Count | Total Effort |
|----------|------------|--------------|
| Data Preparation | 7 | 12 hours + 2-3 weeks collection |
| Environment Setup | 3 | 1.25 hours |
| Core Implementation | 9 | 14 hours |
| Validation | 5 | 3.5 hours |
| **Total** | **24** | **~31 hours (+ collection time)** |

**Tier Classification:** Tier 2 (Medium Complexity)
- Rationale: Real-world data collection adds calendar time but code implementation is straightforward statistical analysis

---

## 5. Success Metrics & Validation

### 5.1 Primary Validation Criteria

**P1: Agreement Rate**
- Metric: Percentage of high-confidence responses within ±1 year of modal date
- Threshold: >70% per benchmark
- Measurement: `(n_within_window / n_total_high_conf) * 100`

**P2: Sample Size**
- Metric: Number of high-confidence (≥4/5) responses
- Threshold: ≥30 per benchmark
- Measurement: `len(df[df['confidence'] >= 4])`

**P3: Chance-Adjusted Agreement**
- Metric: Fleiss' kappa
- Threshold: κ>0.60 (substantial agreement)
- Measurement: `statsmodels.stats.inter_rater.fleiss_kappa(response_matrix)`

### 5.2 Secondary Validation Criteria

**S1: Statistical Significance**
- Test: Permutation test against null distribution
- Threshold: p<0.05 (observed agreement significantly exceeds chance)

**S2: Domain Balance**
- Metric: Vision vs. NLP response ratio
- Threshold: 40-60% split (tolerable imbalance)

**S3: Consistency Across Benchmarks**
- Metric: Agreement rate variance across ImageNet/GLUE/SQuAD
- Threshold: Agreement rate std <15% (similar consensus strength across benchmarks)

### 5.3 Failure Modes & Mitigations

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Low response rate (n<30) | Sample size check | Extend collection 1-2 weeks, add distribution channels |
| Weak agreement (<50%) | Agreement rate calculation | PIVOT to citation-based validation (SOTA decay) |
| High raw agreement but low kappa | Kappa vs. raw comparison | Investigate clustering around obvious dates (e.g., ViT 2021) |
| Domain imbalance (>70% one domain) | Stratification check | Targeted outreach to underrepresented domain |

---

## 6. Expected Outcomes

### 6.1 Hypothesis Pass Scenario

**Gate Status:** SATISFIED  
**Evidence:**
- ImageNet: 78% agreement (n=42 high-conf), modal date=2019-Q2, κ=0.71
- GLUE: 73% agreement (n=38 high-conf), modal date=2020-Q1, κ=0.68
- SQuAD: 75% agreement (n=35 high-conf), modal date=2019-Q4, κ=0.69

**Interpretation:**  
Expert consensus exists and is statistically robust (>70% agreement, substantial kappa). Ground truth validated — proceed to algorithmic detection (H-M1, H-M2) with confidence. Modal saturation dates (2019-2020) provide validation anchor for dual-metric detector.

**Next Steps:**
- Use modal dates as ground truth for H-M1 (score convergence) and H-M2 (velocity decay) validation
- Publish expert consensus dates as benchmark lifecycle metadata (contribution to community)

### 6.2 Hypothesis Fail Scenario

**Gate Status:** FAILED  
**Evidence:**
- ImageNet: 48% agreement (n=31 high-conf), no clear modal date, κ=0.38
- GLUE: 52% agreement (n=29 high-conf), wide date spread (2018-2023), κ=0.41
- SQuAD: 45% agreement (n=33 high-conf), bimodal distribution, κ=0.35

**Interpretation:**  
Expert consensus weak or absent. Community lacks shared understanding of saturation timing. Ground truth validation via expert opinion is not viable.

**Pivot Strategy:**
- Abandon expert survey validation
- IMPLEMENT citation-based validation (A1 fallback):
  - Scrape "main results" citations for each benchmark from recent papers (2018-2024)
  - Detect saturation as citation frequency decay (<50% year-over-year for 2 consecutive years)
  - Compare algorithmic detection dates vs. citation decay dates (±1 year alignment)
- Downgrade validation claim from "expert consensus" to "publication usage patterns"

### 6.3 Partial Pass Scenario

**Gate Status:** CONDITIONALLY SATISFIED  
**Evidence:**
- ImageNet: 72% agreement (n=41 high-conf), κ=0.66 — PASS
- GLUE: 58% agreement (n=32 high-conf), κ=0.52 — WEAK
- SQuAD: 48% agreement (n=28 high-conf, below threshold), κ=0.42 — FAIL

**Interpretation:**  
Mixed results — ImageNet has strong consensus (vision community agreement), GLUE/SQuAD weaker (NLP domain more fragmented or benchmarks less clearly saturated).

**Adjusted Strategy:**
- Proceed with ImageNet validation (vision domain only)
- Use citation-based fallback for GLUE/SQuAD (NLP domain)
- Document domain-specific differences in saturation consensus (contribution: vision benchmarks have clearer lifecycle endpoints than NLP)

---

## 7. Research Impact & Contribution

### 7.1 Immediate Contribution

**Ground Truth Dataset:**  
If consensus validated (>70% agreement), publish expert consensus saturation dates as community resource:
- ImageNet saturation: 2019-Q2 ±1 year (expert consensus)
- GLUE saturation: 2020-Q1 ±1 year
- SQuAD saturation: 2019-Q4 ±1 year

**Methodological Contribution:**  
Demonstrate that expert consensus can serve as validation anchor for automated detection systems (analogous to human-labeled datasets for supervised learning).

### 7.2 Broader Impact

**If Consensus Strong (>70%):**  
- Validates saturation as community-recognized phenomenon (not just isolated researcher observations)
- Provides reference standard for evaluating rotation infrastructure proposals (benchmarks with weak consensus may not need rotation)

**If Consensus Weak (<50%):**  
- Reveals benchmark lifecycle blindspot in ML community (lack of shared understanding when benchmarks exhaust)
- Motivates need for automated detection infrastructure (community cannot manually coordinate transitions)

### 7.3 Limitations & Caveats

**Survey Bias:**
- Response bias: Researchers with strong opinions about saturation more likely to respond
- Recency bias: Experts may anchor on recent paradigm shifts (ViT 2021, GPT-3 2020) rather than true saturation dates
- Survivorship bias: Only benchmarks that survived 2018-2024 included (excludes early-abandoned benchmarks)

**Generalization:**
- Limited to 3 benchmarks (ImageNet, GLUE, SQuAD) — may not generalize to newer benchmarks (MMLU, BIG-Bench)
- Vision/NLP only — excludes RL, robotics, multimodal benchmarks

**Temporal Validity:**
- Expert consensus measured in 2026 (retrospective) — may differ from real-time consensus during saturation (2019-2020)
- Memory decay: Experts may not accurately recall 2019 community sentiment

---

## 8. Implementation Code Snippets

### 8.1 Data Loading & Filtering

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.inter_rater import fleiss_kappa

# Load survey data
df = pd.read_csv('data/expert_survey_responses.csv')

# Filter high-confidence responses
high_conf = df[df['confidence'] >= 4].copy()

# Check sample size per benchmark
for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
    n = len(high_conf[high_conf['benchmark'] == benchmark])
    print(f"{benchmark}: n={n} high-confidence responses")
    if n < 30:
        print(f"  WARNING: Sample size below threshold (n<30)")
```

### 8.2 Agreement Rate Calculation

```python
def calculate_agreement(responses, window_months=12):
    """
    Calculate agreement rate: % of responses within ±window of modal date.
    
    Args:
        responses: pd.Series of saturation dates (datetime)
        window_months: tolerance window (default ±12 months)
    
    Returns:
        agreement_rate (float), modal_date (datetime)
    """
    # Find modal saturation date
    modal_date = responses.mode()[0]
    
    # Count responses within ±window
    lower = modal_date - pd.DateOffset(months=window_months)
    upper = modal_date + pd.DateOffset(months=window_months)
    within_window = ((responses >= lower) & (responses <= upper)).sum()
    
    agreement_rate = (within_window / len(responses)) * 100
    return agreement_rate, modal_date

# Apply per benchmark
for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
    bench_df = high_conf[high_conf['benchmark'] == benchmark]
    rate, modal = calculate_agreement(bench_df['saturation_date'])
    print(f"{benchmark}: {rate:.1f}% agreement, modal={modal.strftime('%Y-%m')}")
```

### 8.3 Fleiss' Kappa Calculation

```python
def prepare_kappa_matrix(df, benchmark):
    """
    Convert survey responses to Fleiss' kappa input format.
    
    Format: rows=items (experts), cols=categories (year buckets)
    Each cell = count of experts assigning that category
    """
    bench_df = df[df['benchmark'] == benchmark].copy()
    
    # Discretize dates into year buckets
    bench_df['year_bucket'] = bench_df['saturation_date'].dt.year
    
    # Create count matrix (experts × year buckets)
    year_range = range(2017, 2025)  # 2017-2024
    matrix = []
    
    for expert_id in bench_df['expert_id'].unique():
        expert_row = [0] * len(year_range)
        expert_year = bench_df[bench_df['expert_id'] == expert_id]['year_bucket'].values[0]
        year_idx = year_range.index(expert_year)
        expert_row[year_idx] = 1
        matrix.append(expert_row)
    
    return np.array(matrix)

# Compute kappa per benchmark
for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
    matrix = prepare_kappa_matrix(high_conf, benchmark)
    kappa = fleiss_kappa(matrix, method='fleiss')
    print(f"{benchmark}: Fleiss' κ = {kappa:.3f}")
    
    # Interpret
    if kappa > 0.80:
        interpretation = "almost perfect agreement"
    elif kappa > 0.60:
        interpretation = "substantial agreement"
    elif kappa > 0.40:
        interpretation = "moderate agreement"
    else:
        interpretation = "fair or poor agreement"
    print(f"  Interpretation: {interpretation}")
```

### 8.4 Bootstrap Confidence Intervals

```python
def bootstrap_agreement(responses, window_months=12, n_iterations=1000):
    """
    Estimate 95% CI for agreement rate via bootstrap resampling.
    """
    agreement_rates = []
    
    for _ in range(n_iterations):
        # Resample with replacement
        sample = responses.sample(n=len(responses), replace=True)
        rate, _ = calculate_agreement(sample, window_months)
        agreement_rates.append(rate)
    
    # Compute 95% CI
    ci_lower = np.percentile(agreement_rates, 2.5)
    ci_upper = np.percentile(agreement_rates, 97.5)
    
    return ci_lower, ci_upper

# Apply per benchmark
for benchmark in ['ImageNet', 'GLUE', 'SQuAD']:
    bench_df = high_conf[high_conf['benchmark'] == benchmark]
    rate, modal = calculate_agreement(bench_df['saturation_date'])
    ci_low, ci_high = bootstrap_agreement(bench_df['saturation_date'])
    print(f"{benchmark}: {rate:.1f}% agreement (95% CI: {ci_low:.1f}%-{ci_high:.1f}%)")
```

---

## 9. References & Prior Art

### 9.1 Benchmark Saturation Literature

- **When AI Benchmarks Plateau: A Systematic Study of Benchmark Saturation** (2026). ArXiv preprint analyzing 60 benchmarks, finding 48% exhibit saturation. Empirical foundation for saturation prevalence.
  - URL: https://arxiv.org/html/2602.16763v1

- **Large Language Model Benchmarks: A Taxonomy of Capabilities, Scientific Quality Assessment, and Saturation Analysis** (2024). Survey of 63 LLM benchmarks spanning 2012-2026, documenting declining discriminative power for frontier models.
  - URL: https://doi.org/10.3390/make8060141

### 9.2 Inter-Rater Agreement Methods

- **Cohen's Kappa in Python** (Statology tutorial). Practical guide to implementing Cohen's kappa using scikit-learn.
  - URL: https://www.statology.org/cohens-kappa-python/

- **GitHub: heolin/agreement** (Python library). Implementation of Cohen's kappa, Fleiss' kappa, Krippendorff's alpha for inter-rater reliability.
  - URL: https://github.com/heolin/agreement

- **GitHub: sophiedkk/pyirr** (Python package). Coefficients of interrater reliability for interval, ordinal, and nominal data.
  - URL: https://github.com/sophiedkk/pyirr

### 9.3 Expert Survey Design

- **Inter-rater agreement and reliability of the COSMIN Checklist** (2010). NCBI PMC article demonstrating expert consensus validation methodology for measurement instruments.
  - URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2957386/

---

## 10. Archon Integration

### 10.1 Task Hierarchy Mapping

**Epic-Level Task (Phase 3):** "Validate Expert Consensus for Benchmark Saturation (h-c1)"

**Subtasks (Data Preparation):**
- DP-01: Design survey instrument
- DP-02: Pilot survey
- DP-03: Distribute survey
- DP-04: Monitor responses
- DP-05: Download data
- DP-06: Clean data
- DP-07: Validate sample size

**Subtasks (Environment Setup):**
- ENV-01: Install dependencies
- ENV-02: Configure Google Forms API
- ENV-03: Create data directories

**Subtasks (Core Implementation):**
- IMPL-01 through IMPL-09 (see Section 4.3)

**Subtasks (Validation):**
- VAL-01 through VAL-05 (see Section 4.4)

### 10.2 Archon Document References

**PRD (to be created in Phase 3):**
- Feature: Expert consensus validation module
- User story: As a researcher, I want to validate that benchmark saturation dates have expert consensus, so I can trust algorithmic detection results.

**Architecture (to be created in Phase 3):**
- Component: Survey data ingestion pipeline (Google Forms API → CSV → pandas DataFrame)
- Component: Statistical analysis module (agreement rate, Fleiss' kappa, bootstrap CI)
- Component: Visualization module (agreement distributions, confidence intervals)

**Logic Specification (to be created in Phase 3):**
- Function: `calculate_agreement(responses, window_months) -> (rate, modal_date)`
- Function: `fleiss_kappa_benchmark(df, benchmark) -> kappa`
- Function: `bootstrap_ci(responses, n_iter) -> (ci_lower, ci_upper)`

**Configuration (to be created in Phase 3):**
- `CONFIDENCE_THRESHOLD = 4` (minimum confidence rating for inclusion)
- `AGREEMENT_WINDOW_MONTHS = 12` (±1 year tolerance)
- `MIN_SAMPLE_SIZE = 30` (per benchmark)
- `AGREEMENT_THRESHOLD = 0.70` (70% agreement criterion)
- `KAPPA_THRESHOLD = 0.60` (substantial agreement criterion)

---

## 11. Experiment Scale & Timeline

### 11.1 Computational Requirements

**Minimal Compute:**
- Survey data analysis: single-core CPU sufficient
- Memory: <1GB (survey data ~10-50 KB)
- Runtime: <5 minutes for all analyses (agreement, kappa, bootstrap)

**No GPU Required:**  
This is purely statistical analysis (no deep learning).

### 11.2 Calendar Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Survey design & pilot | 3-5 days | None |
| Data collection | 2-3 weeks | Survey distribution |
| Data cleaning & validation | 1-2 days | Data collection complete |
| Statistical analysis | 1 day | Clean data available |
| Results interpretation | 1 day | Analysis complete |
| **Total** | **~4 weeks** | **Including collection time** |

### 11.3 Critical Path

**Longest pole:** Data collection (2-3 weeks calendar time)

**Mitigation:**
- Start collection early (immediately after survey design)
- Parallel development: implement analysis code while collecting data
- Weekly reminders to boost response rate

---

## 12. Experiment Brief Summary

**What we're testing:**  
Does expert consensus on benchmark saturation timing exist and is it measurable (>70% agreement)?

**How we're testing it:**  
Survey 50+ ML researchers about ImageNet/GLUE/SQuAD saturation dates, measure agreement rate and Fleiss' kappa among high-confidence responses.

**Why it matters:**  
Without validated ground truth, algorithmic saturation detection (H-M1, H-M2) cannot be evaluated. This is the foundation hypothesis (MUST_WORK gate).

**What happens if it fails:**  
PIVOT to citation-based validation (SOTA mention decay) instead of expert opinion.

**Key deliverable:**  
Expert consensus saturation dates (if validated) or citation-based validation strategy (if consensus weak).

**Effort estimate:**  
~31 hours implementation + 2-3 weeks data collection.

**Experiment type:**  
Real-world survey data collection + statistical validation (NOT synthetic).

---

**Document Status:** COMPLETE  
**Ready for Phase 3:** YES  
**Archon Integration:** Pending (Phase 3 will generate PRD/Architecture/PRP)
