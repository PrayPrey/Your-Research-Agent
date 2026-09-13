---
hypothesis_title: "Capability-Modulated Bidirectional Alignment Asymmetry in LLM Evaluation"
hypothesis_id: "H-BiAlign-v1"
date: "2026-08-04"
confidence_level: 0.78
total_hypothesis_count: 5
research_scope_mode: "incremental"
scope_reduction_percentage: 75
requires_transfer_validation: false
include_condition_hypotheses: true
condition_hypothesis_count: 1
causal_chain_count: 3
phase2a_source: "03_refinement.yaml"
stepsCompleted:
  - "step-00-init-environment"
  - "step-01-init-parsing"
  - "step-02-input-hypothesis"
  - "step-03-hypothesis-generation"
  - "step-04-hypothesis-inventory"
  - "step-05-risk-analysis"
  - "step-06-dependency-graph"
  - "step-07-timeline-planning"
  - "step-08-dialectical-analysis"
  - "step-09-summary"
  - "step-10-finalize"
status: complete
completedAt: "2026-08-04"
---

# Verification Plan: Capability-Modulated Bidirectional Alignment Asymmetry in LLM Evaluation

**Date:** 2026-08-04
**Hypothesis ID:** H-BiAlign-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 75% (6 of 8 claims are BUILD_ON — already established)**

| Claim | Status | Evidence Source |
|-------|--------|----------------|
| AlpacaEval 2.0 CSV (N=222) contains win_rate, length_controlled_winrate, avg_length | BUILD_ON | tatsu-lab/alpaca_eval GitHub; h-e1/h-m1 pipeline |
| Population-level mean(Δ) ≈ −16.37pp across N=58 typed models | BUILD_ON | h-m1 04_validation.md; h-m1_results.json |
| training_type does not predict Δ (p=0.662, d=0.136) — h-m1 FALSIFIED | BUILD_ON | failure_h-m1.md; Mann-Whitney U=109.0 |
| Within RLHF: GPT-4 Δ=−8.8pp vs wizardlm Δ=−32pp — capability signal visible | BUILD_ON | h-m1 reflection_report.md |
| Arena ELO is H→AI proxy (not AI→H) — r=0.97 with MT-Bench | BUILD_ON | failure_h-e1_run1.md; RC-1 root cause |
| LC_winrate empirically distinct from win_rate: ρ≈0.94 [Dubois 2024] | BUILD_ON | arXiv 2404.04475 |
| Direct empirical test of ρ(win_rate, LC_winrate \| avg_length) not in prior literature | **PROVE_NEW** | Phase 1 Semantic Scholar (15 papers); no direct test found |
| Capability-modulated bidirectional alignment gap is capability-dependent | **PROVE_NEW** | Primary hypothesis — requires Phase 4 verification |

**Phase 2B Instructions:** Focus only on PROVE_NEW claims. BUILD_ON claims are pre-validated from prior pipeline runs and published papers. The existence test (H-E1) is the critical MUST_WORK gate.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the scope of N=222 models in the publicly available AlpacaEval 2.0 leaderboard (win_rate, length_controlled_winrate, avg_length columns confirmed accessible), if model capability is higher (operationalized as raw human preference win_rate), then length-debiased preference score (LC_winrate) is also higher beyond what verbosity (avg_length) explains, because high-capability models produce broad-spectrum quality outputs that satisfy both human annotators and AI-based length-controlled evaluation systems simultaneously, while low-capability models disproportionately exploit verbosity/formatting heuristics that the LC correction strips away.

**Formally:** ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15.

### 1.2 Alternative Hypothesis (H0)

There is no significant partial correlation between model capability (win_rate) and length-debiased preference score (LC_winrate) after controlling for response verbosity (avg_length). Any observed correlation between win_rate and LC_winrate is fully explained by verbosity, not by capability per se.

**H0:** ρ(win_rate, LC_winrate | avg_length) = 0.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | AlpacaEval 2.0 Leaderboard (standard) | N=222 models with all required columns confirmed accessible. Zero data acquisition risk. Validated in h-e1/h-m1 pipeline. Single-CSV design avoids all prior cross-leaderboard failure modes. |
| **Model** | N/A — statistical analysis study | No model training or inference required. Analysis operates on pre-computed evaluation scores. Reuses h-e1/h-m1 code infrastructure. |

**Dataset Details:**
- Source: https://github.com/tatsu-lab/alpaca_eval
- Path: docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv

