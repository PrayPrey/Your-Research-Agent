# Phase 2B: Hypothesis Verification Plan
Generated: 2026-08-19
Main Hypothesis: h-c1

## Executive Summary

This verification plan decomposes the main hypothesis (model-specific coupling fingerprints across trustworthiness dimensions) into 4 testable sub-hypotheses with clear success criteria, gate enforcement, and routing logic. The plan addresses all critical objections from Phase 2A discussion and establishes rigorous validation gates to ensure honest failure recording.

**Main Hypothesis:**
> LLMs exhibit model-specific behavioral coupling patterns across trustworthiness dimensions (truthfulness, robustness, fairness, safety, privacy), measurable via co-occurrence analysis on existing multi-dimensional benchmarks using only API access, without requiring internal model states or synthetic data.

**Key Innovation:** Coupling as model fingerprint (architectural/training signature), enabling evidence-based model selection for deployment.

---

## Sub-Hypotheses Overview

| ID | Statement | Type | Gate | Prerequisites |
|----|-----------|------|------|---------------|
| H-E1 | At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair | EXISTENCE | MUST_WORK | [] |
| H-M1 | Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25) | MECHANISM | MUST_WORK | [h-e1] |
| H-M2 | At least two models show ≥3 dimension pairs with medium-to-strong coupling (phi ≥ 0.3) | MECHANISM | SHOULD_WORK | [h-e1, h-m1] |
| H-C1 | Coupling matrices differ across models (Mantel r < 0.7 for ≥1 model pair) | CONDITION | SHOULD_WORK | [h-e1, h-m2] |

**Phase 5 Eligibility:** Requires H-E1 + H-M1 PASS (MUST_WORK gates)

---

## Detailed Sub-Hypothesis Specifications

### H-E1: Coupling Exists (MUST_WORK)

**Statement:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair.

**Rationale:** Foundational existence claim. Without detectable coupling, entire research direction fails.

**Success Criterion:**
- ≥1 model shows ≥1 dimension pair with:
  - Phi coefficient ≥ 0.3 (medium effect size)
  - Chi-square p < 0.01 (statistical significance)

**Measurement:**
- Construct 10 pairwise 2×2 contingency tables per model (5 dimensions → C(5,2) = 10 pairs)
- Calculate phi coefficient and chi-square test for each pair
- Test on 3 models: GPT-4, Claude 3, Llama 3

**Dataset:** MMTrustEval framework, 500 instances per model

**Failure Implications:**
- All dimension pairs show phi < 0.3 OR p > 0.05
- Interpretation: Trustworthiness dimensions are behaviorally independent
- Route to Phase 0: New research direction needed (dimension independence exploitation)

**Gate Type:** MUST_WORK (failure blocks Phase 5)

---

### H-M1: Difficulty-Independent Coupling (MUST_WORK)

**Statement:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25), indicating shared vulnerability mechanisms rather than spurious difficulty correlation.

**Rationale:** Addresses critical objection from Prof. Rex - hard prompts might fail on all dimensions, creating spurious coupling.

**Success Criterion:**
- Partial phi ≥ 0.25 for ≥2 dimension pairs after controlling for model confidence scores
- Coupling survives BOTH partial correlation AND difficulty-stratified analysis

**Measurement:**
- Primary: Partial correlation controlling for model confidence scores (logit probabilities)
- Secondary: Difficulty-stratified analysis (measure coupling within difficulty quartiles)
- Qualitative validation: High-coupling instances should show shared semantic features (embedding similarity > 0.7)

**Dataset:** Same 500 instances from H-E1 + confidence scores

**Difficulty Proxy:**
- Model confidence scores (logit probabilities) proxy instance difficulty
- Validation: Compare with human difficulty ratings if available

**Failure Implications:**
- Partial phi < 0.2 for all pairs → coupling was spurious difficulty correlation
- Route to Phase 2A-Dialogue: Mechanism revision needed (difficulty-adjusted coupling thresholds)
- Alternative route (if modification fails): Phase 0

