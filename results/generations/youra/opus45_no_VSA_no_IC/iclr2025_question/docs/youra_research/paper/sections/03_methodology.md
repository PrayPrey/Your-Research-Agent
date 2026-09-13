# Methodology

## Overview

Our goal is to test whether uncertainty probes generalize across LLM families. If uncertainty encoding is architecture-invariant, a probe trained on one model's hidden states should maintain predictive power on another model's states. We operationalize this through a 3×3 transfer matrix: train three probes (one per model family), evaluate each on all three models' hidden states, and measure the AUROC gap between same-family and cross-family evaluation.

The key insight guiding our design is that if transformers encode uncertainty in a shared geometric structure, linear probes should transfer — and for models with different hidden dimensions, affine alignment should recover the mapping.

## Semantic Entropy Probe Architecture

Following Kossen et al. [2024], we train a linear classifier on hidden states:

**Hidden state extraction.** Given input tokens $x_{1:T}$, we extract the hidden state $h_l \in \mathbb{R}^d$ at layer $l$ and the last token position (Second-Last Token, SLT). We select $l$ at approximately 2/3 depth: layer 21 for 32-layer models (Llama-3, Mistral), layer 18 for the 28-layer model (Qwen-2).

**Probe training.** We train a logistic regression classifier:
$$P(\text{high-SE} \mid h) = \sigma(w^\top h + b)$$
where $w \in \mathbb{R}^d$ and $b \in \mathbb{R}$ are learned parameters. Training labels are binarized semantic entropy: questions with SE above the median are labeled 1 (high uncertainty), others 0. We use sklearn's LogisticRegression with L2 regularization ($C=1.0$) and LBFGS solver.

**Rationale.** Linear probes are sufficient because prior work shows truthfulness signals are approximately linear in hidden-state space [arxiv 2606.02628]. Logistic regression provides calibrated probabilities and fast training on ~650 examples.

## Cross-Family Transfer Protocol

To evaluate whether probes generalize, we construct a transfer matrix:

1. **Extract hidden states.** For each of three models $\{m_1, m_2, m_3\}$, extract hidden states from train and validation splits of TruthfulQA (80/20 split, 653/164 questions). Cache states to disk to enable multi-probe evaluation without reloading models.

2. **Train per-model probes.** Train three SEPs, each on its respective model's training hidden states.

3. **Evaluate all pairs.** For each (source model, target model) pair:
   - If dimensions match: apply source probe directly to target hidden states
   - If dimensions mismatch: apply affine alignment before evaluation

4. **Compute transfer gaps.** The gap for pair $(i, j)$ is:
$$\text{gap}_{i \to j} = \text{AUROC}_{i \to i} - \text{AUROC}_{i \to j}$$
where $\text{AUROC}_{i \to j}$ denotes the AUROC of probe trained on model $i$, evaluated on model $j$ hidden states.

**Success criterion.** Following our pre-registered threshold, transfer succeeds if all gaps are below 0.10 and mean gap is below 0.05.

## Affine Alignment for Dimension Mismatch

Qwen-2-7B has hidden dimension 3584, while Llama-3-8B and Mistral-7B have dimension 4096. Direct probe application fails because the weight vector has wrong size. We address this with affine alignment:

Given paired hidden states from source model (dimension $d_s$) and target model (dimension $d_t$), we learn a mapping:
$$\hat{h}_s = h_t W + b$$
where $W \in \mathbb{R}^{d_t \times d_s}$ and $b \in \mathbb{R}^{d_s}$.

**Fitting.** We solve the least-squares problem on training data:
$$(W^*, b^*) = \arg\min_{W,b} \|H_s - (H_t W + b)\|_F^2$$
where $H_s \in \mathbb{R}^{n \times d_s}$ and $H_t \in \mathbb{R}^{n \times d_t}$ are matrices of paired hidden states.

**Rationale.** Affine alignment is sufficient if the uncertainty subspace is preserved under linear transformation. The least-squares solution is the maximum-likelihood estimator under Gaussian noise. We fit aligners on training split and apply to validation split, preventing overfitting.

## Implementation Details

**Models.** We use instruction-tuned models from HuggingFace: Meta-Llama-3-8B-Instruct, Mistral-7B-Instruct-v0.2, Qwen2-7B-Instruct. All models run in float16 on NVIDIA H100 GPUs.

**Layer selection.** We extract from layer $\lfloor \text{frac} \times n_\text{layers} \rfloor$ with $\text{frac} = 2/3$, following findings that mid-to-upper layers best encode truthfulness [arxiv 2606.02628]. This gives layer 21 for Llama/Mistral (32 layers) and layer 18 for Qwen (28 layers).

**Caching.** Hidden states are cached as NumPy arrays, reducing GPU memory pressure and enabling rapid iteration on transfer experiments.

**Reproducibility.** All experiments use seed 42 for train/val splits. Code and cached states will be released upon publication.

## Algorithm Summary

```
Algorithm: Cross-Family Transfer Evaluation

Input: TruthfulQA questions Q, models M = {Llama, Mistral, Qwen}
Output: Transfer matrix T ∈ R^{3×3}, gap statistics

1. Split Q into train (80%) and val (20%)
2. For each model m ∈ M:
     Extract hidden states H_m^train, H_m^val at layer 2/3 depth
     Cache to disk
3. Compute SE labels on train split, binarize at median
4. For each model m ∈ M:
     Train SEP probe p_m on H_m^train
5. For each pair (source, target) with dimension mismatch:
     Fit AffineAligner on H_source^train, H_target^train
6. For each (i, j) ∈ M × M:
     If dim_i == dim_j: T[i,j] = AUROC(p_i, H_j^val)
     Else: T[i,j] = AUROC(p_i, align(H_j^val))
7. Compute gaps: gap[i,j] = T[i,i] - T[i,j]
8. Return T, mean(gaps), max(gaps)
```