**Model Details:**
- Type: observational analysis
- Source: AlpacaEval 2.0 CSV provides pre-computed scores for 222 LLMs

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| h-m1: Mann-Whitney on RLHF vs SFT Δ | p=0.662, Cohen's d=0.136 (FAIL) | AlpacaEval 2.0 N=58 typed subset | Categorical training_type too coarse; within-group capability variation confounds test; insufficient power (N_RLHF=20, N_SFT=10) |
| Dubois 2024 GLM length control | ρ(win_rate, LC_winrate) ≈ 0.94 | AlpacaEval 2.0 N=222 | Documents correlation but does not test whether capability independently explains LC preference beyond verbosity |
| Null model (no capability effect) | H0: ρ = 0 | N/A | Verbosity-only explanation; contradicted by h-m1 within-RLHF observation |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | win_rate is a valid proxy for model capability (not just verbosity/popularity signal) | AlpacaEval 2.0 uses human annotators; strong correlation with MT-Bench and Chatbot Arena (Dubois 2024); h-m1 within-RLHF group tracks quality gradient | Partial correlation not interpretable as capability-Δ relationship; however Hu 2024 desirability channel shows win_rate has length-independent component |
| A2 | VIF(win_rate, avg_length) < 5 — moderate collinearity at most | win_rate and avg_length measure qualitatively different things; VIF for ρ=0.5 ≈ 1.33, for ρ=0.7 ≈ 1.96; only ρ>0.9 gives VIF>5 | OLS β coefficients imprecise; H-M (dominance comparison) fails; mitigation: Shapley dominance analysis or ridge regression; H-E1 partial correlation is VIF-robust |
| A3 | Capability-Δ relationship in h-m1 (N=58 typed subset) generalizes to full N=222 | Full leaderboard contains broader capability range; larger N increases statistical power | N=58 within-RLHF gradient may be RLHF-specific; run analysis on both N=222 and N=58 separately |
| A4 | AlpacaEval 2.0 dataset is representative (not biased toward specific model families) | N=222 from diverse sources; includes GPT-4, Claude, Llama, Mistral, open-source variants; Dubois 2024 validation against Chatbot Arena | Family-dominated dataset would reflect training differences rather than general capability; check model family distribution |
| A5 | Directional prediction holds: high capability → smaller \|Δ\| (ρ > 0 for partial) | h-m1 within-RLHF observation; theoretical mechanism; Li et al. 2024 evaluator convergence | If reversed: high-capability models show MORE negative Δ (LC penalizes high-quality long outputs) — equally interesting but opposite finding |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical quantification of capability-modulated bidirectional alignment asymmetry across N=222 LLMs using the AlpacaEval 2.0 leaderboard.

**Key Innovation:** Repurposing Δ = LC_winrate − win_rate from "evaluation artifact to correct" to "bidirectional alignment gap signal to explain" — connecting LLM evaluation methodology to bidirectional alignment theory (Shen et al. 2024).

**Differentiation:**
- **vs. Dubois 2024:** Dubois treats Δ as a bias correction. We treat Δ as a signal: does the correction NEED to be as large for high-capability models?
- **vs. Hu 2024:** Hu decomposes win_rate into desirability + information mass but does not test whether this decomposition varies by capability level across models.
- **vs. h-m1 (FALSIFIED):** h-m1 used categorical training_type (p=0.662). This uses continuous win_rate and partial correlation — more powerful and better specified.
- **vs. Shen 2024:** Shen identified the empirical gap as open. This work closes it with a concrete operationalization.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Statement (Brief) | Prerequisites | Source |
|----|------|------|-------------------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | ρ(win_rate, LC_winrate \| avg_length) > 0, p < 0.05, \|r_partial\| ≥ 0.15 | None | SH1 (Phase 2A) |
| H-M1 | MECHANISM | MUST_WORK | win_rate has length-independent quality signal (desirability channel); |β_win_rate_std| > |β_avg_length_std| in standardized OLS | H-E1 | Causal Step 1 |
| H-M2 | MECHANISM | SHOULD_WORK | LC evaluator rewards capability-intrinsic properties at rate proportionate to capability; mechanism confirmed via OLS diagnostics | H-M1 | Causal Step 2 |
| H-M3 | MECHANISM | SHOULD_WORK | Delta (LC_winrate − win_rate) is smaller for high-capability models; Kruskal-Wallis across win_rate quartiles p < 0.05 | H-M2 | Causal Step 3 |
| H-C1 | CONDITION | SHOULD_WORK | Quartile effect is monotonic: Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05; capability-alignment relationship holds at population extremes | H-M3 | Scope/P3 |

**Total: 5 hypotheses** (H-E1 + H-M1 + H-M2 + H-M3 + H-C1)

> Note: Re-counting includes H-M2 separately from H-M1 based on 3-step causal chain. Total = 5.

---

### 2.2 Hypothesis Specifications

---
**H-E1: Existence of Capability-Independent LC Preference Signal**

