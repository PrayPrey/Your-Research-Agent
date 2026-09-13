# Research Proposal: OSLO: Optimized Sparse and Low-rank Allocation for Parameter-Efficient Fine-Tuning via Reconstruction Error Sensitivity

## 1. Introduction

### 1.1 Background

The emergence of large language models (LLMs) has revolutionized natural language processing, achieving unprecedented performance across diverse tasks. However, the computational demands of fine-tuning these models—often containing billions of parameters—present significant challenges for practical deployment. Parameter-efficient fine-tuning (PEFT) methods have emerged as a critical solution, enabling adaptation of pre-trained models while updating only a small fraction of parameters.

Low-Rank Adaptation (LoRA) has become the dominant PEFT paradigm, decomposing weight updates into low-rank matrices to dramatically reduce trainable parameters. Despite its success, LoRA and its variants employ uniform capacity allocation across transformer layers, assigning identical rank budgets regardless of each layer's contribution to task adaptation. This uniform strategy ignores a fundamental insight: different layers exhibit vastly different adaptation requirements and sensitivities to parameter changes.

Recent empirical studies have revealed that reconstruction error—the discrepancy between adapted weights and optimal full fine-tuning weights—correlates strongly with downstream task performance. Methods like HASSLE-free have demonstrated 12% perplexity improvements by optimizing within-layer decomposition based on reconstruction error. Similarly, LoSA introduced Relative Magnitude of Importance (RMI) heuristics for layer-wise rank adjustment, achieving substantial perplexity reductions. However, these approaches rely on heuristic allocation strategies rather than principled optimization frameworks.

### 1.2 Research Gap and Motivation

A critical gap exists in current PEFT methodology: no principled method optimally distributes sparse and low-rank capacity across layers under fixed parameter budgets. This limitation leaves an estimated 15-30% potential performance improvement unrealized. The core challenge lies in developing a theoretically grounded allocation strategy that:

1. Quantifies each layer's sensitivity to additional parameters
2. Optimally distributes budget proportionally to adaptation potential
3. Jointly optimizes sparse and low-rank components within allocated budgets
4. Scales efficiently to billion-parameter models

### 1.3 Research Objectives

This research proposes OSLO (Optimized Sparse and Low-rank Allocation), a novel framework that addresses these challenges through reconstruction error sensitivity optimization. Our specific objectives are:

**Primary Objective:** Develop and validate a principled layer-wise allocation algorithm that achieves ≥15% perplexity reduction compared to uniform allocation under identical parameter budgets.

**Secondary Objectives:**
- Establish theoretical foundations linking reconstruction error sensitivity to downstream performance
- Demonstrate the causal mechanism through which sensitivity-based allocation improves fine-tuning
- Achieve superior performance compared to existing heuristic methods (LoSA, RoseLoRA, SaRA)
- Enable efficient deployment under computational constraints (1-5% parameter budgets)

### 1.4 Significance

This research advances both theoretical understanding and practical methodology in PEFT:

**Theoretical Contribution:** OSLO establishes principled allocation criteria grounded in reconstruction error sensitivity, moving beyond heuristic approaches to optimization-based budget distribution.

**Practical Impact:** By achieving superior performance under fixed parameter constraints, OSLO enables more efficient deployment of LLMs in resource-constrained environments, democratizing access to state-of-the-art language models.

**Methodological Innovation:** The combination of gradient-based sensitivity estimation with alternating minimization for joint sparse-low-rank optimization represents a novel algorithmic contribution applicable beyond fine-tuning.

## 2. Methodology

### 2.1 Problem Formulation

Consider a pre-trained transformer model with $L$ layers, where each layer $l$ has weight matrix $W_l \in \mathbb{R}^{d_l \times d_l}$. The goal of PEFT is to learn weight updates $\Delta W_l$ such that the adapted weights $W_l + \Delta W_l$ minimize task loss while constraining total trainable parameters.

OSLO decomposes each weight update as:

$$\Delta W_l = S_l + L_l R_l^T$$

where $S_l \in \mathbb{R}^{d_l \times d_l}$ is a sparse matrix with at most $k_l$ non-zero entries, and $L_l \in \mathbb{R}^{d_l \times r_l}$, $R_l \in \mathbb{R}^{d_l \times r_l}$ form a rank-$r_l$ decomposition.

The total parameter budget constraint is:

$$\sum_{l=1}^{L} \left( k_l + 2 d_l r_l \right) \leq P$$

where $P$ is the fixed total parameter budget (typically 1-5% of model parameters).

### 2.2 OSLO Algorithm

OSLO operates in four sequential phases:

#### Phase 1: Sensitivity Estimation

For each layer $l$, we compute the reconstruction error sensitivity:

$$\sigma_l = \frac{\partial E_l}{\partial b_l}$$

where $E_l = \|W_l + \Delta W_l - W_l^*\|_F^2$ is the layer-wise reconstruction error, $W_l^*$ represents the optimal full fine-tuning weights (estimated via a small calibration set), and $b_l$ represents the allocated budget for layer $l$.

