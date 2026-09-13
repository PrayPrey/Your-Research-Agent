# Implementation Tasks: H-M2 Metamorphic Contract Validation

**Hypothesis ID:** h-m2  
**Phase:** 3 - Implementation Planning  
**Generated:** 2026-07-11  
**Total Tasks:** 17 (within FULL tier budget of 30)

---

## Task Summary

| Category | Count | Status |
|----------|-------|--------|
| Data Preparation | 1 | Pending |
| Environment Setup | 1 | Pending |
| Epic Tasks | 5 | Pending |
| Subtasks | 8 | Pending |
| Infrastructure | 1 | Pending |
| Failsafe | 1 | Pending |
| **Total** | **17** | **Ready** |

---

## Data Preparation Tasks

### TASK-DATA-01: Setup Test Suite Structure

**Priority:** P0 (Must complete before Epic tasks)  
**Type:** Data Preparation  
**Complexity:** Low

**Description:**
Create directory structure for programmatic test suite generation. No manual data download required (all test cases generated via PyTorch API).

**Actions:**
1. Create `test_suite/` directory
2. Create `test_suite/scenarios/` subdirectory
3. Create `results/` directory for metrics output
4. Create `figures/` directory for visualization

**Reference Files:**
- 03_prd.md (Section "Functional Requirements" → FR-1: Test Suite Generation)
- 03_architecture.md (Section "Core Components")

**Acceptance Criteria:**
- All directories exist and are writable
- No external data downloads required
- Structure ready for test case generation

---

## Environment Setup Tasks

### TASK-ENV-01: Install Dependencies

**Priority:** P0 (Must complete before Epic tasks)  
**Type:** Environment Setup  
**Complexity:** Low

**Description:**
Install Python packages required for metamorphic contract validation experiment.

**Dependencies:**
```python
# Core dependencies
torch>=2.0.0  # PyTorch for softmax, dropout operations
pytest>=7.0.0  # Test framework
matplotlib>=3.5.0  # Visualization

# From h-m1 (prerequisite)
# (Assumes h-m1 contract library is installed)
```

**Actions:**
1. Install torch (latest stable)
2. Install pytest for test execution
3. Install matplotlib for figure generation
4. Verify h-m1 contract library is available

**Reference Files:**
- 03_prd.md (Section "Technical Constraints" → TC-1: Dependencies)

**Acceptance Criteria:**
- All packages install without errors
- `import torch`, `import pytest`, `import matplotlib` succeed
- h-m1 contracts importable: `from h_m1.contracts.validator import validate_structural`

---

## Epic Implementation Tasks

### EPIC-B-1: Implement Metamorphic Validators

**Priority:** P0 (Core mechanism)  
**Type:** Implementation  
**Complexity:** 12 (Medium)  
**Subtasks:** 2

**Description:**
Implement softmax sum validator and dropout identity validator with numerical tolerance checking.

**Components:**
- `contracts/metamorphic.py`: SoftmaxSumValidator, DropoutIdentityValidator
- Numerical tolerance validation using torch.allclose
- Exception hierarchy: SoftmaxSumViolation, DropoutIdentityViolation

**Reference Files:**
- 03_prd.md → FR-3: Proposed Model (Metamorphic Contracts)
- 03_architecture.md → Section 2.1: Metamorphic Validators
- 03_logic.md → L-1: Softmax Sum Validator, L-2: Dropout Identity Validator
- 03_config.md → Section 2.1: MetamorphicConfig (rtol, atol tolerances)

**Acceptance Criteria:**
- SoftmaxSumValidator.validate_softmax() detects sum violations
- DropoutIdentityValidator.validate_dropout_identity() detects identity violations
- Numerical tolerances configurable (rtol=1e-5, atol=1e-7)
- Typed exceptions raised with diagnostic info

**Subtasks:**

#### SUBTASK-B-1.1: Softmax Sum Validation Logic

**Description:** Implement torch.allclose-based validation for softmax sum property.

**Reference Files:**
- 03_logic.md → L-1: Softmax Sum Validator → Pseudo-code section

**Actions:**
1. Implement `validate_softmax(func, probe_input, dim, rtol, atol)` method
2. Compute sum across specified dimension
3. Compare against expected sum (1.0) with tolerance
4. Raise SoftmaxSumViolation if property violated