**Statement:** Under AlpacaEval 2.0 N=222 models with confirmed columns (win_rate, LC_winrate, avg_length), if model capability (win_rate) is higher, then length-debiased preference (LC_winrate) is also higher after controlling for verbosity (avg_length), because capability has a length-independent quality component (desirability channel). Formally: ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15.

**Rationale:** This is the MUST_WORK foundation. If the partial correlation is not significant, the entire hypothesis is falsified. Three independent evidence sources (h-m1 within-RLHF gradient, Dubois 2024 ρ≈0.94, Hu 2024 desirability channel) support existence. Resolves h-m1 failure by using continuous predictor instead of categorical training_type.

**Variables:**
- Independent: win_rate (continuous; human preference win fraction; capability proxy)
- Dependent: length_controlled_winrate (continuous; GLM-debiased preference score; PRIMARY DV)
- Controlled: avg_length (continuous; mean response token length; verbosity confound)

**Verification Protocol:**
1. Load AlpacaEval 2.0 CSV; drop missing values; verify N ≥ 200 after cleaning.
2. Compute VIF(win_rate, avg_length) as diagnostic for H-M1 gate design.
3. Run `pingouin.partial_corr(x='win_rate', y='length_controlled_winrate', covar='avg_length')`.
4. Bootstrap CI (1000 resamples) for Spearman correlations as robustness check.
5. Replicate on N=58 typed subset for comparison with h-m1 prior results.

**Success Criteria:**
- Primary: r_partial > 0 AND p < 0.05 (two-tailed) AND |r_partial| ≥ 0.15
- Secondary: Bootstrap 95% CI for r_partial excludes 0

**Gate:** MUST_WORK — if H-E1 fails: STOP, route to Phase 0 with documented failure mode.

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Prediction P1

---

**H-M1: Capability Dominates Verbosity in OLS Prediction of LC Preference**

**Statement:** In standardized OLS regression (LC_winrate ~ win_rate_std + avg_length_std) on AlpacaEval 2.0 N=222, the absolute standardized coefficient for capability (|β_win_rate_std|) exceeds that for verbosity (|β_avg_length_std|), indicating capability is the dominant predictor of length-debiased preference beyond verbosity.

**Rationale:** Tests Causal Step 1: high-capability models produce length-independent quality (desirability channel from Hu 2024). VIF-contingent gate ensures interpretability. Builds on H-E1 by quantifying relative dominance. MUST_WORK because it validates the primary causal mechanism.

**Variables:**
- Independent: win_rate_std (StandardScaler normalized)
- Dependent: length_controlled_winrate
- Controlled: avg_length_std (StandardScaler normalized, covariate in OLS)

**Verification Protocol:**
1. Apply StandardScaler to win_rate and avg_length.
2. Run OLS: LC_winrate ~ win_rate_std + avg_length_std (statsmodels OLS).
3. IF VIF(win_rate_std, avg_length_std) < 5: compare |β_win_rate_std| vs |β_avg_length_std|.
4. IF VIF ≥ 5: run Shapley-value dominance analysis (sklearn permutation importance).
5. Report OLS diagnostics: Breusch-Pagan test, QQ plot, residual plot.

**Success Criteria:**
- Primary: |β_win_rate_std| > |β_avg_length_std|, both with p < 0.05
- Alternative (if VIF ≥ 5): Shapley(win_rate) > Shapley(avg_length)

**Gate:** MUST_WORK — if H-M1 fails: document as scope limitation; does not invalidate H-E1.

**Dependencies:** H-E1 (PASS required)

**Source:** Phase 2A SH2, Prediction P2, Causal Step 1

---

**H-M2: LC Evaluator Rewards Capability-Intrinsic Properties Proportionate to Capability**

**Statement:** High-capability models (high win_rate) receive higher LC_winrate not merely because of length effects but because the LC GLM correction reveals a residual capability signal: ρ(win_rate_residual, LC_winrate_residual) > 0 after partialling out avg_length from both variables. This confirms the LC evaluator rewards capability-intrinsic properties.

**Rationale:** Tests Causal Step 2: the LC evaluation system itself is sensitive to capability beyond length. This is the mechanism that explains WHY partial correlation is positive. Builds on H-M1 by confirming the residual signal is not an artifact of covariate structure.

**Variables:**
- Independent: win_rate residualized on avg_length
- Dependent: LC_winrate residualized on avg_length
- Controlled: avg_length (regressed out from both IV and DV)

**Verification Protocol:**
1. Regress win_rate on avg_length; save residuals (win_rate_resid).
2. Regress LC_winrate on avg_length; save residuals (lc_resid).
3. Compute Spearman ρ(win_rate_resid, lc_resid) with bootstrap CI.
4. This should reproduce H-E1 r_partial numerically (consistency check).
5. Report as mechanistic confirmation of the residual capability signal.

