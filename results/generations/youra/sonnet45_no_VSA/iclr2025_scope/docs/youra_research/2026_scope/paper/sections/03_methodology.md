# Methodology

## Overview

Building on our observation that environment-stage API defects violate documented invariants testable before training begins, we design a three-tier contract validation framework. Our architecture stratifies contracts by invariant type: structural (shapes, dtypes, device placement), metamorphic (mathematical properties), and composition (cross-library consistency). This stratification enables type-specific optimization—structural contracts execute at import time via decorator introspection, metamorphic contracts run lightweight runtime probes, and composition contracts employ bidirectional propagation to handle multi-library interactions.

Figure 1 illustrates the contract validation lifecycle: (1) At import time, structural decorators intercept function calls to validate tensor shapes and dtypes against documented specifications. (2) Before training begins, metamorphic probes execute lightweight forward passes to verify mathematical invariants (e.g., softmax probability sums). (3) Composition validators check cross-library consistency via bidirectional propagation—blocking downstream execution on upstream failures while validating that upstream libraries recover correctly from downstream errors.

## Tier 1: Structural Contracts

**Design Rationale:** Jiang et al. [1] found that 50.3% of environment-stage API defects involve structural mismatches (incorrect tensor shapes, dtype mismatches, device placement errors). These violations are detectable at import time without executing full forward passes, making them ideal candidates for low-overhead validation.

### Contract Specification

Structural contracts encode shape, dtype, and device constraints as Python decorators:

```python
@api_contract(
    inputs={'x': TensorSpec(shape=('batch', 'channels', 'height', 'width'), 
                            dtype=torch.float32, device='cuda')},
    outputs={'y': TensorSpec(shape=('batch', 'num_classes'), 
                             dtype=torch.float32, device='cuda')}
)
def forward(x: torch.Tensor) -> torch.Tensor:
    ...
```

**Implementation:** At import time, decorators intercept the first function call to validate actual arguments against specifications. Shape constraints support symbolic dimensions (`'batch'`, `'channels'`) that bind to runtime values. Device constraints propagate through the call graph—if an input requires `device='cuda'`, the contract verifies both `x.device == 'cuda'` and that CUDA is available.

**Rationale for Import-Time Validation:** Unlike full integration tests that require launching training runs, import-time validation catches structural violations in <0.03 seconds (h-m1 experiment, Section 5.2). This enables fail-fast behavior: researchers discover mismatches immediately upon importing modules rather than hours into training.

### Alternatives Considered

We evaluated three alternative designs:

1. **Static type checking (mypy, Pyre):** Rejected because tensor shapes and devices are runtime properties not expressible in Python's static type system.
2. **Tracing-based validation:** Rejected due to 10-100× overhead—tracing requires executing forward passes, violating our <10-second constraint.
3. **Manual assertion insertion:** Rejected for poor reusability—assertions are scattered across codebases rather than centralized as library-level contracts.

## Tier 2: Metamorphic Contracts

**Design Rationale:** Beyond structural correctness, APIs must satisfy mathematical invariants—softmax outputs must sum to 1.0, dropout must preserve expectation under eval mode, batch normalization must not change distributional statistics during inference. These metamorphic properties [2] remain stable across library versions (unlike implementation details) and are violated by 30.2% of environment-stage defects that pass structural validation.

### Contract Specification

Metamorphic contracts assert input-output relations via lightweight probes:

```python
@metamorphic_contract(
    property='softmax_probability_sum',
    probe=lambda f, x: torch.allclose(f(x).sum(dim=-1), torch.ones(...), atol=1e-5)
)
def softmax(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    ...
```

**Implementation:** Contracts execute probes on synthetic inputs (random tensors with controlled properties) before the first production call. Probe execution takes 3.7ms on average (h-m2 experiment), enabling validation of 40 distinct properties in <150ms.

**Rationale for Probe-Based Validation:** Full metamorphic testing (generating random inputs during training) incurs per-batch overhead. By executing probes once at environment-setup, we amortize validation cost across the entire training run. The key insight: if `softmax` violates probability-sum invariants on synthetic inputs, it will likely violate them on real data; conversely, if probes pass, we gain confidence without per-batch checks.

### Handling Floating-Point Tolerance

ML computations involve approximate arithmetic where exact equality (`==`) fails even for mathematically equivalent expressions. Contracts use `torch.allclose(atol=1e-5)` for numeric comparisons, with tolerance thresholds derived from IEEE 754 single-precision limits. For edge cases (e.g., softmax over sequences with extreme values), contracts include recovery procedures: if a probe fails, the contract retries with clamped inputs to distinguish genuine invariant violations from numeric instability.

## Tier 3: Composition Contracts

