# TrustLLM: Trustworthiness in Large Language Models

## Key Metadata
- **Authors:** Lichao Sun et al.
- **Year:** 2024
- **Venue:** ICML 2024
- **Core Contribution:** First comprehensive 6-dimensional trustworthiness benchmark evaluating 16 LLMs across truthfulness, safety, fairness, robustness, privacy, and machine ethics.

## Section Summaries

### Abstract
We present TrustLLM, a comprehensive study of trustworthiness in large language models (LLMs), which comprises a set of principles for trustworthy LLMs and a benchmark with over 30 datasets across 8 dimensions (including 6 measurable): truthfulness, safety, fairness, robustness, privacy, and machine ethics. We evaluate 16 mainstream LLMs including GPT-4, Claude-2, LLaMA-2-70B, and others. Key finding: trustworthiness and utility show a complex relationship — models with high utility do not necessarily achieve high trustworthiness.

### Introduction & Motivation
Existing LLM evaluations focus predominantly on capability benchmarks (MMLU, HumanEval, GSM8K) while trustworthiness is studied fragmentarily across isolated dimensions. TrustLLM addresses this by providing a unified benchmark that evaluates multiple trustworthiness dimensions simultaneously for the same models. The central motivation is that LLMs deployed in high-stakes settings must be both capable AND trustworthy, but these two properties may trade off in complex ways that are unmeasured.

### Methodology
TrustLLM constructs a hierarchical evaluation framework: 6 measurable dimensions (truthfulness, safety, fairness, robustness, privacy, machine ethics), each decomposed into 2-5 sub-categories, totaling 30+ datasets. For each model × benchmark pair, a scalar score is computed representing dimension-specific performance. Truthfulness uses TruthfulQA + HaluEval; Safety uses AdvBench + HarmBench-subset; Fairness uses BBQ + WinoBias + StereoSet; Robustness uses AdvGLUE + TextFooler perturbations; Privacy uses privacy-sensitive completion prompts; Machine Ethics uses ETHICS + MoralBench. Scores are normalized to [0,1]. Models evaluated: GPT-4, GPT-3.5-Turbo, Claude-2, Claude-Instant, LLaMA-2 (7B/13B/70B), LLaMA-2-Chat (7B/13B/70B), Vicuna (7B/13B), Mistral-7B, Falcon-7B. Evaluation is in-context, no fine-tuning. Key formula: dimension_score_m = mean(sub-category_scores_m) for model m.

### Experiments & Results
16 LLMs evaluated. Key results: (1) GPT-4 leads on most dimensions but has notably lower robustness than expected; (2) Proprietary models (GPT-4, Claude-2) significantly outperform open-source on safety (safety score gap: ~0.3); (3) LLaMA-2-Chat improves over LLaMA-2-base on safety but degrades on robustness — clear safety-robustness tradeoff within family; (4) Leaderboard published but pairwise Spearman correlation matrix between dimensions NOT computed; (5) Truthfulness-utility correlation noted qualitatively but not quantified as ρ; (6) Higher safety scores correlate with higher refusal rates, which degrades utility scores (utility-safety tension).

### Discussion & Conclusion
TrustLLM establishes that trustworthiness is multi-dimensional and cannot be reduced to a single score. The paper notes that "trustworthiness and utility often trade off" but does not formalize this as a cross-dimension correlation analysis. Key limitation: no statistical test of whether dimension scores are independent or correlated across models.

## Key Contributions
- First 6-dimension trustworthiness benchmark covering 16 LLMs simultaneously
- Identifies qualitative trustworthiness-utility tradeoff
- Provides open-source evaluation toolkit (HowieHwong/TrustLLM, 628★)

## Potential Relevance
TrustLLM provides exactly the cross-model, cross-dimension score matrix needed for Gap 1 analysis. The 16 LLM × 6 dimension score table is the input data for computing a Spearman correlation matrix. The absent analysis (cross-dimension ρ) is precisely what Gap 1 proposes to compute. The LLaMA-2 safety-robustness within-family pattern is a concrete example of the tradeoff Gap 1 aims to generalize across all 6 dimensions.
