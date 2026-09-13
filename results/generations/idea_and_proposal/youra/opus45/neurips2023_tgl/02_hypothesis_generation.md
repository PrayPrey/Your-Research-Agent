# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-HITM-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under discrete-time temporal graph learning conditions with regular snapshots, if we apply curvature-guided selective consolidation with Hebbian memory and sparse retrieval (HITM module), then long-range temporal dependencies will be captured with O(n) complexity while maintaining dynamic adaptability, because structurally important events (high curvature change) carry disproportionate predictive information that can be efficiently stored and retrieved through biologically-inspired memory mechanisms.

**Alternative Hypothesis (H0):**
Curvature-based event selection provides no predictive advantage over uniform temporal attention, and Hebbian memory consolidation does not improve long-range dependency modeling compared to standard attention mechanisms or pre-computation approaches.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Curvature threshold τ | Independent | Adaptive τ = μ(ΔOR) + σ(ΔOR) from Ollivier-Ricci curvature changes | Auto-computed per dataset |
| Memory bank size k | Independent | k = min(k_max, ⌈log₂(\|V\|)⌉ × α) adaptive to graph complexity | 8-128 memory slots |
| Consolidation decay λ | Independent | Hebbian decay rate controlling memory update speed | [0.01, 0.5] |
| Pre-initialization period T₀ | Independent | Number of warmup timesteps for initial memory population | 10-50 timesteps |
| Prediction accuracy | Dependent | MAE, RMSE, MAPE on week-scale forecasting benchmarks | MAE < 2.6, RMSE < 5.2 |
| Computational time | Dependent | Wall-clock time as function of sequence length T | O(n) scaling verified |
| Baseline STGNN | Controlled | STGCN architecture held constant across experiments | Fixed architecture |
| Dataset | Controlled | Standard traffic datasets with fixed preprocessing | METR-LA, PEMS-BAY |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Curvature Detection
    ↓ (ΔOR computation identifies structural importance)
Step 2: Selective Memory Write
    ↓ (Hebbian consolidation for important events)
Step 3: Sparse Associative Retrieval
    ↓ (Top-k attention over memory bank)
Step 4: Enhanced Prediction
    → Outcome (Week-scale forecasting with O(n) complexity)
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | ORC-STGNN (2023) | Curvature improves traffic forecasting by 10% RMSE | Strong |
| Step 2 → Step 3 | PIORF (2025) | ORC identifies bottlenecks, 26.2% improvement | Strong |
| Step 3 → Step 4 | HippoRAG (NeurIPS 2024) | Hippocampal-inspired retrieval validates knowledge integration | Medium |
| Step 4 → Outcome | BigST (2024) | Pre-computed long-range features enable 100k+ node scaling | Strong |

**Key Tension:**
- **Tension:** ORC-STGNN validates curvature for spatial dependencies, but its effectiveness for *temporal* importance detection is inferred rather than directly validated.
- **Resolution:** HITM tests whether spatial curvature importance transfers to temporal event selection.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | Graph curvature changes correlate with predictively important temporal events | ORC-STGNN (10% improvement) | Core mechanism fails; hypothesis rejected |
| A2 | Hebbian consolidation preserves essential temporal information | Sleep microstructure (2025) | Memory degrades; long-range modeling fails |
| A3 | Sparse top-k retrieval is sufficient for prediction | HippoRAG effectiveness | May miss critical contexts |
| A4 | Discrete-time snapshots adequately represent dynamics | Standard in traffic forecasting | Limits continuous-time applicability |

### 1.5 Scope & Boundaries

**Applies To:** Discrete-time temporal graphs, traffic/energy domains, 100-100k nodes, hour-to-week forecasting

**Does NOT Apply To:** Continuous-time event streams, static graphs, uniform-importance domains, sub-second latency

**Limitations:** Warmup period T₀ required, ~5% curvature overhead, may need domain-specific tuning

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Accuracy vs SOTA ~2.88 MAE):**
HITM-augmented STGCN achieves MAE < 2.60 (≥10% improvement) on week-scale traffic forecasting (p < 0.05).

*Falsification:* MAE ≥ 3.17 triggers rejection

**Secondary Predictions:**

**P2 (Complexity):** Computational time scales linearly with T (R² > 0.95)

**P3 (Interpretability):** High-curvature events correspond to interpretable structural changes

**Falsification Criteria:**

1. MAE ≥ 3.17 (worse than baseline)
2. Curvature selection = random selection (p > 0.10)
3. Complexity is O(T²)
4. No advantage on any dimension vs. BigST/STEP

### 1.7 SOTA Baseline Benchmark Summary

| Method | MAE | RMSE | Key Property |
|--------|-----|------|--------------|
| STGCN | 2.88 | 5.74 | Baseline |
| STEP | 2.61 | 5.22 | Pre-training |
| ORC-STGNN | -10% | - | Curvature |
| **HITM Target** | <2.60 | <5.20 | Linear + Adaptive |

### 1.8 Statistical Verification Design

- **Effect size:** Cohen's d > 0.5
- **Required runs:** n ≥ 25
- **Test:** Paired t-test, α = 0.05
- **Report:** Mean ± Std, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does curvature-guided selective consolidation improve temporal graph forecasting accuracy?"
- Verification: Empirical comparison
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 4-step mechanism the cause of improvement?"
- Decomposes to: H-M1 (curvature), H-M2 (Hebbian), H-M3 (retrieval), H-M4 (integration)
- Verification: Ablation studies

**SH3 (Comparison):**
"Does HITM outperform BigST (efficiency) and STEP (accuracy)?"
- Verification: Comparative empirical

**Total Sub-Hypotheses:** 6 (SH1 + 4 mechanism + SH3)

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-HITM-v1
- [x] Confidence: 0.82
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=4) with evidence
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] Predictions (P1 primary, P2-P3 secondary)
- [x] Falsification criteria
- [x] Baselines: STGCN, BigST, STEP
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Resources:** GPU memory for 100k+ node curvature computation?
2. **Data:** Week-scale splits available in METR-LA/PEMS-BAY?
3. **Priority:** Start with curvature validation (H-M1) first?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