**Success Criteria:**
- Primary: ρ(win_rate_resid, lc_resid) > 0 AND p < 0.05
- Consistency: Numerically close to H-E1 r_partial (within 0.02)

**Gate:** SHOULD_WORK — failure documents mechanism complexity, does not invalidate H-E1 or H-M1.

**Dependencies:** H-M1 (PASS preferred)

**Source:** Phase 2A Causal Step 2, evidence: Li et al. 2024, Dubois 2024

---

**H-M3: Bidirectional Alignment Gap (Δ) Is Smaller for High-Capability Models**

**Statement:** The bidirectional alignment gap (Δ = LC_winrate − win_rate) is smaller (less negative) for high-capability models (high win_rate), such that there is a significant negative correlation ρ(win_rate, Δ) < 0 and/or win_rate quartiles show significantly different Δ distributions (Kruskal-Wallis p < 0.05).

**Rationale:** Tests Causal Step 3: the capability-alignment relationship manifests as reduced alignment gap for high-capability models. This is the core claim of the "bidirectional alignment gap" framing. Uses Δ as secondary DV (after resolving the composition problem by using LC_winrate as primary DV in H-E1/H-M1/H-M2).

**Variables:**
- Independent: win_rate (continuous) / win_rate quartiles (categorical)
- Dependent: Δ = length_controlled_winrate − win_rate (alignment gap; secondary DV)
- Controlled: avg_length (covariate for OLS on Δ)

**Verification Protocol:**
1. Compute Δ = length_controlled_winrate − win_rate for all N=222 models.
2. Compute Spearman ρ(win_rate, Δ); note mathematical dependency (−win_rate in Δ).
3. Run OLS: Δ ~ win_rate_std + avg_length_std to partial out trivial composition component.
4. Run Kruskal-Wallis on Δ across win_rate quartiles (pd.qcut q=4).
5. Report correlation as secondary evidence; primary test remains H-E1.

**Success Criteria:**
- Primary: Kruskal-Wallis p < 0.05 (Δ differs across capability quartiles)
- Secondary: ρ(win_rate, Δ) < 0 AND p < 0.05 (with caveat about mathematical dependency)

**Gate:** SHOULD_WORK — failure does not invalidate H-E1 or H-M1.

**Dependencies:** H-M2 (informational dependency)

**Source:** Phase 2A Causal Step 3, h-m1 observation (GPT-4 vs wizardlm within-RLHF)

---

**H-C1: Monotonic Quartile Effect — Capability-Alignment Relationship Holds at Extremes**

**Statement:** The capability-alignment relationship is monotonic across win_rate quartiles: Q4 (highest capability) shows significantly higher LC_winrate than Q1 (lowest capability) after Bonferroni correction (Dunn post-hoc Q1 vs Q4, Bonferroni-corrected p < 0.05), confirming the relationship holds at population extremes.

**Rationale:** Boundary condition test. Tests whether the capability effect is monotonic and holds at the extremes of the capability distribution, not just on average. If the relationship is U-shaped or only holds in the middle range, this is a scope limitation that narrows generalizability.

**Variables:**
- Independent: win_rate quartiles (Q1-Q4 from pd.qcut)
- Dependent: length_controlled_winrate (distribution per quartile)
- Controlled: Within-quartile avg_length variation (acknowledged limitation)

**Verification Protocol:**
1. Create quartile variable: pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4']).
2. Run Kruskal-Wallis on LC_winrate across all 4 quartiles.
3. Run scikit_posthocs.posthoc_dunn for pairwise comparisons.
4. Apply Bonferroni correction; focus on Q1 vs Q4 comparison.
5. Visualize: boxplot of LC_winrate per quartile with median lines.

**Success Criteria:**
- Primary: Kruskal-Wallis p < 0.05 AND Dunn Q1 vs Q4 Bonferroni-corrected p < 0.05
- Secondary: Monotonic median trend Q1 < Q2 < Q3 < Q4 (not required for gate)

**Gate:** SHOULD_WORK — failure narrows scope but does not invalidate H-E1, H-M1, H-M2, or H-M3.

**Dependencies:** H-M3 (informational dependency)

