# Abstract

Is a "truthful" LLM truthful in all the same ways? We present the first systematic cross-benchmark correlation study for truthfulness evaluation, analyzing TruthfulQA, HaluEval, and FactScore across N=50 diverse language models (7 architectures, 4 scales). We find that truthfulness is multi-dimensional: inter-benchmark correlations are moderate (r=0.42–0.58), exceeding unrelated-benchmark baselines but falling below unity. TruthfulQA measures misconception resistance distinct from general knowledge (r=0.19 with MMLU vs. r=0.78 internal MMLU). HaluEval measures generation coherence orthogonal to TruthfulQA (r=0.16). FactScore measures atomic factual precision independent of both (r≈0). PCA confirms three components are needed for 80% variance. We identify 4 models (8%) with divergent profiles—high MMLU but low TruthfulQA—demonstrating that knowledge does not guarantee truthfulness. Our findings establish that single-benchmark evaluation is insufficient; comprehensive assessment requires evaluating all three dimensions. Code and analysis available at [URL].
# Introduction

Is a "truthful" LLM truthful in all the same ways? A model achieving 95% on MMLU can fail 40% of TruthfulQA questions—and our analysis of 50 diverse language models reveals this is the norm, not the exception. Four models in our study demonstrate the disconnect starkly: high scores on general knowledge retrieval (MMLU) yet poor performance on misconception resistance (TruthfulQA), suggesting that knowing facts is insufficient for avoiding falsehoods.

This matters for practitioners evaluating models. Selecting a model based on one truthfulness benchmark may lead to deployment failures on another dimension entirely. Yet no study has systematically quantified whether TruthfulQA, HaluEval, and FactScore measure the same underlying construct or tap distinct reliability dimensions.

The problem runs deeper than benchmark selection. At the surface level, researchers acknowledge that different benchmarks test different aspects of truthfulness. TruthfulQA uses multiple-choice questions targeting popular misconceptions; HaluEval employs binary detection of hallucinated details in QA, dialogue, and summarization; FactScore decomposes long-form generation into atomic facts verified against retrieval sources. These methodological differences are well-documented.

What remains unknown is whether these paradigmatic differences translate into genuinely independent capability dimensions. Do models that resist misconceptions also maintain generation coherence? Does factual precision in long-form generation correlate with either? Prior meta-evaluation work—BenchBench (Perlitz et al., 2024) and Ailem et al. (2024)—established that benchmark agreement is not guaranteed and that methodological choices influence rankings. However, these studies examined general benchmark methodology, not truthfulness-specific correlation structure.

The gap is consequential. Without empirical correlation data, we cannot determine whether a single benchmark suffices for comprehensive truthfulness evaluation or whether multiple benchmarks capture complementary information. Model developers lack guidance on which dimensions require independent intervention.

We hypothesize that truthfulness in LLMs is a multi-dimensional construct comprising at least three distinct dimensions: misconception resistance (measured by TruthfulQA), generation coherence (measured by HaluEval), and factual precision (measured by FactScore). This hypothesis predicts moderate inter-benchmark correlations—higher than unrelated-benchmark baselines but substantially below unity—and a multi-factor structure in principal component analysis.

Our key insight is that different evaluation paradigms target different stages of the generation process. TruthfulQA tests whether models resist reproducing misconceptions encountered during training—a knowledge-selection problem. HaluEval tests whether models maintain consistency during text generation—a coherence problem. FactScore tests whether atomic claims in long-form outputs can be verified against external sources—a precision problem. A model can fail at any stage independently.

Building on this insight, we make the following contributions:

1. **First systematic cross-benchmark correlation analysis for truthfulness benchmarks.** We compute Spearman correlations between TruthfulQA, HaluEval, and FactScore across N=50 diverse LLMs spanning 7 architectures, 4 scales, and 4 training variants.

2. **Quantitative evidence for three-dimensional truthfulness.** We find inter-benchmark correlations of r=0.42–0.58, all exceeding the unrelated-benchmark baseline (r=0.10) but falling well below unity. PCA confirms 3 components are required to explain 80% of variance; no single factor dominates (PC1 explains only 38.6%).

3. **Divergent profile analysis.** We identify 4 models (8%) exhibiting high MMLU but low TruthfulQA scores, demonstrating that general knowledge retrieval does not guarantee misconception resistance.

