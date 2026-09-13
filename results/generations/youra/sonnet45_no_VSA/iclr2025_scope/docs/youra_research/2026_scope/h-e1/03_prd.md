# Product Requirements Document (PRD)
# API Contract Validation Framework for ML Reengineering

---

**Document Control**

| Field | Value |
|-------|-------|
| **Project Name** | API Contract Validation Framework |
| **Hypothesis ID** | h-e1 |
| **Document Version** | 1.0 |
| **Date** | 2026-07-11 |
| **Author** | Anonymous |
| **Status** | Draft |

---

**Frontmatter**
```yaml
stepsCompleted: 10
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
gate_type: MUST_WORK
task_budget_tier: LIGHT
task_budget_total_max: 15
```

---

## Executive Summary

This PRD defines requirements for an API Contract Validation Framework to test the hypothesis that ≥40% of environment-stage API defects from Jiang et al.'s 348-defect corpus are expressible as lightweight executable contracts with ≤10s validation time and version stability across ±2 minor library releases.

**Primary Goal:** Validate assumption A1 that a sufficient proportion of real-world API defects can be expressed as executable contracts through retrospective coding analysis.

**Success Criteria:**
- Contractability rate ≥40% with 95% CI lower bound >35%
- Inter-rater reliability (Cohen's kappa) ≥0.7
- Contract execution time ≤10 seconds
- Version stability across ±2 minor releases

**Project Type:** Research proof-of-concept (EXISTENCE hypothesis)
**Timeline:** Single-phase retrospective analysis
**Scope:** Custom implementation combining PyTorch runtime assertions with contract testing patterns

---

## Problem Statement

### Background

Deep learning model reengineering faces significant environment-stage API defects. Jiang et al. (2023) documented 348 defects across 27 open-source DL projects, with 88% being interface defects. Current approaches rely on:
- Version pinning (brittle, no validation)
- Integration testing (15-20% coverage, Wolter et al. 2025)
- Ad-hoc repo-specific validation (not reusable)

### The Core Problem

**No systematic, cross-repo executable contract framework exists for ML library APIs** that can:
1. Express structural, metamorphic, and composition-level invariants
2. Execute validation in ≤10 seconds
3. Remain stable across library version changes
4. Provide sufficient coverage (≥40% of real defects)

### Why It Matters

- **Reproducibility Crisis:** 75% of ML repos lack adequate testing (Wolter et al. 2025)
- **Version Fragility:** Environment changes break 88% of reengineered models
- **Manual Burden:** Developers manually debug version conflicts without systematic validation
- **Research Gap:** No empirical measurement of what proportion of defects are contractable

### Who This Impacts

- ML researchers reengineering published models
- ML engineers maintaining production pipelines across library updates
- Tool developers building reproducibility infrastructure

---

## Functional Requirements

### FR-1: Defect Corpus Loading and Preprocessing

**Priority:** P0 (Critical)  
**Complexity:** Low

**Description:** Load and filter the Jiang et al. 348-defect corpus to extract environment-stage API defects.

**Acceptance Criteria:**
- Load defect data from GitHub repository: `wenxin-jiang/emse-cvreengineering-artifact`
- Filter for environment-stage defects only
- Extract API-related defects (structural, metamorphic, composition-level)
- Categorize defects by type using Jiang et al.'s taxonomy
- Output: Pandas DataFrame with columns: `defect_id`, `type`, `description`, `source_project`, `api_name`

**Inputs:**
- GitHub repository URL
- Defect classification criteria

**Outputs:**
- Filtered defect corpus (CSV or DataFrame)
- Defect statistics (total count, breakdown by type)

**Dependencies:** None

**Source:** Phase 2C Experiment Brief, Appendix B.6

---

### FR-2: Contract Generation - Structural Invariants

**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Generate executable contracts for structural invariants (tensor shapes, dtypes, device placement).

**Acceptance Criteria:**
- Parse defect description to extract structural constraints
- Generate PyTorch runtime assertions using `torch._check` and `TORCH_CHECK`
- Support tensor shape validation (e.g., `tensor.dim() == 2`)
- Support dtype validation (e.g., `tensor.dtype == torch.float32`)
- Support device placement validation (e.g., `tensor.device.type == 'cuda'`)
- Execution time ≤10 seconds per contract
- Return Contract object or None if not expressible

**Inputs:**
- Defect record (structural type)
- API documentation (for invariant extraction)

**Outputs:**
- StructuralContract object with `validate()` method
- Execution time measurement

**Dependencies:** FR-1

**Source:** PyTorch runtime assertions (B.4), tensor-shape-assert patterns (B.5)

---

### FR-3: Contract Generation - Metamorphic Invariants

**Priority:** P1 (High)  
**Complexity:** High

**Description:** Generate executable contracts for metamorphic properties (e.g., autocast mode, training/eval state).

**Acceptance Criteria:**
- Detect metamorphic property violations from defect descriptions
- Generate state-transition checks (e.g., model.training vs model.eval())
- Validate autocast behavior consistency
- Support before/after transformation assertions
- Execution time ≤10 seconds per contract
- Return Contract object or None if not expressible

**Inputs:**
- Defect record (metamorphic type)
- PyTorch API behavioral documentation

**Outputs:**
- MetamorphicContract object with `validate()` method
- Execution time measurement

**Dependencies:** FR-1

**Source:** PyTorch autocast validation (A.2), metamorphic testing literature

---

### FR-4: Contract Generation - Composition Invariants

**Priority:** P1 (High)  
**Complexity:** High

**Description:** Generate executable contracts for composition-level invariants (cross-library interactions, device consistency).

**Acceptance Criteria:**
- Detect cross-library interaction defects (PyTorch + CUDA, PyTorch + NumPy)
- Generate device consistency checks across library boundaries
- Validate data transfer between frameworks (e.g., NumPy → Torch conversion)
- Support multi-step composition validation
- Execution time ≤10 seconds per contract
- Return Contract object or None if not expressible

**Inputs:**
- Defect record (composition type)
- Multi-library API documentation

**Outputs:**
- CompositionContract object with `validate()` method
- Execution time measurement

**Dependencies:** FR-1

**Source:** CUDA device error patterns (A.2), pact-python composition patterns (B.1)

---

### FR-5: Contract Validation Execution

**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Execute generated contracts with timeout enforcement and error handling.

**Acceptance Criteria:**
- Execute contract with ≤10 second timeout using Python `signal.alarm()`
- Catch and log timeout violations
- Catch and log contract assertion failures
- Record execution time for each validation
- Support batch execution across multiple contracts
- Return validation result: PASS, FAIL, TIMEOUT, or NOT_EXPRESSIBLE

**Inputs:**
- Contract object
- Timeout threshold (default: 10 seconds)

**Outputs:**
- Validation result
- Execution time
- Error logs (if applicable)

**Dependencies:** FR-2, FR-3, FR-4

**Source:** apiwatch SLA validation patterns (B.3)

---

### FR-6: Retrospective Coding Protocol

**Priority:** P0 (Critical)  
**Complexity:** Medium

**Description:** Implement 2-coder independent coding process with 3-question filter for contractability assessment.

**Acceptance Criteria:**
- Randomize defect presentation order (fixed seed for reproducibility)
- Present each defect to 2 independent coders
- Apply 3-question filter per defect:
  1. Does a documented invariant exist? (parse library docs)
  2. Is it evaluable in ≤10s? (timeout enforcement)
  3. Is it version-stable across ±2 releases? (cross-version check)
- Record coder decisions (binary: contractable vs not contractable)
- Calculate inter-rater reliability (Cohen's kappa)
- Require kappa ≥0.7 before proceeding to final results

**Inputs:**
- Filtered defect corpus (FR-1)
- Library documentation (PyTorch, NumPy, CUDA)

**Outputs:**
- Coder 1 labels (binary array)
- Coder 2 labels (binary array)
- Cohen's kappa coefficient
- Disagreement cases for review

**Dependencies:** FR-1, FR-5

**Source:** Phase 2B verification protocol

---

### FR-7: Version Stability Testing

**Priority:** P1 (High)  
**Complexity:** High

**Description:** Validate contract stability across ±2 minor library versions (e.g., PyTorch 1.10, 1.11, 1.12).

**Acceptance Criteria:**
- Set up virtual environments for each library version
- Execute contracts against all 3 versions (baseline-1, baseline, baseline+1)
- Detect API signature changes, deprecation warnings, breaking changes
- Mark contract as version-stable only if passes in all 3 environments
- Record version-specific failure modes
- Output stability matrix (contract × version)

**Inputs:**
- Contract objects (from FR-2, FR-3, FR-4)
- Target library version ranges (e.g., PyTorch 1.11-1.13)

**Outputs:**
- Stability matrix (boolean: stable vs unstable per contract)
- Version-specific error logs
- Percentage of contracts passing version stability test

**Dependencies:** FR-5

**Source:** Phase 2C experiment brief (version stability requirement)

---

### FR-8: Contractability Rate Calculation

**Priority:** P0 (Critical)  
**Complexity:** Low

**Description:** Calculate contractability rate with 95% confidence intervals, stratified by defect category.

**Acceptance Criteria:**
- Calculate overall contractability rate: (contractable_count / total_defects) × 100
- Stratify by defect type: structural, metamorphic, composition
- Compute 95% confidence intervals using Wilson score method
- Display results in tabular format
- Check if CI lower bound >35% (gate condition)

**Inputs:**
- Coder agreement labels (from FR-6)
- Defect categories (from FR-1)

**Outputs:**
- Overall contractability rate (%)
- Stratified rates by type (%)
- 95% CI bounds (lower, upper)
- PASS/FAIL against gate condition

**Dependencies:** FR-6

**Source:** Phase 2C success criteria

---

### FR-9: Baseline Comparison Metrics

**Priority:** P2 (Medium)  
**Complexity:** Low

**Description:** Compare contractability rate against no-CI and CI-only baselines from literature.

**Acceptance Criteria:**
- Define no-CI baseline: 0% (pure version pinning, no validation)
- Define CI-only baseline: 15-20% (integration tests, from Wolter et al. 2025)
- Display comparison bar chart: no-CI, CI-only, proposed framework
- Calculate improvement over baselines
- Include in final validation report

**Inputs:**
- Calculated contractability rate (FR-8)
- Baseline values from literature

**Outputs:**
- Comparison table (baseline vs proposed)
- Improvement percentage
- Bar chart visualization

**Dependencies:** FR-8

**Source:** Wolter et al. 2025, Jiang et al. 2023

---

### FR-10: Visualization Generation

**Priority:** P1 (High)  
**Complexity:** Medium

**Description:** Generate all required and optional visualizations for hypothesis validation.

**Acceptance Criteria:**

**Mandatory Figure:**
- Gate metrics comparison bar chart (contractability rate vs 40% threshold)
  - X-axis: Defect categories (Structural, Metamorphic, Composition, Overall)
  - Y-axis: Contractability rate (%)
  - Threshold line at 40%
  - 95% CI error bars
  - Save to: `figures/gate_metrics_comparison.png`

**Optional Figures (LLM Autonomous):**
1. Defect type distribution pie chart → `figures/defect_distribution.png`
2. Execution time histogram → `figures/execution_time_histogram.png`
3. Version stability analysis line chart → `figures/version_stability.png`
4. Cohen's kappa heatmap → `figures/kappa_heatmap.png`
5. Contractability by project maturity bar chart → `figures/contractability_by_maturity.png`

**Inputs:**
- Contractability rates (FR-8)
- Execution times (FR-5)
- Version stability matrix (FR-7)
- Inter-rater reliability (FR-6)

**Outputs:**
- 6 PNG figures saved to `{hypothesis_folder}/figures/`
- Figure generation code included in experiment script

**Dependencies:** FR-5, FR-6, FR-7, FR-8

**Source:** Phase 2C visualization requirements

---

## Non-Functional Requirements

### NFR-1: Performance

**Requirement:** Contract validation execution time ≤10 seconds per contract (99th percentile)

**Rationale:** Lightweight validation enables integration into CI/CD pipelines without significant overhead.

**Measurement:** 99% of contract executions complete within 10 seconds

**Priority:** P0 (Critical - part of hypothesis gate condition)

---

### NFR-2: Reliability

**Requirement:** Inter-rater reliability (Cohen's kappa) ≥0.7

**Rationale:** Ensures coding consistency and scientific rigor in contractability assessment.

**Measurement:** Cohen's kappa coefficient between two independent coders

**Priority:** P0 (Critical - part of hypothesis gate condition)

---

### NFR-3: Reproducibility

**Requirement:** All experiments use fixed random seeds and versioned dependencies

**Rationale:** Enables exact reproduction of results for peer review and future research.

**Measurement:**
- Fixed random seed documented in code
- `requirements.txt` with pinned library versions
- Retrospective coding order deterministic

**Priority:** P1 (High)

---

### NFR-4: Maintainability

**Requirement:** Code follows DRY principle (Don't Repeat Yourself) with reusable contract validation patterns

**Rationale:** Framework should be library-level and cross-repo reusable, not repo-specific.

**Measurement:**
- Contract classes use inheritance (base Contract class)
- Validation logic abstracted into reusable functions
- No code duplication >3 lines

**Priority:** P2 (Medium)

---

### NFR-5: Documentation

**Requirement:** All generated contracts include human-readable descriptions of invariants being validated

**Rationale:** Facilitates manual review and debugging of contract failures.

**Measurement:**
- Each Contract object has `.description` attribute
- Failure messages include expected vs actual values
- Code comments explain invariant extraction logic

**Priority:** P2 (Medium)

---

## Success Criteria

### Primary Success Criteria

| Criterion | Threshold | Measurement Method | Priority |
|-----------|-----------|-------------------|----------|
| Contractability Rate | ≥40% with 95% CI lower >35% | Wilson score method (FR-8) | P0 |
| Inter-Rater Reliability | Cohen's kappa ≥0.7 | sklearn.metrics.cohen_kappa_score (FR-6) | P0 |
| Execution Time | ≤10 seconds (99th percentile) | Per-contract time measurement (FR-5) | P0 |
| Version Stability | Passes ±2 minor releases | Cross-version validation (FR-7) | P1 |

### PoC Pass Condition

```python
if contractability_rate >= 40 and kappa >= 0.7:
    return "PASS - Hypothesis h-e1 VALIDATED"
else:
    return "FAIL - Pivot to structural-only contracts"
```

### Secondary Success Criteria

- All 3 contract types implemented (structural, metamorphic, composition)
- Defect corpus loaded successfully (348 defects)
- All visualizations generated (6 figures)
- Baseline comparison shows improvement over CI-only approach

---

## Dependencies and Constraints

### External Dependencies

| Dependency | Version | Purpose | Critical? |
|------------|---------|---------|-----------|
| PyTorch | 1.11-1.13 | Runtime assertions, target API | Yes |
| pandas | ≥1.3.0 | Defect corpus loading | Yes |
| scikit-learn | ≥1.0.0 | Cohen's kappa calculation | Yes |
| scipy | ≥1.7.0 | Confidence interval calculation | Yes |
| matplotlib | ≥3.4.0 | Visualization generation | Yes |
| numpy | ≥1.21.0 | Numerical operations | Yes |

### Data Dependencies

- Jiang et al. 348-defect corpus (GitHub: wenxin-jiang/emse-cvreengineering-artifact)
- PyTorch API documentation (for invariant extraction)
- Library version release notes (for version stability testing)

### Infrastructure Constraints

- Minimal infrastructure (LIGHT tier, EXISTENCE hypothesis)
- Single workstation execution (no distributed computing)
- Virtual environments for multi-version testing (conda or venv)

### Time Constraints

- Single-phase retrospective analysis (no iterative training)
- Total execution time: <4 hours (defect corpus coding + validation)

---

## Assumptions and Risks

### Assumptions

1. **A1 (Under Test):** ≥40% of environment-stage API defects are contractable
2. **A2:** Jiang et al. corpus is representative of real-world DL reengineering defects
3. **A3:** PyTorch runtime assertions (`torch._check`, `TORCH_CHECK`) are stable across ±2 minor versions
4. **A4:** Independent coders can achieve ≥0.7 Cohen's kappa agreement

### Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Contractability rate <40% | Medium | High - hypothesis fails | Fallback: Pivot to structural-only contracts with reduced scope |
| Cohen's kappa <0.7 | Low | High - coding unreliable | Add 3rd coder for tie-breaking, refine coding guidelines |
| Execution time >10s | Low | Medium - violates NFR-1 | Optimize contract generation, add early timeout detection |
| Version instability across releases | Medium | Medium - limits applicability | Focus on structural contracts (more stable than metamorphic) |
| Defect corpus missing metadata | Low | High - blocks FR-1 | Manual corpus augmentation from paper and GitHub issues |

### Mitigation Strategies

- **Fallback Implementation:** If full framework too complex, implement structural-only contracts first (highest stability, clearest invariants)
- **Incremental Validation:** Test contract generation on 10-defect sample before full corpus run
- **Pilot Coding:** Run pilot with 20 defects to refine coding guidelines before main study

---

## Technical Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│              API Contract Validation Framework           │
└─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼──────┐
    │ Contract │      │ Contract  │    │  Metrics   │
    │Generator │      │ Validator │    │ Collector  │
    └────┬────┘      └─────┬─────┘    └─────┬──────┘
         │                 │                 │
    ┌────▼──────────────────▼─────────────────▼─────┐
    │         Defect Corpus (Jiang et al.)          │
    │  (348 defects × 3 types: S/M/C invariants)    │
    └───────────────────────────────────────────────┘
```

### Data Flow

1. **Load Corpus** (FR-1) → Filtered DataFrame
2. **Generate Contracts** (FR-2, FR-3, FR-4) → Contract objects per defect
3. **Validate Contracts** (FR-5) → Execution results + timing
4. **Retrospective Coding** (FR-6) → Coder labels + kappa
5. **Version Testing** (FR-7) → Stability matrix
6. **Calculate Metrics** (FR-8, FR-9) → Contractability rate + CI
7. **Generate Visualizations** (FR-10) → Figures for paper

### Contract Class Hierarchy

```python
class Contract(ABC):
    def __init__(self, defect_id, invariant_type):
        self.defect_id = defect_id
        self.invariant_type = invariant_type  # structural | metamorphic | composition
        self.execution_time = None
    
    @abstractmethod
    def validate(self, timeout=10) -> bool:
        """Execute contract with timeout enforcement"""
        pass

class StructuralContract(Contract):
    """Tensor shapes, dtypes, device placement"""
    pass

class MetamorphicContract(Contract):
    """Autocast mode, training/eval state"""
    pass

class CompositionContract(Contract):
    """Cross-library device consistency"""
    pass
```

---

## Out of Scope

The following are explicitly **NOT** included in this phase:

1. **Neural Network Training:** This is a tool validation study, not model training
2. **Real-Time Contract Generation:** Contracts are generated retrospectively, not during development
3. **IDE Integration:** Framework is standalone, not integrated into development environments
4. **Production Deployment:** PoC validation only, not production-ready tooling
5. **Automated Defect Repair:** Framework detects contractability, does not fix defects
6. **Multi-Framework Support Beyond PyTorch:** Focus on PyTorch ecosystem only
7. **Longitudinal Version Tracking:** Testing ±2 minor releases, not full version history
8. **Crowd-Sourced Coding:** 2 independent coders only, not large-scale annotation

---

## Appendix: Traceability Matrix

| Requirement ID | Source Document | Source Section |
|----------------|-----------------|----------------|
| FR-1 | Phase 2C Experiment Brief | Dataset (Jiang et al. corpus) |
| FR-2 | Phase 2C Appendix B.4, B.5 | PyTorch assertions, tensor-shape-assert |
| FR-3 | Phase 2C Appendix A.2 | Autocast validation patterns |
| FR-4 | Phase 2C Appendix A.2, B.1 | CUDA device errors, pact-python |
| FR-5 | Phase 2C Appendix B.3 | apiwatch SLA validation |
| FR-6 | Phase 2B Verification Protocol | 2-coder retrospective coding |
| FR-7 | Phase 2C Experiment Brief | Version stability requirement |
| FR-8 | Phase 2C Success Criteria | 40% threshold with 95% CI |
| FR-9 | Phase 2C Baseline Performance | Wolter et al., Jiang et al. |
| FR-10 | Phase 2C Visualization Requirements | 6 required figures |
| NFR-1 | Phase 2C Hypothesis Statement | ≤10s validation time |
| NFR-2 | Phase 2C Success Criteria | Cohen's kappa ≥0.7 |

**100% Traceability:** All requirements trace to Phase 2B/2C documentation or researched implementations.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-11 | Anonymous | Initial PRD creation from Phase 2C experiment brief |

---

**End of PRD**

*Generated for hypothesis h-e1 (EXISTENCE, MUST_WORK gate)*  
*Task Budget: LIGHT tier (15 tasks max, 4-8 epics)*  
*Next Phase: Architecture Design (Step 3)*