**Source:** Phase 2A SH3, Prediction P3, Scope analysis

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (MUST_WORK) → H-M1 (MUST_WORK) → H-M2 (SHOULD_WORK) → H-M3 (SHOULD_WORK) → H-C1 (SHOULD_WORK)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | r_partial > 0 AND p < 0.05 AND \|r_partial\| ≥ 0.15 | STOP — route to Phase 0; document failure mode |
| H-M1 | MUST_WORK | \|β_win_rate_std\| > \|β_avg_length_std\| (or Shapley if VIF ≥ 5) | Document scope limitation; H-E1 still valid |
| H-M2 | SHOULD_WORK | ρ(win_rate_resid, lc_resid) > 0, p < 0.05 | Document mechanism complexity; continue |
| H-M3 | SHOULD_WORK | Kruskal-Wallis p < 0.05 on Δ across quartiles | Document limitation; continue |
| H-C1 | SHOULD_WORK | Dunn Q1 vs Q4 Bonferroni p < 0.05 | Narrow scope; relationship may not hold at extremes |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |
| Phase 2.5: Condition | H-C1 | 1 week |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: VIF collinearity between win_rate and avg_length | A2 | H-M1, H-M2, H-M3 | Critical (managed) |
| R2: win_rate as capability proxy validity | A1 | H-E1, H-M1 | High (inherent) |
| R3: N=222 generalizability to 2025+ era | A3, A4 | All hypotheses | Medium |
| R4: Dataset family dominance bias | A4 | H-M1, H-M3 | Medium |
| R5: Directional reversal (rho < 0) | A5 | H-E1 (gate condition) | Medium |

### 4.2 Mitigation Strategies

**Risk R1: VIF Collinearity (CRITICAL — MANAGED)**
- Source: A2 — VIF(win_rate, avg_length) unknown pre-experiment
- Affected: H-M1, H-M2, H-M3
- Prevention: Implement VIF diagnostic before any OLS interpretation
- Detection: VIF computation in first analysis step
- Response:
  - IF VIF < 5: proceed with OLS beta comparison (standard approach)
  - IF VIF ≥ 5: switch to Shapley-value dominance analysis (sklearn permutation importance)
  - H-E1 partial correlation is VIF-robust — valid regardless of collinearity
- Early Warning: ρ(win_rate, avg_length) > 0.85 in EDA would signal VIF > 5

**Risk R2: win_rate Proxy Validity (HIGH — INHERENT)**
- Source: A1 — win_rate conflates capability with response style preferences
- Affected: H-E1, H-M1
- Prevention: Partial correlation controls for avg_length (primary verbosity confound)
- Detection: Check ρ(win_rate, avg_length) in EDA; if > 0.85, verbosity dominates
- Response: Acknowledge in limitations that win_rate includes length-independent style preferences; Hu 2024 desirability channel provides mechanistic support
- Note: Inherent to observational design; cannot be fully resolved without experimental manipulation

**Risk R3: Temporal Generalizability (MEDIUM)**
- Source: A3 — AlpacaEval 2.0 reflects 2023-2024 era models
- Affected: All hypotheses
- Prevention: Explicitly scope conclusions to 2023-2024 era in all results
- Detection: Not applicable within experiment scope
- Response: Note in paper limitations; suggest replication with 2025/2026 leaderboard data when available
- Note: Out of scope for this hypothesis; acceptable limitation

**Risk R4: Dataset Family Bias (MEDIUM)**
- Source: A4 — N=222 may be dominated by specific model families
- Affected: H-M1, H-M3
- Prevention: Report model family distribution in descriptive statistics
- Detection: Count unique model families; check if any family > 30% of N=222
- Response: Run family-stratified robustness check; report family-specific effect sizes as sensitivity analysis

**Risk R5: Directional Reversal (MEDIUM — MONITORING)**
- Source: A5 — direction expected ρ > 0 but could be ρ < 0 if information mass dominates
- Affected: H-E1 gate condition
- Prevention: Pre-specify that both directions are publishable
- Detection: Check sign of r_partial before significance test
- Response:
  - IF r_partial > 0: thesis supported (expected)
  - IF r_partial < 0: antithesis supported (equally interesting — LC penalizes high-quality long outputs)
  - Document as pre-specified analysis regardless of direction

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | VIF collinearity | A2 | Critical (managed) | H-M1/M2/M3 | VIF-contingent gate: OLS if <5, Shapley if ≥5 |
| R2 | win_rate proxy validity | A1 | High (inherent) | H-E1, H-M1 | Partial correlation controls avg_length; acknowledge in limitations |
| R3 | Temporal generalizability | A3 | Medium | All | Scope to 2023-2024 era explicitly |
| R4 | Family dominance bias | A4 | Medium | H-M1, H-M3 | Report family distribution; family-stratified robustness check |
| R5 | Directional reversal | A5 | Medium | H-E1 | Pre-specify both directions; both publishable |

**Critical Risks: 1 (managed) | High Risks: 1 (inherent) | Medium Risks: 3 | Low Risks: 0**

### 4.4 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| h-m1: categorical training_type (p=0.662) | Coarse predictor misses within-group variation | Use continuous win_rate instead of categorical |
| h-e1-run1: Arena ELO misclassified as AI→H | Proxy direction errors | Use only AlpacaEval 2.0 LC within single CSV |
| h-e1: cross-leaderboard fuzzy matching failures | Model name matching errors | Single-CSV design; no fuzzy matching needed |

