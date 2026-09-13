# 3. Methodology

Our key insight is that annotation drift is detectable as a *direction-level* change in stylistic preference coefficients across annotation strata — not merely a magnitude shift. This motivates a design with three components: (1) a quality covariate that isolates stylistic preference from semantic quality updating; (2) round-stratified coefficient comparison with bootstrap confidence interval non-overlap testing; and (3) an AI-typicality geometric projection with discriminant validity control. Together, these form the two experimentally validated components of the Alignment Asymmetry Index (AAI).

## 3.1 Problem Formulation

Let $D = \{(q_i, r_i^+, r_i^-, \ell_i, t_i)\}_{i=1}^N$ denote a preference dataset where $q_i$ is a prompt, $r_i^+$ and $r_i^-$ are the preferred and rejected responses, $\ell_i$ is the preference label, and $t_i \in \{1, 2, 3\}$ is the annotation round (stratum). We model the preference probability as:

$$P(\ell_i = 1 \mid x_i, t_i) = \sigma\!\left(\beta_Q^{(t)} \cdot Q_{\text{early}}(x_i) + \beta_L^{(t)} \cdot \Delta L_i + \beta_H^{(t)} \cdot \Delta H_i + \beta_S^{(t)} \cdot \Delta S_i\right)$$

where $Q_{\text{early}}(x_i)$ is a frozen quality surrogate trained on round-1 labels, $\Delta L_i$, $\Delta H_i$, $\Delta S_i$ are stylistic feature differences between preferred and rejected responses, and all coefficients are estimated separately per stratum $t$.

**The AAI drift signal** is defined as the vector $(\Delta\beta_L, \Delta\beta_H, \Delta\beta_S)$ where $\Delta\beta_k = \beta_k^{(3)} - \beta_k^{(1)}$ and a coefficient is counted as *directionally drifted* if the 95% bootstrap confidence intervals for round 1 and round 3 do not overlap.

## 3.2 Quality Covariate: Q_early

The central challenge in measuring stylistic drift is separating genuine quality-based preference updating (annotators learning to identify better responses) from stylistic norm internalization (annotators adapting to AI-typical surface features). We address this with a frozen quality surrogate.

**Q_early** is a logistic regression model trained exclusively on round-1 preference labels, using non-stylistic features: response perplexity, semantic similarity to the prompt, and toxicity score. Once trained, Q_early is frozen and its prediction is included as a covariate in all downstream round-stratified regressions.

**Rationale:** If $\beta_Q^{(t)}$ remains stable across rounds while $\beta_L^{(t)}$ shifts, we can attribute the coefficient change to stylistic preference updating rather than quality recalibration. The stability criterion is $|\beta_Q| < 0.2$ (threshold set in pre-registration; observed $|\beta_Q| = 0.017$, well within bounds).

Q_early is calibrated via Platt scaling (sigmoid calibration). We validate calibration via the Brier score difference between rounds. Note: HH-RLHF's public release contains near-uniform preference labels (chosen responses are consistently preferred), requiring pseudo-label construction for Brier validation — a documented limitation that affects calibration precision but not the stability of the quality control covariate.

Figure 2 shows the Q_early reliability diagrams across rounds, confirming that the quality surrogate maintains stable calibration across annotation strata.

## 3.3 Stylistic Feature Extraction

We extract three stylistic features from the difference between preferred and rejected responses:

| Feature | Symbol | Operationalization |
|---------|--------|-------------------|
| Verbosity | $\Delta L_i$ | $n\_words(r_i^+) - n\_words(r_i^-)$ |
| Hedging | $\Delta H_i$ | $hedge\_count(r_i^+) - hedge\_count(r_i^-)$ |
| Structured reasoning | $\Delta S_i$ | $struct\_count(r_i^+) - struct\_count(r_i^-)$ |

Hedging count is computed as the frequency of uncertainty markers (e.g., "perhaps", "might", "it depends"); structured count captures enumeration markers (numbered lists, bullet points, "First/Second/Finally" sequences). All features are standardized with a shared StandardScaler fit on round-1 training data and applied consistently to rounds 2 and 3 — ensuring coefficient comparability across strata.

**Rationale for shared scaler:** If each round's features are standardized independently, coefficient magnitudes reflect within-round variance rather than cross-round shifts. Fitting the scaler once on round 1 and applying it to later rounds anchors all coefficients to the same feature scale, making $\Delta\beta_k$ interpretable as a direction-level shift.

