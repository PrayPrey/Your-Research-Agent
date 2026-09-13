# Product Requirements Document (PRD)

**Hypothesis:** h-m4  
**Type:** MECHANISM  
**Date:** 2026-07-11  
**Author:** Anonymous  
**Version:** 1.0  

---

## Executive Summary

### Problem Statement

ML reengineering workflows currently experience median 68% training-stage defect detection (Jiang et al., 2023), leading to delayed time-to-first-failure and increased debugging costs. While h-m3 validated that composition-level contracts can detect 71.4% of defects at composition stage, the practical impact on lifecycle timing in real CI workflows remains unquantified.

### Solution Overview

Integrate composition-level contract validation (proven in h-m3) into GitHub Actions CI workflows at environment-setup time to shift defect detection from training-stage to environment-stage. This implementation measures the lifecycle shift impact through:

1. **Retrospective Analysis:** Apply contracts to Jiang et al. 348-defect corpus to establish baseline shift
2. **Prospective Trial:** Randomized PR-level trial on live GitHub repositories (CI-Only vs. CI+Contracts)

### Success Criteria

**Gate Type:** SHOULD_WORK

**Primary Criteria:**
- Median time-to-first-failure reduced by ≥5 hours (CI+Contracts vs. CI-Only)

**Secondary Criteria:**
- CI+Contracts detects ≥25% more environment-stage API defects than CI-Only

**Fail Action:**
- If lifecycle shift <3 hours: Document as incremental improvement

---

## Functional Requirements

### FR-1: Contract Validator Extension (from h-m3)

**Priority:** P0 (Critical)  
**Source:** h-m3/code/composition_validator.py

**Requirements:**
1.1. Reuse composition validator from h-m3 with proven 71.4% detection rate  
1.2. Maintain device/dtype/layout consistency checks  
1.3. Preserve <0.01s execution time overhead  
1.4. Support decorator-based integration pattern  

**Acceptance Criteria:**
- All 5/7 defects from h-m3 still detected
- Zero false positives maintained (0/1 control)
- Execution time remains <10ms average

### FR-2: GitHub Actions CI Integration

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Core Mechanism Implementation"

**Requirements:**
2.1. Implement GitHub Actions workflow YAML configuration  
2.2. Add contract validation step between environment-setup and training  
2.3. Fail CI early if contract violations detected  
2.4. Support GitHub Actions native output syntax (`::set-output`, `::error`)  

**Acceptance Criteria:**
- Workflow step executes after `actions/setup-python@v4`
- Training step skipped if validation fails
- Failure logs show contract violation details

### FR-3: Timing Instrumentation

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Training Protocol - Data Collection"

**Requirements:**
3.1. Log `started_at` timestamp at workflow start  
3.2. Log `completed_at` timestamp at failure detection  
3.3. Calculate time-to-first-failure in hours  
3.4. Export timestamps to GitHub Actions outputs  

**Acceptance Criteria:**
- Timestamps accurate to second precision
- TTFF calculation handles timezone-aware datetime
- Metrics exportable via GitHub Actions API

### FR-4: Failure Stage Classification

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Evaluation - Stage-of-First-Failure Distribution"

**Requirements:**
4.1. Parse CI logs to determine failure location  
4.2. Classify as "environment" if failure in setup/contract steps  
4.3. Classify as "training" if failure in training script  
4.4. Handle edge cases (timeout, infra failure) as "unknown"  

**Acceptance Criteria:**
- Classification accuracy ≥95% on labeled test set
- Unknown category used for <5% of failures
- Stage label stored with TTFF metric

### FR-5: Dataset 1 - Retrospective Corpus Analysis

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Dataset 1: Jiang et al. 348-Defect Corpus"

**Requirements:**
5.1. Download and parse Jiang et al. supplementary materials  
5.2. Filter for environment-stage contractable defects  
5.3. Apply h-m3 contract validator to each defect scenario  
5.4. Measure baseline lifecycle shift (training → environment)  

**Acceptance Criteria:**
- All 348 defects processed
- Contractable defects filtered (estimated 30-50 cases)
- Per-defect TTFF reduction calculated

### FR-6: Dataset 2 - Live Repository Trial

**Priority:** P1 (High)  
**Source:** Phase 2C Section "Dataset 2: Live GitHub Repositories"

