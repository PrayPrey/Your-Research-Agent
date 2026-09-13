# Phase 2B: Verification Plan
## Proxy Validation for Multi-Objective Code Generation RL

**Generated**: 2026-07-09  
**Main Hypothesis**: H-ProxyValidation-v1  
**Archon Project ID**: 741b39b6-61c9-4277-a967-99f025130b49

---

## Executive Summary

This verification plan decomposes the main hypothesis into **6 testable sub-hypotheses** structured around a four-stage validation pipeline. The plan follows a sequential validation approach where early-stage failures (measurement reliability, conditional independence) prevent wasted investment in later stages (RL training, Pareto analysis).

**Core Innovation**: Establishes construct validation as a prerequisite for proxy-based optimization, converting reward engineering from heuristic art to scientifically validated methodology.

**Total Timeline**: 10-12 weeks  
**Critical Path**: H-E1 → H-E2 → H-M1 → H-M2 → H-C2

---

## Main Hypothesis

**ID**: H-ProxyValidation-v1  
**Confidence**: 0.75

**Statement**: Under code generation tasks with existing test suites (HumanEval, SWE-bench, MBPP), if models are trained via constrained multi-objective RL using validated proxy metrics (those passing measurement reliability, conditional independence, and cross-domain generalization stages), then they will achieve ≥5% improvement in downstream developer acceptance outcomes (edit distance to accepted solutions, PR acceptance rates) while maintaining per-task execution pass rates within 5% of baseline, because validated proxies capture non-redundant quality dimensions (structural similarity, runtime efficiency, style conformity) that influence developer acceptance beyond execution correctness alone.

**Alternative Hypothesis (H₀)**: After controlling for execution correctness, proxy metrics do NOT explain significant additional variance (ΔR² < 0.03, p > 0.01) in behavioral outcomes, OR constrained multi-objective models do NOT achieve ≥5% improvement while maintaining per-task execution regressions ≤5%.

---

## Sub-Hypothesis Inventory

### 1. H-E1: Proxy Measurement Reliability (Stage 1)
- **Type**: EXISTENCE
- **Gate**: MUST_WORK
- **Prerequisites**: None (READY to start)
- **Archon Task ID**: af62f509-0467-4742-b644-62e460ed8f16

**Statement**: Proxy metrics (CodeBLEU, normalized runtime ratio, learned PR-style score) demonstrate measurement reliability sufficient for optimization.

**Success Criteria**:
- Intra-implementation coefficient of variation (CV) ≤ 5%
- Inter-complexity-class separability: Cohen's d ≥ 0.8 (e.g., O(n) vs O(n²))
- Cross-hardware rank correlation: Spearman ρ ≥ 0.8

**Experimental Method**:
- Calibration study: 50 HumanEval problems, 10 solutions × 5 runs each
- Controlled asymptotic tasks: 50 synthetic problems with known optimal complexity classes
- Cross-hardware validation: AWS g4dn.xlarge vs local GPU

**Timeline**: 2 weeks

**Falsification Trigger**: If efficiency metric fails CV ≤5% threshold OR complexity class separation fails Cohen's d ≥0.8, drop efficiency from optimization and continue with remaining proxies.

---

### 2. H-E2: Proxy Conditional Independence (Stage 2)
- **Type**: EXISTENCE
- **Gate**: MUST_WORK
- **Prerequisites**: H-E1
- **Archon Task ID**: b379c503-78eb-4419-96f0-61d11ef1b1bd

**Statement**: Validated proxies (from Stage 1) explain additional variance in developer acceptance outcomes beyond execution correctness, with effects persisting within perfect-execution stratum.

**Success Criteria**:
- Hierarchical regression: ΔR² ≥ 0.03 after controlling for execution pass rate (p < 0.01)
- Stratified analysis: Effect persists within 100%-correct stratum (proxy ΔR² ≥ 0.03)
- Structural equation modeling (SEM) confirms causal path: Proxy → Developer Acceptance (independent of Execution)

