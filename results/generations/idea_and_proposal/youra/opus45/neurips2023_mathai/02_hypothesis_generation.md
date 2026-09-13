# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ADPSG-v1
**Confidence Level:** 0.77

**Main Hypothesis:**
Under conditions of mathematical reasoning tasks requiring both informal understanding and formal proof generation, if a transformer architecture maintains parallel dual-pathway representations (informal semantic + formal syntactic) with adaptive bidirectional cross-grounding at meta-learned intervals, then it will achieve higher combined accuracy on informal (MATH) and formal (MiniF2F) benchmarks compared to sequential autoformalization approaches, because simultaneous representation maintenance prevents information loss that occurs at sequential translation boundaries.

**Alternative Hypothesis (H0):**
There is no significant difference in combined benchmark accuracy between parallel dual-pathway architectures with cross-grounding and sequential autoformalization approaches; any observed differences are attributable to increased model capacity or computational overhead rather than the dual-pathway mechanism itself.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Architecture paradigm | Independent | A-DPSG (parallel dual-pathway) vs FIRMA (sequential translation) vs DeepSeek-Prover-V2 (formal-only) | 3 discrete conditions |
| Cross-grounding frequency | Independent | Adaptive interval K (meta-learned) vs fixed interval vs no grounding | K ∈ [1, 10] steps; adaptive baseline |
| Combined benchmark accuracy | Dependent | Weighted average: 0.5 × MiniF2F-test + 0.5 × MATH accuracy | 0-100% |
| Semantic preservation score | Dependent | BEq+ score measuring bidirectional entailment between parallel pathway outputs | 0.0-1.0 |
| Step consistency rate | Dependent | Percentage of reasoning steps where both pathways agree on intermediate conclusions | 0-100% |
| Base model size | Controlled | Fixed at 7B parameters for all conditions | 7B |
| Training data | Controlled | Same paired informal-formal dataset (MiniF2F + ProofNet + synthetic pairs) | ~50K examples |
| Evaluation benchmarks | Controlled | MiniF2F-test, MATH, BEq+ | Fixed benchmark versions |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Dual Parallel Decoders
    ↓ (shared embedding enables alignment)
Step 2: Bidirectional Cross-Attention
    ↓ (corrects divergence before accumulation)
Step 3: Semantic Consistency Loss
    ↓ (reinforces cross-pathway coherence)
Step 4: Aligned Dual Representations
    ↓ (synergistic benefits)
Outcome: Higher Combined Accuracy
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | HuggingFace diffusers attention_processor.py | Cross-attention patterns successfully integrate multi-modal representations | Strong |
| Step2 → Step3 | Seger et al. 2025 (PFC dual-stream) | Human cognition uses parallel processing for abstract rules + schema grounding | Medium |
| Step3 → Step4 | FIRMA 2025 | Bidirectional translation achieves 277.8% improvement over unidirectional | Strong |
| Step4 → Outcome | DeepSeek-Prover-V2 vs DeepSeek-V3 | 88.9% formal vs varying informal shows gap that dual-pathway could bridge | Medium |

**Key Tension:**
- **Tension**: FIRMA (2025) achieves strong results with sequential bidirectional translation, suggesting translation may be sufficient.
- **Resolution**: This verification plan tests whether simultaneous maintenance (A-DPSG) offers benefits over sequential translation (FIRMA) by measuring information preservation during reasoning.

### 1.4 Key Assumptions

| # | Assumption | Consequence if Violated |
|---|------------|------------------------|
| A1 | Paired informal-formal training data is sufficient for learning cross-grounding mappings | Cross-attention learns spurious correlations; fails to generalize |
| A2 | Cross-attention can learn semantic-syntactic correspondences between pathways | Dual pathways operate independently; no synergistic benefit |
| A3 | Adaptive cross-grounding frequency can be meta-learned without excessive overhead | Fixed frequency either too sparse or too frequent |
| A4 | Lean 4 verification provides reliable ground truth for formal correctness | Formal pathway optimization target is unreliable |

### 1.5 Scope & Boundaries

**Applies to:**
- Mathematical reasoning with both natural language and formal proof targets
- Competition mathematics with formalization potential
- MiniF2F, MATH, ProofNet benchmark domains

**Does NOT Apply to:**
- Pure informal reasoning without formal verification (e.g., GSM8K only)
- Pure formal proving without informal interpretation
- Non-mathematical reasoning tasks

**Limitations:**
- Requires paired training data
- ~1.5-2x computational overhead
- 7B scale evaluation (larger scales may differ)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Combined Accuracy)**:
A-DPSG will achieve combined benchmark accuracy (0.5 × MiniF2F + 0.5 × MATH) exceeding the best single-pathway baseline by ≥3 percentage points (p < 0.05).

- Target: Combined accuracy ≥ 73%
- Falsification: Combined accuracy ≤ 67%
- Statistical test: Paired t-test, n ≥ 25 runs

**Secondary Predictions:**

**P2 (Semantic Preservation)**: BEq+ score ≥ 0.80 between parallel pathway outputs
- Falsification: BEq+ < 0.60

**P3 (Computational Efficiency)**: Overhead < 2x with accuracy gains maintained
- Falsification: Overhead > 3x with no accuracy gain

**Falsification Criteria:**

1. **Primary Failure**: Combined accuracy ≤ 67%
2. **Mechanism Failure**: BEq+ < 0.60
3. **Efficiency Failure**: Overhead > 3x with accuracy ≤ baseline
4. **Comparative Failure**: Both FIRMA AND DeepSeek-Prover outperform A-DPSG

### 1.7 SOTA Baseline

| Method | Benchmark | Performance | Year |
|--------|-----------|-------------|------|
| DeepSeek-Prover-V2-671B | MiniF2F-test | 88.9% | 2025 |
| DeepSeek-Prover-V2-7B | MiniF2F-test | ~52% | 2025 |
| FIRMA | Translation (BEq+) | 277.8% improvement | 2025 |
| Claude Opus 4.6 | ProofBench | 50% | 2026 |

**Performance Tier**: Medium (50-70% at 7B scale)
**Target**: ≥65-70% combined at 7B scale

### 1.8 Statistical Verification Design

- **Effect size**: Cohen's d = 0.6 (medium-large)
- **Required runs**: n ≥ 25 per condition
- **Conditions**: 3 (A-DPSG, FIRMA, DeepSeek-Prover)
- **Test**: One-way ANOVA with Tukey HSD; α = 0.05

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does A-DPSG successfully maintain both informal and formal representations simultaneously?"
- Verification: Empirical existence test
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 4-step causal mechanism the actual cause of improved accuracy?"
- Decomposes to H-M1 through H-M4 (ablation studies)
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does A-DPSG outperform FIRMA and DeepSeek-Prover on combined benchmarks?"
- Verification: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis in scientific format with H0
- [x] Hypothesis ID: H-ADPSG-v1, Confidence: 0.77
- [x] Variables operationalized (7 variables)
- [x] Causal mechanism with N=4 steps and evidence
- [x] Key tension identified with resolution
- [x] 4 assumptions with violation consequences
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] Baselines: FIRMA, DeepSeek-Prover-V2
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Data**: Sufficient paired informal-formal data beyond MiniF2F + ProofNet?
2. **Compute**: GPU requirements for 25+ runs at 7B scale with 2x overhead?
3. **Implementation**: Meta-learning approach for adaptive K (MAML? RL? Gating?)
4. **Priority**: Verify SH1 first, or run ablations in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (7 sources with full citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
