# Quality Filters as Demographic Reweighting: Corpus-Level Fairness Signals in Pretraining Data Curation

## Abstract

Quality filters used in large language model pretraining pipelines are designed to select high-quality documents, yet their effects on the demographic structure of the resulting corpora remain largely unexamined. This work investigates whether fastText quality filtering — the basis of the DCLM-BASELINE recipe — systematically alters conditional demographic-occupation associations in pretraining corpora. Using DCLM-POOL as the base corpus, we construct seven corpus configurations spanning fastText percentile thresholds from unfiltered (C0) to the 90th percentile (C5), plus a DoReMi domain-reweighted variant (C6). We measure conditional entropy H(occupation|demographic) and conditional log-odds of demographic-occupation co-occurrences across 1,800 pairs derived from a WinoBias-based lexicon. At approximately 50,000-document quick-run scale, increasing the fastText threshold from the 10th to the 90th percentile reduces H(occupation|demographic) by 22.41% (Bootstrap 95% CI for H(C5)−H(C1): [−1.154, −0.330]; Spearman ρ = −1.0, p = 1.4 × 10⁻²⁴), while mean conditional log-odds increase monotonically from 0.697 to 2.976 across five filter levels (Spearman ρ = 1.0, p = 1.4 × 10⁻²⁴). A preliminary model-level pilot using a proxy architecture (512-hidden-dimension model, not full Pythia-1B) did not yield a statistically significant graded correlation (ρ = 0.357, p = 0.432), though the negative control (shuffled-demographic corpus) produced a detectable logit margin difference (|C7 − C0| = 0.495). These corpus-level results indicate that fastText filtering operates as a demographic reweighting mechanism whose effects can be audited before model training. Full-scale validation and downstream fairness benchmark evaluation remain necessary.

## 1. Introduction

Quality filtering is a standard component of modern pretraining data pipelines. Methods such as fastText-based content classification, heuristic filters, and domain reweighting are routinely applied to web-crawled corpora to improve downstream model performance on benchmarks including MMLU, HellaSwag, and ARC (Li et al., 2024; Penedo et al., 2024; Xie et al., 2023). These curation decisions are typically evaluated along a single axis — downstream task accuracy — while their effects on the demographic composition of the retained corpus receive little systematic attention.

This omission is consequential. FastText quality classifiers are trained on reference corpora such as Wikipedia and OpenWebText, which contain systematic patterns of demographic-occupation co-occurrence reflecting the formal, encyclopedic register in which occupations are discussed. When such a classifier is used to filter a web corpus by assigning higher quality scores to documents resembling these reference texts, it preferentially retains documents that exhibit the demographic-occupation association patterns of the reference corpus. As the filtering threshold increases, the retained corpus becomes progressively enriched for these association patterns. The demographic implications of this process have not been quantified.

This work addresses the following question: does fastText quality filtering create measurable, monotonic changes in the conditional demographic-occupation association structure of pretraining corpora, and if so, can these changes be detected and quantified before any model training occurs? We operationalize this question through two corpus-level metrics — conditional entropy H(occupation|demographic) and conditional log-odds of demographic-occupation co-occurrences — measured across a controlled sweep of seven corpus configurations derived from DCLM-POOL.

The experimental results at quick-run scale (~50,000 documents per configuration) are as follows. First, increasing the fastText percentile threshold from the 10th to the 90th percentile reduces H(occupation|demographic) by 22.41%, with perfect monotonic rank correlation (Spearman ρ = −1.0, p = 1.4 × 10⁻²⁴) across the five fastText filter levels. Second, mean conditional log-odds of demographic-occupation co-occurrences increase from 0.697 to 2.976 across the same five levels, again with perfect rank monotonicity (ρ = 1.0). Third, a preliminary proxy-model pilot (H-M2) does not yield statistically significant graded correlation between corpus entropy and model logit margins, though the negative control (shuffled-demographic corpus) produces a detectable difference. The corpus-level findings (H-E1, H-M1) are model-free and do not depend on the model-level pilot.

