---
stepsCompleted: ["step-01", "step-02", "step-03", "step-04", "step-05", "step-06", "step-07", "step-08"]
phase2c_status: "COMPLETED"
completed_at: "2026-03-18T01:55:00Z"
---

# Experiment Design: h-m1

**Date:** 2026-03-18
**Author:** Anonymous
**Hypothesis Statement:** Deep layers compress semantic information into low-rank operators with decreasing operator entropy, enabling bounded-state conversion
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanism operation.

---

## Workflow Status

**Verification State:** Phase 2C Complete - Experiment Design Specified
**Prerequisites Satisfied:** h-e1 (pending execution - h-m1 will be executed after h-e1)
**Gate Status:** MUST_WORK - If fails, state unbounded

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1

### Gate Condition
MUST_WORK gate - If hypothesis fails (mechanism validation negative), SSM state size must scale with sequence length, defeating linear efficiency. This would abort the entire conversion approach.

---

## Continuation Context

This hypothesis depends on h-e1 (Low-Rank Structure Existence) which must complete first.

**Execution Order:** h-e1 → h-m1 → h-m2 → h-m3 → h-m4

### Previous Hypothesis Results (if applicable)
None yet - h-e1 has not been executed. Once h-e1 completes, its findings (confirmed r_eff<256, entropy β<0) will inform this experiment's baseline expectations.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Low-Rank Attention Compression Experiments**
- Result 1: [HuggingFace PEFT - Low-Rank Adaptation (LoRA)](https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora)
  - Technique: Low-rank decomposition for attention weight matrices
  - Pattern: Decompose W into W = BA where B, A are low-rank
  - Relevance: Demonstrates attention matrices can be efficiently compressed
  - Note: LoRA focuses on fine-tuning, not pre-trained structure analysis

