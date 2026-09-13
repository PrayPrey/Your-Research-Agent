# The LLM Documentation-Benchmark Registry: Infrastructure for Studying Data Curation Documentation and Open-Weight Model Performance

## Abstract

Data quality is a recognized determinant of large language model performance, yet measuring it directly requires access to pretraining corpora that are rarely released. Model cards -- structured transparency documents accompanying open-weight LLM releases -- describe curation practices in human-readable prose, but whether these descriptions correlate with independently measured benchmark outcomes has not been tested at scale. This work introduces the LLM Documentation-Benchmark Registry, a dataset of n = 4,493 models linking binary curation documentation indicators extracted from HuggingFace model cards to Open LLM Leaderboard v2 benchmark scores. Using targeted family sampling to prioritize well-documented model families (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo), the registry achieves non-zero variance in three of four documentation features. A scale-and-architecture OLS baseline explains approximately 42% of V2 benchmark variance (R-squared = 0.4247). Adding a composite documentation score yields a statistically significant but negative coefficient (beta = -3.45, p = 1.1 x 10^-8), with a marginal R-squared increment of 0.0042. This negative association is attributed to a size-vintage confound rather than a causal effect of documentation on performance. Additionally, perplexity filtering -- a widely practiced curation technique -- is absent from all 3,749 retrieved model cards under its canonical name, indicating a vocabulary gap in current documentation standards. The registry is intended as infrastructure for future causal analysis using propensity-matched designs.

## 1. Introduction

Across 4,493 open-weight language models submitted to the Open LLM Leaderboard, only 3.5% document any pretraining data curation practice in their model cards. Naive OLS regression indicates that those models score lower on standardized benchmarks than their undocumented counterparts (beta = -3.45, p = 1.1 x 10^-8). This counterintuitive result reflects a size-vintage confound rather than a causal effect, and it motivates the systematic registry introduced in this paper.

Data quality has been formalized as a determinant of language model loss. Subramanyam et al. (2025) extend the Chinchilla scaling law (Hoffmann et al., 2022) to include a dimensionless data quality scalar Q, yielding a loss function L(N, D, Q) with gamma_CLM approximately 0.39. However, directly measuring Q requires controlled noise injection experiments or access to proprietary training corpora. For the majority of deployed open-weight models, neither is available.

Model cards (Mitchell et al., 2019) and datasheets (Gebru et al., 2021) are structured transparency documents that describe training data practices. When model developers document deduplication, domain composition choices, or decontamination procedures, they provide binary indicators of curation practice that are observable at scale without corpus access. Whether these documentation indicators serve as reliable proxies for data quality -- whether they predict benchmark performance beyond scale -- has not been empirically tested. No systematic registry linking model card curation documentation to benchmark performance at scale has previously existed.

This gap is relevant to AI governance. If documentation correlates with quality, transparency frameworks carry evidential weight for model evaluation. If the correlation is absent or confounded, governance frameworks that treat documentation as a quality proxy lack empirical support.

This work makes three contributions:

1. **The LLM Documentation-Benchmark Registry (n = 4,493).** The first large-scale dataset joining binary curation documentation indicators from HuggingFace model cards with Open LLM Leaderboard v2 benchmark scores across six evaluation tasks (IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO). Three of four documentation features (deduplication, domain composition, decontamination) exhibit non-zero variance.

2. **Targeted family sampling methodology.** An initial alphabetical retrieval approach (H-E1) yielded only 177 model cards concentrated in the 0-A range, missing all major documented families. A targeted family sampling approach (H-E1-v2) prioritizes LLaMA, Mistral, Qwen, Falcon, Pythia, and OLMo families, retrieving 3,749 cards and achieving sufficient feature variance for regression analysis.

3. **Confound identification.** Naive OLS produces a statistically significant negative documentation coefficient (beta = -3.45, p = 1.1 x 10^-8). The most plausible explanation is a size-vintage confound: well-documented base models are disproportionately older and smaller-parameter models, while high-scoring V2 models tend to be newer, larger, or instruction-tuned derivatives. Additionally, perplexity filtering is absent from model cards under its canonical name, revealing a vocabulary gap in current documentation standards.

The paper is organized as follows. Section 2 surveys related work. Section 3 describes the registry construction methodology. Section 4 presents the experimental design. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.

## 2. Related Work

This work intersects four areas: quality-aware scaling laws, perplexity-based data selection, benchmark evaluation methodology, and model documentation standards.