**Requirements:**
6.1. Search GitHub for repos: stars>1K, Python, computer vision topic  
6.2. Filter active repos (commits in last 6 months)  
6.3. Stratify by maturity: High (>5K stars) vs Medium (1K-5K stars)  
6.4. Target 30-50 repositories for trial  

**Acceptance Criteria:**
- Repository list includes ≥30 eligible repos
- Stratification balanced (50% high, 50% medium)
- All repos have active CI workflows

### FR-7: PR-Level Randomization

**Priority:** P1 (High)  
**Source:** Phase 2C Section "Training Protocol - Randomization"

**Requirements:**
7.1. Assign incoming PRs to CI-Only or CI+Contracts (50/50 split)  
7.2. Implement random assignment with stratification by repo maturity  
7.3. Track assignment in metadata database  
7.4. Prevent contamination (same PR doesn't switch arms)  

**Acceptance Criteria:**
- 50/50 split achieved within ±5% after 100 PRs
- Stratification variables balanced between arms
- Assignment persistence verified

### FR-8: CI-Only Baseline Arm

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Training Protocol - Baseline Condition"

**Requirements:**
8.1. Standard GitHub Actions workflow with pytest only  
8.2. No contract validation step  
8.3. Measure TTFF from job start to first failure  
8.4. Classify failure stage (environment vs training)  

**Acceptance Criteria:**
- Workflow mirrors current best practice
- TTFF measurement accurate
- Stage classification functional

### FR-9: CI+Contracts Proposed Arm

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Training Protocol - Proposed Condition"

**Requirements:**
9.1. Baseline workflow + contract validation step at environment-setup  
9.2. Contract step executes before training  
9.3. Fail fast on contract violations  
9.4. Measure TTFF including earlier environment-stage detection  

**Acceptance Criteria:**
- Contract step adds <10s to workflow
- Environment-stage detection functional
- TTFF shows expected reduction

### FR-10: GitHub Actions API Data Collection

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Training Protocol - Data Collection"

**Requirements:**
10.1. Use PyGithub library to access workflow run data  
10.2. Pull job timestamps (`started_at`, `completed_at`)  
10.3. Pull step-level timing and failure logs  
10.4. Store data in structured format (JSON/CSV)  

**Acceptance Criteria:**
- API rate limits handled gracefully
- Data collected for all trial PRs
- Timestamps timezone-consistent

### FR-11: Metric Calculation - Median TTFF Reduction

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Evaluation - Primary Metrics"

**Requirements:**
11.1. Calculate median TTFF for CI-Only arm  
11.2. Calculate median TTFF for CI+Contracts arm  
11.3. Compute reduction: `median(CI-Only) - median(CI+Contracts)`  
11.4. Test against ≥5 hour threshold  

**Acceptance Criteria:**
- Calculation handles missing data
- Statistical test (Mann-Whitney U) included
- Threshold comparison explicit

### FR-12: Metric Calculation - Marginal Detection Improvement

**Priority:** P1 (High)  
**Source:** Phase 2C Section "Evaluation - Secondary Metrics"

**Requirements:**
12.1. Count environment-stage defects detected by CI+Contracts  
12.2. Count environment-stage defects detected by CI-Only  
12.3. Calculate: `(Contracts - Only) / Only * 100`  
12.4. Test against ≥25% threshold  

**Acceptance Criteria:**
- Detection count excludes duplicates
- Percentage calculation correct
- Threshold comparison explicit

### FR-13: Visualization - Gate Metrics Comparison

**Priority:** P0 (Critical)  
**Source:** Phase 2C Section "Visualization Requirements - Required Figure"

**Requirements:**
13.1. Bar chart: CI-Only vs CI+Contracts median TTFF  
13.2. Horizontal line at -5h threshold  
13.3. Error bars showing 95% CI  
13.4. Save to `h-m4/figures/gate_metrics.png`  

**Acceptance Criteria:**
- Figure publication-ready (300 DPI)
- Threshold line clearly visible
- Labels clear and readable

### FR-14: Visualization - Stage-of-Failure Distribution

**Priority:** P1 (High)  
**Source:** Phase 2C Section "Visualization Requirements - Additional Figures"

**Requirements:**
14.1. Stacked bar chart: environment vs training stage  
14.2. X-axis: CI-Only, CI+Contracts  
14.3. Y-axis: Proportion (0-100%)  
14.4. Save to `h-m4/figures/stage_distribution.png`  

**Acceptance Criteria:**
- Proportions sum to 100% per arm
- Colors distinguish stages clearly
- Figure publication-ready

### FR-15: Visualization - TTFF Distribution

**Priority:** P1 (High)  
**Source:** Phase 2C Section "Visualization Requirements - Additional Figures"

**Requirements:**
15.1. Box plot or violin plot showing TTFF distributions  
15.2. X-axis: CI-Only, CI+Contracts  
15.3. Y-axis: Time (hours)  
15.4. Save to `h-m4/figures/ttff_distribution.png`  

**Acceptance Criteria:**
- Outliers visible
- Median marked clearly
- Distribution shape visible

---

## Non-Functional Requirements

### NFR-1: Performance

**Requirement:** Contract validation overhead <10 seconds per CI run  
**Rationale:** Minimize impact on developer experience  
**Measurement:** Mean validation time across all CI runs  

### NFR-2: Reliability

**Requirement:** CI integration false positive rate <5%  
**Rationale:** Avoid blocking legitimate PRs  
**Measurement:** FP rate = (false positives / total validations)  

### NFR-3: Scalability

**Requirement:** Support ≥200 PRs across 50 repositories  
**Rationale:** Achieve statistical power for lifecycle shift detection  
**Measurement:** Successful data collection from all trial PRs  

### NFR-4: Observability

**Requirement:** All failures logged with stage classification and timestamps  
**Rationale:** Enable post-hoc analysis and debugging  
**Measurement:** 100% of failures have complete metadata  

### NFR-5: Reproducibility

**Requirement:** Experiment setup reproducible via seed-controlled randomization  
**Rationale:** Enable replication and validation  
**Measurement:** Re-running with same seed produces identical PR assignments  

---

## Technical Constraints

### TC-1: GitHub Actions Environment

**Constraint:** Contract validation must run in standard GitHub Actions ubuntu-latest runner  
**Impact:** No custom Docker images requiring special permissions  
**Mitigation:** Use standard Python 3.9+ environment with pip-installable dependencies  

### TC-2: GitHub API Rate Limits

**Constraint:** 5000 requests/hour for authenticated API access  
**Impact:** Data collection may throttle with >200 PRs  
**Mitigation:** Implement exponential backoff and request caching  

### TC-3: Prerequisite Dependency

**Constraint:** h-m3 composition validator must be frozen (no modifications)  
**Impact:** Cannot fix h-m3 limitations (generator objects, layout compatibility)  
**Mitigation:** Document known limitations in validation report  

### TC-4: Trial Duration

**Constraint:** 8-12 week trial window to collect 100-200 PRs  
**Impact:** Late-stage implementation errors cannot be fixed mid-trial  
**Mitigation:** Pilot test on 5 PRs before full trial launch  

---

## Dependencies

### Internal Dependencies

**DEP-1: h-m3 Composition Validator** (COMPLETED)  
- Status: VALIDATED (PASS)  
- Deliverable: `h-m3/code/composition_validator.py`  
- Usage: Imported and extended with CI integration layer  

### External Dependencies

**DEP-2: Jiang et al. (2023) Defect Corpus**  
- Source: Supplementary materials from published paper  
- Format: CSV with defect taxonomy and stage-of-failure labels  
- Access: Public research data  

**DEP-3: GitHub API Access**  
- Service: GitHub REST API v3  
- Authentication: Personal Access Token with repo scope  
- Rate Limit: 5000 requests/hour  

**DEP-4: PyGithub Library**  
- Version: ≥1.59  
- Purpose: GitHub API client  
- Installation: `pip install PyGithub`  

**DEP-5: PyTorch Ecosystem**  
- Purpose: Target libraries for contract validation  
- Versions: PyTorch ≥2.0, transformers ≥4.30  
- Used by: Contract validator (from h-m3)  

---

## Data Requirements

### Dataset 1: Jiang et al. Retrospective Corpus

**Format:** CSV  
**Size:** 348 defects  
**Schema:**
- defect_id: unique identifier  
- stage_of_failure: environment | training | deployment  
- defect_type: structural | metamorphic | composition-level  
- description: defect scenario description  

**Processing:**
- Filter: environment-stage contractable defects  
- Expected yield: 30-50 defects  

### Dataset 2: Live Repository Trial

**Format:** Programmatic API (GitHub)  
**Size:** 30-50 repos, 100-200 PRs  
**Schema (collected via API):**
- repo_id, repo_name, stars, last_commit_date  
- pr_id, pr_number, created_at, arm_assignment  
- run_id, job_id, started_at, completed_at  
- failure_stage, ttff_hours  

**Storage:** SQLite database + CSV exports  

---

## Validation & Testing

### Unit Testing

**Coverage:** ≥80% for contract validator CI integration layer  
**Framework:** pytest  
**Key Test Cases:**
- Contract validation executes correctly in CI environment  
- Timing instrumentation captures accurate timestamps  
- Stage classification handles edge cases  

### Integration Testing

**Scope:** Full CI workflow end-to-end  
**Environment:** GitHub Actions test repository  
**Key Test Cases:**
- CI-Only arm workflow completes successfully  
- CI+Contracts arm detects known defects  
- GitHub API data collection pipeline functional  

### Pilot Testing

**Scope:** 5 PRs before full trial launch  
**Purpose:** Validate randomization, data collection, and failure handling  
**Success Criteria:**
- All 5 PRs assigned correctly  
- TTFF and stage data collected  
- No false positives  

---

## Success Metrics

### PoC Success (Directional Validation)

**Criteria:**
- Code runs without error  
- `TTFF_reduction > 0` (any improvement)  
- `environment_stage_proportion_proposed > baseline`  

### Gate Success (Threshold Validation)

**Primary:**
- Median TTFF reduction ≥5 hours  

**Secondary:**
- Marginal detection improvement ≥25%  

### Scientific Rigor

**Criteria:**
- Statistical significance: p < 0.05 (Mann-Whitney U test)  
- Effect size: Cohen's d ≥0.5 (medium effect)  
- Power analysis: 1-β ≥0.80 achieved  

---

## Timeline & Milestones

### Phase 3: Implementation Planning (Current)

**Duration:** 1 session  
**Deliverables:** PRD, Architecture, Logic, Config, Tasks  

### Phase 4: Coding & PoC Validation

**Duration:** 2-3 sessions  
**Deliverables:**
- Contract validator CI integration  
- GitHub Actions workflow templates  
- Data collection pipeline  
- Retrospective corpus analysis (Dataset 1)  
- Pilot test (5 PRs)  
- PoC validation report  

### Phase 4 (Extended): Live Trial Execution

**Duration:** 8-12 weeks  
**Deliverables:**
- 100-200 PRs collected  
- TTFF and stage data for both arms  
- Statistical analysis  
- Gate metrics validation  

---

## Risks & Mitigation

### RISK-1: Insufficient PR Volume

**Probability:** Medium  
**Impact:** High (underpowered statistical tests)  
**Mitigation:** Expand repository search to 100 candidates, accept 50 most active  

### RISK-2: GitHub API Rate Limiting

**Probability:** Medium  
**Impact:** Medium (delayed data collection)  
**Mitigation:** Implement request caching, distribute collection over trial duration  

### RISK-3: False Positive Contract Violations

**Probability:** Low (h-m3 achieved 0% FPR)  
**Impact:** High (invalidates trial by blocking valid PRs)  
**Mitigation:** Pilot test on 5 PRs first, monitor FPR continuously  

### RISK-4: Contamination Between Arms

**Probability:** Low  
**Impact:** Critical (invalidates causal inference)  
**Mitigation:** Strict PR-level assignment, no mid-trial arm switching  

---

## Appendix

### A. Baseline Performance Expectations

From Jiang et al. (2023):
- Median TTFF (CI-Only): 8-12 hours (estimated)  
- Environment-stage detection: ~32% (100% - 68% training-stage)  

From h-m3 validation:
- Composition-level detection rate: 71.4%  
- Execution time: 0.004s average  
- False positive rate: 0%  

### B. Hypothesis Dependency Chain

```
h-e1 → h-m1 → h-m2 → h-m3 (VALIDATED) → h-m4 (current)
```

h-m4 extends h-m3 from validation-in-isolation to validation-in-CI-workflow.

### C. Glossary

- **TTFF:** Time-to-First-Failure (hours from CI start to first detected defect)  
- **CI-Only:** Baseline arm with pytest integration tests only  
- **CI+Contracts:** Proposed arm with composition-level contract validation  
- **Environment-stage:** CI workflow phase before training script execution  
- **Training-stage:** CI workflow phase during training script execution  

---

**Document Status:** Draft (Phase 3 Step 2)  
**Next Step:** Architecture Design (Phase 3 Step 3)  
**Approval Required:** N/A (Research experiment, not production system)
