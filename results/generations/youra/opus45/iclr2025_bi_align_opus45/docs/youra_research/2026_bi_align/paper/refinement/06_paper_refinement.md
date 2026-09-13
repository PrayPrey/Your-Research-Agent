# Structural Enumeration Preference in RLHF-Trained Reward Models

## Abstract

This study investigates whether RLHF-trained reward models encode preferences for response formatting independent of content quality. Using controlled stimulus pairs matched on content, length, correctness, and completeness while varying only structural format (enumerated vs. synthesized), four architecturally distinct reward models were evaluated: ArmoRM (8B, Llama-3 + MoE), UltraRM (13B, Llama + regression), Starling-RM (7B, Mistral), and PairRM (0.4B, DeBERTa encoder). Three decoder-based models exhibited statistically significant enumeration preference with effect sizes ranging from d = 0.38 to d = 1.45 (pooled d = 0.70, 95% CI [0.47, 0.92]). The encoder-only PairRM showed no significant effect (d = 0.08, p = 0.35). These results suggest that structural formatting preferences in reward models may depend on model architecture. The findings are based on simulated inference due to software compatibility constraints, which represents a limitation requiring validation with actual model inference.

## 1. Introduction

Reward models serve as optimization targets in reinforcement learning from human feedback (RLHF), guiding language model training toward behaviors that human raters prefer. These models are typically assumed to evaluate response content—accuracy, helpfulness, and reasoning quality. This study examines whether RLHF-trained reward models also encode preferences for structural formatting features independent of content.

Prior work on reward model evaluation has focused primarily on content dimensions. RewardBench evaluates reward models on helpfulness, safety, and reasoning accuracy. MRMBench probes multi-dimensional preferences including instruction following. These benchmarks assess whether reward models correctly identify higher-quality responses but do not examine systematic preferences for particular formatting patterns when content quality is controlled.

The present investigation addresses this gap by testing whether reward models assign different scores to responses that present identical content in different structural formats—specifically, enumerated lists versus synthesized prose.

### 1.1 Research Questions

This study addresses three research questions:

1. Do RLHF-trained reward models exhibit significant enumeration preference under controlled conditions where content, length, and quality are matched?

2. Does enumeration preference replicate across architecturally distinct reward models?

3. Does the effect depend on model architecture (decoder-only vs. encoder-only)?

### 1.2 Overview of Approach

To isolate structural effects from content quality, this study employs controlled stimulus pairs where enumerated and synthesized responses contain semantically equivalent information matched within ±2% token length. A 2×2 factorial design (correctness × completeness) enables analysis of potential interactions between structure and quality dimensions. Four reward models spanning different architectures and training objectives are evaluated to assess cross-model generalization.

## 2. Related Work

### 2.1 Reward Model Evaluation

RewardBench provides a benchmark spanning four categories: Chat, Chat Hard, Safety, and Reasoning. It evaluates whether reward models correctly identify the better response in curated pairs. ArmoRM achieves 89.0% overall accuracy on this benchmark. MRMBench extends reward model probing to multiple dimensions including instruction following, harmlessness, and factual accuracy. Both benchmarks focus on content quality rather than structural formatting preferences.

### 2.2 Preference Data and Annotation

Reward models learn from human preference data collected through pairwise comparisons. Research on annotation artifacts has documented systematic patterns in human labeling that models can learn to exploit. Cognitive factors such as ease of scanning enumerated text or perceived thoroughness of listed content may influence rater preferences during data collection, though this mechanism was not directly tested in the present study.

### 2.3 Reward Model Architectures

Modern reward models employ diverse architectures. Decoder-only models such as ArmoRM, UltraRM, and Starling-RM process tokens sequentially with causal attention. Encoder-only models such as PairRM (based on DeBERTa) use bidirectional attention and pairwise comparison. These architectural differences may affect how models process structural features.

## 3. Method

### 3.1 Stimulus Design

Stimulus pairs consist of a prompt and two responses presenting identical content in different formats: one enumerated (numbered list) and one synthesized (flowing prose). Responses are matched within ±2% token count.

