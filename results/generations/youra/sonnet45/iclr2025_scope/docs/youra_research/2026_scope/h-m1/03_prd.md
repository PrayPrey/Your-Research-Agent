---
stepsCompleted: ["requirements", "data", "metrics", "dependencies"]
phase: "Phase 3 - Implementation Planning"
hypothesis_id: "h-m1"
generated_at: "2026-03-18T04:00:00Z"
---

# Product Requirements Document: h-m1 Low-Rank Compression Mechanism

**Hypothesis:** Deep layers compress semantic information into low-rank operators with decreasing operator entropy, enabling bounded-state conversion

**Type:** MECHANISM | **Gate:** MUST_WORK | **Prerequisites:** h-e1

---

## Executive Summary

This PRD specifies the implementation of a mechanism validation experiment to test whether deep Transformer layers (L≥20) exhibit low-rank compression with decreasing operator entropy. The experiment analyzes pre-trained LLaMA-7B/13B models using SVD-based rank analysis and entropy measurement across all 32 layers.

**Key Deliverables:**
- SVD-based layer analysis tool (LayerRankEntropyAnalyzer)
- Effective rank measurement (r_eff) for all layers
- Operator entropy computation and regression analysis
- Context-length stability validation (8K-128K tokens)
- Visualization suite (4 figures: rank vs depth, entropy regression, stability heatmap, singular value distribution)

**Success Criteria:**
- All deep layers (L≥20) have r_eff < 256
- Entropy slope β < 0 with p < 0.01
- Entropy stable across context lengths (variance ≤ 1.2× baseline)

---

## Problem Statement

### Context
The main hypothesis proposes hybrid SSM-Attention conversion for long-context efficiency. This mechanism hypothesis (h-m1) validates a critical assumption: that deep layers compress semantic information into low-rank operators, enabling bounded-state SSM conversion without scaling state size with sequence length.

### Challenge
Need to empirically validate that:
1. Deep Transformer layers (L≥20) exhibit effective rank r_eff < 256
2. Operator entropy decreases monotonically with depth (β < 0, p < 0.01)
3. These properties are stable across context lengths (not artifacts of short sequences)

### Significance
**Gate Type:** MUST_WORK - If this fails, SSM state size N must scale with sequence length, defeating linear efficiency and aborting the entire conversion approach.

---

## Functional Requirements

### FR-1: Model Loading and Initialization
**Priority:** P0 (Critical)

**Description:** Load pre-trained LLaMA-7B/13B models with access to attention weight matrices.

**Acceptance Criteria:**
- Load model from HuggingFace: `meta-llama/Llama-2-7b-hf`
- Use float16 precision for memory efficiency
- Access Q, K, V projection weights for all 32 layers
- Model in eval mode (no gradient computation)

**Dependencies:**
- HuggingFace Transformers library
- PyTorch with CUDA support
- Single GPU with ≥14GB memory

---

### FR-2: SVD-Based Rank Analysis
**Priority:** P0 (Critical)

**Description:** Compute effective rank (r_eff) for attention operators in each layer using SVD decomposition.

**Acceptance Criteria:**
- Perform SVD on Q, K, V weight matrices per layer
- Calculate effective rank at 99% variance threshold
- Verify r_eff < 256 for all layers L≥20
- Store per-layer rank metrics (r_eff_q, r_eff_k, r_eff_v, r_eff_avg)

**Method:**
```python
U, S, Vh = torch.linalg.svd(Q, full_matrices=False)
cumsum = torch.cumsum(S**2, dim=0)
r_eff = (cumsum < 0.99 * cumsum[-1]).sum() + 1
```

---

### FR-3: Operator Entropy Measurement
**Priority:** P0 (Critical)

**Description:** Compute operator entropy using log-determinant of covariance matrix of top-256 principal vectors.

**Acceptance Criteria:**
- Extract top-k principal vectors from combined Q/K/V SVD
- Compute covariance matrix
- Calculate entropy: H = -Σ λ_i log(λ_i)
- Store entropy value per layer

**Method:**
```python
k = min(256, U.shape[1])
U_combined = torch.cat([U_q[:, :k], U_k[:, :k], U_v[:, :k]], dim=1)
cov = U_combined.T @ U_combined / U_combined.shape[0]
eigenvalues = torch.linalg.eigvalsh(cov) + 1e-10
entropy = -torch.sum(eigenvalues * torch.log(eigenvalues))
```

---

### FR-4: Entropy Regression Analysis
**Priority:** P0 (Critical)

**Description:** Fit linear regression to test for monotonically decreasing entropy with depth.

**Acceptance Criteria:**
- Fit OLS regression: entropy = α + β*layer + ε
- Extract slope (β), p-value, R²
- Verify β < 0 with p < 0.01 (statistically significant negative slope)
- Display 95% confidence interval

**Dependencies:**
- SciPy: `scipy.stats.linregress`

---

### FR-5: Context-Length Stability Test
**Priority:** P0 (Critical)

