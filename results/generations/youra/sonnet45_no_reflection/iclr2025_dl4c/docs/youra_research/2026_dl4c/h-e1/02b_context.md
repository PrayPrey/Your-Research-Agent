# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-11
**Main Hypothesis:** Aspect-Factorized Multi-Objective Code Alignment
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under multi-objective code generation contexts with GitHub commit data (10K minimal-diff commits), if human expert modifications are analyzed via spectral decomposition of residual covariance matrices, then aspect-dominant directional structure will emerge with median cross-aspect coupling ≤0.2× primary effect and spectral gap λ₄/λ₅>2.0, because developers cognitively factorize programming concerns into separable dimensions.

### Type
EXISTENCE

### Rationale
This hypothesis validates the foundational empirical assumption that human code modifications exhibit separable structure across quality aspects. Without this separability in real data, the entire architectural factorization approach lacks empirical grounding.

---

## Verification Protocol

### Conceptual Test
1. Collect 10K minimal-diff commits (AST distance <20) from GitHub with aspect labels via message parsing + expert validation (n=500 subset for purity >70%)
2. Compute metrics: Δcorrectness (test pass rate), Δquality (SonarQube), Δsecurity (CodeQL alerts), Δefficiency (pytest-benchmark)
3. Perform residual covariance analysis after confound regression (edit size, file entropy), eigenanalysis, permutation test (1000 shuffles)
4. Measure directional stability via on-axis projection z-scores and leave-one-repo-out cross-validation
5. Validate commit purity via expert annotation; apply mixture modeling if purity <70%

### Success Criteria
- Primary: Cross-aspect coupling ≤0.2× (95% CI), spectral gap λ₄/λ₅>2.0 (exceeds 95th percentile of permutation null), on-axis projection z-score >2.0
- Secondary: Purity >70%, metric validation passed (ICC≥0.8, r≥0.7)

### Variables (if applicable)
- **Independent Variable:** Commit Type (categorical: security, refactor, performance, bugfix)
- **Dependent Variable:** Cross-Aspect Coupling (median ratio ≤0.2), Spectral Gap (λ₄/λ₅>2.0)
- **Controlled Variables:** Metric Reliability (ICC≥0.8, construct validity r≥0.7), Edit Size, File Entropy

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** GitHub Commit Corpus (Multi-Aspect Labeled)
- **Type:** standard (real-world commit data)
- **Source:** GitHub public repositories, filtered for minimal-diff commits (AST distance <20) with aspect labels (security, refactor, performance, bugfix)
- **Path:** To be mined via GitHub API + commit message analysis + expert validation subset (n=500)
- **Hypothesis Fit:** Provides real-world labeled data for empirical separability validation. Commit-level causal edits are natural experiments showing human expert aspect-specific modifications.

### Selected Model
- **Name:** CodeLlama-7B
- **Type:** Pretrained Code LLM
- **Source:** Meta AI open-source release
- **Hypothesis Fit:** Standard pretrained code model with sufficient capacity for LoRA adaptation. 7B size balances expressiveness with computational feasibility (~100 GPU-hours training budget).

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Weighted PPOCoder: Grid search over 25 weight combinations w∈[0,1]^4 for (correctness, quality, security, efficiency), train separate models to estimate Pareto frontier
- LoRA-only (no factorization): Standard LoRA fine-tuning with multi-objective loss but no architectural separation or orthogonality constraints
- LoRA + Orthogonality (no gating): LoRA adapters with L_ortho regularization but no learned routing - tests necessity of functional separation beyond geometric orthogonality

### Baseline Performance
Weighted PPOCoder: Grid search over 25 weight combinations

### Gap Analysis
H-E1 is an empirical analysis hypothesis (not a model comparison), so baseline methods serve as null hypothesis reference for Phase 5 comparison if H-E1 passes Gate 1.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** ABANDON architectural factorization → Publish negative result that multi-objective code alignment is intrinsically entangled → Pivot to co-adaptive methods

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 2 weeks (Phase 0: 2-3 days, Phase 1A: 5 days, Phase 1B: 2 days, Phase 2: 3 days, Phase 3: 3 days, Phase 4: Gate decision)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. H-M-Integrated (4-Step Causal Chain Mechanism) depends on H-E1 passing. If H-E1 fails, the entire pipeline stops.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** Will be updated by Phase 2C
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