---

## 5. Execution Plan: DAG & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root: MUST_WORK]
    H-E1 (EXISTENCE — no dependencies)
         │  GATE 1: r_partial > 0, p < 0.05, |r| ≥ 0.15
         ▼  FAIL → STOP (Phase 0)
[Level 1 — Core Mechanism: MUST_WORK]
    H-M1 ← H-E1
         │  GATE 2: |β_win_rate_std| > |β_avg_length_std|
         ▼  FAIL → document; continue
[Level 2 — Mechanism Confirmation: SHOULD_WORK]
    H-M2 ← H-M1
         │  GATE 3: ρ(resid_win_rate, resid_lc) > 0, p < 0.05
         ▼  FAIL → document; continue
[Level 3 — Gap Analysis: SHOULD_WORK]
    H-M3 ← H-M2
         │  GATE 4: Kruskal-Wallis on Δ across quartiles p < 0.05
         ▼  FAIL → document; continue
[Level 4 — Boundary Condition: SHOULD_WORK]
    H-C1 ← H-M3
         │  GATE 5: Dunn Q1 vs Q4 Bonferroni p < 0.05
         ▼  FAIL → narrow scope

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 (both MUST_WORK)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-C1 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses, 6 Weeks Total
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3     │ W4     │ W5     │ W6
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 1: Foundation
  H-E1              │ ████████│        │        │        │
  [Gate 1]          │       ◆ │        │        │        │
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 2: Mechanisms
  H-M1              │         │ ██████ │        │        │
  H-M2              │         │        │ ██████ │        │
  H-M3              │         │        │        │ ██████ │
  [Gate 2]          │         │      ◆ │        │        │
────────────────────┼─────────┼────────┼────────┼────────┼────────
PHASE 2.5: Condition
  H-C1              │         │        │        │        │ ██████
  [Gate 3]          │         │        │        │        │      ◆
════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
Critical Path: H-E1 (W1-2) → H-M1 (W3) = 3 weeks minimum
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 (MUST_WORK chain)
  H-E1: 2 weeks (partial correlation + diagnostics)
  H-M1: 1 week (OLS + VIF check + dominance analysis)
  Minimum viable: 3 weeks to critical gate decision

Total Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
  Duration: 2 + 1 + 1 + 1 + 1 = 6 weeks

Slack: 0 weeks (all sequential, all statistical analysis)

Note: This is a statistical analysis study (CPU-only). Each
hypothesis runs in <1 minute computationally. "Weeks" reflect
iteration, review, and reporting time, not compute time.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 3 (H-M1, H-M2, H-M3)
  - Condition: 1 (H-C1)

Verification Phases: 3
  1. Foundation (H-E1) — 2 weeks
  2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks
  3. Condition (H-C1) — 1 week

Compute Resources: CPU-only; <1 min per hypothesis
Data: Single CSV (AlpacaEval 2.0, N=222; already downloaded)
Libraries: scipy, statsmodels, pingouin, scikit_posthocs, sklearn
Code Reuse: h-e1/h-m1 pipeline infrastructure

Total Duration: 6 weeks
Critical Path: 3 weeks (H-E1 + H-M1)
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

1. Execute H-E1 (Foundation) — Week 1-2
2. Evaluate Gate 1: r_partial > 0, p < 0.05, |r| ≥ 0.15
   - FAIL → STOP; route to Phase 0
   - PASS → proceed to Phase 2
3. Execute H-M1 (Dominance test) — Week 3
4. Evaluate Gate 2: |β_win_rate_std| vs |β_avg_length_std| (or Shapley if VIF ≥ 5)
5. Execute H-M2 (Residual confirmation) — Week 4
6. Execute H-M3 (Gap analysis) — Week 5
7. Evaluate Gate 3: Kruskal-Wallis on Δ across quartiles
8. Execute H-C1 (Boundary condition) — Week 6
9. Evaluate Gate 4: Dunn Q1 vs Q4 Bonferroni-corrected
10. Verification complete — route to Phase 3/4 for implementation

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Model capability (win_rate) independently predicts LC_winrate after controlling for verbosity, with ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15. High-capability models exhibit smaller bidirectional alignment gap independent of response length.

**Supporting Evidence:**
1. h-m1 within-RLHF empirical observation: GPT-4 (Δ=−8.8pp) vs wizardlm (Δ=−32pp) — 2.3x capability-Δ gradient within same training type (direct empirical prior)
2. Hu et al. 2024 desirability decomposition: win_rate has length-independent quality component that survives LC correction (mechanistic support)
3. Li et al. 2024: capability drives evaluator preference convergence across LLM sizes — capability intrinsic to evaluation agreement (theoretical support)