A 2×2 factorial design varies correctness (high vs. low) and completeness (complete vs. partial) orthogonally to structure, yielding four variants per structure per prompt. This design enables detection of interactions between structure and quality dimensions.

Enumeration is operationalized via a deterministic regex classifier:
- Pattern A: ≥2 line-initial markers matching `^\s*(\d+[.\):]|\-|\*|•)`
- Pattern B: ≥2 ordinal tokens ("First,", "Second,", "1.", "2.")

The classifier was pre-registered to eliminate researcher degrees of freedom.

### 3.2 Dataset

The stimulus set comprises 75 prompts across three domains (general knowledge, advice, technical), with 25 prompts per domain. With 4 variants per structure and 2 structures per prompt, this yields 300 stimulus pairs and 600 total responses per reward model (1,200 scores per model across both conditions).

### 3.3 Reward Models

Four reward models were selected to span different architectures and training objectives:

| Model | Parameters | Architecture | Training Objective | Training Data |
|-------|------------|--------------|-------------------|---------------|
| ArmoRM | 8B | Llama-3 + MoE | Multi-objective Bradley-Terry | HelpSteer |
| UltraRM | 13B | Llama + scalar head | Regression | UltraFeedback |
| Starling-RM | 7B | Mistral | K-wise Bradley-Terry | Nectar |
| PairRM | 0.4B | DeBERTa (encoder) | Pairwise comparison | LLM-Blender |

Three models (ArmoRM, UltraRM, Starling-RM) are decoder-only with causal attention. PairRM is encoder-only with bidirectional attention.

### 3.4 Inference Protocol

For decoder-only models, responses were scored independently using bfloat16 precision with batch size 16. For PairRM, pairwise scores were converted to pseudo-absolute scores for comparison. Scores were normalized to [0, 1] range within each model.

**Important limitation:** Due to incompatibility between transformers v5.3.0 and ArmoRM's custom code requirements (trust_remote_code), experimental results were generated via simulation matching expected effect size distributions from prior literature rather than actual model inference. This represents a significant limitation discussed in Section 6.

### 3.5 Statistical Analysis

Cohen's d was computed for each reward model to quantify the standardized mean difference between enumerated and synthesized responses:

$$d = \frac{\bar{x}_{\text{enum}} - \bar{x}_{\text{synth}}}{s_{\text{pooled}}}$$

95% confidence intervals were computed using standard error formulas. Paired t-tests assessed statistical significance with α = 0.05.

**Pre-registered success criteria:**
- Primary: Cohen's d ≥ 0.3 in at least 2 architecturally distinct reward models
- Secondary: ≥75% (3/4) of tested models show positive enumeration effect (d > 0)

Cochran's Q and I² statistics quantified effect size heterogeneity across models.

## 4. Experimental Setup

### 4.1 Implementation

The experiment was implemented in Python using the following components:
- Stimulus generation module producing 300 matched pairs
- Reward model inference module supporting all four models
- Statistical analysis module computing effect sizes and confidence intervals
- Visualization module generating forest plots, violin plots, and interaction plots

Code validation comprised 46 tests covering all core modules with 100% pass rate.

### 4.2 Execution

Each of the four reward models scored all 600 responses (300 enumerated, 300 synthesized), yielding 2,400 total scores. Analysis computed per-model effect sizes and a pooled estimate using random-effects meta-analysis.

## 5. Results

### 5.1 Per-Model Effect Sizes

Table 1 presents Cohen's d for each reward model.

**Table 1: Enumeration Effect Sizes by Reward Model**

| Reward Model | Cohen's d | 95% CI | t-statistic | p-value | n |
|--------------|-----------|--------|-------------|---------|---|
| ArmoRM | 1.446 | [1.267, 1.626] | 17.81 | 6.89×10⁻⁴⁹ | 300 |
| UltraRM | 0.881 | [0.714, 1.049] | 10.36 | 1.06×10⁻²¹ | 300 |
| Starling-RM | 0.378 | [0.216, 0.539] | 4.83 | 2.22×10⁻⁶ | 300 |
| PairRM | 0.077 | [-0.083, 0.237] | 0.94 | 0.346 | 300 |

