# Phase 2A Hypothesis Refinement Summary

**Generated:** 2026-07-09  
**Workflow:** Phase 2A-Dialogue (Self-Contained Tikitaka Loop)  
**Discussion Exchanges:** 15  
**Convergence:** Achieved

---

## Executive Summary

The research discussion successfully established a **four-stage validation pipeline** for proxy-based optimization in code generation, moving the field from heuristic reward engineering to scientifically validated methodology. The hypothesis tests whether validated proxy metrics (structural similarity, runtime efficiency, style conformity) beyond execution correctness can yield Pareto-dominant improvements in downstream developer acceptance outcomes.

**Key Innovation:** Construct validation as a prerequisite for optimization — test proxy independence BEFORE RL training, not after.

---

## Refined Hypothesis

**Core Statement:**

> Under code generation tasks with existing test suites (HumanEval, SWE-bench, MBPP), if models are trained via constrained multi-objective RL using validated proxy metrics (those passing measurement reliability, conditional independence, and cross-domain generalization stages), then they will achieve ≥5% improvement in downstream developer acceptance outcomes (edit distance to accepted solutions, PR acceptance rates) while maintaining per-task execution pass rates within 5% of baseline, because validated proxies capture non-redundant quality dimensions (structural similarity, runtime efficiency, style conformity) that influence developer acceptance beyond execution correctness alone.

**Hypothesis ID:** H-ProxyValidation-v1

**Confidence Level:** 0.75

---

## Four-Stage Validation Pipeline

### Stage 1: Measurement Reliability
**Objective:** Establish signal quality before any modeling

**Calibration Studies:**
- 50 HumanEval problems × 10 solutions × 5 runs each
- Metrics:
  - Intra-implementation CV ≤5%
  - Inter-complexity-class Cohen's d ≥ 0.8
  - Cross-hardware Spearman ρ ≥ 0.8
- 50 controlled asymptotic tasks (O(n), O(n log n), O(n²) reference solutions)

**Fail Condition:** If efficiency measurements too noisy (CV >5%), drop efficiency from optimization

### Stage 2: Conditional Independence
**Objective:** Test proxy non-redundancy via stratified regression

**Protocol:**
- Hierarchical regression: `Outcome ~ Execution_visible + Proxy`
- Primary outcomes: Hidden test pass rate, edit distance, PR acceptance
- **Critical test:** Effect must persist within perfect-execution stratum (100% test pass)
- Threshold: ΔR² ≥ 0.03 (p < 0.01 corrected)

**Fail Condition:** If proxy effects vanish within perfect-execution stratum, proxy is conditionally redundant — drop it

### Stage 3: Cross-Domain Generalization
**Objective:** Validate stability across distribution shifts

**Protocol:**
- PR-style model: Leave-cluster-out validation (train on 8 SWE-bench repos, test on 4 unseen)
- Test across stylistically diverse repositories (verbose vs terse, functional vs OOP)
- Thresholds: R² drops <50%, ensemble disagreement ≤20% on quality features

**Fail Condition:** Predictive power collapse or high disagreement → repository-specific artifacts, not generalizable preference

### Stage 4: Constrained Optimization
**Objective:** Per-task safety with Pareto improvement

**Protocol:**
- Execution constraint: Per-problem pass rate regression ≤5% (not global mean)
- Secondary improvement: ≥5% gain in validated proxies on behavioral outcomes
- Ablation: execution-only, execution+each proxy, full multi-objective
- Fractional factorial: Test interaction effects (≥5% variance → synergy detected)

**Fail Condition:** >10% of problems show >5% execution regression OR no secondary improvement

---

## Testable Predictions

### P1: Proxy Validation Success (Primary)
**Prediction:** At least ONE proxy (CodeBLEU, normalized runtime ratio, learned PR-style) survives all four validation stages

**Success Criteria:**
- ✓ Stage 1 calibration (CV ≤5%, d ≥ 0.8, ρ ≥ 0.8)
- ✓ Stage 2 conditional independence (ΔR² ≥ 0.03, effect persists in 100%-correct stratum)
- ✓ Stage 3 cross-repo generalization (R² stable, disagreement ≤20%)
- ✓ Stage 4 per-task safety (≤5% regression per problem)

**Falsifiability:** If ALL proxies fail conditional independence (effects vanish in perfect-execution stratum), hypothesis simplifies to "execution correctness suffices"

### P2: Pareto Dominance
**Prediction:** Constrained multi-objective models (Condition C) achieve ≥5% secondary improvement with per-task execution within 5% of baseline

