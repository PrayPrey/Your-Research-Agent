# Experimental Setup

Our experiments test three core claims: (1) consistency and conformal methods measure distinct signals (complementarity), (2) joint calibration improves ECE beyond baselines (calibration quality), and (3) HBC reduces computational cost while maintaining coverage (efficiency). We design experiments to validate each claim with statistical rigor.

## Research Questions

**Q1 (Complementarity)**: Do consistency-based scores C(x) and conformal prediction interval membership I(x) exhibit moderate correlation (0.3 < ρ < 0.7), indicating distinct but complementary uncertainty signals?

**Q2 (Calibration Quality)**: Does hierarchical Bayesian calibration achieve Expected Calibration Error (ECE) < 0.05, significantly lower than SelfCheckGPT-only, COIN-only, and independent cascade baselines?

**Q3 (Efficiency)**: Does HBC reduce computational cost by 30-50% compared to COIN-only while maintaining coverage ≥ 90%?

## Datasets

We evaluate on three datasets selected to cover different uncertainty profiles:

### TruthfulQA (Epistemic Uncertainty)

- **Source**: Lin et al. (2021), HuggingFace `truthful_qa/generation`
- **Size**: 817 questions (full dataset)
- **Uncertainty Profile**: High epistemic uncertainty—questions designed to elicit common misconceptions and knowledge gaps
- **Example**: "What happens to you if you eat watermelon seeds?" (tests factual knowledge vs. folk beliefs)
- **Rationale**: Tests HBC on queries where consistency methods should excel (model unsure → inconsistent generation)

### HH-RLHF (Aleatoric Uncertainty)

- **Source**: Anthropic (2022), HuggingFace `Anthropic/hh-rlhf`
- **Size**: 8,552 preference pairs (test split)
- **Uncertainty Profile**: High aleatoric uncertainty—value alignment preferences with inherent ambiguity
- **Example**: Choosing between helpful vs. harmless responses in trolley problem scenarios
- **Rationale**: Tests HBC on queries where conformal methods should excel (inherent ambiguity → wide intervals needed)

### SQuAD v2 (Mixed Uncertainty)

- **Source**: Rajpurkar et al. (2018), HuggingFace `rajpurkar/squad_v2`
- **Size**: 11,873 questions (validation set)
- **Uncertainty Profile**: Mixed epistemic and aleatoric—factual QA with answerable and unanswerable questions
- **Example**: "In what country is Normandy located?" (factual but may be outside model training distribution)
- **Rationale**: Tests HBC on realistic deployment scenarios with diverse uncertainty sources

**Dataset Justification**: The three datasets span epistemic-heavy (TruthfulQA), aleatoric-heavy (HH-RLHF), and mixed (SQuAD) uncertainty profiles, enabling robust evaluation of complementarity across varied contexts.

## Baseline Methods

We compare HBC against three baselines representing different integration strategies:

### SelfCheckGPT-only (Consistency Baseline)

- **Method**: Generate k=5 samples, compute NLI + BERTScore consistency, threshold at C(x) < 0.5 to flag uncertain queries
- **Threshold**: Tuned on validation set via grid search (tested 0.3, 0.4, 0.5, 0.6, 0.7)
- **Limitation**: No statistical guarantees on coverage; provides binary uncertainty signal only

### COIN-only (Statistical Baseline)

- **Method**: Standard conformal prediction with α=0.1 (90% coverage target), n_cal=500 calibration examples
- **Conformity Score**: Negative log-likelihood s(x) = -log P(y|x)
- **Limitation**: Ignores epistemic structure; uniform treatment of all queries regardless of consistency

### Independent Cascade (Cascade Baseline)

- **Method**: SelfCheckGPT filters high-consistency queries (C(x) > 0.6), COIN applied to low-consistency subset
- **Threshold**: Consistency and conformal parameters tuned independently on same validation set
- **Limitation**: No bidirectional information flow; threshold tuning does not exploit correlation structure

**Baseline Justification**: These represent natural points in the design space—consistency-only, statistical-only, and independent sequential application—enabling attribution of HBC improvements to joint calibration specifically.

## Evaluation Metrics

### Primary Metric: Expected Calibration Error (ECE)

Measures calibration quality by comparing predicted confidence to empirical accuracy across B=10 equal-mass bins:

```
ECE = Σᵢ₌₁ᴮ (nᵢ/n) |acc(i) - conf(i)|
```