**Experimental Method**:
- Dataset: SWE-bench training set (PR acceptance labels, edit distance to accepted solutions)
- Model: `Outcome ~ Execution + Proxy` vs `Outcome ~ Execution`
- Stratification: Within-band analysis for [0-25%, 25-50%, 50-75%, 75-99%, 100%] execution correctness

**Timeline**: 2 weeks

**Falsification Trigger**: If ALL proxies show ΔR² < 0.03 within perfect-execution stratum, hypothesis simplifies to execution-sufficiency. Route to Phase 0 for new direction.

---

### 3. H-M1: Constrained Multi-Objective RL Feasibility
- **Type**: MECHANISM
- **Gate**: MUST_WORK
- **Prerequisites**: H-E2
- **Archon Task ID**: 55716450-1e12-4bd2-9376-390ba9c80535

**Statement**: Constrained multi-objective RL using Lagrangian relaxation can simultaneously optimize validated proxies while enforcing per-task execution constraints.

**Success Criteria**:
- ≤10% of problems show >5% pass rate regression during training
- Per-task constraint monitoring functional (per-problem Lagrangian penalty adjustment)
- Training converges within 1,000 GPU hours

**Experimental Method**:
- Infrastructure: OpenRLHF with Lagrangian relaxation
- Benchmarks: HumanEval (164 problems), MBPP (500 problems)
- Monitoring: Per-problem pass rate tracked every 100 training steps
- Constraint: `λ_i * max(0, baseline_pass_i - current_pass_i - 0.05)` for problem i

**Timeline**: 4 weeks

**Falsification Trigger**: If >10% of problems violate execution constraint, constraint enforcement fails. Attempt tighter Lagrangian coefficients (1 modification attempt), then route to Phase 2A-Dialogue for mechanism revision.

---

### 4. H-M2: Pareto Dominance Demonstration
- **Type**: MECHANISM
- **Gate**: MUST_WORK
- **Prerequisites**: H-M1
- **Archon Task ID**: 495aa585-b2e0-4076-bf01-10f0c83f6acf

**Statement**: Constrained multi-objective models (Condition C) achieve Pareto dominance over execution-only (Condition A) and sequential optimization (Condition B) baselines.

**Success Criteria**:
- Edit distance reduced by ≥5% vs Condition A on SWE-bench test set
- PR acceptance rate improved by ≥5 percentage points
- Hidden test pass rate maintained (no significant degradation, p > 0.05)
- Pareto frontier: Condition C dominates A and B (no baseline achieves superior secondary metrics without execution degradation)

**Experimental Method**:
- Condition A: CodeRL (execution-only reward)
- Condition B: Execution training → preference fine-tuning (sequential)
- Condition C: Constrained multi-objective (simultaneous)
- Fractional factorial ablation: 2³ design (CodeBLEU × Efficiency × Style) to test interaction effects

**Timeline**: 2 weeks

**Falsification Trigger**: If Condition C does NOT dominate A and B on Pareto frontier (no ≥5% secondary improvement without execution violation), multi-objective approach provides no benefit. Route to Phase 0.

---

### 5. H-C1: Cross-Domain Generalization (Stage 3)
- **Type**: CONDITION
- **Gate**: SHOULD_WORK
- **Prerequisites**: H-E2
- **Archon Task ID**: 67696901-bd65-48e1-b88d-597d7e082262

**Statement**: Proxy signals generalize across repositories, demonstrating domain-general quality capture rather than repository-specific artifacts.

**Success Criteria**:
- Leave-cluster-out validation: Cross-repo R² drop < 50% (train on 8 repos, test on 4 disjoint)
- Ensemble disagreement ≤ 20% on quality feature rankings
- Adversarial style pair analysis: Verbose repos (Django) vs terse repos (Flask) show consistent quality orderings

**Experimental Method**:
- Dataset: SWE-bench (12 diverse Python repositories)
- Split: Train {Django, NumPy, SciPy, Matplotlib, Pandas, Requests, Sympy, pytest} → Test {Flask, scikit-learn, Sphinx, Werkzeug}
- Ensemble: 3 learned PR-style models with different architectures