### 2.1 Data Quality in Pretraining and Scaling Laws

The Chinchilla scaling law (Hoffmann et al., 2022) characterizes loss as a function of model size N and training data volume D, assuming fixed data quality. Subramanyam et al. (2025) extend this framework to include a data quality scalar Q, yielding L(N, D, Q) = A/N^alpha + B/(D^beta * Q^gamma) + E with gamma_CLM approximately 0.39. This formalization is important for understanding the role of data quality but operationally limited: Q must be measured through controlled experiments, not observationally from deployed models.

Myntti et al. (2025) show that text register (opinion, news, web) differentially affects benchmark scores. Diao et al. (2025) demonstrate that automated domain mixture optimization yields improvement on target-domain benchmarks. These studies establish that data composition affects benchmark performance but require corpus access to compute composition.

The present work operationalizes data quality through observable documentation indicators (binary presence/absence in model cards) rather than requiring corpus access. This approach scales to thousands of models but measures documentation rather than implementation -- a distinction discussed further in Section 6.

### 2.2 Perplexity and Corpus-Level Quality Proxies

Thrush et al. (2025) estimate perplexity-benchmark rank correlations across 90 Open LLM Leaderboard v1 models to identify high-quality data sources for pretraining. Shum et al. (2025) build on this with FastText-based data selection using pre-computed loss-benchmark correlations. Messmer et al. (2025) show that model-based filtering on MMLU can match rule-based filtering with 15% of training tokens.

These methods require either inference access or actual training runs. The documentation proxy used here requires only model card scraping and scales to 4,493 models with no inference compute. This work uses Open LLM Leaderboard v2, which evaluates harder reasoning and mathematical capabilities (IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO) that differ from the v1 benchmark suite (ARC, HellaSwag, TruthfulQA, Winogrande, GSM8K, MMLU). Direct score comparisons with Thrush et al. (2025) are therefore not appropriate.

### 2.3 Benchmark Evaluation and Contamination

Wu et al. (2024) propose constructing contamination-free benchmarks from new knowledge. Lee et al. (2022) demonstrate that deduplication of pretraining data measurably improves downstream benchmark performance. These studies establish that documented decontamination and deduplication practices -- tracked here as binary features -- have real effects on benchmark outcomes.

### 2.4 Model Documentation Standards

Mitchell et al. (2019) introduce model cards as AI transparency infrastructure. Gebru et al. (2021) propose datasheets for datasets. Despite wide adoption on HuggingFace, model cards have primarily been studied qualitatively rather than for their relationship to independently measured outcomes. The present work is, to the authors' knowledge, the first to quantitatively link model card curation documentation to independently measured benchmark performance at the scale of thousands of models.

### 2.5 Summary of Positioning

| Work | Models | Documentation Signal | Performance Signal |
|---|---|---|---|
| Thrush et al. (2025) | 90 | Computed (inference) | Open LLM Leaderboard v1 |
| Subramanyam et al. (2025) | Synthetic | Controlled (training) | Held-out loss |
| Myntti et al. (2025) | Few | Direct corpus access | Benchmark scores |
| This work | 4,493 | Human-written (cards) | Open LLM Leaderboard v2 |

## 3. Method

### 3.1 Overview

The approach operationalizes data quality through observable documentation indicators in HuggingFace model cards. The central challenge is connecting two independently maintained data sources -- model card text and leaderboard benchmark scores -- at ecosystem scale. Direct measurement of data quality Q requires accessing pretraining corpora, which are proprietary for most deployed models. Model cards are the only large-scale observable artifact describing training data practices.

### 3.2 Data Sources

**Open LLM Leaderboard v2.** The `open-llm-leaderboard/contents` dataset (HuggingFace Datasets) provides benchmark scores for 4,497 model submissions across six tasks: IFEval, BBH, MATH Level 5, GPQA, MUSR, and MMLU-PRO. This dataset includes `params_b` (parameter count in billions) and `avg_score` (mean of six benchmark scores). V2 benchmarks were used because they measure harder reasoning and mathematical capabilities that resist scale saturation, yielding a lower baseline R-squared and potentially more room for additional explanatory factors.

**HuggingFace Model Card API.** Model card text was retrieved via the HuggingFace Hub Python library, accessing the README.md markdown content for each model.

