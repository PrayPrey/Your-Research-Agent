# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SDPA-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under transformer self-attention settings with token sequences of length n >= 64, if softmax attention is replaced with q-deformed optimal transport (Tsallis entropy regularization, q in [0.5, 0.8]), then extracted Kantorovich dual potentials will provide interpretability scores with higher faithfulness (measured by SaCo coefficient and lower faithfulness violation rate) than raw attention weights, because dual potentials mathematically represent marginal contributions to optimal transport cost, which directly corresponds to gradient-based sensitivity under mild smoothness conditions.

**Alternative Hypothesis (H0):**
Kantorovich dual potentials extracted from q-deformed OT attention do NOT provide significantly higher faithfulness scores than raw attention weights, OR the computational overhead (~2-3x) negates any interpretability benefits, OR the theoretical connection between dual potentials and gradient-based sensitivity does not hold in practice.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| q (deformation parameter) | Independent | Tsallis entropy parameter, set at model initialization | [0.5, 0.8] - lower = sparser |
| Attention mechanism type | Independent | Binary selection: standard softmax vs. q-deformed OT | {softmax, q-OT} |
| Interpretability faithfulness | Dependent | SaCo coefficient (Wu et al. 2024), faithfulness violation rate (Liu et al. 2022) | SaCo: higher is better; Violation rate: lower is better |
| Spectral expressivity | Dependent | Effective rank of attention matrices, eigenvalue distribution | Effective rank > 0.5 * n (avoiding collapse) |
| Model performance | Dependent | Task accuracy on standard benchmarks | SST-2: >90%, ImageNet: >75% (within 2% of baseline) |
| Model architecture | Controlled | Fixed transformer: BERT-base (NLP), ViT-B/16 (vision) | Fixed per experiment |
| Dataset | Controlled | Standard benchmarks: SST-2 (NLP), ImageNet-1K (vision) | Fixed per experiment |
| Random seed | Controlled | Fixed seeds for reproducibility | {42, 123, 456, 789, 1000} |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: q-Deformed OT Formulation
    |
    v (Tsallis entropy promotes sparsity)
Step 2: Sparse Attention Matrices
    |
    v (Sparse matrices avoid rank collapse)
Step 3: Preserved Spectral Expressivity
    |
    v (Kantorovich duality: u_i = d(cost)/d(mass_i))
Step 4: Dual Potential Extraction --> Interpretability Scores
    |
    v (Optimization-theoretic meaning vs. heuristic attention)
Outcome: Higher Faithfulness than Raw Attention
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 -> Step2 | Bao & Sakaue (2022), Martins et al. (2022) | Tsallis entropy (q < 1) yields sparse distributions; closed-form for alpha-entmax | Strong |
| Step2 -> Step3 | Liu (2026) - Homogeneity Trap paper | Dense doubly-stochastic attention suffers spectral collapse; sparsity preserves expressivity | Strong |
| Step3 -> Step4 | Kantorovich duality theory; He & Vitercik (2025) | Dual potentials encode marginal costs; successfully used in neural algorithmic reasoning | Medium |
| Step4 -> Outcome | Liu et al. (2022) ICML | Raw attention has faithfulness violation (polarity inconsistency); dual potentials have direct optimization meaning | Medium |

**Key Tension:**
- **Tension:** Liu et al. (2022) show attention-based explanations have faithfulness issues, but existing OT-attention work (Sinkformers 2022) focuses on efficiency, NOT interpretability via dual potentials. No prior work validates dual potentials for faithfulness.
- **Resolution:** This hypothesis directly tests whether dual potentials (not transport plans) provide better faithfulness, filling the gap between OT-attention efficiency work and interpretability evaluation.

### 1.4 Key Assumptions

1. **Kantorovich dual potentials remain extractable under q-deformation**
   - Evidence: Bao & Sakaue (2022) prove existence for Tsallis entropy
   - Consequence if violated: Cannot extract interpretability coefficients; hypothesis fails at Step 4

2. **Sparse transport plans preserve task-relevant information**
   - Evidence: Martins et al. (2022) show sparse attention maintains performance in classification
   - Consequence if violated: Model accuracy degrades >5%, making interpretability gains worthless

3. **Faithfulness metrics (SaCo, violation rate) are valid**
   - Evidence: Wu et al. (2024) show SaCo differentiates methods from random attribution; Liu et al. (2022) established faithfulness violation test
   - Consequence if violated: Cannot measure interpretability improvement; need alternative metrics

4. **The bound ||u_i - dL/dx_i|| is tight enough for practical use**
   - Evidence: Theoretical from OT duality; needs empirical validation
   - Consequence if violated: Dual potentials are theoretically grounded but practically useless; need to establish empirical correlation

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Transformer architectures with self-attention (encoder-only: BERT; decoder-only: GPT; encoder-decoder; ViT)
- Token sequences n >= 64 (below this, OT overhead may not justify)
- Classification and generation tasks where interpretability matters
- Post-hoc explanation scenarios (explaining existing predictions)

