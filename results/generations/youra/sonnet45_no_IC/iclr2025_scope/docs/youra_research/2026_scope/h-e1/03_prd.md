# Product Requirements Document: H-E1 Benchmark Data Collection

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis:** H-E1 (EXISTENCE)
**Status:** Draft

---

## Executive Summary

### Purpose
Validate the existence and accessibility of sufficient benchmark data for meta-method selector research by systematically collecting method rankings from target benchmark suites (OGB, FedML, LEAF, pFL-Bench, Champneys, Zhou, Papers with Code).

### Success Criteria
- Collect ≥50 benchmarks with complete baseline comparisons
- Achieve domain diversity: ≥10 benchmarks in ≥3 domains (vision, time-series, tabular, graph)
- Ensure 100% data completeness (all benchmarks have ≥3 methods with rankings)

### Hypothesis Statement
Under supervised learning literature mining from target benchmark suites, if we systematically extract method rankings from published papers, then at least 50 benchmarks with complete baseline comparisons will be collected, because these suites collectively provide diverse coverage across vision, time-series, tabular, and graph domains.

---

## Problem Statement

### Background
Meta-method selector research requires aggregated benchmark results to train meta-classifiers that predict which method families perform well on new datasets. The viability of this approach depends on whether sufficient benchmark data with complete method rankings exists and can be collected from literature.

### Current State
- Phase 2C experiment design completed
- Target benchmark suites identified: OGB (15), FedML (6), LEAF (5), pFL-Bench (8), Champneys (5), Zhou (9), Papers with Code (10+)
- No existing aggregated collection available

### Problem
Unknown whether target benchmark suites provide:
1. Sufficient total benchmarks (≥50)
2. Domain diversity (≥3 domains with ≥10 benchmarks each)
3. Complete method rankings (no missing data)

### Gate Condition
**MUST_WORK gate:** If <50 benchmarks collected, entire meta-method selector hypothesis chain fails (H-M1-4, H-C1 all depend on this data).

---

## Functional Requirements

### FR-1: OGB Graph Benchmark Collection
**Priority:** HIGH | **Complexity:** MEDIUM

**Description:** Extract graph benchmark data from Open Graph Benchmark (OGB) using the official `ogb` Python library.

**Acceptance Criteria:**
- [ ] Install `ogb` library
- [ ] Query API for 15 target datasets (ogbn-arxiv, ogbn-products, ogbn-proteins, etc.)
- [ ] Extract dataset metadata: sample size, dimensionality, num_classes
- [ ] Extract published method rankings from OGB leaderboards
- [ ] Classify methods into families: Linear, Polynomial, RNN, Augmentation
- [ ] Store in standardized schema with ≥3 methods per benchmark
- [ ] Handle API errors with retry logic

**Input:** OGB dataset names list
**Output:** List of graph benchmark records with method rankings

**Dependencies:** None
**Estimated Effort:** 3-4 hours

---

### FR-2: FedML/LEAF/pFL-Bench GitHub Repository Parsing
**Priority:** HIGH | **Complexity:** MEDIUM

**Description:** Parse published results from federated learning benchmark repositories on GitHub.

**Acceptance Criteria:**
- [ ] Clone/download FedML, LEAF, pFL-Bench repositories
- [ ] Parse README files and result tables
- [ ] Extract benchmark metadata and method performance
- [ ] Standardize data schema across sources
- [ ] Handle missing values and incomplete tables
- [ ] Collect ≥19 benchmarks total (FedML: 6, LEAF: 5, pFL-Bench: 8)

**Input:** GitHub repository URLs
**Output:** List of federated learning benchmark records

**Dependencies:** None
**Estimated Effort:** 4-5 hours

---

### FR-3: Papers with Code API Query
**Priority:** MEDIUM | **Complexity:** LOW

**Description:** Query Papers with Code API for leaderboard data across target domains.

**Acceptance Criteria:**
- [ ] Authenticate with Papers with Code API
- [ ] Query leaderboards filtered by domains: vision, nlp, graph
- [ ] Extract top methods per benchmark
- [ ] Filter benchmarks with ≥3 methods
- [ ] Map method names to families
- [ ] Collect ≥10 additional benchmarks

**Input:** Domain filters, API credentials
**Output:** List of benchmark records from Papers with Code

**Dependencies:** None
**Estimated Effort:** 2-3 hours

---

### FR-4: Manual Paper Extraction (Champneys, Zhou)
**Priority:** MEDIUM | **Complexity:** HIGH

**Description:** Manually extract benchmark results from specific papers (Champneys NLSI, Zhou Medical FL) where no API access exists.

**Acceptance Criteria:**
- [ ] Download PDF files for target papers
- [ ] Extract result tables from papers
- [ ] Transcribe benchmark metadata and method rankings
- [ ] Validate data completeness manually
- [ ] Collect ≥14 benchmarks (Champneys: 5, Zhou: 9)

