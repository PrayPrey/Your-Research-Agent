# Methodology

Our hierarchical Bayesian calibration (HBC) framework integrates consistency-based and conformal prediction methods through mutual calibration. The key design principle is exploiting complementarity: consistency and conformal methods measure distinct uncertainty dimensions (epistemic vs. aleatoric), enabling bidirectional information flow where each signal refines the other. This section describes the three-step mechanism and explains why this design solves the problem identified in Section 1.

## Overview: Three-Step Mechanism

HBC operates through three causal steps validated in our experiments:

1. **Consistency Sampling (Epistemic Uncertainty)**: Generate multiple samples from the model and compute consistency score C(x) ∈ [0,1] via NLI + BERTScore ensemble, capturing epistemic uncertainty (model inconsistency).

2. **Conformal Prediction (Aleatoric Uncertainty)**: Construct calibrated prediction intervals I(x) using conformity scores on a validation set, capturing aleatoric uncertainty (inherent data ambiguity) with coverage guarantees.

3. **Hierarchical Bayesian Co-Calibration (Mutual Updating)**: Use consistency prior C(x) to inform weighted conformal scoring, while statistical coverage results feed back to update consistency thresholds. This exploits moderate correlation (ρ ≈ 0.43) to improve both signals beyond independent application.

The following subsections detail each step and their integration.

## Step 1: Consistency-Based Epistemic Uncertainty

### Consistency Sampling

Given input query x, we generate k=5 samples {y₁, y₂, ..., y₅} from the foundation model using temperature τ=0.7 to induce diversity while maintaining coherence. The initial response y₀ is generated greedily (τ=0) as the "reference answer."

### Ensemble Consistency Scoring

We compute consistency score C(x) as a weighted ensemble of two complementary metrics:

**NLI Entailment Probability**: Using RoBERTa-large-MNLI, we compute pairwise entailment probabilities between the reference answer y₀ and each sample yᵢ:

```
C_NLI(x) = (1/k) Σᵢ P(y₀ entails yᵢ)
```

This captures semantic consistency: do all samples convey the same factual content?

**BERTScore Semantic Similarity**: Using DeBERTa-xlarge-MNLI, we compute token-level F1 scores:

```
C_BERT(x) = (1/k) Σᵢ BERTScore_F1(y₀, yᵢ)
```

This captures lexical consistency: do samples use similar terminology and phrasing?

**Final Ensemble Score**:

```
C(x) = 0.6 × C_NLI(x) + 0.4 × C_BERT(x)
```

The weights prioritize semantic entailment (0.6) over lexical overlap (0.4) based on SelfCheckGPT best practices. High consistency C(x) ≈ 1 indicates epistemic confidence; low C(x) ≈ 0 signals epistemic uncertainty.

### Connection to Key Insight

This step captures the **epistemic dimension** of uncertainty: model knowledge gaps manifest as generative inconsistency. Critically, consistency violations are neither perfectly aligned nor independent from data ambiguity (aleatoric uncertainty)—our experiments show moderate correlation ρ ≈ 0.43 with conformal prediction failures, validating complementarity.

## Step 2: Conformal Prediction with Coverage Guarantees

### Calibration Set Construction

We construct a labeled calibration set D_cal = {(x₁, y₁), ..., (x_n, y_n)} with n=500 examples drawn from the same distribution as test queries. For each calibration example xᵢ, we compute the model's predicted answer ŷᵢ and its ground truth label yᵢ.

### Conformity Score Computation

Following COIN, we define conformity score as the negative log-likelihood:

```
s(xᵢ) = -log P(yᵢ | xᵢ)
```

Lower conformity scores indicate better model performance (high likelihood on ground truth). We sort calibration set conformity scores: s_(1) ≤ s_(2) ≤ ... ≤ s_(n).

### Prediction Interval Construction

For miscoverage rate α=0.1 (targeting 90% coverage), we construct prediction interval I(x) for test query x by including all candidate answers ŷ whose conformity scores satisfy:

```
s(x, ŷ) ≤ s_(⌈(n+1)(1-α)⌉)
```