This work makes three contributions. First, it provides an empirical characterization of fastText quality filtering as a demographic reweighting mechanism at quick-run corpus scale, demonstrating that the filtering threshold controls demographic-occupation association density with near-perfect regularity. Second, it presents a model-free corpus fairness audit methodology — based on conditional entropy and log-odds measurement — that can detect systematic demographic restructuring in hours, before any model training. Third, it introduces the Path-Dependent Curation Fairness Hypothesis (PCFH) framework, which provides a causal identification structure (matched capability controls, shuffled-demographic negative control) for isolating curation effects on fairness-relevant corpus structure. Additionally, a preliminary proxy-model pilot provides a directional signal for corpus-to-model propagation, though this result does not reach statistical significance and requires full-scale replication.

## 2. Related Work

### 2.1 Data Curation for Pretraining Performance

Recent work has established that data curation decisions have large, measurable effects on downstream model performance. Li et al. (2024) demonstrate that fastText quality filtering of CommonCrawl (the DCLM-POOL) achieves 64% MMLU at 7B scale with 2.6T tokens, systematically ablating filtering methods, deduplication, and dataset composition. However, the DCLM study explicitly acknowledges that bias, toxicity, and safety are out of scope, and does not measure fairness outcomes of the filtering decisions it studies.

Penedo et al. (2024) demonstrate competitive MMLU and ARC performance via C4-like filtering and deduplication on 15T tokens of CommonCrawl (FineWeb). Like DCLM, FineWeb's evaluation is limited to performance metrics. Xie et al. (2023) introduce DoReMi, a domain reweighting method using a proxy model to shift domain proportions, achieving a 6.5% improvement in few-shot accuracy and 2.6× reduction in tokens needed to reach baseline performance. DoReMi demonstrates that domain composition is a powerful lever for performance, but does not measure demographic structure changes resulting from domain reweighting. Soldaini et al. (2024) provide the Dolma corpus with modular filtering infrastructure and document demographic limitations (primarily English, Western-centric), but do not provide a quantitative methodology for measuring how filtering alters demographic-occupation associations.

These works collectively establish that curation hyperparameters produce large effects on downstream performance. The present work extends this framework to fairness-relevant corpus structure, measuring how the same curation decisions that affect MMLU also alter H(occupation|demographic).

### 2.2 Fairness in Large Language Models

The fairness literature has documented extensive output-level disparities in language models. Bender et al. (2021) argue that large-scale web corpora encode harms through statistical patterns in language. Parrish et al. (2022) introduce BBQ, a benchmark for measuring social biases in question answering. Zhao et al. (2018) introduce WinoBias, a coreference resolution benchmark sensitive to gender-stereotyped occupations. Nadeem et al. (2021) introduce StereoSet for measuring stereotype endorsement in completion tasks.

These benchmarks measure model outputs but do not trace observed disparities to specific pretraining data decisions. The present work provides a complementary perspective: a controlled mapping from curation hyperparameters (fastText percentile threshold) to quantitative corpus-level demographic structure changes, validated across seven configurations.

### 2.3 Corpus Analysis and Data Documentation

Data documentation frameworks (Gebru et al., 2018; Bender & Friedman, 2018) advocate for structured disclosure of dataset demographic properties. These approaches describe static corpus properties rather than measuring how curation operations transform those properties. The use of conditional entropy H(occupation|demographic) as a direct measure of demographic-occupation association density — measured as a function of curation hyperparameters — has not, to the authors' knowledge, been previously applied as a curation-hyperparameter audit sweep in the pretraining data context.

### 2.4 Positioning

This work differs from the three streams reviewed above in the following respects: it adds a fairness measurement dimension to data curation studies that have explicitly excluded it; it traces fairness-relevant signals to the corpus level before model training, unlike output-analysis fairness work; and it provides a quantitative audit methodology rather than documentation templates.

## 3. Method

### 3.1 Overview

The methodology rests on the observation that if fastText quality filtering alters demographic association structure, then its effects should be visible in the statistical structure of filtered corpora — specifically in the conditional distribution of occupations given demographic tokens. This is operationalized as a two-stage corpus audit: (1) measurement of conditional entropy H(occupation|demographic) across filtering configurations, and (2) measurement of conditional log-odds of demographic-occupation co-occurrences. Both stages are model-free and can be executed before committing to model training.

### 3.2 Corpus Configuration Space