**Gate Type:** MUST_WORK (failure blocks Phase 5)

---

### H-M2: Multi-Pair Coupling (SHOULD_WORK)

**Statement:** At least two models show ≥3 dimension pairs with medium-to-strong coupling (phi ≥ 0.3).

**Rationale:** Strengthens claim beyond single isolated coupling. Demonstrates coupling is not rare edge case.

**Success Criterion:**
- ≥2 models show ≥3 dimension pairs with:
  - Phi coefficient ≥ 0.3
  - Chi-square p < 0.01

**Measurement:**
- Count dimension pairs meeting threshold per model
- Verify ≥2 models reach ≥3 pairs

**Dataset:** Same 500 instances from H-E1

**Failure Implications:**
- Coupling exists but rare (e.g., 1 model, 1-2 pairs)
- Interpretation: Coupling is detectable but limited generalization
- Does NOT block Phase 5 (SHOULD_WORK gate)
- Publishable as Tier 2 success (weaker contribution)

**Gate Type:** SHOULD_WORK (failure does NOT block Phase 5)

---

### H-C1: Model-Specific Fingerprints (SHOULD_WORK)

**Statement:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair), demonstrating model-specific fingerprints.

**Rationale:** Differentiates model-specific coupling (fingerprints) from universal coupling (architectural property). Enables deployment-critical model selection use case.

**Success Criterion:**
- Mantel test r < 0.7 between ≥1 model pair:
  - GPT-4 vs Claude 3
  - GPT-4 vs Llama 3
  - Claude 3 vs Llama 3

**Measurement:**
- Construct 10×10 coupling matrix per model (phi values for 10 dimension pairs)
- Perform Mantel test for pairwise model comparison
- Matrix correlation r < 0.7 indicates distinct coupling profiles

**Dataset:** Same coupling measurements from H-E1

**Failure Implications:**
- All model pairs show Mantel r > 0.9 → models exhibit identical coupling patterns
- Reframe contribution: "Universal coupling architecture" (transformer fundamental property)
- Does NOT block Phase 5 (SHOULD_WORK gate)
- Still publishable (alternative framing, first coupling characterization)

**Gate Type:** SHOULD_WORK (failure does NOT block Phase 5)

---

## Dependency Graph

```
H-E1 (READY) ──> H-M1 ──> H-M2 ──> H-C1
                   │         │
                   │         └──> Phase 5 (if H-E1 + H-M1 PASS)
                   │
                   └──> Phase 5 (minimum eligibility)
```

**Execution Order:** Sequential (each hypothesis depends on prior completion)

**Critical Path:** H-E1 → H-M1 → (Phase 5 eligible)

**Parallelization:** None within this DAG

---

## Risk Analysis Summary

### Critical Risks (MUST_WORK Gate Blockers)

**R5: Null Result on H-E1 (30% likelihood)**
- No dimension pairs show phi ≥ 0.3
- Mitigation: Tier 3 success criterion (negative result publishable)
- Route: Phase 0

**R6: Coupling Disappears with Difficulty Control (40% likelihood)**
- Partial phi < 0.2 for all pairs
- Mitigation: Qualitative validation, stratified analysis
- Route: Phase 2A-Dialogue or Phase 0

**R2: Difficulty Proxy Validity (60% likelihood)**
- Model confidence scores may not validly proxy difficulty
- Mitigation: Use both partial correlation AND stratified analysis
- Validation: Compare with human ratings

**Combined MUST_WORK Failure Probability:** ~58%

### Managed Risks (SHOULD_WORK Gates)

**R7: Weak Effect Sizes (30% likelihood)**
- Phi values 0.15-0.25
- Impact: Tier 2 success (weaker contribution)
- Does NOT block Phase 5

**R8: Cross-Model Homogeneity (40% likelihood)**
- Mantel r > 0.9 (identical patterns)
- Mitigation: Reframe as "universal coupling"
- Does NOT block Phase 5

