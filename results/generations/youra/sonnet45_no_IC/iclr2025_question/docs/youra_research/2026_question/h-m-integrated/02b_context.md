# Phase 2B Context: h-m-integrated

**Generated:** 2026-07-13
**Source:** 02b_verification_plan.md (Section 2.2)

---

## Hypothesis Information

**ID:** h-m-integrated
**Type:** Mechanism
**Gate:** MUST_WORK

**Statement**: Under foundation model uncertainty quantification settings, if we apply hierarchical Bayesian calibration (HBC) where consistency priors C(x) inform conformal calibration and statistical validation results update consistency thresholds (mutual calibration), then we achieve Expected Calibration Error (ECE) < 0.05 with 30-50% computational cost reduction vs. COIN-only while maintaining coverage ≥ 90%, because the three-step causal mechanism operates: (Step 1) Consistency sampling measures epistemic uncertainty producing prior C(x), (Step 2) Conformal prediction provides aleatoric bounds producing interval I(x), (Step 3) Hierarchical Bayesian updating creates co-calibration exploiting complementarity (0.3 < ρ < 0.7), where mutual calibration improves both signals beyond independent application.

**Rationale**: This hypothesis tests the complete 3-step causal chain from Phase 2A. It validates that joint calibration (not independent or cascade application) provides superior ECE with computational efficiency. This is the core HBC contribution—proving that Bayesian integration of complementary signals improves both consistency and conformal methods.

---

## Variables

**Independent Variables:**
- Calibration Method (4-level: SelfCheckGPT-only, COIN-only, Independent Cascade, HBC)
- Dataset Type (TruthfulQA/HH-RLHF/SQuAD)

**Dependent Variables:**
- Expected Calibration Error (ECE)
- Computational Cost (forward passes/1000 queries)
- Coverage (fraction y ∈ I(x))

**Controlled Variables:**
- Foundation Model (Llama-2-7B)
- Consistency Metric (NLI+BERTScore)
- Conformal Coverage Target (90%)

---

## Experimental Setup

### Dataset
- **Primary:** TruthfulQA (epistemic uncertainty)
- **Secondary:** HH-RLHF (aleatoric uncertainty), SQuAD (mixed uncertainty)
- **Source:** TruthfulQA: https://github.com/sylinrl/TruthfulQA; HH-RLHF: Anthropic; SQuAD: Stanford
- **Sample Size:** n ≥ 1000 test samples per dataset

### Model
- **Name:** Llama-2-7B
- **Type:** Autoregressive transformer LLM
- **Source:** Meta AI, HuggingFace Hub
- **Justification:** Widely benchmarked, supports sampling (required for consistency methods), manageable size for multi-sample experiments

### Baselines
1. **SelfCheckGPT-only** (Manakul et al., 2023) - Consistency-based hallucination detection
2. **COIN-only** (Wang et al., 2025) - Conformal prediction with FDR control
3. **Independent Cascade** (SelfCheckGPT → COIN) - Sequential application without joint calibration

**Best Baseline:** Independent cascade achieves ECE ~0.06-0.08 on TruthfulQA (to be validated)

---

## Verification Protocol

1. Implement four calibration methods (SelfCheckGPT-only, COIN-only, Independent Cascade, HBC) with identical train/val/test splits.
2. HBC implementation: Bayesian updating where C(x) informs conformal prior (epistemic → statistical direction), statistical validation updates consistency threshold (statistical → epistemic feedback).
3. Measure ECE (primary), computational cost (forward passes per 1000 queries), coverage (fraction y ∈ I(x)) on n≥1000 test samples per dataset.
4. Statistical comparison: two-tailed t-test comparing HBC vs. each baseline on ECE (SelfCheckGPT-only, COIN-only, Independent Cascade), require p<0.05 for all three.
5. Efficiency validation: HBC cost reduction ≥ 30% vs. COIN-only while maintaining coverage ≥ 90%.
6. Ablation study: test with ρ=0.2, 0.5, 0.8 to validate sweet spot dependency (ECE improvement should peak at ρ~0.5).

---

## Success Criteria (MUST_WORK Gate)

**Primary:**
- ECE_HBC < 0.05 AND significantly lower than all three baselines (p<0.05 for each pairwise comparison)

**Secondary:**
- Cost reduction 30-50% vs. COIN-only while coverage ≥ 90%

**Mechanism Validation:**
- Ablation shows ECE improvement peaks at ρ~0.5 (sweet spot dependency)

**Minimum Effect Size:**
- ECE improvement ≥ 0.01 vs. independent cascade (practical significance, not just statistical)

---

## Failure Response

**IF ECE improvement < 0.01 vs. independent cascade:**
→ Joint calibration adds no value → ABANDON HBC, report independent cascade as sufficient

**IF cost reduction < 20%:**
→ Efficiency claim invalid → PIVOT to "quality-only" contribution (drop efficiency claim from paper)

**IF coverage < 85%:**
→ Statistical guarantees violated → EXPLORE conformal recalibration or ABANDON coverage claim

**IF ablation shows no sweet spot dependency:**
→ Complementarity claim weak → REFINE theoretical model or ABANDON ρ-based mechanism

---

## Dependencies

**Prerequisites:** H-E1 (complementarity must be validated before testing joint calibration)

**Previous Hypothesis Results:** H-E1 completed with PASS status
- Correlation ρ(C,I) validated: 0.4633 (TruthfulQA), 0.4313 (HH-RLHF), 0.4351 (SQuAD)
- All values fall within sweet spot 0.3 < ρ < 0.7 ✅
- Statistical significance confirmed (p < 0.05 for all datasets) ✅
- **Implication:** Complementarity assumption validated, proceed with joint calibration

---

## Gate Status

**Type:** MUST_WORK
**Prerequisites Satisfied:** Yes (H-E1 PASS)
**Status:** Ready for Phase 2C experiment design
