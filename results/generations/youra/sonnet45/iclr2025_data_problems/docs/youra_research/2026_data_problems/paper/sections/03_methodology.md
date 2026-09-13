# 3. Methodology

## 3.1 Overview

Our approach operationalizes the data quality scalar Q from quality-aware scaling
laws [Subramanyam et al., 2025] through observable documentation indicators in
HuggingFace model cards. The key challenge — connecting two independently maintained
data sources at ecosystem scale — requires a dedicated registry construction pipeline.

**Rationale:** Direct measurement of Q requires accessing pretraining corpora, which
are proprietary for most deployed models. Model cards are the only large-scale
observable artifact describing training data practices. If documentation presence
correlates with implementation rigor, binary documentation indicators provide a
tractable proxy for Q without corpus access.

Figure 1 (dropout_funnel.png) illustrates the full pipeline, from raw leaderboard data
to the OLS regression analysis. We describe each stage below.

## 3.2 Data Sources

**Open LLM Leaderboard v2.** We use the `open-llm-leaderboard/contents` dataset
(HuggingFace Datasets), which provides benchmark scores for 4,497 model submissions
across six tasks: IFEval, BBH, MATH Level 5, GPQA, MUSR, and MMLU-PRO. This dataset
also includes `params_b` (parameter count in billions) and `avg_score` (mean of six
benchmark scores), eliminating the need for separate HuggingFace API calls for scale
information.

*Why v2 rather than v1:* The v1 schema (`open-llm-leaderboard/results`) uses an
incompatible benchmark column structure. V2 benchmarks (GPQA, MUSR, MATH Lvl 5)
measure harder reasoning and mathematical capabilities that resist scale saturation,
yielding lower baseline R² and more room for data quality signals to emerge.

**HuggingFace Model Card API.** We retrieve model card text via the HuggingFace Hub
Python library (`huggingface_hub.model_info()`), accessing the README.md markdown
content for each model in the leaderboard.

## 3.3 Registry Construction Pipeline

The pipeline proceeds in five stages (see `h-e1-v2/code/main.py`, `data_collection.py`):

**Stage 1: Leaderboard Loading and Filtering.**
We load the leaderboard dataset and apply two filters:
(a) *Deduplication:* Remove model_name duplicates (keeping first occurrence), reducing
4,497 → 4,497 unique models.
(b) *Benchmark coverage filter:* Retain only models with non-null scores in ≥4/6 benchmark
tasks, yielding n = 4,493 analyzable models. Missing benchmark scores are imputed as
the model's mean across available tasks.

**Stage 2: Targeted Family Sampling.**
A key innovation is the retrieval order for model card API calls, which are subject
to HuggingFace API rate limits (~3,000–4,000 cards per day). Alphabetical retrieval
(implemented in H-E1) systematically excludes well-documented model families: the
0–A prefix range contains primarily fine-tuned derivatives that do not document
pretraining curation.

We implement `sort_model_ids_by_family()`, which reorders the model ID list to
prioritize six well-documented families first:

```python
TARGETED_FAMILY_PREFIXES = [
    "meta-llama/", "NousResearch/Llama",  # LLaMA family
    "mistralai/",                           # Mistral
    "Qwen/",                                # Qwen
    "tiiuae/falcon",                        # Falcon
    "EleutherAI/pythia",                    # Pythia
    "allenai/OLMo",                         # OLMo
]
```

These families were selected because their technical reports explicitly document
deduplication, domain composition, and/or decontamination practices. After exhausting
targeted families, the remainder of the list follows original alphabetical order.
Within a rate-limited retrieval window (~3,749 cards), this ordering ensures that
the cards most likely to show feature variance are retrieved first.

**Stage 3: Model Card Retrieval.**
We retrieve model cards using `retrieve_model_cards()` with exponential backoff and
checkpoint-based resumability (saving every 100 cards). Retrieved cards from H-E1
(177 cards, 0–A prefix range) are reused from checkpoint to avoid redundant API calls.
Total cards retrieved: 3,749 (including 177 reused from H-E1).

**Stage 4: Feature Extraction.**
We extract four binary documentation indicators from card text using pre-registered
regular expression patterns:

| Feature | Pattern Target | Example Terms Detected |
|---|---|---|
| `dedup_documented` | Deduplication practice | "deduplication", "MinHash", "exact dedup" |
| `perplexity_filter_documented` | Perplexity filtering | "perplexity filter", "perplexity-based filtering" |
| `domain_composition_documented` | Domain mix reporting | "domain composition", "web crawl fraction", "data mixture" |
| `decontamination_documented` | Test set removal | "decontamination", "benchmark decontamination", "test set removal" |

Features are binary (1 = documented, 0 = not documented or card unavailable).
The composite `doc_score` = sum of four binary features (range 0–4).

**Stage 5: Registry Assembly.**
`build_registry()` joins leaderboard benchmark scores with extracted documentation
features on `model_name`. Models without retrieved cards receive `doc_score = 0`
(default, conservative). The final registry contains n = 4,493 rows with complete
benchmark coverage and documentation feature vectors.

## 3.4 Statistical Analysis

**Baseline OLS model:**
$$\text{avg\_score}_i = \beta_0 + \beta_1 \log(\text{params}_i) + \beta_2 \log(\text{tokens}_i) + \sum_k \gamma_k \cdot \mathbb{1}[\text{arch\_family}_i = k] + \varepsilon_i$$

**Proposed OLS model:**
$$\text{avg\_score}_i = \beta_0 + \beta_1 \log(\text{params}_i) + \beta_2 \log(\text{tokens}_i) + \beta_{\text{docs}} \cdot \text{doc\_score}_i + \sum_k \gamma_k \cdot \mathbb{1}[\text{arch\_family}_i = k] + \varepsilon_i$$

where `arch_family` is recovered from the model_id prefix via `extract_arch_family()`.
Models without recoverable token counts receive a median imputed value. Both models
are estimated using OLS via `statsmodels` with heteroskedasticity-robust standard errors.

The primary estimands are:
- **R²_baseline**: Variance explained by scale-and-architecture alone
- **β_docs**: Documentation coefficient (marginal effect of one additional documented curation feature)
- **δR²**: Incremental R² gain from adding documentation (R²_proposed − R²_baseline)

**Gate criteria (H-E1 / H-E1-v2):**
- `n_analyzable ≥ 200`: Registry has sufficient scale for OLS analysis
- `n_features_with_variance ≥ 3`: At least 3 of 4 binary features have non-zero variance across the registry

Both criteria are evaluated in `validate_registry()` before OLS estimation proceeds.

## 3.5 Implementation Notes

The pipeline is implemented in Python 3.10 using `pandas`, `statsmodels`, `scipy`,
and `huggingface_hub`. Code is modular (8 files): `main.py` orchestrates the pipeline;
`data_collection.py`, `feature_extraction.py`, `registry_builder.py`, `analysis.py`,
and `visualization.py` implement respective stages; `config.py` centralizes constants;
`utils.py` provides checkpointing and logging utilities. The H-E1-v2 implementation
is a minimal SCOPE_REFINEMENT of H-E1 — only `main.py` is modified to add
`sort_model_ids_by_family()`.

All code, registry data, and pre-registered regex patterns are made publicly available
to support reproducibility and future registry extensions.
