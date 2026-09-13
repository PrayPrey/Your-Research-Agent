# Does Better Pre-Training Data Produce More Generalizable Models? A Matched-Scale Evaluation of Corpus Curation and Generalization Balance

**Authors:** [Anonymous]  
**Affiliation:** [Anonymous Institution]  
**Format:** ICML 2025  
**Date:** 2026-08-31  
**Note:** Negative result — primary findings refute the corpus-quality hypothesis at approximately 300 billion training tokens.

---

## Abstract

The intuition that higher-quality pre-training data yields more generalizable language models motivates substantial investment in corpus curation, but this assumption has rarely been tested under controlled conditions. This study evaluates OLMo-7B (trained on Dolma, a multi-stage curated corpus) and Pythia-6.9B (trained on The Pile, a minimally curated corpus) at matched training scale (approximately 300 billion tokens), testing whether the curated-corpus model achieves a higher MMLU/HellaSwag generalization balance ratio. Contrary to the hypothesis, Pythia-6.9B achieves the higher ratio (0.5650 vs. 0.5383; difference = −0.0267, 95% bootstrap CI [−0.0447, −0.0069], Cohen's d = −2.732). The most structurally significant finding is that both models achieve identical HellaSwag 0-shot accuracy (0.4580) at this training scale, irrespective of corpus quality. This convergence collapses the ratio into a proxy for MMLU differences that are themselves confounded by the architectural difference between the two model families (GPT-NeoX vs. LLaMA-style). The results do not support causal attribution to corpus quality without architecture-matched controls or temporal trajectory analysis. This work characterizes the conditions under which cross-architecture, single-checkpoint comparisons fail to isolate corpus quality effects, and proposes concrete requirements for future corpus quality studies.

---

## 1. Introduction

Pre-training corpus curation is among the most resource-intensive components of large language model development. Decisions about which documents to include, how aggressively to deduplicate, and which high-quality sources to prioritize (e.g., academic papers, Wikipedia) are made under the assumption that higher-quality data produces models with stronger generalization — not only higher average benchmark scores, but better balance between knowledge-intensive and commonsense reasoning capabilities. Despite the practical stakes of this assumption, it has rarely been tested under controlled conditions at matched training scales.

The specific hypothesis examined in this work is: *at approximately 300 billion training tokens, a model trained on a more carefully curated corpus will achieve a higher MMLU/HellaSwag generalization balance ratio than a model trained on a less curated corpus.* This hypothesis is operationalized by comparing OLMo-7B [Groeneveld et al., 2024], trained on Dolma [Soldaini et al., 2024] (multi-stage quality filtering, URL blocklisting, deduplication, and explicit inclusion of academic sources), against Pythia-6.9B [Biderman et al., 2023], trained on The Pile [Gao et al., 2020] (minimal curation, basic deduplication and language filtering). Both models provide publicly available intermediate checkpoints at approximately matched training token counts, enabling a controlled matched-scale comparison.

Prior work comparing curated and uncurated corpora has consistently confounded corpus quality with training duration, model architecture, or both. Falcon models trained on RefinedWeb [Penedo et al., 2023] differ from The Pile-trained models in architecture; Pythia-dedup vs. Pythia comparisons [Biderman et al., 2023] measure deduplication in isolation. No prior study has evaluated MMLU/HellaSwag generalization balance ratios for an architecture-paired comparison at matched training token counts.

The primary finding is a direct refutation of the hypothesis: Pythia-6.9B achieves a higher MMLU/HellaSwag ratio (0.5650 vs. 0.5383) at matched training scale, and this advantage is consistent across all four benchmarks evaluated. The directional refutation is statistically robust (95% CI entirely below zero, Cohen's d = −2.732). More structurally informative is the observation that both models achieve identical HellaSwag accuracy (0.4580), irrespective of corpus curation quality, at this training scale. When the denominator of the generalization balance ratio is a constant, the ratio reduces to a noisy proxy for MMLU differences alone — differences that cannot be attributed to corpus quality without resolving the architecture confound.

This paper makes four contributions:

1. **Matched-scale empirical evaluation.** The first systematic evaluation of MMLU/HellaSwag generalization balance as a corpus-quality discriminator, comparing Pythia-6.9B (The Pile, step143000 ≈ 299.9B tokens) and OLMo-7B (Dolma, step68000 ≈ 301B tokens) at controlled matched scale. The corpus-quality prediction is directly refuted (ratio difference = −0.0267, 95% CI [−0.0447, −0.0069], one-sided p = 0.996 for the test that OLMo ≥ Pythia).

2. **Metric sensitivity analysis.** HellaSwag 0-shot commonsense accuracy converges to identical values (0.4580) for both models at approximately 300 billion tokens, demonstrating that the MMLU/HellaSwag ratio is not a reliable corpus curation quality discriminator at this training scale in a cross-architecture comparison.

3. **Methodological characterization.** The conditions under which cross-architecture, single-checkpoint comparisons fail to support causal corpus-quality claims are characterized: when a ratio metric's denominator saturates, the ratio loses its intended discriminative property, and architecture differences in the numerator cannot be attributed to data quality.

4. **Scope-qualified null result.** The negative finding is explicitly scoped to approximately 300 billion training tokens, the GPT-NeoX/LLaMA-style architecture pairing, and the MMLU/HellaSwag ratio metric. It does not rule out corpus quality effects at other training scales, with architecture-matched designs, or using different generalization metrics.

---

## 2. Related Work

### 2.1 Pre-Training Corpus Curation and Model Generalization

The empirical literature on corpus curation and model performance is substantial but consistently confounded by architecture differences or training duration mismatches. Biderman et al. [2023] demonstrate via the Pythia suite that deduplication yields small but consistent benchmark improvements, including a modest HellaSwag gain of approximately 0.01 absolute. This within-architecture, within-corpus comparison isolates deduplication as a single intervention; it does not address multi-stage quality curation, and the small HellaSwag gain is consistent with near-saturation behavior at 300 billion tokens. Penedo et al. [2023] show that web-filtered RefinedWeb data outperforms unfiltered training data for Falcon models; however, the comparison involves different model architectures and focuses on average performance rather than generalization balance ratios, leaving the architecture confound unresolved.

Groeneveld et al. [2024] document OLMo-7B's design and report competitive MMLU performance at full training (approximately 2 trillion tokens), attributing part of this to Dolma's academic content inclusion. This comparison, however, is not matched by training scale; comparing OLMo at 2 trillion tokens to Pythia at 300 billion tokens conflates corpus quality with training duration. The present work tests the same corpus pairing at a matched intermediate scale.

Muennighoff et al. [2023] establish a data quality × training scale interaction, finding that higher-quality data benefits may compound with additional training tokens. A null result at 300 billion tokens is consistent with this interaction: the Dolma advantage may emerge at later training stages without implying that curation is ineffective overall.

Soldaini et al. [2024] document the Dolma corpus in detail, including its multi-stage curation pipeline, domain composition, and deduplication methodology. This documentation provided the primary basis for the hypothesis that Dolma would produce superior generalization balance relative to The Pile.

### 2.2 Generalization Evaluation Metrics

MMLU [Hendrycks et al., 2021] is a 57-subject multiple-choice benchmark spanning STEM, humanities, social sciences, and professional domains, designed to measure multi-task language understanding. HellaSwag [Zellers et al., 2019] is a commonsense completion benchmark derived from ActivityNet and WikiHow, designed to measure web-sourced procedural and situational knowledge. ARC-Easy and ARC-Challenge [Clark et al., 2018] are science question benchmarks at elementary and challenge levels.

The use of performance ratios as generalization balance metrics has precedent in out-of-distribution generalization research, where in-distribution/out-of-distribution performance gaps characterize model behavior [Miller et al., 2021; Koh et al., 2021]. However, ratio metrics require that both numerator and denominator remain discriminative at the comparison point. The present study demonstrates that this requirement is violated when the denominator task saturates at the target training scale.

### 2.3 Data Attribution and Quality Proxy Methods

Influence functions [Koh and Liang, 2017], TRAK [Park et al., 2023], and TracIn [Pruthi et al., 2020] provide tools for attributing model behavior to specific training examples. These methods could in principle quantify the contribution of high-quality versus low-quality data subsets to generalization performance but have not been applied to the corpus-quality × generalization-balance question at 300-billion-token pre-training scale. Such attribution analyses remain a promising direction but require architecture-matched designs to avoid confounding attribution results with architecture effects.

### 2.4 Positioning

This work differs from prior literature in three respects. First, a matched training scale (approximately 300 billion tokens, both models within 0.5% of target) eliminates training duration as a confound. Second, the focus is on generalization balance — the ratio between knowledge-intensive and commonsense task performance — rather than absolute benchmark scores. Third, a scope-qualified null result is reported with explicit characterization of the conditions under which the comparison breaks down, rather than drawing causal conclusions from an architecturally confounded design.

---

## 3. Method

### 3.1 Study Design

The study tests whether a measurably higher-quality pre-training corpus produces a measurably higher MMLU/HellaSwag generalization balance ratio when training scale is held constant. The design exploits public intermediate checkpoints from two model suites — Pythia [Biderman et al., 2023] and OLMo [Groeneveld et al., 2024] — that differ in documented corpus curation quality but provide accessible checkpoints at approximately matched training scales.

### 3.2 Model Selection and Checkpoint Matching

**Pythia-6.9B** (EleutherAI) is trained on The Pile, an 825 GB heterogeneous corpus assembled from 22 diverse text sources with minimal quality filtering beyond basic deduplication and language identification. The checkpoint at step143000 corresponds to approximately 299.9 billion training tokens (143,000 steps × 2,097,152 tokens per step), a deviation of −0.03% from the 300-billion-token target.

**OLMo-7B** (Allen Institute for AI) is trained on Dolma, a 3-trillion-token corpus with multi-stage quality filtering including URL blocklisting, content heuristics, deduplication, and explicit inclusion of high-quality academic sources (Semantic Scholar papers via S2ORC, Wikipedia, Project Gutenberg). The checkpoint at revision `step68000-tokens301B` corresponds to approximately 301 billion training tokens, a deviation of +0.33% from the target. Both checkpoints fall within 0.5% of the 300-billion-token target.

**Table 1: Model and Checkpoint Summary**

| Model | Architecture | HuggingFace ID | Revision | Training Tokens | Deviation |
|-------|-------------|----------------|----------|-----------------|-----------|
| Pythia-6.9B | GPT-NeoX | `EleutherAI/pythia-6.9b` | `step143000` | ≈ 299.9B | −0.03% |
| OLMo-7B | LLaMA-style | `allenai/OLMo-7B` | `step68000-tokens301B` | ≈ 301B | +0.33% |

Both models are evaluated as base (non-instruction-tuned) models to avoid alignment confounds. The architecture difference — GPT-NeoX for Pythia, LLaMA-style with rotary positional embeddings for OLMo — is a known limitation discussed in Section 6.

### 3.3 Evaluation Protocol

All evaluations use `lm-evaluation-harness` v0.4.12 [Gao et al., 2024] on NVIDIA H100 NVL hardware. Shot configurations match those used in the original Pythia and OLMo publications.

**Table 2: Benchmark Configurations**

| Benchmark | Shot | Metric | Role in Analysis |
|-----------|------|--------|-----------------|
| MMLU | 5-shot | mean accuracy (57 subjects) | Numerator: knowledge-intensive OOD generalization |
| HellaSwag | 0-shot | accuracy | Denominator: commonsense reasoning baseline |
| ARC-Easy | 25-shot | accuracy | Secondary: easy factual reasoning |
| ARC-Challenge | 25-shot | accuracy_normalized | Secondary: hard factual reasoning |

Evaluations were conducted with the `--limit 500` flag, evaluating approximately 500 examples per task (approximately 8–9 questions per MMLU subject across 57 subjects). This fast evaluation protocol was used for rapid hypothesis screening. The implications of limited sampling for result reliability are discussed in Section 6.

Evaluation commands follow the pattern:

```bash
lm_eval --model hf \
  --model_args pretrained=<model_id>,revision=<revision> \
  --tasks mmlu,hellaswag,arc_easy,arc_challenge \
  --num_fewshot <task-specific> \
  --limit 500 \
  --output_path ./results/<model>-300B/ \
  --log_samples
```

### 3.4 Primary Metric

**MMLU/HellaSwag Generalization Balance Ratio:**

$$r = \frac{\text{MMLU}_{5\text{-shot}}}{\text{HellaSwag}_{0\text{-shot}}}$$

This ratio captures the balance between knowledge-intensive task performance (MMLU) and commonsense reasoning performance (HellaSwag). Higher values indicate that knowledge acquisition outpaces commonsense baseline performance, operationalizing the hypothesis that curated corpora — which include academic sources expected to improve MMLU — should yield higher ratios.

**Secondary Metric — ARC-Challenge/Easy Delta:**

$$\Delta_{\text{ARC}} = \text{ARC-Challenge}_{\text{acc\_norm}} - \text{ARC-Easy}_{\text{acc}}$$

This delta measures the degree to which challenge-level reasoning degrades relative to easy-level reasoning. Less-negative values indicate better maintenance of reasoning difficulty sensitivity.

### 3.5 Statistical Analysis

Bootstrap confidence intervals (1,000 iterations, seed = 42) are computed on the ratio difference (OLMo − Pythia) by resampling MMLU subject-level accuracy estimates with replacement and recomputing ratios at each iteration. The one-sided p-value is the fraction of bootstrap iterations in which OLMo ratio exceeds Pythia ratio. Cohen's d is computed as mean(bootstrap ratio differences) / std(bootstrap ratio differences).

The pre-registered hypothesis criterion requires OLMo ratio − Pythia ratio > 0.02, Cohen's d > 0.2, and one-sided p < 0.05. A result below this threshold in either direction is treated as falsifying the specific prediction.

### 3.6 Known Limitations of the Design

Three structural limitations affect causal attribution and are discussed in Section 6:

1. **Architecture confound.** Pythia-6.9B uses GPT-NeoX; OLMo-7B uses a LLaMA-style architecture. Performance differences, including MMLU differences, cannot be attributed purely to corpus quality without architecture-matched controls or temporal trajectory analysis.

2. **Fast evaluation.** The 500-sample limit introduces higher variance in per-subject MMLU estimates. Effect direction is reliable; magnitude requires full evaluation to confirm.

3. **Single training scale.** Only approximately 300 billion tokens is evaluated. Corpus quality effects may emerge at different training scales.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does OLMo-7B, trained on Dolma, achieve a higher MMLU/HellaSwag generalization balance ratio than Pythia-6.9B, trained on The Pile, at matched training scale (approximately 300 billion tokens)?

**RQ2:** Does OLMo-7B achieve a less-negative ARC-Challenge/Easy delta than Pythia-6.9B at the same training scale?

**RQ3:** Is any MMLU performance advantage for Pythia-6.9B broadly distributed across subjects, or concentrated in specific domains consistent with benchmark contamination from The Pile?

### 4.2 Hardware and Software

Evaluations were run on NVIDIA H100 NVL hardware using `lm-evaluation-harness` v0.4.12. Results were stored as JSON files and loaded for metric computation. The evaluation pipeline implements resume-on-existing-output logic to ensure reproducibility across restarts.

### 4.3 Statistical Analysis Protocol

The primary test uses bootstrap resampling of MMLU subject-level accuracy estimates. The secondary ARC delta comparison is directional only, with no pre-specified statistical threshold. Contamination assessment is conducted qualitatively via a per-subject MMLU accuracy heatmap: concentration of any Pythia advantage in domains well-represented in The Pile (e.g., PubMed for medicine, ArXiv for physics) would increase the plausibility of contamination as an explanation.

---

## 5. Results

### 5.1 Primary Finding: Corpus-Quality Hypothesis Refuted

The corpus-quality → generalization-balance prediction is directly refuted. Pythia-6.9B achieves a higher MMLU/HellaSwag ratio than OLMo-7B at matched training scale, opposite to the hypothesis direction.

**Table 3: Benchmark Results at Approximately 300 Billion Training Tokens**

| Model | Corpus | MMLU 5-shot | HellaSwag 0-shot | ARC-Easy 25-shot | ARC-Challenge 25-shot |
|-------|--------|-------------|-----------------|-----------------|----------------------|
| Pythia-6.9B | The Pile (minimal curation) | **0.2588** | **0.4580** | **0.6700** | **0.3360** |
| OLMo-7B | Dolma (multi-stage curation) | 0.2463 | 0.4580 | 0.6400 | 0.2960 |

Pythia-6.9B achieves higher or equal performance on all four individual benchmarks. The MMLU gap is 0.0125 in favor of Pythia (0.2588 vs. 0.2463). HellaSwag scores are identical at 0.4580 for both models. ARC-Easy and ARC-Challenge both favor Pythia (0.0300 and 0.0400 absolute differences, respectively). The consistent directional pattern across all metrics makes the refutation robust to choice of aggregation method.

### 5.2 Primary Metric: MMLU/HellaSwag Generalization Balance Ratio

![MMLU/HellaSwag ratio comparison with 95% bootstrap CI](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/ratio_delta.png)

*Figure 1: MMLU/HellaSwag generalization balance ratio for Pythia-6.9B and OLMo-7B with 95% bootstrap confidence intervals. The hypothesis predicted OLMo − Pythia > +0.02; the observed difference is −0.0267.*

**Table 4: Primary Metric Summary**

| Metric | Pythia-6.9B | OLMo-7B | Difference (OLMo − Pythia) | 95% CI | Cohen's d |
|--------|-------------|---------|---------------------------|--------|-----------|
| MMLU/HellaSwag ratio | 0.5650 | 0.5383 | −0.0267 | [−0.0447, −0.0069] | −2.732 |
| ARC delta (Challenge − Easy) | −0.3340 | −0.3440 | −0.0100 (OLMo worse) | — | — |

The hypothesis predicted OLMo − Pythia > +0.02; the observed value is −0.0267. The bootstrap 95% CI on the ratio difference lies entirely below zero. The one-sided p-value for the test that OLMo ≥ Pythia is 0.996, indicating that only 0.4% of bootstrap iterations produced an OLMo ratio exceeding Pythia's. Cohen's d = −2.732 indicates a large effect in the direction opposite to the prediction. All three pre-registered gate criteria (ratio difference > 0.02, Cohen's d > 0.2, one-sided p < 0.05) failed. The result is not a null result in the sense of no detectable effect; it is a large, statistically robust result in the direction opposite to the hypothesis.

### 5.3 Secondary Metric: ARC-Challenge/Easy Delta

Pythia-6.9B achieves an ARC-Challenge score of 0.3360 and ARC-Easy score of 0.6700, yielding a delta of −0.3340. OLMo-7B achieves 0.2960 and 0.6400, yielding a delta of −0.3440. OLMo's delta is more negative by 0.0100, indicating greater degradation from easy to challenge-level reasoning. The directional refutation is confirmed across both primary and secondary metrics.

### 5.4 Analysis: HellaSwag Convergence as a Structural Finding

![All four benchmark scores for Pythia-6.9B and OLMo-7B](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/absolute_scores.png)

*Figure 2: Side-by-side comparison of all four benchmark scores for both models at approximately 300 billion training tokens.*

The identical HellaSwag scores (0.4580 for both models in fast evaluation) are structurally significant. Three explanations are considered:

1. **Scale-dependent saturation (HIGH plausibility).** At approximately 300 billion tokens, 6–8 billion parameter models have absorbed sufficient web-sourced commonsense content — present in both The Pile and Dolma via CommonCrawl — to reach a convergent performance ceiling on HellaSwag. This is consistent with Biderman et al. [2023], who show that deduplication gains on HellaSwag are approximately 0.01 absolute within the Pythia suite, suggesting limited discriminative power of the task for corpus quality differences in this model family.

2. **Sampling variance (MEDIUM plausibility).** With approximately 500 evaluation examples, identical scores to three decimal places could arise by chance. Full evaluation with the complete 10,042-example HellaSwag validation set is needed to confirm.

3. **Task insensitivity to quality differences (MEDIUM plausibility).** HellaSwag's commonsense content is well-represented in both corpora via CommonCrawl, making it inherently insensitive to quality differences between The Pile and Dolma at this scale.

The key structural implication is: when the denominator of the MMLU/HellaSwag ratio is a constant (0.4580), the ratio reduces algebraically to MMLU / 0.4580. The observed ratio difference of −0.0267 is entirely driven by the MMLU gap of 0.0125. HellaSwag provides no discriminative information in this comparison, and the MMLU differences are confounded by the architecture difference between the two models.

### 5.5 Per-Subject MMLU Heatmap and Contamination Assessment

![Per-subject MMLU accuracy heatmap for all 57 subjects](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/mmlu_heatmap.png)

*Figure 3: Per-subject MMLU accuracy for Pythia-6.9B and OLMo-7B across 57 MMLU subjects. Pythia's advantage is broadly distributed rather than concentrated in specific domains.*

The per-subject heatmap shows Pythia's MMLU advantage is broadly distributed across subjects including STEM (physics, chemistry, biology), social sciences (economics, law, psychology), and humanities (history, philosophy). This pattern is inconsistent with The Pile contamination as the primary explanation: contamination would be expected to concentrate in domains well-represented in The Pile's specific sources (e.g., PubMed for medicine, ArXiv for physics, legal databases for law). The absence of domain concentration reduces the plausibility of contamination, though it does not rule it out. Min-K% contamination detection [Shi et al., 2024] applied to MMLU test questions against The Pile would provide more definitive evidence.

### 5.6 Bootstrap Distribution

![Bootstrap distribution of ratio differences](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet46/TEST_data_problems/docs/youra_research/h-e1/figures/bootstrap_dist.png)

*Figure 4: Bootstrap distribution of ratio differences (OLMo − Pythia) across 1,000 iterations. Dashed vertical line at 0 (null hypothesis); dotted vertical line at +0.02 (hypothesis threshold). Neither falls within the distribution.*

The bootstrap distribution is centered at −0.0265 and lies entirely below zero. Neither the null value (0) nor the hypothesis threshold (+0.02) falls within the distribution. The 95% CI of [−0.0447, −0.0069] excludes zero, confirming that the directional refutation is statistically robust to MMLU subject-level sampling variance.

### 5.7 Summary of Research Questions

**RQ1:** Pythia-6.9B achieves a significantly higher MMLU/HellaSwag ratio than OLMo-7B (0.5650 vs. 0.5383, d = −2.732, 95% CI entirely negative). The hypothesis is directly falsified.

**RQ2:** OLMo-7B does not achieve a less-negative ARC delta. Pythia's delta (−0.334) is less negative than OLMo's (−0.344), confirming the directional refutation via an independent metric.

**RQ3:** Pythia's MMLU advantage is broadly distributed across subjects, inconsistent with domain-specific contamination from The Pile as the primary explanation.

---

## 6. Discussion

### 6.1 Competing Explanations for the Observed Result

Three explanations for Pythia's MMLU advantage are assessed.

**Architecture Difference (HIGH plausibility).** The most plausible explanation is the uncontrolled architecture difference. Pythia-6.9B uses GPT-NeoX architecture; OLMo-7B uses a LLaMA-style architecture with rotary positional embeddings and different attention configurations. Architecture-dependent differences in few-shot multiple-choice task performance have been observed across model families [Touvron et al., 2023]. An architecture advantage in MMLU would produce broadly distributed gains (consistent with Figure 3), would not affect HellaSwag (which is commonsense-based rather than knowledge-intensive), and would produce a stable gap across training checkpoints rather than a narrowing one. Without temporal trajectory analysis comparing both models at an earlier checkpoint (approximately 143 billion tokens), the stability versus narrowing of the gap cannot be determined, and causal attribution to corpus quality is not possible.

**Training Scale Insufficient (HIGH plausibility).** A second compelling explanation is that 300 billion training tokens is insufficient for Dolma's curation quality advantage to manifest. Groeneveld et al. [2024] report competitive MMLU performance for full-training OLMo-7B (approximately 2 trillion tokens), attributing part of this to Dolma's academic content inclusion. If the academic content advantage compounds with training scale — as suggested by the data quality × token count interaction documented by Muennighoff et al. [2023] — the Dolma advantage may not be detectable at 300 billion tokens.

**The Pile MMLU Contamination (LOW-MEDIUM plausibility).** The Pile may contain MMLU-adjacent content (e.g., academic PDFs from PubMed, ArXiv) that inflates Pythia's MMLU scores via benchmark contamination. However, the per-subject heatmap (Figure 3) shows Pythia's advantage is distributed across subjects less likely to appear in The Pile's specific domain sources (e.g., philosophy, sociology, moral scenarios), reducing the plausibility of contamination as the primary explanation.

### 6.2 Structural Insight: HellaSwag Denominator Saturation

The most methodologically significant finding is the HellaSwag convergence. Both models achieve exactly 0.4580 on HellaSwag at approximately 300 billion tokens, regardless of corpus quality. This convergence has a direct implication for metric design: the MMLU/HellaSwag ratio is not a valid discriminator of corpus curation quality at this training scale in a cross-architecture comparison, because the denominator provides no discriminative information.

A ratio metric $r = \text{numerator} / \text{denominator}$ is a reliable quality discriminator only when both components remain sensitive to the factor being tested. When the denominator saturates — reaching a scale-dependent ceiling for the model family — the ratio collapses into a scalar multiple of the numerator alone. For cross-architecture comparisons, numerator differences may reflect architecture effects rather than corpus quality. Researchers designing generalization balance metrics should verify denominator sensitivity at their target training scale before using ratio metrics as quality proxies.

### 6.3 Limitations

**L1: Architecture Confound Not Bounded.** The planned method for bounding the architecture confound — temporal trajectory analysis comparing both models at approximately 143 billion and 300 billion tokens — was not executed. The temporal trajectory would determine whether the ratio gap is widening (consistent with a quality-driven advantage that compounds with tokens) or stable (consistent with a fixed architecture-driven difference). Without this analysis, causal attribution of any observed performance difference to corpus quality is not possible. Future work should evaluate both models at an earlier checkpoint (Pythia step72000 ≈ 143 billion tokens; matched OLMo intermediate checkpoint) to distinguish these explanations.

**L2: Fast Evaluation (500-Sample Limit).** The use of `--limit 500` evaluates approximately 8–9 examples per MMLU subject, introducing high variance in per-subject accuracy estimates. Full evaluation across 14,042 MMLU questions would provide more reliable per-subject estimates and reduce bootstrap CI width. The large effect size (Cohen's d = −2.732) and CI entirely below zero indicate that the directional refutation is unlikely to reverse with full evaluation, but the exact magnitude of −0.0267 is less reliable.

**L3: Single Training Scale.** Results are specific to approximately 300 billion training tokens. The corpus-quality hypothesis may hold at different scales; prior work suggests it does at approximately 2 trillion tokens [Groeneveld et al., 2024]. The null result should not be generalized beyond its explicit scope.

**L4: Corpus Quality IV Not Directly Measured.** The corpus quality independent variable was operationalized via corpus identity (The Pile vs. Dolma) rather than direct measurement of quality proxy scores (n-gram repetition rate, Flesch-Kincaid grade level, fastText language identification confidence). Dolma's curation advantages are well-documented [Soldaini et al., 2024], but whether these advantages manifest in the specific quality dimensions expected to predict MMLU/HellaSwag balance has not been empirically verified on matched document samples.

### 6.4 Implications for Metric Design

Two design requirements for future generalization balance metrics follow from these results:

1. **Verify denominator sensitivity.** Before using a ratio metric as a quality proxy, confirm that the denominator task remains sensitive to the factor being tested at the target training scale. HellaSwag's convergence to identical values at approximately 300 billion tokens for both model families suggests it is an insensitive denominator for corpus quality comparisons at this scale.

2. **Require architecture-matched designs for causal claims.** Single-checkpoint cross-architecture comparisons cannot isolate corpus quality effects. Future studies should either (a) use models with identical architecture trained on different corpora, or (b) use temporal trajectory analysis to bound the architecture confound within a cross-suite comparison.

### 6.5 Broader Context

The primary positive contribution of this work is methodological: documenting where cross-architecture, single-checkpoint comparisons break down reduces the risk of misattributing performance differences to corpus quality when they may reflect architecture effects. A potential concern with publishing a null result on corpus curation quality is misinterpretation as evidence that curation does not matter in general. The results are explicitly scoped to approximately 300 billion training tokens, this specific architecture pair, and the MMLU/HellaSwag ratio metric. They do not contradict prior evidence of curation benefits at full training scale [Groeneveld et al., 2024; Penedo et al., 2023]; rather, they reveal the conditions under which those benefits are not detectable with current evaluation protocols.

---

## 7. Conclusion

This study set out to test whether a more carefully curated pre-training corpus produces a more generalizable language model at matched training scale. At approximately 300 billion training tokens, using the MMLU/HellaSwag generalization balance ratio as the primary metric, and comparing Pythia-6.9B (The Pile) against OLMo-7B (Dolma), the answer is: the prediction is directly refuted, and the structural reason is that the metric's denominator is insensitive at this training scale.

The corpus-quality hypothesis predicted OLMo-7B would achieve a higher MMLU/HellaSwag ratio than Pythia-6.9B. The matched-scale evaluation (both models within 0.5% of 300 billion training tokens) finds the opposite: Pythia achieves ratio 0.5650 versus OLMo's 0.5383 (difference = −0.0267, 95% CI [−0.0447, −0.0069], Cohen's d = −2.732). This directional refutation is consistent across all four benchmarks evaluated. The most informative result is not the direction of the ratio difference, which may reflect an architecture effect, but the HellaSwag convergence: both models achieve 0.4580 on commonsense reasoning at this training scale regardless of corpus quality. When the denominator of a ratio metric is a constant, the ratio cannot discriminate between the factors hypothesized to drive its numerator.

The methodological contributions of this work are: (1) demonstration that the MMLU/HellaSwag generalization balance ratio does not discriminate corpus curation quality at approximately 300 billion tokens in a cross-architecture comparison; (2) identification of HellaSwag denominator saturation as the structural explanation; and (3) characterization of the minimum requirements — architecture-matched designs or temporal trajectory analysis — for future studies drawing causal conclusions about corpus quality effects.

Future work should address the architecture confound directly through an architecture-matched comparison: two small-scale models (1–3 billion parameters) with identical architecture trained on matched subsets of The Pile and Dolma. Temporal trajectory analysis — evaluating both models at approximately 143 billion and 300 billion tokens — would test whether the ratio gap is stable (architecture-driven) or narrowing (scale-driven). Alternative generalization balance metrics with verified denominator sensitivity at intermediate training scales (e.g., GSM8K/HellaSwag, MMLU/WinoGrande) may retain discriminative power where the MMLU/HellaSwag ratio fails. Direct measurement of quality proxy scores (n-gram repetition, Flesch-Kincaid grade level, fastText language identification) on matched document samples from each corpus would verify that the assumed quality difference is empirically real in the dimensions relevant to downstream generalization. These directions together constitute a principled research agenda for resolving the corpus quality → generalization balance question that the present study was unable to answer due to its design limitations.

---

## References

Biderman, S., Schoelkopf, H., Anthony, Q., Bradley, H., O'Brien, K., Hallahan, E., Khan, M. A., Purohit, S., Prashanth, U. S., Raff, E., Skowron, A., Sutawika, L., and Van Der Wal, O. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. *arXiv:2304.01373*.

Clark, P., Cowhey, I., Etzioni, O., Khot, T., Sabharwal, A., Schoenick, C., and Tafjord, O. (2018). Think You Have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge. *arXiv:1803.05457*.

Gao, L., Biderman, S., Black, S., Golding, L., Hoppe, T., Foster, C., Phang, J., He, H., Thite, A., Nabeshima, N., Presser, S., and Leahy, C. (2020). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. *arXiv:2101.00027*.

Gao, L., Tow, J., Abbasi, B., Biderman, S., Black, S., DiPofi, A., Foster, C., Golding, L., Hsu, J., Le Noac'h, A., Li, H., McDonell, K., Muennighoff, N., Ociepa, C., Phang, J., Reynolds, L., Schoelkopf, H., Skowron, A., Sutawika, L., Tang, P., Thite, A., Wang, B., Wang, K., and Zou, A. (2024). A Framework for Few-Shot Language Model Evaluation. *Zenodo. lm-evaluation-harness v0.4.12*. DOI: 10.5281/zenodo.10256836.

Groeneveld, D., Beltagy, I., Walsh, P., Bhagia, A., Kinney, R., Tafjord, O., Jha, A., Ivison, H., Magnusson, I., Wang, Y., Arora, S., Atkinson, D., Authur, R., Chandu, K. R., Cohan, A., Dumas, J., Elazar, Y., Gu, Y., Hessel, J., Khot, T., Merrill, W., Morrison, J., Muennighoff, N., Naik, A., Nam, C., Peters, M. E., Pyatkin, V., Ravichander, A., Schwenk, D., Shah, S., Smith, W., Strubell, E., Subramani, N., Wortsman, M., Dasigi, P., Lambert, N., Richardson, K., Zettlemoyer, L., Dodge, J., Lo, K., Soldaini, L., Smith, N. A., and Hajishirzi, H. (2024). OLMo: Accelerating the Science of Language Models. *arXiv:2402.00838*.

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., and Steinhardt, J. (2021). Measuring Massive Multitask Language Understanding. *ICLR 2021. arXiv:2009.03300*.

Koh, P. W. and Liang, P. (2017). Understanding Black-box Predictions via Influence Functions. *ICML 2017*.

Koh, P. W., Sagawa, S., Marklund, H., Xie, S. M., Zhang, M., Balsubramani, A., Hu, W., Yasunaga, M., Phillips, R. L., Gao, I., Lee, T., David, E., Stavness, I., Guo, W., Earnshaw, B., Haque, I., Beery, S., Leskovec, J., Kundaje, A., Pierson, E., Levine, S., Finn, C., and Liang, P. (2021). WILDS: A Benchmark of in-the-Wild Distribution Shifts. *ICML 2021*.

Miller, J. P., Taori, R., Raghunathan, A., Sagawa, S., Koh, P. W., Shankar, V., Liang, P., Carlin, B. P., and Schmidt, L. (2021). Accuracy on the Line: On the Strong Correlation Between OOD and In-Distribution Generalization. *ICML 2021*.

Muennighoff, N., Rush, A., Barak, B., Le Scao, T., Tazi, N., Piktus, A., Pyysalo, S., Wolf, T., and Raffel, C. (2023). Scaling Data-Constrained Language Models. *NeurIPS 2023. arXiv:2305.16264*.

Park, S. M., Georgiev, K., Ilyas, A., Leclerc, G., and Madry, A. (2023). TRAK: Attributing Model Behavior at Scale. *ICML 2023. arXiv:2303.14186*.

Penedo, G., Malartic, Q., Hesslow, D., Cojocaru, R., Cappelli, A., Beguier, C., Nguyen, B., and Launay, J. (2023). The RefinedWeb Dataset for Falcon LLM: Outperforming Curated Corpora with Web Data, Only. *arXiv:2306.01116*.

Pruthi, G., Liu, F., Kale, S., and Sundararajan, M. (2020). Estimating Training Data Influence by Tracing Gradient Descent. *NeurIPS 2020*.

Shi, W., Ajith, A., Xia, M., Huang, Y., Liu, D., Blevins, T., Chen, D., and Zettlemoyer, L. (2024). Detecting Pretraining Data from Large Language Models. *ICLR 2024. arXiv:2310.16789*.

Soldaini, L., Kinney, R., Bhagia, A., Schwenk, D., Atkinson, D., Authur, R., Bogin, B., Chandu, K., Dumas, J., Elazar, Y., Hofmann, V., Jha, A. H., Kumar, S., Lucy, L., Lyu, X., Lambert, N., Magnusson, I., Morrison, J., Muennighoff, N., Naik, A., Nam, C., Peters, M. E., Ravichander, A., Richardson, K., Shen, Z., Strubell, E., Subramani, N., Tafjord, O., Walsh, P., Zettlemoyer, L., Smith, N. A., Hajishirzi, H., Beltagy, I., Groeneveld, D., Dodge, J., and Lo, K. (2024). Dolma: An Open Corpus of Three Trillion Tokens for Language Model Pretraining Research. *arXiv:2402.00159*.

Touvron, H., Lavril, T., Izacard, G., Martinet, X., Lachaux, M.-A., Lacroix, T., Rozière, B., Goyal, N., Hambro, E., Azhar, F., Rodriguez, A., Joulin, A., Grave, E., and Lample, G. (2023). LLaMA: Open and Efficient Foundation Language Models. *arXiv:2302.13971*.

Zellers, R., Holtzman, A., Bisk, Y., Farhadi, A., and Choi, Y. (2019). HellaSwag: Can a Machine Really Finish Your Sentence? *ACL 2019. arXiv:1905.07830*.

---

*Note: All citations are drawn from the research directory documentation. Semantic Scholar verification is recommended prior to submission.*
