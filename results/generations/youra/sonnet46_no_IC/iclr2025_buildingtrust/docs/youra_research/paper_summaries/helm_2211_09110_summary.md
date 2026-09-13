# Holistic Evaluation of Language Models (HELM)

## Key Metadata
- **Authors:** Percy Liang et al. (Stanford CRFM)
- **Year:** 2023
- **Venue:** NeurIPS 2023 Datasets & Benchmarks
- **Core Contribution:** Multi-metric, multi-scenario framework evaluating 30 LLMs across 16 scenarios and 7 metric categories with a living leaderboard.

## Section Summaries

### Abstract
We present Holistic Evaluation of Language Models (HELM), a living benchmark that evaluates 30 language models across 16 core scenarios and 7 metric categories (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency). Our goal is to prioritize transparency and identify tradeoffs between metrics. Key finding: "There are important trade-offs across metrics" — no model excels on all metrics simultaneously.

### Introduction & Motivation
Prior LLM evaluation focuses on a single metric per benchmark, making it impossible to understand tradeoffs between desiderata. HELM addresses this by simultaneously measuring all major evaluation dimensions for every model. The key insight is that responsible deployment requires understanding the full profile of model behavior, not just peak performance on a single task.

### Methodology
HELM evaluates 30 LLMs (GPT-3.5, Codex, T0, BLOOM, OPT, TNLGv2, Gopher, Chinchilla, Jurassic, LLaMA variants, etc.) across: 16 scenarios (NLP tasks × domains), 7 metric categories: (1) Accuracy (EM, F1, accuracy), (2) Calibration (ECE), (3) Robustness (performance under input perturbation), (4) Fairness (demographic parity across groups), (5) Bias (Winogender, BBQ), (6) Toxicity (Perspective API), (7) Efficiency (tokens/second). For each model × scenario × metric, a scalar score is computed. Aggregate rankings across metrics reveal the tradeoff structure. The paper explicitly notes these tradeoffs in Section 5 ("Holistic evaluation reveals important tradeoffs") but presents them as radar charts, not Spearman correlation matrices.

### Experiments & Results
30 models × 16 scenarios × 7 metrics = comprehensive evaluation matrix. Key results: (1) GPT-3.5 leads on accuracy but not robustness; (2) Models with high fairness scores (due to refusal behavior) show lower accuracy — fairness-accuracy tension; (3) Calibration and accuracy positively correlated but robustness and accuracy are not; (4) Toxicity and accuracy appear nearly independent; (5) Radar chart analysis in Figure 5 shows model-specific tradeoff profiles; (6) Spearman correlation between metric categories NOT reported; (7) Epoch AI reanalysis (2023) computes median ρ=0.73 across HELM benchmarks but for capability benchmarks only, not the 7 metric categories.

### Discussion & Conclusion
HELM establishes that holistic evaluation is necessary and reveals qualitative tradeoffs. Key limitation acknowledged: the paper presents "important tradeoffs" but does not quantify the correlation structure between its 7 metric categories. The data to compute such correlations exists in the public leaderboard (stanford-crfm/helm).

## Key Contributions
- Living benchmark with 30 LLMs × 16 scenarios × 7 metrics
- Identifies qualitative accuracy-robustness and fairness-accuracy tradeoffs
- Open leaderboard data enables downstream correlation analysis

## Potential Relevance
HELM provides a second data source (complementary to TrustLLM) for Gap 1 correlation analysis. Its 7 metric categories (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) map onto trustworthiness dimensions differently than TrustLLM's 6 dimensions, enabling cross-framework validation of any correlation structure found. The 30-model coverage (more than TrustLLM's 16) increases statistical power for Spearman correlation estimation.