**Design Rationale:** Our initial proof-of-concept (h-e1, Section 5.1) revealed that 19.5% of environment-stage defects arise from cross-library interactions—PyTorch tensors passed to HuggingFace models may reside on incompatible devices, or dtype conversions across library boundaries may lose precision. Naive unidirectional contracts (validating inputs only) achieved 0% contractability due to version-dependent failure modes. This motivated our bidirectional propagation design.

### Bidirectional Propagation Mechanism

Composition contracts validate both forward compatibility (downstream libraries can consume upstream outputs) and backward compatibility (upstream libraries recover correctly from downstream failures):

**Forward Propagation:** When library A calls library B, contracts block execution if A's output violates B's input requirements. Example: If PyTorch produces a CPU tensor but HuggingFace requires CUDA, the contract raises an error *before* calling HuggingFace, providing an actionable message: "Expected device=cuda, got device=cpu. Insert .to('cuda') before calling transformers.AutoModel."

**Backward Propagation:** When library B fails, contracts verify that library A can handle the failure gracefully. Example: If HuggingFace raises an out-of-memory error, the contract checks whether PyTorch's tensor allocator correctly releases GPU memory. This prevents silent resource leaks that accumulate across failed retries.

**Implementation:** Composition contracts intercept cross-library boundaries using Python's context manager protocol:

```python
with composition_contract(upstream=torch, downstream=transformers):
    model_output = transformers.AutoModel.from_pretrained(...)(torch_tensor)
```

The context manager wraps both the call site and exception handlers, enabling bidirectional validation.

**Rationale for Bidirectional Design:** Unidirectional validation (h-e1) could not distinguish between (1) legitimate version incompatibilities (library B intentionally changed requirements) and (2) genuine defects (library A violates B's documented contract). Bidirectional propagation resolves this ambiguity: if B's requirements are documented and A fails to meet them, the forward contract flags the defect; if B changes requirements without documentation updates, the backward contract detects the inconsistency.

### Design Space Exploration

The evolution from h-e1 (0% contractability) to h-c3 (89.7% detection) illustrates iterative mechanism refinement:

| Design Iteration | Composition Detection | Key Limitation |
|-----------------|----------------------|----------------|
| **h-e1 (Unidirectional)** | 0% | False negatives from version drift; false positives from undocumented requirements |
| **h-c3 (Bidirectional)** | 89.7% | Requires library cooperation for backward propagation; opaque C++ extensions limit introspection |

This iteration demonstrates that composition contracts are not straightforward extensions of structural/metamorphic patterns—cross-library validation requires architectural innovation to handle bidirectional failure modes.

## Execution Model and Performance

### Deployment Timeline

```
Import Time (0-50ms)
├─ Structural contracts: Introspect function signatures
└─ Register metamorphic/composition contracts

Environment Setup (50-500ms)
├─ Metamorphic contracts: Execute probes on synthetic inputs
└─ Composition contracts: Validate library bindings

Training Begins (>500ms)
└─ Contracts dormant; no per-batch overhead
```

**Performance Constraints:** Our <10-second execution constraint (Section 1) allocates budget across contract tiers: structural (<0.1s), metamorphic (<0.5s), composition (<2s), leaving >7 seconds for library imports and environment initialization. This budget is validated in h-m2 (Section 5.2), where 40 metamorphic contracts execute in 148ms.

### Contract Overhead Analysis

| Contract Tier | Execution Phase | Overhead | Frequency |
|--------------|----------------|----------|-----------|
| Structural | Import time | <0.03s | Once per import |
| Metamorphic | Environment setup | 3.7ms/property | Once per setup |
| Composition | Environment setup | <2s total | Once per setup |

Critically, contracts incur *zero* per-batch overhead during training—validation occurs once at environment-setup, then contracts become dormant. This contrasts with runtime assertion checking, which repeats validation on every forward pass.

## Contract Auto-Generation (Future Work)

While our evaluation uses manually curated contracts, we note that 60-70% of contracts are mechanically derivable from library docstrings. For example, PyTorch documentation for `torch.nn.functional.softmax` specifies:

> "Applies the Softmax function to an input tensor. [...] The returned tensor will have the same shape as input."

This docstring encodes a structural contract (output shape equals input shape) and a metamorphic contract (outputs form a probability distribution). Auto-generation of such contracts from documentation is a promising direction but requires handling ambiguous specifications and informal language—challenges we defer to future work.

## Reproducibility and Artifact Availability

Our contract implementation, experiment scripts, and evaluation datasets are available at [ANONYMIZED FOR REVIEW]. The codebase includes (1) contract decorators for PyTorch/HuggingFace/JAX, (2) probe generation utilities, (3) bidirectional propagation context managers, and (4) experiment harnesses for reproducing all results in Section 5.

---

**References (Section 3 only - full list in Section 7)**

[1] Jiang et al. (2023). An Empirical Study of Bugs in PyTorch-Based Deep Learning Systems.  
[2] Chen et al. (1998). Metamorphic Testing: A New Approach for Generating Test Cases.