**Input:** Paper PDFs, result table screenshots
**Output:** List of manually extracted benchmark records

**Dependencies:** None
**Estimated Effort:** 5-6 hours

---

### FR-5: Data Schema Standardization
**Priority:** HIGH | **Complexity:** LOW

**Description:** Transform all collected benchmark data into a unified schema for meta-classifier training.

**Acceptance Criteria:**
- [ ] Define standard benchmark record schema (JSON)
- [ ] Required fields: benchmark_id, dataset_name, domain, sample_size, dimensionality, num_classes, method_rankings, source_paper, year
- [ ] Implement transformation functions for each data source
- [ ] Validate all records against schema
- [ ] Handle missing fields with defaults or exclusion

**Input:** Raw benchmark data from all sources
**Output:** Standardized JSON collection

**Dependencies:** FR-1, FR-2, FR-3, FR-4
**Estimated Effort:** 2-3 hours

---

### FR-6: Data Validation and Quality Checks
**Priority:** HIGH | **Complexity:** LOW

**Description:** Validate collected data against success criteria before proceeding to meta-classifier training.

**Acceptance Criteria:**
- [ ] Count total benchmarks collected
- [ ] Calculate domain distribution
- [ ] Check data completeness (≥3 methods per benchmark)
- [ ] Verify no duplicate benchmarks
- [ ] Generate validation report
- [ ] PASS if: total≥50 AND domains_with_10+≥3 AND completeness=100%

**Input:** Standardized benchmark collection
**Output:** Validation report with PASS/FAIL decision

**Dependencies:** FR-5
**Estimated Effort:** 1-2 hours

---

### FR-7: Visualization Generation
**Priority:** MEDIUM | **Complexity:** LOW

**Description:** Generate visualizations for data collection results and validation.

**Acceptance Criteria:**
- [ ] Bar chart: Benchmark count by domain
- [ ] Pie chart: Benchmark sources breakdown
- [ ] Stacked bar: Method family distribution
- [ ] Heatmap: Data completeness by source
- [ ] Save figures to `{hypothesis_folder}/figures/`

**Input:** Validated benchmark collection
**Output:** PNG figure files

**Dependencies:** FR-6
**Estimated Effort:** 2 hours

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** HIGH

- Collection script must be deterministic (same inputs → same outputs)
- Document all API versions and access dates
- Store raw data before transformation
- Version control collection code

### NFR-2: Error Handling
**Priority:** HIGH

- Retry failed API calls (max 3 attempts)
- Log unavailable sources without failing entire collection
- Continue collection if one source fails
- Generate partial results report

### NFR-3: Performance
**Priority:** MEDIUM

- Total collection time: <2 hours
- Optional: Parallelize API calls for speed
- Cache downloaded data to avoid redundant queries

### NFR-4: Data Privacy
**Priority:** LOW (public benchmark data)

- Use only publicly available benchmark data
- No private or restricted datasets
- Cite all data sources in output

---

## Data Requirements

### Input Data
1. **OGB Library Access**
   - Method: `pip install ogb`
   - Data: Public OGB leaderboards

2. **GitHub Repositories**
   - FedML: https://github.com/FedML-AI/FedML
   - LEAF: https://github.com/TalwalkarLab/leaf
   - pFL-Bench: (URL from Phase 2C)

3. **Papers with Code API**
   - Endpoint: https://paperswithcode.com/api/v1/
   - Authentication: Public API (no key required for basic access)

4. **Research Papers**
   - Champneys NLSI paper (PDF)
   - Zhou Medical FL paper (PDF)

### Output Data Schema
```json
{
  "benchmark_id": "string (unique identifier)",
  "dataset_name": "string",
  "domain": "vision | time-series | tabular | graph",
  "sample_size": "integer",
  "dimensionality": "integer",
  "num_classes": "integer",
  "method_rankings": {
    "method_name": {
      "family": "Linear | Polynomial | RNN | Augmentation",
      "accuracy": "float",
      "ranking_percentile": "float (0-100)"
    }
  },
  "source_paper": "string (citation)",
  "year": "integer"
}
```

### Storage
- Format: JSON Lines (`.jsonl`)
- Location: `{hypothesis_folder}/benchmarks_collection.jsonl`
- Estimated Size: 50-100 KB

---

## Dependencies and Integration

### External Dependencies
1. **Python Libraries:**
   - `ogb>=1.3.0` - OGB dataset access
   - `requests>=2.28.0` - HTTP API calls
   - `pandas>=1.5.0` - Data aggregation
   - `beautifulsoup4>=4.11.0` - HTML parsing
   - `matplotlib>=3.6.0` - Visualization
   - `seaborn>=0.12.0` - Statistical plots

