# 6. Discussion

## 6.1 Key Findings and Their Interpretation

**The LC correction preserves capability ordering.** Our primary finding — r_partial = 0.985 after verbosity control — provides empirical validation of AlpacaEval 2.0's core design goal. The LC correction removes verbosity inflation while leaving capability-intrinsic quality ordering intact. This is not obvious a priori: the LC correction could have introduced evaluation artifacts, reordered models based on response-style biases unrelated to capability, or been confounded by model family clustering. The near-perfect partial correlation across 223 diverse models suggests none of these alternatives dominate the signal.

**Why partial correlation exceeds bivariate.** The counterintuitive strengthening from ρ = 0.94 (bivariate, Dubois 2024) to ρ = 0.985 (partial, ours) deserves attention. Verbosity acts as a mild suppressor here: capable models write somewhat longer responses (ρ(win_rate, avg_length) ≈ 0.63), which shared length between win_rate and LC_winrate creates a small common-cause structure. Once this is partialled out, the residual variance in each metric reflects capability almost exclusively — hence the strengthening. This is consistent with Hu et al. [2024]'s theoretical decomposition, which predicts the desirability (length-independent capability) channel survives LC correction.

**The verbosity penalty.** β_len = −4.37 in standardized OLS is negative — verbosity, once capability is held constant, is *penalized* rather than rewarded by the LC evaluator. This is precisely the intended behavior: the LC correction should remove length rewards so that models optimizing response length for human annotators do not receive inflated LC scores. The negative coefficient confirms that the correction is directionally correct.

**Capability quartile structure.** The 7-fold difference in median LC_winrate between Q1 (7.14%) and Q4 (51.62%) models is substantively large. Ε² = 0.883 means quartile membership explains 88% of LC_winrate variance — models are highly stratified by capability, with little overlap between extreme quartiles.

## 6.2 The Alignment Gap Δ: Nuance and Interpretation

The non-monotonic Δ pattern — where Q3 models show the largest median Δ (5.43) rather than Q1 — is best understood as a combination of two factors:

1. **Mathematical dependency**: Δ = LC_winrate − win_rate, so when models are grouped by win_rate quartiles, Δ inherits a compositional dependency on the grouping variable. Spearman(win_rate, Δ) = −0.050 (p = 0.455) is non-significant precisely because of this self-referential structure. H-M3's KW test on Δ still passed (p = 5.97e-05), but the effect size (ε² = 0.088) is attenuated by ~10× compared to the LC_winrate-based test.

2. **Genuine Q3 heterogeneity**: Q3 models may exhibit a distinct verbosity-exploitation signature — mid-high capability combined with verbose responses that the LC correction upgrades more dramatically, producing large positive Δ. This interpretation is speculative without model-level verbosity analysis, but is consistent with the Q3 > Q1 median Δ pattern.

The practical implication is clear: for studies examining capability-alignment relationships, LC_winrate is the more appropriate and interpretable dependent variable; Δ introduces self-referential noise that attenuates effect sizes.

## 6.3 Limitations

**L1: Observational study — association, not causation.** All findings are correlational. We cannot rule out unmeasured confounders (model family, training data size, RLHF budget, base model) that co-vary with both win_rate and LC_winrate. The correct interpretation is: "win_rate independently *predicts* LC_winrate beyond verbosity," not "model capability *causes* LC preference." Controlled experimentation (e.g., interventions holding verbosity constant while varying training) would be required for causal claims.

**L2: Single dataset (AlpacaEval 2.0) — generalization untested.** All 223 models are from the AlpacaEval 2.0 leaderboard, predominantly 2023–2024 era instruction-tuned models evaluated on 805 instruction-following prompts. The findings may not generalize to: other evaluation frameworks (MT-Bench, MMLU, Chatbot Arena), specialized task types (code, mathematics), or post-2024 frontier models where capability-verbosity dynamics may differ. Cross-benchmark replication is the immediate priority for future work.

**L3: win_rate is an imperfect capability proxy.** Win_rate reflects human pairwise preference against a GPT-4o reference, conflating true cognitive capability with response style, format preferences, and annotator biases. Our claims should be interpreted as: "human preference win_rate independently predicts LC_winrate beyond verbosity," not making strong claims about underlying model cognitive capability.

**L4: Mild heteroscedasticity in OLS.** Breusch-Pagan p = 0.011 indicates mild non-constant variance in OLS residuals. This does not affect coefficient estimates (which are BLUE-unbiased under OLS assumptions with heteroscedasticity) but may slightly inflate standard errors. Given p_win = 4.58e-145, the significance would survive even substantial standard error inflation.

**L5: Δ-monotonicity not confirmed.** The original hypothesis anticipated strict monotonic ordering of Δ across capability quartiles; this was not confirmed. The LC_winrate-based analysis (H-C1) provides strong evidence for the overall capability-LC relationship; Δ is better treated as an exploratory secondary finding.

## 6.4 Broader Impact

This work validates a widely used evaluation infrastructure decision: the use of LC_winrate as a capability-ordering metric in LLM evaluation. Positive impacts include: more confident use of LC-based rankings in capability comparisons; the FWL verification methodology as a replicable template for confound control in evaluation studies; and a principled framework for thinking about when Δ vs LC_winrate should be the dependent variable.

Potential negative impacts are limited but worth noting: strong evidence that LC_winrate and win_rate agree on capability ordering could reduce incentive to develop more fundamentally different evaluation paradigms. We emphasize that our findings apply to the current model landscape and evaluation framework; continued evaluation diversity research remains important.

No personal data was used; all analyses are on publicly available aggregated leaderboard scores. No discriminatory or harmful applications of the findings are apparent.
