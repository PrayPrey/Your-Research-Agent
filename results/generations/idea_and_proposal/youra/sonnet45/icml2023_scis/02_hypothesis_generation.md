# Phase 2A Extended: Hypothesis Summary (Phase 2B Input)

**Date:** 2026-02-06
**Hypothesis ID:** H-IBTF-001
**Confidence:** 0.835 (HIGH)
**Source:** Phase 2A Round 1 - Invariance-Based Translation Framework
**Researcher:** Pray

---

## Hypothesis Statement

**Main Hypothesis:**

If machine learning models are trained under a unified framework that operationalizes spurious correlations as violations of probability distribution invariances across three dimensions (structural/causal, distributional/fairness, environmental/OOD), then the resulting models will achieve superior robustness to spurious correlations compared to single-dimension approaches, because invariance satisfaction across multiple constraint types bounds spurious correlation risk more tightly than any individual constraint alone.

**Core Innovation:** First formal unification of causal ML, algorithmic fairness, and OOD generalization via probability distribution invariance principle P(Y|X,C).

---

## Key Variables

| Variable | Type | Measurement | Expected Effect |
|----------|------|-------------|-----------------|
| Invariance Type Config | IV | {I_struct, I_dist, I_env} combinations | More constraints → lower spurious score |
| Weight Vector w | IV | [w₁, w₂, w₃], Σw=1 | Application-specific; learned from validation |
| Spurious Correlation Severity | DV | w₁·V_struct + w₂·V_dist + w₃·V_env | Primary outcome (minimize) |
| Worst-Group Accuracy | DV | min_g Acc(g) | Should increase vs. baselines |
| Cross-Domain Degradation | DV | 1 - (P_target/P_source) | Should decrease vs. baselines |

---

## Testable Predictions

**P1: Multi-Invariance Superiority**
- Worst-group accuracy: ≥ +5% absolute over best single-dimension baseline
- Cross-domain degradation: ≥ 15% relative reduction
- Intervention robustness: ≥ 25% KL divergence reduction

**P2: Translation Effectiveness**
- Translated methods achieve ≥ 85% of original method performance on target benchmarks

**P3: Weight Learning Generalization**
- Application-specific weights cluster by deployment type (clustering coefficient ≥ 0.7)

**Falsification:** Hypothesis falsified if multi-invariance performs worse than best single-constraint on ≥ 50% of multi-shift test scenarios.

---

## SOTA Baselines

| Method | Best Performance | Limitation |
|--------|-----------------|------------|
| DANN | PACS: 85.5% domain acc | Environmental only; no causal/fairness |
| IRM | ColoredMNIST: 70% test acc | Structural only; requires multiple envs |
| GroupDRO | Waterbirds: 91.4% worst-group | Distributional only; needs group labels |

**IBTF Target:** Exceed best specialized method on their own metrics + ≥10% on composite multi-shift metric.

---

## Sub-Hypotheses (Phase 2B Decomposition Preview)

**SH1 (Existence):** Triple-constraint achieves ≥15% lower spurious_score than best single-constraint
- Verification: Comparative experiments on 5 benchmarks
- Difficulty: MEDIUM

**SH2 (Mechanism):** Multi-invariance features have ≥40% lower mutual information with spurious attributes
- Verification: Feature importance + MI analysis
- Difficulty: MEDIUM

**SH3 (Comparison):** IBTF achieves ≥10% higher composite robustness than specialized SOTA on multi-shift
- Verification: Head-to-head on multi-shift benchmarks
- Difficulty: HIGH

---

## Implementation Path

**Foundation:** Extend DoWhy (7,900★) + CausalML (5,700★) with fairness and OOD modules

**Benchmarks:** Waterbirds, CelebA, PACS, ColoredMNIST, Multi-Shift Synthetic

**Experimental Design:** 10 methods × 5 datasets × 3 shift intensities × 5 seeds = 750 runs

**Primary Test:** One-way ANOVA on composite robustness, α=0.05, Cohen's d ≥ 0.5

---

## Critical Open Questions

1. **Invariance Compatibility:** Can all three invariances be jointly satisfied without degenerate solutions? (CRITICAL)
2. **Weight Learning Method:** Which approach (multi-objective, constraint satisfaction, Bayesian, meta-learning) is most effective? (HIGH)
3. **Computational Efficiency:** Can training time overhead be kept under 10× for large-scale datasets? (HIGH)

---

## Contributions to Research Gaps

**Gap 2 (Unified Framework): DIRECTLY ADDRESSED**
- IBTF is the unified framework integrating causal ML + fairness + OOD
- Translation protocol enables cross-community method adaptation
- First formal unification via invariance principle

**Gap 1 (Automated Discovery): PARTIALLY ADDRESSED**
- Unified evaluation suite provides platform for future discovery methods
- Framework can integrate with annotation-free methods (ShortcutProbe, Evidential Alignment)

**Gap 3 (Temporal Dynamics): EXTENSIBLE**
- Framework design allows temporal invariance as fourth dimension (future work)
- Can incorporate fairness drift insights

---

## Phase 2B Readiness: 95%

**Ready:**
- ✅ Hypothesis statement falsifiable with quantitative thresholds
- ✅ Variables operationalized with measurement protocols
- ✅ Causal mechanism detailed with evidence for each link
- ✅ Statistical design specified (750 runs, power analysis complete)
- ✅ SOTA baselines identified with performance benchmarks
- ✅ Sub-hypothesis decomposition preview complete

**Remaining:**
- ⚠️ Prototype multi-constraint optimization to validate assumption A2 (5%)

**Next Phase:** Phase 2B will create detailed verification plan with prioritized experiments, resource allocation, and success criteria for Phase 3-4 implementation.

---

## Key Sources (Top 5)

1. **Clever Hans Survey** (Ye et al., 2024, 51 cit): Identifies gap IBTF addresses
2. **OOD Generalization Survey** (Shen et al., 2021, 636 cit): Environmental invariance foundation
3. **Counterfactual Invariance** (Veitch et al., 2021, 102 cit): Structural invariance + stress testing
4. **DoWhy Library** (7,900★): Causal inference implementation foundation
5. **CausalML Library** (5,700★): Production causal ML integration

---

*Full Document: 02a_extended_hypothesis_full.md*
*Phase 2A Extended completed in YOLO MODE (automated execution)*
*Ready for: Phase 2B - Verification Planning*