---

## Success Tier Matrix

### Tier 1: Full Success
**Criteria:**
- H-E1 PASS: ≥2 models show ≥3 pairs with phi ≥ 0.3, p < 0.01
- H-M1 PASS: Partial phi ≥ 0.25 for ≥2 pairs
- H-M2 PASS: Multi-pair generalization confirmed
- H-C1 PASS: Mantel r < 0.7 (model-specific)

**Contribution:** "Model-specific coupling fingerprints for evidence-based model selection"

**Phase 5:** Proceed to baseline comparison

---

### Tier 2: Partial Success
**Criteria:**
- H-E1 PASS: ≥1 model shows ≥1 pair with phi ≥ 0.3, p < 0.01
- H-M1 PASS: Partial phi ≥ 0.25
- H-M2 FAIL: Limited generalization
- H-C1 FAIL OR PASS: Either framing works

**Contribution:** "Coupling phenomenon detected, limited generalization OR universal coupling architecture"

**Phase 5:** Proceed to baseline comparison

---

### Tier 3: Negative Result
**Criteria:**
- H-E1 FAIL: No significant coupling
- OR H-M1 FAIL: Coupling disappears with difficulty control

**Contribution:** "Empirical evidence for dimensional independence (deployment reassurance)"

**Routing:** Phase 0 (research direction refuted)

---

## Routing Logic

### Decision Point 1: After H-E1 Validation

**PASS (phi ≥ 0.3, p < 0.01):**
- Continue to H-M1

**FAIL (no significant coupling):**
- Route to Phase 0
- Reason: Foundational claim refuted
- Lesson: Trustworthiness dimensions are independent
- Serena memory: `failure_h-e1.md`

---

### Decision Point 2: After H-M1 Validation

**PASS (partial phi ≥ 0.25):**
- Continue to H-M2
- Phase 5 eligibility ACHIEVED

**PARTIAL (partial phi 0.15-0.24):**
- Route to Phase 2A-Dialogue
- Reason: Mechanism needs revision (difficulty-adjusted thresholds)
- Serena memory: `failure_h-m1.md`
- Modification attempt: 1 (max)

**FAIL (partial phi < 0.15):**
- Route to Phase 0
- Reason: Coupling was spurious difficulty correlation
- Lesson: Difficulty confound dominates trustworthiness coupling
- Serena memory: `failure_h-m1.md`

---

### Decision Point 3: After H-M2/H-C1 Validation

**H-M2/H-C1 PASS:**
- Tier 1 success → Phase 5

**H-M2 OR H-C1 FAIL:**
- Tier 2 success → Phase 5
- Does NOT block progression (SHOULD_WORK gates)

---

## Timeline & Resource Estimates

**Phase 2C (Experiment Design):** 11 hours (~2 workdays)
- H-E1: 4h, H-M1: 3h, H-M2: 2h, H-C1: 2h

**Phase 3 (Implementation Planning):** 16 hours (~2 workdays)
- H-E1: 6h, H-M1: 4h, H-M2: 3h, H-C1: 3h

**Phase 4 (PoC Validation):** 32 hours (~4 workdays)
- H-E1: 12h, H-M1: 8h, H-M2: 6h, H-C1: 6h

**Phase 5 (Baseline Comparison):** 20 hours (~2.5 workdays)

**Total:** ~79 hours (11 workdays, ~2.2 weeks)

**Contingency Buffer:** +16 hours (~2 workdays) → 13 workdays worst-case

**API Cost Estimate:** $150-200 (7,500 API calls across 3 models)

---

## Qualitative Validation (Prof. Rex's Recommendation)

### Pre-Registered Criteria

**For H-M1 (Difficulty-Independent Coupling):**
- Select top-10 highest-coupling instance pairs per dimension pair
- Compute embedding similarity (sentence-transformers)
- Threshold: embedding similarity > 0.7 for high-coupling instances
- Interpretation:
  - Similarity > 0.7 → Coupling reflects shared semantic/structural features
  - Similarity < 0.7 → Coupling may be statistical noise despite significance