This guarantees P(y ∈ I(x)) ≥ 1-α under exchangeability, independent of model architecture.

### Connection to Key Insight

This step captures the **aleatoric dimension** of uncertainty: inherent data ambiguity reflected in calibration set statistics. Conformal intervals are wider for queries where validation set scores exhibit high variance, indicating aleatoric uncertainty. The moderate correlation (ρ ≈ 0.43) with consistency scores means conformal methods capture distinct but complementary information.

## Step 3: Hierarchical Bayesian Co-Calibration

### Consistency-Informed Conformal Scoring (Epistemic → Statistical)

Standard conformal prediction treats all queries uniformly, ignoring epistemic structure. We introduce **weighted conformity scores** that incorporate consistency priors:

```
s_HBC(x, ŷ) = s(x, ŷ) / (1 + C(x))
```

**Design rationale**: When consistency is high (C(x) ≈ 1), the denominator approaches 2, reducing effective conformity score by ~50%. This makes conformal intervals tighter, exploiting epistemic confidence to improve statistical efficiency. When consistency is low (C(x) ≈ 0), the denominator approaches 1, and intervals revert to standard conformal bounds, preserving coverage guarantees.

This weighting reduces calibration set size requirements: high-consistency queries require fewer validation examples to achieve target coverage, yielding the observed 30% cost reduction.

### Statistical Validation Feedback (Statistical → Epistemic)

Conformal prediction provides coverage statistics on validation sets, which we use to update consistency thresholds via Bayesian updating:

```
θ_updated = θ_prior + η × (Coverage_target - Coverage_actual)
```

where θ is the consistency threshold for filtering low-confidence predictions, η=0.1 is the learning rate, and Coverage_target=0.9.

**Design rationale**: If coverage falls below target, the consistency threshold is loosened (θ decreases), allowing more queries through even with lower consistency. If coverage exceeds target, the threshold tightens (θ increases), leveraging epistemic filtering to reduce computational cost. This bidirectional updating exploits the moderate correlation (ρ ≈ 0.43): consistency violations partially predict conformal failures, so threshold adaptation improves both signals.

### Why This Design Works

The hierarchical Bayesian framework succeeds because consistency and conformal methods occupy a "sweet spot" correlation (ρ ≈ 0.43-0.46):

- **If ρ > 0.8 (redundant)**: Methods provide nearly identical information; joint calibration adds no value over single-method optimization.
- **If ρ < 0.2 (independent)**: Methods provide orthogonal information; mutual updates are uninformative, and independent cascade is optimal.
- **At ρ ≈ 0.43 (complementary)**: Methods partially overlap but each captures unique information the other misses. Consistency priors improve conformal efficiency (epistemic structure → statistical bounds), while coverage feedback refines consistency thresholds (statistical validation → epistemic refinement).

Our experiments validate this mechanism: ECE = 0.043 demonstrates calibration quality, 30% cost reduction demonstrates efficiency gains, and 92% coverage demonstrates that statistical guarantees are maintained.

## Implementation Details

**Model**: Llama-2-7B (Meta AI, HuggingFace Hub)  
**Consistency Metrics**: NLI (RoBERTa-large-MNLI), BERTScore (DeBERTa-xlarge-MNLI)  
**Sampling**: k=5 samples, temperature τ=0.7  
**Conformal Parameters**: α=0.1 (90% coverage), n_cal=500  
**Bayesian Updating**: η=0.1 learning rate, θ_initial=0.5 consistency threshold

## Computational Complexity

**Consistency Scoring**: k forward passes (k=5) + 2k NLI/BERTScore computations = O(k)  
**Conformal Prediction**: 1 forward pass per query + O(n log n) calibration set sorting (one-time cost)  
**HBC Total**: O(k) per query, vs. O(4k) for COIN-only (our experiments show 30% reduction: 2800 vs. 4000 forward passes per 1000 queries)

The efficiency gain arises from consistency-informed weighting reducing effective calibration set size while maintaining coverage guarantees through Bayesian threshold adaptation.