**Strengths:**
- Zero data acquisition risk — single confirmed CSV
- Resolves h-m1 failure directly (continuous vs categorical predictor)
- First empirical quantification of capability-modulated alignment gap
- VIF-contingent gate design handles primary methodological risk
- N=222 provides statistical power ≥ 0.82 for |ρ| ≥ 0.2

**Expected Outcomes:**
- Primary (P1): r_partial ≈ 0.3-0.5 based on h-m1 within-RLHF extrapolation
- Secondary (P2): |β_win_rate_std| > |β_avg_length_std| in OLS
- Tertiary (P3): Kruskal-Wallis p < 0.05 + Dunn Q1 vs Q4 p < 0.05

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant partial correlation between win_rate and LC_winrate after controlling for avg_length. Any observed correlation is fully mediated by verbosity. Δ is constant across capability levels.

**Counter-Arguments:**
1. VIF(win_rate, avg_length) may be high enough to make partial correlation uninformative — capability and verbosity may be insufficiently orthogonal in this dataset
2. h-m1 precedent: if categorical training_type failed (p=0.662), continuous win_rate may also fail at population scale (though different operationalization)
3. Information mass argument (Hu 2024): high-capability models may produce longer, richer responses — LC correction penalizes them equally, creating rho ≈ 0

**Potential Failure Points:**
- Failure 1 (R1): VIF ≥ 5 → OLS interpretation fails; Shapley may show avg_length dominates
- Failure 2 (R2): win_rate primarily reflects formatting preferences, not quality → partial correlation not interpretable as capability effect
- Failure 3 (R5): Direction reversal → r_partial < 0 (LC penalizes high-quality long outputs)

**Conditions Under Which H0 Would Be Supported:**
- r_partial ≤ 0 OR p ≥ 0.05 OR |r_partial| < 0.15 → H-E1 FAILS
- VIF ≥ 5 AND Shapley(avg_length) > Shapley(win_rate) → H-M1 FAILS
- Kruskal-Wallis p ≥ 0.05 on Δ → H-M3 FAILS (SHOULD_WORK level)

### 6.3 Synthesis

**Balanced Assessment:**

H-BiAlign-v1 presents a well-specified, testable claim with three independent evidence sources (h-m1 empirical observation, Hu 2024 mechanism, Dubois 2024 correlation structure). However, the null hypothesis raises valid concerns about collinearity and proxy validity in an observational design.

**Resolution Path:**

The verification plan addresses the dialectic through:
1. **Foundation verification (H-E1):** Partial correlation is VIF-robust — establishes existence regardless of collinearity level
2. **Sequential mechanism testing (H-M1-M3):** VIF-contingent gate handles the primary antithesis risk systematically
3. **Clear gate conditions:** Allow early detection of H0 support with documented failure modes and Phase 0 routing

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (r_partial > 0, p < 0.05, |r| ≥ 0.15)
- H-M1 MUST_WORK gate passes (capability dominates verbosity in OLS or Shapley)

**Conditions for Antithesis Support:**
- H-E1 fails (r_partial ≤ 0 OR p ≥ 0.05 OR |r| < 0.15) → H0 confirmed, route Phase 0
- VIF ≥ 5 AND Shapley(avg_length) > Shapley(win_rate) → mechanism fails (SHOULD_WORK)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M2 + H-M3 + H-C1 all pass → thesis fully validated
2. **Partial Support:** H-E1 + H-M1 pass; H-M2/H-M3/H-C1 fail → capability effect exists, mechanism more complex
3. **Mechanism Partial:** H-E1 passes; H-M1 fails → capability effect real but verbosity co-prediction; scope limitation
4. **No Support:** H-E1 fails → H0 supported; route to Phase 0 with documented failure

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | ρ(partial) > 0 supported by 3 evidence sources | VIF collinearity may wash out signal | H-E1 partial corr is VIF-robust |
| Mechanism | Capability dominates via OLS betas | VIF ≥ 5 makes beta comparison invalid | VIF-contingent Shapley fallback |
| Gap Analysis | Δ decreases with capability | Mathematical dependency in Δ = LC - win | OLS on Δ controls for composition |
| Scope | Holds for N=222 full leaderboard | Family dominance may confound | Family-stratified robustness check |
| Direction | ρ > 0 (capability → LC preference) | Information mass may reverse direction | Pre-specified: both directions publishable |

**Overall Robustness Score:** High (for existence test H-E1); Medium (for mechanism tests H-M1-M3)

