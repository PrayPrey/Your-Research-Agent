# Product Requirements Document: h-c3 Composition Contract Validation

**Date:** 2026-07-11  
**Hypothesis:** Chains of contracts (e.g., dataset → preprocess → model → output) propagate failures bidirectionally  
**Experiment Type:** MECHANISM (COMPOSITION)  
**Priority:** HIGH (blocks h-m4 lifecycle validation)

---

## 1. Executive Summary

### 1.1 Objective
Validate whether composition-level contracts can detect cross-library API defects through bidirectional failure propagation across ML pipeline stages (dataset → preprocess → model → output).

### 1.2 Success Criteria
- **Primary:** Detection rate ≥60% on 62 composition defects (Jiang corpus subset)
- **Baseline:** 0% (from h-e1 - composition contracts deemed not contractable)
- **Gate:** SHOULD_WORK - failure documents limitation, doesn't block pipeline
- **Execution:** All contracts complete within ≤10s
- **Stability:** Contracts work across ±2 minor library releases

### 1.3 Critical Context
h-e1 showed **0% contractability** for composition-level defects due to version instability. This is a HIGH-RISK experiment testing whether composition contracts are even feasible.

---

## 2. Scope

### 2.1 In-Scope
- Composition contract framework for cross-library API validation
- Three contract types: device placement, tensor layout, cross-library bindings
- Bidirectional failure propagation (forward + backward through pipeline stages)
- Retrospective analysis on 62 composition defects from Jiang corpus
- Version stability testing across ±2 minor releases
- Comparison to manual validation baseline (0% from h-e1)

### 2.2 Out-of-Scope
- Training-based experiments (this is retrospective analysis only)
- Real-time contract enforcement in production systems
- Automated contract generation (manual specification required)
- Contracts for single-library defects (covered by h-m1, h-m2)

### 2.3 Dataset
- **Source:** h-e1 experiment results (`docs/youra_research/h-e1/data/defect_corpus.csv`)
- **Subset:** 62 composition-level defects (cross-library interaction failures)
- **Libraries:** PyTorch + CUDA + Transformers version triads
- **Reuse Rationale:** Enables controlled comparison across contract types

---

## 3. Functional Requirements

### 3.1 Core Functionality

**FR-1: Composition Contract Framework**
- **Description:** Implement contract chain validators for pipeline stages
- **Components:**
  - Pipeline stage definitions (dataset, preprocess, model, output)
  - Contract types (device placement, tensor layout, cross-library bindings)
  - Bidirectional failure propagation mechanism
- **Input:** Defect metadata from corpus (lib versions, failure type)
- **Output:** (contractable: bool, execution_time: float)

**FR-2: Device Placement Contract**
- **Description:** Validate GPU/CPU consistency across pipeline stages
- **Validation:** Check device placement for tensors, models, generators
- **Example:** Detect "Expected 'cuda' device but found 'cpu'" errors
- **Constraint:** Must be version-stable across ±2 minor PyTorch releases

**FR-3: Tensor Layout Contract**
- **Description:** Validate shape/dtype consistency across library boundaries
- **Validation:** Check tensor dimensions, data types, memory layouts
- **Example:** Detect shape mismatches between Transformers and PyTorch tensors
- **Constraint:** Must be version-stable across ±2 minor library releases

**FR-4: Cross-Library Binding Contract**
- **Description:** Validate API compatibility across library version triads
- **Validation:** Check method signatures, parameter types, return types
- **Example:** Detect API changes breaking PyTorch + Transformers integration
- **Constraint:** Must be version-stable across ±2 minor releases

**FR-5: Bidirectional Failure Propagation**
- **Description:** Propagate contract failures to dependent stages
- **Forward Propagation:** Mark downstream stages as blocked when upstream fails
- **Backward Propagation:** Check if upstream stages can recover from downstream failures
- **Mechanism:** Contract chains track dependencies between pipeline stages

### 3.2 Data Processing

**FR-6: Corpus Loading**
- **Source:** `docs/youra_research/h-e1/data/defect_corpus.csv`
- **Filter:** Extract 62 composition-level defects (category == 'composition')
- **Validation:** Assert len(composition_defects) == 62
- **Output:** Defect metadata for contract generation