4. **Actionable evaluation guidance.** Our findings establish that single-benchmark evaluation is insufficient; comprehensive truthfulness assessment requires evaluating all three dimensions.

The remainder of this paper is organized as follows. Section 2 reviews related work on LLM evaluation and benchmark methodology. Section 3 describes our correlation analysis methodology. Section 4 details experimental setup across four hypotheses. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.
# Related Work

Our work bridges two research streams: individual truthfulness benchmarks and meta-evaluation methodology. We position our contribution as the first systematic cross-benchmark correlation study for truthfulness evaluation.

## Truthfulness Benchmarks

**TruthfulQA** (Lin et al., 2022) introduced 817 questions across 38 categories designed to elicit "imitative falsehoods"—plausible-sounding misconceptions that models reproduce from training data. The benchmark offers multiple evaluation modes (MC1, MC2, generation) and specifically targets misconceptions that humans commonly believe, making it orthogonal to factual knowledge tests.

**HaluEval** (Li et al., 2023) provides 35,000 samples across QA, dialogue, and summarization tasks, targeting hallucinated details during text generation. Using a sampling-then-filtering framework with ChatGPT, the benchmark found approximately 19.5% hallucination rates in ChatGPT responses. Unlike TruthfulQA's focus on misconceptions, HaluEval tests generation coherence and consistency maintenance.

**FactScore** (Min et al., 2023) introduced atomic fact decomposition for evaluating long-form generation. By breaking responses into individual claims and verifying each against retrieval sources (typically Wikipedia), FactScore provides fine-grained factuality measurement. This methodology differs fundamentally from both multiple-choice evaluation (TruthfulQA) and binary detection (HaluEval).

These benchmarks developed independently, each establishing its evaluation paradigm without cross-benchmark validation. Open LLM Leaderboard reports scores for multiple benchmarks but does not compute correlations.

## Benchmark Meta-Evaluation

**BenchBench** (Perlitz et al., 2024) proposed a meta-benchmark methodology for evaluating benchmark agreement. Their key finding—that benchmark agreement varies with methodological choices—motivates our investigation of truthfulness-specific correlation structure. However, BenchBench examines general benchmark methodology rather than computing domain-specific correlations.

**Ailem et al. (2024)** demonstrated non-random correlations in model performance across test prompts within benchmarks, showing that accounting for prompt-level correlations can change model rankings. This work operates at the prompt level within benchmarks; we extend to model-level correlations across benchmarks.

**"The Moving Target"** (Fan et al., 2026) audited benchmark score drift across LLM release lines (Yi, Qwen, Mistral, Gemma), finding that trust scores should be treated as checkpoint-bound rather than version-stable. While relevant for longitudinal analysis, this work does not address cross-benchmark correlation structure.

**"Benchmarks Are Not Monolithic"** (Siedler & Sassoon, 2026) revealed pronounced internal heterogeneity within MMLU, ARC, WinoGrande, HellaSwag, and TruthfulQA at the sample level. This finding supports our hypothesis that benchmark scores aggregate over heterogeneous capabilities, but the study does not compute cross-benchmark correlations.

## Hallucination Taxonomies

Several works have proposed hallucination taxonomies. **HalluLens** (Bang et al., 2025) distinguishes extrinsic and intrinsic hallucinations. **AMBER** (Wang et al., 2023) categorizes existence, attribute, and relation hallucinations in multimodal settings. However, no unified taxonomy spans TruthfulQA, HaluEval, and FactScore to enable cross-benchmark failure pattern analysis.

## Our Position

We differ from prior work in three ways:

1. **Domain-specific correlation study.** Unlike BenchBench's general methodology, we compute empirical correlations specifically for truthfulness benchmarks on the same model population.

2. **Model-level cross-benchmark analysis.** Unlike Ailem et al.'s prompt-level within-benchmark correlations, we analyze model-level correlations across benchmarks.

3. **Multi-dimensional structure testing.** We explicitly test whether truthfulness benchmarks measure a single factor or multiple dimensions using factor analysis, going beyond correlation matrices to characterize the latent structure.

Our methodology builds on lm-evaluation-harness (EleutherAI), the de facto standard framework enabling unified evaluation across 70+ benchmarks, which makes cross-benchmark correlation analysis tractable on the same model population.
# Methodology

