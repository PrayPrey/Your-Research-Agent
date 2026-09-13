# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (MetroFM-Bench - Round 1)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MetroFM-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under conditions of multi-domain foundation model evaluation, **if** metrological principles (transfer standards via bridge datasets, traceability chains via Domain-Canonical Task Templates) are applied, **then** fair cross-domain comparison of foundation models becomes possible with quantifiable transfer efficiency, **because** bridge datasets serve as domain-invariant reference points linking domain-specific benchmarks to a unified evaluation framework.

**Alternative Hypothesis (H0):**
There is no systematic relationship between metrological framework components (bridge datasets, DCTTs) and cross-domain FM comparison fairness—observed performance differences reflect only domain-specific characteristics rather than transferable FM capabilities.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Bridge Dataset Composition | Independent | Multi-domain reference datasets spanning domain boundaries with MMD-based diversity score | Diversity score D > 0.5; 3 datasets per domain pair |
| Domain-Canonical Task Templates (DCTTs) | Independent | Abstract task specifications validated via expert agreement and embedding similarity | κ > 0.7 (expert); cosine > 0.8 (embedding) |
| Transfer Efficiency (T_eff) | Dependent | (Perf_target / Perf_source) / (Data_target / Data_source)^β with 95% CI | T_eff ∈ [0.1, 2.0]; β calibrated per task |
| Cross-Domain Rank Correlation | Dependent | Spearman correlation between FM rankings across domains | ρ > 0.6 indicates strong framework validity |
| Compute Budget | Controlled | Fixed FLOP budget or parameter count for all evaluations | Standardized per evaluation tier |
| Task Template Specification | Controlled | Same DCTT specification language across all instantiations | BNF-like formal grammar |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: DCTT Definition
    ↓ (validated semantic equivalence)
Step 2: Domain-Specific Instantiation + Bridge Dataset Evaluation
    ↓ (transfer efficiency measurement)
Step 3: Cross-Domain FM Ranking
    ↓ (fair comparison)
Outcome: Unified FM Evaluation Framework
```

**Step 1 → Step 2:** Domain-Canonical Task Templates define abstract task specifications. Domain experts create instantiations validated via agreement (κ > 0.7) and embedding similarity (cosine > 0.8).

**Step 2 → Step 3:** Bridge datasets provide domain-invariant reference data. Transfer efficiency T_eff = (Perf_target / Perf_source) / (Data_target / Data_source)^β captures generalization independent of domain.

**Step 3 → Outcome:** Transfer efficiency metrics enable fair cross-domain ranking based on FM capability rather than domain fit.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | PANGAEA (2024) | Standardized evaluation protocol with extensible task/dataset inclusion | Strong |
| Step2 → Step3 | TEMPLATE Framework | Transferability metrics achieve 35% improvement over baselines for model selection | Strong |
| Step3 → Outcome | Data Cards (2022) | Documentation standardization enables systematic comparison (273 citations) | Strong |

**Key Tension:**
- **Tension:** PANGAEA shows "GFMs don't consistently outperform supervised models" yet TEMPLATE shows transferability metrics predict cross-domain success.
- **Resolution:** MetroFM-Bench tests when transfer succeeds vs. fails, providing nuanced guidance rather than universal ranking.

### 1.4 Key Assumptions

1. **Task Semantic Equivalence:** DCTTs achieve semantic equivalence (κ > 0.7, cosine > 0.8)
   - *If violated:* Rankings reflect task formulation artifacts

2. **Bridge Dataset Representativeness:** Sufficient diversity to avoid domain bias
   - *If violated:* Traceability invalid; rankings favor better-represented domains

3. **Transfer Efficiency Validity:** T_eff measures FM generalization capability
   - *If violated:* Metric gaming; rankings diverge from deployment performance

4. **Metrological Transfer:** Physical measurement principles apply to ML benchmarking
   - *If violated:* Fundamental framework design invalid

### 1.5 Scope & Boundaries

**Applies to:**
- Foundation models with multi-domain applicability claims
- Cross-domain comparison scenarios
- Open science benchmarking (ICLR 2025 SCI-FM aligned)

**Does NOT apply to:**
- Single-domain specialized models
- Real-time deployment (compute overhead)
- Domains without sufficient public data

**Limitations:**
- Initial scope: 2-4 domains
- Expert validation adds upfront cost
- Computational overhead: ~2-3x evaluation cost

### 1.6 Testable Predictions

**Primary Prediction (P1):**
Transfer efficiency rankings differ significantly from raw accuracy rankings.
- Spearman ρ(T_eff, accuracy) < 0.7 with p < 0.05
- ≥30% FM pairs show rank reversal
- **Falsification:** ρ > 0.9 suggests T_eff adds no information

**Secondary Predictions:**
- **P2:** Bridge datasets expose domain-specific biases (ANOVA η² > 0.14)
- **P3:** Cost normalization changes architecture rankings (≥2 families rerank)

**Falsification Criteria:**
1. Semantic equivalence failure: κ < 0.5 or cosine < 0.6
2. Bridge dataset bias: MMD diversity < threshold for >50% pairs
3. T_eff invalidity: ρ < 0.3 with fine-tuning success
4. No ranking divergence: ρ(T_eff, accuracy) > 0.9

### 1.8 Statistical Verification Design

| Parameter | Value |
|-----------|-------|
| Minimum FMs | n ≥ 10 |
| Minimum domains | 4 |
| Bridge datasets per pair | 3 |
| Runs per FM per dataset | 5 |
| Primary test | Spearman ρ < 0.7 |
| Significance | p < 0.05 |
| Effect size | Cohen's d, η² reported |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does transfer efficiency (T_eff) provide different rankings than raw accuracy for foundation models across domains?"
- Maps to: Primary prediction (P1)
- Verification: Empirical measurement
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step mechanism (DCTT → Bridge Dataset → T_eff) the cause of fair comparison?"
- Decomposes to: H-M1 (DCTT validation), H-M2 (Bridge diversity), H-M3 (T_eff correlation)
- Verification: Causal analysis with ablations
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does MetroFM-Bench provide actionable insights beyond HELM, lm-eval, PANGAEA?"
- Maps to: P2, P3
- Verification: Comparative empirical
- Critical: Determines practical value

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-MetroFM-v1
- [x] Confidence: 0.85
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism (N=3) with evidence
- [x] Key tension identified
- [x] Assumptions with consequences
- [x] Testable predictions (P1 primary)
- [x] Falsification criteria (4)
- [x] Baselines identified
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Resources:** ~500-1000 GPU-hours for 10+ FMs × 4 domains × 3 bridge datasets
2. **Data:** Which public datasets serve as bridge candidates? Need domain overlap assessment
3. **Experts:** Crowdsourcing vs. targeted panels for DCTT validation?
4. **Priority:** SH1 → SH2-M1 → SH2-M2 → SH2-M3 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
