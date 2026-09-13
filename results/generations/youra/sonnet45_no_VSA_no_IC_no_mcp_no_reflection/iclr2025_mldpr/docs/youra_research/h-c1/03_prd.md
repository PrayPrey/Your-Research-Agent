# Product Requirements Document (PRD)
## Expert Consensus Validation System (h-c1)

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis ID:** h-c1  
**Author:** Anonymous  
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Purpose
Build a validation system that measures expert consensus on benchmark saturation timing for ImageNet, GLUE, and SQuAD benchmarks. The system validates the foundational assumption that measurable expert agreement (>70%) exists for saturation dates, providing ground truth for downstream algorithmic saturation detection.

### 1.2 Success Criteria
- **Primary**: ≥70% of high-confidence (≥4/5) responses fall within ±1 year of modal saturation date per benchmark
- **Secondary**: ≥30 high-confidence responses per benchmark (statistical power threshold)
- **Tertiary**: Fleiss' kappa >0.60 (substantial chance-adjusted agreement)

### 1.3 Hypothesis Gate
**Type**: MUST_WORK  
**Pass**: Proceed to H-M1/H-M2 with validated ground truth  
**Fail**: PIVOT to citation-based validation (SOTA mention decay analysis)

---

## 2. Problem Statement

### 2.1 Background
Algorithmic benchmark saturation detection systems require validated ground truth to measure performance. Without community consensus on when benchmarks saturated, detector accuracy cannot be evaluated.

### 2.2 Current Limitations
- No validated expert consensus dataset exists for major benchmark saturation dates
- Community understanding of saturation timing is assumed but unmeasured
- Lack of reference standard prevents validation of automated detection

### 2.3 Proposed Solution
Survey 50+ ML researchers across vision/NLP domains to establish consensus saturation dates for ImageNet, GLUE, and SQuAD. Measure agreement using raw percentage and chance-adjusted Fleiss' kappa.

---

## 3. Functional Requirements

### FR-1: Survey Data Collection
**Priority**: P0  
**Description**: Collect expert responses on benchmark saturation timing via Google Forms survey.

**Acceptance Criteria**:
- Survey instrument captures saturation date (year + month) for each of 3 benchmarks
- Confidence rating (1-5 scale) per response
- Metadata: research domain (vision/NLP), career stage
- ≥50 total responses collected
- Domain stratification: 40-60% vision/NLP split acceptable
- IP-based deduplication enabled

### FR-2: High-Confidence Response Filtering
**Priority**: P0  
**Description**: Filter survey responses to include only high-confidence (≥4/5) ratings for primary analysis.

**Acceptance Criteria**:
- Extract responses with confidence ≥4
- Exclude confidence=1 (very uncertain) responses
- Flag responses with <30s completion time (spam filter)
- Exclude impossible dates (saturation after 2024 for selected benchmarks)
- Verify ≥30 high-confidence responses per benchmark

### FR-3: Modal Saturation Date Calculation
**Priority**: P0  
**Description**: Compute most common saturation date per benchmark from high-confidence responses.

**Acceptance Criteria**:
- Calculate mode for each benchmark independently
- Handle ties by selecting earliest date
- Store modal date with benchmark identifier
- Support month-level granularity (YYYY-MM format)

### FR-4: Agreement Rate Measurement
**Priority**: P0  
**Description**: Calculate percentage of high-confidence responses within ±1 year of modal date.

**Acceptance Criteria**:
- Window: ±12 months from modal date
- Per-benchmark agreement rate calculation
- Overall agreement rate across all benchmarks
- Output format: percentage with 1 decimal precision

### FR-5: Fleiss' Kappa Calculation
**Priority**: P0  
**Description**: Compute chance-adjusted inter-rater agreement using Fleiss' kappa for categorical year buckets.

**Acceptance Criteria**:
- Discretize saturation dates into year buckets (2017-2024)
- Use statsmodels.stats.inter_rater.fleiss_kappa implementation
- Per-benchmark kappa values
- Interpretation labels: κ>0.80=almost perfect, κ>0.60=substantial, κ>0.40=moderate
- Handle edge cases: all raters agree → κ=1.0

### FR-6: Bootstrap Confidence Intervals
**Priority**: P1  
**Description**: Estimate 95% CI for agreement rate via bootstrap resampling (1000 iterations).

**Acceptance Criteria**:
- Resample with replacement from high-confidence responses
- 1000 bootstrap iterations
- Calculate 2.5th and 97.5th percentile for CI bounds
- CI width <15% indicates stable estimate

### FR-7: Null Hypothesis Baseline (Permutation Test)
**Priority**: P1  
**Description**: Generate random agreement baseline by shuffling responses to test statistical significance.

**Acceptance Criteria**:
- 1000 permutations of shuffled responses
- Compute agreement rate per permutation
- Calculate p-value: proportion of permutations with agreement ≥ observed
- Threshold: p<0.05 for significance
- Expected null agreement: <30%