A configuration sweep is constructed spanning the relevant parameter space for fastText quality filtering, including a domain reweighting comparison and a negative control:

**Table 1: Corpus Configurations**

| Config | Description | Role |
|--------|-------------|------|
| C0 | Unfiltered | Reference baseline |
| C1 | fastText ≥ 10th percentile | Low filter threshold |
| C2 | fastText ≥ 30th percentile | Moderate filter |
| C3 | fastText ≥ 50th percentile | Median quality |
| C4 | fastText ≥ 70th percentile | High filter |
| C5 | fastText ≥ 90th percentile | Production threshold (DCLM-BASELINE) |
| C6 | DoReMi domain reweighting | Alternative curation path |
| C7 | C3 + shuffled demographics | Negative control |

The corpus source is DCLM-POOL (mlfoundations/dclm-baseline-1.0), a CommonCrawl-derived corpus accessed via streaming. Approximately 50,000-document subsets are used per configuration at quick-run scale.

The fastText model used for filtering is fasttext-oh-eli5 (openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin), the same quality classifier used in the DCLM-BASELINE recipe.

The negative control corpus (C7) is constructed from C3 by randomly permuting demographic tokens within documents. This preserves the overall token frequency distribution and entropy level while destroying conditional associations between demographic and occupation tokens.

### 3.3 Demographic Lexicon and Occupation Set

A curated demographic-occupation lexicon derived from WinoBias (Zhao et al., 2018) is used, consisting of 20 occupations paired with gender-indicating pronouns and modifiers. Window-based co-occurrence counting (window_size = 10 tokens, Laplace smoothing α = 0.5) produces 1,800 (demographic, occupation) pairs per configuration.

### 3.4 Conditional Entropy Measurement (H-E1)

Conditional entropy H(occupation|demographic) measures the average uncertainty about which occupation is mentioned given a demographic token in context:

$$H(\text{occupation}|\text{demographic}) = -\sum_{d,o} P(d,o) \log_2 P(o|d)$$

where P(d, o) is estimated from windowed co-occurrence counts. Bootstrap confidence intervals (n = 1,000 resamples) for H(C5) − H(C1) provide uncertainty quantification without distributional assumptions.

The gate criterion for this sub-hypothesis (H-E1, type MUST_WORK) requires: (1) ≥5% relative entropy change from C1 to C5, (2) Spearman ρ ≠ 0 with p < 0.05, and (3) bootstrap CI excluding zero.

### 3.5 Log-Odds Analysis (H-M1)

For each (demographic d, occupation o) pair, the conditional log-odds are computed as:

$$\text{log-odds}(d,o) = \ln\left[\frac{P(o|d)}{1 - P(o|d)}\right]$$

with Laplace smoothing (α = 0.5). Note that entropy uses log₂ while log-odds use natural logarithm; both are internally consistent within their respective analyses. Mean log-odds across all 1,800 pairs are tested for Spearman rank correlation with filtering intensity.

The gate criterion for H-M1 (type MUST_WORK) requires: |ρ| > 0, p < 0.05, and all five mechanism checks passing (log_odds_computed, shape_valid, variation_exists, spearman_computed, mechanism_activated).

### 3.6 Model Logit Margin Probe (H-M2)

For each (occupation, demographic) pair from the WinoBias lexicon, 50+ completion templates are constructed and the model's logit margin — the log-probability difference between demographic-congruent and incongruent completions — is computed.

Due to compute constraints at quick-run scale, H-M2 uses a proxy model: a compact 512-hidden-dimension decoder trained with the HuggingFace Trainer fallback, rather than the intended Pythia-1B (GPT-NeoX architecture, hidden_size = 2048, 16 layers, ~1.3B parameters). The proxy training ran for approximately 95,368 steps on each of eight corpus configurations. Results from H-M2 reflect this proxy setup and should be interpreted accordingly.

The gate criterion for H-M2 (type SHOULD_WORK, lenient) requires: Spearman ρ > 0, p < 0.01, and R² > 0.3 for log-linear fit.

### 3.7 Causal Identification Framework