In practice, we approximate this gradient using finite differences:

$$\sigma_l \approx \frac{E_l(b_l + \epsilon) - E_l(b_l - \epsilon)}{2\epsilon}$$

where $\epsilon$ is a small perturbation. For computational efficiency, we use a calibration dataset of 1,000 samples to estimate $W_l^*$ via one epoch of full fine-tuning on a subset of layers.

#### Phase 2: Layer Importance Ranking

Layers are ranked by their normalized sensitivity scores:

$$\tilde{\sigma}_l = \frac{\sigma_l}{\sum_{j=1}^{L} \sigma_j}$$

This normalization ensures that allocation proportions sum to unity and provides interpretable importance weights.

#### Phase 3: Budget Allocation

The total budget $P$ is distributed proportionally to sensitivity:

$$b_l = \tilde{\sigma}_l \cdot P$$

This allocation is then decomposed into sparse and low-rank components. We introduce a layer-wise mixing coefficient $\alpha_l \in [0, 1]$ that determines the sparse-to-low-rank ratio:

$$k_l = \alpha_l \cdot b_l, \quad 2 d_l r_l = (1 - \alpha_l) \cdot b_l$$

The mixing coefficient is optimized jointly with the decomposition in Phase 4.

#### Phase 4: Per-Layer Alternating Minimization

For each layer $l$, we solve the following optimization problem:

$$\min_{S_l, L_l, R_l} \|W_l + S_l + L_l R_l^T - W_l^*\|_F^2$$

subject to $\|S_l\|_0 \leq k_l$ and $\text{rank}(L_l R_l^T) \leq r_l$.

We employ alternating minimization with the following update rules:

**Sparse Update:** Given fixed $L_l, R_l$, solve:

$$S_l^{(t+1)} = \mathcal{H}_{k_l}\left(W_l^* - W_l - L_l^{(t)} R_l^{(t)T}\right)$$

where $\mathcal{H}_{k_l}(\cdot)$ is the hard thresholding operator that retains the $k_l$ largest magnitude entries.

**Low-Rank Update:** Given fixed $S_l$, solve:

$$L_l^{(t+1)}, R_l^{(t+1)} = \text{SVD}_{r_l}\left(W_l^* - W_l - S_l^{(t+1)}\right)$$

where $\text{SVD}_{r_l}(\cdot)$ computes the rank-$r_l$ truncated singular value decomposition.

The alternating updates continue until convergence:

$$\|E_l^{(t+1)} - E_l^{(t)}\| < \delta$$

where $\delta = 10^{-6}$ is the convergence threshold.

### 2.3 Theoretical Analysis

**Convergence Guarantee:** Under standard assumptions (bounded weights, Lipschitz continuity), the alternating minimization converges to a stationary point. Following Bertsimas et al. (2023), the convergence rate is:

$$E_l^{(t)} - E_l^* \leq \mathcal{O}\left(\frac{1}{t}\right)$$

**Approximation Bound:** The OSLO decomposition achieves reconstruction error bounded by:

$$\|W_l + \Delta W_l - W_l^*\|_F \leq \sigma_{k_l+1}(W_l^* - W_l) + \sigma_{r_l+1}(W_l^* - W_l - S_l)$$

where $\sigma_i(\cdot)$ denotes the $i$-th singular value.

### 2.4 Experimental Design

#### 2.4.1 Models and Datasets

**Primary Models:**
- LLaMA-7B (primary evaluation)
- LLaMA-13B (scalability validation)

**Datasets:**
- Fine-tuning: Alpaca instruction-tuning dataset (52K examples)
- Evaluation: WikiText-2 (perplexity), MMLU (accuracy), HellaSwag (accuracy)

#### 2.4.2 Baselines

| Method | Description | Source |
|--------|-------------|--------|
| Uniform LoRA | Standard LoRA with uniform rank across layers | Hu et al. (2022) |
| LoSA | RMI-based heuristic rank allocation | Huang et al. (2025) |
| HASSLE-free | Reconstruction error within-layer optimization | Makni et al. (2025) |
| RoseLoRA | Knowledge editing via low-rank adaptation | (2024) |
| SaRA | Nuclear-norm regularized low-rank | (2024-2025) |

#### 2.4.3 Experimental Conditions

**Parameter Budget Levels:** 1%, 2%, 3%, 4%, 5% of total model parameters

**Random Seeds:** 5 independent seeds per condition

**Hyperparameters:**
- Learning rate: $1 \times 10^{-4}$
- Batch size: 16
- Training epochs: 3
- Optimizer: AdamW with weight decay 0.01

**Total Experimental Runs:** 25 runs per method (5 seeds × 5 budget levels)

#### 2.4.4 Evaluation Metrics

**Primary Metric:**
- WikiText-2 Perplexity: $\text{PPL} = \exp\left(-\frac{1}{N}\sum_{i=1}^{N} \log p(x_i | x_{<i})\right)$

