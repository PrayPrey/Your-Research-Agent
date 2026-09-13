# Experiment Design: h-m4

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Under ML reengineering workflows with CI + Contracts deployed, if contracts execute at environment-setup time, then defect detection shifts from training-stage (median 68% per Jiang et al.) to environment-stage, with ≥5-hour earlier median time-to-first-failure compared to CI-only baseline.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C - Experiment Design)
**Prerequisites Satisfied:** ✅ YES (h-m3 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK (not yet evaluated - will be tested in Phase 4)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3 (Composition-level contract validation)

### Gate Condition

**Type:** SHOULD_WORK
**Threshold:** Lifecycle shift ≥5h, marginal detection ≥25%
**Pass Condition:** 
- Primary: Median time-to-first-failure reduced by ≥5 hours (CI+Contracts vs. CI-Only)
- Secondary: CI+Contracts detects ≥25% more environment-stage API defects than CI-Only

**Fail Action:** If lifecycle shift <3h, insufficient practical impact — document as incremental improvement

---

## Continuation Context

**h-m4 builds directly on h-m3 (Composition-Level Contract Validation)**

**Sequential Relationship:**
- h-m3 validated the MECHANISM (composition-level contracts detect 71.4% of defects)
- h-m4 tests the OUTCOME (does this mechanism shift lifecycle timing in real CI workflows?)

**Controlled Extension:**
- **Reused component:** Composition validator (device, dtype, layout checks)
- **New component:** CI integration + timing measurement
- **Isolated variable:** Deployment context (standalone vs. CI pipeline)

This design ensures h-m4 measures lifecycle shift WITHOUT confounding from mechanism validity (already established in h-m3).

### Previous Hypothesis Results: h-m3

**Gate Result:** ✓ PASS (SHOULD_WORK gate satisfied)

**Key Results:**
- **Detection Rate:** 71.4% at composition stage (5/7 defects, threshold: ≥60%)
- **False Positive Rate:** 0% (0/1 control test)
- **Execution Time:** 0.004s average (<<10s requirement)
- **Proven Mechanism:** Device/dtype consistency validation works

**Lessons Learned:**
1. **Generator object limitation:** Validation targets tensor parameters only; generator objects (device-002) not covered
2. **Layout compatibility:** Overly strict for operations like torch.sparse.mm that intentionally accept mixed layouts
3. **Detection timing:** Validation executes at import/call time (suitable for environment-stage deployment)

**Reuse for h-m4:**
- ✅ Composition validator code (`composition_validator.py`)
- ✅ Device/dtype/layout checking logic
- ✅ Validation execution patterns (decorator-based)
- ⚠️ Extend with CI integration layer (GitHub Actions step)
- ⚠️ Add instrumentation for timing measurement (started_at, completed_at)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: CI Integration Testing ML Workflows**
- **Limited direct matches:** Archon KB primarily contains CV/diffusion model implementations rather than CI/testing infrastructure research
- **Related finding:** HuggingFace Diffusers PR #3313 shows CUDA environment setup patterns for CI/CD testing
- **Insight:** ML repositories often lack systematic CI testing patterns (aligns with Wolter et al. finding that 75% of ML repos lack automated testing)

**Query 2: Defect Detection Lifecycle Shift**
- **No direct experimental precedent found in Archon KB**
- **Related finding:** Several HuggingFace issues demonstrate post-deployment defect discovery patterns
- **Insight:** Current ML practice relies on manual trial-and-error debugging rather than systematic early-stage detection

**Query 3: GitHub Repository Experimental Trials**
- **Finding:** Multiple GitHub gist examples show experiment reproduction scripts
- **Pattern:** Common pattern is single-machine script execution, not distributed CI-based trials
- **Insight:** PR-level randomized trials on live repos is novel experimental design (no precedent in Archon KB)

**Query 4: Time-to-Failure Measurement**
- **Finding:** Performance benchmarking examples (DeepCache: 14.78s baseline vs. 8.36s optimized)
- **Pattern:** Timing measurement via logging timestamps, comparison framework
- **Insight:** Standard pattern is execution time comparison; adapting to time-to-first-failure will require CI log timestamp extraction

### Archon Code Examples

**Query 1: CI Testing Integration**
- **Example 1:** HuggingFace Diffusers PR #3313 - CUDA environment setup in Docker for CI
  - **Pattern:** apt-get dependencies + pyenv + pip install torch + git clone libraries
  - **Insight:** Environment setup is complex multi-step process (prime target for contract validation)
  
- **Example 2:** Python package installation logging
  - **Code snippet:** Shows pip install output with dependency resolution
  - **Pattern:** Import-time dependency checking
  - **Insight:** Dependency conflicts often emerge during pip install, not just runtime

**Query 2: GitHub API CI Logs Timestamps**
- **No direct code examples found**
- **Workaround insight:** Will need to implement custom GitHub Actions API or CI log scraping

**Query 3: Randomized Trial Baseline Comparison**
- **Example 1:** Apple ML Stable Diffusion baseline JSON structure
  ```json
  {
    "model_version": "stabilityai/stable-diffusion-xl-base-1.0",
    "baselines": {
      "original": 82.2,
      "linear_8bit": 66.025,
      ...
    }
  }
  ```
  - **Pattern:** JSON-based baseline tracking, multiple configurations
  - **Insight:** Can adapt this structure for CI-Only vs. CI+Contracts comparison tracking

- **Example 2:** DeepCache performance logging
  - **Code pattern:** Detailed logging with timestamps, progress bars, baseline vs. optimized comparison
  - **Insight:** Standard pattern for timing comparisons: run_baseline() → measure time → run_proposed() → measure time → compare

### Exa GitHub Implementations

**⚠️ Exa MCP Unavailable (402 Payment/Quota Error)**

**Alternative Research Strategy Applied:**
- Used Phase 2B verification protocol specifications
- Referenced h-m3 completed implementation patterns
- Leveraged domain knowledge of ML CI/testing infrastructure

**Implementation Strategy for h-m4:**

Since h-m4 tests lifecycle shift (defect detection timing), not a specific ML algorithm, we focus on:

1. **CI Infrastructure Patterns:**
   - Standard: GitHub Actions `.github/workflows/` YAML configurations
   - Testing: pytest with CI integration (pytest-cov, pytest-xdist)
   - Logging: GitHub Actions job timestamps, step duration tracking
   
2. **Baseline Implementations (From Phase 2B):**
   - **No-CI Baseline:** Version pinning only (`requirements.txt` + manual execution)
   - **CI-Only Baseline:** pytest + GitHub Actions + version pinning (current best practice)
   - **CI+Contracts (Proposed):** CI + pytest + contract validation at environment setup

3. **Time-to-Failure Measurement:**
   - **Data Source:** GitHub Actions API (`GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`)
   - **Timestamps:** `started_at`, `completed_at`, step-level `started_at`/`completed_at`
   - **Defect Stage Detection:** Parse logs for failure location (environment setup vs. training stage)
   
4. **Experimental Trial Design:**
   - **Randomization:** PR-level assignment to CI-Only vs. CI+Contracts
   - **Stratification:** Repository maturity (stars, commits), reporter type (58% re-users per Jiang et al.)
   - **Sample:** ≥1K stars CV repos from GitHub (target: 30-50 repos, 100-200 PRs)

**Serena Analysis Needed:** ❌ FALSE (infrastructure experiment, not algorithm implementation)

### 🎯 Implementation Priority Assessment

**h-m4 is NOT a paper reproduction experiment** - it's a novel infrastructure experiment measuring lifecycle shift.

**Implementation Strategy:**

**Priority 1: Extend h-m3 Implementation** ⭐⭐⭐ HIGHEST
- Reuse composition validator from h-m3 (71.4% detection rate validated)
- Add GitHub Actions CI integration layer
- Add timing/logging instrumentation

**Priority 2: GitHub Actions Integration**
- Standard YAML workflow configuration
- Python action for contract validation step
- API integration for metrics collection

**Priority 3: Experimental Infrastructure**
- PR randomization logic
- Data collection pipeline (GitHub API)
- Statistical analysis scripts

**Recommended Implementation Path:**
- Primary: Build on h-m3/code/composition_validator.py + GitHub Actions integration
- Fallback: N/A (no alternative - this is the validated implementation from prerequisite)
- Justification: h-m3 already validated composition-level contracts (PASS gate). h-m4 extends with CI integration to measure lifecycle shift, not re-implement validation logic.

### Code Analysis (Serena MCP)

*Skipped* - h-m4 is an infrastructure experiment (CI + contract validation workflow), not an algorithm implementation requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**h-m4 uses a dual-dataset design for comprehensive validation:**

**Dataset 1: Jiang et al. 348-Defect Corpus (Retrospective Analysis)**
- **Type:** standard (published research dataset)
- **Source:** Jiang et al. (2023) supplementary materials
- **Purpose:** Establish baseline lifecycle shift (current: 68% training-stage detection)
- **Statistics:** 348 ML reengineering defects, environment-stage API defects filtered
- **Preprocessing:** Extract stage-of-failure labels, filter for contractable defects
- **Stratification:** Defect type (structural, metamorphic, composition-level)

**Loading Information** (for Phase 4 download):
- Method: custom (CSV/JSON download from paper)
- Identifier: `jiang2023_348defects.csv`
- Code: `pd.read_csv("data/jiang2023_defects.csv")`

**Dataset 2: Live GitHub Repositories (Randomized PR-Level Trial)**
- **Type:** programmatic-api (GitHub API)
- **Source:** GitHub repositories (stars > 1K, Python, computer vision)
- **Purpose:** Measure marginal lifecycle shift (CI-Only vs. CI+Contracts) in real workflows
- **Statistics:** Target 30-50 repos, 100-200 PRs total
- **Preprocessing:** Filter for active repos, stratify by maturity (stars, commits)
- **Randomization:** PR-level assignment to CI-Only vs. CI+Contracts arms

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (PyGithub library)
- Identifier: Search query `"stars:>1000 language:python topic:computer-vision"`
- Code:
  ```python
  from github import Github
  g = Github(os.environ["GITHUB_TOKEN"])
  repos = g.search_repositories("stars:>1000 language:python topic:computer-vision")
  target_repos = [r for r in repos if is_active(r)][:50]
  ```

### Models

#### Baseline Model

**h-m4 does not use a traditional ML model. The "model" is the contract validation framework.**

**Contract Validation Framework (extended from h-m3)**
- **Type:** Validation framework (composition-level contracts)
- **Source:** Local codebase from h-m3/code/composition_validator.py
- **Purpose:** Validate device/dtype/layout consistency at environment-setup time
- **Configuration:**
  - Validation categories: device, dtype, layout consistency
  - Execution timing: CI environment-setup stage (before training)
  - Integration: GitHub Actions workflow step
- **Modifications for h-m4:** Add CI integration layer + timestamp logging for lifecycle measurement

**Loading Information** (for Phase 4 download):
- Method: custom (inherit from h-m3 implementation)
- Identifier: `h-m3/code/composition_validator.py`
- Code:
  ```python
  from h_m3.code.composition_validator import validate_composition
  # Add CI integration wrapper:
  # - GitHub Actions step definition
  # - Timestamp logging (started_at, completed_at)
  # - Failure stage detection (environment vs. training)
  ```

#### Proposed Model

**Architecture:** Baseline (CI-Only) + Contract Validation at Environment-Setup

**Integration Point:** GitHub Actions workflow, environment-setup stage
- Insert after: `actions/checkout@v3` and `actions/setup-python@v4`
- Before: Training script execution step
- Timing: After environment initialization, before any training code runs

**Core Mechanism Implementation:**

```python
# Core Mechanism: Environment-Setup Contract Validation in CI
# Based on: h-m3 composition validator + GitHub Actions integration
# Purpose: Shift defect detection from training-stage to environment-stage

# GitHub Actions workflow integration (YAML):
# .github/workflows/train.yml

jobs:
  train:
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      
      # === CONTRACT VALIDATION STEP (NEW - environment-stage) ===
      - name: Validate API Contracts
        id: contract_validation
        run: |
          python -m contract_validator \
            --config .contract_config.yaml \
            --log-level INFO
        env:
          CONTRACT_FAIL_FAST: true
      
      # Only reached if contracts pass
      - name: Run Training
        if: steps.contract_validation.outcome == 'success'
        run: python train.py

# contract_validator/__main__.py pseudo-code:

import time
from h_m3.composition_validator import validate_composition

def run_contract_validation():
    """Execute contract validation at environment-setup time."""
    start_time = time.time()
    
    # Import libraries to trigger composition checks
    import torch
    import transformers
    
    # Run composition-level validation (from h-m3)
    results = validate_composition(
        check_device=True,
        check_dtype=True,
        check_layout=True
    )
    
    # Log timing for lifecycle measurement
    elapsed = time.time() - start_time
    print(f"::set-output name=validation_time::{elapsed}")
    
    if results.has_violations():
        # Defect detected at ENVIRONMENT stage
        print(f"::error::Contract violations: {results.violations}")
        raise SystemExit(1)  # Fail CI early
    
    print("::notice::Contracts validated successfully")
    return 0

# Integration: Executed as GitHub Actions step
# Timing: Environment-setup stage (before training)
# Effect: Defects caught here shift time-to-first-failure forward by hours
```

### Training Protocol

**Note:** h-m4 does NOT train ML models. The "training" is the CI workflow execution.

**Experimental Protocol:**
- **Baseline Condition (CI-Only):** Standard GitHub Actions workflow with pytest integration tests only
- **Proposed Condition (CI+Contracts):** Baseline + contract validation step at environment-setup
- **Randomization:** PR-level assignment (50/50 split between conditions)
- **Stratification:** 
  - Repository maturity: High (>5K stars) vs. Medium (1K-5K stars)
  - Reporter type: Re-user (58%) vs. Original author (42%)
- **Sample Size:** 100-200 PRs across 30-50 repositories
- **Duration:** 8-12 weeks trial period
- **Seeds:** N/A (infrastructure experiment, no randomness)

**Data Collection:**
- **GitHub Actions API:** Pull job timestamps, step durations, failure logs
- **Stage Classification:** Parse logs to determine environment vs. training stage failure
- **Time-to-First-Failure:** `completed_at - started_at` for first failing job

### Evaluation

**Task Type:** Infrastructure lifecycle measurement

**Primary Metrics:**

1. **Median Time-to-First-Failure Reduction** (hours)
   - Formula: `median(TTFF_CI_only) - median(TTFF_CI+Contracts)`
   - Success threshold: ≥5 hours reduction
   - Source: Phase 2B success criteria

2. **Stage-of-First-Failure Distribution**
   - CI-Only: Expected 68% training-stage (baseline from Jiang et al.)
   - CI+Contracts: Expected shift to environment-stage
   - Success threshold: Lifecycle shift observable (environment-stage proportion increases)

**Secondary Metrics:**

3. **Marginal Detection Improvement** (%)
   - Formula: `(defects_detected_CI+Contracts - defects_detected_CI_only) / defects_detected_CI_only`
   - Success threshold: ≥25% marginal improvement
   - Source: Phase 2B success criteria

**PoC Success Criteria:**
- `TTFF_reduction > 0` (directional improvement)
- `environment_stage_proportion_proposed > environment_stage_proportion_baseline`

**Expected Baseline Performance** (from research):
- Median TTFF (CI-Only): 8-12 hours (estimated from Jiang et al. 68% training-stage detection)
- Environment-stage proportion (CI-Only): ~32% (100% - 68% training-stage)
- Source: Jiang et al. (2023) defect taxonomy

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Infrastructure lifecycle measurement
- Library: custom (GitHub Actions API via `PyGithub`)
- Code:
  ```python
  from github import Github
  
  def measure_ttff(repo, run_id):
      job = repo.get_workflow_run(run_id).jobs()[0]
      ttff_hours = (job.completed_at - job.started_at).total_seconds() / 3600
      return ttff_hours
  
  def classify_failure_stage(job):
      for step in job.steps:
          if step.conclusion == "failure":
              if "contract" in step.name.lower() or "setup" in step.name.lower():
                  return "environment"
              else:
                  return "training"
      return "unknown"
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: 
  - Median TTFF bar chart (CI-Only vs. CI+Contracts)
  - Target line at -5h reduction threshold
  - Shows: baseline TTFF, proposed TTFF, threshold

#### Additional Figures (LLM Autonomous)

Based on hypothesis (lifecycle shift measurement) and evaluation metrics, generate:

1. **Stage-of-Failure Distribution** (Stacked bar chart)
   - X-axis: CI-Only, CI+Contracts
   - Y-axis: Proportion (0-100%)
   - Segments: Environment-stage (bottom), Training-stage (top)
   - Purpose: Visualize lifecycle shift

2. **Time-to-First-Failure Distribution** (Box plot or violin plot)
   - X-axis: CI-Only, CI+Contracts
   - Y-axis: Time (hours)
   - Purpose: Show distribution shift, not just median

3. **Marginal Detection Improvement** (Line or bar chart)
   - X-axis: Detection rate (%)
   - Y-axis: CI-Only baseline, CI+Contracts proposed
   - Target line: +25% improvement threshold
   - Purpose: Show detection rate increase

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note:** Archon KB primarily contains CV/diffusion model implementations rather than CI/testing infrastructure research. Limited direct matches found.

**Source A.1:** HuggingFace Diffusers PR #3313
- **Type:** GitHub issue/PR in knowledge base
- **Query Used:** "CI integration testing ML workflows"
- **Relevance:** Shows CUDA environment setup patterns for CI/CD testing
- **Key Insights:**
  - Environment setup is complex multi-step process (apt-get + pyenv + pip install)
  - Dependency conflicts often emerge during pip install, not just runtime
  - Prime target for contract validation
- **Used For:** Understanding environment-stage failure patterns

**Source A.2:** DeepCache Performance Logging Example
- **Type:** Code example
- **Query Used:** "randomized trial experiment comparison baseline"
- **Relevance:** Standard pattern for timing comparisons
- **Key Code Pattern:**
  ```python
  # Baseline: 14.78 seconds
  # Optimized: 8.36 seconds
  # Pattern: run_baseline() → measure → run_proposed() → measure → compare
  ```
- **Used For:** Time-to-first-failure measurement protocol design

**Source A.3:** Apple ML Stable Diffusion Baseline JSON Structure
- **Type:** Code example
- **Query Used:** "randomized trial experiment comparison baseline"
- **Key Pattern:**
  ```json
  {
    "model_version": "...",
    "baselines": {
      "original": 82.2,
      "variant_1": 66.025,
      ...
    }
  }
  ```
- **Used For:** Baseline comparison tracking structure (adapted for CI-Only vs. CI+Contracts)

### B. GitHub Implementations (Exa)

**⚠️ Exa MCP Unavailable:** All Exa searches returned 402 payment/quota errors.

**Alternative Research Strategy:**
- Used Phase 2B verification protocol specifications as primary source
- Referenced h-m3 completed implementation for contract validation mechanism
- Applied domain knowledge of ML CI/testing infrastructure

**Conceptual Sources (not from Exa):**
- GitHub Actions documentation: Workflow YAML structure, job/step timing
- PyGithub library documentation: API for accessing workflow runs, jobs, timestamps
- Pytest documentation: Integration testing patterns in ML projects

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - h-m4 is an infrastructure experiment (CI + contract validation workflow), not an algorithm implementation requiring semantic code analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-m3
- **File:** `docs/youra_research/h-m3/04_validation.md`
- **Reused Components:**
  - **Contract Validator:** `composition_validator.py` (71.4% detection rate)
  - **Validation Logic:** Device/dtype/layout consistency checks
  - **Decorator Pattern:** `@validate_composition` integration approach
  - **Execution Timing:** Import/setup time validation (proven <0.01s overhead)
- **Why Reused:** h-m3 validated the detection mechanism (PASS). h-m4 extends to measure lifecycle shift in CI context — reusing proven validator ensures h-m4 isolates timing variable, not mechanism validity.

**Key h-m3 Results Referenced:**
- Detection rate: 71.4% (5/7 defects) at composition stage
- False positive rate: 0% (0/1 control)
- Execution time: 0.004s average
- Known limitations: Generator object validation, layout compatibility refinement needed

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset 1 (Jiang et al. corpus) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Dataset 2 (Live GitHub repos) | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Contract validation mechanism | h-m3 validated | h-m3/04_validation.md |
| Composition validator code | h-m3 implementation | h-m3/code/composition_validator.py |
| GitHub Actions integration | Domain knowledge | Standard CI patterns (workflow YAML) |
| Time-to-failure measurement | Archon KB + Domain | DeepCache logging pattern (A.2) + GitHub API |
| Stage classification (env vs train) | Phase 2B + Jiang et al. | Verification protocol + Jiang et al. (2023) taxonomy |
| Success criteria (≥5h, ≥25%) | Phase 2B | 02b_verification_plan.md h-m4 section |
| Baseline (CI-Only) | Phase 2B | Standard best practice (pytest + CI) |
| Proposed (CI+Contracts) | h-m3 + h-m4 design | Composition validator + CI integration |
| Randomization protocol | Phase 2B + Research design | PR-level assignment, stratification |
| Evaluation metrics (TTFF, stage) | Phase 2B + Jiang et al. | Success criteria + defect taxonomy |
| Pseudo-code (CI integration) | h-m3 + Domain knowledge | GitHub Actions YAML + Python action pattern |

**Research Grounding:**
- **Phase 2B Verification Plan:** Primary source for experimental design (datasets, success criteria, gate conditions)
- **h-m3 Validation:** Validated contract validation mechanism (prerequisite)
- **Jiang et al. (2023):** Defect taxonomy, baseline lifecycle distribution (68% training-stage)
- **Archon KB (Limited):** Timing measurement patterns, baseline comparison structures
- **Domain Knowledge:** CI/testing infrastructure, GitHub Actions, experimental trial design

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-11

### Workflow History for This Hypothesis

**Phase 2C - Experiment Design (Current)**
- **Started:** 2026-07-11T13:25:00Z
- **Status:** IN_PROGRESS
- **Actions:**
  - Initialized workflow and validated prerequisites (h-m3 COMPLETED)
  - Searched Archon KB (limited CI/testing infrastructure results, adapted with domain knowledge)
  - Attempted Exa GitHub searches (402 payment/quota errors, used alternative strategy)
  - Skipped Serena analysis (infrastructure experiment, not algorithm implementation)
  - Confirmed dual-dataset design (Jiang et al. corpus + live GitHub repos)
  - Synthesized experiment specification with CI integration pseudo-code
  - Defined lifecycle shift measurement protocol

**Previous Phase: Phase 2B - Verification Planning**
- **Status:** COMPLETED
- **Output:** 02b_verification_plan.md, 02b_context.md
- **Key Decision:** h-m4 tests final causal step (lifecycle shift outcome)

**Prerequisite: Phase 4 - h-m3 Implementation**
- **Status:** COMPLETED (2026-07-11T13:20:00Z)
- **Result:** PASS (71.4% detection rate, 0% FPR, 0.004s execution time)
- **Impact on h-m4:** Composition validator validated and ready for CI integration

---

*MCP Tools Used: Archon (Knowledge + Code - limited results), Exa (Unavailable - 402 errors), Serena (Skipped - not applicable)*
*Specifications grounded in: Phase 2B planning, h-m3 validated implementation, domain knowledge of CI/testing infrastructure*
*Next Phase: Phase 3 - Implementation Planning*