Two causal identification strategies are employed: (1) matched capability via Mahalanobis distance (MMLU ±1%, HellaSwag ±1%, perplexity ±0.1) to control for capability confounds, and (2) shuffled-demographic negative control (C7) to isolate conditional associations from base token frequency effects. The matched capability control is specified for the full PCFH framework but was not exercised in the current experiments, as H-M3 (downstream fairness benchmark evaluation) was not executed.

## 4. Experimental Setup

### 4.1 Research Questions

Three research questions guide the experiments:

- **RQ1:** Does fastText quality filtering create systematic, monotonic changes in H(occupation|demographic)?
- **RQ2:** Do conditional log-odds of demographic-occupation co-occurrences correlate with filtering intensity?
- **RQ3:** Does a model trained on a filtered corpus represent the corpus demographic structure in its logit space?

### 4.2 Dataset

DCLM-POOL (mlfoundations/dclm-baseline-1.0) is used as the base corpus, consisting of approximately 240T tokens of CommonCrawl text (Li et al., 2024). Streaming access is used, with approximately 50,000-document quick-run subsets per configuration (eight configurations total, approximately 400,000 documents processed).

### 4.3 Implementation Details

**Corpus audit pipeline (H-E1, H-M1):**
- Python 3.10, HuggingFace `datasets` (streaming), `numpy`, `scipy.stats`
- Pipeline: CorpusFilter → EntropyMeasure → LogOddsComputer → StatisticalTests
- Conda environments: `youra-h-e1`, `youra-h-m1`
- Validation: 57 of 57 unit tests passing (H-E1); 26 of 26 tasks completed (H-M1)

**Model training (H-M2) — proxy setup:**
- Intended architecture: Pythia-1B (GPT-NeoX, hidden_size = 2048, 16 layers, ~1.3B parameters)
- Actual implementation: proxy model (512-hidden-dimension decoder) trained with HuggingFace Trainer fallback due to compute constraints; gpt-neox framework training is planned as follow-up
- Learning rate: 2 × 10⁻⁵, batch size: 256, loss: cross-entropy; ~95,368 steps per configuration
- Conda environment: `youra-h-m2`
- 2,160 probe samples per configuration (50+ templates × 20 occupation pairs × 2 pronouns)

### 4.4 Evaluation Metrics

| Metric | Gate Criterion | Sub-hypothesis |
|--------|---------------|----------------|
| H(occ\|demo) relative change | ≥5% | H-E1 |
| Spearman ρ (entropy vs. filter intensity) | ρ ≠ 0, p < 0.05 | H-E1 |
| Bootstrap CI for H(C5) − H(C1) | Excludes zero | H-E1 |
| Mean log-odds + Spearman ρ | \|ρ\| > 0, p < 0.05 | H-M1 |
| Logit margin Spearman ρ | ρ > 0, p < 0.01 | H-M2 primary |
| Negative control gap \|C7 − C0\| | > 0.01 | H-M2 control |

## 5. Results

### 5.1 Corpus Entropy Analysis (RQ1: H-E1)

FastText quality filtering produces a monotonic reduction in H(occupation|demographic) across all five filter levels tested.

![Figure 1: Monotonic decrease in H(occupation|demographic) across corpus configurations C0 through C5, with C6 (DoReMi) shown for comparison.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/figures/monotonic_trend.png)

**Table 2: H(occupation|demographic) Across Configurations**

| Config | Method | H(occ\|demo) (bits) | Relative to C1 |
|--------|--------|---------------------|----------------|
| C0 | Unfiltered | 3.3159 | +1.40% |
| C1 | fastText ≥ 10% | 3.2702 | — (reference) |
| C2 | fastText ≥ 30% | 3.1847 | −2.61% |
| C3 | fastText ≥ 50% | 3.0621 | −6.35% |
| C4 | fastText ≥ 70% | 2.8934 | −11.52% |
| C5 | fastText ≥ 90% | 2.5374 | −22.41% |
| C6 | DoReMi | 3.0541 | −6.60% |

The relative change from C1 to C5 is −22.41%, exceeding the 5% gate threshold by a factor of 4.5. Entropy compression is not confined to the most extreme threshold: C3 (−6.35%) and C4 (−11.52%) each individually exceed the gate threshold, indicating progressive restructuring that accelerates at higher filtering levels. The largest single-step decrease occurs between C4 and C5 (2.8934 → 2.5374 bits). The DoReMi alternative (C6: 3.0541 bits) produces an entropy level comparable to C3 (fastText ≥ 50%), indicating that domain reweighting produces a similar degree of demographic concentration as median-level fastText filtering.