**Acceptance:** Detects sum violations within numerical tolerance

#### SUBTASK-B-1.2: Dropout Identity Validation Logic

**Description:** Implement exact equality check for dropout eval mode identity.

**Reference Files:**
- 03_logic.md → L-2: Dropout Identity Validator → Pseudo-code section

**Actions:**
1. Implement `validate_dropout_identity(module, probe_input, eval_mode)` method
2. Set module to eval mode if eval_mode=True
3. Apply module to probe input
4. Check torch.equal(input, output)
5. Raise DropoutIdentityViolation if identity violated

**Acceptance:** Detects identity violations in eval mode

---

### EPIC-B-2: Implement Test Scenario Generation

**Priority:** P0 (Core test suite)  
**Type:** Implementation  
**Complexity:** 10 (Medium)  
**Subtasks:** 1

**Description:**
Create control, softmax violation, and dropout violation test scenarios with known ground truth.

**Components:**
- `test_suite/scenarios.py`: Scenario definitions
- Control scenarios (valid operations, properties hold)
- Softmax violation scenarios (perturbed output)
- Dropout violation scenarios (dropout in eval mode)

**Reference Files:**
- 03_prd.md → FR-1: Test Suite Generation
- 03_architecture.md → Section 2: Module Specifications → test_suite/scenarios.py
- 03_config.md → Section 2.2: ScenarioConfig (num_control, num_softmax, num_dropout)

**Acceptance Criteria:**
- 10 control scenarios (no defects)
- 20 softmax violation scenarios (sum ≠ 1.0)
- 20 dropout violation scenarios (identity broken)
- Total: 50 test cases
- All scenarios deterministic (seed=42)

**Subtasks:**

#### SUBTASK-B-2.1: Scenario Class Definitions

**Description:** Define scenario data structures and generation logic.

**Reference Files:**
- 03_logic.md → L-4: Probe Generator
- 03_config.md → Section 2.2: ScenarioConfig

**Actions:**
1. Define Scenario dataclass (type, probe_input, expected_violation)
2. Implement control scenario generator (valid operations)
3. Implement softmax violation generator (perturbed outputs)
4. Implement dropout violation generator (train mode forced)

**Acceptance:** All 3 scenario types generated with known ground truth

---

### EPIC-B-3: Implement Defect Injection

**Priority:** P0 (Controlled testing)  
**Type:** Implementation  
**Complexity:** 11 (Medium)  
**Subtasks:** 2

**Description:**
Implement controlled violation injection for softmax (perturbation) and dropout (mode forcing).

**Components:**
- `test_suite/defect_injection.py`: Violation injection logic
- Softmax perturbation (multiply by 0.9 to break sum property)
- Dropout mode forcing (train=True in eval mode)

**Reference Files:**
- 03_prd.md → FR-1.3: Test cases include defect types
- 03_architecture.md → Section 2: test_suite/defect_injection.py
- 03_config.md → Section 2.2: softmax_perturbation_factor, dropout_force_train_mode

**Acceptance Criteria:**
- Softmax perturbation creates sum ≠ 1.0 violations
- Dropout mode forcing creates identity violations
- Ground truth labels (violation: yes/no) available per test

**Subtasks:**

#### SUBTASK-B-3.1: Softmax Perturbation Logic

**Description:** Perturb softmax output to violate sum property.

**Reference Files:**
- 03_config.md → softmax_perturbation_factor = 0.9

**Actions:**
1. Implement perturbation function: `output * perturbation_factor`
2. Verify sum(perturbed_output) ≠ 1.0
3. Label as violation in ground truth

**Acceptance:** Perturbed softmax outputs fail sum validation

#### SUBTASK-B-3.2: Dropout Mode Forcing

**Description:** Force dropout to apply in eval mode (break identity).

**Reference Files:**
- 03_config.md → dropout_force_train_mode = True

**Actions:**
1. Implement mode forcing: `torch.dropout(x, p, train=True)` even in eval
2. Verify output ≠ input
3. Label as violation in ground truth

**Acceptance:** Forced dropout breaks identity property in eval mode

---

### EPIC-B-4: Implement Experiment Runner