2. **Data Sources:**
   - OGB API (online)
   - GitHub repositories (online, can be cached)
   - Papers with Code API (online)
   - Research papers (PDFs, manual download)

### Internal Dependencies
None (standalone data collection, no dependency on other modules)

### Integration Points
**Output to:** Phase 3 Architecture (defines data pipeline structure)
**Output to:** Phase 4 Implementation (executes collection script)
**Output to:** H-M1 (uses collected data for meta-classifier training)

---

## Success Criteria

### Quantitative Metrics
1. **Total Benchmarks:** ≥50 collected
2. **Domain Diversity:** ≥10 benchmarks in ≥3 domains
3. **Data Completeness:** 100% (all benchmarks have ≥3 methods)

### Qualitative Criteria
1. Data validates successfully against schema
2. No duplicate benchmarks
3. Method family classifications are correct
4. Source citations are complete

### Validation Method
Execute FR-6 validation checks. PASS condition:
```python
success = (total_count >= 50 and 
           domains_above_10 >= 3 and 
           completeness == 100)
```

### Gate Decision
- **PASS (≥50 benchmarks):** Proceed to H-M1 (meta-classifier training)
- **PARTIAL (40-49 benchmarks):** Explore additional sources, retry
- **FAIL (<40 benchmarks):** ABANDON entire meta-method selector hypothesis

---

## Constraints and Assumptions

### Constraints
1. **Time:** Collection must complete within 2 hours
2. **Resources:** Single machine, no GPU required
3. **Access:** Only public data sources (no paywalled papers)
4. **Budget:** LIGHT tier (minimal infrastructure: 15 tasks max)

### Assumptions
1. Target benchmark suites have public API/GitHub access
2. Published papers contain extractable result tables
3. Method names can be mapped to 4 families
4. Benchmark metadata is available or can be inferred

### Risks
1. **API Unavailability:** Papers with Code API might require authentication or rate-limit
   - Mitigation: Use GitHub alternatives, manual extraction fallback
2. **Incomplete Data:** Some benchmarks might lack method rankings
   - Mitigation: Exclude incomplete benchmarks, document exclusion rate
3. **Domain Imbalance:** One domain might dominate (e.g., 40 graph, 10 vision)
   - Mitigation: Document imbalance, note limitation for meta-classifier generalization

---

## Implementation Notes

### Recommended Implementation Order
1. FR-1: OGB Collection (API-based, most reliable)
2. FR-2: GitHub Parsing (well-documented repositories)
3. FR-3: Papers with Code (API might require troubleshooting)
4. FR-5: Schema Standardization (consolidate early sources)
5. FR-6: Validation (check if target met before manual work)
6. FR-4: Manual Extraction (only if needed to reach 50)
7. FR-7: Visualization (after validation passes)

### LIGHT Tier Infrastructure Guidance
- **Configuration:** Hardcoded source URLs in collection script (no YAML config)
- **Logging:** `print()` statements + CSV log file (no WandB)
- **Testing:** Smoke test (run on 2 sources, verify schema) - no unit tests
- **Code Structure:** Single `collect_benchmarks.py` script (~200-300 lines)

### Phase 4 Coding Notes
- This is NOT a training experiment - no model, no optimizer, no GPU
- Primary file: `collect_benchmarks.py`
- Secondary file: `validate_collection.py`
- Output files: `benchmarks_collection.jsonl`, `validation_report.txt`

---

## Appendix

### A. Phase 2C Traceability

| Phase 2C Section | PRD Mapping |
|------------------|-------------|
| Dataset → Aggregated Benchmark Collection | FR-1, FR-2, FR-3, FR-4 |
| Data Schema | FR-5, Data Requirements |
| Success Criteria → ≥50 benchmarks | Success Criteria |
| Validation Protocol → evaluate_collection() | FR-6 |
| Visualization Requirements → 4 figures | FR-7 |
| Gate Condition → MUST_WORK | Problem Statement, Success Criteria |

### B. Task Budget Allocation Preview

**LIGHT Tier: 15 tasks max**

| Category | Tasks | Allocation |
|----------|-------|------------|
| Data Preparation | 2 | Install dependencies, Setup folders |
| Environment Setup | 2 | Verify API access, Clone repos |
| Epic Tasks (FR-1 to FR-7) | 7 | One per FR |
| Subtasks | 3 | Sub-collections, Transformations |
| Failsafe/Documentation | 1 | README, Citation file |

**Total: 15 tasks** (at LIGHT tier budget limit)

### C. Related Documents

- **Input:** `02c_experiment_brief.md` (Phase 2C)
- **Next:** `03_architecture.md` (Phase 3 Step 3)
- **Pipeline:** Verification Plan `02b_verification_plan.md`

---

**Document Status:** Ready for Architecture Design (Step 3)
**Next Phase:** Phase 3 Step 3 - Architecture Agent spawning