**Description:** Validate entropy stability across context lengths 8K→128K tokens.

**Acceptance Criteria:**
- Test on context lengths: 8K, 16K, 32K, 64K, 128K
- Compute entropy for 10 samples per context length
- Measure variance across context lengths per layer
- Verify variance ≤ 1.2× baseline for all layers

**Data Source:**
- Dataset: The Pile (EleutherAI)
- Loading: HuggingFace datasets with streaming
- Samples: 10 per context length (50 total)

---

### FR-6: Visualization Suite
**Priority:** P1 (High)

**Description:** Generate 4 publication-quality figures for mechanism validation.

**Required Figures:**

**Figure 1:** Effective Rank vs Layer Depth
- Line plot: layer (x) vs r_eff (y)
- Horizontal line at r_eff=256 threshold
- Shaded region for deep layers (L≥20)

**Figure 2:** Operator Entropy vs Layer Depth
- Scatter plot with regression line
- Annotated with β, p-value, R²
- 95% confidence interval shaded

**Figure 3:** Entropy Stability Heatmap
- Heatmap: context length (x) × layer (y)
- Color: entropy value
- Shows stability across context lengths

**Figure 4:** Singular Value Distribution
- Multi-panel (early/middle/deep layers)
- Log-scale singular value magnitude
- Shows compression in deep layers

**Output Location:** `{hypothesis_folder}/figures/`

---

### FR-7: Mechanism Activation Verification
**Priority:** P0 (Critical)

**Description:** Verify that SVD analysis actually runs and produces valid metrics.

**Acceptance Criteria:**
- Log message per layer: "SVD computed for layer {i}, r_eff={value}, entropy={value}"
- Verify all 32 layers analyzed
- Check tensor shapes: S (singular values) = (min(d_model, d_model),)
- Confirm r_eff decreases in deep vs early layers

**Verification Function:**
```python
def verify_mechanism_activated(results):
    checks = {
        "svd_computed": len(results['layer_results']) == 32,
        "rank_measured": all('r_eff' in r for r in results['layer_results']),
        "entropy_measured": all('entropy' in r for r in results['layer_results']),
        "regression_computed": 'entropy_slope_beta' in results,
        "deep_layers_analyzed": len(results['deep_layers_reff']) == 12
    }
    return all(checks.values()), checks
```

---

## Non-Functional Requirements

### NFR-1: Performance
- **Runtime:** ≤10 minutes per model (LLaMA-7B)
- **GPU Memory:** ≤14GB (float16 precision)
- **Storage:** ~100MB for results (32 layers × metrics)

### NFR-2: Reproducibility
- **Deterministic:** Analysis is deterministic (no randomness)
- **Environment:** Single GPU, CUDA_VISIBLE_DEVICES set explicitly
- **Dependencies:** Pin PyTorch, Transformers, SciPy versions

### NFR-3: Extensibility
- **Model Support:** Compatible with any Transformer with ≥20 layers
- **Architecture Check:** Fail early if model incompatible
- **Metric Export:** Results in JSON/YAML format

### NFR-4: Error Handling
- **SVD Failure:** Detect numerical instability, log error
- **Architecture Mismatch:** Check `model.model.layers` accessible
- **Memory Overflow:** Use float16, process one layer at a time

---

## Data Specifications

### Input Data

**Dataset:** The Pile
- **Source:** EleutherAI via HuggingFace
- **Type:** Standard (real text data, not synthetic)
- **Size:** 825 GiB uncompressed, 22 diverse sources
- **Subset:** 10M-10B tokens (streaming for memory efficiency)

**Loading Method:**
```python
from datasets import load_dataset
dataset = load_dataset("EleutherAI/pile", split="train", streaming=True)
```

**Preprocessing:**
- Tokenization: LLaMA tokenizer (SentencePiece, vocab=32000)
- Context windows: 8K, 16K, 32K, 64K, 128K tokens
- No augmentation (read-only analysis)

### Model Specifications

**Primary Model:** LLaMA-7B
- **ID:** `meta-llama/Llama-2-7b-hf`
- **Layers:** 32
- **Hidden size:** 4096
- **Attention heads:** 32

**Secondary Model:** LLaMA-13B (validation)
- **ID:** `meta-llama/Llama-2-13b-hf`
- **Layers:** 32
- **Hidden size:** 5120
- **Attention heads:** 40

### Output Data

**Metrics File:** `{hypothesis_folder}/h-m1_analysis_results.json`

**Structure:**
```json
{
  "model": "LLaMA-7B",
  "layer_results": [
    {
      "layer": 0,
      "r_eff": 245.0,
      "r_eff_q": 243.0,
      "r_eff_k": 246.0,
      "r_eff_v": 246.0,
      "entropy": 5.234
    },
    ...
  ],
  "regression": {
    "entropy_slope_beta": -0.042,
    "p_value": 0.003,
    "r_squared": 0.89
  },
  "deep_layers": {
    "max_reff": 251.0,
    "all_below_256": true
  },
  "context_stability": {
    "max_variance": 0.08,
    "stable": true
  }
}
```

