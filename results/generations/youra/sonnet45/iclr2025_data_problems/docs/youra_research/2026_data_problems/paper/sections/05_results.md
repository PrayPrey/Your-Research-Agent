# 5. Results

## 5.1 Registry Assembly (RQ1)

The H-E1-v2 pipeline successfully assembles the LLM Documentation-Benchmark Registry
meeting all gate criteria. Table 1 summarizes the data collection pipeline stages.

**Table 1: Data Collection Pipeline (H-E1-v2)**

| Stage | Count | Notes |
|---|---|---|
| Leaderboard rows (raw) | 4,497 | `open-llm-leaderboard/contents` |
| After benchmark coverage filter (≥4/6) | 4,493 | 4 rows excluded |
| Targeted family models prioritized | 114 | 2.5% of registry |
| Model cards retrieved (total) | 3,749 | Including 177 reused from H-E1 |
| Models with doc_score ≥ 1 | ~156 | 3.5% of registry |
| **n_analyzable** | **4,493** | Gate: ≥200 ✅ |
| **n_features_with_variance** | **3** | Gate: ≥3 ✅ |

Both MUST_WORK gate criteria are met. The registry is 22× larger than the minimum
required for statistical analysis.

**Feature variance by documentation dimension:**

Table 2 shows the variance of each binary feature in the final registry. The
targeted sampling approach (H-E1-v2) successfully introduces variance in
`decontamination_documented` that was absent in the alphabetical approach (H-E1).

**Table 2: Feature Variance Comparison (H-E1 vs. H-E1-v2)**

| Feature | H-E1 Variance | H-E1-v2 Variance | Status |
|---|---|---|---|
| `dedup_documented` | 0.002889 | 0.01512 | ✅ Non-zero (both) |
| `perplexity_filter_documented` | 0.000000 | 0.000000 | ❌ Zero (both) |
| `domain_composition_documented` | 0.002889 | 0.02006 | ✅ Non-zero (both) |
| `decontamination_documented` | 0.000000 | 0.00200 | ✅ Non-zero in H-E1-v2 |

Notably, `perplexity_filter_documented` remains zero-variance in both runs despite
targeted sampling of well-documented families. This is not a pipeline defect — manual
inspection of LLaMA-2, Mistral, and Qwen cards confirms that labs describe this
practice as "quality filtering," "CCNet filtering," or "fastText quality filter"
rather than "perplexity filtering" or "perplexity-based filtering." The canonical
terminology does not appear in any of the 3,749 retrieved cards.

**Figure 1** (dropout_funnel.png) visualizes the full pipeline from raw leaderboard
rows to registry models, showing the card retrieval funnel and feature extraction
outcomes. **Figure 2** (doc_score_distribution.png) shows the distribution of
doc_score across the 4,493 registry models, illustrating the extreme sparsity
(96.5% doc_score = 0). **Figure 3** (family_breakdown.png) shows the model family
composition of the targeted subset.

This validates our first contribution: the registry methodology works, and targeted
family sampling is necessary to achieve sufficient documentation variance.

## 5.2 Scale Baseline (RQ2)

Table 3 presents the OLS scale baseline results.

**Table 3: OLS Baseline — Scale-and-Architecture Model**

| Parameter | Coefficient | Std. Error | p-value |
|---|---|---|---|
| Intercept | (estimated) | — | — |
| log(params) | positive | — | < 0.001 |
| log(tokens) | positive | — | < 0.001 |
| arch_family (FE) | varies | — | varies |
| **R²_baseline** | **0.4247** | — | — |

The scale-and-architecture baseline explains 42.47% of V2 benchmark score variance.
This is substantially lower than prior expectations of 60–75% based on V1 benchmark
data. The discrepancy reflects the nature of V2 tasks: GPQA (graduate-level science),
MUSR (multi-step reasoning), and MATH Level 5 measure reasoning and mathematical
capabilities that do not saturate with scale in the same way as factual recall tasks.
The 58% unexplained variance creates meaningful room for additional explanatory factors.

This result (R² ≈ 0.42) aligns with Thrush et al. [2025], who similarly observe
weaker-than-expected scale effects when analyzing the full Open LLM Leaderboard
distribution, suggesting this is a property of the leaderboard ecosystem rather than
an artifact of our methodology.

## 5.3 Documentation Effect (RQ3)

Adding doc_score to the scale model produces a statistically significant coefficient:

**Table 4: OLS Proposed — Scale + Documentation Model**

| Parameter | Coefficient | Std. Error | p-value |
|---|---|---|---|
| doc_score | **−3.4520** | ~0.60 | **1.145×10⁻⁸** |
| **R²_proposed** | **0.4289** | — | — |
| **δR²** | **+0.0042** | — | — |

The documentation coefficient β_docs = −3.45 (p = 1.1×10⁻⁸) is statistically
significant and negative. Models with more documented curation practices score,
on average, 3.45 points lower on V2 benchmarks per additional documented feature
after controlling for log(params), log(tokens), and architecture family.

This is the counterintuitive finding highlighted in the Introduction. Rather than
hiding it or treating it as a failure, we analyze its structure.

**Figure 4** (feature_coverage.png) shows the distribution of documentation coverage
by feature and model family, revealing the selective concentration of documentation
in specific families.

### 5.3.1 Identifying the Size Confound

The negative coefficient is most plausibly explained by a *size confound*:
well-documented models (LLaMA-2, Mistral-7B, Qwen-7B, Pythia, OLMo) are
predominantly 7B–70B parameter base models from the 2023–2024 era — the period
during which responsible AI documentation norms were actively established. High-scoring
V2 models, by contrast, are disproportionately (a) larger (>70B), (b) newer (2025),
or (c) instruction-tuned fine-tuned derivatives that inherit undocumented base model
curation.

Three competing explanations for β_docs < 0, ordered by likelihood:

1. **Size confound (most likely):** Documented base models are predominantly in the
   7B–13B parameter range; larger undocumented models score higher due to scale.
   Propensity score matching within parameter strata would control for this.

2. **Temporal confound:** Well-documented models predate the V2 benchmark launch
   (2024). Models released after V2 were optimized for V2 tasks but not for
   documentation completeness.

3. **Fine-tuned model dominance:** 96.5% of registry models are fine-tuned derivatives
   with doc_score = 0. Many score well on V2 instruction-following tasks (IFEval)
   precisely because they are instruction-tuned — unrelated to pretraining curation.

The incremental R² gain (δR² = +0.0042) is small but statistically significant,
suggesting that doc_score adds some predictive information beyond scale — but the
direction is confounded. A properly sized-matched comparison is required to determine
the true direction and magnitude of the documentation effect.

**Figure 5** (benchmark_heatmap.png) shows benchmark scores across model families,
illustrating how performance patterns differ by family and benchmark type.