### FR-8: Raw Agreement Baseline
**Priority**: P1  
**Description**: Calculate agreement rate using ALL responses (not just high-confidence) as weaker baseline.

**Acceptance Criteria**:
- Include all responses regardless of confidence
- Same ±1 year window
- Expected performance: 50-60% (weaker than high-conf subset)
- Use for comparison: high-conf agreement should exceed raw agreement

### FR-9: Results Visualization
**Priority**: P1  
**Description**: Generate plots for agreement distributions and confidence intervals.

**Acceptance Criteria**:
- Histogram: saturation date distribution per benchmark with modal date marker
- Agreement rate bar chart with 95% CI error bars
- Kappa comparison across benchmarks
- Save plots as PNG to results directory

### FR-10: Results Export
**Priority**: P0  
**Description**: Export summary table with agreement metrics per benchmark.

**Acceptance Criteria**:
- CSV format with columns: benchmark, n_high_conf, modal_date, agreement_rate, fleiss_kappa, ci_lower, ci_upper, p_value
- JSON format for programmatic access
- Markdown summary table for documentation

### FR-11: Data Quality Validation
**Priority**: P0  
**Description**: Validate survey data completeness and quality before analysis.

**Acceptance Criteria**:
- Check: no duplicate responses (IP-based)
- Check: all required fields present (date, confidence, domain)
- Check: dates within valid range (2017-2024)
- Check: sample size meets threshold (≥30 high-conf per benchmark)
- Fail fast with clear error messages if quality checks fail

### FR-12: Domain Stratification Check
**Priority**: P2  
**Description**: Verify response balance across vision/NLP domains.

**Acceptance Criteria**:
- Calculate vision:NLP ratio
- Acceptable range: 40-60% split
- Warn if imbalance exceeds threshold (>70% one domain)
- Display stratification summary in results

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Survey data loading: <5 seconds for 150 responses
- Statistical analysis runtime: <1 minute for all metrics
- Bootstrap CI calculation: <30 seconds (1000 iterations)
- Total execution time: <5 minutes end-to-end

### NFR-2: Reliability
- Handle missing data gracefully (skip incomplete responses)
- Validate all inputs before analysis
- Deterministic results (fix random seeds for permutation/bootstrap)
- Error messages include actionable guidance

### NFR-3: Usability
- Single command execution: `python validate_consensus.py --survey_data=survey.csv`
- Progress indicators for long-running operations (bootstrap, permutation)
- Human-readable summary report generated automatically
- Example data included for testing

### NFR-4: Maintainability
- Modular functions: one function per metric (agreement_rate, fleiss_kappa, etc.)
- Type hints for all function signatures
- Docstrings with mathematical definitions
- Unit tests for core statistical functions

### NFR-5: Data Privacy
- No personally identifiable information collected
- Survey classified as minimal-risk opinion research
- Only aggregate statistics reported (no individual responses)
- IP addresses used only for deduplication, not stored

---

## 5. Data Specifications

### 5.1 Input Data Schema

**Survey Response CSV Format**:
```csv
response_id,benchmark,saturation_year,saturation_month,confidence,domain,career_stage
1,ImageNet,2019,6,5,vision,faculty
2,ImageNet,2020,1,4,vision,phd_student
3,GLUE,2020,3,5,nlp,industry
...
```

**Fields**:
- `response_id`: int, unique identifier
- `benchmark`: str, one of {ImageNet, GLUE, SQuAD}
- `saturation_year`: int, 2017-2024
- `saturation_month`: int, 1-12
- `confidence`: int, 1-5 scale
- `domain`: str, one of {vision, nlp, other}
- `career_stage`: str, one of {phd_student, postdoc, industry, faculty, other}

### 5.2 Output Data Schema

**Results JSON Format**:
```json
{
  "ImageNet": {
    "n_total": 42,
    "n_high_conf": 42,
    "modal_date": "2019-06",
    "agreement_rate": 78.0,
    "fleiss_kappa": 0.71,
    "ci_lower": 73.5,
    "ci_upper": 82.1,
    "p_value": 0.001
  },
  "GLUE": {...},
  "SQuAD": {...}
}
```

---

## 6. Success Metrics

### 6.1 Primary Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Agreement Rate | >70% | Per-benchmark % within ±1 year |
| Sample Size | ≥30 | High-conf responses per benchmark |
| Fleiss' Kappa | >0.60 | Chance-adjusted agreement |

### 6.2 Secondary Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Statistical Significance | p<0.05 | Permutation test |
| Domain Balance | 40-60% | Vision:NLP ratio |
| Agreement Consistency | std<15% | Variance across benchmarks |

### 6.3 Gate Decision Logic
```
IF (agreement_rate > 0.70 AND sample_size >= 30 AND fleiss_kappa > 0.60):
    gate.satisfied = True
    action = "Proceed to H-M1/H-M2"
ELIF (agreement_rate < 0.50):
    gate.satisfied = False
    action = "PIVOT to citation-based validation"
ELSE:
    gate.satisfied = Partial
    action = "Mixed results - use ImageNet consensus, citation fallback for NLP"
```

