# Experiment Design: H-M3

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** The distortion is geometric (affects probability landscape shape) rather than scalar (temperature-like rescaling), evidenced by Brier decomposition showing Refinement degradation in instruct models.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests geometric vs scalar nature of confidence distortion.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m2 COMPLETED with PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (COMPLETED - β_percentile attenuation confirmed)

### Gate Condition
- **Type:** SHOULD_WORK
- **Primary:** Refinement_instruct < Refinement_base (discrimination degrades)
- **Secondary:** Reliability may improve (temperature-like calibration effect coexists)
- **Failure Response:** IF fails → Accept scalar rescaling as sufficient explanation; revise theoretical claims

---

## Continuation Context

This hypothesis builds on the chain:
- **H-E1 (PASS):** AUROC discriminative degradation exists (Qwen: +0.0222, Mistral: +0.0385)
- **H-M1 (PASS):** E[margin|incorrect] inflation confirmed (Qwen 3.06x, Mistral 16.79x)
- **H-M2 (PASS):** β_percentile attenuation confirmed (Qwen Δβ=0.76, Mistral Δβ=0.63)

H-M3 tests whether this distortion is:
- **Geometric:** Affects the SHAPE of the probability landscape (Refinement degrades)
- **Scalar:** Temperature-like rescaling (only Reliability changes)

### Previous Hypothesis Results (if applicable)
From H-M2 04_validation.md:
- Qwen: β_base=2.22, β_inst=1.47, Δβ=0.76 (p<0.001), effect_size=15.3
- Mistral: β_base=1.56, β_inst=0.93, Δβ=0.63 (p<0.001), effect_size=17.0
- Both families show statistically significant monotonicity attenuation
- Confidence-correctness relationship is weaker in instruct models

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "Brier score decomposition calibration"**
- Limited direct results for Brier decomposition in LLM context
- Found calibration-related papers (hf.co/papers/2305.14314) but not specific to Murphy decomposition
- Key insight: Brier decomposition is well-established in forecasting literature but less common in LLM calibration studies

**Query 2: "LLM confidence calibration reliability refinement"**
- Found references to quantization and model compression (not directly relevant)
- Key insight: LLM calibration research focuses primarily on ECE rather than Brier decomposition components

**Query 3: "probability calibration proper scoring rule"**
- Limited direct results
- Key insight: Proper scoring rules are fundamental to calibration but Brier-specific decomposition is specialized

**Archon KB Summary:**
- Brier decomposition (Murphy 1973) is a classical statistical method not heavily represented in recent LLM literature
- Implementation will need to follow original statistical definitions rather than LLM-specific libraries
- This represents a NOVEL application of classical calibration theory to LLM confidence analysis

### Archon Code Examples

**Query 1: "Brier score Python sklearn"**
- sklearn.metrics.brier_score_loss available for basic Brier score
- No direct Murphy decomposition implementation found in Archon KB
- Implementation approach: Custom decomposition following Murphy (1973) formulation

**Code Pattern Insight:**
```python
from sklearn.metrics import brier_score_loss
# Basic Brier score available, but decomposition requires custom implementation
brier = brier_score_loss(y_true, y_prob)
```

### Exa GitHub Implementations

**Query 1: "Brier score decomposition Murphy reliability refinement Python implementation"**