**Secondary Metrics:**
- MMLU 5-shot accuracy
- HellaSwag accuracy
- Training time (GPU hours)
- Memory consumption (GB)

**Mechanism Validation Metrics:**
- Sensitivity-allocation correlation: Pearson's $r$ between $\sigma_l$ and $b_l$
- Reconstruction error reduction per layer
- Convergence iterations per layer

#### 2.4.5 Statistical Analysis

**Primary Hypothesis Test:**
- Test: Paired t-test comparing OSLO vs. uniform allocation
- Significance level: $\alpha = 0.05$ (one-tailed)
- Effect size: Cohen's $d$
- Required power: 0.8

**Sample Size Justification:**
With expected effect size $d = 0.6$ (medium-large), $\alpha = 0.05$, and power = 0.8, the required sample size is $n \geq 25$ runs, which our design satisfies.

**Reporting Format:**
- Mean difference with 95% confidence interval
- Cohen's $d$ effect size
- $p$-value

### 2.5 Ablation Studies

To validate the causal mechanism, we conduct the following ablations:

**A1: Sensitivity Estimation Method**
- Compare gradient-based sensitivity vs. random allocation vs. uniform allocation
- Validates Step 1 → Step 2 of causal chain

**A2: Allocation Strategy**
- Compare proportional allocation vs. top-k allocation vs. threshold-based allocation
- Validates Step 2 → Step 3 of causal chain

**A3: Optimization Method**
- Compare alternating minimization vs. joint optimization vs. sequential optimization
- Validates Step 3 → Step 4 of causal chain

**A4: Sparse-Low-Rank Ratio**
- Vary $\alpha_l$ from 0 (pure low-rank) to 1 (pure sparse)
- Identifies optimal decomposition balance

### 2.6 Implementation Details

**Computational Requirements:**
- Sensitivity estimation: 2-4 hours on 8×A100 GPUs for LLaMA-7B
- Full fine-tuning: 4-6 hours per configuration
- Total compute: ~500 GPU hours for complete experiments

**Software Stack:**
- PyTorch 2.0+
- Hugging Face Transformers
- PEFT library (modified for OSLO)
- Custom alternating minimization implementation

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):**
We predict OSLO will achieve ≥15% perplexity reduction on WikiText-2 compared to uniform LoRA allocation. Based on prior work (HASSLE-free achieving 12%, LoSA achieving substantial reductions), our principled optimization approach should exceed these heuristic methods.

**Quantitative Predictions:**

| Method | WikiText-2 PPL (2% budget) | Relative Improvement |
|--------|---------------------------|---------------------|
| Uniform LoRA | ~8.5 | Baseline |
| LoSA | ~7.8 | ~8% |
| HASSLE-free | ~7.5 | ~12% |
| **OSLO (predicted)** | **~7.0** | **~18%** |

**Mechanism Validation (P2):**
We expect strong correlation ($r > 0.7$, $p < 0.01$) between layer sensitivity scores and allocated budgets, confirming that the proposed causal mechanism operates as designed.

**Comparative Advantage (P3):**
OSLO should outperform LoSA by at least 5% additional perplexity reduction, demonstrating the advantage of gradient-based sensitivity over RMI heuristics.

### 3.2 Falsification Criteria

The hypothesis will be **rejected** if:
1. Perplexity reduction < 5% compared to uniform allocation
2. Sensitivity-allocation correlation $r < 0.3$
3. OSLO performs worse than LoSA on any benchmark

### 3.3 Broader Impact

**Scientific Contribution:**
- Establishes theoretical foundations for principled PEFT allocation
- Provides empirical evidence for reconstruction error as optimization target
- Advances understanding of layer-wise adaptation in transformers

**Practical Applications:**
- Enables efficient fine-tuning under strict computational constraints
- Reduces barrier to LLM deployment in resource-limited settings
- Provides actionable guidelines for PEFT practitioners

**Future Directions:**
- Extension to encoder-decoder and vision transformer architectures
- Dynamic allocation during training (online OSLO)
- Integration with quantization for compound efficiency gains
- Theoretical analysis of attention layer convergence

### 3.4 Limitations and Risks

**Known Limitations:**
- Convergence proof limited to linear/MLP layers; attention layers require empirical validation
- Sensitivity estimation overhead may not scale to 100B+ models
- Current formulation assumes fixed architecture

**Mitigation Strategies:**
- Empirical convergence monitoring for attention layers
- Approximate sensitivity estimation via sampling for larger models
- Modular design enabling architecture-specific extensions

### 3.5 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1 | Weeks 1-4 | Implementation and debugging |
| Phase 2 | Weeks 5-8 | Primary experiments (LLaMA-7B) |
| Phase 3 | Weeks 9-10 | Scalability experiments (LLaMA-13B) |
| Phase 4 | Weeks 11-12 | Ablation studies and analysis |
| Phase 5 | Weeks 13-14 | Paper writing and submission |

This research proposal presents OSLO as a principled advancement in parameter-efficient fine-tuning, combining theoretical rigor with practical applicability to address a critical gap in current methodology.