**FR-7: Version Stability Testing**
- **Input:** Defect + library version range (±2 minor releases)
- **Process:** Execute contracts across all version combinations
- **Output:** Version stability rate (% contracts stable across versions)
- **Baseline:** 0% (from h-e1 - composition contracts failed version stability)

### 3.3 Evaluation

**FR-8: Detection Rate Calculation**
- **Formula:** (contractable_count / 62) × 100%
- **Target:** ≥60% (SHOULD_WORK gate)
- **Baseline:** 0% (from h-e1 manual validation)
- **Output:** Detection rate with 95% confidence interval

**FR-9: Execution Time Monitoring**
- **Constraint:** ≤10 seconds per contract validation
- **Measurement:** time.time() before/after contract execution
- **Output:** Mean, max execution times; % contracts within constraint

**FR-10: False Positive Rate**
- **Test Set:** Known-good code examples (valid library usage)
- **Constraint:** <5% false positives
- **Output:** False positive rate on validation set

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-1:** Contract validation completes within ≤10s per defect
- **NFR-2:** Total experiment runtime ≤15 minutes for 62 defects
- **NFR-3:** Version stability testing completes within ≤60 minutes

### 4.2 Reliability
- **NFR-4:** Deterministic results (fixed seed, no randomness)
- **NFR-5:** Graceful handling of version incompatibilities
- **NFR-6:** Timeout protection for hanging contract executions

### 4.3 Maintainability
- **NFR-7:** Modular contract framework (extensible to new contract types)
- **NFR-8:** Clear separation: contract generation vs execution vs evaluation
- **NFR-9:** Comprehensive logging for debugging version stability failures

---

## 5. Technical Constraints

### 5.1 Dependencies
- **Python:** ≥3.8 (for type hints, dataclasses)
- **PyTorch:** Multiple versions for stability testing (±2 minor releases)
- **Transformers:** Multiple versions for stability testing (±2 minor releases)
- **CUDA:** Compatible versions for device placement testing
- **Testing:** pytest, hypothesis (property-based testing framework)

### 5.2 Data Constraints
- **Dataset Size:** 62 composition defects (fixed from h-e1)
- **Data Format:** CSV with columns: defect_id, category, lib_versions, failure_type
- **Data Quality:** Validated in h-e1 (checksum: 6572aa34c06ecf13)

### 5.3 Baseline Constraints
- **Baseline Model:** Manual validation from h-e1 (0% contractability)
- **Baseline Metric:** Detection rate = 0% for composition defects
- **Comparison:** Composition contracts must exceed 0% to show improvement

---

## 6. Acceptance Criteria

### 6.1 PoC Pass Conditions
1. ✅ Code runs without error
2. ✅ Detection rate > baseline (0%)
3. ✅ All 62 defects processed
4. ✅ Execution time constraint met (≤10s per defect)

### 6.2 Gate Pass Conditions (SHOULD_WORK)
1. ✅ Detection rate ≥60%
2. ✅ Version stability rate ≥80% (contracts stable across ±2 minor releases)
3. ✅ False positive rate <5%
4. ✅ Bidirectional propagation demonstrated (≥1 example)

### 6.3 Gate Warning Conditions
- Detection rate < 40%: Document composition contracts as manual curation requirement
- Version stability < 60%: Document version fragility
- False positive rate ≥5%: Document brittleness concerns

**Note:** SHOULD_WORK gate allows continuation even if warning conditions triggered.

---

## 7. Deliverables

### 7.1 Code Artifacts
- `code/contracts/composition_chain.py` - Core contract framework
- `code/contracts/device_placement.py` - Device placement validators
- `code/contracts/tensor_layout.py` - Tensor layout validators
- `code/contracts/cross_library_binding.py` - Cross-library API validators
- `code/data/composition_loader.py` - Corpus loading + filtering
- `code/analysis/metrics.py` - Detection rate, execution time, stability calculations
- `code/visualization/plots.py` - Gate metrics, version stability heatmap
- `code/run_experiment.py` - Main experiment orchestration

### 7.2 Documentation
- `04_validation.md` - Experiment results and analysis
- `figures/gate_metrics.png` - Target vs actual metrics (mandatory)
- `figures/detection_by_type.png` - Detection rate by contract type
- `figures/execution_time_dist.png` - Execution time distribution
- `figures/version_stability_heatmap.png` - Version stability patterns
- `figures/failure_propagation.png` - Bidirectional propagation network

