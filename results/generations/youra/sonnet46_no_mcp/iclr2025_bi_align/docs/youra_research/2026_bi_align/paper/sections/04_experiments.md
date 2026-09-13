# 4. Experimental Setup

We design experiments to answer three research questions derived directly from the claims in Section 1:

**RQ1:** Do stylistic preference coefficients (β_L, β_H, β_S) shift directionally across HH-RLHF annotation strata after controlling for semantic quality (Q_early)?

**RQ2:** Is the annotation preference gradient in WebGPT comparisons aligned with the AI-typicality direction in sentence embedding space, and is this alignment discriminant-valid?

**RQ3:** What minimum data requirements are needed to confirm individual annotator causal adaptation — and what can we learn from the null results where those requirements are unmet?

These questions map to three sub-hypothesis experiments: H-E1 (existence of coefficient drift), H-M1 (AI-typicality geometric projection), and H-M2 (round-stratified coefficient comparison).

## 4.1 Datasets

**Anthropic HH-RLHF** [Bai et al. 2022] provides 160,800 preference comparisons across three sequential annotation phases. We load the dataset via HuggingFace Datasets (Anthropic/hh-rlhf) and partition into three equal strata of 53,600 rows each using index-based ordering. This partitioning serves as a temporal proxy; genuine annotation timestamps are not present in the public release (see Section 6.1 for implications).

| Dataset | Rows | Strata | Rows/Stratum | Task |
|---------|------|--------|--------------|------|
| HH-RLHF | 160,800 | 3 (index-based) | 53,600 | Helpful/Harmless preference |

*Why chosen:* HH-RLHF is the most widely analyzed RLHF preference dataset with documented sequential annotation phases. The three-phase structure provides the minimum temporal depth needed for round-stratified coefficient comparison.

**OpenAI WebGPT Comparisons** [Stiennon et al. 2020] provides 19,578 preference comparisons between model-generated and reference human-written responses. The dataset documents annotation sessions via worker IDs and timestamps in the original design; however, the public JSONL release does not include worker\_id fields, and the HuggingFace loading script is deprecated in datasets ≥ 4.0. We use the 19,578 available comparison records for the geometric projection analysis (RQ2), substituting a between-group tercile design for the planned within-annotator panel regression.

| Dataset | Rows | Design | Task |
|---------|------|--------|------|
| WebGPT | 19,578 | Between-group tercile | Summary preference |

*Why chosen:* WebGPT provides a second RLHF dataset with different annotation structure and task type (summarization vs. conversation), enabling cross-dataset validation of the AI-typicality projection.

## 4.2 Baselines

We compare against three reference conditions:

**Random temporal split:** We verify that the temporal round split produces different coefficient patterns than an equivalent random split of the same size. This confirms that observed effects are attributable to temporal ordering rather than sampling variance.

**Q_early quality predictor (frozen):** The quality covariate baseline isolates how much of the preference signal is explained by semantic quality alone, providing the denominator for interpreting stylistic coefficient magnitudes.

**Placebo AI-typicality vector:** A randomly oriented unit vector in the same embedding space, used to validate that the AI-typicality projection signal is direction-specific rather than an embedding artifact (discriminant validity baseline).

*Why each baseline is included:* The random split baseline rules out sampling effects; the Q_early baseline enables stylistic-quality decomposition; the placebo vector validates measurement specificity — all three are necessary to establish the causal interpretation of the observed drift signal.

## 4.3 Evaluation Metrics

**Primary metrics (pre-registered):**

| Metric | Definition | Gate Threshold | Hypothesis |
|--------|------------|----------------|------------|
| n\_directional | Number of features with non-overlapping 95% bootstrap CIs across rounds | ≥ 2 of 3 | H-M2 |
| sign\_consistent | All stylistic Δβ > 0 | true | H-M2 |
| β_exposure | Coefficient for exposure tercile in projection regression | > 0, p < 0.05 | H-M1 |
| Placebo p-value | Empirical p for random vector projection | > 0.05 | H-M1 |
| Interaction p-value | Round × ambiguity interaction in logistic model | < 0.0167 (Bonferroni) | H-E1 |

**Secondary metrics:**

- Δβ_L magnitude: verbosity coefficient difference (early vs. late round)
- Bootstrap CI non-overlap: direction-level evidence strength
- Tercile F-statistic: between-group separation in geometric projection
- β_Q stability: |β_Q| < 0.2 (quality covariate stability check)
- Topic balance p-value: chi-square test for topic distribution uniformity across strata

Statistical significance is evaluated at α = 0.05 (unadjusted) and α = 0.0167 (Bonferroni-corrected for k = 3 stylistic features). Bootstrap confidence intervals use 2,000 stratified resamples.

## 4.4 Implementation Details

**Feature engineering:** Stylistic features are extracted from the text difference between preferred and rejected responses. All features are standardized with a shared StandardScaler fit on round-1 training data and applied to later rounds without refitting, ensuring coefficient comparability.

**Logistic regression:** scikit-learn LogisticRegression with C = 1.0, solver = lbfgs, max\_iter = 1000, class\_weight = balanced, random\_state = 42. Train/test split: 75%/25% stratified by stratum.

**Bootstrap CI:** 2,000 stratified resamples per stratum (H-M2); 200 resamples (H-E1). Degenerate cases (single-class bootstrap samples) handled via exception catching with sample count reporting.

**Sentence encoder:** all-MiniLM-L6-v2 sentence transformer, frozen weights, batch encoding at inference (H-M1).

**Compute:** Single NVIDIA H100 NVL GPU (CUDA\_VISIBLE\_DEVICES=0). H-E1 runtime: ~49 minutes (bootstrap-dominated). H-M1 runtime: ~8 minutes. H-M2 runtime: ~2.5 minutes.

**Reproducibility:** All random states fixed (random\_state = 42). Dataset loading via HuggingFace Datasets with deterministic shuffling disabled. Code available with full unit test suite (26 tests, all passing).