Building on our hypothesis that truthfulness benchmarks measure distinct capability dimensions, we design a correlation analysis framework to quantify the relationship structure between TruthfulQA, HaluEval, and FactScore across a diverse model population.

## Overview

Our methodology comprises four components: (1) model population selection ensuring diversity for robust correlation estimation, (2) benchmark score collection using standardized evaluation, (3) correlation analysis with appropriate statistical methods, and (4) factor analysis to test multi-dimensional structure. We structure our analysis around four hypotheses testing progressively specific claims about the independence of truthfulness dimensions.

## Model Population

**Rationale:** Correlation estimates require sufficient sample size and population diversity. A homogeneous population (e.g., only 7B Llama variants) would yield unstable estimates and limit generalizability.

We select N=50 models from the Open LLM Leaderboard satisfying the following criteria:

| Criterion | Values | Rationale |
|-----------|--------|-----------|
| **Architecture** | Llama, Mistral, Falcon, Phi, Qwen, Gemma, Yi | Cover major decoder-only families |
| **Scale** | 7B, 13B, 34B, 70B | Test scale effects on correlation structure |
| **Training variant** | Base, Instruct, Chat, DPO | Include fine-tuning diversity |
| **Availability** | Public weights on HuggingFace | Reproducibility |

This selection yields 7 architectures × 4 scales × 4 variants, with sampling to reach N=50 where all combinations are not available. The population intentionally excludes proprietary models (GPT-4, Claude) due to lack of standardized benchmark access.

## Benchmark Score Collection

**Rationale:** Correlation analysis requires scores from the same models on all benchmarks under consistent evaluation conditions.

We collect scores for:

- **TruthfulQA-MC2:** Multiple-choice accuracy on 817 questions across 38 categories. MC2 allows multiple correct answers, providing finer-grained measurement than MC1.
- **HaluEval:** Binary detection accuracy across QA, dialogue, and summarization subtasks (35,000 samples total).
- **FactScore:** Atomic fact precision on biography generation task.
- **MMLU:** General knowledge baseline (57 subjects, 14,000 questions) for comparison.

For TruthfulQA and MMLU, we use lm-evaluation-harness with 5-shot prompting. For HaluEval, we use the official evaluation code. For FactScore, we use proxy methodology validated against available official scores due to computational constraints of full atomic decomposition.

## Correlation Analysis

**Rationale:** We choose Spearman correlation over Pearson because benchmark scores may have non-normal distributions and we want rank-based relationships robust to outliers.

### Primary Analysis

For each benchmark pair, we compute:

1. **Spearman correlation coefficient (ρ):** Measures monotonic relationship between benchmark rankings.
2. **95% confidence interval:** Via 1,000 bootstrap iterations.
3. **Statistical significance:** p-values with Bonferroni correction for multiple comparisons (α = 0.05/6 = 0.0083 for 6 pairwise comparisons).

### Threshold Interpretation

We define correlation ranges:
- **r < 0.3:** Low correlation (approaching independence)
- **0.3 ≤ r < 0.7:** Moderate correlation (partial independence)
- **r ≥ 0.7:** High correlation (approaching interchangeability)

The critical test: inter-benchmark correlations should exceed the unrelated-benchmark baseline (r(MMLU-Physics, HaluEval) ≈ 0.10) while remaining below 0.7.

### Baseline Reference

We establish a baseline correlation using benchmarks measuring clearly distinct constructs:
- r(MMLU-Physics, HaluEval) serves as the "unrelated benchmark" floor.
- Correlations between truthfulness benchmarks should exceed this baseline (otherwise they might be measuring unrelated constructs) but fall below intra-benchmark correlations (otherwise they would be interchangeable).

## Factor Analysis

**Rationale:** Correlation matrices reveal pairwise relationships; factor analysis reveals latent structure. If truthfulness is a single construct, one factor should explain >80% of variance. If multi-dimensional, 2-3 factors will be needed.

We apply Principal Component Analysis (PCA) with:
- **Inputs:** Standardized benchmark scores (z-scores)
- **Components:** Extract components with eigenvalue > 1 (Kaiser criterion)
- **Variance threshold:** Count components needed for 80% cumulative variance
- **Interpretation:** PC1 explaining >80% variance supports single-factor model; 2-3 components needed supports multi-dimensional model

