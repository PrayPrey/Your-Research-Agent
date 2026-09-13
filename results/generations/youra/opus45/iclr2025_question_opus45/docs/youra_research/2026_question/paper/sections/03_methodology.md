# Methodology

We designed SE-Distilled Probes (SEDP) to extend Semantic Entropy Probes with similarity-augmented training, hypothesizing that semantic similarity structure would improve cross-model transfer. This section describes our approach and the rationale behind key design decisions.

## Overview

SEDP learns to predict semantic entropy from a single forward pass by combining two information sources: (1) hidden state representations from the LLM, and (2) semantic similarity features computed on generated response sets. The intuition is that similarity structure—being computed on output text rather than internal representations—may provide model-agnostic regularization that enables transfer across different LLMs.

The training pipeline consists of four stages:
1. **Response Generation**: Generate N=20 diverse responses per question using temperature sampling
2. **SE Label Computation**: Cluster responses via NLI entailment and compute true semantic entropy
3. **Feature Extraction**: Extract hidden states and similarity features
4. **Probe Training**: Train logistic regression to predict SE from combined features

## Semantic Entropy Labels

We compute ground-truth SE labels following the established protocol. For each question, we generate N=20 responses using temperature T=0.7 and cluster them by semantic equivalence. Two responses are considered equivalent if DeBERTa-v3-large-MNLI predicts bidirectional entailment with probability exceeding 0.5.

Given clusters C₁, C₂, ..., Cₖ with sizes n₁, n₂, ..., nₖ, the semantic entropy is:

$$H_{SE} = -\sum_{i=1}^{k} p_i \log p_i$$

where $p_i = n_i / N$ is the proportion of responses in cluster i. High SE indicates diverse, potentially uncertain responses; low SE indicates consistent responses.

For probe training, we binarize SE labels using the median threshold, creating a balanced classification task: predict whether a question has high or low semantic uncertainty.

## Hidden State Extraction

We extract hidden states from layer 25 of Llama-3-8B-Instruct (of 32 total layers) at the Token-Before-Generation (TBG) position—the last token of the prompt immediately before generation begins.

**Rationale**: Middle-to-late layers are recommended by the SEP literature as containing the most SE-relevant information. Layer 25 falls in this range. The TBG position captures the model's "state of mind" just before committing to a response.

**Alternative considered**: We could have tested multiple layers (20-31) and token positions (TBG, SLT, pooling). Budget constraints limited us to a single configuration, which we selected following published guidance.

## Similarity Feature Extraction

For each question's response set, we compute semantic similarity features:

1. Embed all N=20 responses using sentence-transformers (all-MiniLM-L6-v2)
2. Compute pairwise cosine similarity matrix S ∈ ℝ^(N×N)
3. Extract summary statistics from upper triangle: [mean, std, min, max]

This yields a 4-dimensional similarity feature vector per question. The features capture response diversity: high mean similarity indicates consistent responses (low uncertainty), while high variance suggests mixed agreement.

**Rationale**: Similarity structure is computed on output text, not internal representations, making it potentially model-agnostic. If similarity features help on one model, they may transfer to others—the motivation for our cross-model transfer hypothesis.

## Probe Architecture

### SEP Baseline

The baseline Semantic Entropy Probe is a logistic regression classifier:

$$\hat{y} = \sigma(W_h \cdot h + b)$$

where h ∈ ℝ^4096 is the hidden state and σ is the sigmoid function. We use sklearn's LogisticRegression with L2 regularization (C=1.0) and LBFGS optimizer.

### SEDP (Proposed)

SEDP extends SEP by concatenating similarity features:

$$\hat{y} = \sigma(W \cdot [h; s] + b)$$

where s ∈ ℝ^4 is the similarity feature vector and [h; s] ∈ ℝ^4100 is the concatenation. The same logistic regression architecture is used.

**Note on feature balance**: Hidden states (4096 dimensions) vastly outnumber similarity features (4 dimensions). This imbalance may limit the influence of similarity features, though we hypothesized the complementary information would still help.

## Training Protocol

We train on TruthfulQA with an 80/20 train/test split (~653/164 questions), using fixed random seed 42 for reproducibility. Training uses sklearn's LBFGS optimizer with max_iter=1000.

No hyperparameter search is performed—this is an existence proof (PoC) to verify whether the approach works at all. If the basic configuration succeeds, systematic optimization would follow; our failure at this stage makes optimization moot.

## Evaluation Metrics

We evaluate using two complementary metrics:

**Spearman Correlation (ρ)**: Measures rank correlation between predicted SE probabilities and true continuous SE values. Our MUST_WORK threshold is ρ ≥ 0.3; our target is ρ ≥ 0.7.

**AUROC**: Measures binary classification performance for detecting high-uncertainty questions. Random baseline is 0.50; published SEP results report ~0.85.

Statistical significance is assessed via p-values for Spearman correlation; we require p < 0.05 for significance.