**Priority:** P0 (Core execution)  
**Type:** Implementation  
**Complexity:** 13 (Medium-High)  
**Subtasks:** 2

**Description:**
Run baseline (no contracts) vs proposed (with metamorphic contracts), calculate detection metrics.

**Components:**
- `experiments/run_experiment.py`: Main experiment runner
- Baseline execution (zero validation)
- Proposed execution (metamorphic validation)
- Metrics calculation (detection rate, execution time, false positives)

**Reference Files:**
- 03_prd.md → FR-2: Baseline Model, FR-3: Proposed Model, FR-4: Evaluation Metrics
- 03_architecture.md → Section 2: experiments/run_experiment.py
- 03_logic.md → L-3: Metamorphic Decorator (integration pattern)
- 03_config.md → Section 2.3: ExperimentConfig (seed, max_total_time_s)

**Acceptance Criteria:**
- Baseline runs all 50 scenarios without validation (0% detection)
- Proposed runs all 50 scenarios with metamorphic validation
- Detection rate calculated: (detected_violations / total_violations) × 100%
- Execution time <10s total
- False positive rate <5% (control scenarios)

**Subtasks:**

#### SUBTASK-B-4.1: Baseline Execution

**Description:** Run all scenarios without metamorphic validation.

**Reference Files:**
- 03_prd.md → FR-2: Baseline Model
- 03_logic.md → Integration with h-m1 section

**Actions:**
1. Execute all scenarios with plain PyTorch operations
2. Record execution time
3. Expected detection: 0/40 violations (no validation)

**Acceptance:** Baseline completes with 0% detection rate

#### SUBTASK-B-4.2: Proposed Execution & Metrics

**Description:** Run all scenarios with metamorphic contracts, calculate metrics.

**Reference Files:**
- 03_prd.md → FR-4: Evaluation Metrics
- 03_logic.md → L-3: Metamorphic Decorator

**Actions:**
1. Apply @validate_metamorphic decorator to test functions
2. Execute all scenarios, catch violations
3. Calculate detection rate, execution time, false positive rate
4. Validate against success criteria (≥70% detection, ≤10s, <5% FP)

**Acceptance:** Proposed execution achieves ≥70% detection rate

---

### EPIC-B-5: Implement Numerical Tolerance Testing

**Priority:** P1 (Validation support)  
**Type:** Implementation  
**Complexity:** 9 (Medium)  
**Subtasks:** 1

**Description:**
Validate rtol/atol configurations for numerical stability across edge cases.

**Components:**
- Test edge cases: all zeros, large values, NaN/Inf handling
- Boundary testing for rtol/atol thresholds
- Probe size validation (<10K elements)

**Reference Files:**
- 03_prd.md → NFR-1: Performance (numerical stability)
- 03_architecture.md → Section 7: Performance Optimizations
- 03_logic.md → L-1: Numerical Tolerance Logic
- 03_config.md → Section 2.1: rtol, atol, max_probe_elements

**Acceptance Criteria:**
- rtol/atol validation passes for normal inputs
- Edge cases handled gracefully (zeros, large values)
- Probe size validation prevents >10K element probes
- Execution overhead <30ms per test

**Subtasks:**

#### SUBTASK-B-5.1: Edge Case Validation

**Description:** Test numerical tolerance with edge cases.

**Reference Files:**
- 03_logic.md → L-1.1: Numerical Tolerance Logic → Handle edge cases

**Actions:**
1. Test softmax validation with all-zero input
2. Test softmax validation with large values (overflow risk)
3. Test NaN/Inf handling
4. Verify rtol/atol boundary cases

**Acceptance:** All edge cases handled without crashes

---

## Infrastructure Tasks

### TASK-INFRA-01: Setup Visualization Pipeline

**Priority:** P1 (Required for complete validation)  
**Type:** Infrastructure  
**Complexity:** Low

**Description:**
Setup matplotlib-based figure generation for required visualizations.

**Figures (from FR-5):**
1. Gate Metrics Comparison (mandatory)
2. Detection Rate Breakdown (softmax vs dropout)
3. Execution Time Comparison (baseline vs contracts)
4. Violation Severity Distribution (histogram of deviations)