**Repository 1**: [tensorflow/probability](https://tensorflow.google.cn/probability/api_docs/python/tfp/stats/brier_decomposition)
- **URL**: https://tensorflow.google.cn/probability/api_docs/python/tfp/stats/brier_decomposition
- **Relevance**: Official TensorFlow Probability implementation of Brier decomposition
- **Architecture**: `tfp.stats.brier_decomposition(labels, logits, name=None)`
- **Key Code**:
  ```python
  import tensorflow_probability as tfp
  uncertainty, resolution, reliability = tfp.stats.brier_decomposition(labels, logits)
  # Score = Uncertainty - Resolution + Reliability
  ```
- **Decomposition Formula**:
  - Uncertainty: generalized entropy of average predictive distribution
  - Resolution: generalized variance of individual predictive distributions (HIGHER = BETTER)
  - Reliability: miscalibration measure (LOWER = BETTER calibrated)
- **Note**: Returns (uncertainty, resolution, reliability) - uses logits input

**Repository 2**: [google-research/google-research](https://github.com/google-research/google-research/blob/master/uq_benchmark_2019/metrics_lib.py)
- **URL**: https://github.com/google-research/google-research/blob/master/uq_benchmark_2019/metrics_lib.py
- **Relevance**: Google Research uncertainty quantification benchmark - reference implementation
- **Architecture**: Binning-based decomposition following Murphy (1973)
- **Key Insight**: Decomposition requires binning continuous probability outputs into discrete bins
- **Binning Strategy**: Top-class probability bins (C bins where C = number of classes)

**Repository 3**: [dholzmueller/probmetrics](https://github.com/dholzmueller/probmetrics)
- **URL**: https://github.com/dholzmueller/probmetrics
- **Relevance**: PyTorch-based classification metrics with Brier decomposition
- **Architecture**: Supports refinement and calibration error decomposition
- **Key Code**:
  ```python
  from probmetrics.metrics import Metrics
  metrics = Metrics.from_names([
      'brier',
      'refinement_brier_ts-mix_all',
      'calib-err_brier_ts-mix_all',
  ])
  ```
- **Note**: Decomposition via temperature scaling mixture approach

**Repository 4**: [flimao/briercalc](https://github.com/flimao/briercalc)
- **URL**: https://github.com/flimao/briercalc
- **Relevance**: Dedicated Brier score decomposition for multiple classes
- **Features**: Brier scores, Brier skill scores, calibration, resolution, uncertainty
- **License**: MIT

**Query 2: "LLM calibration Brier score decomposition PyTorch GitHub"**

**Repository 5**: [appier-research/llm-calibration](https://github.com/appier-research/llm-calibration) ⭐ Very Recent (2026)
- **URL**: https://github.com/appier-research/llm-calibration
- **Relevance**: HIGHLY RELEVANT - LLM calibration research repository
- **Paper**: "On Calibration of Large Language Models: From Response To Capability"
- **Models Tested**: GPT variants, Qwen, Mistral
- **Datasets**: TriviaQA, GSM8K, MATH-500
- **Key Methods**: Response calibration vs capability calibration framework

**Repository 6**: [NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark](https://github.com/NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark)
- **URL**: https://github.com/NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark
- **Relevance**: LLM calibration benchmark with Brier Score analysis
- **Models**: Llama-3.2, Gemma-7b, TinyLlama, Qwen, Mistral
- **Datasets**: GSM8K, BoolQ, TruthfulQA, CommonSenseQA
- **Metrics**: ECE, MCE, Brier Score, reliability diagrams

**scikit-learn Issue #23767**: [Additive Score Decomposition](https://github.com/scikit-learn/scikit-learn/issues/23767)
- **Status**: Open feature request
- **Relevance**: Community discussion with implementation snippets
- **Key Code Pattern**:
  ```python
  import numpy as np
  from sklearn.isotonic import IsotonicRegression

  def score_decompose(target, pred_probs, scoring_function):
      # Murphy decomposition: SCORE = MSC - DSC + UNC
      # MSC = miscalibration (reliability)
      # DSC = discrimination (resolution)
      # UNC = uncertainty
      ...
  ```
- **Reference**: Siegert (2017) "Simplifying and generalising Murphy's Brier score decomposition"

**Murphy Decomposition Formula** (from academic sources):
```
BS = REL - RES + UNC

where:
  REL = Σ(nk/n)(fk - ȳk)²  # Reliability (calibration error)
  RES = Σ(nk/n)(ȳk - ȳ)²   # Resolution (discrimination)
  UNC = ȳ(1 - ȳ)           # Uncertainty (base rate entropy)
```

**Serena Analysis Needed**: false
- Code is clear - mathematical formula with standard binning approach
- Reference implementations available in TensorFlow Probability and Google Research

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

- No official implementation found for Brier decomposition in LLM calibration context
- Murphy (1973) decomposition is a mathematical formula, not a complex algorithm
- Implementation from first principles is appropriate and straightforward

**Recommended Implementation Path:**
- Primary: Custom implementation following Murphy (1973) decomposition formula
- Fallback: Adapt netcal library calibration metrics if needed
- Justification: Classical statistical method with clear mathematical definition; custom implementation ensures correctness and interpretability

### Code Analysis (Serena MCP)

**Project Memory: failure_h-m2_run1**
- Different pipeline context (CoT entropy hypothesis)
- Not directly applicable to current Brier decomposition task

**Project Memory: buildingtrust_alignment_calibration_2026**
- Relevant prior work on alignment-induced calibration changes
- Key insight: "Cache reuse dramatically accelerates hypothesis chain" - can reuse H-E1 cached inference results
- Proven components: logit extraction, margin computation infrastructure exists

*Skipped* - Code from search results was sufficiently clear. Murphy (1973) Brier decomposition is a well-documented mathematical formula with reference implementations in TensorFlow Probability (`tfp.stats.brier_decomposition`) and Google Research (`uq_benchmark_2019/metrics_lib.py`). The implementation requires standard binning of probability predictions, which can be adapted from H-E1's existing logit processing infrastructure.

---

## Experiment Specification

### Dataset

**Dataset:** H-E1 Cached Inference Results (reuse)
**Type:** standard (MMLU)
**Source:** `h-e1/cache/` directory

**Continuation Experiment Notes:**
- **Reusing H-E1 cached data** - enables controlled comparison within hypothesis chain
- **Rationale:** Same samples used in H-E1, H-M1, H-M2 ensure fair comparison of decomposition components
- **No new model inference required** - this is a statistical reanalysis

**Original Dataset (from H-E1):**
- **Name:** MMLU (Massive Multitask Language Understanding)
- **Size:** 14,042 test samples
- **Format:** Multiple-choice QA (4 options per question)
- **Domains:** 57 subjects across STEM, humanities, social sciences, other

**Cached Data Structure:**
```
h-e1/cache/
├── qwen_base_logits.npy       # Shape: (14042, 4) - logits for each option
├── qwen_instruct_logits.npy   # Shape: (14042, 4)
├── mistral_base_logits.npy    # Shape: (14042, 4)
├── mistral_instruct_logits.npy # Shape: (14042, 4)
├── labels.npy                 # Shape: (14042,) - correct answer indices
└── metadata.json              # Sample IDs, domains, etc.
```

**Loading Information** (for Phase 4 download):
- Method: File Load (cached)
- Identifier: `h-e1/cache/`
- Code:
  ```python
  import numpy as np

  # Load cached logits and labels
  logits_base = np.load("../h-e1/cache/qwen_base_logits.npy")
  logits_inst = np.load("../h-e1/cache/qwen_instruct_logits.npy")
  labels = np.load("../h-e1/cache/labels.npy")
  ```

### Models

#### Baseline Model

**Architecture:** N/A - Statistical Reanalysis (no model inference)
**Type:** Pre-computed logits from H-E1

**Model Pairs Used (from H-E1 cache):**

| Family | Base Model | Instruct Model | Status |
|--------|------------|----------------|--------|
| Qwen | Qwen/Qwen2.5-7B | Qwen/Qwen2.5-7B-Instruct | ✅ Cached |
| Mistral | mistralai/Mistral-7B-v0.3 | mistralai/Mistral-7B-Instruct-v0.3 | ✅ Cached |

**Loading Information** (for Phase 4 download):
- Method: No model loading required (using cached logits)
- Identifier: N/A
- Code:
  ```python
  # No model loading - use cached logits from H-E1
  # Logits already extracted and saved in .npy format
  ```

#### Proposed Model

**Architecture:** Statistical Analysis Module (no neural network training)
**Analysis Type:** Murphy Brier Score Decomposition

This is a **statistical reanalysis experiment** - no model training or inference required.
The "proposed model" is the Brier decomposition analysis applied to instruct model predictions.
The "baseline model" is the same analysis applied to base model predictions.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Murphy (1973) Brier Score Decomposition
# Based on: TensorFlow Probability tfp.stats.brier_decomposition
# Reference: Murphy, A.H. (1973). "A New Vector Partition of the Probability Score"

import numpy as np
from scipy.special import softmax

def murphy_brier_decomposition(logits: np.ndarray, labels: np.ndarray, n_bins: int = 15):
    """
    Decompose Brier score into Reliability, Resolution, and Uncertainty.

    Args:
        logits: (N, C) raw logits for N samples and C classes
        labels: (N,) true class indices
        n_bins: number of bins for calibration (default: 15)

    Returns:
        dict with keys: brier_score, reliability, resolution, uncertainty
    """
    N, C = logits.shape
    probs = softmax(logits, axis=1)  # Convert logits to probabilities

    # One-hot encode labels
    y_onehot = np.eye(C)[labels]  # (N, C)

    # Brier score = mean squared error
    brier_score = np.mean(np.sum((probs - y_onehot) ** 2, axis=1))

    # Base rate (climatological probability)
    y_bar = np.mean(y_onehot, axis=0)  # (C,)

    # Uncertainty: ȳ(1 - ȳ) summed over classes
    uncertainty = np.sum(y_bar * (1 - y_bar))

    # Bin by top-class probability for calibration analysis
    top_probs = np.max(probs, axis=1)  # (N,)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(top_probs, bin_edges[1:-1])  # (N,)

    reliability = 0.0
    resolution = 0.0

    for k in range(n_bins):
        mask = (bin_indices == k)
        n_k = np.sum(mask)
        if n_k == 0:
            continue

        # Mean prediction in bin k
        f_k = np.mean(probs[mask], axis=0)  # (C,)
        # Mean outcome in bin k
        y_bar_k = np.mean(y_onehot[mask], axis=0)  # (C,)

        # Reliability: sum over k of (n_k/n) * ||f_k - y_bar_k||²
        reliability += (n_k / N) * np.sum((f_k - y_bar_k) ** 2)

        # Resolution: sum over k of (n_k/n) * ||y_bar_k - y_bar||²
        resolution += (n_k / N) * np.sum((y_bar_k - y_bar) ** 2)

    return {
        'brier_score': brier_score,
        'reliability': reliability,   # Lower is better (calibration)
        'resolution': resolution,     # Higher is better (discrimination)
        'uncertainty': uncertainty,   # Base rate entropy (constant)
        'refinement': resolution      # Alias: refinement = resolution
    }

# Verification: BS ≈ REL - RES + UNC (within numerical tolerance)
```

### Training Protocol

**N/A - Statistical Reanalysis Experiment**

This experiment performs statistical analysis on pre-computed logits. No model training required.

**Analysis Protocol:**
1. Load cached logits from H-E1 (`h-e1/cache/`)
2. Apply Murphy Brier decomposition to each model (base and instruct)
3. Compare decomposition components between base and instruct
4. Bootstrap confidence intervals for component differences

**Computational Parameters:**
- **Bootstrap iterations:** 1000 (for confidence intervals)
- **Number of bins:** 15 (standard for calibration analysis)
- **Random seed:** 42 (for reproducibility)

**Source:** Continuation from H-E1/H-M1/H-M2 chain using same cached inference results

### Evaluation

**Primary Metrics (from Brier Decomposition):**

| Metric | Definition | Direction | Hypothesis Test |
|--------|------------|-----------|-----------------|
| **Refinement (Resolution)** | Σ(nk/n)(ȳk - ȳ)² | Higher = Better discrimination | Refinement_inst < Refinement_base |
| **Reliability** | Σ(nk/n)(fk - ȳk)² | Lower = Better calibration | May improve in instruct models |
| **Brier Score** | REL - RES + UNC | Lower = Better overall | Compare changes |
| **Uncertainty** | ȳ(1 - ȳ) | Constant (base rate) | Should be equal |

**Success Criteria (SHOULD_WORK Gate):**
- **Primary:** Refinement_instruct < Refinement_base (discrimination degrades)
  - Direction must be consistent across BOTH model families (Qwen, Mistral)
  - Bootstrap 95% CI for difference should exclude zero
- **Secondary:** Reliability may improve (temperature-like calibration effect coexists)
  - Not required for gate pass, but informative for mechanism interpretation

**Statistical Testing:**
- Bootstrap paired difference test (n=1000 iterations)
- Report 95% confidence intervals for Δ_Refinement and Δ_Reliability
- p-value from bootstrap null distribution

**Expected Results (based on hypothesis chain):**
- Given H-M2 showed β_percentile attenuation (weaker confidence-correctness slope)
- Expect Refinement degradation as a consequence of distorted probability landscape
- Refinement measures how well predictions discriminate between outcomes

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (calibration decomposition)
- Library: numpy, scipy (softmax, bootstrap)
- Code:
  ```python
  from scipy.special import softmax
  from scipy.stats import bootstrap
  import numpy as np

  # Custom murphy_brier_decomposition function (defined above)
  # Bootstrap for confidence intervals:
  def compute_refinement_diff(indices):
      base_ref = murphy_brier_decomposition(logits_base[indices], labels[indices])['refinement']
      inst_ref = murphy_brier_decomposition(logits_inst[indices], labels[indices])['refinement']
      return base_ref - inst_ref  # Positive = base has higher refinement (hypothesis supported)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Brier Decomposition Bar Chart** (`figures/brier_decomposition_comparison.png`)
   - Grouped bars: Base vs Instruct for each family
   - Show Reliability, Resolution (Refinement), Uncertainty components
   - Error bars from bootstrap CIs

2. **Reliability Diagram** (`figures/reliability_diagram.png`)
   - Calibration curve: predicted probability vs observed frequency
   - 15 bins, separate curves for base and instruct
   - One subplot per model family

3. **Refinement Delta Forest Plot** (`figures/refinement_delta_forest.png`)
   - Effect size visualization across families
   - Point estimates with 95% CIs
   - Dashed line at zero (null hypothesis)

4. **Decomposition Verification Plot** (`figures/decomposition_verification.png`)
   - Scatter: BS_computed vs (REL - RES + UNC)
   - Should show perfect correlation (verify decomposition correctness)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Refinement_instruct < Refinement_base for both model families

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Brier Score Decomposition Calibration
- **Type**: Knowledge base article
- **Query Used**: "Brier score decomposition calibration"
- **Relevance**: Limited direct results for LLM context
- **Key Insights**:
  - Brier decomposition established in forecasting literature
  - Less common in LLM calibration (novelty opportunity)
- **Used For**: Confirming implementation approach

**Source 2**: LLM Calibration Literature
- **Type**: Knowledge base article
- **Query Used**: "LLM confidence calibration reliability refinement"
- **Relevance**: LLM calibration research focuses on ECE not Brier decomposition
- **Key Insights**:
  - ECE is dominant metric in LLM calibration
  - Brier decomposition represents novel analysis angle
- **Used For**: Positioning novelty of approach

### B. GitHub Implementations (Exa)

**Repository 1**: tensorflow/probability
- **URL**: https://tensorflow.google.cn/probability/api_docs/python/tfp/stats/brier_decomposition
- **Query Used**: "Brier score decomposition Murphy reliability refinement Python implementation"
- **Relevance**: Official TensorFlow Probability Brier decomposition
- **Key Code**:
  ```python
  import tensorflow_probability as tfp
  uncertainty, resolution, reliability = tfp.stats.brier_decomposition(labels, logits)
  ```
- **Configuration Extracted**: Decomposition formula, input format (logits)
- **Used For**: Reference for decomposition algorithm

**Repository 2**: google-research/uq_benchmark_2019
- **URL**: https://github.com/google-research/google-research/blob/master/uq_benchmark_2019/metrics_lib.py
- **Query Used**: Same as above
- **Relevance**: Google Research uncertainty quantification benchmark
- **Key Insight**: Binning-based decomposition following Murphy (1973)
- **Used For**: Binning strategy for continuous probabilities

**Repository 3**: appier-research/llm-calibration
- **URL**: https://github.com/appier-research/llm-calibration
- **Query Used**: "LLM calibration Brier score decomposition PyTorch GitHub"
- **Relevance**: Recent (2026) LLM calibration research with Qwen, Mistral models
- **Paper**: "On Calibration of Large Language Models: From Response To Capability"
- **Used For**: Validation that our model selection aligns with recent LLM calibration work

**Repository 4**: NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark
- **URL**: https://github.com/NIKHIL0VERMA/LLM-Confidence-Calibration-Benchmark
- **Query Used**: Same as above
- **Relevance**: LLM calibration benchmark with Brier Score
- **Models**: Includes Qwen, Mistral families
- **Used For**: Confirming our model selection and metrics

**Repository 5**: scikit-learn Issue #23767
- **URL**: https://github.com/scikit-learn/scikit-learn/issues/23767
- **Query Used**: Same as above
- **Relevance**: Community discussion with implementation snippets
- **Reference Paper**: Siegert (2017) "Simplifying and generalising Murphy's Brier score decomposition"
- **Used For**: Implementation pattern guidance

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

Murphy (1973) Brier decomposition is a well-documented mathematical formula with
reference implementations in TensorFlow Probability and Google Research. The
implementation requires standard binning of probability predictions.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports - H-E1, H-M1, H-M2
- **Files**:
  - `h-e1/04_validation.md` - AUROC discriminative degradation
  - `h-m1/04_validation.md` - Conditional margin inflation
  - `h-m2/04_validation.md` - Percentile-normalized monotonicity attenuation
- **Reused Components**:
  - Dataset: H-E1 cached inference results (14,042 MMLU samples)
  - Models: Qwen2.5-7B, Mistral-7B (base + instruct pairs)
  - Analysis infrastructure: Logit processing, bootstrap CI computation
- **Why Reused**: Enables controlled experiment within hypothesis chain

**Serena Memory**: global/phase45/buildingtrust_alignment_calibration_2026
- **Key Insight**: "Cache reuse dramatically accelerates hypothesis chain"
- **Used For**: Confirming cache reuse strategy

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous Hypothesis | H-E1 cache (D.1) |
| Model pairs | Previous Hypothesis | H-E1 validation (D.1) |
| Brier decomposition algorithm | GitHub | TensorFlow Probability (B.1) |
| Binning strategy | GitHub | Google Research (B.2) |
| Murphy formula | Academic | Murphy (1973) via (B.5) |
| Pseudo-code | GitHub + Academic | B.1, B.5 combined |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | H-M3 specification |
| Bootstrap methodology | Previous Hypothesis | H-M1, H-M2 code |

### F. Academic References

1. **Murphy, A.H. (1973)**. "A New Vector Partition of the Probability Score." *Journal of Applied Meteorology*, 12:595-600.
   - Original Brier score decomposition into Reliability, Resolution, Uncertainty

2. **Siegert, S. (2017)**. "Simplifying and generalising Murphy's Brier score decomposition." *Quarterly Journal of the Royal Meteorological Society*.
   - Simplified derivation: REL = B(p) - B(q), RES = B(r) - B(q), UNC = B(r)

3. **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K.Q. (2017)**. "On Calibration of Modern Neural Networks." *ICML*.
   - Temperature scaling and calibration in neural networks

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- Archon knowledge base searched (limited direct results for Brier decomposition)
- Proceeding with Exa GitHub search for implementations

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