where nᵢ is the number of predictions in bin i, acc(i) is empirical accuracy, and conf(i) is mean predicted confidence.

**Target**: ECE < 0.05 (well-calibrated threshold from literature)

### Secondary Metrics

**Coverage**: Fraction of ground truth labels within conformal intervals, P(y ∈ I(x))  
**Target**: ≥ 90% (conformal prediction guarantee)

**Computational Cost**: Forward passes per 1000 queries  
**Target**: 30-50% reduction vs. COIN-only (~2000-2800 vs. 4000)

**Disagreement Rate**: Fraction of queries where C(x) < 0.5 AND y ∉ I(x), or C(x) > 0.5 AND y ∈ I(x)  
**Purpose**: Quantifies complementarity—moderate disagreement validates distinct signals

## Implementation Details

### Model Configuration

- **Model**: Llama-2-7B (meta-llama/Llama-2-7b-hf from HuggingFace)
- **Consistency Sampling**: k=5 samples, temperature τ=0.7, greedy reference (τ=0)
- **NLI Model**: RoBERTa-large-MNLI (393M parameters)
- **BERTScore Model**: DeBERTa-xlarge-MNLI (772M parameters)
- **Device**: CUDA (single GPU for reproducibility)

### Conformal Prediction Parameters

- **Miscoverage Rate**: α=0.1 (90% coverage target)
- **Calibration Set Size**: n_cal=500 per dataset
- **Conformity Score**: s(x, y) = -log P(y|x)

### HBC-Specific Parameters

- **Weighted Conformity**: s_HBC(x, y) = s(x, y) / (1 + C(x))
- **Bayesian Learning Rate**: η=0.1
- **Initial Consistency Threshold**: θ₀=0.5
- **Update Frequency**: After each 100-query batch

### Data Splits

For each dataset:
- **Calibration**: 500 examples (for conformal calibration and threshold tuning)
- **Test**: Remaining examples (TruthfulQA: 317, HH-RLHF: 8052, SQuAD: 11373)

Split procedure: Stratified random sampling to preserve label distribution.

## Statistical Testing

### Complementarity Test (Q1)

- **Metric**: Pearson correlation ρ between C(x) and I_binary(x) = 1{y ∈ I(x)}
- **Null Hypothesis**: ρ = 0 (independence) or ρ = 1 (redundancy)
- **Test**: Two-tailed significance test, p < 0.05 threshold
- **Success Criterion**: 0.3 ≤ ρ ≤ 0.7 on all three datasets

### Calibration Quality Test (Q2)

- **Metric**: ECE (primary), Coverage (secondary)
- **Null Hypothesis**: ECE_HBC = ECE_baseline for each baseline
- **Test**: Two-tailed paired t-test across 5 random seeds, p < 0.05 threshold
- **Success Criterion**: ECE_HBC < 0.05 AND p < 0.05 for all three pairwise comparisons

### Efficiency Test (Q3)

- **Metric**: Forward passes per 1000 queries, Coverage
- **Null Hypothesis**: No cost reduction or coverage drops below 85%
- **Test**: Forward pass counting across test set
- **Success Criterion**: Cost reduction ≥ 30% vs. COIN-only AND Coverage ≥ 90%

## Validation Procedure

1. **Load datasets and models** (TruthfulQA, HH-RLHF, SQuAD; Llama-2-7B, NLI, BERTScore)
2. **Split data** into calibration (500) and test sets (stratified sampling)
3. **Run each method** (SelfCheckGPT-only, COIN-only, Independent Cascade, HBC) on test sets
4. **Compute metrics** (ECE, Coverage, Cost, ρ) per dataset and method
5. **Statistical testing** (Pearson correlation for ρ, paired t-tests for ECE comparisons)
6. **Aggregate results** across datasets and random seeds (n=5)

## Reproducibility

All experiments use fixed random seeds (seed=42) for:
- Data splitting (calibration vs. test)
- Model sampling (temperature-based generation)
- Initialization (Bayesian threshold θ₀)

Code and data will be released upon acceptance to ensure full reproducibility.

## Experiment Scope

**What We Test**: Core calibration mechanism on three diverse datasets with statistical rigor (correlation analysis, paired t-tests, coverage guarantees).

**What We Do Not Test**: Out-of-distribution detection (domain shift experiments deferred to future work), adversarial robustness (not within scope of calibration contribution), real-time deployment latency (focus on forward pass count as proxy for computational cost).

These design choices focus validation on the core claims: complementarity, calibration quality, and efficiency.
