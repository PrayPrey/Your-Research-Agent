## 5. Results

We present results in order of the three research questions, followed by the methodology-level finding that motivates all three.

### 5.1 The Role of Capability Control

Before presenting primary results, we establish why capability control is necessary.

Raw (unadjusted) Spearman ρ between in-distribution and OOD model rankings is near-ceiling across all dimensions: ρ_fairness = 0.979, ρ_ANLI ≈ 0.983, ρ_OOD ≈ 0.984. The dimension-level gap is Δρ_raw = −0.005 — essentially zero. This occurs because higher-capability models (higher MMLU) outperform lower-capability models on *all* trustworthiness benchmarks in both ID and OOD conditions, creating a capability-driven floor for rank stability.

Figure 4 (per_dimension_scatter.png) shows this collapse: three panels, one per dimension, with raw ρ near-identical across all. After MMLU control (right panels), the partial ρ values diverge, revealing the dimension-specific structure that is the subject of this analysis.

**Takeaway:** MMLU capability control is methodologically essential. Without it, all trustworthiness dimensions appear equally stable, and the fairness-robustness comparison is invisible.

---

### 5.2 RQ1: Fairness Rank Stability (P1 — Confirmatory)

Figure 1 (rank_scatter_bbq.png) shows the primary result. Each point is one of the 16 LLMs. The x-axis is rank on BBQ-Disambig (in-distribution), the y-axis is rank on BBQ-Ambig (OOD). The near-diagonal arrangement reflects the high rank preservation.

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| Partial Spearman ρ (MMLU-ctrl) | **0.962** | > 0.4 | ✅ PASS |
| p-value (one-tailed) | **< 0.0001** | < 0.05 | ✅ PASS |
| 95% CI | [0.90, 1.00] | — | — |
| N models | 16 | ≥ 10 | ✅ PASS |

**Interpretation.** Fairness rankings (BBQ-Disambig → BBQ-Ambig) are near-perfectly preserved after controlling for general capability (MMLU). A model ranked among the fairest in disambiguated evaluation contexts will rank among the fairest in ambiguous contexts where stereotype pressure is maximal. This is consistent with fairness failures encoding stable latent properties of model representations — pretraining-induced stereotypical associations persist across the BBQ context shift.

The magnitude (ρ = 0.962) substantially exceeds our a priori threshold (0.4) and our expected range (0.45–0.75). This unexpected strength raises two competing interpretations we address in Section 6.

**Sensitivity analysis.** Substituting Winogrande for MMLU as the capability covariate yields partial ρ = 0.969 (N=14, p < 0.0001) — near-identical to the MMLU result (Figure 5, Appendix). Fairness rank stability is not an artifact of the MMLU proxy choice.

---

### 5.3 RQ3: Adversarial Robustness Rank Stability (Mechanism Test)

We present RQ3 before RQ2 because the mechanism test result reframes the interpretation of the Δρ analysis.

Figure 3 (rank_reversal_heatmap.png) shows model rank positions across benchmark pairs. The absence of color discontinuities — zero rank reversals across all pairs — is the visual summary of the finding.

| Pair | Partial ρ | p-value | Rank Reversals | Gate |
|------|-----------|---------|----------------|------|
| ANLI R1 → R3 | **0.684** | 0.007 | 0 | FAIL (≥0.4, sig) |
| OOD Robustness | **0.868** | 0.0001 | 0 | FAIL (≥0.4, sig) |

Both adversarial robustness pairs show significantly positive partial ρ after MMLU control, and zero rank reversals. The hypothesis that adversarial benchmark construction disrupts rank stability is **falsified**. ρ_OOD = 0.868 substantially exceeds the threshold that would indicate disruption.

Figure 6 (rank_scatter_anli.png) shows ANLI R1 vs ANLI R3 rank scatter. Despite ANLI R3 being constructed specifically to defeat models that passed R1 (iterative adversarial human-in-the-loop protocol), model rank ordering is strongly preserved.

**Interpretation.** Adversarial robustness appears to be a stable latent model property — possibly related to training data breadth, instruction-tuning quality, or base architecture robustness — that persists across adversarial difficulty escalation. This contradicts the adversarial disruption mechanism proposed from the DecodingTrust GPT-3.5/4 anecdote [Wang et al., 2023]. At N=2, rank ordering can reverse by chance; at N=13 with diverse model families, the stable ordering emerges.

---

### 5.4 RQ2: Fairness > Robustness Stability (P2 — Exploratory)

Figure 2 (forest_plot.png) shows partial ρ with 95% CI for all three pairs, with the preregistered Δρ threshold marked.

| Metric | Value | Criterion | Status |
|--------|-------|-----------|--------|
| Δρ = ρ_fairness − ρ_robust_mean | **0.192** | ≥ 0.200 | ❌ Near-miss |
| Fisher z-statistic | 2.265 | — | — |
| p-value (one-tailed) | **0.024** | < 0.05 | ✅ Directional significance |
| N | 13 | — | — |

The directional hypothesis — fairness stability exceeds robustness stability — is supported by Fisher z-test (p = 0.024). The preregistered effect size criterion (Δρ ≥ 0.200) was not met, falling short by 0.008. We report this as directional evidence, not a confirmed finding.

**Interpretation.** The fairness advantage in rank stability is present but small. Given N=13 for the robustness sample and the covariate sensitivity (Winogrande control reduces Δρ to 0.073), the 0.008 shortfall reflects real measurement uncertainty. The correct characterization is: fairness shows marginally stronger rank stability than adversarial robustness, directionally significant, not confirmed at the preregistered effect size.

---

### 5.5 Summary

Table 1 consolidates all results.

**Table 1.** Partial Spearman ρ (MMLU-controlled) for all trustworthiness dimension pairs.

| Dimension | Pair | N | Partial ρ | p-value | Raw ρ | Gate | P-Criterion |
|-----------|------|---|-----------|---------|-------|------|-------------|
| Fairness | BBQ-Disambig→Ambig | 16 | **0.962** | <0.0001 | 0.979 | PASS | P1 ✅ |
| Robustness | ANLI R1→R3 | 13 | **0.684** | 0.007 | 0.983 | FAIL* | — |
| Robustness | OOD Robustness | 13 | **0.868** | 0.0001 | 0.984 | FAIL* | — |
| Δρ (fairness−robust_mean) | — | 13 | **0.192** | 0.024† | −0.005 | — | P2 ❌ (directional) |

*Gate FAIL = falsification criterion triggered: partial ρ is significantly positive, contradicting the adversarial disruption hypothesis.  
†Fisher z-test for dependent correlations [Meng et al., 1992]. Note: ρ_fairness in the Δρ computation is re-estimated on the N=13 robustness model subset (ρ=0.967) to ensure same-sample comparison; the N=16 fairness estimate (ρ=0.962) is reported separately in Table row 1.