---

## Success Criteria

### Primary Criteria (ALL must pass)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Deep Layer Rank** | r_eff < 256 for all L≥20 | max(r_eff[20:32]) < 256 |
| **Entropy Slope** | β < 0 with p < 0.01 | Linear regression significance |
| **Context Stability** | Variance ≤ 1.2× baseline | Entropy variance across 8K-128K |

### Gate Validation

**MUST_WORK Gate:**
- If ANY criterion fails → Mechanism not validated
- Consequence: SSM state unbounded, conversion approach aborted
- Action: Document failure, escalate to Phase 4.5 synthesis

### Secondary Metrics (Informational)

- R² of entropy regression (target > 0.85)
- Rank decrease trend (early → middle → deep layers)
- Singular value decay rate (exponential expected)

---

## Dependencies

### System Dependencies
- **GPU:** Single CUDA GPU with ≥14GB memory
- **OS:** Linux (tested on Ubuntu 20.04+)
- **Python:** 3.8+

### Python Libraries
- **PyTorch:** 2.0+ (with CUDA support)
- **Transformers:** 4.30+ (HuggingFace)
- **Datasets:** 2.10+ (HuggingFace)
- **SciPy:** 1.10+ (linear regression)
- **NumPy:** 1.24+
- **Matplotlib:** 3.7+ (visualization)
- **Seaborn:** 0.12+ (heatmaps)

### Model Access
- **HuggingFace Account:** Required for LLaMA model access
- **Token:** Set `HF_TOKEN` environment variable
- **License:** Accept Meta LLaMA 2 license on HuggingFace

### External Services
- **HuggingFace Hub:** Model and dataset downloads
- **Archon MCP:** Task and project management
- **Serena MCP:** Code analysis (if needed)

---

## Out of Scope

### Explicitly NOT Included
- ❌ Model training or fine-tuning (read-only analysis)
- ❌ Gradient computation (eval mode only)
- ❌ SSM conversion implementation (future work in h-m2)
- ❌ Attention mechanism modification
- ❌ Multi-GPU distributed analysis
- ❌ Other model architectures (GPT, BERT, etc.)

### Future Work
- H-M2: Adapter distillation with Jacobian alignment
- H-M3: Calibration token sufficiency
- H-M4: End-to-end hybrid SSM-SWA efficiency

---

## Risks and Mitigations

### Risk R1: High-Rank Structure in Deep Layers
**Severity:** Critical
**Detection:** r_eff > 512 at L≥20
**Mitigation:** Early diagnostic on single layer before full analysis
**Impact:** Invalidates entire conversion approach (ABORT)

### Risk R2: Entropy Slope Non-Significant
**Severity:** High
**Detection:** p-value ≥ 0.01 or β ≥ 0
**Mitigation:** Test on multiple context lengths, verify data quality
**Impact:** Mechanism not validated (ABORT)

### Risk R3: Context-Length Instability
**Severity:** Medium
**Detection:** Variance > 1.2× baseline
**Mitigation:** Increase sample size, test on longer contexts
**Impact:** Limited applicability (DOCUMENT)

### Risk R4: Numerical Instability
**Severity:** Low
**Detection:** SVD fails, NaN values in results
**Mitigation:** Use float32 for SVD, add epsilon to log
**Impact:** Implementation bug (FIX)

---

## Timeline and Milestones

**Phase 3 Duration:** ~2-4 hours (architecture + logic + config design)

**Phase 4 Duration:** ~4-6 hours (implementation + validation)

### Milestones
1. **M1:** Core analyzer class implemented (LayerRankEntropyAnalyzer)
2. **M2:** Full 32-layer analysis runs without error
3. **M3:** Regression and stability tests complete
4. **M4:** Visualizations generated
5. **M5:** Gate criteria validated (PASS/FAIL determination)

---

## Appendix: Phase 2C Traceability

### Dataset Selection
- **Source:** Phase 2B Section 1.3 (Causal Step 1)
- **Validation:** Phase 2C Step 03 (Dataset specification)
- **Type:** standard (confirmed in 02c_experiment_brief.md line 195)

### Model Selection
- **Source:** Phase 2B Section 1.3 (LLaMA-7B/13B selection)
- **Validation:** Phase 2C Step 03 (Model specification)
- **Justification:** 32-layer architecture enables deep-layer analysis

### Metrics Selection
- **Source:** Phase 2B Section 2.2 (H-M1 verification protocol)
- **Validation:** Phase 2C Step 04 (Evaluation metrics)
- **Criteria:** r_eff, entropy slope, context stability

### Success Criteria
- **Source:** verification_state.yaml lines 52-55
- **Gate:** MUST_WORK (lines 46-47)
- **Action:** ABORT if fails (line 55)

---

*Generated by Phase 3 Step 02 - PRD Generation*
*Source: Phase 2C Experiment Brief (02c_experiment_brief.md)*
*Next: Step 03 - Architecture Agent*
