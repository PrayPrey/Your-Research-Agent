# 6. Discussion

## 6.1 Interpreting the 53% Scale Confound

The primary finding — that MMLU scale control reduces the TruthfulQA × BBQ correlation by 53% — should be interpreted carefully. It does not mean that factuality and bias avoidance are unrelated; the residual partial correlation (0.343, p = 1.40 × 10⁻⁹) is positive and highly significant. It means that the raw leaderboard correlation dramatically overstates the alignment-specific relationship: the impression of coherence one gets from comparing models on TruthfulQA and BBQ simultaneously is more than half scale artifact.

What drives this? Models scoring high on MMLU are typically larger, more capable models trained on more data. Such models tend to answer more factual questions correctly (boosting TruthfulQA) and make fewer reasoning errors in bias-sensitive contexts (boosting BBQ), not necessarily because their alignment training is coherent, but because capability scales with both. This is the classic confounding structure: a common cause (scale) induces positive correlation between two effects (alignment benchmark scores), even when the direct relationship between those effects is weaker.

The implication for leaderboard interpretation is direct: a model family that improves TruthfulQA and BBQ together may simply be scaling up. Attributing such correlated improvement to aligned training objectives requires, at minimum, controlling for MMLU or an equivalent capability proxy.

## 6.2 The Residual Coupling: What Does 0.343 Mean?

After MMLU control, partial_rho = 0.343 [0.180, 0.492] remains strongly significant. Three competing explanations deserve consideration:

**(1) Genuine RLHF co-training effect.** If RLHF and safety-focused fine-tuning jointly improve factuality and bias avoidance, cross-model variation in training intensity would induce residual coupling. This is consistent with within-model results from Touvron et al. (2023), showing TruthfulQA and BBQ both improving from Llama 2 base to chat. However, our Tier 3 null result (RLHF sign test p = 0.686 on BBQ proxy) provides no cross-model evidence for this mechanism.

**(2) ARC Proxy artifact.** ARC Challenge measures logical reasoning, not social bias. TruthfulQA also has a reasoning component (answering questions that require factual recall and avoiding misleading associations). The partial correlation 0.343 may largely reflect shared reasoning demands between TruthfulQA and ARC, inflating the estimate beyond what genuine factuality × social-bias coupling would show. This is our preferred explanation for the residual magnitude and is the primary motivation for replication with genuine BBQ data.

**(3) Residual family-level clustering.** Within-family variation in training recipes — independent of scale — may drive residual rho even after family-weighted correction. If Llama-family models systematically differ from Falcon-family models on both alignment benchmarks through common fine-tuning choices, this would appear as residual correlation.

Disambiguation requires genuine HELM Lite BBQ per-model accuracy. If partial_rho under real BBQ is substantially lower than 0.343 (say, < 0.20), explanation (2) dominates. If it remains near 0.343, explanations (1) or (3) are more plausible.

## 6.3 Limitations

**L1: BBQ Proxy (ARC Challenge).** The most important limitation is the substitution of ARC Challenge accuracy for genuine HELM Lite BBQ per-model scores. ARC measures logical reasoning; BBQ measures social bias in ambiguous question contexts. These are different constructs. All secondary claims about "factuality-bias coupling" in this paper are qualified by this proxy. The primary claim — that MMLU confounds alignment benchmark correlations, demonstrated by Fisher z p = 3.22 × 10⁻¹² — holds regardless of proxy choice (the Fisher z methodology is valid; what the "bias" dimension actually measures is what changes under different proxies).

**L2: Scenario Classification Underpowered (N=296).** partial_rho = 0.343 with CI [0.180, 0.492] spans the 0.40 structural threshold. Resolving whether the true residual coupling crosses into "scale-free coherence" (scenario b) or remains in the grey zone requires N ≥ 400–600 or genuine BBQ data. The AMBIGUOUS outcome is pre-registered and scientifically valid — it precisely characterizes what can and cannot be concluded from the available data.

**L3: Safety Dimension Excluded (HarmBench N=0).** The three-benchmark partial Spearman matrix (factuality × bias × safety) could not be computed due to zero model overlap between LLM LB v1 and HarmBench Table 2. Safety dimension analysis requires either an alternative safety benchmark with better LLM LB v1 coverage, or a direct download of HarmBench model names with manual name normalization.

**L4: RLHF Sign Test on Proxy.** The null result for RLHF effects on BBQ proxy (p = 0.686) may reflect the proxy's inadequacy rather than a genuine absence of RLHF bias effects. RLHF objectives specifically target HHH (helpful, harmless, honest) responses; ARC reasoning accuracy may not capture the targeted behavior.

**L5: Observational, Cross-Sectional, Open-Weight Only.** This study characterizes population-level correlation structure for approximately 296 open-weight LLMs from the 2022–2024 era. Results do not necessarily generalize to proprietary models (GPT-4, Claude, Gemini), post-2024 RLHF training recipes, or within-model longitudinal dynamics.

## 6.4 Implications for Alignment Evaluation Practice

The Fisher z difference test between raw and partial Spearman correlation should be a standard diagnostic step in alignment benchmark analysis whenever a capability proxy (MMLU, ARC, or similar) co-varies with the benchmarks of interest. The computational cost is negligible: given benchmark scores and a scale proxy, `pingouin.partial_corr` and `scipy.stats` provide all necessary machinery in a few lines of Python.

More broadly, this work supports a methodological recommendation: positive correlations between alignment benchmarks should not be interpreted as evidence of aligned constructs without first checking whether a common scale factor explains the co-movement. The current practice of reporting raw leaderboard correlations may systematically overstate the coherence of alignment training signals.