### Validation Process

1. Extract high-coupling instance pairs (top-10 per dimension pair)
2. Embed instances using sentence-transformers (all-MiniLM-L6-v2)
3. Calculate pairwise cosine similarity
4. Report mean similarity per dimension pair
5. Flag dimension pairs with similarity < 0.7 as "coupling present but not interpretable"

### Failure Handling

**If qualitative validation fails (similarity < 0.7):**
- Downgrade contribution claim: "Co-occurrence phenomenon requiring further investigation"
- Do NOT claim "shared vulnerabilities" (mechanism unverified)
- Report honestly in Phase 6 paper

---

## Controlled Variables (from Phase 2A)

**Fixed Across All Hypotheses:**
- Dataset: MMTrustEval framework
- Models: GPT-4, Claude 3, Llama 3
- Dimensions: truthfulness, robustness, fairness, safety, privacy
- Sample Size: 500 instances per model
- Evaluation Mode: API-only (no internal states)

**Analysis Methods:**
- Phi coefficient (effect size)
- Chi-square test (significance)
- Partial correlation (difficulty control)
- Mantel test (cross-model comparison)

---

## Phase 5 Baseline Comparison Context

**DETERMINES_SUCCESS Gate:**
After all sub-hypotheses validated (H-E1 + H-M1 minimum), Phase 5 compares our coupling-based approach against baseline trustworthiness evaluation methods.

**Success Criterion:**
- Our method outperforms baseline on deployment-relevant metrics (compound risk detection, model selection accuracy)

**Failure Routing:**
- PARTIAL (baseline wins) → Route to Phase 0
- Reason: Approach fundamentally inferior to baseline
- Lesson: Independent dimension evaluation sufficient
- Serena memory: `phase5_failure_h-c1.md`

---

## ROUTE_TO_0 Compliance Check

✅ **No layer-specific mechanisms:** Behavioral analysis only (API outputs)
✅ **Real data:** MMTrustEval benchmark instances (not synthetic)
✅ **Observable behaviors:** Binary pass/fail labels + confidence scores
✅ **Architecture-agnostic:** Tests 3 model families (GPT-4, Claude 3, Llama 3)
✅ **Existing benchmarks:** MMTrustEval framework validated and pip-installable

**Pipeline Feasibility:**
✅ No new benchmarks required
✅ No synthetic data generation
✅ No human evaluation
✅ Testable immediately (framework, APIs, statistical tools exist)

---

## Next Steps (Automatic Execution in UNATTENDED Mode)

1. **Phase 2B Complete → Phase 2C Start**
   - Generate experiment design for H-E1 (first READY hypothesis)
   - Use exa-search and scholar-search MCPs for coupling detection literature

2. **Phase 2C → Phase 3 → Phase 4 Loop**
   - Execute hypothesis loop sequentially (H-E1 → H-M1 → H-M2 → H-C1)
   - Enforce gate checks at end of each Phase 4 validation

3. **After Phase 4 Complete → Phase 5**
   - Baseline comparison (DETERMINES_SUCCESS gate)

4. **Phase 5 PASS → Phase 6**
   - Paper writing with validated findings

5. **Phase 5 PARTIAL/FAIL → Phase 0**
   - Route to new research direction with failure context preserved

---

## References to Supporting Documents

- **Hypothesis Inventory:** `hypothesis_inventory.md`
- **Risk Analysis:** `risk_analysis.md`
- **Dependency DAG:** `dependency_dag.md`
- **Timeline Planning:** `timeline_gantt.md`
- **Dialectical Analysis:** `dialectical_analysis.md`

---

**Phase 2B Status:** COMPLETE
**Phase 2C Trigger:** Automatic (UNATTENDED mode)
**Next Hypothesis:** H-E1 (READY)