### 7.3 Data Outputs
- `results/composition_results.csv` - Per-defect results (contractable, exec_time)
- `results/version_stability.csv` - Version stability matrix
- `results/false_positives.csv` - False positive test results

---

## 8. Risk Assessment

### 8.1 High-Severity Risks
**R1: Version Instability (h-e1 baseline: 0% contractability)**
- **Impact:** Composition contracts may be fundamentally infeasible
- **Likelihood:** HIGH (h-e1 evidence)
- **Mitigation:**
  - Focus on LTS library versions only
  - Test across ±2 minor releases (not patch releases)
  - Document version fragility patterns if stability <60%
- **Fallback:** Document composition contracts as manual curation requirement

**R2: Insufficient Documentation for Binding Assumptions**
- **Impact:** Cannot generate contracts without documented invariants
- **Likelihood:** MEDIUM
- **Mitigation:**
  - Hybrid approach: auto-generation + manual specification
  - Focus on well-documented libraries (PyTorch, HuggingFace)
  - Document manual curation requirements in 04_validation.md

### 8.2 Medium-Severity Risks
**R3: Execution Time Constraint Violations**
- **Impact:** Contracts exceed ≤10s limit
- **Likelihood:** LOW (h-m2 validated lightweight probes)
- **Mitigation:** Timeout protection, optimize contract execution

**R4: False Positive Rate >5%**
- **Impact:** Contracts too brittle for adoption
- **Likelihood:** MEDIUM (version combinations increase fragility)
- **Mitigation:** Test on known-good code examples, adjust contract thresholds

---

## 9. Timeline & Milestones

### Phase 3 (Implementation Planning) - Current
- ✅ PRD generation
- ⏳ Architecture design (parallel with Logic + Config)
- ⏳ Task breakdown + budget allocation

### Phase 4 (Coding + Validation)
- **Milestone 1:** Data setup (load + filter 62 composition defects)
- **Milestone 2:** Contract framework implementation
- **Milestone 3:** Contract type implementations (device, layout, binding)
- **Milestone 4:** Bidirectional propagation mechanism
- **Milestone 5:** Version stability testing
- **Milestone 6:** Metrics + visualization
- **Milestone 7:** Validation report (04_validation.md)

**Estimated Effort:** LIGHT tier (15 tasks max)
- Novel mechanism (no existing implementations)
- But reuses h-e1 data + h-m1/h-m2 retrospective methodology

---

## 10. Dependencies & Prerequisites

### 10.1 Completed Prerequisites
- ✅ h-e1: Contractability validated (74.76% overall, 0% composition)
- ✅ h-m1: Structural contracts working
- ✅ h-m2: Metamorphic contracts working

### 10.2 Data Dependencies
- ✅ h-e1 defect corpus: `docs/youra_research/h-e1/data/defect_corpus.csv`
- ✅ h-e1 baseline: 0% contractability for composition defects

### 10.3 Methodology Dependencies
- ✅ Retrospective coding approach (from h-e1)
- ✅ Lightweight probe execution (from h-m2, ≤10s constraint)
- ✅ Version stability testing (from h-e1, ±2 minor releases)

---

## 11. Open Questions

**Q1:** Can composition contracts overcome version instability (h-e1 showed 0%)?
- **Resolution:** Experiment will test; SHOULD_WORK gate tolerates failure

**Q2:** Which contract type is most version-stable (device, layout, binding)?
- **Resolution:** Analyze detection rate by contract type (FR-8)

**Q3:** Is bidirectional propagation necessary vs unidirectional?
- **Resolution:** Compare forward-only vs bidirectional modes (if time permits)

**Q4:** What false positive rate is acceptable for adoption?
- **Resolution:** Use <5% threshold from h-e1; document if exceeded

---

## 12. Approval

**PRD Author:** Claude (Phase 3 Architecture Agent)  
**Stakeholders:** Phase 4 Coder, Phase 4 Validator  
**Status:** DRAFT (pending Architecture + Logic + Config review)  

**Next Steps:**
1. Architecture design (03_architecture.md)
2. Logic specification (03_logic.md)
3. Configuration parameters (03_config.md)
4. Task breakdown + budget allocation
5. Phase 4 implementation

---

*Generated by Phase 3 Implementation Planning (Step 02)*  
*Source: 02c_experiment_brief.md + 02b_context.md*