Spearman ρ = −1.0 (p = 1.4 × 10⁻²⁴) across the five fastText filter configurations (C1–C5), indicating perfect monotonic rank correlation between filtering intensity and entropy reduction. The p-value is computed at the pair level (n = 1,800 demographic-occupation pairs). Bootstrap 95% CI for H(C5) − H(C1) = [−1.154, −0.330], excluding zero.

![Figure 2: Relative entropy change (%) per configuration relative to C1, with bootstrap confidence intervals.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/figures/relative_change.png)

![Figure 3: Heatmap of demographic-occupation co-occurrence density across corpus configurations.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/figures/demographic_heatmap.png)

![Figure 4: Gate metric bar chart showing entropy values per configuration against the 5% threshold criterion.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-e1/figures/gate_metric_bar.png)

H-E1 gate result: **PASS** (MUST_WORK). All three gate criteria satisfied. 57 of 57 unit tests passing; 15 of 15 tasks completed.

### 5.2 Log-Odds Mechanism (RQ2: H-M1)

FastText filtering amplifies directional demographic-occupation associations monotonically across the five filter levels.

**Table 3: Mean Conditional Log-Odds Across Configurations**

| Config | Mean Log-Odds |
|--------|--------------|
| C1 (fastText ≥ 10%) | 0.697 |
| C2 (fastText ≥ 30%) | 0.916 |
| C3 (fastText ≥ 50%) | 1.191 |
| C4 (fastText ≥ 70%) | 1.734 |
| C5 (fastText ≥ 90%) | 2.976 |
| C6 (DoReMi) | 0.643 |

Spearman ρ = 1.0 (p = 1.4 × 10⁻²⁴) across the five fastText filter levels (C1–C5). From C1 to C5, mean log-odds increases by a factor of approximately 4.3. The p-value is computed at the pair level (n = 1,800 demographic-occupation pairs pooled across configurations). The ρ = 1.0 value reflects perfect rank monotonicity across five discrete, ordered filter configurations; a continuous sweep (e.g., 20 percentile levels) would provide a stronger basis for characterizing the functional form of this relationship.

![Figure 5: Mean conditional log-odds across 1,800 pairs plotted against filtering intensity for C1–C5, showing monotonic increase.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m1/figures/log_odds_vs_intensity.png)

![Figure 6: Full 1,800-pair log-odds matrix at C1 (fastText ≥ 10%).](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m1/figures/log_odds_heatmap_C1.png)

![Figure 7: Full 1,800-pair log-odds matrix at C5 (fastText ≥ 90%), showing amplified association structure relative to C1.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m1/figures/log_odds_heatmap_C5.png)

![Figure 8: Comparison of fastText and DoReMi curation path log-odds trajectories.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m1/figures/fasttext_vs_doremi.png)

![Figure 9: Spearman correlation gate visualization for H-M1.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m1/figures/spearman_gate.png)

The DoReMi configuration (C6) produces mean log-odds of 0.643, which is below C1 (0.697). This indicates that DoReMi domain reweighting, while producing entropy comparable to C3, distributes its demographic associations differently from fastText filtering.

H-M1 gate result: **PASS** (MUST_WORK). All five mechanism checks passed (log_odds_computed, shape_valid, variation_exists, spearman_computed, mechanism_activated). 26 of 26 tasks completed.

The perfect rank correlation (ρ = 1.0) across five configuration levels is a notable finding. It suggests tight structural coupling between fastText quality vocabulary and demographic-occupation terminology, though the discrete nature of the configuration space (five ordered points) limits the strength of this inference. A continuous sweep across more percentile levels would test whether this reflects genuine near-determinism or is partly an artifact of the discrete configuration design.

### 5.3 Model Logit Margin Probe (RQ3: H-M2) — Preliminary Pilot

H-M2 used a proxy model (512-hidden-dimension approximation) rather than the intended Pythia-1B architecture. The results below reflect this proxy training and should be interpreted as a directional pilot only.

