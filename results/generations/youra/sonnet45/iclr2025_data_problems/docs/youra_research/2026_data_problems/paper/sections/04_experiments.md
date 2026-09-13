# 4. Experimental Setup

We design a two-stage experimental protocol to answer the following research questions,
corresponding directly to the three contributions described in the Introduction:

**RQ1 (Registry Feasibility):** Can a registry of ≥200 open-weight LLMs with ≥3
non-zero-variance curation documentation features be assembled from publicly available
leaderboard and model card data?

**RQ2 (Scale Baseline):** How much of V2 benchmark score variance is explained by
scale-and-architecture alone, and does this leave meaningful room for data quality signals?

**RQ3 (Documentation Effect):** After controlling for scale and architecture, does
curation documentation (doc_score) predict benchmark performance, and if so, in which
direction and with what magnitude?

## 4.1 Dataset: Open LLM Leaderboard v2

We use the Open LLM Leaderboard v2 (`open-llm-leaderboard/contents`, accessed
2026-03-17) as the primary benchmark dataset. V2 contains 4,497 unique model
submissions with scores across six tasks:

| Task | Type | Score Range |
|---|---|---|
| IFEval | Instruction following | 0–100 |
| BBH (BIG-Bench Hard) | Multi-step reasoning | 0–100 |
| MATH Level 5 | Advanced mathematics | 0–100 |
| GPQA (Diamond) | Graduate-level science | 0–100 |
| MUSR | Multi-step reasoning | 0–100 |
| MMLU-PRO | Professional knowledge | 0–100 |

The composite `avg_score` (mean of all six tasks) serves as our dependent variable.
V2 benchmarks were chosen over V1 because they (a) measure harder capabilities
resistant to scale saturation, (b) use a stable, publicly accessible dataset
format with pre-computed scores, and (c) include `params_b` (parameter count in
billions) as a metadata field, reducing API call requirements.

We apply two preprocessing filters: (1) deduplication on model_name (no duplicates
found), and (2) benchmark coverage filter retaining models with ≥4/6 non-null scores.
This yields **n = 4,493 analyzable models**.

## 4.2 Model Card Feature Extraction

For each model in the leaderboard, we attempt to retrieve the associated HuggingFace
model card via the Hub API (`huggingface_hub.model_info()`). We extract four binary
features using pre-registered regular expression patterns. Feature definition and
example triggering phrases are given in Section 3.4 (Table 1 in Methodology).

**Retrieval protocol (H-E1 vs. H-E1-v2):**
To understand the effect of retrieval order on feature variance, we conduct two
experimental runs with the same extraction pipeline:

| Run | Card Retrieval Order | Cards Retrieved | n_features_with_variance | Gate |
|---|---|---|---|---|
| H-E1 | Alphabetical (0–A range first) | 177 | 2 | PARTIAL |
| H-E1-v2 | Targeted family sampling | 3,749 | 3 | **PASS** |

H-E1-v2 builds on H-E1 incrementally: the 177 cards from H-E1 are reused from
checkpoint, and 3,572 additional cards are retrieved using the targeted family order.
This two-run protocol provides a natural ablation study: targeted sampling vs.
alphabetical retrieval, holding all other pipeline components constant.

## 4.3 Baselines

We evaluate two regression models:

**Scale Baseline:** OLS regression predicting `avg_score` from log(params), log(tokens),
and architecture family fixed effects. This replicates the standard scaling-law
regression for deployed models and establishes how much variance is attributable to
scale alone. We use this as the comparison floor for evaluating documentation effects.

**Scale + Documentation (Proposed):** OLS regression adding `doc_score` (integer 0–4,
sum of binary curation features) to the scale baseline. The additional explanatory
power of documentation — δR² = R²_proposed − R²_baseline — quantifies how much
variance is attributable to documentation above and beyond scale.

We do not compare against external baselines (e.g., Thrush et al. [2025]) because
those methods use V1 benchmarks and inference-based perplexity measures that are
incommensurable with our V2 documentation-based approach. Our contribution is the
registry and methodology, not superiority over alternative quality proxies.

## 4.4 Evaluation Metrics

**Primary metrics:**
- `n_analyzable`: Registry scale — must be ≥200 for reliable OLS estimation (RQ1)
- `n_features_with_variance`: Number of binary features with non-zero variance (RQ1)
- `R²_baseline`: Fraction of avg_score variance explained by scale-and-architecture (RQ2)
- `β_docs`: OLS coefficient on doc_score (RQ3), with 95% confidence interval
- `p_value_docs`: Statistical significance of documentation coefficient (RQ3)
- `δR²`: Incremental R² from adding documentation to baseline (RQ3)

**Statistical testing:** We use OLS with heteroskedasticity-robust standard errors
(HC3). Statistical significance threshold: α = 0.05. We report coefficients with
their direction and confidence intervals rather than binary significance alone,
given the observational nature of the design.

## 4.5 Implementation Details

All analyses use Python 3.10 with `pandas` (2.x), `statsmodels` (0.14), `scipy` (1.11),
and `huggingface_hub` (0.20). Feature extraction uses pre-registered regex patterns
(defined before any data was accessed) to prevent post-hoc tuning. The gate evaluation
(`n_analyzable ≥ 200` AND `n_features_with_variance ≥ 3`) is enforced programmatically
before any OLS estimation proceeds. Models with missing token count estimates receive
a median-imputed value derived from the non-missing subset.

Total H-E1-v2 runtime: ~6.7 hours (dominated by HuggingFace API rate-limited card
retrieval at ~500–600 cards/hour). CPU-only (no GPU required for OLS).
