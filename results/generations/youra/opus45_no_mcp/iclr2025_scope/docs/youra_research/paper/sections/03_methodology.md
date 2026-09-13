# Methodology

Our approach systematically measures loss landscape geometry and LoRA adaptation efficiency across task types under controlled architecture conversion. The design follows directly from our key insight: if landscape geometry mediates task-dependent transformation, then measuring sharpness, effective rank, and performance across the task spectrum should reveal predictable patterns.

## Architecture Conversion Protocol

We convert Transformer models to Mamba using SSM-attention duality. For controlled comparison, we apply matched LoRA configurations:

- **LoRA rank**: 16
- **LoRA alpha**: 32
- **Transformer targets**: q_proj, k_proj, v_proj, o_proj
- **Mamba targets**: in_proj, out_proj (structurally analogous projections)
- **Dropout**: 0.0

This isocapacity design ensures performance differences reflect architectural effects rather than parameter count confounds.

## Loss Landscape Measurement

We measure landscape geometry using SAM-style perturbation analysis:

**Sharpness metric**: Maximum loss increase under epsilon-norm perturbation
$$\text{sharpness} = \max_{\|\delta\| \leq \epsilon} L(w + \delta) - L(w)$$

with ε=0.05 and 100 batch samples. Higher sharpness indicates more curved landscape around the minimum.

**Eigenvalue analysis**: PyHessian-style eigenvalue extraction from loss Hessian reveals landscape curvature structure. KL divergence between eigenvalue distributions quantifies landscape geometry change:
$$D_{KL}(P_{\text{Transformer}} \| P_{\text{Mamba}})$$

## LoRA Effective Rank Computation

We quantify adaptation complexity via SVD analysis of learned LoRA matrices:

**Effective rank**: Number of singular values capturing 90% of total energy
$$r_{\text{eff}} = \min \{k : \sum_{i=1}^{k} \sigma_i^2 / \sum_{j} \sigma_j^2 \geq 0.90\}$$

Lower effective rank indicates the adaptation found a simpler, lower-dimensional solution — our proxy for adaptation efficiency.

## Task Spectrum Design

We select four benchmarks spanning retrieval density:

| Benchmark | Retrieval Density | Samples | Task Type |
|-----------|------------------|---------|-----------|
| GSM8K | 0.1 (low) | 1,319 | Sequential reasoning |
| MMLU | 0.5 (medium) | 14,042 | Mixed |
| HotpotQA | 0.7 (high) | 7,405 | Multi-hop retrieval |
| Natural Questions | 0.9 (very high) | 3,610 | Factual retrieval |

Retrieval density operationalizes the ratio of retrieval-dependent to reasoning-dependent operations. Expert assignment follows the principle: GSM8K requires step-by-step reasoning with minimal fact lookup; NQ requires locating specific facts with minimal reasoning.

## Experimental Variables

**Independent Variables**:
- Architecture type: Transformer (baseline) vs. Mamba-converted
- Task retrieval density: 0.1 to 0.9 continuous

**Dependent Variables**:
- Task accuracy post-adaptation
- Adaptation sharpness (SAM metric)
- LoRA effective rank
- Accuracy delta (Mamba - Transformer)

**Controlled Variables**:
- Total trainable parameters (matched LoRA configuration)
- Training hyperparameters (AdamW, lr=2e-4, cosine schedule)
- Evaluation protocol (same test splits, metrics)

## Hypothesis Verification Structure

We verify the causal chain through ordered experiments:

1. **H-E1 (Existence)**: Does task-dependent pattern exist?
   - Gate: GSM8K delta ≥-5%, NQ delta ≤-15%, Spearman ρ>0.5

2. **H-M1 (Mechanism 1)**: Does conversion change landscape?
   - Gate: |sharpness_delta| > 10%, KL divergence > 0.1

3. **H-M2 (Mechanism 2)**: Does SSM favor sequential tasks?
   - Gate: sharpness_ratio(sequential/retrieval) < 0.8

4. **H-M3 (Mechanism 3)**: Does landscape predict LoRA efficiency?
   - Gate: Spearman ρ(sharpness, rank) > 0.5

5. **H-M4 (Mechanism 4)**: Does retrieval density predict transformation?
   - Gate: Spearman ρ(density, delta) > 0.7

This MUST_WORK gate structure ensures each mechanism step is verified before claiming the complete causal chain.