**Success Criteria:**
- Edit distance reduced ≥5% vs execution-only (Condition A)
- PR acceptance rate improved ≥5 percentage points
- ≤10% of problems show >5% pass rate regression
- Improvements persist on post-2023 SWE-bench (temporal generalization)

**Falsifiability:** If Condition C does not dominate A/B on Pareto frontier, multi-objective provides no benefit

### P3: Interaction Analysis
**Prediction:** Either synergy detected (≥5% interaction variance) OR simplification to additive (< 5%)

**Success Criteria:**
- Path A (Synergy): 2-way interactions significant (p < 0.01), ΔR² ≥ 0.05
- Path B (Additive): Additive model R² within 2% of interaction model

**Both outcomes valuable:** Path A reveals conditional dependencies, Path B establishes dimensional independence

---

## Key Assumptions

**A1:** CodeBLEU captures structural quality independent of execution correctness  
→ Test via partial correlation with hidden tests

**A2:** Runtime measurements reliably distinguish complexity classes  
→ Validate via CV ≤5%, d ≥ 0.8, ρ ≥ 0.8 calibration

**A3:** PR-style signals generalize across repositories  
→ Cross-repo validation with ≤20% disagreement threshold

**A4:** Developer acceptance influenced by multiple dimensions beyond execution  
→ SEM/hierarchical regression shows ΔR² ≥ 0.03

**A5:** Interaction effects between quality dimensions exist  
→ Fractional factorial shows ≥5% interaction variance

---

## Critical Risks & Mitigations

**R1: Conditional redundancy (proxies fail independence test)**  
→ Mitigation: Drop non-independent proxies, continue with validated subset

**R2: Efficiency noise too high (CV >5%)**  
→ Mitigation: Calibration study identifies this BEFORE RL training; drop if failed

**R3: Style signals repository-specific**  
→ Mitigation: Switch to domain-specific ensemble approach

**R4: Execution constraint violations (>10% problems exceed 5% regression)**  
→ Mitigation: Tighter Lagrangian penalties, per-problem monitoring

**R5: Temporal generalization failure (post-2023 data)**  
→ Mitigation: Indicates benchmark artifacts; pivot to domain boundary investigation

---

## Novelty & Contributions

### Methodological Contribution
**Primary:** Establishes construct validation as prerequisite for proxy-based optimization

**Innovations:**
- Four-stage pipeline reusable for any auxiliary objective
- Conditional independence within correctness strata (not just global correlation)
- Per-task constraints prevent average-case masking
- Built-in fail-safes: drop invalidated proxies, simplify if no interactions

### Empirical Contributions
- **If successful:** Validated proxies demonstrate non-redundant quality dimensions
- **If proxies fail:** Rules out false signals, prevents wasted field-wide effort
- **Interaction analysis:** Reveals synergistic vs additive quality structure

### Field Impact
Provides methodological blueprint for future auxiliary objective proposals, raising evidentiary standards for multi-objective code generation research.

---

## Experimental Setup

**Timeline:** 10-12 weeks  
**Compute:** ~1,000 GPU hours (standard academic allocation)  
**Baselines:** CodeRL (execution-only), Sequential optimization, Per-proxy ablations

**Benchmarks:**
- HumanEval (164 problems) — visible + hidden test splits
- MBPP (500 problems) — cross-dataset validation
- SWE-bench Lite (300 issues) — PR acceptance, temporal splits
- 50 controlled asymptotic tasks — ground-truth complexity validation

**No new data collection required** — all analysis uses existing benchmark infrastructure

---

## Phase 2B Readiness

✅ **READY FOR PHASE 2B**

**Outputs Generated:**
- `03_refinement.yaml` — Primary hypothesis specification
- `02_synthesis.yaml` — Synthesis details
- `01_round_table/final_opinions.yaml` — Per-persona assessments

**Next Steps:**
- Phase 2C: Specify 50 controlled asymptotic tasks (implementation patterns)
- Phase 3: Design calibration study protocols (Stage 1 validation)
- Phase 3: Implement hierarchical regression pipeline (Stage 2 validation)
- Phase 3: Design cross-repo validation scheme (Stage 3 validation)

---

## Discussion Statistics

- **Total Exchanges:** 15
- **Personas Engaged:** 6 (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex)
- **Convergence Reason:** Formally specified falsifiable pipeline with explicit causal model, strict success criteria, and per-task safety guarantees
- **Unanimous Agreement:** Four-stage validation pipeline is rigorous, per-task constraints essential, built-in fail-safes ensure value either way
- **Remaining Concerns:** Threshold stringency (Prof. Rex), efficiency measurement reliability (Prof. Pax), theory formalization (Prof. Rex)

---

*Phase 2A-Dialogue Complete — Ready for Phase 2B Verification Protocol Design*