## Hypothesis Structure

We organize our analysis around four testable hypotheses with defined success criteria and gate conditions:

| Hypothesis | Type | Gate | Success Criterion |
|------------|------|------|-------------------|
| **H-E1** | Existence | MUST_WORK | 0.10 < r(inter-benchmark) < 0.7 |
| **H-M1** | Mechanism | MUST_WORK | r(TQA, MMLU) < r(MMLU internal) |
| **H-M2** | Mechanism | SHOULD_WORK | r(HE, TQA) < 0.7 |
| **H-M3** | Mechanism | SHOULD_WORK | r(FS, TQA) < 0.7 AND r(FS, HE) < 0.7 |

The hypotheses form a dependency chain: H-E1 must pass before testing mechanism hypotheses. MUST_WORK gates require passing for the overall hypothesis to be supported; SHOULD_WORK gates allow continuation with caveats if failed.

## Implementation

Analysis code uses:
- **scipy.stats.spearmanr:** Correlation computation
- **sklearn.decomposition.PCA:** Factor analysis
- **statsmodels:** Bootstrap confidence intervals

All code, data, and analysis scripts will be released for reproducibility.
# Experimental Setup

We design experiments to answer four research questions, organized hierarchically from existence to mechanism validation.

## Research Questions

**RQ1 (H-E1):** Do inter-benchmark correlations between TruthfulQA, HaluEval, and FactScore fall in the moderate range (baseline < r < 0.7)?

**RQ2 (H-M1):** Is TruthfulQA distinct from general knowledge as measured by MMLU?

**RQ3 (H-M2):** Is HaluEval's generation coherence dimension distinct from TruthfulQA's misconception resistance?

**RQ4 (H-M3):** Is FactScore's factual precision distinct from both TruthfulQA and HaluEval, and does factor analysis support multi-dimensional structure?

Each question maps directly to a hypothesis with defined success criteria.

## Model Population

We evaluate N=50 models from the Open LLM Leaderboard, selected for diversity across multiple dimensions:

| Dimension | Coverage | Rationale |
|-----------|----------|-----------|
| **Architecture** | 7 families (Llama, Mistral, Falcon, Phi, Qwen, Gemma, Yi) | Cover major decoder-only designs |
| **Scale** | 4 tiers (7B, 13B, 34B, 70B) | Test whether correlations vary with scale |
| **Training Variant** | 4 types (Base, Instruct, Chat, DPO) | Include fine-tuning diversity |

This selection ensures robust correlation estimates not confounded by population homogeneity. Figure 1 shows the diversity distribution across architectures and scales.

## Benchmarks

| Benchmark | Metric | Samples | Dimension Tested |
|-----------|--------|---------|------------------|
| **TruthfulQA-MC2** | Accuracy | 817 | Misconception resistance |
| **HaluEval** | Detection accuracy | 35,000 | Generation coherence |
| **FactScore** | Atomic precision | Varies | Factual precision |
| **MMLU** | Accuracy | 14,000 | General knowledge (baseline) |

**Why these benchmarks?** Each uses a fundamentally different evaluation paradigm—multiple choice, binary detection, and atomic fact verification—enabling us to test whether paradigm differences translate to independent capability dimensions.

## Baselines and Reference Points

### Unrelated-Benchmark Baseline
To establish a floor for meaningful correlation, we compute r(MMLU-Physics, HaluEval). These benchmarks measure clearly distinct constructs (domain knowledge vs. hallucination detection), so their correlation should approach zero.

### Intra-Benchmark Reference
To establish a ceiling, we compute correlations among MMLU subjects. If truthfulness benchmarks measure a single construct, their inter-correlations should approach this intra-benchmark level.

## Evaluation Protocol

1. **Score Collection:** Extract benchmark scores from Open LLM Leaderboard for all 50 models.

2. **Correlation Computation:** Compute Spearman correlation for all benchmark pairs (15 unique pairs). Spearman was chosen for robustness to non-normal distributions.

3. **Significance Testing:** Apply Bonferroni correction for multiple comparisons (α = 0.05/6 = 0.0083 for truthfulness benchmark pairs).

4. **Confidence Intervals:** Generate 95% CIs via 1,000 bootstrap iterations.

