# Phase 2B Ready Summary: Adaptive State Compression for Length-Robust SSMs

**Generated:** 2026-02-06
**Hypothesis ID:** H-nxgenseqm-001
**Confidence Level:** 0.80 (High)
**Status:** ✅ READY FOR PHASE 2B

---

## Core Hypothesis Statement

Training SSMs with **learnable information bottleneck layers** (varying compression rates α=0.9→0.3) systematically expands state distribution coverage, enabling robust length generalization (2k→128k) without extensive post-training interventions.

**Alternative (H0):** SSM length generalization depends only on training sequence length; compression-based augmentation provides no systematic improvement over vanilla training or post-hoc interventions.

---

## Key Variables

| Type | Variable | Measurement |
|------|----------|-------------|
| **Independent** | Compression schedule (α_start, α_end, progression) | Bottleneck dimension ratio |
| | Rate-distortion loss weight (λ) | Scalar weight [0.01, 0.1, 1.0] |
| **Dependent** | Length OOD accuracy | % accuracy at 2k→8k→32k→128k |
| | Training overhead | % increase in wall-clock time |
| **Controlled** | SSM architecture (Mamba), dataset, training hyperparameters | Fixed across experiments |

---

## Causal Mechanism

**Information Bottleneck Compression → State Distribution Expansion → Length-Robust Representations**

1. **Compression forces minimal sufficient statistics:** Bottleneck (α<1.0) reduces state dimensions → model must preserve only task-relevant information
2. **Varying compression simulates different sequence regimes:** Low α (0.3) = tight state budget ≈ states at longer sequences
3. **Progressive schedule expands distribution:** Curriculum α=0.9→0.3 exposes model to diverse state budgets during training
4. **Compact encoding transfers:** Model trained on compressed states generalizes to longer sequences (similar state budget per timestep)

**Evidence:** Information bottleneck theory (Tishby et al.), unexplored states hypothesis (Ruiz & Gu 2025), randomized PE analogy (Ruoss et al. 2023)

---

## Testable Predictions

**P1 (Primary):** SSM + bottleneck (α=0.9→0.3) > vanilla SSM by ≥5% accuracy at 4× length extrapolation

**P2 (Training Efficiency):** SSM + bottleneck ≥ Ruiz & Gu 500-step post-training method with <1% inference overhead

**P3 (Compression Schedule):** Progressive schedule (0.9→0.3) > fixed compression (α=0.5) by ≥3% on length OOD

**P4 (Cross-Domain):** Vision Mamba + bottleneck improves resolution extrapolation (64×64→256×256) by ≥5%

**Falsification:** If SSM + bottleneck performs ≤2% better than vanilla SSM at 4× length OR training overhead >15% → hypothesis FALSIFIED

---

## Contributions

**Theoretical:** Information-theoretic framing of SSM length generalization; compression-state distribution connection; first application of bottleneck theory to SSM training

**Methodological:** Progressive compression schedule for state augmentation; training-time solution vs. post-hoc; ablation protocol for compression parameters

**Practical:** Minimal overhead (~5-10%); applicable to any SSM architecture (Mamba, S4); cross-domain validation (language, vision)

---

## Phase 2B Sub-Hypotheses Preview

**SH1 (Existence):** Information bottleneck layers can compress/reconstruct SSM states while maintaining task performance (reconstruction loss <5%)

**SH2 (Mechanism):** Compression rate correlates with effective sequence length in state space (empirical validation via state distribution analysis)

**SH3 (Comparison):** Bottleneck training outperforms vanilla SSM (≥5% @ 4×) and matches/exceeds Ruiz & Gu post-training intervention

---

## Next Steps

**Phase 2B Verification Planning:**
1. Decompose into 6-8 sub-hypotheses (existence, mechanism, comparison, ablation, cross-domain)
2. Design experiments for each SH with success criteria
3. Prioritize validation roadmap (pilot → small → medium → large scale)
4. Establish dependencies and critical path

**Expected Timeline:** 2-3 months for full validation (pilot + 4 scale stages)

---

*This summary provides Phase 2B with focused, testable hypothesis ready for verification decomposition.*
*Generated: 2026-02-06*
