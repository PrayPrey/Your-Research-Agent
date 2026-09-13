# Product Requirements Document (PRD)
# h-m2: Embedding Similarity → Behavioral Concordance Correlation

**Version:** 1.0
**Date:** 2026-04-19
**Hypothesis:** h-m2 (MECHANISM)
**Author:** Anonymous
---

## Executive Summary

This PRD defines requirements for implementing a correlation analysis experiment to test whether embedding cosine similarity predicts behavioral concordance. The experiment analyzes user embeddings from h-m1 on the ETHICS benchmark:
- **Baseline**: Random user pairing (expected concordance ~0.50)
- **Analysis**: Correlation between embedding similarity and behavioral concordance rate

**Success Criteria**: Positive correlation (r > 0.5) with statistical significance (p < 0.05), and high-similarity pairs (>0.7) achieve concordance >0.65.

**Key Innovation**: Tests whether learned embeddings capture decision-relevant value dimensions by correlating embedding space similarity with actual behavioral agreement on moral reasoning tasks.

---

## Problem Statement

### Research Question
Does embedding similarity in the learned value space predict behavioral concordance on moral reasoning tasks, validating that embeddings capture decision-relevant value dimensions?

### Hypothesis Statement
Under the assumption that users with similar values make similar choices, if embedding cosine similarity is high (> 0.7), then behavioral concordance rate will be high (> 0.65), because the embedding space learned via contrastive learning captures decision-relevant value dimensions.

### Context
- **Prerequisite**: h-m1 (MECHANISM) validated that contrastive learning drives clustering (silhouette=0.38)
- **Building On**: h-m1 embeddings are well-clustered; h-m2 tests if similarity predicts behavior
- **Key Test**: Correlation mechanism validates that embeddings capture values, not superficial patterns

### Success Impact
- Validates that embedding similarity reflects actual value similarity
- Provides evidence for dependent hypotheses (h-m3, h-m4)
- Establishes methodological foundation for embedding-based value measurement

---

## Functional Requirements

### FR-1: Dataset Acquisition and Preprocessing

**FR-1.1: ETHICS Dataset Loading**
- Load `hendrycks/ethics` dataset (all 5 categories) from HuggingFace
- Categories: deontology, virtue, justice, utilitarianism, commonsense
- Use test split: ~13,000 examples for evaluation
- Cache to: `docs/youra_research/20260419_bi_align/.data_cache/datasets/huggingface`

**FR-1.2: User Embedding Loading**
- Load pre-trained embeddings from h-m1 checkpoint
- Expected format: User embeddings (N, 256) with user IDs
- Verify embedding dimension matches h-m1 (128 or 256-d)
- Load checkpoint: `../h-m1/checkpoints/best_model.pt`

**FR-1.3: User Response Simulation**
- Generate user responses on ETHICS tasks using h-m1 embeddings
- Response method: Embedding-based preference prediction
- Ensure each user has responses for identical task subset (for concordance measurement)
- Sample size: 1000-3000 user pairs across similarity bins

**FR-1.4: Data Statistics Tracking**
- Total ETHICS test samples: ~13,000
- User count: Based on h-m1 embeddings
- User pair sample size: 1000 (stratified by similarity)
- Similarity distribution across bins

### FR-2: Embedding Similarity Analysis

**FR-2.1: Similarity Matrix Computation**
- Compute pairwise cosine similarity for all user embeddings
- Normalize embeddings (L2 normalization)
- Similarity matrix size: (N_users, N_users)
- Store for stratified sampling

**FR-2.2: Stratified User Pair Sampling**
- Define similarity bins:
  - Low: < 0.3
  - Medium: 0.3-0.7
  - High: > 0.7 (hypothesis threshold)
- Sample ~333 pairs per bin (1000 total)
- Ensure balanced representation across bins
- Track similarity values for each sampled pair

**FR-2.3: Baseline Comparison**
- Random user pairing: Shuffle pairs randomly
- Expected baseline concordance: ~0.50 (chance level)
- Sample size: 1000 random pairs
- Use for statistical comparison

### FR-3: Concordance Measurement

**FR-3.1: Agreement Rate Calculation**
- For each user pair (i, j), measure agreement on ETHICS tasks
- Agreement = (responses_i == responses_j).mean()
- Calculate concordance for all sampled pairs
- Store concordance values aligned with similarity values

**FR-3.2: Concordance by Similarity Bin**
- Compute mean concordance for each bin (low/medium/high)
- Track standard deviation within bins
- Compare high-similarity bin against baseline

**FR-3.3: Concordance Metrics**
- Overall concordance distribution
- Concordance by ETHICS category (deontology, virtue, etc.)
- Concordance vs similarity scatter data