- Result 2: [OpenReview Paper](https://openreview.net/forum?id=gU58d5QeGv)
  - Context: Academic paper on low-rank methods
  - Relevance: May contain theoretical foundations for rank analysis
  - Note: Requires further investigation for specific methodologies

**Query 2: Operator Entropy in Transformer Layers**
- Result 1: [HuggingFace Diffusers - Transformer 2D](https://github.com/huggingface/diffusers/blob/main/src/diffusers/models/transformers/transformer_2d.py)
  - Architecture: Transformer block implementation
  - Relevance: Shows standard attention layer structure
  - Note: Diffusion model context, not language modeling

**Query 3: SVD Attention Matrix Analysis**
- Result 1: [OpenReview Analysis Paper](https://openreview.net/forum?id=M3Y74vmsMcY)
  - Context: Matrix analysis techniques in ML
  - Potential insights: SVD-based evaluation methods
  - Relevance: Moderate - general matrix analysis

**Key Insight:** Limited direct precedents for operator entropy measurement in language model layers. Most low-rank work focuses on compression/adaptation (LoRA), not mechanistic analysis of pre-trained structure.

### Archon Code Examples

**Query 1: SVD Rank Analysis in PyTorch**
- Limited direct examples found
- General PyTorch distributed operations available
- Note: Will need custom implementation for attention-specific SVD analysis

**Query 2: Attention Entropy Analysis**
- Result 1: [Flash Attention Citation](https://github.com/HazyResearch/flash-attention)
  - Reference: Flash Attention papers (Dao et al. 2022, 2024)
  - Relevance: Efficient attention computation, not entropy analysis
  - Code pattern: Optimized attention kernels

**Implementation Gap Identified:**
- No direct code examples for operator entropy measurement in Transformers
- Will require custom implementation combining:
  - PyTorch SVD: `torch.linalg.svd()`
  - Log-det covariance computation
  - Layer-wise analysis across depth

### Exa GitHub Implementations

**⚠️ Exa MCP Unavailable (HTTP 402 - API quota/billing issue after 3 retries)**

**Fallback Strategy:** Manual implementation required based on standard PyTorch patterns

**Relevant Repositories (from literature context):**

**Repository 1: LLaMA Model Access**
- **Source**: Meta AI / HuggingFace Transformers
- **URL**: https://huggingface.co/meta-llama/Llama-2-7b-hf
- **Relevance**: Pre-trained LLaMA-7B model for analysis
- **Loading Method**:
  ```python
  from transformers import AutoModel, AutoTokenizer
  model = AutoModel.from_pretrained("meta-llama/Llama-2-7b-hf")
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```
- **Key Insight**: Access attention weights via `model.model.layers[i].self_attn`

**Repository 2: SVD Analysis Pattern (Standard PyTorch)**
- **Method**: `torch.linalg.svd()`
- **Pattern**:
  ```python
  # Extract attention matrices Q, K, V from layer
  Q, K, V = layer.self_attn.q_proj.weight, layer.self_attn.k_proj.weight, layer.self_attn.v_proj.weight

  # Compute SVD for each matrix
  U, S, Vh = torch.linalg.svd(Q, full_matrices=False)

  # Calculate effective rank at 99% variance
  cumsum = torch.cumsum(S**2, dim=0)
  variance_threshold = 0.99 * cumsum[-1]
  r_eff = (cumsum < variance_threshold).sum() + 1
  ```

**Repository 3: Operator Entropy Computation**
- **Method**: Log-det covariance of principal vectors
- **Pattern**:
  ```python
  # Compute covariance matrix of top-k principal vectors
  k = min(256, U.shape[1])  # Top-k vectors
  U_k = U[:, :k]
  cov = U_k.T @ U_k / U_k.shape[0]

  # Compute entropy via log-determinant
  eigenvalues = torch.linalg.eigvalsh(cov)
  entropy = -torch.sum(eigenvalues * torch.log(eigenvalues + 1e-10))
  ```

**Serena Analysis Needed**: false (standard PyTorch operations, no custom layers)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOT a paper reproduction experiment - it's an analysis of existing models to validate a hypothesis about their internal structure.

**Recommended Implementation Path:**
- Primary: Custom implementation using PyTorch SVD and scipy regression (documented in Step 3)
- Fallback: N/A (standard operations, no fallback needed)
- Justification: No existing tools specifically analyze operator entropy in Transformers; requires custom implementation combining standard linear algebra operations

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear (standard PyTorch operations)

---

## Experiment Specification

### Dataset

**Dataset Name:** The Pile (calibration data for SVD/entropy analysis)
**Type:** standard (large-scale text corpus)
**Source:** EleutherAI via HuggingFace
**Statistics:** 825 GiB uncompressed, 22 diverse text sources
**Subset for Analysis:** 10M-10B token samples (per hypothesis calibration requirements)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"EleutherAI/pile"`
- Code:
  ```python
  from datasets import load_dataset
  # Load subset for calibration (streaming for memory efficiency)
  dataset = load_dataset("EleutherAI/pile", split="train", streaming=True)
  # Take N tokens as needed (10M, 100M, 1B, 10B)
  ```

**Preprocessing:**
- Tokenization: LLaMA tokenizer (SentencePiece, vocab=32000)
- Context window: Variable (8K, 16K, 32K, 64K, 128K for stability test)
- No augmentation (analysis of pre-trained model, not training)

**Dataset Type Verification:** ✅ CONFIRMED `standard` (real text data, not synthetic)

### Models

#### Baseline Model

**Model Name:** LLaMA-7B (primary), LLaMA-13B (secondary validation)
**Type:** decoder-only Transformer (autoregressive language model)
**Architecture:** 32 layers, enabling deep-layer analysis (L≥20)
**Parameters:** 7B (LLaMA-7B), 13B (LLaMA-13B)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"` or `"meta-llama/Llama-2-13b-hf"`
- Code:
  ```python
  from transformers import AutoModel, AutoTokenizer
  import torch

  model_id = "meta-llama/Llama-2-7b-hf"
  model = AutoModel.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
  tokenizer = AutoTokenizer.from_pretrained(model_id)

  # Access attention weights for layer i:
  # layer = model.model.layers[i]
  # Q = layer.self_attn.q_proj.weight
  # K = layer.self_attn.k_proj.weight
  # V = layer.self_attn.v_proj.weight
  ```

**Configuration:**
- Hidden size: 4096 (7B), 5120 (13B)
- Attention heads: 32 (7B), 40 (13B)
- Layers: 32 (both models)
- Context window: Originally 2048, extended to 128K for analysis

**Modifications for Hypothesis:** None (analyzing pre-trained model as-is)

#### Proposed Model

**Architecture:** LLaMA-7B (analysis target - no modification)

**Analysis Mechanism:**

This is an ANALYSIS experiment, not a training experiment. We analyze the pre-trained LLaMA-7B model to validate the low-rank compression mechanism hypothesis.

**Core Mechanism Implementation:**

```python
# Core Mechanism: SVD-Based Rank and Entropy Analysis
# Based on: Standard PyTorch linear algebra operations

import torch
import torch.nn as nn
from scipy.stats import linregress

class LayerRankEntropyAnalyzer:
    """
    Analyzes effective rank and operator entropy across Transformer layers.

    Tests hypothesis: Deep layers compress semantic information into low-rank
    operators with decreasing operator entropy.
    """
    def __init__(self, model, variance_threshold=0.99, top_k=256):
        self.model = model
        self.variance_threshold = variance_threshold
        self.top_k = top_k

    def analyze_layer(self, layer_idx):
        """
        Args:
            layer_idx: Layer index (0-31 for 32-layer model)
        Returns:
            dict: {r_eff, entropy, Q_rank, K_rank, V_rank}
        """
        layer = self.model.model.layers[layer_idx]

        # Extract attention weight matrices
        Q = layer.self_attn.q_proj.weight.detach()
        K = layer.self_attn.k_proj.weight.detach()
        V = layer.self_attn.v_proj.weight.detach()

        # Compute SVD for each matrix
        U_q, S_q, _ = torch.linalg.svd(Q, full_matrices=False)
        U_k, S_k, _ = torch.linalg.svd(K, full_matrices=False)
        U_v, S_v, _ = torch.linalg.svd(V, full_matrices=False)

        # Calculate effective rank (99% variance threshold)
        r_eff_q = self._effective_rank(S_q)
        r_eff_k = self._effective_rank(S_k)
        r_eff_v = self._effective_rank(S_v)
        r_eff = (r_eff_q + r_eff_k + r_eff_v) / 3

        # Compute operator entropy (log-det of covariance of top-k principal vectors)
        k = min(self.top_k, U_q.shape[1])
        U_combined = torch.cat([U_q[:, :k], U_k[:, :k], U_v[:, :k]], dim=1)
        cov = U_combined.T @ U_combined / U_combined.shape[0]

        # Add small epsilon for numerical stability
        eigenvalues = torch.linalg.eigvalsh(cov) + 1e-10
        entropy = -torch.sum(eigenvalues * torch.log(eigenvalues)).item()

        return {
            'layer': layer_idx,
            'r_eff': r_eff.item(),
            'entropy': entropy,
            'r_eff_q': r_eff_q.item(),
            'r_eff_k': r_eff_k.item(),
            'r_eff_v': r_eff_v.item()
        }

    def _effective_rank(self, singular_values):
        """Calculate effective rank at variance threshold"""
        cumsum = torch.cumsum(singular_values**2, dim=0)
        threshold = self.variance_threshold * cumsum[-1]
        r_eff = (cumsum < threshold).sum() + 1
        return r_eff

    def analyze_all_layers(self):
        """
        Analyze all 32 layers and compute regression statistics.

        Returns:
            dict: {layer_results, entropy_slope_beta, p_value, r_eff_deep_layers}
        """
        results = []
        for i in range(32):
            results.append(self.analyze_layer(i))

        # Extract entropy values for regression
        layers = [r['layer'] for r in results]
        entropies = [r['entropy'] for r in results]

        # Fit linear regression: entropy vs depth
        slope, intercept, r_value, p_value, std_err = linregress(layers, entropies)

        # Check deep layers (L≥20) for r_eff < 256
        deep_layers_reff = [r['r_eff'] for r in results if r['layer'] >= 20]

        return {
            'layer_results': results,
            'entropy_slope_beta': slope,
            'p_value': p_value,
            'r_squared': r_value**2,
            'deep_layers_reff': deep_layers_reff,
            'max_reff_deep': max(deep_layers_reff),
            'all_deep_below_256': all(r < 256 for r in deep_layers_reff)
        }

# Integration: Run after model loading, before any training
# This is a READ-ONLY analysis, no gradient computation needed
```

### Training Protocol

**⚠️ NOTE: This is an ANALYSIS experiment, not a training experiment**

No training occurs. The experiment analyzes pre-trained LLaMA-7B model weights.

**Analysis Protocol:**

**Model Loading:**
- Model: LLaMA-7B (pre-trained)
- Device: Single GPU (CUDA_VISIBLE_DEVICES set to empty GPU)
- Precision: float16 for memory efficiency
- Mode: `model.eval()` - no gradient computation

**Data Processing:**
- Dataset: The Pile (for context-length stability test)
- Context lengths tested: 8K, 16K, 32K, 64K, 128K tokens
- Batch size: 1 (single sample per context length)
- Samples per context length: 10 (for stability check)

**Analysis Steps:**
1. Load pre-trained LLaMA-7B
2. For each layer (0-31):
   - Extract Q, K, V weight matrices
   - Compute SVD
   - Calculate effective rank (99% variance)
   - Compute operator entropy (log-det covariance)
3. Statistical analysis:
   - Linear regression: entropy vs layer depth
   - Check: β < 0, p < 0.01
   - Verify: all L≥20 have r_eff < 256
4. Context-length stability test:
   - Repeat analysis on samples from different context lengths
   - Measure entropy variance across context lengths

**Seeds:** Not applicable (deterministic analysis of fixed weights)

**Computational Requirements:**
- GPU Memory: ~14GB (LLaMA-7B in float16)
- Runtime: ~5-10 minutes per model
- Storage: ~100MB for results (32 layers × metrics)

### Evaluation

**Primary Metrics:**

1. **Effective Rank (r_eff)**
   - Definition: Minimum number of singular values capturing 99% variance
   - Measurement: `r_eff = argmin_k(Σ_{i=1}^k σ_i^2 / Σ_{i=1}^n σ_i^2 ≥ 0.99)`
   - Success: r_eff < 256 for all layers L≥20

2. **Operator Entropy**
   - Definition: Log-determinant of covariance matrix of top-256 principal vectors
   - Measurement: `H = -Σ λ_i log(λ_i)` where λ_i are eigenvalues of cov(U_k)
   - Success: Monotonically decreasing with depth

3. **Entropy Slope (β)**
   - Definition: Linear regression slope of entropy vs layer depth
   - Measurement: `H = α + β*L + ε`, fit via OLS
   - Success: β < 0 with p < 0.01 (statistically significant negative slope)

4. **Context-Length Stability**
   - Definition: Entropy variance across context lengths 8K→128K
   - Measurement: `Var(entropy) across context lengths` for each layer
   - Success: Variance ≤ 1.2× baseline (entropy stable)

**Success Criteria** (ALL must pass for MECHANISM validation):
- ✅ All deep layers (L≥20) have r_eff < 256
- ✅ Entropy slope β < 0 with p < 0.01
- ✅ Entropy stable across context lengths (variance ≤ 1.2× baseline)

**Expected Results** (based on hypothesis):
- r_eff decreases with depth (semantic compression)
- Entropy decreases with depth (operator simplification)
- Stable across context (not artifact of sequence length)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Model analysis (not standard ML task)
- Library: PyTorch (torch.linalg.svd), SciPy (scipy.stats.linregress)
- Code:
  ```python
  import torch
  from scipy.stats import linregress

  # Effective rank
  U, S, Vh = torch.linalg.svd(matrix, full_matrices=False)
  cumsum = torch.cumsum(S**2, dim=0)
  r_eff = (cumsum < 0.99 * cumsum[-1]).sum() + 1

  # Entropy
  eigenvalues = torch.linalg.eigvalsh(cov_matrix)
  entropy = -torch.sum(eigenvalues * torch.log(eigenvalues + 1e-10))

  # Regression
  slope, intercept, r_value, p_value, std_err = linregress(layers, entropies)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on mechanism analysis hypothesis, the following visualizations effectively communicate results:

1. **Effective Rank vs Layer Depth** (Line plot)
   - X-axis: Layer index (0-31)
   - Y-axis: Effective rank (r_eff)
   - Horizontal line at r_eff=256 (threshold)
   - Shaded region for deep layers (L≥20)

2. **Operator Entropy vs Layer Depth** (Scatter + Regression line)
   - X-axis: Layer index (0-31)
   - Y-axis: Operator entropy
   - Regression line with β and p-value annotated
   - 95% confidence interval shaded

3. **Entropy Stability Heatmap** (Context-length × Layer)
   - X-axis: Context length (8K, 16K, 32K, 64K, 128K)
   - Y-axis: Layer index (0-31)
   - Color: Entropy value
   - Shows stability across context lengths

4. **Singular Value Distribution** (Multi-panel)
   - One panel per layer category (early/middle/deep)
   - X-axis: Singular value index
   - Y-axis: Singular value magnitude (log scale)
   - Shows compression in deep layers

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Pre-trained LLaMA model accessible with attention weight matrices | TRUE |
| Mechanism Isolatable | Analysis is read-only, no enable/disable needed | TRUE |
| Baseline Measurable | Random initialization or shallow layers (L<20) as baseline | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Transformer architecture with multi-layer attention
- Access to Q, K, V projection weight matrices
- Minimum 20 layers (for deep-layer analysis)

**Compatible Architectures:**
- ✅ LLaMA-7B/13B (32 layers)
- ✅ Any Transformer with ≥20 layers

**Incompatible Architectures:**
- ❌ Pure SSM models (no attention matrices to analyze)
- ❌ Shallow models (<20 layers)
- ❌ Models without accessible weight matrices

> ⚠️ If architecture is incompatible, Phase 4 MUST fail early with clear error message!

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "SVD computed for layer {i}, r_eff={value}, entropy={value}" | LayerRankEntropyAnalyzer.analyze_layer() |
| Tensor Shape | S (singular values) shape = (min(d_model, d_model),) | After torch.linalg.svd() |
| Metric Delta | r_eff decreases in deep layers vs early layers | analyze_all_layers() results |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(analysis_results):
    """
    Verify SVD analysis actually ran and computed metrics.

    Returns:
        bool: True if mechanism activated
        dict: Diagnostic info
    """
    indicators = {
        "svd_computed": len(analysis_results['layer_results']) == 32,
        "rank_measured": all('r_eff' in r for r in analysis_results['layer_results']),
        "entropy_measured": all('entropy' in r for r in analysis_results['layer_results']),
        "regression_computed": 'entropy_slope_beta' in analysis_results,
        "deep_layers_analyzed": len(analysis_results['deep_layers_reff']) == 12  # L≥20
    }

    all_active = all(indicators.values())

    return all_active, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| SVD failed | Missing singular values in results | FAIL: Numerical instability or wrong tensor format |
| No entropy values | entropy field missing | FAIL: Covariance computation failed |
| No regression | entropy_slope_beta missing | FAIL: Linear regression not computed |
| All ranks same | r_eff variance == 0 | FAIL: No compression detected (likely wrong matrices) |
| Architecture mismatch | model.model.layers not accessible | FAIL: Wrong model format |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | All 32 layers analyzed |
| Effect Measurable | r_eff varies across layers | std(r_eff) > 0 |
| Hypothesis Supported | β < 0, p < 0.01, r_eff < 256 for L≥20 | Linear regression + rank check |

**Hypothesis Support Threshold:**
- Entropy slope β < 0 with p < 0.01
- All layers L≥20 have r_eff < 256

**Hypothesis Support Metric:**
- Primary: entropy_slope_beta (must be negative with p<0.01)
- Secondary: max_reff_deep (must be <256)

---

## 🔬 Mechanism Validation Check

**Mechanism Pass Condition:**
1. ✅ Code runs without error
2. ✅ Mechanism operates as theorized (entropy β<0, p<0.01)
3. ✅ All deep layers (L≥20) have r_eff < 256
4. ✅ Effect stable across conditions (context lengths 8K→128K)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: [HuggingFace PEFT - Low-Rank Adaptation (LoRA)](https://huggingface.co/docs/peft/conceptual_guides/adapter#low-rank-adaptation-lora)
- **Type**: Knowledge base article
- **Query Used**: "low-rank attention compression experiment"
- **Relevance**: Demonstrates low-rank decomposition techniques for attention matrices
- **Key Insights**:
  - Attention matrices can be efficiently compressed via low-rank decomposition (W = BA)
  - LoRA focuses on fine-tuning, not structural analysis
  - Validates that attention matrices exhibit compressibility
- **Used For**: Conceptual validation of low-rank hypothesis

**Source A.2**: [PyTorch Transformers Documentation](https://huggingface.co/docs/transformers/index)
- **Type**: Official documentation
- **Query Used**: "The Pile dataset load HuggingFace"
- **Relevance**: Dataset loading methods
- **Key Insights**:
  - HuggingFace datasets library provides streaming access
  - The Pile available via `load_dataset("EleutherAI/pile")`
- **Used For**: Dataset loading specification

**Source A.3**: [HuggingFace BitsAndBytes Blog](https://huggingface.co/blog/4bit-transformers-bitsandbytes)
- **Type**: Technical blog post
- **Query Used**: "LLaMA model load pretrained"
- **Relevance**: Model loading best practices
- **Key Insights**:
  - Use `torch_dtype=torch.float16` for memory efficiency
  - `device_map="auto"` for automatic GPU allocation
- **Used For**: Model loading specification

### Archon Code Examples

**Code Source 1**: Limited direct examples found
- **Query Used**: "SVD rank PyTorch", "attention entropy analysis"
- **Key Findings**: No direct code examples for operator entropy measurement in Transformers
- **Used For**: Identified need for custom implementation

### B. GitHub Implementations (Exa)

**⚠️ Exa MCP Unavailable** (HTTP 402 - API quota/billing issue after 3 retries)

**Fallback Source B.1**: Meta AI / HuggingFace - LLaMA Model Access
- **URL**: https://huggingface.co/meta-llama/Llama-2-7b-hf
- **Query Used**: Manual fallback (Exa unavailable)
- **Relevance**: Official pre-trained LLaMA-7B model
- **Key Code**:
  ```python
  from transformers import AutoModel, AutoTokenizer
  model = AutoModel.from_pretrained("meta-llama/Llama-2-7b-hf")
  # Access attention weights: model.model.layers[i].self_attn.{q,k,v}_proj.weight
  ```
- **Used For**: Model loading, attention matrix access

**Fallback Source B.2**: PyTorch Documentation - SVD
- **URL**: https://pytorch.org/docs/stable/generated/torch.linalg.svd.html
- **Query Used**: Manual fallback (Exa unavailable)
- **Relevance**: Standard SVD computation
- **Key Code**:
  ```python
  U, S, Vh = torch.linalg.svd(matrix, full_matrices=False)
  # Effective rank: (cumsum(S**2) < 0.99 * cumsum(S**2)[-1]).sum() + 1
  ```
- **Used For**: SVD analysis pseudo-code, effective rank calculation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear (standard PyTorch operations)

### D. Previous Hypothesis Context

**Previous Context**: None - h-m1 depends on h-e1 which hasn't been executed yet.

**Note**: Once h-e1 completes, its findings (confirmed r_eff<256, entropy β<0) will serve as baseline expectations for h-m1.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (The Pile) | Phase 2A → 02b_context.md | Phase 2B Section 1.3 |
| Dataset loading method | Archon KB | Source A.2 (HuggingFace docs) |
| Model selection (LLaMA-7B) | Phase 2A → 02b_context.md | Phase 2B Section 1.3 |
| Model loading method | Archon KB + GitHub | A.3, B.1 (HuggingFace + Meta AI) |
| SVD implementation | GitHub (fallback) | B.2 (PyTorch docs) |
| Effective rank calculation | Custom derivation | Based on variance threshold method (standard practice) |
| Operator entropy formula | Custom derivation | Log-det covariance (information theory standard) |
| Linear regression | SciPy | scipy.stats.linregress (standard library) |
| Success criteria | Phase 2B | 02b_context.md Section "Success Criteria" |
| Mechanism verification protocol | Phase 2C Step 6 | Template instantiation |

---

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-18T01:31:00Z

### Workflow History for This Hypothesis

**Phase 2C Start:** 2026-03-18T01:45:00Z
**Status:** Experiment design COMPLETED
**Steps Completed:** step-01 through step-07
**MCP Tools Used:**
- Archon KB: 5 knowledge searches, 2 code searches
- Exa: Failed (HTTP 402), manual fallback used
- Serena: Skipped (not needed for standard operations)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
