# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1: THAR - FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-THAR-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under long-context processing conditions (1K-100K+ tokens), if depth-biased routers select between SSM and attention mechanisms based on hierarchical temporal timescale principles (lower layers → attention for fast/parallel processing, upper layers → SSM for efficient/integrative processing), then the model will achieve comparable or better task accuracy while reducing computational complexity from O(n²) to expected O(n·log(n)), because lower layers require fine-grained token interactions (attention's strength) while upper layers benefit from efficient long-range dependency modeling (SSM's strength), mirroring the brain's hierarchical temporal processing.

**Alternative Hypothesis (H0):**
There is no systematic relationship between layer depth and optimal mechanism selection; random or uniform mechanism allocation achieves equivalent efficiency-accuracy trade-offs as depth-biased routing.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Layer Depth | Independent | Layer index (1-12), categorized as lower (1-4), middle (5-8), upper (9-12) | 1-12 (discrete) |
| Router Architecture | Independent | MLP router: R(x) = softmax(W₂·ReLU(W₁·pool(x)) + bias_depth) | Hidden dim: 64-256 |
| Efficiency Regularization λ | Independent | Loss: L = L_task + λ·Σ_layers p_attn | [0.01, 0.5] |
| Routing Decision Distribution | Dependent | Percentage of SSM vs attention per layer (p_ssm) | [0, 1] per layer |
| Computational Complexity | Dependent | FLOPs, memory (GB), wall-clock time (ms) | FLOPs: 10^12 - 10^15 |
| Task Accuracy | Dependent | Perplexity, LongBench v2 accuracy | Perplexity: 5-50, Acc: 40-90% |
| Model Size | Controlled | Fixed parameter count | 3B parameters |
| Training Data | Controlled | Same pretraining corpus | Fixed corpus |
| Hardware | Controlled | Same GPU type | A100 80GB |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Depth-Biased Router Initialization
    ↓
Step 2: Layer-wise Mechanism Selection (Hard Gating)
    ↓
Step 3: Heterogeneous Computational Pattern
    ↓
[OUTCOME]: Efficiency + Accuracy Trade-off Optimization
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | MoE literature, PyTorch SDPA | Learned routing converges to meaningful specialization | Strong |
| Step2 → Step3 | Mamba (Gu & Dao, 2023) | SSM achieves 5x throughput with linear scaling | Strong |
| Step2 → Step3 | FlashAttention (Dao, 2022) | IO-aware attention optimizes short-range interactions | Strong |
| Step3 → Outcome | Mamba-2-Hybrid (2024) | Hybrid exceeds Transformer by +2.65 points, 8x faster | Strong |

**Key Tension:**
Mamba excels at efficiency (5x throughput) but lags on copying/in-context learning tasks. Attention excels at these but scales O(n²). *Can routing capture when each is optimal, or will it learn suboptimal shortcuts?*

**Resolution:** Ablation studies on routing patterns will reveal if learned allocations match hypothesized temporal hierarchy.

### 1.4 Key Assumptions

1. **SSM-Attention Embedding Compatibility** - If violated: Layer-to-layer information flow degrades
2. **Cross-Modal Depth Bias Generalization** - If violated: Separate routing policies required per modality
3. **Gumbel-Softmax Gradient Sufficiency** - If violated: Router fails to learn beyond initialization
4. **Efficiency Regularization Balance** - If violated: Routing collapses to all-SSM or no efficiency gain

### 1.5 Scope & Boundaries

**Applies to:** Long-context (1K-100K+) foundation models; text, vision, video, genomics; 1B-10B+ parameters
**Does NOT apply to:** Real-time streaming; <1K token contexts; extreme low-latency; <1B parameters
**Limitations:** Router collapse risk; depth bias rigidity; modality-specific adapters required

### 1.6 Testable Predictions

**Primary Prediction (P1 - Routing Pattern Emergence):**
After training with λ ∈ [0.1, 0.3]: SSM usage in layers 9-12 > 70%, attention in layers 1-4 > 60%, middle layers balanced.
- *Measurement*: Track p_ssm per layer across 10K samples
- *Test*: One-sample t-test vs chance (0.5), n ≥ 25, p < 0.05

**Secondary Predictions:**
- **P2:** THAR achieves ≥95% of Mamba-2-Hybrid accuracy while using ≤60% of Transformer FLOPs
- **P3:** Text-trained router transfers to vision with <10% fine-tuning cost

**Falsification Criteria:**
1. Routing shows no depth correlation (uniform p_ssm ≈ 0.5)
2. <90% of Mamba-2-Hybrid accuracy OR >80% of Transformer FLOPs
3. >80% layers converge to single mechanism
4. Vision transfer requires >50% of from-scratch cost

### 1.7 SOTA Baseline

| Method | Performance | Key Metric |
|--------|-------------|------------|
| Mamba-2-Hybrid (8B) | +2.65 pts vs Transformer | 12 tasks avg |
| GLA Transformer | Competitive with LLaMA | 2K→20K generalization |
| TransMamba | Baseline hybrid | Fixed alternation |

**Target:** Match/exceed Mamba-2-Hybrid (+2.5% improvement), >50% FLOPs reduction vs Transformer

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 25 runs, Cohen's d = 0.6, power = 0.8
- **Test:** Paired t-test, α = 0.05 (one-tailed), Bonferroni correction
- **Report:** Mean difference, 95% CI, Cohen's d, p-value, routing heatmaps

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does depth-biased routing emerge when training THAR with efficiency regularization?"
- Maps to: P1 (routing pattern)
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is hierarchical routing (not arbitrary allocation) the cause of improvement?"
- Decomposes to: H-M1 (initialization → bias), H-M2 (hard gating → efficiency), H-M3 (heterogeneous → Pareto)
- Total: 3 sub-hypotheses

**SH3 (Comparison):**
"Does THAR outperform fixed hybrid baselines (TransMamba, uniform routing)?"
- Maps to: P2 (efficiency-accuracy)

**Total Sub-Hypotheses:** 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-THAR-v1
- [x] Confidence: 0.88
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=3)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Testable predictions (P1 primary, P2-P3 secondary)
- [x] Falsification criteria (4)
- [x] Baselines identified
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** Minimum compute for validation? Can we validate at 1B before 3B?
2. **Data Availability:** Best datasets for routing pattern analysis? Synthetic probing tasks?
3. **Implementation Priority:** Text-only first, or multi-modal from start?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