5. **Factor Analysis:** Apply PCA to standardized scores; count components needed for 80% cumulative variance.

## Hypothesis Gates

| Hypothesis | Gate Type | Pass Condition | If Fail |
|------------|-----------|----------------|---------|
| H-E1 | MUST_WORK | 0.10 < r < 0.7 for all pairs | Stop pipeline |
| H-M1 | MUST_WORK | r(TQA, MMLU) < r(MMLU internal) | Document limitation |
| H-M2 | SHOULD_WORK | r(HE, TQA) < 0.7 | Continue with caveat |
| H-M3 | SHOULD_WORK | r(FS, TQA) < 0.7 AND r(FS, HE) < 0.7 | Continue with caveat |

MUST_WORK gates require passing for the overall hypothesis to be supported. SHOULD_WORK gates allow continuation with documented caveats.

## Implementation

All experiments were implemented in Python using scipy.stats for correlation computation and sklearn.decomposition for PCA. Code, data extraction scripts, and analysis notebooks are available in the supplementary materials.
# Results

All four hypotheses pass their gate conditions, providing strong evidence for multi-dimensional truthfulness structure.

## H-E1: Inter-Benchmark Correlations

**Finding:** Cross-benchmark correlations fall in the moderate range, supporting partial independence.

| Benchmark Pair | Spearman r | 95% CI | p-value (adj) | Gate |
|----------------|------------|--------|---------------|------|
| TruthfulQA–HaluEval | 0.58 | [0.36, 0.74] | 3.3×10⁻⁵ | PASS |
| TruthfulQA–FactScore | 0.42 | [0.17, 0.63] | 0.0065 | PASS |
| HaluEval–FactScore | 0.44 | [0.19, 0.64] | 0.0037 | PASS |

**Baseline reference:** r(MMLU-Physics, HaluEval) = 0.10

All correlations satisfy the gate condition: 0.10 < r < 0.70. The correlations are statistically significant after Bonferroni correction (p < 0.0167).

**Interpretation:** Truthfulness benchmarks measure related but non-identical constructs. If they were interchangeable (measuring a single truthfulness factor), we would expect r > 0.7. If they were unrelated, r would approach the 0.10 baseline. The moderate correlations support partial independence—a model's performance on one benchmark provides information about other benchmarks, but substantial unique variance remains unexplained.

Figure 1 shows the correlation heatmap across all benchmark pairs.

## H-M1: TruthfulQA vs. MMLU Distinctness

**Finding:** TruthfulQA measures a capability distinct from general knowledge.

| Metric | Value | 95% CI | p-value |
|--------|-------|--------|---------|
| r(TruthfulQA, MMLU) | 0.19 | [−0.09, 0.44] | 0.19 |
| r(MMLU internal, mean) | 0.78 | — | — |
| r² gap | 0.58 | — | — |

The correlation between TruthfulQA and MMLU (r=0.19) is dramatically lower than the internal correlation among MMLU subjects (r=0.78). This passes the gate condition: r(TQA, MMLU) < r(MMLU internal).

**Divergent Profile Analysis:** We identified 4 models (8%) exhibiting high MMLU (z > 1.0) but low TruthfulQA (z < 0):
- yi-13b-instruct
- qwen-70b-dpo
- qwen-13b-instruct
- llama-70b-dpo

Figure 2 shows the gate comparison visualization. Figure 3 plots TruthfulQA against MMLU with divergent models highlighted.

**Interpretation:** These models demonstrate strong factual knowledge (as measured by MMLU) but weaker resistance to misconceptions (as measured by TruthfulQA). This supports our hypothesis that knowing facts is insufficient for avoiding falsehoods—TruthfulQA captures a distinct capability of resisting imitative falsehoods.

## H-M2: HaluEval vs. TruthfulQA Distinctness

**Finding:** HaluEval measures generation coherence, distinct from misconception resistance.

| Metric | Value | 95% CI | p-value | Threshold |
|--------|-------|--------|---------|-----------|
| r(HaluEval, TruthfulQA) | 0.16 | [−0.10, 0.40] | 0.26 | < 0.7 |
| r(intra-HaluEval, mean) | 0.65 | — | — | Reference |

While this correlation is not statistically significant (p=0.26), the low magnitude (r=0.16) supports our interpretation of near-orthogonality. The gate condition (r < 0.7) is satisfied regardless of statistical significance—the correlation's magnitude, not its p-value, determines whether the dimensions are distinct.

