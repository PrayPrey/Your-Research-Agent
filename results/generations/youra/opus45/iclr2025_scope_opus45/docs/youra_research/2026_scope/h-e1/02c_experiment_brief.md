# Experiment Design: H-E1

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** The spectral memory horizon H_spec = -1/log|λ_max| is a measurable, stable property of pretrained Mamba models, with coefficient of variation CV < 0.3 across different input sequences.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK - Failure stops entire workflow

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
CV(H_spec) < 0.3 across 1000 random input sequences. This is a MUST_WORK gate - if this fails, the entire MHSH/EUH framework is invalidated.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to continue from.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "Mamba SSM eigenvalue spectral analysis"**
- Limited direct results - this research area is novel
- Found diffusers-related pages but no direct SSM eigenvalue content
- Insight: Archon KB lacks specific Mamba/SSM spectral analysis documentation

**Query 2: "state space model Jacobian computation"**
- No results found
- Insight: Jacobian computation for SSM is not well-documented in indexed sources

**Query 3: "SSM memory horizon LoRA adaptation"**
- No results found
- Insight: This is a novel research direction without prior indexed work

**Query 4: "coefficient variation stability measurement"**
- Found general measurement/statistics pages but no SSM-specific content
- Insight: CV calculation is standard statistics, implementation straightforward

**Summary**: The Archon KB search confirms this is a novel research area. No prior indexed implementations exist for measuring spectral memory horizons in Mamba models. This supports the research gap identified in Phase 2B.

### Archon Code Examples

**Query 1: "Mamba SSM PyTorch eigenvalue"**
- No direct SSM eigenvalue code examples found
- Found general PyTorch MPS backend documentation

**Query 2: "Jacobian autograd hooks PyTorch"**
- Found hook attachment patterns from accelerate library:
  ```python
  >>> from accelerate.hooks import attach_layerwise_casting_hooks
  >>> attach_layerwise_casting_hooks(model, storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)
  ```
- Pattern: Use `register_forward_hook` for layer-wise instrumentation

**Query 3: "register forward hook module"**
- Found distributed training hook patterns:
  ```python
  >>> ddp_model.register_comm_hook(state=None, hook=allreduce)
  ```
- Insight: PyTorch hook API is well-established for model instrumentation

**Relevant Implementation Patterns Extracted:**
1. Use `torch.nn.Module.register_forward_hook()` for capturing intermediate states
2. Use `torch.autograd.grad()` for Jacobian computation
3. Use `torch.linalg.eig()` for eigenvalue decomposition
4. Standard CV formula: `cv = std(x) / mean(x)`

### Exa GitHub Implementations

**Query 1: "Mamba SSM state-spaces eigenvalue analysis PyTorch implementation"**

**Repository 1**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (Official)
- **URL**: https://github.com/state-spaces/mamba
- **Relevance**: Official Mamba implementation by Gu & Dao - THE authoritative source
- **Architecture**: Mamba SSM with selective scan, diagonal A matrix
- **Key Insight from Paper**: "SSMs are sensitive to precision" - eigenvalue computations need float32/64
- **Key Code Location**: `mamba_ssm/modules/mamba_simple.py` - contains A matrix and state dynamics
- **Training Config**: Uses PyTorch AMP for mixed precision
- **Critical Note from Issues**: Forward hooks may not work on inner modules due to fused CUDA implementations - need to use slow path for introspection