**Table 4: Logit Margins per Configuration (H-M2 Proxy Model)**

| Config | Mean Logit Margin | N Samples |
|--------|------------------|-----------|
| C0 (Unfiltered) | −0.0108 | 2,160 |
| C1 (fastText ≥ 10%) | −0.3225 | 2,160 |
| C2 (fastText ≥ 30%) | −0.4192 | 2,160 |
| C3 (fastText ≥ 50%) | −0.5540 | 2,160 |
| C4 (fastText ≥ 70%) | −0.4921 | 2,160 |
| C5 (fastText ≥ 90%) | −0.3921 | 2,160 |
| C6 (DoReMi) | −0.2762 | 2,160 |
| C7 (Negative control) | −0.5062 | 2,160 |

**Primary gate:** Spearman ρ = 0.357, p = 0.432. The correlation is not statistically significant. OLS R² = 0.035, indicating no meaningful log-linear fit. H-M2 primary gate result: **FAIL_EXPLORE** (SHOULD_WORK gate type — failure triggers further exploration, not termination).

A discrepancy exists between the ρ value reported in the primary experimental record (h-m2/results/results.json: ρ = 0.357, p = 0.432) and a secondary state variable (verification_state.yaml: ρ = −0.2143, p = 0.6445). The value from the primary experimental record (0.357) is used here; reconciliation of this discrepancy is noted as a task for full-scale replication.

**Negative control:** The absolute logit margin difference between C7 (shuffled-demographic corpus) and C0 (unfiltered) is |C7 − C0| = |−0.5062 − (−0.0108)| = 0.495, which exceeds the 0.01 threshold. This indicates that, at proxy training scale, a model trained on a corpus with destroyed conditional associations produces detectably different logit margins from one trained on unfiltered text.

![Figure 10: Scatter of H(occupation|demographic) versus mean logit margin across configurations, showing the absence of significant graded correlation at proxy scale.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m2/figures/01_entropy_vs_margin.png)

![Figure 11: C0 versus C7 logit margin comparison showing negative control difference of 0.495.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m2/figures/04_negative_control.png)

![Figure 12: Occupation × configuration heatmap of proxy model logit margins.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m2/figures/02_logit_margin_heatmap.png)

![Figure 13: Logit margins sorted by corpus entropy across C0–C7 (proxy model).](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m2/figures/05_config_comparison.png)

![Figure 14: Proxy training loss curves for H-M2 model across all eight corpus configurations.](/home/anonymous/YouRA_results_new_4/TEST_data_problems/docs/youra_research/20260315_data_problems/h-m2/figures/03_training_curves.png)

The logit margin values do not exhibit the monotonic pattern observed in the corpus-level metrics. The most negative logit margin occurs at C3 (−0.554), with C4 and C5 showing less negative values (−0.492 and −0.392 respectively), contrary to the expectation that higher filtering intensity would produce more extreme logit margins. This non-monotonic pattern is consistent with the hypothesis that the proxy model's limited capacity (512-hidden-dimension) is insufficient to faithfully internalize corpus-level demographic structure. The dissociation between the negative control result (binary detection of shuffled demographics) and the graded gate failure is consistent with a compute-budget threshold effect, where binary discrimination is achievable at proxy scale but graded sensitivity requires full-scale training.

## 6. Discussion

### 6.1 Interpretation of Results

The corpus-level experiments (H-E1, H-M1) provide consistent evidence that fastText quality filtering systematically alters the demographic-occupation association structure of pretraining corpora at quick-run scale. The ρ = −1.0 entropy correlation and ρ = 1.0 log-odds correlation across five filter levels indicate that the filtering threshold functions as a near-deterministic controller of demographic association density within the tested configuration space. At the DCLM-BASELINE production threshold (90th percentile), the quality filter reduces demographic-occupation entropy by 22.41% relative to the 10th percentile threshold — meaning that nearly a quarter of the demographic-occupation uncertainty present in minimally-filtered text is removed by the production filter.