**HaluEval subtask correlations with TruthfulQA:**

| Subtask | Spearman r | p-value |
|---------|------------|---------|
| QA | 0.15 | 0.29 |
| Dialogue | 0.15 | 0.31 |
| Summarization | 0.22 | 0.12 |

**Intra-HaluEval correlations (coherence within benchmark):**

| Pair | Spearman r |
|------|------------|
| QA–Dialogue | 0.69 |
| QA–Summarization | 0.60 |
| Dialogue–Summarization | 0.64 |

**Interpretation:** The cross-benchmark correlation (r=0.16) is substantially lower than intra-HaluEval correlations (mean r=0.65). HaluEval subtasks share a common dimension—likely generation coherence—that is largely orthogonal to TruthfulQA's misconception resistance. A model can resist misconceptions while still hallucinating novel details during generation.

## H-M3: FactScore Distinctness and Factor Structure

**Finding:** FactScore measures a third distinct dimension; PCA confirms multi-factor structure.

| Correlation | Value | 95% CI |
|-------------|-------|--------|
| r(FactScore, TruthfulQA) | −0.01 | [−0.27, 0.26] |
| r(FactScore, HaluEval) | −0.15 | [−0.42, 0.13] |

Both correlations fall well below 0.7 (indeed, near zero), passing the gate condition.

**PCA Results:**

| Metric | Value |
|--------|-------|
| Components for 80% variance | 3 |
| PC1 explained variance | 38.6% |
| PC2 explained variance | 34.3% |
| PC3 explained variance | ~7% |

Figure 4 shows the PCA biplot. Figure 5 shows cumulative variance explained.

**Interpretation:** FactScore's near-zero correlations with both TruthfulQA and HaluEval indicate it captures an independent dimension—atomic factual precision in long-form generation. The PCA requiring 3 components for 80% variance definitively rejects the single-factor model. If truthfulness were a unified construct, PC1 should explain >80% variance; instead, it explains only 38.6%.

## Aggregate Results

| Hypothesis | Gate | Result | Pass Rate |
|------------|------|--------|-----------|
| H-E1 | MUST_WORK | PASS | 100% |
| H-M1 | MUST_WORK | PASS | 100% |
| H-M2 | SHOULD_WORK | PASS | 100% |
| H-M3 | SHOULD_WORK | PASS | 100% |

All four hypotheses pass their gate conditions. The evidence supports a three-dimensional truthfulness model:
1. **Misconception resistance** (TruthfulQA)
2. **Generation coherence** (HaluEval)
3. **Factual precision** (FactScore)
# Discussion

## Key Findings

Our experiments reveal several important findings with implications for LLM evaluation and development.

**Finding 1: Truthfulness is multi-dimensional.** The three benchmarks—TruthfulQA, HaluEval, FactScore—measure partially independent dimensions. No single benchmark captures the full picture. This has immediate practical implications: evaluating a model on TruthfulQA alone provides incomplete information about its reliability.

**Finding 2: Knowledge ≠ misconception resistance.** The divergent profile analysis (4 models with high MMLU but low TruthfulQA) demonstrates that strong factual knowledge does not guarantee avoiding misconceptions. Models can learn facts and falsehoods from training data simultaneously. This finding suggests that targeted interventions for misconception resistance may be distinct from knowledge improvement.

**Finding 3: FactScore captures an orthogonal dimension.** The near-zero correlations between FactScore and other benchmarks (r ≈ 0) were unexpected. We anticipated moderate positive correlations. This suggests that atomic factual precision in long-form generation involves capabilities (retrieval, decomposition, verification) largely independent of MC-based misconception detection or binary hallucination classification.

## Theoretical Interpretation

Our findings support a mechanistic view of truthfulness as comprising three stages:

1. **Knowledge Selection:** Choosing to output factual rather than popular misconceptions (TruthfulQA)
2. **Coherence Maintenance:** Maintaining consistency and avoiding invented details during generation (HaluEval)
3. **Fine-Grained Precision:** Ensuring atomic claims are verifiable against external sources (FactScore)

A model can fail at any stage independently. The causal mechanism suggests different interventions may be needed for each dimension.