**Reference Files:**
- 03_prd.md → FR-5: Visualization
- 03_config.md → Section 2.4: ResultsConfig (figure_dpi, figure_formats)

**Actions:**
1. Implement gate_metrics_comparison() function
2. Implement detection_rate_breakdown() function
3. Implement execution_time_comparison() function
4. Implement violation_severity_distribution() function
5. Save all figures to `figures/` directory as PNG (300 DPI)

**Acceptance Criteria:**
- All 4 figure types generated
- Saved to `{hypothesis_folder}/figures/`
- PNG format with 300 DPI

---

## Failsafe Tasks

### TASK-FAILSAFE-01: Minimal PoC Execution

**Priority:** P2 (Backup plan)  
**Type:** Failsafe  
**Complexity:** Low

**Description:**
If full implementation exceeds time budget, execute minimal PoC with reduced scope.

**Minimal Scope:**
- 1 control scenario (instead of 10)
- 2 softmax violations (instead of 20)
- 2 dropout violations (instead of 20)
- Total: 5 test cases (instead of 50)

**Success Criteria for Minimal PoC:**
- Code executes without errors
- Proposed detection rate > baseline detection rate (0%)
- At least 1 violation detected

**Reference Files:**
- 03_prd.md → "PoC Success Check" section

**Acceptance Criteria:**
- Minimal PoC completes if full scope blocked
- Detection rate calculated on reduced test set
- Gate evaluation still performed (may not pass ≥70% threshold)

---

## Task Execution Order

```
PHASE 1: Setup (P0 - Prerequisite)
├── TASK-DATA-01: Setup Test Suite Structure
└── TASK-ENV-01: Install Dependencies

PHASE 2: Core Implementation (P0 - Parallel where possible)
├── EPIC-B-1: Metamorphic Validators
│   ├── SUBTASK-B-1.1: Softmax Sum Validation
│   └── SUBTASK-B-1.2: Dropout Identity Validation
├── EPIC-B-2: Test Scenario Generation
│   └── SUBTASK-B-2.1: Scenario Class Definitions
├── EPIC-B-3: Defect Injection
│   ├── SUBTASK-B-3.1: Softmax Perturbation
│   └── SUBTASK-B-3.2: Dropout Mode Forcing
├── EPIC-B-4: Experiment Runner
│   ├── SUBTASK-B-4.1: Baseline Execution
│   └── SUBTASK-B-4.2: Proposed Execution & Metrics
└── EPIC-B-5: Numerical Tolerance Testing
    └── SUBTASK-B-5.1: Edge Case Validation

PHASE 3: Infrastructure (P1 - After core implementation)
└── TASK-INFRA-01: Visualization Pipeline

PHASE 4: Failsafe (P2 - Only if needed)
└── TASK-FAILSAFE-01: Minimal PoC
```

---

## Budget Compliance

| Category | Allocated | Actual | Status |
|----------|-----------|--------|--------|
| Data Preparation | 2 | 1 | ✅ Under budget |
| Environment Setup | 1 | 1 | ✅ On budget |
| Epic Tasks | 6-12 | 5 | ✅ Within range |
| Subtasks | ~8 | 8 | ✅ On target |
| Infrastructure | - | 1 | ✅ Minimal |
| Failsafe | - | 1 | ✅ Backup only |
| **Total** | **30 max** | **17** | ✅ **57% of budget** |

**Tier:** FULL (MECHANISM hypothesis)  
**Budget Utilization:** 17/30 tasks (conservative for PoC scope)

---

## Quality Gates

### Pre-Implementation Checklist
- ✅ All Phase 3 documents complete (PRD, Architecture, Logic, Config)
- ✅ Task references link to specific document sections
- ✅ Dependencies identified (h-m1 prerequisite)
- ✅ Total tasks within budget (17 ≤ 30)

### Post-Implementation Checklist (Phase 4)
- [ ] All P0 tasks completed
- [ ] Detection rate ≥70% (SHOULD_WORK gate)
- [ ] Execution time ≤10s
- [ ] False positive rate <5%
- [ ] All 4 required figures generated

---

**Status:** Ready for Phase 4 Implementation  
**Next Phase:** Phase 4 - Coding & PoC Validation