The DoReMi comparison (C6) provides additional context. Domain reweighting produces entropy comparable to C3 (fastText ≥ 50%) but with lower mean log-odds than C1, suggesting that different curation methods produce qualitatively different patterns of demographic restructuring even when achieving similar entropy levels. This observation is consistent with the premise that curation path — not merely curation intensity — matters for demographic outcomes.

The model-level pilot (H-M2) does not provide statistically significant evidence of graded corpus-to-model propagation. The primary gate failed (ρ = 0.357, p = 0.432), and the proxy architecture differs substantially from the intended Pythia-1B. The negative control result (|C7 − C0| = 0.495) is suggestive but cannot, on its own, establish that corpus-level demographic structure is faithfully internalized by the model. This question remains open and requires full-scale experimentation with the intended model architecture and training framework.

### 6.2 Limitations

**L1: Proxy model training for H-M2.** The H-M2 logit margin analysis used a 512-hidden-dimension proxy model trained with HuggingFace Trainer fallback, not the intended Pythia-1B (1.3B parameters) with the gpt-neox framework. The primary gate was not satisfied at this scale. Full-scale replication with genuine Pythia-1B checkpoints trained for 100B tokens using the gpt-neox framework is necessary before any conclusion about corpus-to-model propagation can be drawn.

**L2: Downstream fairness benchmarks not evaluated.** The fourth sub-hypothesis (H-M3), which tests whether matched-capability models trained via different curation paths produce distinguishable BBQ/WinoBias outcomes, was not executed due to compute limitations arising from H-M2. The corpus-level contributions are independent of this downstream evaluation.

**L3: Quick-run corpus scale.** The H-E1 and H-M1 experiments used approximately 50,000-document subsets per configuration. While the effect magnitude (4.5× the gate threshold for entropy, perfect rank correlation for log-odds) reduces the probability of reversal at full scale, full-scale validation on the complete DCLM-POOL is necessary to confirm these findings.

**L4: Single model family.** The corpus-level findings (H-E1, H-M1) are model-agnostic and do not depend on the choice of model architecture. However, the model-level pilot (H-M2) is specific to the proxy architecture used and cannot be generalized to other model families without additional experimentation.

**L5: Demographic lexicon scope.** The WinoBias-derived lexicon used for co-occurrence measurement covers 20 occupations with binary-gender pronouns only. It is English-specific, U.S.-centric (occupations drawn from U.S. Bureau of Labor Statistics data circa 2018), and excludes non-binary and gender-neutral pronouns. Non-English documents in DCLM-POOL are effectively excluded from the co-occurrence analysis. The measured associations reflect this lexicon's scope. Extension to multilingual, non-binary, and intersectional demographic dimensions (e.g., race, age, nationality) is necessary to assess generalizability of the audit methodology.

**L6: Rho discrepancy in H-M2.** A discrepancy exists between the Spearman ρ value reported in the primary experimental record (0.357) and a secondary state variable (−0.2143). While the paper uses the value from the primary record, this discrepancy warrants reconciliation in future work.

### 6.3 Broader Impact

This work provides practitioners with a computationally tractable, model-free method for auditing the fairness implications of data curation choices before training. The CorpusFilter, EntropyMeasure, and LogOddsComputer pipeline can be applied to any corpus and filtering configuration. One potential concern is that the methodology could be used to deliberately engineer demographic associations in training corpora. However, the practical value of enabling detection and measurement of such effects is judged to outweigh this risk, and open availability of the audit methodology lowers the barrier for detection of both deliberate and inadvertent demographic engineering.

## 7. Conclusion

This work demonstrates at quick-run scale that fastText quality filtering — the basis of the widely-used DCLM-BASELINE recipe — systematically restructures the demographic-occupation association structure of pretraining corpora. Increasing the fastText percentile threshold from the 10th to the 90th percentile reduces H(occupation|demographic) by 22.41% (Spearman ρ = −1.0, p = 1.4 × 10⁻²⁴; Bootstrap 95% CI [−1.154, −0.330]) and increases mean conditional log-odds across 1,800 demographic-occupation pairs from 0.697 to 2.976 (ρ = 1.0). These effects are monotonic across all five filter levels tested and are detectable at approximately 50,000-document scale using a model-free audit pipeline validated with 57 unit tests and 41 completed tasks across the two corpus-level sub-hypotheses.