---

## 7. Dependencies

### 7.1 External Dependencies
- **Google Forms API**: Survey data collection and download
- **Python Libraries**:
  - pandas (data manipulation)
  - scipy (statistical tests)
  - statsmodels (Fleiss' kappa)
  - numpy (numerical operations)
  - matplotlib (visualization)

### 7.2 Data Dependencies
- Survey responses: requires 2-3 weeks data collection
- No pretrained models required
- No large datasets required

### 7.3 Hypothesis Dependencies
**Prerequisites**: None (FOUNDATION hypothesis)  
**Blocks**: H-M1, H-M2, H-M3 (all mechanism hypotheses depend on validated ground truth)

---

## 8. Implementation Constraints

### 8.1 Time Constraints
- Data collection: 2-3 weeks calendar time
- Implementation: ~31 hours (24 tasks)
- Analysis execution: <5 minutes

### 8.2 Resource Constraints
- Compute: Single-core CPU sufficient
- Memory: <1GB
- Storage: <10MB (survey data ~50KB)
- No GPU required

### 8.3 Quality Constraints
- Code coverage: ≥80% for core statistical functions
- Documentation: all functions have docstrings with mathematical definitions
- Reproducibility: fixed random seeds for stochastic operations

---

## 9. Risks & Mitigations

### 9.1 Low Response Rate
**Risk**: Fewer than 30 high-confidence responses per benchmark  
**Likelihood**: Medium  
**Impact**: High (blocks hypothesis validation)  
**Mitigation**:
- Extend collection window by 1-2 weeks
- Add distribution channels (conference mailing lists)
- Lower confidence threshold to ≥3/5 if necessary

### 9.2 Weak Agreement
**Risk**: Agreement rate <50%, no clear consensus  
**Likelihood**: Medium  
**Impact**: High (hypothesis fails, pivot required)  
**Mitigation**:
- Pre-planned pivot to citation-based validation
- SOTA mention decay analysis (papers 2018-2024)
- Downgrade claim from "expert consensus" to "usage patterns"

### 9.3 Domain Imbalance
**Risk**: >70% responses from one domain (vision or NLP)  
**Likelihood**: Low  
**Impact**: Medium (reduces generalizability)  
**Mitigation**:
- Targeted outreach to underrepresented domain
- Report domain-specific results separately
- Document limitation in paper

### 9.4 Survey Bias
**Risk**: Response/recency/survivorship bias affects consensus  
**Likelihood**: High (inherent to survey method)  
**Impact**: Low (documented limitation)  
**Mitigation**:
- Acknowledge in limitations section
- Compare results to citation-based validation as cross-check
- Focus on relative consensus strength, not absolute dates

---

## 10. Out of Scope

- Collection of responses (manual task, not automated)
- IRB approval process (assumed minimal-risk exemption)
- Survey instrument design iteration (one pilot, then deploy)
- Extension to additional benchmarks beyond ImageNet/GLUE/SQuAD
- Real-time survey monitoring dashboard
- Automated reminder emails to non-responders

---

## 11. Timeline & Milestones

| Milestone | Duration | Dependencies |
|-----------|----------|--------------|
| Survey design & pilot | 3-5 days | None |
| Data collection | 2-3 weeks | Survey distribution |
| Implementation | 31 hours | None (parallel with collection) |
| Analysis execution | <1 hour | Data collection complete |
| Results interpretation | 1 day | Analysis complete |
| **Total** | **~4 weeks** | **Longest pole: data collection** |

---

## 12. Appendix

### 12.1 Hypothesis Context
**Parent**: H-E1 (expert consensus exists)  
**Type**: CONDITION  
**Gate**: MUST_WORK  
**Assumption Validated**: A1 (expert consensus measurable)

### 12.2 Pivot Strategy (If Failed)
**Citation-Based Validation**:
1. Scrape "main results" citations for each benchmark from papers (2018-2024)
2. Detect saturation as citation frequency decay (<50% YoY for 2 consecutive years)
3. Compare algorithmic detection dates vs. citation decay dates (±1 year alignment)
4. Downgrade validation claim to "publication usage patterns" instead of "expert consensus"

### 12.3 Research Contribution
**If Pass**: Ground truth dataset for saturation dates + methodological validation  
**If Fail**: Reveals benchmark lifecycle blindspot in ML community

### 12.4 Baseline Experiment Summary
| Baseline | Expected Performance | Purpose |
|----------|---------------------|---------|
| Null (permutation) | <30% agreement | Statistical significance test |
| Raw agreement | 50-60% agreement | Compare high-conf vs all responses |
| Fleiss' kappa | κ=0.65-0.75 | Chance-adjusted validation |

---

**Document Status**: Draft  
**Next Phase**: Architecture Design (Step 3)  
**Phase 3 Progress**: 2/10 steps complete