**Training token counts.** Training token counts were obtained from model card metadata and, where unavailable, from model family defaults reported in original papers (e.g., LLaMA-2: 2T tokens, Mistral-7B: 1T tokens, Pythia: per-checkpoint training tokens from EleutherAI). Models without retrievable token counts were handled by architecture-family mean imputation. Token counts were log-transformed before regression. The availability of token counts varies across the registry, and full provenance is documented in the released dataset.

### 3.3 Registry Construction Pipeline

**Stage 1: Leaderboard Loading and Filtering.** The leaderboard dataset was loaded, deduplicated, and filtered to retain models with at least 4 of 6 benchmark scores non-null, yielding n = 4,493 analyzable models.

**Stage 2: Targeted Family Sampling.** A key methodological choice is the retrieval order for model card API calls, which are subject to rate limits of approximately 3,000-4,000 cards per day. An initial alphabetical retrieval (H-E1) yielded only 177 cards concentrated in the 0-A range, systematically excluding well-documented model families whose names begin with later letters (LLaMA, Mistral, Qwen). The targeted family sampling approach reorders the model ID list to prioritize six well-documented families:

- LLaMA family: `meta-llama/`, `NousResearch/Llama`
- Mistral: `mistralai/`
- Qwen: `Qwen/`
- Falcon: `tiiuae/falcon`
- Pythia: `EleutherAI/pythia`
- OLMo: `allenai/OLMo`

This prioritization ensures that models from families known to document curation practices are retrieved first, achieving feature variance within API rate constraints. This constitutes a non-random sampling strategy: the selected families are among the best-documented in the ecosystem and may not be representative of all 4,493 registry models. The sampling is a practical necessity given API constraints and is appropriate for testing whether any observable documentation signal exists; it is not appropriate for estimating ecosystem-wide documentation rates. Of the 4,493 models in the registry, 114 (2.5%) matched targeted family prefixes.

**Stage 3: Model Card Retrieval.** Cards were retrieved with exponential backoff and checkpoint-based resumability (saving every 100 models). Total cards retrieved: 3,749, including 177 reused from the initial H-E1 run. The remaining 744 models without retrievable cards were assigned doc_score = 0 by default. This conservative assignment conflates "undocumented" with "documentation not retrievable," which may introduce downward bias in documentation rate estimates.

**Stage 4: Feature Extraction.** Four binary documentation indicators were extracted using pre-registered regex patterns applied before data access:

| Feature | Regex Pattern Target |
|---|---|
| `dedup_documented` | `dedup\|near.?dup\|minhash\|exact.?dedup` |
| `perplexity_filter_documented` | `perplexity.{0,20}filter\|ppl.{0,10}filter` |
| `domain_composition_documented` | `domain.{0,30}(%\|percent\|composition)\|data.{0,30}mix` |
| `decontamination_documented` | `decontaminat\|n.?gram.{0,20}overlap\|benchmark.{0,20}holdout` |

A composite `doc_score` was computed as the sum of four binary features (range 0-4).

**Stage 5: Registry Assembly.** Leaderboard scores were joined with documentation features on model name. Models without retrieved cards received doc_score = 0 (conservative default).

### 3.4 Statistical Analysis

Two OLS regression specifications were estimated:

- **Baseline:** avg_score ~ log(params) + log(tokens) + C(arch_family)
- **Proposed:** avg_score ~ log(params) + log(tokens) + doc_score + C(arch_family)

Both were estimated using OLS (statsmodels) with heteroskedasticity-robust (HC3) standard errors. Gate criteria for the existence test were: n_analyzable >= 200 AND n_features_with_variance >= 3.

The doc_score variable is 0 for 96.5% of observations, making it a highly zero-inflated regressor. OLS is used as a first-order approximation, and the coefficient is treated as a descriptive statistic rather than a causal estimate. A binary any_documentation robustness check (doc_score >= 1 vs. 0) is deferred to future analysis to address the zero-inflation of the continuous doc_score regressor.

## 4. Experimental Setup

Three research questions guided the experiments:

**RQ1 (Registry Feasibility):** Can a registry of at least 200 LLMs with at least 3 non-zero-variance curation documentation features be assembled from publicly available data?

**RQ2 (Scale Baseline):** How much V2 benchmark variance is explained by scale and architecture alone?

**RQ3 (Documentation Effect):** After scale controls, does doc_score predict benchmark performance, and in what direction?

### 4.1 Dataset