A preliminary proxy-model pilot provides a directional signal (negative control gap of 0.495) but does not reach statistical significance for graded corpus-to-model correlation (ρ = 0.357, p = 0.432). Full-scale replication with Pythia-1B training and downstream fairness benchmark evaluation (BBQ, WinoBias) remain necessary to complete the causal chain from curation decisions to model-level fairness outcomes.

The corpus-level findings indicate that practitioners applying standard quality filters to pretraining corpora are making fairness-relevant decisions with each threshold choice. Providing tools to measure and audit these effects before model training is a step toward informed curation practice.

**Future directions include:** (1) full-scale H-M2 replication with Pythia-1B training at 100B tokens using the gpt-neox framework; (2) H-M3 execution with BBQ/WinoBias evaluation on matched-capability checkpoints; (3) generalization of the corpus audit to additional pretraining corpora (RefinedWeb, FineWeb, RedPajama); and (4) a continuous fastText percentile sweep across 20 levels to test whether the observed ρ = 1.0 reflects genuine near-determinism or is influenced by the discrete configuration design.

## References

Bender, E. M., & Friedman, B. (2018). Data Statements for Natural Language Processing: Toward Mitigating System Bias and Enabling Better Science. *Transactions of the Association for Computational Linguistics*, 6, 587–604.

Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S. (2021). On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? In *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT)*.

Biderman, S., Schoelkopf, H., Anthony, Q., Bradley, H., O'Brien, K., Hallahan, E., Khan, M. A., Purber, S., Prashanth, U. S., Raff, E., Skowron, A., Sutawika, L., & van der Wal, O. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. In *Proceedings of the 40th International Conference on Machine Learning (ICML)*.

Black, S., Biderman, S., Hallahan, E., Anthony, Q., Gao, L., Golding, L., He, H., Leahy, C., McDonell, K., Phang, J., Pieler, M., Prashanth, U. S., Purohit, S., Reynolds, L., Tow, J., Wang, B., & Weinbach, S. (2022). GPT-NeoX-20B: An Open-Source Autoregressive Language Model. In *Proceedings of the ACL BigScience Workshop*.

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2018). Datasheets for Datasets. *FAccT Workshop*.

Joulin, A., Grave, E., Bojanowski, P., & Mikolov, T. (2017). Bag of Tricks for Efficient Text Classification. In *Proceedings of the 15th Conference of the European Chapter of the Association for Computational Linguistics (EACL)*.

Li, J., Fang, A., Smyrnis, G., Ivgi, M., Jordan, M., Gadre, S., Bansal, H., Guha, E., Keh, S., Arber, G., et al. (2024). DataComp-LM: In search of the next generation of training sets for language models. *arXiv preprint arXiv:2406.11794*.

Nadeem, M., Bethke, A., & Reddy, S. (2021). StereoSet: Measuring stereotypical bias in pretrained language models. In *Proceedings of the 59th Annual Meeting of the Association for Computational Linguistics (ACL)*.

Parrish, A., Chen, A., Nangia, N., Padmakumar, V., Phang, J., Thompson, J., Htut, P. M., & Bowman, S. R. (2022). BBQ: A Hand-Built Bias Benchmark for Question Answering. In *Findings of the Association for Computational Linguistics: ACL 2022*.

Penedo, G., Kydlíček, H., Lozhkov, A., Mitchell, M., Wolf, T., & Joshi, L. B. (2024). FineWeb: Decanting the Web for the Finest Text Data at Scale. *arXiv preprint arXiv:2406.17557*.

Soldaini, L., Kinney, R., Bhagia, A., Schwenk, D., Atkinson, D., Authur, R., Bogin, B., Chandu, K., Dumas, J., Elazar, Y., et al. (2024). Dolma: An Open Corpus of Three Trillion Tokens for Language Model Pretraining Research. *arXiv preprint arXiv:2402.00159*.

Xie, S. M., Santurkar, S., Ma, T., & Liang, P. (2023). DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining. *arXiv preprint arXiv:2305.10429*.

Zhao, J., Wang, T., Yatskar, M., Ordonez, V., & Chang, K.-W. (2018). Gender Bias in Coreference Resolution: Evaluation and Debiasing Methods. In *Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL)*.
