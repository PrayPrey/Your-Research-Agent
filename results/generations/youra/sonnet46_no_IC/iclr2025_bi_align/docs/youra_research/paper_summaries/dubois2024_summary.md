# Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators

## Key Metadata
- **Authors:** Yann Dubois, Balázs Galambosi, Percy Liang, Tatsunori Hashimoto
- **Year:** 2024
- **Venue:** arXiv (2404.04475); citations: 889
- **Core Contribution:** Introduces length-controlled win rate (LC_winrate) via GLM regression to debias LLM-as-judge evaluators from verbosity bias, and provides the AlpacaEval 2.0 leaderboard (N=222 models) with both win_rate and length_controlled_winrate columns.

## Section Summaries

### Abstract
Automatic evaluators based on LLMs (like GPT-4) are biased toward longer outputs, leading to inflated win rates for verbose models. We propose Length-Controlled (LC) AlpacaEval which adjusts win rates using a GLM regression, regressing out the effect of response length. LC win rate increases Spearman correlation with LMSYS Chatbot Arena from 0.94 to 0.98, indicating it better reflects human preferences. The AlpacaEval 2.0 leaderboard provides per-model win_rate, length_controlled_winrate, and avg_length columns for N=222 models.

### Introduction & Motivation
LLM-as-judge systems (GPT-4 judging model outputs) systematically prefer longer responses even when they are not qualitatively better. This verbosity bias inflates raw win rates for models that generate longer outputs. The gap between raw win_rate and LC win rate (Δ = LC_winrate − win_rate) operationalizes the per-model verbosity-induced bias. High-verbosity models show large negative Δ (LC penalizes their length inflated scores); lower-verbosity models show smaller |Δ|.

### Methodology
The core method fits a Generalized Linear Model (GLM) logistic regression predicting human preference from: (1) response quality features and (2) response length (avg_length). The length coefficient is then removed from the logistic model to produce length-controlled win probabilities. This produces per-model LC_winrate that is orthogonalized against avg_length. Implementation: GLM with controlled features from the AlpacaEval dataset; the leaderboard CSV stores both win_rate (raw human preference fraction) and length_controlled_winrate (length-debiased) for each of 222 models. Δ = length_controlled_winrate − win_rate is computable directly. Mean Δ across all models: approximately −16 percentage points (confirmed in h-m1 pipeline).

### Experiments & Results
Leaderboard: N=222 models from AlpacaEval 2.0 (GPT-4-turbo annotator). Spearman correlation with Chatbot Arena ELO increases from ρ=0.94 (raw win_rate) to ρ=0.98 (LC win rate), demonstrating that length debiasing recovers human preference signal. Models with high avg_length (verbose) show substantially lower LC win rate than raw win rate (negative Δ). Some models show Δ exceeding −30 percentage points. The population-level gap (mean Δ ≈ −16pp) is robust across the leaderboard.

### Discussion & Conclusion
LC AlpacaEval provides a simple, computationally cheap method to debias LLM-as-judge evaluations. Limitations: the GLM approach assumes linear length effect; extreme outliers may have different mechanisms. Future work: adaptive approaches (AdapAlpaca) explore non-linear debiasing.

## Key Contributions
- AlpacaEval 2.0 leaderboard with N=222 models and win_rate, length_controlled_winrate, avg_length columns
- GLM-based length debiasing method for automatic evaluators
- Empirical evidence that LC win rate better correlates with human preferences (Arena ELO)

## Potential Relevance
The AlpacaEval 2.0 CSV is the PRIMARY data source for testing whether model capability (win_rate) predicts bidirectional alignment asymmetry (Δ = LC_winrate − win_rate). All three required columns (win_rate, length_controlled_winrate, avg_length) are confirmed accessible. The h-m1 pipeline already established mean(Δ) ≈ −16pp — this paper is the foundational reference for interpreting Δ as a proxy for human vs. GPT-4 LC annotator divergence.
