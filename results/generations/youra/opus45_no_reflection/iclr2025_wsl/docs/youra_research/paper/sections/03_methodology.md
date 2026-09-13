# Methodology

We decompose our research question into two testable hypotheses with distinct experimental designs.

## 3.1 Hypothesis Framework

**H-E1 (Existence):** Under CNN model zoo scope, class-wise accuracy profiles exhibit variance beyond what overall accuracy and per-class difficulty explain.

**H-M1 (Mechanism):** Weight matrix features correlate with class-wise accuracy profiles, explaining variance beyond the stratified baseline.

H-E1 is a prerequisite: if all behavioral variance is explained by overall accuracy, there is no signal for weight features to capture. H-M1 tests whether simple weight representations extract whatever behavioral signal exists.

## 3.2 Behavioral Variance Decomposition (H-E1)

### Stratified Baseline

We construct a baseline that predicts class-wise accuracy from overall model accuracy and per-class difficulty:

$$\hat{a}_{i,c} = \alpha_c \cdot A_i + \beta_c$$

where $a_{i,c}$ is model $i$'s accuracy on class $c$, $A_i$ is model $i$'s overall accuracy, and $\alpha_c, \beta_c$ are per-class linear coefficients fit via least squares.

This baseline captures the intuition that high-accuracy models perform better on all classes, with per-class slopes and intercepts accounting for varying class difficulty (e.g., cats are harder than ships in CIFAR-10).

### Residual Variance Ratio

We compute the fraction of class-wise variance *not* explained by the stratified baseline:

$$\text{Residual Ratio} = 1 - \frac{\sum_{i,c}(\hat{a}_{i,c} - a_{i,c})^2}{\sum_{i,c}(a_{i,c} - \bar{a}_c)^2}$$

A residual ratio > 0.05 indicates meaningful behavioral variance beyond accuracy. Higher values suggest stronger behavioral fingerprints—models with identical overall accuracy performing differently on specific classes.

### Per-Class Variance Analysis

We decompose variance per class to identify which classes show the highest behavioral differentiation:

$$\sigma^2_c = \text{Var}(a_{:,c} - \hat{a}_{:,c})$$

Classes with high $\sigma^2_c$ are those where models specialize differently despite similar overall performance.

## 3.3 Weight Statistics Probe (H-M1)

### Feature Extraction

For each model, we extract per-layer weight statistics from all convolutional and fully-connected layers:

- **Mean:** $\mu_l = \frac{1}{|W_l|}\sum_{w \in W_l} w$
- **Standard deviation:** $\sigma_l = \sqrt{\text{Var}(W_l)}$
- **Minimum:** $\min(W_l)$
- **Maximum:** $\max(W_l)$
- **L2 norm:** $\|W_l\|_2$

For the Small CNN Zoo architecture (3 convolutional + 2 fully-connected layers), this yields $5 \times 5 = 25$ features per model.

### Regression Approach

We use Ridge regression to predict per-class accuracy from weight features:

$$\hat{a}_{:,c} = X\beta_c + \lambda\|\beta_c\|^2$$

where $X$ is the $n \times 25$ feature matrix. Ridge regularization ($\lambda = 1.0$) addresses potential multicollinearity among correlated weight statistics.

### Evaluation Metric

The success criterion compares weight-feature R² against stratified baseline R²:

$$\Delta R^2 = R^2_{\text{weight}} - R^2_{\text{baseline}}$$

If $\Delta R^2 > 0$, weight features capture behavioral variance beyond overall accuracy. If $\Delta R^2 \leq 0$, simple weight statistics fail to extract behavioral signal.

## 3.4 Gate Structure

We adopt a hypothesis chain with gates:

| Hypothesis | Gate Type | Criterion | Failure Action |
|------------|-----------|-----------|----------------|
| H-E1 | MUST_WORK | Residual ratio > 0.05 | STOP: No behavioral signal exists |
| H-M1 | MUST_WORK | $\Delta R^2 > 0$ | STOP: Simple features insufficient |

H-E1 passing unlocks H-M1. If H-E1 fails, there is no behavioral variance to extract. If H-M1 fails, we conclude that more expressive representations (NF-Layers, learned embeddings) may be required.

## 3.5 Design Rationale

**Why stratified baseline?** A fair comparison requires controlling for overall accuracy. Predicting "model X is 90% accurate, so it's ~95% on easy classes and ~80% on hard classes" is not behavioral prediction—it's accuracy propagation. The stratified baseline captures this null hypothesis.

**Why simple statistics?** Unterthiner et al. achieve R² ≈ 0.97 for scalar accuracy with these features. Testing whether they extend to structured predictions establishes a baseline before investing in complex architectures.

**Why Ridge regression?** With 193 models and 25 features, regularization prevents overfitting. Ridge is interpretable and provides stable coefficient estimates.

**Why per-class analysis?** Aggregate metrics can hide class-specific failures. Per-class R² reveals whether the mechanism works uniformly or fails systematically on certain classes.
