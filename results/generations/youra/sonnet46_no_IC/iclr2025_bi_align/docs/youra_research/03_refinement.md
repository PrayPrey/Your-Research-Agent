# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-04T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap_1
- **Gap Title**: Capability-Modulated Bidirectional Alignment Gap — No Direct Empirical Test
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) met at exchange 15 (min_exchanges=15 from phase2a_config.yaml). All 6 personas participated. Prof. Rex raised 5 distinct breaking points, all addressed constructively.

### Key Insights
1. h-m1 failure (training_type categorical predictor, p=0.662) directly motivates using continuous win_rate — a theoretically better-specified test of the same capability-alignment hypothesis.
2. DV changed from Δ = LC_winrate − win_rate to LC_winrate itself — eliminates composition problem (Δ contains −win_rate, creating mathematical dependency with predictor win_rate).
3. Partial correlation ρ(win_rate, LC_winrate | avg_length) is the critical test — raw Spearman alone could be a verbosity artifact.
4. The bidirectional alignment gap (Δ) repurposed from "evaluation artifact to correct" to "alignment gap signal to explain" — connects evaluation methodology to Shen et al. 2024 bidirectional alignment theory.
5. VIF-contingent gate design ensures H-M robustness without requiring pre-experimental knowledge of collinearity.

### Breakthrough Moments
- **Exchange 6** (Prof. Rex): Identified the composition problem in using Δ as DV — forced critical redesign to LC_winrate as DV, producing a stronger hypothesis.
- **Exchange 7** (Dr. Nova): Provided direction justification from h-m1 within-RLHF data (GPT-4 Δ=−8.8pp vs wizardlm Δ=−32pp) — critical prior empirical evidence.
- **Exchange 8** (Prof. Vera): Formalized exact falsification criteria — made the test operationally actionable.
- **Exchange 13** (Dr. Nova): Reframed novelty as "first quantification of capability-modulated bidirectional alignment gap" — elevated significance from correlation study to alignment theory contribution.

---

## Final Hypothesis

### Title
Capability-Modulated Bidirectional Alignment Asymmetry in LLM Evaluation

### Hypothesis ID
H-BiAlign-v1

### Core Claim
Under the scope of N=222 models in the publicly available AlpacaEval 2.0 leaderboard (win_rate, length_controlled_winrate, avg_length columns confirmed accessible), if model capability is higher (operationalized as raw human preference win_rate), then length-debiased preference score (LC_winrate) is also higher beyond what verbosity (avg_length) explains, because high-capability models produce broad-spectrum quality outputs that satisfy both human annotators and AI-based length-controlled evaluation systems simultaneously, while low-capability models disproportionately exploit verbosity/formatting heuristics that the LC correction strips away.

**Formal statement:** ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15.

**Equivalently:** In the bidirectional alignment gap interpretation, Δ = LC_winrate − win_rate is less negative for high-capability models — the human-AI annotator divergence is capability-modulated.

### Null Hypothesis
H0: ρ(win_rate, LC_winrate | avg_length) = 0 — no capability signal independent of verbosity; any correlation between win_rate and LC_winrate is fully explained by avg_length.

### Mechanism
Three-step causal chain:
1. **Desirability channel**: High-capability models produce outputs with high length-independent desirability (Hu et al. 2024) — quality that satisfies human annotators (win_rate) via non-verbosity signals.
2. **Evaluator convergence**: The GPT-4 LC evaluator also rewards these capability-intrinsic quality signals (accuracy, structure, task relevance), producing LC_winrate that tracks win_rate beyond length correction (ρ≈0.94 per Dubois 2024).
3. **Gap modulation**: Low-capability models inflate raw win_rate via length/formatting that the LC correction penalizes → large negative Δ. High-capability models satisfy both evaluators → small |Δ|. Within h-m1 RLHF group: GPT-4 Δ=−8.8pp (high capability) vs wizardlm Δ=−32pp (low capability).

---

## Predictions

| ID | Statement | Success Criterion | Level |
|----|-----------|-------------------|-------|
| P1 | ρ(win_rate, LC_winrate \| avg_length) > 0, p < 0.05 | r_partial > 0 AND p < 0.05 AND \|r_partial\| ≥ 0.15 | MUST_WORK |
| P2 | \|β_win_rate_std\| > \|β_avg_length_std\| in standardized OLS | Both β significant; capability β larger in absolute terms (or Shapley if VIF ≥ 5) | SHOULD_WORK |
| P3 | Kruskal-Wallis on LC_winrate across win_rate quartiles p < 0.05; Dunn Q1 vs Q4 p < 0.05 | Both tests significant; Q4 > Q1 direction confirmed | SHOULD_WORK |

---

## Novelty

**Novel contribution**: First empirical quantification of capability-modulated bidirectional alignment asymmetry across N=222 LLMs, using Δ = LC_winrate − win_rate as an alignment gap signal (not just an evaluation correction).

**Differentiation from prior work**:
- **Dubois 2024 (LC-AlpacaEval)**: Treats Δ as bias to correct → we treat Δ as signal to explain
- **Hu 2024 (Length decomposition)**: Decomposes mechanism but doesn't test capability variation across models
- **h-m1 (FALSIFIED)**: Used categorical training_type → we use continuous win_rate (better specified)
- **Shen et al. 2024 (Bidirectional survey)**: Identified open challenge → we close it empirically

---

## Experimental Design

**Dataset**: AlpacaEval 2.0 leaderboard CSV (N=222 models)
- Source: `tatsu-lab/alpaca_eval` GitHub (Apache 2.0 license)
- Path: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Columns: `name`, `win_rate`, `length_controlled_winrate`, `avg_length`

**Primary analysis**:
1. Load CSV; compute Δ; check missing values
2. VIF(win_rate, avg_length) diagnostic
3. OLS: `LC_winrate ~ win_rate_std + avg_length_std` (StandardScaler)
4. Partial correlation: `pingouin.partial_corr(x='win_rate', y='LC_winrate', covar='avg_length')`
5. Bootstrap CI (1000 resamples) for Spearman correlations
6. Kruskal-Wallis + Dunn post-hoc on win_rate quartiles

**Code reuse**: h-e1/h-m1 data loading and Δ computation code; no new dependencies needed beyond `pingouin` (lightweight).

---

## Limitations

1. win_rate is not a pure capability measure — conflates capability with response style preferences.
2. AlpacaEval 2.0 reflects 2023-2024 era LLMs — generalization to 2025/2026 models not guaranteed.
3. Analysis is observational — VIF or unmeasured confounds may affect coefficient interpretation.
4. VIF(win_rate, avg_length) unknown pre-experiment — contingent gate design addresses this.
5. Results may not generalize beyond instruction-following evaluation framework.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15; all 6 personas participated |
| **Clarity Verified** | Yes |
| **Remaining Objections** | VIF unknown (managed); novelty claim needs Phase 6 re-verification |
| **Phase 4 Gate** | H-E: ρ(win_rate, LC_winrate \| avg_length) > 0, p < 0.05, \|r_partial\| ≥ 0.15 — MUST_WORK |
| **Prior Failures Avoided** | All 5 modes: era mismatch, Arena ELO misclassification, training_type, cross-leaderboard, proxy collapse |

---

*Generated by Phase 2A Self-Play Loop (Claude-only, Independent-Controller Ablation)*
*Architecture: 6 personas × 15 exchanges × self-judged convergence*