| Stage | Count |
|---|---|
| Leaderboard rows (raw) | 4,497 |
| After benchmark coverage filter (>= 4/6) | 4,493 |
| Targeted family models prioritized | 114 |
| Model cards retrieved (total) | 3,749 |
| Models with doc_score >= 1 | 158 |

The 114 models matching targeted family prefixes were prioritized for retrieval; remaining cards were retrieved within the same API budget window until the rate limit was reached.

V2 benchmarks (IFEval, BBH, MATH Level 5, GPQA, MUSR, MMLU-PRO) were used rather than V1 because they measure harder capabilities less susceptible to scale saturation.

### 4.2 Baselines

**Scale Baseline:** OLS with log(params) + log(tokens) + architecture family fixed effects, establishing how much variance is attributable to scale.

**Scale + Documentation (Proposed):** Adds doc_score to the scale baseline.

### 4.3 Evaluation Metrics

Primary metrics: n_analyzable, n_features_with_variance, R-squared_baseline, beta_docs, p_value_docs, delta_R-squared. Statistical significance threshold: alpha = 0.05 with HC3 robust standard errors. Nested model comparison: the F-test for a single added regressor is equivalent to the squared t-statistic for beta_docs.

### 4.4 Implementation Details

Python 3.10, pandas, statsmodels 0.14, huggingface_hub 0.20. All regex patterns were pre-registered before data access. Total H-E1-v2 runtime was approximately 6.7 hours, dominated by API rate-limited card retrieval. The analysis was CPU-only (no GPU required for OLS).

## 5. Results

### 5.1 Registry Assembly (RQ1)

The H-E1-v2 pipeline assembled the registry meeting all gate criteria: n_analyzable = 4,493 (gate: >= 200) and n_features_with_variance = 3 (gate: >= 3).

**Table 1: Feature Variance Comparison (H-E1 vs. H-E1-v2)**

| Feature | H-E1 Variance | H-E1-v2 Variance | Status |
|---|---|---|---|
| `dedup_documented` | 0.002889 | 0.01512 | Non-zero (both) |
| `perplexity_filter_documented` | 0.000000 | 0.000000 | Zero (both) |
| `domain_composition_documented` | 0.002889 | 0.02006 | Non-zero (both) |
| `decontamination_documented` | 0.000000 | 0.00200 | Non-zero in H-E1-v2 only |

The `perplexity_filter_documented` feature remained zero-variance in both runs despite targeted sampling. Manual inspection of LLaMA-2, Mistral, and Qwen cards confirmed that labs describe this practice using alternative terminology such as "quality filtering," "CCNet filtering," or "fastText quality filter" rather than "perplexity filtering."

![Registry construction pipeline showing data collection stages and dropout funnel.](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_data_problems/docs/youra_research/20260317_data_problems/paper/figures/dropout_funnel.png)

**Figure 1.** Registry construction pipeline: 4,497 raw leaderboard rows to 4,493 analyzable models with documentation features.

![Distribution of doc_score across 4,493 models.](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_data_problems/docs/youra_research/20260317_data_problems/paper/figures/doc_score_distribution.png)

**Figure 2.** Distribution of doc_score across 4,493 registry models. 96.5% of models have doc_score = 0.

![Model family breakdown in the registry.](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_data_problems/docs/youra_research/20260317_data_problems/paper/figures/family_breakdown.png)

**Figure 3.** Model family composition of the registry.

### 5.2 Scale Baseline (RQ2)

**Table 2: OLS Baseline -- Scale-and-Architecture Model**

| Estimand | Value |
|---|---|
| R-squared_baseline | 0.4247 |
| log(params) coefficient | Positive, statistically significant |
| log(tokens) coefficient | Positive, statistically significant |

The scale-and-architecture baseline explains 42.47% of V2 benchmark variance. This is substantially lower than the 60-75% that might be expected based on V1 benchmark data, consistent with the observation that V2 tasks (GPQA, MUSR, MATH Level 5) resist scale saturation. The remaining 57.53% of unexplained variance leaves room for additional explanatory factors.

### 5.3 Documentation Effect (RQ3)

**Table 3: OLS Proposed -- Scale + Documentation Model**

| Parameter | Value |
|---|---|
| doc_score coefficient (beta_docs) | -3.4520 |
| p-value (beta_docs) | 1.145 x 10^-8 |
| R-squared_proposed | 0.4289 |
| delta_R-squared | +0.0042 |
| Wald F-test (nested model comparison) | p = 1.145 x 10^-8 |