### FR-4: Correlation Analysis

**FR-4.1: Primary Correlation Test**
- Compute Pearson correlation coefficient (r)
- Input: (similarity_values, concordance_values) for all 1000 pairs
- Statistical significance test (p-value < 0.05)
- Use scipy.stats.pearsonr

**FR-4.2: Success Criteria Validation**
- Criterion 1: r > 0.5 (positive correlation)
- Criterion 2: High-similarity concordance > 0.65
- Criterion 3: p < 0.05 (statistical significance)
- Criterion 4: High-sim > Random baseline + 0.10

**FR-4.3: Secondary Analyses**
- Spearman rank correlation (robustness check)
- Concordance gradient across similarity threshold sweep
- Category-specific correlation (by ETHICS domain)

### FR-5: Evaluation Metrics

**FR-5.1: Primary Metrics**
- Pearson correlation coefficient (r)
- p-value (statistical significance)
- High-similarity bin concordance (mean ± std)
- Baseline concordance (random pairs)

**FR-5.2: Secondary Metrics**
- Concordance by bin (low/medium/high)
- Spearman rank correlation
- Effect size: High-sim concordance - Random concordance
- Confidence intervals (95%) for correlation coefficient

**FR-5.3: Statistical Tests**
- Pearson correlation test
- Wilcoxon rank-sum test (high-sim vs random pairs)
- Bootstrap confidence intervals for correlation
- Significance threshold: p < 0.05

### FR-6: Visualization

**FR-6.1: Required Figure - Gate Metrics**
- Bar chart: High-similarity concordance vs target (0.65) and random baseline
- Correlation coefficient display (r value with p-value annotation)
- Save to: `h-m2/figures/gate_metrics_comparison.png`

**FR-6.2: Correlation Analysis Figures**
- Scatter plot: Embedding similarity (x) vs Behavioral concordance (y) with regression line
- Box plot: Concordance distribution by similarity bin (low/med/high)
- Heatmap: Similarity matrix with concordance values overlaid for sampled pairs
- Bar chart: Mean concordance by bin with error bars and baseline reference

**FR-6.3: Figure Generation**
- All figures auto-generated during experiment execution
- Save to: `h-m2/figures/` directory
- Use matplotlib/seaborn for consistency

### FR-7: Experiment Execution

**FR-7.1: Analysis Pipeline**
- Load h-m1 embeddings and ETHICS dataset
- Compute similarity matrix
- Sample user pairs (stratified)
- Measure concordance for all pairs
- Compute correlation and statistical tests
- Generate all visualizations

**FR-7.2: No Training Required**
- This is an analysis experiment, not a training experiment
- Uses frozen embeddings from h-m1
- Computational requirement: CPU sufficient (no GPU needed)
- Execution time: ~5-10 minutes

**FR-7.3: Results Reporting**
- Summary table: correlation coefficient, p-value, concordance by bin
- Statistical test results
- Visualizations saved to figures folder
- Embeddings and concordance data saved for reproducibility

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42) for pair sampling
- Deterministic operations throughout analysis
- Save sampling indices for reproducibility
- Version control for h-m1 checkpoint path

### NFR-2: Computational Efficiency
- CPU-only execution (no GPU needed)
- Similarity matrix computation: vectorized operations
- Memory efficient: ~4GB for embeddings + similarity matrix
- Execution time: < 15 minutes total

### NFR-3: Code Quality
- Modular design: separate similarity, concordance, correlation modules
- Type hints for all function signatures
- Docstrings for all classes and functions
- Unit tests for concordance calculation

### NFR-4: Data Integrity
- Verify h-m1 checkpoint exists and is loadable
- Check ETHICS dataset integrity
- Validate user pair sampling stratification
- Assert similarity and concordance array alignment

---

## Dependencies

### External Dependencies

**Datasets**:
- ETHICS Benchmark (`hendrycks/ethics`) from HuggingFace
- Cache path: `docs/youra_research/20260419_bi_align/.data_cache/datasets/huggingface`

**Pretrained Models**:
- h-m1 embeddings (pre-trained, frozen)
- Checkpoint path: `../h-m1/checkpoints/best_model.pt`

**Python Libraries**:
- PyTorch >= 1.10 (for loading embeddings)
- Transformers >= 4.20 (for RoBERTa if needed)
- datasets (HuggingFace)
- scipy (pearsonr, spearmanr, wilcoxon)
- numpy, pandas
- matplotlib, seaborn
- scikit-learn (optional, for additional metrics)

### Internal Dependencies