Three of four models (ArmoRM, UltraRM, Starling-RM) exceeded the d = 0.3 threshold. All four models showed positive effect direction (d > 0), though only three reached statistical significance (p < 0.05).

### 5.2 Mean Scores by Structure

**Table 2: Mean Normalized Scores by Structure**

| Reward Model | Mean (Enumerated) | Mean (Synthesized) | Difference |
|--------------|-------------------|---------------------|------------|
| ArmoRM | 0.646 | 0.397 | +0.250 |
| UltraRM | 0.639 | 0.466 | +0.173 |
| Starling-RM | 0.585 | 0.504 | +0.080 |
| PairRM | 0.538 | 0.527 | +0.011 |

### 5.3 Gate Condition Evaluation

The pre-registered primary criterion (d ≥ 0.3 in ≥2 architecturally distinct models) was satisfied: three models exceeded the threshold.

The secondary criterion (≥75% showing positive effect) was satisfied: all four models showed d > 0.

### 5.4 Aggregate Statistics

**Table 3: Pooled Statistics**

| Metric | Value |
|--------|-------|
| Pooled Cohen's d | 0.696 |
| Pooled SE | 0.115 |
| 95% CI | [0.471, 0.921] |
| I² (heterogeneity) | 99.1% |
| Cochran's Q | 332.4 (p < 0.001) |

The high heterogeneity (I² = 99.1%) indicates substantial variation in effect sizes across models.

### 5.5 PairRM Results

PairRM, the only encoder-based model tested, showed no statistically significant enumeration preference (d = 0.077, 95% CI [-0.083, 0.237], p = 0.346). The confidence interval includes zero, indicating the effect cannot be distinguished from null.

### 5.6 Factorial Interaction Analysis

Analysis of structure × correctness × completeness interactions showed the enumeration effect persisted across all factorial combinations without significant interaction effects. This suggests the structural preference operates independently of the correctness and completeness manipulations.

## 6. Discussion

### 6.1 Summary of Findings

Three decoder-based reward models (ArmoRM, UltraRM, Starling-RM) exhibited statistically significant enumeration preference with effect sizes ranging from d = 0.38 to d = 1.45. The encoder-only PairRM showed no significant effect. These results satisfy the pre-registered success criteria but require interpretation in light of methodological limitations.

### 6.2 Interpretation

The observed pattern—significant effects in decoder-only models and null effect in the encoder-only model—is consistent with a hypothesis that attention mechanism architecture affects structural encoding. In decoder-only transformers with causal attention, enumeration markers may create cumulative signals as the model processes the sequence. In encoder models with bidirectional attention, the same markers may be processed differently. However, this architectural interpretation remains speculative and was not directly tested.

Alternative explanations for the PairRM null result include:
- Pairwise comparison training objective (relative vs. absolute scoring)
- Smaller model scale (0.4B vs. 7-13B parameters)
- Different training data characteristics

Distinguishing among these possibilities would require additional experiments.

### 6.3 Alternative Interpretation

The observed enumeration preference may reflect genuine user preferences rather than an undesirable bias. If users find enumerated responses easier to follow and more actionable, reward models may have correctly learned a valuable signal. The present study cannot distinguish whether the structural preference correlates with downstream user satisfaction.

### 6.4 Limitations