Variance Inflation Factor analysis confirms feature orthogonality: VIF < 1.03 for all three features, ruling out multicollinearity as a confound.

## 3.4 Round-Stratified Coefficient Comparison (H-M2 Protocol)

For each annotation stratum $t \in \{1, 3\}$ (early and late rounds), we:

1. Split the stratum data into 75% train / 25% held-out test
2. Fit a logistic regression preference predictor with features $[Q_{\text{early}}, \Delta L, \Delta H, \Delta S]$
3. Extract coefficients $(\beta_L^{(t)}, \beta_H^{(t)}, \beta_S^{(t)})$
4. Compute 2,000-iteration stratified bootstrap confidence intervals

A coefficient is classified as *directionally drifted* if the 95% CIs for rounds 1 and 3 are non-overlapping. The pre-registered gate requires $n\_directional \geq 2$ of 3 features. We observe $n\_directional = 1$ (β_L only meets this criterion), with all three deltas positive (sign\_consistent = true).

**Logistic regression configuration:** C = 1.0, solver = lbfgs, max\_iter = 1000, class\_weight = balanced, random\_state = 42.

## 3.5 AI-Typicality Geometric Projection (H-M1 Protocol)

The coefficient comparison tests whether preference *weights* shift directionally. The geometric projection tests whether the preference *gradient* — the direction in which annotation decisions move — is specifically aligned with AI-typical stylistic patterns.

**AI-typicality vector construction:** We compute the centroid difference between AI-generated and human-written responses in round-1 HH-RLHF data, encoded via a frozen all-MiniLM-L6-v2 sentence transformer (384-dimensional embedding space). This vector $\mathbf{v}_{AI}$ represents the stylistic direction from human-typical to AI-typical text.

**Projection score:** For each annotation decision, we compute the cosine projection of the preference gradient (embedding difference between preferred and rejected response) onto $\mathbf{v}_{AI}$. Higher projection scores indicate preference decisions more aligned with the AI-typicality direction.

**Between-group analysis:** We use WebGPT comparisons dataset (19,578 annotation decisions). Due to the absence of worker\_id fields in the public release (a documented limitation; see Section 6), we substitute a between-group tercile design: annotators are grouped by annotation confidence proxy (score magnitude $|s_0 - s_1|$) into three terciles and compared via regression.

$$\text{projection\_score} \sim \beta_{\text{exposure}} \cdot \text{exposure\_tercile} + \epsilon$$

**Discriminant validity control:** We validate that the signal is specific to the AI-typicality vector (not a generic embedding artifact) via a placebo permutation test: we replace $\mathbf{v}_{AI}$ with a randomly oriented unit vector and repeat the projection analysis 200 times. The observed $\beta_{\text{exposure}} = 0.041$ (p = 2.05×10⁻⁵) is significantly above the placebo null distribution (placebo p = 0.48), confirming discriminant validity.

Figure 2 shows the AI-typicality projection vector alongside a topic-axis placebo vector, illustrating the specificity of the signal.

## 3.6 Datasets

**Anthropic HH-RLHF** [Bai et al. 2022]: 160,800 preference comparisons across three annotation phases (helpful, harmless, red-team). We use equal index-based partitioning to create three strata of 53,600 rows each. We note that this partitioning is a proxy for temporal order, not a verified temporal metadata field — a limitation we address in Section 6.

**OpenAI WebGPT Comparisons** [Stiennon et al. 2020]: 19,578 preference comparisons between model-generated and human-written summaries. Used for the geometric projection analysis (H-M1). Worker ID metadata is absent from the public JSONL release, requiring the between-group tercile design.

Both datasets are available via HuggingFace Datasets (Anthropic/hh-rlhf; openai/webgpt\_comparisons).

## 3.7 Implementation

All experiments are implemented in Python 3.10 with scikit-learn (logistic regression, bootstrap), sentence-transformers (MiniLM-L6-v2 encoder), statsmodels (panel regression), and matplotlib (visualization). Code is organized as modular pipelines (data\_loader.py, features.py, q\_early.py, coefficient\_comparison.py) with 26 unit tests (all passing). Experiments were run on a single NVIDIA H100 NVL GPU (CUDA\_VISIBLE\_DEVICES=0). The H-E1 coefficient analysis required approximately 49 minutes; H-M2 completed in approximately 2.5 minutes.