**Prerequisite Hypothesis**:
- h-m1 (COMPLETED, PASS)
- Required artifacts: embeddings checkpoint from h-m1
- Reuse: RoBERTa encoder architecture, embedding dimension

**Codebase**:
- Reuse embedding loading utilities from h-m1
- Adapt ETHICS dataset loading for concordance measurement
- New: Correlation analysis module (not in h-m1)

---

## Data Specifications

### Input Data Schema

**h-m1 Embeddings**:
```python
{
    "embeddings": np.ndarray,          # (N_users, 256) - user value embeddings
    "user_ids": np.ndarray,            # (N_users,) - user identifiers
    "metadata": {
        "model_type": str,             # "contrastive"
        "seed": int,                   # Best seed from h-m1
        "embedding_dim": int           # 128 or 256
    }
}
```

**ETHICS Record**:
```python
{
    "scenario": str,                   # Moral reasoning scenario
    "label": int,                      # 0 or 1 (acceptable/unacceptable)
    "category": str                    # deontology, virtue, justice, etc.
}
```

**User Pair Sample**:
```python
{
    "user_i": int,                     # User index i
    "user_j": int,                     # User index j
    "similarity": float,               # Cosine similarity
    "bin": str                         # "low", "medium", or "high"
}
```

### Output Data Schema

**Concordance Results**:
```python
{
    "user_i": int,
    "user_j": int,
    "similarity": float,
    "concordance": float,              # Agreement rate on ETHICS tasks
    "bin": str,                        # Similarity bin
    "n_tasks": int                     # Number of tasks compared
}
```

**Correlation Results**:
```python
{
    "pearson_r": float,                # Correlation coefficient
    "pearson_p": float,                # p-value
    "spearman_r": float,               # Rank correlation
    "spearman_p": float,
    "high_sim_concordance": {
        "mean": float,
        "std": float,
        "n_pairs": int
    },
    "random_baseline_concordance": {
        "mean": float,
        "std": float,
        "n_pairs": int
    }
}
```

---

## Success Criteria

### Gate Criteria (MUST_WORK)

1. **Primary Metric**: Pearson correlation r > 0.5
2. **Statistical Significance**: p < 0.05
3. **High-Similarity Concordance**: Mean concordance for high-sim pairs (>0.7) > 0.65
4. **Baseline Comparison**: High-sim concordance > Random baseline + 0.10

**Gate Result**:
- PASS: All 4 criteria met → h-m2 validated, unlock h-m3
- FAIL: Any criterion not met → Embeddings may not capture decision-relevant values

### Secondary Criteria

5. **Monotonic Relationship**: Low < Medium < High concordance across bins
6. **Effect Robustness**: Spearman rank correlation > 0.45
7. **Category Consistency**: Positive correlation across all 5 ETHICS categories

---

## Risks and Mitigations

### Technical Risks

**Risk 1: h-m1 checkpoint loading failure**
- Mitigation: Verify checkpoint path before analysis
- Fallback: Use alternative seed checkpoint from h-m1

**Risk 2: Insufficient user diversity**
- Mitigation: Use h-m1's 60 demographic groups as users
- Validation: Check similarity distribution covers full range [0, 1]

**Risk 3: ETHICS dataset download failures**
- Mitigation: Retry logic (3 attempts, 15s delay), offline cache
- Fallback: Use cached version from h-m1 if available

### Methodological Risks

**Risk 4: Spurious correlation from confounds**
- Mitigation: Compare against random baseline, bootstrap confidence intervals
- Validation: Check correlation holds across ETHICS categories

**Risk 5: Sample size too small (1000 pairs)**
- Mitigation: 1000 pairs provides adequate power for r > 0.5 detection
- Fallback: Increase sample size to 2000 if p-value borderline

---

## Out of Scope

- Training new models (use frozen h-m1 embeddings)
- Multi-dataset evaluation (only ETHICS)
- Real user study validation
- Causal intervention experiments
- Embedding dimension analysis
- Temperature sensitivity analysis
- Cross-domain generalization testing

---

## Appendix

### Reference Implementations

- Contrastive Behavioral Similarity Embeddings (ICLR 2021)
- Data-Centric RLHF: Embedding similarity analysis methodology
- ETHICS Benchmark: https://github.com/hendrycks/ethics

### Glossary

- **Embedding Similarity**: Cosine similarity between user value embeddings
- **Behavioral Concordance**: Agreement rate on identical moral reasoning tasks
- **Correlation Coefficient**: Pearson r measuring linear relationship strength
- **High-Similarity Pairs**: User pairs with cosine similarity > 0.7

### Version History

- v1.0 (2026-04-19): Initial PRD for Phase 3 implementation planning