**Timeline**: 2 weeks (parallel with H-M1)

**Falsification Trigger**: If cross-repo R² drop >50% OR ensemble disagreement >20%, style signals are repository-specific. Switch to domain-specific ensemble approach (still valid, but limited generalization claim).

---

### 6. H-C2: Temporal Stability Validation
- **Type**: CONDITION
- **Gate**: SHOULD_WORK
- **Prerequisites**: H-M2
- **Archon Task ID**: 7814f305-bbc5-4773-bc6d-49327a9055be

**Statement**: Improvements persist on temporally held-out benchmarks, confirming proxies capture enduring quality rather than temporal artifacts.

**Success Criteria**:
- Post-2023 SWE-bench issues: ≥5% secondary metric improvement maintained
- Effect size (Cohen's d) remains ≥ 0.5 on temporal hold-out
- No significant interaction between training-test temporal gap and improvement magnitude

**Experimental Method**:
- Training data: SWE-bench issues before 2023-01-01
- Test data: SWE-bench issues after 2023-01-01 (temporal hold-out)
- Control: Verify baseline methods also maintain performance (not just ours degrading)

**Timeline**: 1 week

**Falsification Trigger**: If improvements disappear on post-2023 data (effect size drops below 0.3), proxies optimize benchmark artifacts not enduring quality. Limits generalization claims to pre-2023 period.

---

## Dependency Graph (DAG)

```
                    H-E1 [READY]
                (Measurement Reliability)
                         |
                         v
                    H-E2 [NOT_STARTED]
            (Conditional Independence)
                    /        \
                   /          \
                  v            v
         H-M1 [NOT_STARTED]   H-C1 [NOT_STARTED]
      (Constrained RL)      (Cross-Domain Gen.)
                  |
                  v
         H-M2 [NOT_STARTED]
      (Pareto Dominance)
                  |
                  v
         H-C2 [NOT_STARTED]
      (Temporal Stability)
```

**Critical Path**: H-E1 → H-E2 → H-M1 → H-M2 → H-C2 (10 weeks)  
**Parallel Opportunity**: H-C1 can run concurrently with H-M1 (saves 2 weeks)

---

## Risk Analysis & Mitigation

### R1: Proxies Fail Conditional Independence (H-E2)
- **Severity**: High
- **Likelihood**: Medium
- **Impact**: Core hypothesis collapses to execution-sufficiency
- **Mitigation**: Built-in fail-safe — negative result is publishable ("Execution correctness suffices for test-covered domains")
- **Linked Hypotheses**: H-E2 (direct), H-M1/H-M2 (blocked if failed)

### R2: Efficiency Measurements Too Noisy (H-E1)
- **Severity**: Medium
- **Likelihood**: Medium
- **Impact**: Efficiency proxy dropped from optimization
- **Mitigation**: Calibration study catches this BEFORE RL training investment; continue with CodeBLEU + style
- **Linked Hypotheses**: H-E1 (direct)

### R3: Style Signals Repository-Specific (H-C1)
- **Severity**: Medium
- **Likelihood**: Low
- **Impact**: Limits generalization claims
- **Mitigation**: Switch to domain-specific ensemble approach; still valid contribution with scoped claims
- **Linked Hypotheses**: H-C1 (direct)

### R4: Per-Task Execution Constraints Violated (H-M1)
- **Severity**: Critical
- **Likelihood**: Low
- **Impact**: Safety guarantee fails; cannot proceed to deployment claims
- **Mitigation**: Tighter Lagrangian penalty coefficients; 1 modification attempt, then route to Phase 2A-Dialogue
- **Linked Hypotheses**: H-M1 (direct), H-M2 (blocked if failed)

### R5: Temporal Generalization Fails (H-C2)
- **Severity**: High
- **Likelihood**: Medium
- **Impact**: Proxies optimize benchmark artifacts not enduring quality
- **Mitigation**: Pivot to investigating temporal domain boundaries rather than claiming universal improvement
- **Linked Hypotheses**: H-C2 (direct)

---

## Timeline & Resource Allocation

### Phase 2C: Experiment Design (Sub-hypotheses)
- **Duration**: 1 week
- **Deliverables**: 6 experiment design documents (one per sub-hypothesis)

### Phase 3: Implementation Planning
- **Duration**: 2 weeks
- **Deliverables**: PRD, Architecture docs, Task breakdowns

### Phase 4: PoC Implementation & Validation
- **Sequential Execution** (hypothesis loop):
  - H-E1: 2 weeks
  - H-E2: 2 weeks
  - H-M1 & H-C1: 4 weeks (parallel)
  - H-M2: 2 weeks
  - H-C2: 1 week
- **Total**: 11 weeks
- **Compute**: ~1,000 GPU hours (standard academic allocation)

### Phase 5: Baseline Comparison
- **Duration**: 1 week
- **DETERMINES_SUCCESS gate**: Compare best model from Phase 4 against execution-only baseline from existing repo

### Total Pipeline Duration: 15-16 weeks (Phase 2C through Phase 5)

---

## Gate Strategy

### MUST_WORK Gates (Foundation Hypotheses)
- **H-E1**: If measurement reliability fails, proxies are unusable → Drop unreliable proxies, continue with validated subset
- **H-E2**: If conditional independence fails, proxies are redundant → Route to Phase 0 (execution-sufficiency finding)
- **H-M1**: If constraint enforcement fails, safety guarantee invalid → 1 modification attempt, then Phase 2A-Dialogue
- **H-M2**: If Pareto dominance fails, multi-objective provides no benefit → Route to Phase 0

**Failure Handling**: MUST_WORK PARTIAL → 1 modification attempt; MUST_WORK FAIL → Route to Phase 0

### SHOULD_WORK Gates (Scoping Conditions)
- **H-C1**: If cross-domain fails, limits generalization claims → Switch to domain-specific approach
- **H-C2**: If temporal fails, scopes claims to training period → Publish with temporal boundary acknowledgment

**Failure Handling**: SHOULD_WORK failures do NOT block Phase 5; they scope/qualify claims

---

## Controlled Variables (Experimental Hygiene)

From Phase 2A refinement:
- **Base Model**: Same pretrained checkpoint across all conditions (e.g., CodeLlama-7B-Instruct)
- **Hardware**: Containerized execution with deterministic seeds, fixed GPU/CPU allocation
- **Benchmarks**: Fixed train/test splits for HumanEval, MBPP, SWE-bench
- **Constraint Threshold**: ≤5% per-task pass rate regression (constant across experiments)

---

## Dialectical Synthesis

### Tension 1: Proxy Independence vs Redundancy
- **Thesis** (Dr. Nova, Dr. Ally): Proxies capture quality dimensions beyond execution
- **Antithesis** (Prof. Rex): Proxies are conditionally redundant within perfect-execution stratum
- **Synthesis**: H-E2 stratified regression resolves empirically — if effects vanish in 100%-correct stratum, hypothesis simplifies to execution-sufficiency (publishable negative result)

### Tension 2: Simultaneous vs Sequential Optimization
- **Thesis** (Prof. Vera): Multi-objective simultaneous optimization needed for synergy
- **Antithesis** (Prof. Pax): Sequential (execution then preference) may suffice
- **Synthesis**: H-M2 fractional factorial design tests interaction effects — if <5% interaction variance, simplify to additive model (less complex, still valid)

### Tension 3: Efficiency Signal vs Noise
- **Thesis** (Dr. Ally): Normalized runtime ratios capture algorithmic quality
- **Antithesis** (Prof. Rex): Measurement noise swamps signal under realistic conditions
- **Synthesis**: H-E1 calibration study (CV ≤5%) determines viability BEFORE RL investment — if noisy, drop efficiency, continue with CodeBLEU + style

---

## Success Scenarios

### Full Success (All MUST_WORK Gates Pass)
1. H-E1: All three proxies pass reliability thresholds
2. H-E2: Proxies demonstrate conditional independence (ΔR² ≥ 0.03 within perfect-execution stratum)
3. H-M1: Constrained RL maintains execution constraints
4. H-M2: Pareto dominance demonstrated (≥5% secondary improvement, no execution degradation)
5. Phase 5: Outperforms baseline → **Proceed to Phase 6 (Paper Writing)**

**Impact**: Establishes new evidentiary standard for auxiliary objectives in code generation; validation framework becomes reusable methodology

### Partial Success (Some SHOULD_WORK Failures)
- H-C1 fails: Style signals repository-specific → Domain-specific ensemble approach
- H-C2 fails: Temporal boundaries identified → Scoped claims to training period
- **Still proceeds to Phase 5** if MUST_WORK gates pass

**Impact**: Narrower claims but still publishable contribution

### Informative Failure
- H-E2 fails (conditional independence): **Execution correctness suffices for test-covered domains**
- H-M2 fails (Pareto dominance): **Multi-objective coupling unnecessary — additive model works**
- **Route to Phase 0 for new direction, but negative result publishable**

**Impact**: Prevents field from pursuing false signals; closes research direction responsibly

---

## Novelty Positioning

### Methodological Contribution
**Four-stage validation pipeline as reusable framework**:
1. Measurement reliability (Stage 1 / H-E1)
2. Conditional independence (Stage 2 / H-E2)
3. Cross-domain generalization (Stage 3 / H-C1)
4. Constrained optimization (Stage 4 / H-M1, H-M2)

**Key Insight**: Prior work bundles metrics and validates post-hoc; this work tests independence BEFORE optimization investment.

### Empirical Contribution
- **If successful**: Validated proxies demonstrate non-redundant quality dimensions → Multi-dimensional evaluation becomes standard
- **If proxies fail**: Rules out false signals → Saves field from unmeasurable quality pursuits

**Either outcome advances understanding of developer preference structure.**

---

## Related Work Positioning

**Builds On**:
- CodeRL (Le et al., NeurIPS 2022): Execution-only RL baseline
- Lei Chen et al. (2025): Multi-granularity rewards break plateaus
- Becker et al. (2025): 19% slowdown despite correctness motivates efficiency dimension

**Differs From**:
- CodeUltraFeedback, SEAlign: No pre-optimization proxy validation, global constraints only
- Prior multi-objective RL: No conditional independence testing, average-case metrics mask tail failures

**Closes Gap**: Integration of execution feedback with multi-dimensional alignment via validated construct framework

---

## Next Steps (Phase 2C)

For each sub-hypothesis, generate detailed experiment design document specifying:
1. Exact dataset splits and sample sizes
2. Model architectures and hyperparameters
3. Evaluation metrics and statistical tests
4. Code dependencies and environment setup
5. Expected outputs and visualization plans

**Order of Design**:
1. H-E1 (READY to start immediately)
2. H-E2 (depends on H-E1 proxy selection)
3. H-M1 & H-C1 (both depend on H-E2, can design in parallel)
4. H-M2 (depends on H-M1 infrastructure)
5. H-C2 (depends on H-M2 trained models)

---

## Archon Project Tracking

- **Project ID**: 741b39b6-61c9-4277-a967-99f025130b49
- **Project Title**: Anonymous Pipeline: Proxy Validation for Multi-Objective Code Generation RL
- **Phase Tasks Created**: 11 pipeline-level phase tasks (Phase 0 through Phase 6.5.1)
- **Sub-Hypothesis Tasks Created**: 6 parent tasks (H-E1 through H-C2)

All tasks are tracked in Archon MCP server and linked to verification_state.yaml via metadata.hypothesis_task_mapping.

---

**Document Status**: Phase 2B Complete  
**Next Workflow**: Phase 2C Experiment Design (6 sub-hypotheses)  
**Estimated Start**: Immediate (H-E1 is READY)