**Where it does NOT apply:**
- Non-attention architectures (CNNs, MLPs, SSMs)
- Real-time inference where ~2-3x overhead is unacceptable
- Very short sequences (n < 64) where sparse attention may be too restrictive
- Tasks where interpretability is not needed

**Known limitations:**
- Computational overhead: q-OT requires iterative solver (~10-30 iterations)
- Hyperparameter sensitivity: q must be tuned per task (though range [0.5, 0.8] is theoretically motivated)
- Multi-head attention: Dual potential interpretation may be complex for multiple heads

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Faithfulness Improvement):**
SDPA will achieve significantly higher faithfulness scores than raw attention:
- SaCo coefficient: SDPA > Softmax + 0.1 (10% relative improvement)
- Faithfulness violation rate: SDPA < Softmax (at least 20% reduction)

*Measurement*:
- SaCo coefficient (Wu et al. 2024) computed on explanation heatmaps
- Faithfulness violation rate (Liu et al. 2022) - % of samples where top-attention regions suppress predictions
- Statistical test: Paired t-test, n >= 30 test samples, p < 0.05

*Basis*:
Raw attention suffers from faithfulness violation in ~30-50% of cases (Liu et al. 2022). Dual potentials have direct optimization interpretation, expected to reduce violations.

*Success Criteria for Phase 2B*:
- Primary: SaCo(SDPA) - SaCo(Softmax) > 0.1 with p < 0.05
- Falsification: SaCo(SDPA) <= SaCo(Softmax) OR violation_rate(SDPA) >= violation_rate(Softmax)

**Secondary Predictions:**

**P2 (Spectral Expressivity):**
SDPA with q in [0.5, 0.8] will maintain higher effective rank than dense doubly-stochastic attention (Sinkhorn, q=1):
- Effective rank: SDPA > 0.5 * n (not collapsed)
- Comparison: SDPA effective_rank > Sinkhorn effective_rank

*Measurement*: Effective rank = exp(entropy(normalized eigenvalues))

**P3 (Performance Preservation):**
SDPA will maintain model accuracy within 2% of baseline softmax attention:
- SST-2 accuracy: |SDPA - Softmax| < 2%
- ImageNet accuracy: |SDPA - Softmax| < 2%

*Measurement*: Standard test set accuracy, averaged over 5 random seeds

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure (Faithfulness):** SaCo(SDPA) <= SaCo(Softmax) OR improvement < 5% (not statistically significant)

2. **Mechanism Failure (Spectral Collapse):** SDPA effective rank < 0.3 * n (spectral collapse despite q-deformation)

3. **Performance Failure:** Model accuracy drops >5% compared to softmax baseline

4. **Computation Failure:** q-OT does not converge within 100 iterations for >10% of batches

### 1.7 SOTA Baseline (Optional)

*Not applicable for this hypothesis - targeting faithfulness improvement over raw attention, not SOTA performance competition.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): Expected ~0.5 (medium effect for faithfulness improvement)
- Required test samples: n >= 30 per dataset
- Random seeds: 5 seeds for variance estimation
- Statistical power: 0.8

**Test Specification:**
- Primary test: Paired t-test (same samples, different explanation methods)
- Significance level: alpha = 0.05 (one-tailed for improvement claims)
- Multiple comparison correction: Bonferroni for 3 predictions

**Report Format:**
- Mean +- Std Dev for all metrics
- 95% Confidence Intervals
- Cohen's d effect sizes
- p-values with exact values (not just < 0.05)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does q-deformed optimal transport attention with dual potential extraction produce valid interpretability scores under standard transformer settings?"
- Maps to: Primary prediction P1 (faithfulness improvement)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism (q-OT -> sparsity -> expressivity -> dual potentials -> faithfulness) the actual cause of improved interpretability?"
- Maps to: Causal chain (4 sub-hypotheses: H-M1 through H-M4)
  - H-M1: q-OT produces sparse attention (vs. dense Sinkhorn)
  - H-M2: Sparse attention preserves effective rank
  - H-M3: Dual potentials correlate with gradients
  - H-M4: Dual potentials have lower faithfulness violation than raw attention
- Verification type: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does SDPA outperform existing interpretability baselines (raw attention, integrated gradients, attention rollout) on faithfulness metrics?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 4 = 6 (SH1, H-M1, H-M2, H-M3, H-M4, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SDPA-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps, evidence_for_links table)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 defined, with primary marked)
- [x] Falsification criteria are defined (4 failure conditions)
- [x] Baselines are identified for comparison (Sinkformers, IG, Attention Rollout)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions for Phase 2B

1. **Implementation choice:** Should we use BFGS solver (exact but slower) or iterative Sinkhorn-like updates (approximate but faster) for q-OT?
   - Impact: Affects wall-clock time and convergence guarantees
   - Recommendation: Start with POT library's entropic solver modified for Tsallis

2. **Multi-head attention handling:** How to aggregate dual potentials across multiple attention heads?
   - Options: Average, max, learned weighting
   - Impact: Affects interpretability clarity for multi-head models

3. **Layer selection:** Apply SDPA to all layers or selected layers?
   - Impact: Computational cost vs. interpretability coverage
   - Recommendation: Start with final 3 layers (most task-relevant)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