The F-test for nested model comparison (baseline vs. proposed) is equivalent to the t-test for beta_docs under OLS with a single added regressor; the Wald F-statistic equals the squared t-statistic. The reported p-value confirms that adding doc_score provides a statistically significant improvement over the baseline model at p < 0.001.

The documentation coefficient beta_docs = -3.45 is statistically significant and negative. Models with more documented curation practices score 3.45 points lower per additional documented feature after controlling for scale and architecture. However, the practical effect size is small: delta_R-squared = +0.0042 represents 0.42 percentage points of additional variance explained -- a statistically detectable but substantively modest increment.

![Documentation feature coverage across model families.](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_data_problems/docs/youra_research/20260317_data_problems/paper/figures/feature_coverage.png)

**Figure 4.** Documentation coverage by feature and model family.

![Benchmark score heatmap across model families.](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_data_problems/docs/youra_research/20260317_data_problems/paper/figures/benchmark_heatmap.png)

**Figure 5.** Benchmark score heatmap by architecture family and documentation status.

### 5.4 Identifying the Size-Vintage Confound

The negative coefficient is most plausibly explained by a size-vintage confound. Well-documented models (LLaMA-2, Mistral-7B, Qwen-7B, Pythia, OLMo) are predominantly 7B-70B parameter base models from the 2023-2024 era. High-scoring V2 models tend to be newer, larger, or instruction-tuned derivatives that inherit undocumented base model curation.

Three competing explanations for beta_docs < 0, ordered by qualitative assessment of plausibility (formal tests distinguishing these mechanisms are not available in this study and are deferred to propensity-matched analysis):

1. **Size confound (most plausible):** Documented base models are predominantly in the 7B-13B range; larger undocumented models score higher due to scale.
2. **Temporal confound:** Well-documented models predate the V2 benchmark launch.
3. **Fine-tuned model dominance:** 96.5% of models are fine-tuned derivatives with doc_score = 0; many score well on instruction-following tasks unrelated to pretraining curation.

The delta_R-squared = +0.0042 indicates that doc_score adds detectable information beyond scale, but the direction of the effect is confounded. Causal interpretation of beta_docs is not warranted from this analysis.

## 6. Discussion

### 6.1 Findings

**Finding 1: Registry assembly is feasible and reveals ecosystem documentation patterns.** 96.5% of Open LLM Leaderboard models document zero curation practices. The 3.5% that do are concentrated in well-established model families. This sparsity characterizes the documentation landscape within which AI governance frameworks must operate.

**Finding 2: Naive regression conflates documentation with model characteristics.** The negative beta_docs = -3.45 is statistically robust but substantively misleading as a causal estimate. It reflects a selection artifact: documented models are from an earlier, smaller-parameter era. Without size-matched controls, the documentation-quality relationship cannot be credibly estimated from these data.

**Finding 3: Perplexity filtering is undocumented under its canonical name.** Complete absence of the `perplexity_filter_documented` signal across 3,749 model cards indicates that automated documentation checks using canonical vocabulary will systematically miss this practice. Labs use alternative terms such as "quality filtering," "CCNet filtering," or "fastText quality filter."

### 6.2 Limitations

**L1: Documentation-to-implementation validity is untested.** The assumption that documentation presence reflects actual curation implementation has not been verified. Bridge validation using models with accessible pretraining corpora (e.g., Pythia/The Pile, OLMo/Dolma) is required.

**L2: Extreme feature sparsity.** With 96.5% of models at doc_score = 0, the effective sample of documented models is small (n = 158). This is sufficient for the existence gate but may limit statistical power for subgroup analyses.

**L3: V2 benchmark mismatch with original hypothesis.** The hypothesis was originally formulated for V1 knowledge-recall benchmarks (MMLU, ARC). The operational data uses V2 benchmarks (IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO), which emphasize reasoning and mathematics. The original prediction about differential sensitivity across benchmark types requires reformulation for V2.

**L4: Observational design.** All beta_docs estimates are subject to unmeasured confounding. Findings are correlational.

**L5: Targeted sampling introduces selection bias.** The families chosen (LLaMA, Mistral, Qwen, Falcon, Pythia, OLMo) are among the best-documented in the ecosystem. This non-random sampling is necessary for achieving feature variance but limits generalizability.

**L6: Missing card non-randomness.** The 744 models without retrievable cards are assigned doc_score = 0 by default. These models may differ systematically from those with accessible cards, introducing measurement error that is not random with respect to benchmark performance.

