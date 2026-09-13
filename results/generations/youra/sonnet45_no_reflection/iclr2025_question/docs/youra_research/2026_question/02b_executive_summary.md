# Executive Summary - Phase 2B Verification Plan

## Executive Summary

**Main Hypothesis:** Geometric features (PR, eigenvalue spectrum, condition number) from layers 24-31 hidden states correlate |ρ| > 0.4 with semantic entropy under epistemic uncertainty, enabling single-pass uncertainty detection via collapsed subspace mechanism.
- ID: H-GeometricUQ-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (75% scope reduction via BUILD_ON claims)
- Sub-Hypotheses: 3 total (H-E1: Existence, H-M-integrated: 4-step mechanism, H-C1: Architecture invariance)
- Phases: 3 phases over 6 weeks (Foundation → Mechanism → Boundary)
- Critical Gates: 3 decision points (Gate 1: MUST_WORK, Gate 2: MUST_WORK, Gate 2.5: SHOULD_WORK)

**Risk Assessment:** Medium-High
- Primary concerns: Layer selection arbitrary (R2), PR stability unproven (R3)
- Mitigation: Ablation studies (H-M), bootstrap validation (H-E1)

**Immediate Action:** Begin Phase 2C (Experiment Design) for H-E1, then Phase 3 (Implementation Planning)

---

## Key Achievements

**Verification Plan Deliverables:**
- 3 hypotheses with streamlined 40-50 line specifications
- Sequential dependency chain: H-E1 → H-M-integrated → H-C1
- 5 risks identified with mitigation strategies (2 high, 3 medium)
- Dialectical analysis balancing thesis (geometric features work) vs antithesis (spurious correlation)

**H0 Integration:**
- Null hypothesis: No significant correlation (|ρ| < 0.3 or p > 0.05) between geometric features and SE
- Addressed through falsification-first design with clear abandonment criteria

---

## Verification Execution Order

**Phase 1: Foundation** (Weeks 1-2)
- **H-E1:** Geometric-Semantic Entropy Correlation
  - Test: Spearman |ρ| > 0.4, p < 0.001, 95% CI excludes 0.3
  - Bootstrap validation: CV < 0.15 for PR stability
- **Gate 1:** MUST PASS
  - FAIL → ABANDON entire hypothesis
  - PASS → Proceed to mechanism validation

**Phase 2: Mechanism** (Weeks 3-5)
- **H-M-integrated:** Four-Step Causal Mechanism Chain
  - Test: Subspace collapse (PR_high < PR_low, p < 0.01), negative PR~SE correlation
  - Ablation: Layer ranges (16-23, 20-27, 24-31)
  - Control: Epistemic vs non-epistemic tasks
- **Gate 2:** MUST PASS
  - CRITICAL FAIL → PIVOT to black-box correlation without mechanistic understanding
  - PASS → Proceed to architecture generalization

**Phase 2.5: Boundary Condition** (Week 6)
- **H-C1:** Architecture Invariance
  - Test: |Δρ| ≤ 0.15 across Llama-2-7B and Llama-3-8B
  - Ablation: Fixed vs proportional layer selection
- **Gate 2.5:** SHOULD_WORK
  - FAIL → SCOPE to Llama-3 specific, document per-architecture calibration requirement
  - PASS → Architecture-invariant within Llama family

---

## Critical Decision Points

**1. Gate 1 (Foundation - Week 2):** H-E1 must demonstrate correlation
- **FAIL** (|ρ| < 0.3 or p > 0.05): STOP entire verification, geometric features don't proxy uncertainty
- **PASS**: Proceed to mechanism validation (Phase 2)

**2. Gate 2 (Mechanism - Week 5):** H-M-integrated must validate causal chain
- **CRITICAL FAIL** (wrong correlation direction): PIVOT to black-box correlation, abandon mechanistic interpretation
- **PARTIAL FAIL** (some ablation failures): Document limitations, scope appropriately
- **PASS**: Proceed to architecture generalization (Phase 2.5)

**3. Gate 2.5 (Boundary - Week 6):** H-C1 determines generalization scope
- **FAIL** (|Δρ| > 0.25): SCOPE to Llama-3 specific, note per-architecture calibration needed
- **PARTIAL** (0.15 < |Δρ| ≤ 0.25): Minor calibration needed but generalizes
- **PASS** (|Δρ| ≤ 0.15): Architecture-invariant, broad deployment viable

---

## Open Questions

From Phase 2A Section 5 (Phase 2B Readiness):
1. **Optimal layer range selection:** 24-31 vs alternatives - requires ablation study (addressed in H-M-integrated)
2. **Multi-metric combination strategy:** Linear combination vs PCA vs trained ensemble (future work post-H-E1)
3. **Cross-architecture validation protocol:** Llama → GPT-2/Mistral/Gemma (H-C1 addresses Llama-family only)
4. **Statistical stability guarantees:** Bootstrap CV < 0.15 for small-sample PR (addressed in H-E1)

---

## Recommendations

**1. Immediate Actions:**
- Begin Phase 2C (Experiment Design) for H-E1 with detailed protocol
- Set up measurement infrastructure: TruthfulQA dataset, Llama-3-8B-Instruct model, DeBERTa-NLI for SE computation
- Pre-compute ground truth SE for all TruthfulQA questions (reusable across hypotheses)

**2. Resource Allocation:**
- Allocate 6 weeks for critical path (no parallelization opportunities)
- Reserve 2-week buffer for failures and iterations
- GPU resources: 1x for Llama-3-8B-Instruct + 1x for Llama-2-7B (H-C1)
- Estimated total GPU hours: 12-18 hours

**3. Failure Management:**
- Document all gate failures with detailed diagnostics
- Execute PIVOT strategies: H-M failure → black-box correlation, H-C1 failure → Llama-3 scoping
- Preserve partial results: H-E1 success alone may warrant publication (geometric correlation without mechanism)

**4. Success Propagation:**
- H-E1 + H-M success → Interpretable uncertainty detection validated, proceed to production optimization
- All hypotheses pass → Architecture-invariant geometric UQ, broad Llama-family deployment viable
- Prepare Phase 5 (Baseline Comparison) if pipeline_options.skip_baseline_comparison = false

---

## Appendices

### A. Phase 2A Reference
- **Source:** `/docs/youra_research/20260512_question/03_refinement.yaml`
- **Hypothesis ID:** H-GeometricUQ-v1
- **Causal Chain:** 4 steps (epistemic uncertainty → subspace collapse → spectral signatures → SE proxy)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 3 (incremental mode)
- **Tools:** `mcp__clearThought__scientificmethod` (3x: H-E1, H-M-integrated, H-C1)
- **Call efficiency:** 4-6 calls target vs 10-14 comprehensive (75% reduction via Phase 2A pre-mapping)

### C. Verification State File
- **Output:** `verification_state.yaml` (generated in Step 10)
- **Purpose:** Hypothesis tracking for Phase 2C → 3 → 4 loop execution
- **Structure:** 3 hypotheses with READY status, sequential dependencies, gate conditions