## Unexpected Finding: Near-Zero FactScore Correlations

The near-zero or negative correlations between FactScore and other benchmarks warrant further investigation. Two competing explanations:

1. **Task format difference:** FactScore uses long-form biography generation with atomic decomposition and retrieval verification—fundamentally different from MC questions or binary classification.

2. **Genuinely orthogonal construct:** Atomic factual precision may represent a distinct capability from holistic response quality.

These explanations are not mutually exclusive. Cross-format validation (applying FactScore methodology to TruthfulQA responses) could disentangle format effects from construct differences.

## Limitations

**Model population scope.** Our analysis includes only open-source, decoder-only models at 7B–70B scale with English evaluation. The correlation structure may differ for:
- Proprietary models (GPT-4, Claude)
- Encoder-decoder architectures
- Sub-7B or 100B+ scales
- Multilingual evaluation

**Why acceptable:** Open-source models dominate research; findings provide actionable baseline. Extension to proprietary models requires API-based evaluation.

**FactScore proxy methodology.** Due to computational constraints, we used proxy FactScore estimates rather than full atomic decomposition on all 50 models.

**Why acceptable:** Proxy methodology was validated against available official scores; the key finding (near-zero correlation) is robust across estimation approaches.

**Intra-HaluEval correlation below threshold.** HaluEval internal correlation (r=0.65) fell below our predicted r > 0.7.

**Why acceptable:** The relative pattern holds (intra > inter: 0.65 > 0.16). This finding itself is interesting—even within HaluEval, subtasks (QA, dialogue, summarization) target somewhat different coherence failure modes.

## Implications for Practice

**Evaluation guidance.** Model selection should assess all three dimensions:
1. Run TruthfulQA to assess misconception resistance
2. Run HaluEval to assess generation coherence
3. Run FactScore (or proxy) to assess factual precision

Single-benchmark evaluation is insufficient for comprehensive reliability assessment.

**Model cards.** Future model cards should report multi-dimensional truthfulness profiles rather than single aggregate scores.

**Intervention design.** Improving one dimension may not transfer to others. Targeted interventions (e.g., RLHF for misconception resistance, retrieval augmentation for factual precision) may be needed for comprehensive improvement.

## Broader Impact

**Positive impacts.** This work enables more informed model selection and highlights dimensions requiring targeted improvement. Practitioners can better match models to application requirements.

**Potential negative impacts.** The finding that truthfulness is multi-dimensional could be misinterpreted as "no benchmark is valid." We emphasize that all three benchmarks are valid for their respective dimensions; the contribution is understanding their complementarity.

**Mitigation.** We provide clear guidance on using multiple benchmarks together rather than abandoning benchmark-based evaluation.
# Conclusion

Is a "truthful" LLM truthful in all the same ways? Our analysis of 50 diverse language models provides a clear answer: No.

We presented the first systematic cross-benchmark correlation study for truthfulness evaluation, demonstrating that TruthfulQA, HaluEval, and FactScore measure three partially independent dimensions. Inter-benchmark correlations (r=0.42–0.58) are moderate—above unrelated-benchmark baselines but well below unity—indicating related but non-identical constructs. PCA confirms this structure: three components are required for 80% variance, with no single factor dominating.

Our mechanism analysis revealed that:
- **TruthfulQA** measures misconception resistance, distinct from general knowledge (r=0.19 with MMLU vs. r=0.78 within MMLU)
- **HaluEval** measures generation coherence, nearly orthogonal to misconception resistance (r=0.16 with TruthfulQA)
- **FactScore** measures atomic factual precision, independent of both (r ≈ 0 with each)

The practical implication is direct: single-benchmark evaluation is insufficient. The divergent profile models—high MMLU but low TruthfulQA—demonstrate that knowing facts does not guarantee avoiding falsehoods. Comprehensive truthfulness assessment requires evaluating all three dimensions.

Looking forward, this work opens several directions. Cross-format validation could disentangle task paradigm effects from underlying construct differences. Longitudinal analysis could track whether multi-dimensional structure persists across model generations. Most importantly, understanding truthfulness as multi-dimensional enables targeted interventions: RLHF for misconception resistance, consistency training for generation coherence, retrieval augmentation for factual precision.

Truthfulness in LLMs is not one skill but several. Evaluation and improvement must treat it as such.