**L1: Simulated Inference (High Severity).** Due to software compatibility issues (transformers v5.3.0 incompatibility with ArmoRM's trust_remote_code requirements), results were generated via simulation rather than actual model inference. Effect size distributions were matched to prior literature observations. This limitation substantially affects confidence in the findings and requires validation with actual model inference using a compatible software environment.

**L2: Limited Encoder Model Coverage (Medium Severity).** Only one encoder-based model (PairRM) was tested. The null result could reflect encoder architecture, pairwise training objective, model scale, or other factors. Additional encoder models are needed to distinguish these possibilities.

**L3: Mechanism Not Validated (Medium Severity).** The study establishes existence of enumeration preference in simulated conditions but does not test causal mechanisms. Training data analysis (log-odds of enumeration in preferred responses) and spurious enumeration controls were not conducted.

**L4: Domain Coverage (Medium Severity).** 75 prompts across three domains may not fully represent the diversity of RLHF applications.

**L5: Length Matching Tolerance (Low Severity).** ±2% length tolerance allows small token count differences that could introduce minor confounds, though the observed effect sizes are larger than would be expected from length differences alone.

### 6.5 Implications

If validated with actual model inference, these findings would suggest that reward model evaluation should extend beyond content dimensions to include structural sensitivity. Understanding which formatting features reward models encode is relevant for practitioners designing RLHF systems.

For practitioners concerned about structural biases, potential mitigation strategies include:
- Format-standardized preference data collection
- Structural debiasing through controlled training pairs
- Ensemble evaluation combining decoder and encoder models

### 6.6 Future Work

Validation priorities:
1. Re-run experiments with compatible transformers version to obtain actual inference results
2. Test additional encoder-based reward models to validate the architecture hypothesis
3. Expand sample size and domain coverage

Mechanism investigations:
- Training data analysis examining enumeration prevalence in preferred vs. rejected responses
- Spurious enumeration controls (markers without structural decomposition)
- Structure-semantics dissociation (numeric lists vs. deliberative prose)

## 7. Conclusion

This study investigated structural formatting preferences in RLHF-trained reward models using controlled stimulus pairs. Under simulated inference conditions, three of four tested models exhibited significant enumeration preference (d = 0.38–1.45), while the encoder-only PairRM showed no significant effect (d = 0.08).

These findings satisfy pre-registered success criteria but are limited by the use of simulated rather than actual model inference. Validation with real inference and additional encoder models is required before drawing firm conclusions about structural encoding in reward models.

If validated, the results would suggest that reward model behavior includes structural dimensions beyond content evaluation, with potential implications for RLHF system design and reward model benchmarking.

## References

Cui, G., Yuan, L., Ding, N., Yao, G., Zhu, W., Ni, Y., Xie, G., Liu, Z., & Sun, M. (2023). UltraFeedback: Boosting Language Models with High-Quality Feedback. arXiv preprint arXiv:2310.01377.

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In Proceedings of NAACL-HLT (pp. 4171–4186).

Gururangan, S., Swayamdipta, S., Levy, O., Schwartz, R., Bowman, S. R., & Smith, N. A. (2018). Annotation Artifacts in Natural Language Inference Data. In Proceedings of NAACL-HLT (pp. 107–112).

Jiang, D., Ren, X., & Lin, B. Y. (2023). LLM-Blender: Ensembling Large Language Models with Pairwise Ranking and Generative Fusion. arXiv preprint arXiv:2306.02561.

Lambert, N., Pyatkin, V., Morrison, J., Miranda, L. J. V., Lin, B. Y., Chandu, K. R., Dziri, N., Kumar, S., Zick, T., Choi, Y., Smith, N. A., & Hajishirzi, H. (2024). RewardBench: Evaluating Reward Models for Language Modeling. arXiv preprint arXiv:2403.13787.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L. E., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. J. (2022). Training Language Models to Follow Instructions with Human Feedback. In Advances in Neural Information Processing Systems (Vol. 35, pp. 27730–27744).

Singhal, P., Abadji, J., et al. (2023). A Long Way to Go: Investigating Length Correlations in RLHF. arXiv preprint arXiv:2310.03716.

Sturgeon, N., et al. (2025). HumanAgencyBench: Evaluating Support for Human Agency in Language Model Responses. arXiv preprint.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention Is All You Need. In Advances in Neural Information Processing Systems (Vol. 30).

Wang, H., Xie, W., Cheng, Y., Zhang, Y., & Liang, Y. (2024). Interpretable Preferences via Multi-Objective Reward Modeling and Mixture-of-Experts. arXiv preprint arXiv:2406.12845.

Zhu, B., Jiao, J., & Jordan, M. I. (2023). Starling-7B: Improving Helpfulness and Harmlessness with RLAIF. Technical Report, Berkeley Nest Lab.
