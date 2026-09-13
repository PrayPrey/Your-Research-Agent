# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HSI-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of iterative self-training on synthetic data (≥13B parameter models), if a Homeostatic Self-Improvement (HSI) framework integrating adaptive constitutional anchoring, diversity-based ensemble verification, and decay-weighted accumulative training is applied, then foundation models will sustain significantly more self-improvement iterations before performance degradation compared to single-component approaches, because the three-component regulatory architecture provides complementary negative feedback mechanisms that prevent distribution drift and model collapse analogous to biological homeostatic systems.

**Alternative Hypothesis (H0):**
The three-component HSI framework provides no significant advantage over individual components (Constitutional AI alone, Accumulation alone, or Weak-to-Strong alone) in terms of sustainable self-improvement iterations. The integration overhead may even reduce performance compared to optimized single-component approaches.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Adaptive λ_anchor(t) | Independent | KL-divergence regularization strength adjusting based on drift detection | 0.01 - 1.0, adaptive |
| Ensemble size K | Independent | Number of diverse verifier models for T-similarity verification | 3-5 models |
| Decay rate γ | Independent | Exponential decay factor for historical vs new data weighting | 0.9 - 0.99 |
| Drift threshold θ_drift | Independent | JS-divergence threshold triggering λ_anchor adjustment | 0.05 - 0.2 |
| Iterations before degradation | Dependent | Cycles before accuracy drops >5% from peak | Target: 2-3x baseline |
| Distribution drift | Dependent | JS-divergence vs original model per iteration | < θ_drift |
| Final performance | Dependent | Accuracy on MMLU, HumanEval after N iterations | ≥95% of peak |
| Base model architecture | Controlled | Transformer ≥13B (Llama-3, Qwen-2) | Fixed |
| Dataset | Controlled | Fixed training corpus and benchmarks | Fixed |
| Compute budget | Controlled | Fixed GPU hours per iteration | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Adaptive Constitutional Anchor → Alignment Preservation
Step 2: Diversity-Based Ensemble Verification → Quality Filtering
Step 3: Decay-Weighted Accumulative Training → Collapse Prevention
Step 4: Three-Component Regulatory System → Sustained Self-Improvement
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Constitutional AI (Bai 2022, 2431 cit.) | RLAIF enables self-improvement without human labels | Strong |
| Step2 → Step3 | Ensemble Diversity (Odonnat AISTATS 2024) | T-similarity provides theoretical verification guarantees | Medium |
| Step3 → Step4 | Model Collapse (Gerstgrasser 2024, 108 cit.) | Accumulation prevents collapse with finite error bound | Strong |
| Step4 → Outcome | Novel Integration (This work) | First unified framework combining all three | To validate |

**Key Tension:**
- **Tension:** Zhang (2025) shows CAI alone accelerates collapse in smaller models without accumulation
- **Resolution:** HSI mandates ≥13B scale AND combines CAI with accumulative training to mitigate collapse

### 1.4 Key Assumptions

1. **Multiple weak verifiers > single verifier** (W2SG Burns 2023, Odonnat 2024)
   - If violated: Simplify to single-model filtering

2. **JS-divergence reliably proxies collapse risk** (Seddik 2024)
   - If violated: Need alternative drift metrics

3. **Self-improvement emerges at ≥13B scale** (Zhang 2025)
   - If violated: Need larger compute or alternative validation

4. **Constitutional principles embed as KL constraints** (Bai 2022)
   - If violated: Use alternative constraint (DPO, contrastive loss)

### 1.5 Scope & Boundaries

**Applies to:** Transformer FMs ≥13B, self-training without human feedback, verifiable tasks, 8+ GPU environments

**Does NOT apply to:** Models <13B, non-transformers, pure creative tasks, single-GPU deployment

**Limitations:** K-model overhead, θ_drift calibration needed, conceptual (not literal) biological analogy

### 1.6 Testable Predictions

**Primary Prediction (P1):**
HSI enables ≥2x more iterations before degradation vs best single-component baseline.

*Measurement:* Count iterations until >5% accuracy drop; compare HSI vs CAI vs Accumulation vs W2SG
*Test:* One-way ANOVA + Tukey HSD, n≥5 runs/condition, p<0.05
*Success:* Iterations(HSI) ≥ 2.0 × max(baselines)
*Falsification:* Iterations(HSI) ≤ max(baselines)

**Secondary Predictions:**
- **P2:** HSI maintains bounded drift (JS < θ_drift) while baselines show unbounded growth
- **P3:** Ablating any component reduces iterations by >30% (all three necessary)

**Falsification Criteria:**
1. HSI ≤1.5x iterations vs best baseline (insufficient advantage)
2. Any causal link fails (λ-drift r<0.3, ensemble ≤ single, no decay advantage, ablation <30%)
3. Fails at 13B scale or requires >100 GPU-days/experiment

### 1.8 Statistical Verification Design

**Sample Size:** n≥5 runs/condition, 12 conditions (4 main + 8 ablation) = 60 total runs
**Tests:** One-way ANOVA (primary), paired t-test (direct comparison), repeated measures (drift)
**Significance:** α=0.05 with Bonferroni correction
**Report:** Mean±SD, 95% CI, Cohen's d, corrected p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does HSI enable sustainable self-improvement (>baseline iterations) under specified conditions?"
- Maps to: P1; Verification: Empirical comparison; MUST PASS

**SH2 (Mechanism):**
"Is the three-component architecture the actual cause of sustained self-improvement?"
- Maps to: 4 causal steps → Phase 2B decomposes into:
  - H-M1: Constitutional Anchor → Alignment Preservation
  - H-M2: Ensemble Verification → Quality Filtering
  - H-M3: Accumulative Training → Collapse Prevention
  - H-M4: Integration → Synergistic Sustainability
- Verification: Ablation + causal analysis

**SH3 (Comparison):**
"Does HSI outperform each baseline by ≥2x iterations?"
- Maps to: P2, P3; Verification: Comparative empirical

**Total sub-hypotheses:** 6 (1 + 4 + 1)

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HSI-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] 10 variables operationalized
- [x] N=4 causal steps with evidence
- [x] Key tension + resolution
- [x] 4 assumptions with consequences
- [x] 3 testable predictions (P1 primary)
- [x] 3 falsification criteria
- [x] 3 baselines identified
- [x] SH1/SH2/SH3 clear

### Open Questions

1. **Compute:** ~672 GPU-days total (12 conditions × 5 runs × 8 A100 × 7 days)
2. **Models:** Llama-3-13B, Qwen-2-14B candidates; verify CAI compatibility
3. **Priority:** SH1 → H-M3 → H-M1 → H-M2 → H-M4 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