**Confidence in Verification Plan:** 0.78 (reflects appropriate uncertainty about VIF and direction)

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** Capability (win_rate) independently predicts LC_winrate beyond verbosity in AlpacaEval 2.0 N=222.
- ID: H-BiAlign-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (75% scope reduction from BUILD_ON claims)
- Sub-Hypotheses: 5 total (H-E1, H-M1, H-M2, H-M3, H-C1)
- Phases: 3 phases over 6 weeks
- Critical Gates: 2 MUST_WORK (H-E1, H-M1) + 3 SHOULD_WORK

**Risk Assessment:** Medium (1 Critical managed, 1 High inherent, 3 Medium scope)
- Primary concerns: VIF collinearity (managed by contingent design); win_rate proxy validity (inherent)

**Immediate Action:** Begin Phase 1 with H-E1 (partial correlation on N=222 AlpacaEval 2.0 CSV)

### Key Achievements

- 5 hypotheses across 3 phases (H-E: 1, H-M: 3, H-C: 1)
- H0 addressed: ρ(win_rate, LC_winrate | avg_length) = 0 — verbosity fully explains LC preference
- 75% scope reduction achieved — BUILD_ON claims not re-tested
- VIF-contingent gate design handles primary collinearity risk
- All five prior failure modes explicitly avoided (single-CSV design)

### Verification Execution Order

**Phase 1: Foundation (2 weeks)**
- H-E1: ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15
- Gate 1: MUST PASS → if fail, route Phase 0

**Phase 2: Core Mechanisms (3 weeks)**
- H-M1 (W3): |β_win_rate_std| > |β_avg_length_std| (VIF-contingent) [MUST_WORK]
- H-M2 (W4): ρ(win_rate_resid, lc_resid) > 0 [SHOULD_WORK]
- H-M3 (W5): Kruskal-Wallis on Δ across quartiles [SHOULD_WORK]
- Gate 2: H-M1 must pass (MUST_WORK)

**Phase 2.5: Condition (1 week)**
- H-C1 (W6): Dunn Q1 vs Q4 Bonferroni p < 0.05 [SHOULD_WORK]
- Gate 3: Failure narrows scope only

### Critical Decision Points

1. **Gate 1 (Foundation — Week 2):** H-E1 MUST PASS
   - FAIL → STOP entire pipeline; document as h-bialign-v1 failure; route to Phase 0
   - PASS → proceed to Phase 2 with confidence

2. **Gate 2 (Mechanism — Week 3):** H-M1 MUST PASS
   - FAIL → document capability effect real but mechanism not dominant; scope limitation; continue to H-M2
   - PASS → proceed to H-M2/M3

3. **Gate 3 (Condition — Week 6):** H-C1 SHOULD_WORK
   - FAIL → narrow scope: capability-alignment relationship may not hold at extremes; acceptable limitation

### Open Questions

- What is ρ(win_rate, avg_length) in AlpacaEval 2.0? (Determines VIF and collinearity strategy)
- Does the capability-Δ relationship hold within model families (GPT vs open-source) separately?
- At what win_rate threshold does |Δ| become negligible (< 5pp)?
- Does the h-m1 observation (GPT-4 Δ=−8.8pp vs wizardlm Δ=−32pp) hold at population scale N=222?

### Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (implement partial_corr test; EDA first to check VIF)
   - Run EDA before full analysis: compute ρ(win_rate, avg_length) to pre-assess VIF risk

2. **Resource Allocation:**
   - 6 weeks total on critical path; compute is trivial (CPU < 1 min per test)
   - Allocate iteration time for VIF diagnosis and contingent gate selection

3. **Failure Management:**
   - H-E1 fail: document failure_h-bialign-v1.md; extract lessons for Phase 0
   - H-M1 fail: document scope limitation; H-E1 result still publishable as partial finding
   - All SHOULD_WORK failures: document as scope limitations; proceed to Phase 3/4

---

## 8. Appendices

### A. Phase 2A Reference

- **Source:** 03_refinement.yaml (ID: H-BiAlign-v1)
- **Discussion:** 15 exchanges, 6 personas, all STRONG verdicts
- **Key Refinements:** DV changed from Δ to LC_winrate (Exchange 7); VIF-contingent H-M gate (Exchange 12); direction justified from h-m1 data (Exchange 7)

### B. MCP Tool Usage Summary

- **Total MCP calls:** 5 (incremental mode)
- **Tools used:**
  - mcp__clearThought__scientificmethod: 2 calls (H-E1-verification × 2 stages, H-M-integrated × 2 stages)
  - mcp__clearThought__collaborativereasoning: 1 call (risk analysis, 3-expert panel)
  - mcp__clearThought__structuredargumentation: 3 calls (thesis, antithesis, synthesis)
- **Archon:** Pipeline project found (ID: 00230e1d-d4dd-4478-8366-dd40e4513296)