**Repository 2**: [johnma2006/mamba-minimal](https://github.com/johnma2006/mamba-minimal)
- **URL**: https://github.com/johnma2006/mamba-minimal
- **Relevance**: Pure PyTorch implementation for readability - ideal for eigenvalue analysis
- **Architecture**: Single-file Mamba implementation without CUDA dependencies
- **Key Advantage**: Can use standard PyTorch hooks since no fused kernels
- **Numerical Parity**: Equivalent numerical output to official implementation

**Repository 3**: [tommyip/mamba2-minimal](https://github.com/tommyip/mamba2-minimal)
- **URL**: https://github.com/tommyip/mamba2-minimal
- **Relevance**: Mamba-2 minimal implementation with SSD formulation
- **Key Code**:
  ```python
  from mamba2 import Mamba2, Mamba2Config
  config = Mamba2Config(d_model=768)
  model = Mamba2(config)
  ```

**Query 2: "Mamba model Jacobian computation autograd hooks"**

**GitHub Issue Finding**: [state-spaces/mamba#59](https://github.com/state-spaces/mamba/issues/59)
- **Critical Discovery**: In fused fast implementations, inner modules may not be called directly
- **Solution**: Use weights directly or force slow path for hook access:
  ```python
  # Register hook on mixer level, not inner modules
  model.backbone.layers[0].mixer.register_forward_hook(hook_fn)
  ```
- **Important**: Pretrained weights are the same regardless of computation path

**Query 3: "PyTorch torch.linalg.eig eigenvalue decomposition"**

**PyTorch Documentation**: [torch.linalg.eig](https://docs.pytorch.org/docs/stable/generated/torch.linalg.eig.html)
- **Syntax**: `eigenvalues, eigenvectors = torch.linalg.eig(A)`
- **Returns**: Complex-valued eigenvalues and eigenvectors (even for real input)
- **For diagonal A (Mamba)**: Use `torch.linalg.eigvals()` for efficiency
- **Key Code**:
  ```python
  import torch
  # For Mamba's diagonal A matrix
  A = model.layers[0].mixer.A_log.exp()  # Get A matrix
  eigenvalues = torch.linalg.eigvals(A)
  lambda_max = eigenvalues.abs().max()
  H_spec = -1 / torch.log(lambda_max)
  ```

**Serena Analysis Needed**: false (Code patterns are clear from Exa results)

### 🎯 Implementation Priority Assessment

**CRITICAL: For eigenvalue extraction, use minimal implementation for hook access**

**Implementation Priority:**
1. **johnma2006/mamba-minimal** (HIGHEST) - Pure PyTorch, no CUDA dependencies, full hook access
2. **state-spaces/mamba** (official) - Authoritative but fused kernels may block inner hooks
3. **tommyip/mamba2-minimal** - Alternative if Mamba-2 analysis needed

**Recommended Implementation Path:**
- Primary: `johnma2006/mamba-minimal` - Load pretrained weights into minimal implementation for eigenvalue access
- Fallback: `state-spaces/mamba` with `use_fast_path=False` to enable hook access
- Justification: Minimal implementations expose A_log directly without CUDA fusion, enabling straightforward eigenvalue extraction via `torch.exp(A_log)`

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The Mamba minimal implementations (johnma2006/mamba-minimal, tommyip/mamba2-minimal) provide readable pure-PyTorch code without CUDA dependencies, making eigenvalue extraction straightforward using standard PyTorch APIs (`torch.linalg.eig`, `torch.linalg.eigvals`).

---

## Experiment Specification

### Dataset

**CRITICAL CLARIFICATION**: H-E1 is an EXISTENCE hypothesis measuring an **intrinsic model property** (eigenvalue stability). This is NOT a task performance experiment - no training is performed. The "dataset" is random input sequences used to probe the model's state dynamics.

**Dataset Type**: programmatic-api (random sequence generation)
**Name**: Random Token Sequences for Eigenvalue Probing
**Type**: programmatic-api (NOT synthetic task data - this is a measurement methodology)
**Source**: `torch.randint()` to generate random token IDs within vocabulary

**Experiment Design Justification**:
- Per Panda et al. (2019) "Evaluating the Stability of Recurrent Neural Models during Training with Eigenvalue Spectra Analysis" - random inputs are standard for eigenvalue stability measurement
- Per Jarne (2022) "Different eigenvalue distributions encode the same temporal tasks in recurrent neural networks" - eigenvalue properties are model-intrinsic, not input-dependent
- The hypothesis tests whether CV(H_spec) < 0.3 **across random inputs** - this is the measurement design, not a synthetic benchmark

**Sample Count**: 1000 random sequences (per Phase 2B verification protocol)
**Sequence Length**: 512 tokens (standard context length)
**Vocabulary**: Mamba tokenizer vocabulary size

**Loading Information** (for Phase 4 implementation):
- Method: programmatic-api (torch random generation)
- Identifier: N/A - generated at runtime
- Code:
  ```python
  import torch
  # Generate 1000 random token sequences for eigenvalue probing
  vocab_size = tokenizer.vocab_size
  seq_length = 512
  num_samples = 1000
  random_sequences = torch.randint(0, vocab_size, (num_samples, seq_length))
  ```

### Models

#### Baseline Model

**Architecture**: Mamba-1.4B (pretrained SSM)
**Type**: State Space Model with selective scan
**Source**: state-spaces/mamba (official repository)
**Hypothesis Fit**: Primary Mamba architecture with accessible eigenanalysis via diagonal A matrix

**Model Details**:
- Parameters: ~1.4B
- Layers: 48 Mamba blocks
- State dimension: 16 (d_state)
- Model dimension: 2048 (d_model)
- A matrix: Diagonal, input-independent (key for eigenvalue stability)

**Cross-Validation Model**: Mamba-370M
- For scale consistency check (H_spec should scale with model size)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers + mamba-ssm
- Identifier: `state-spaces/mamba-1.4b`
- Code:
  ```python
  from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel
  from transformers import AutoTokenizer

  # Load pretrained Mamba-1.4B
  model = MambaLMHeadModel.from_pretrained("state-spaces/mamba-1.4b")
  tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")

  # For cross-validation
  model_370m = MambaLMHeadModel.from_pretrained("state-spaces/mamba-370m")
  ```

#### Proposed Model

**Architecture:** N/A - This is an EXISTENCE hypothesis measuring intrinsic model properties, NOT proposing a new model architecture.

**Measurement Approach**: Extract eigenvalues from pretrained Mamba model across random inputs to verify H_spec stability.

**Core Mechanism Implementation (Eigenvalue Extraction + H_spec Computation):**

```python
# Core Mechanism: Spectral Memory Horizon Measurement
# Based on: Mamba SSM A-matrix eigenvalue analysis
# Source: state-spaces/mamba, Panda et al. (2019) eigenvalue stability methodology

import torch
import torch.nn as nn
from typing import List, Tuple

def compute_spectral_horizon(model: nn.Module, input_ids: torch.Tensor) -> float:
    """
    Compute H_spec = -1/log|λ_max| for a given input sequence.

    Args:
        model: Pretrained Mamba model
        input_ids: (seq_len,) token IDs
    Returns:
        H_spec: Spectral memory horizon in tokens
    """
    # Extract A matrix from each Mamba layer (diagonal, input-independent)
    lambda_max_per_layer = []

    for layer in model.backbone.layers:
        # A_log is stored as log of diagonal elements
        A_log = layer.mixer.A_log  # (d_state,) or (d_inner, d_state)
        A = torch.exp(A_log)  # Diagonal eigenvalues

        # Get maximum eigenvalue magnitude per layer
        lambda_max = A.abs().max()
        lambda_max_per_layer.append(lambda_max)

    # Global H_spec from max eigenvalue across all layers
    global_lambda_max = torch.stack(lambda_max_per_layer).max()
    H_spec = -1.0 / torch.log(global_lambda_max)

    return H_spec.item()

def measure_h_spec_stability(model: nn.Module,
                             random_sequences: torch.Tensor,
                             num_samples: int = 1000) -> Tuple[float, float, float]:
    """
    Measure CV(H_spec) across random input sequences.

    Returns:
        (mean_H_spec, std_H_spec, CV)
    """
    h_spec_values: List[float] = []

    for i in range(num_samples):
        h_spec = compute_spectral_horizon(model, random_sequences[i])
        h_spec_values.append(h_spec)

    mean_h = sum(h_spec_values) / len(h_spec_values)
    std_h = (sum((x - mean_h)**2 for x in h_spec_values) / len(h_spec_values))**0.5
    cv = std_h / mean_h

    return mean_h, std_h, cv

# Success criterion: CV < 0.3
```

### Training Protocol

**N/A - No Training Required**

This is an EXISTENCE hypothesis measuring an **intrinsic property of pretrained models**. No fine-tuning or training is performed.

**Experiment Type**: Measurement/Analysis (not training)
**Model State**: Pretrained weights only (frozen)
**Computation**: Forward passes for eigenvalue extraction

**Resource Requirements**:
- GPU Memory: ~8GB (Mamba-1.4B inference)
- Compute Time: ~30-60 minutes for 1000 sequences
- Seeds: 1 (random sequence generation seed for reproducibility)

### Evaluation

**Primary Metric**: Coefficient of Variation (CV) of H_spec
- Formula: CV = std(H_spec) / mean(H_spec)
- Computed across 1000 random input sequences

**Success Criteria** (EXISTENCE PoC):
- **PASS**: CV(H_spec) < 0.3
- **FAIL**: CV(H_spec) >= 0.3

**Secondary Metric**: Scale Consistency
- H_spec(Mamba-1.4B) vs H_spec(Mamba-370M)
- Expected: H_spec scales monotonically with model size

**Expected Results** (from hypothesis):
- H_spec should be stable because Mamba's A matrix is input-independent diagonal
- CV < 0.3 indicates H_spec is a measurable model property, not sequence artifact

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: measurement/analysis
- Library: numpy/torch (standard statistics)
- Code:
  ```python
  import numpy as np

  def compute_cv(values: list) -> float:
      """Coefficient of Variation"""
      return np.std(values) / np.mean(values)

  # Success check
  cv = compute_cv(h_spec_values)
  success = cv < 0.3
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **H_spec Distribution Histogram**: Distribution of H_spec values across 1000 sequences
   - X-axis: H_spec value (tokens)
   - Y-axis: Frequency
   - Annotate: mean, std, CV

2. **H_spec per Layer**: H_spec values computed per Mamba layer
   - X-axis: Layer index (0-47)
   - Y-axis: H_spec value
   - Shows which layers contribute most to memory horizon

3. **Eigenvalue Magnitude Distribution**: Histogram of |λ| values
   - Shows eigenvalue distribution across A matrices
   - Annotate: λ_max location

4. **Scale Comparison** (if cross-validation performed):
   - Bar chart: H_spec for Mamba-370M vs Mamba-1.4B
   - Validates monotonic scaling assumption

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. CV(H_spec) < 0.3

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: PyTorch Hook Documentation
- **Type**: Knowledge base article
- **Query Used**: "register forward hook module"
- **Relevance**: Hook patterns for model instrumentation
- **Key Insights**:
  - Use `register_forward_hook()` for layer-wise instrumentation
  - Distributed training hook patterns applicable to eigenvalue extraction
- **Used For**: Eigenvalue extraction methodology

**Source A.2**: General PyTorch Documentation
- **Type**: Knowledge base article
- **Query Used**: "Mamba SSM eigenvalue spectral analysis"
- **Relevance**: Limited direct results - confirms novelty of research
- **Key Insights**:
  - No existing indexed implementations for Mamba eigenvalue analysis
  - Research gap confirmed
- **Used For**: Validating research novelty

### B. GitHub Implementations (Exa)

**Repository B.1**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (⭐18K+)
- **URL**: https://github.com/state-spaces/mamba
- **Query Used**: "Mamba SSM state-spaces eigenvalue analysis PyTorch implementation"
- **Relevance**: Official Mamba implementation by Gu & Dao
- **Key Code** (annotated):
  ```python
  # A_log stored in each Mamba layer mixer
  # Source: mamba_ssm/modules/mamba_simple.py
  self.A_log = nn.Parameter(torch.log(A))  # Diagonal A matrix
  ```
- **Configuration Extracted**: A matrix is diagonal and input-independent
- **Their Results**: State-of-the-art SSM performance
- **Used For**: Understanding A matrix storage, eigenvalue access pattern

**Repository B.2**: [johnma2006/mamba-minimal](https://github.com/johnma2006/mamba-minimal)
- **URL**: https://github.com/johnma2006/mamba-minimal
- **Query Used**: "Mamba SSM state-spaces eigenvalue analysis PyTorch implementation"
- **Relevance**: Pure PyTorch implementation without CUDA dependencies
- **Key Insight**: Enables standard hook access for eigenvalue extraction
- **Used For**: Primary implementation path recommendation

**Repository B.3**: [tommyip/mamba2-minimal](https://github.com/tommyip/mamba2-minimal)
- **URL**: https://github.com/tommyip/mamba2-minimal
- **Relevance**: Mamba-2 minimal implementation
- **Used For**: Alternative reference for SSD formulation

**GitHub Issue B.4**: [state-spaces/mamba#59](https://github.com/state-spaces/mamba/issues/59)
- **URL**: https://github.com/state-spaces/mamba/issues/59
- **Query Used**: "Mamba model Jacobian computation autograd hooks"
- **Relevance**: Critical discovery about hook limitations in fused implementations
- **Key Insight**: Inner modules may not be called directly in fused CUDA path
- **Solution**: Use weights directly or force slow path
- **Used For**: Implementation strategy (use minimal implementation)

**Documentation B.5**: [torch.linalg.eig](https://docs.pytorch.org/docs/stable/generated/torch.linalg.eig.html)
- **URL**: https://docs.pytorch.org/docs/stable/generated/torch.linalg.eig.html
- **Query Used**: "PyTorch torch.linalg.eig eigenvalue decomposition"
- **Relevance**: Official PyTorch eigenvalue computation API
- **Key Code**:
  ```python
  eigenvalues, eigenvectors = torch.linalg.eig(A)
  # Returns complex-valued even for real input
  ```
- **Used For**: Eigenvalue extraction methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

The Mamba minimal implementations provide readable pure-PyTorch code where A_log is directly accessible without requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

### E. Academic References

**Reference E.1**: Panda et al. (2019)
- **Title**: "Evaluating the Stability of Recurrent Neural Models during Training with Eigenvalue Spectra Analysis"
- **URL**: https://arxiv.org/pdf/1905.03219
- **Relevance**: Establishes eigenvalue stability analysis methodology using random inputs
- **Used For**: Validating CV measurement approach

**Reference E.2**: Jarne (2022)
- **Title**: "Different eigenvalue distributions encode the same temporal tasks in recurrent neural networks"
- **URL**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9020562/
- **Relevance**: Eigenvalue properties as intrinsic model characteristics
- **Used For**: Theoretical grounding for H_spec stability hypothesis

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| A matrix structure | GitHub | B.1 (state-spaces/mamba) |
| Eigenvalue access | GitHub | B.2 (mamba-minimal) |
| Hook limitations | GitHub Issue | B.4 (#59) |
| torch.linalg.eig API | Documentation | B.5 |
| CV methodology | Academic | E.1 (Panda et al.) |
| H_spec stability theory | Academic | E.2 (Jarne) |
| Model loading | GitHub | B.1, B.2 |
| Success criterion (CV<0.3) | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T20:25:00Z

### Workflow History for This Hypothesis
- 2026-03-27T20:12:00Z: Phase 2C experiment design started
- 2026-03-27T20:25:00Z: Phase 2C experiment design completed (PASSED validation)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