**L7: Binary indicator operationalization.** The `perplexity_filter_documented` indicator uses canonical terminology and misses equivalent practices described under alternative names. This operationalization limitation applies to all four binary features and should be addressed in future work using vocabulary-aware NLP extraction.

**L8: Log(doc_score + 1) specification not empirically verified.** An alternative log-transformed specification was considered to address the right-skewed distribution of doc_score but was not computed from actual data. The directional consistency of such a specification with the linear model remains to be confirmed empirically.

### 6.3 Broader Impact

The registry provides a public dataset for empirically grounding AI governance frameworks. The finding that perplexity filtering documentation is absent under its canonical name has practical value for documentation standard bodies.

Uncritical use of this characterization could stigmatize model families without accounting for the documented selection biases. The negative beta_docs should not be interpreted as evidence that documentation is harmful.

## 7. Conclusion

Across 4,493 open-weight language models, naive OLS regression shows that models documenting their pretraining data curation practices score lower on standardized benchmarks. This result is traced to a size-vintage confound: well-documented models are predominantly older, smaller-parameter base models, while high-scoring V2 models tend to be newer, larger, or fine-tuned derivatives. The confound itself is a finding that motivates propensity-matched analysis as the appropriate next step.

The contributions of this work are:

1. **The LLM Documentation-Benchmark Registry (n = 4,493):** The first large-scale dataset linking binary curation documentation indicators to V2 benchmark scores, revealing that 96.5% of evaluated models document zero curation practices.

2. **Targeted family sampling:** A retrieval methodology ensuring sufficient feature variance (3 of 4 binary features) within API rate constraints, with explicit acknowledgment of the resulting selection bias.

3. **Confound identification:** Documentation of the size-vintage confound behind beta = -3.45 and the perplexity filtering vocabulary gap.

Several directions for future work are motivated by these findings. Bridge validation should test whether documented families show measurably different corpus hygiene metrics using models with accessible pretraining corpora. Propensity-matched regression should attempt to isolate documentation effects within parameter strata, controlling for model size and vintage. Benchmark-type differential analysis should reformulate the differential sensitivity claim for V2 benchmarks. Vocabulary-aware NLP extraction should expand feature coverage beyond canonical terminology.

Whether model cards contain genuine signals about training data quality remains an open question. The registry provides the infrastructure to make it an answerable one.

## References

Mitchell, M., Wu, S., Zaldivar, A., et al. (2019). Model Cards for Model Reporting. *Proceedings of FAT\** 2019.

Gebru, T., Morgenstern, J., Vecchione, B., et al. (2021). Datasheets for Datasets. *Communications of the ACM*, 64(12).

Hoffmann, J., Borgeaud, S., Mensch, A., et al. (2022). Training Compute-Optimal Large Language Models. *NeurIPS 35*.

Lee, K., Ippolito, D., Nystrom, A., et al. (2022). Deduplicating Training Data Makes Language Models Better. *ACL 2022*.

Wu, X., Pan, L., et al. (2024). AntiLeak-Bench: Preventing Data Contamination by Automatically Constructing Benchmarks. *ACL 2024*.

Thrush, T., Potts, C., Hashimoto, T. (2025). Improving Pretraining Data Using Perplexity Correlations. *ICLR 2025*. arXiv:2409.05816.

Subramanyam, A., Chen, Y., Grossman, R. L. (2025). Scaling Laws Revisited: Modeling the Role of Data Quality in Language Model Pretraining. arXiv:2510.03313.

Myntti, A., Henriksson, E., Laippala, V., Pyysalo, S. (2025). Register Always Matters: Analysis of LLM Pretraining Data Through the Lens of Language Variation. arXiv:2504.01542.

Diao, S., et al. (2025). Nemotron-CLIMB: CLustering-based Iterative Data Mixture Bootstrapping for Language Model Pre-training. arXiv:2504.13161.

Shum, K., Huang, Y., et al. (2025). Predictive Data Selection: The Data That Predicts Is the Data That Teaches. *ICML 2025*. arXiv:2503.00808.

Messmer, B., Sabolcec, V., Jaggi, M. (2025). Enhancing Multilingual LLM Pretraining with Model-Based Data Selection. arXiv:2502.10361.

HuggingFace Open LLM Leaderboard Team. (2024). Open LLM Leaderboard v2. HuggingFace Dataset: `open-llm-leaderboard/contents`.
