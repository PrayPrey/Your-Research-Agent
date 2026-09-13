# 2. Related Work

## 2.1 Verbosity Bias and Length-Controlled Evaluation

The problem of length bias in LLM-based evaluation is well-documented. Zheng et al. [2023] show that GPT-4 as a pairwise judge prefers longer, more structured responses even when content quality is equal. Wang et al. [2023] corroborate this finding across multiple judge models, observing consistent preferences for formatting features such as markdown headers and bullet points. Shi et al. [2024] extend this to reward models, finding that RLHF reward models exhibit similar verbosity preferences.

Dubois et al. [2024] respond to this critique with AlpacaEval 2.0's length-controlled win rate (LC_winrate). Their GLM-based approach regresses response length out of the pairwise comparison outcomes, yielding a debiased preference score. They report a bivariate Spearman correlation of ρ ≈ 0.94 between win_rate and LC_winrate, and show that LC_winrate correlates more strongly with Chatbot Arena (ρ ≈ 0.98) than raw win_rate. Our work extends this finding: we move from bivariate to partial correlation, controlling for verbosity (avg_length), and find that the capability-LC alignment strengthens to 0.985 when verbosity is properly held constant.

Hu et al. [2024] provide a mechanistic decomposition of win_rate into a desirability component (length-independent quality) and an information mass component (length-dependent content quantity). Their framework predicts that the desirability channel should survive LC correction, consistent with our finding that β_win dominates β_len in standardized regression. Our population-scale evidence (N=223) empirically confirms their theoretical decomposition.

## 2.2 Bidirectional Human-AI Alignment

Shen et al. [2024] provide a systematic review of bidirectional alignment between humans and AI systems, identifying a gap in empirical quantification of capability-modulated alignment asymmetry. Ji et al. [2023] survey alignment approaches more broadly, noting that evaluation metric consistency across human and AI evaluators is an open problem. Our work directly addresses the empirical gap identified by Shen et al.: we quantify, at population scale, how strongly capability modulates the alignment between human preference (win_rate) and AI-debiased preference (LC_winrate).

The concept of alignment gap Δ = LC_winrate − win_rate operationalizes this asymmetry as a per-model scalar. Negative Δ indicates the AI evaluator rates a model lower than humans do; positive Δ indicates the opposite. While Dubois et al. [2024] introduce this gap implicitly, they do not analyze it as a capability-dependent variable. We show that Δ varies significantly across capability quartiles (KW p = 5.97e-05, ε² = 0.088), though the effect is medium-sized and non-monotonic — a nuance that distinguishes our findings from the simpler capability-monotonicity story.

## 2.3 LLM Evaluation Reliability and Cross-Metric Agreement

Li et al. [2024] demonstrate that LLMs of similar capability converge in their pairwise preference judgments, explaining why evaluation metrics track capability. Singhal et al. [2023] show that RLHF amplifies length differently depending on model capability, predicting that capability-verbosity interactions should be visible in evaluation data — consistent with our VIF = 1.764 (moderate but separable collinearity between win_rate and avg_length).

Existing work on evaluation reliability generally uses bivariate agreement metrics. Our contribution is the application of partial correlation and standardized regression — standard econometric tools for confound control — to LLM evaluation data. The Frisch-Waugh-Lovell theorem [Frisch and Waugh, 1933; Lovell, 1963], which guarantees that residualization-then-correlation converges to partial correlation under linear assumptions, has not been previously applied as a robustness check in LLM evaluation studies. We show that the delta between the two estimators is 0.011, well within the expected Spearman approximation error.

## 2.4 Positioning

Our work differs from prior studies in three ways: (1) we study the *partial* relationship between capability and LC preference (not bivariate), explicitly controlling for verbosity; (2) we provide a FWL-based methodological robustness check that is new to this literature; and (3) we analyze both LC_winrate and Δ as dependent variables, providing a comparative effect-size lesson that has implications for future evaluation study design. We complement, rather than contradict, the AlpacaEval 2.0 evaluation methodology: our results validate the LC correction as a capability-preserving transformation.
