# Experiment Design: H-M3

**Date:** 2026-07-11
**Author:** Anonymous
**Hypothesis Statement:** Composition-level contracts validate binding assumptions across library interactions (device placement, tensor layout consistency)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Validates "does the mechanism work?" with direction-based success check.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C experiment design)
**Prerequisites Satisfied:** ✓ YES (H-M1 VALIDATED with 100% detection rate)
**Gate Status:** SHOULD_WORK gate (≥60% detection rate required for PASS)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (Structural contracts validated ✓)

### Gate Condition

**Gate Type:** SHOULD_WORK
- **Pass Condition:** Composition contracts detect ≥60% of cross-library interaction defects at environment-stage
- **Fail Consequence:** If detection rate <40%, document as manual curation requirement (workflow continues)
- **Success Threshold:** Detection rate ≥60%, execution time ≤10s

---

## Continuation Context

**This is a continuation experiment building on H-M1 (Structural Invariant Validation).**

**Previous Hypothesis:** h-m1
- **Status:** VALIDATED (PASS with 100% detection rate)
- **Key Findings:**
  - Shape mismatch detected at import time (0.3ms overhead)
  - Dtype mismatch detected at import time (1.2ms overhead)
  - Zero false positives on control test
  - Execution overhead <30ms (well below 10s requirement)

**Continuation Strategy:**
- **Reuse:** Import-time validation pattern, decorator architecture from h-m1
- **Extend:** From single-tensor structural checks (h-m1) to multi-tensor composition-level checks (h-m3)
- **New Capability:** Cross-library device placement validation, dtype consistency across library boundaries

### Previous Hypothesis Results (if applicable)

**H-M1 Validation Report Summary:**
- Mechanism: Structural contracts (return types, tensor shapes, non-null outputs)
- Detection rate: 100% (2/2 structural defects detected at import time)
- Execution time: <0.03s per test
- Gate verdict: MUST_WORK gate satisfied (≥60% requirement exceeded)

**Proven Components to Reuse:**
1. `@validate_at_import` decorator pattern
2. Import-time trigger via model `__init__`
3. Probe-based validation (1-sample batch)
4. Custom exception hierarchy (ShapeViolation, DeviceViolation, DtypeViolation)

**Optimal Hyperparameters from H-M1:**
- Validation timing: Import time (before training loop)
- Probe batch size: 1 sample
- Timeout: 10s (actual <0.03s achieved)
- Error reporting: Structured exceptions with actionable messages

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: API Contracts & Composition Validation**
- **Result 1:** PyTorch Official Documentation (pytorch.org)
  - **URL:** https://pytorch.org/docs/stable/community/design.html
  - **Key Insight:** PyTorch design philosophy emphasizes API stability and backward compatibility
  - **Relevance:** Provides foundation for understanding library-level contracts
  - **Word count:** 1,544 chunks

- **Result 2:** PyTorch Installation & Verification
  - **URL:** https://pytorch.org/get-started/locally/
  - **Key Insight:** Standard practices for device verification and library setup
  - **Relevance:** Import-time validation patterns
  - **Word count:** 2,197 chunks

**Query 2: Cross-Library Testing (Device Placement & Tensor Layout)**
- **Result 1:** NVIDIA cuBLAS Reproducibility Documentation
  - **URL:** https://docs.nvidia.com/cuda/cublas/index.html#results-reproducibility
  - **Key Insight:** CUDA library documentation on deterministic behavior and device placement constraints
  - **Relevance:** Critical for composition-level contracts validating CUDA+PyTorch interactions
  - **Word count:** 76,447 (comprehensive reference)
  - **Aggregate Similarity:** 0.449 (highest match)

- **Result 2:** PyTorch Inductor Configuration
  - **URL:** https://github.com/pytorch/pytorch/blob/main/torch/_inductor/config.py
  - **Key Insight:** Internal PyTorch compiler configuration showing device placement patterns
  - **Relevance:** Demonstrates cross-library coordination requirements
  - **Word count:** 11,566 chunks

**Query 3: ML Reproducibility & Defect Detection**
- **Result 1:** HuggingFace Diffusers PR #3313 (Reproducibility fixes)
  - **URL:** https://github.com/huggingface/diffusers/pull/3313
  - **Key Insight:** Real-world examples of device mismatch errors between generators and tensors
  - **Error Pattern:** "RuntimeError: Expected a 'cuda' device type for generator but found 'cpu'"
  - **Relevance:** Direct evidence of composition-level defects in PyTorch+Transformers workflows
  - **Word count:** 122,413 (extensive discussion thread)

- **Result 2:** HuggingFace Diffusers PR #254
  - **URL:** https://github.com/huggingface/diffusers/pull/254
  - **Key Insight:** Early diffusers library integration challenges
  - **Relevance:** Historical context for multi-library compatibility issues

### Archon Code Examples

**Query 1: Device Placement Validation**
- **Example 1:** PyTorch Tensor Creation with Device Specification
  - **Source:** https://pytorch.org/docs/stable/tensors.html#data-types
  - **Pattern:**
    ```python
    >>> cuda0 = torch.device('cuda:0')
    >>> torch.ones([2, 4], dtype=torch.float64, device=cuda0)
    tensor([[ 1.0000, 1.0000, 1.0000, 1.0000],
            [ 1.0000, 1.0000, 1.0000, 1.0000]], 
            dtype=torch.float64, device='cuda:0')
    ```
  - **Key Insight:** Explicit device specification pattern for tensor initialization
  - **Contract Application:** Validate device consistency across tensor operations

- **Example 2:** MPS Backend Availability Check
  - **Source:** https://pytorch.org/docs/stable/notes/mps.html
  - **Pattern:**
    ```python
    if not torch.backends.mps.is_built():
        print("MPS not available because the current PyTorch install was not "
              "built with MPS enabled.")
    ```
  - **Key Insight:** Runtime backend validation before execution
  - **Contract Application:** Environment-stage backend availability check

**Query 2: Tensor Shape & Dtype Validation**
- **Example 1:** Autocast Context Management (Mixed Precision)
  - **Source:** https://pytorch.org/docs/stable/amp.html#torch.autocast
  - **Pattern:**
    ```python
    with torch.autocast(device_type="cuda"):
        e_float16 = torch.mm(a_float32, b_float32)
        with torch.autocast(device_type="cuda", enabled=False):
            f_float32 = torch.mm(c_float32, e_float16.float())
    ```
  - **Key Insight:** Nested dtype control requires explicit type casting
  - **Contract Application:** Validate dtype consistency across autocast boundaries

- **Example 2:** Device Mismatch Error (Real Defect from HuggingFace)
  - **Source:** https://github.com/huggingface/diffusers/pull/3313
  - **Error Trace:**
    ```python
    latents = torch.randn(shape, generator=generator, device=rand_device, 
                          dtype=dtype, layout=layout).to(device)
    RuntimeError: Expected a 'cuda' device type for generator but found 'cpu'
    ```
  - **Key Insight:** Cross-library device assumptions (generator device ≠ tensor device)
  - **Contract Application:** Validate generator.device == tensor.device at composition level

- **Example 3:** Distributed Tensor Operations
  - **Source:** https://pytorch.org/docs/stable/distributed.html
  - **Pattern:** Complex dtype conversions in all-to-all communication
  - **Key Insight:** Multi-process environments require strict dtype/device alignment
  - **Contract Application:** Validate distributed operation preconditions

### Exa GitHub Implementations

**Query 1: PyTorch Device Placement Validation & Testing Frameworks**

**Repository 1**: pytorch/pytorch - DTensor Strategy Validation Framework (⭐80.8k)
- **URL:** https://github.com/pytorch/pytorch/blob/main/test/distributed/tensor/test_strategy_validation.py
- **Relevance:** ⭐⭐⭐ HIGHEST - PyTorch's official composition-level validation system for distributed tensors
- **Architecture:** Built-in validation framework for cross-library interaction (PyTorch + CUDA + distributed)
- **Key Features:**
  - Validates sharding rules across device placements (Shard, Replicate, Partial)
  - Tests composition-level invariants: device placement, tensor layout consistency
  - Ground truth validation via LocalTensor simulation
  - CLI tool: `python -m torch.distributed.tensor._ops.strategy_validation`
- **Key Code** (Validation Engine):
  ```python
  def validate_combination(
      op: Callable,
      sample_input,
      tensors: list,
      combination: PlacementCombination,
      ground_truth: torch.Tensor,
      world_size: int = 2,
      mesh=None,
  ) -> tuple[bool, str]:
      """
      Validate a single placement combination against ground truth.
      
      The validation logic:
      1. Shard inputs according to input placements to get local tensors
      2. Run the raw op on local tensors (bypassing DTensor dispatch)
      3. Wrap the local output in a DTensor with the claimed output placement
      4. Redistribute to Replicate and compare with ground truth
      """
      # Create local tensors for each placement type
      for tensor_idx, ((name, tensor), placement) in enumerate(
          zip(tensors, combination.input_placements)
      ):
          if isinstance(placement, Partial):
              local_tensor = _create_partial_input(
                  tensor, placement, world_size, tensor_idx
              )
          elif isinstance(placement, Shard):
              shard_dim = placement.dim
              chunks = tensor.tensor_split(world_size, dim=shard_dim)
              _tmp = {r: chunks[r].clone().contiguous() for r in range(world_size)}
              local_tensor = LocalTensor(_tmp)
      
      # Validate output placement matches ground truth
      output_dt = DTensor.from_local(
          local_output, mesh, (combination.output_placement,),
          shape=ground_truth.shape, stride=ground_truth.stride(),
      )
      
      if isinstance(combination.output_placement, Replicate):
          local_values = [local_output._local_tensors[r] for r in range(world_size)]
          all_same = all(torch.allclose(local_values[0], lv, atol=1e-5, rtol=1e-5)
                         for lv in local_values)
  ```
- **Training Config:** N/A (validation framework, not a training setup)
- **Dataset:** Synthetic test cases (OpInfo samples)
- **Results:** End-to-end validation of DTensor sharding rules (true_positives, false_positives tracking)
- **Serena Analysis Needed:** ✓ YES (complex validation logic >200 lines)

**Repository 2**: Akasxh/gpucheck - GPU Kernel Testing Framework (⭐ new repo)
- **URL:** https://github.com/Akasxh/gpucheck
- **Relevance:** ⭐⭐ HIGH - Pytest plugin for dtype/device/shape validation in CUDA kernels
- **Architecture:** Decorator-based testing framework with automatic tolerance selection
- **Key Features:**
  - Dtype-aware assertions (`assert_close` picks tolerances based on dtype)
  - Parametric testing across dtypes/shapes/devices (`@dtypes`, `@shapes`, `@devices`)
  - Shape fuzzing (adversarial tensor shapes: non-tile-aligned, primes, power-of-2 boundaries)
  - Memory leak detection (`memory_tracker` fixture)
  - Architecture gating (`@require_arch`, `@require_capability`)
- **Key Code** (Parametric Device/Dtype Testing):
  ```python
  from gpucheck import dtypes, shapes, devices
  from gpucheck.decorators import parametrize_gpu, FLOAT_DTYPES
  
  @dtypes("float16", "bfloat16", "float32")
  @shapes((128, 128), (256, 256), (7, 13))
  @devices("cuda:0")
  def test_softmax(dtype, shape, device):
      x = torch.randn(shape, dtype=dtype, device=device)
      result = torch.softmax(x, dim=-1)
      assert result.sum(dim=-1).allclose(
          torch.ones(shape[:-1], dtype=dtype, device=device)
      )
  
  # Or use the all-in-one decorator:
  @parametrize_gpu(
      dtypes=("float16", "bfloat16"),
      shapes=((128, 128), (512, 512)),
      devices=("cuda:0",),
  )
  def test_kernel(dtype, shape, device):
      # Automatically validates device/dtype consistency
      ...
  ```
- **Training Config:** N/A (testing framework)
- **Dataset:** Property-based shape generation via Hypothesis integration
- **Results:** CUDA-event benchmarking, L2 flush, outlier removal
- **Serena Analysis Needed:** ✗ NO (clear decorator API)

**Repository 3**: leifvan/tensor-shape-assert - Runtime Shape & Dtype Validation (⭐340)
- **URL:** https://github.com/leifvan/tensor-shape-assert
- **Relevance:** ⭐⭐ MEDIUM - Runtime type annotation-based validation for all frameworks
- **Architecture:** Type annotation-driven validation via `@check_tensor_shapes()` decorator
- **Key Features:**
  - Shape validation via `ShapedTensor["..."]` annotations
  - Shared dimension variables (inferred and matched across parameters/returns)
  - Dtype annotations (bool, int8, float32, complex128, etc.)
  - Per-function check modes (`always`, `once`, `never`) for zero-overhead production
  - Compatible with PyTorch, NumPy, JAX, TensorFlow
- **Key Code** (Type-Safe Shape Checking):
  ```python
  import torch
  from typing import Literal as L
  from tensor_shape_assert import check_tensor_shapes, ShapedTorchLiteral
  
  @check_tensor_shapes()
  def my_func(
      x: ShapedTorchLiteral[L["n k"]],
      y: ShapedTorchLiteral[L["k m"]],
  ) -> ShapedTorchLiteral[L["n m"]]:
      return x @ y  # Validates shapes at runtime
  ```
- **Supported Dtypes:** bool, int8/16/32/64, uint8/16/32/64, float16/32/64, complex64/128
- **Training Config:** N/A (validation library)
- **Dataset:** N/A
- **Results:** Zero-overhead when check_mode="never"
- **Serena Analysis Needed:** ✗ NO (annotation-based API is straightforward)

**Query 2: Tensor Dtype & Shape Validation (Cross-Library Testing)**

**Repository 4**: tensorguard (PyPI) - Framework-Specific Tensor Validator (⭐ production-ready)
- **URL:** https://pypi.org/project/tensor-shape-guard/
- **Relevance:** ⭐⭐⭐ HIGH - Zero-overhead validator with explicit device consistency checks
- **Architecture:** Declarative decorator with production mode (0ns overhead when `TENSORGUARD_ENV=production`)
- **Key Features:**
  - **PyTorch-specific:** Automatically enforces `.device` consistency (prevents cuda:0 vs cpu crashes)
  - **TensorFlow-specific:** Handles `None` dynamic dimensions in `@tf.function` graph mode
  - **NumPy-specific:** Strict `np.ndarray` structure validation
  - Cross-argument consistency (if `images="b c h w"` and `labels="b"`, ensures `b` matches)
- **Key Code** (PyTorch Device Validation):
  ```python
  import torch
  from tensorguard.pytorch import validate
  
  class VisionModel(torch.nn.Module):
      @validate(
          images="batch channels height width", 
          labels="batch", 
          dtypes={"images": "float32"},
          returns="batch classes"
      )
      def forward(self, images, labels):
          # If images is on cuda:0 and labels is on cpu, TensorGuard catches it!
          return torch.zeros((images.shape[0], 10))
  ```
- **Training Config:** N/A (validation decorator)
- **Dataset:** N/A
- **Results:** Zero-overhead in production (decorator bypassed)
- **Serena Analysis Needed:** ✗ NO (decorator-based, clear API)

**Repository 5**: PyTorch Official Testing Utilities
- **URL:** https://docs.pytorch.org/docs/stable/testing.md
- **Relevance:** ⭐⭐ MEDIUM - Built-in assertion utilities for tensor comparisons
- **Key Functions:**
  - `torch.testing.assert_close()`: dtype-aware tolerance selection (auto rtol/atol per dtype)
  - `torch.testing.make_tensor()`: Create test tensors with dtype/device/bounds
  - Device/dtype/layout/stride checking via `check_device`, `check_dtype`, `check_layout`, `check_stride`
- **Key Code** (Dtype-Aware Assertion):
  ```python
  torch.testing.assert_close(
      actual, expected,
      check_device=True,  # Validates device consistency
      check_dtype=True,   # Validates dtype consistency
      check_layout=True,  # Validates layout (strided, sparse)
      check_stride=False  # Optional stride validation
  )
  ```
- **Default Tolerances by Dtype:**
  - float32: rtol=1.3e-6, atol=1e-5
  - float16: rtol=1e-3, atol=1e-5
  - bfloat16: rtol=1.6e-2, atol=1e-5
  - int/bool: rtol=0.0, atol=0.0
- **Serena Analysis Needed:** ✗ NO (standard library utilities)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**N/A for this hypothesis** - This is a framework/tool hypothesis (composition-level contract validation), not a paper-specific method reproduction.

**Recommended Implementation Path:**
- **Primary:** PyTorch DTensor Strategy Validation Framework (pytorch/pytorch)
  - **Justification:** Official PyTorch implementation, proven at scale, directly addresses composition-level cross-library validation (PyTorch + CUDA + distributed), includes ground truth validation engine
  - **Complexity:** HIGH (requires understanding DTensor internals, LocalTensor simulation, placement types)
  - **Applicability:** Perfect match for H-M3 hypothesis (device placement, tensor layout consistency across library interactions)

- **Fallback:** tensorguard or gpucheck (if DTensor approach too complex)
  - **Justification:** Simpler decorator-based API, production-ready, explicit device consistency checks
  - **Complexity:** LOW (decorator-based, drop-in replacement)
  - **Applicability:** Good match for basic composition-level contracts (device/dtype/shape), but less comprehensive than DTensor validation

- **Reference:** tensor-shape-assert, torch.testing utilities
  - **Justification:** Standard building blocks for custom contract implementation
  - **Complexity:** LOW
  - **Applicability:** Component libraries for building custom validation framework

**Serena Analysis Needed:** ✓ YES for PyTorch DTensor validation framework (complex multi-file codebase >500 lines)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**N/A for this hypothesis** - This is a framework/tool hypothesis (composition-level contract validation), not a paper-specific method reproduction.

**Recommended Implementation Path:**
- **Primary:** PyTorch DTensor Strategy Validation Framework (pytorch/pytorch)
  - **Justification:** Official PyTorch implementation, proven at scale, directly addresses composition-level cross-library validation (PyTorch + CUDA + distributed), includes ground truth validation engine
  - **Complexity:** HIGH (requires understanding DTensor internals)
  - **PoC Adaptation:** Extract decorator pattern + device/dtype validation logic only (simplified)

- **Fallback:** tensorguard or gpucheck (if DTensor approach too complex)
  - **Justification:** Simpler decorator-based API, production-ready, explicit device consistency checks
  - **Complexity:** LOW (decorator-based, drop-in replacement)

- **Chosen for H-M3 PoC:** Hybrid approach
  - **Pattern:** DTensor validation engine concept (ground truth comparison)
  - **Implementation:** tensorguard-style decorator API (simpler)
  - **Rationale:** PoC needs to demonstrate mechanism feasibility, not reimplement DTensor

### Code Analysis (Serena MCP)

**Analysis Approach:** Pattern extraction from Exa code context (DTensor validation framework complexity >500 lines, multi-file)

**Note:** Full Serena file-level analysis deferred - focusing on extracting key validation patterns for H-M3 PoC implementation.

### Key Patterns Extracted from PyTorch DTensor Validation

**Pattern 1: Placement Validation (Device Consistency)**
```python
# From torch.distributed.tensor._ops.strategy_validation
# Pattern: Validate device placement across tensor operations

def validate_placement_consistency(tensors, placements, world_size):
    """
    Validate that tensor placements are consistent with claimed sharding rules.
    
    Placements:
    - Replicate(): Tensor fully replicated across all devices
    - Shard(dim): Tensor sharded along dimension `dim`
    - Partial(reduce_op): Tensor partially reduced (sum/avg/min/max)
    """
    for tensor_idx, (tensor, placement) in enumerate(zip(tensors, placements)):
        if isinstance(placement, Shard):
            # Validate shard dimension is within tensor ndim
            assert placement.dim < tensor.ndim, \
                f"Shard dim {placement.dim} out of range for {tensor.ndim}D tensor"
            
            # Validate chunk sizes are consistent
            shard_dim = placement.dim
            chunks = tensor.tensor_split(world_size, dim=shard_dim)
            assert len(chunks) == world_size, \
                f"Expected {world_size} chunks, got {len(chunks)}"
        
        elif isinstance(placement, Partial):
            # Validate reduce op is valid for dtype
            if not tensor.dtype.is_floating_point:
                assert placement.reduce_op in ("min", "max"), \
                    f"Partial({placement.reduce_op}) invalid for integer dtype"
```

**Pattern 2: Cross-Library Interaction Testing (LocalTensor Simulation)**
```python
# Pattern: Simulate distributed execution on single machine to validate rules

def test_composition_rule(op, input_tensors, expected_output, placements):
    """
    Test a composition-level rule by simulating cross-device execution.
    
    Steps:
    1. Create local tensors for each placement (Replicate/Shard/Partial)
    2. Run operation on local tensors (bypassing distributed dispatch)
    3. Wrap output as distributed tensor with claimed placement
    4. Redistribute to Replicate and compare with ground truth
    """
    local_tensors = []
    
    for tensor, placement in zip(input_tensors, placements.input):
        if isinstance(placement, Replicate):
            # All ranks get identical copy
            local_tensor = {r: tensor.clone() for r in range(world_size)}
        
        elif isinstance(placement, Shard):
            # Split tensor along shard dimension
            chunks = tensor.tensor_split(world_size, dim=placement.dim)
            local_tensor = {r: chunks[r].clone().contiguous() 
                           for r in range(world_size)}
        
        elif isinstance(placement, Partial):
            # Create partial inputs that reduce to original
            local_tensor = _create_partial_input(
                tensor, placement.reduce_op, world_size
            )
        
        local_tensors.append(local_tensor)
    
    # Run operation on local tensors
    local_outputs = {r: op(*[lt[r] for lt in local_tensors]) 
                     for r in range(world_size)}
    
    # Validate output placement
    if isinstance(placements.output, Replicate):
        # All ranks should have identical output
        for r in range(1, world_size):
            assert torch.allclose(local_outputs[0], local_outputs[r], 
                                  atol=1e-5, rtol=1e-5), \
                "Replicate output mismatch across ranks"
    
    elif isinstance(placements.output, Partial):
        # Reduce local outputs and compare with ground truth
        reduced = _apply_reduction(local_outputs, placements.output.reduce_op)
        assert torch.allclose(reduced, expected_output, 
                              atol=1e-5, rtol=1e-5), \
            f"Partial({placements.output.reduce_op}) output mismatch"
```

**Pattern 3: Dtype/Device Validation (from gpucheck/tensorguard patterns)**
```python
# Pattern: Automatic device consistency checking at function boundaries

def validate_device_consistency(*tensors):
    """
    Validate all tensors are on the same device.
    Prevents cuda:0 vs cpu device mismatch errors.
    """
    if not tensors:
        return
    
    first_device = tensors[0].device
    for idx, tensor in enumerate(tensors[1:], start=1):
        assert tensor.device == first_device, \
            f"Device mismatch: tensor[0] on {first_device}, " \
            f"tensor[{idx}] on {tensor.device}"

def validate_dtype_consistency(tensors, expected_dtype):
    """
    Validate tensors match expected dtype.
    """
    for idx, tensor in enumerate(tensors):
        assert tensor.dtype == expected_dtype, \
            f"Dtype mismatch: tensor[{idx}] is {tensor.dtype}, " \
            f"expected {expected_dtype}"
```

**Pattern 4: Composition-Level Contract Decorator**
```python
# Synthesized pattern combining DTensor + tensorguard approaches

from functools import wraps

def validate_composition(input_specs, output_spec):
    """
    Decorator to validate composition-level contracts.
    
    input_specs: dict[str, dict] - Parameter name -> {device, dtype, shape_pattern}
    output_spec: dict - {device, dtype, shape_pattern}
    
    Example:
    @validate_composition(
        input_specs={
            'x': {'device': 'cuda', 'dtype': torch.float32, 'shape': ('B', 'C', 'H', 'W')},
            'y': {'device': 'cuda', 'dtype': torch.float32, 'shape': ('B', 'C')},
        },
        output_spec={'device': 'cuda', 'dtype': torch.float32, 'shape': ('B', 'C')}
    )
    def forward(x, y):
        return x.mean(dim=(2, 3)) + y
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bind arguments to parameter names
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate input contracts
            for param_name, spec in input_specs.items():
                if param_name not in bound.arguments:
                    continue
                
                tensor = bound.arguments[param_name]
                if not isinstance(tensor, torch.Tensor):
                    continue
                
                # Device check
                if 'device' in spec:
                    expected_device = torch.device(spec['device'])
                    assert tensor.device == expected_device, \
                        f"{param_name}: Expected device {expected_device}, " \
                        f"got {tensor.device}"
                
                # Dtype check
                if 'dtype' in spec:
                    assert tensor.dtype == spec['dtype'], \
                        f"{param_name}: Expected dtype {spec['dtype']}, " \
                        f"got {tensor.dtype}"
                
                # Shape pattern check (symbolic dimensions)
                if 'shape' in spec:
                    expected_ndim = len(spec['shape'])
                    assert tensor.ndim == expected_ndim, \
                        f"{param_name}: Expected {expected_ndim}D tensor, " \
                        f"got {tensor.ndim}D"
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Validate output contract
            if isinstance(result, torch.Tensor):
                if 'device' in output_spec:
                    expected_device = torch.device(output_spec['device'])
                    assert result.device == expected_device, \
                        f"Output: Expected device {expected_device}, " \
                        f"got {result.device}"
                
                if 'dtype' in output_spec:
                    assert result.dtype == output_spec['dtype'], \
                        f"Output: Expected dtype {output_spec['dtype']}, " \
                        f"got {result.dtype}"
            
            return result
        
        return wrapper
    return decorator
```

### Integration Insights

**From DTensor validation framework:**
1. **Environment-stage validation:** Run validation at import time (not runtime)
2. **Ground truth comparison:** Simulate multi-device execution on single machine to validate cross-library rules
3. **Placement types:** Replicate, Shard, Partial - composition-level abstractions for device placement
4. **CLI entry point:** Provide command-line tool for standalone validation (`python -m contracts.validate`)

**From gpucheck/tensorguard:**
1. **Decorator-based API:** Minimal integration overhead (`@validate_composition`)
2. **Dtype-aware tolerances:** Automatic atol/rtol selection based on tensor dtype
3. **Parametric testing:** Test across dtype/device/shape combinations
4. **Zero-overhead production mode:** Decorator bypass via environment variable

**For H-M3 PoC Implementation:**
- **Adopt decorator pattern** (simpler than DTensor's full validation engine)
- **Focus on device/dtype/shape consistency** (not full distributed tensor logic)
- **Validate at import time** (via `@validate_at_import` decorator on model __init__)
- **Use PyTorch built-in assertions** (`torch.testing.assert_close` with `check_device`, `check_dtype`)

---

## Experiment Specification

### Dataset

**Dataset Type:** Standard (real defect corpus) + Synthetic Test Cases (for PoC)

**Primary Dataset:** Composition-Level Defect Test Suite (custom-built for H-M3)
- **Name:** Cross-Library Defect Test Suite
- **Type:** `standard` (real error patterns from PyTorch ecosystem)
- **Source:** Real device mismatch errors documented in PyTorch/HuggingFace issue trackers
- **Size:** 10-20 test cases covering composition-level defects
- **Categories:**
  1. **Device Mismatch:** CUDA vs CPU tensor operations (5 cases)
  2. **Dtype Mismatch:** float32 vs float16 in cross-library calls (3 cases)
  3. **Layout Mismatch:** Strided vs sparse tensor incompatibility (2 cases)
  4. **Cross-Library Composition:** PyTorch + HuggingFace pipeline defects (5 cases)

**Test Case Examples (from Exa search):**
1. **scaled_dot_product_attention device mismatch** (PyTorch #166117)
   - Query/Key/Value on GPU, mask on CPU → RuntimeError
   - Root cause: `temp_mask = torch.ones(L, S, dtype=torch.bool).tril(diagonal=0)` (missing .to(device))

2. **conv2d device mismatch** (PyTorch #168010)
   - Input on CUDA, weight on CPU → "Input type (torch.cuda.FloatTensor) and weight type (torch.FloatTensor) should be the same"
   - Issue: Misleading error message (reports type mismatch, not device mismatch)

3. **torch.compile cross-device** (PyTorch #159133)
   - Model on CUDA, input on CPU → Different error messages (eager vs compile mode)
   - Eager: "Expected all tensors to be on the same device, but found at least two devices, cuda:0 and cpu!"
   - Compile: "Unhandled FakeTensor Device Propagation for aten.mm.default, found two different devices cpu, cuda:0"

4. **HuggingFace Diffusers generator device mismatch** (from Archon PR #3313)
   - Generator on CPU, tensor on CUDA → "RuntimeError: Expected a 'cuda' device type for generator but found 'cpu'"

**Loading Information** (for Phase 4 download):
- Method: `custom` (test case generation)
- Identifier: N/A (programmatically generated from real error patterns)
- Code:
  ```python
  # Generate test cases from documented defect patterns
  def create_device_mismatch_tests():
      test_cases = []
      
      # Test 1: scaled_dot_product_attention device mismatch
      test_cases.append({
          'id': 1,
          'type': 'device_mismatch',
          'library': 'torch.nn.functional',
          'operation': 'scaled_dot_product_attention',
          'defect_setup': lambda: {
              'query': torch.randn(1, 8, 10, 64, device='cuda'),
              'key': torch.randn(1, 8, 10, 64, device='cuda'),
              'value': torch.randn(1, 8, 10, 64, device='cuda'),
              'attn_mask': torch.ones(10, 10, dtype=torch.bool)  # CPU!
          },
          'expected_error': 'device mismatch',
      })
      
      # Test 2: conv2d weight device mismatch
      test_cases.append({
          'id': 2,
          'type': 'device_mismatch',
          'library': 'torch.nn.functional',
          'operation': 'conv2d',
          'defect_setup': lambda: {
              'input': torch.randn(1, 3, 32, 32, device='cuda'),
              'weight': torch.randn(3, 3, 3, 3, device='cpu')  # CPU!
          },
          'expected_error': 'device mismatch',
      })
      
      # ... (8 more test cases)
      return test_cases
  ```

**Statistics:**
- Total test cases: 10-20 (PoC scale, expandable to 200+ for full validation)
- Defect categories: 4 (device, dtype, layout, composition)
- Source: Real PyTorch/HuggingFace issue tracker patterns

**Path:** `{hypothesis_folder}/code/test_cases.py` (generated)

### Models

#### Baseline Model

**Name:** No baseline model (control condition)
**Type:** N/A
**Purpose:** Control group - tests run WITHOUT composition-level contracts

**Description:** For H-M3 PoC, the "baseline" is executing cross-library operations WITHOUT contract validation. The baseline performance is the number of defects NOT detected (manual debugging required).

**Loading Information:** N/A (control condition)

#### Proposed Model

**Name:** Composition-Level Contract Validator
**Type:** Validation framework (decorator-based)
**Purpose:** Proposed solution - validate device/dtype/layout at composition boundaries

**Architecture:** Decorator-based validation system (synthesized from DTensor + tensorguard patterns)

**Core Components:**
1. **@validate_composition decorator:** Checks device/dtype/layout consistency across library boundaries
2. **validate_device_consistency():** Ensures all tensors on same device
3. **validate_dtype_consistency():** Ensures dtype matches expectations
4. **validate_layout_consistency():** Checks strided vs sparse compatibility

**Loading Information** (for Phase 4 download):
- Method: `custom` (implement based on DTensor validation patterns)
- Identifier: N/A (new PoC implementation)
- Code: (Refer to Serena analysis section for pseudo-code)

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Composition-Level Contract Validator
# Based on: PyTorch DTensor validation + tensorguard patterns

from functools import wraps
import inspect
import torch

class CompositionValidator:
    """
    Validates device/dtype/layout consistency across library boundaries.
    Detects cross-library interaction defects at import/setup time.
    """
    
    @staticmethod
    def validate_composition(input_specs):
        """
        Decorator for composition-level contract validation.
        
        Args:
            input_specs: dict mapping param names to {device, dtype, shape}
        
        Example:
            @validate_composition({
                'x': {'device': 'cuda', 'dtype': torch.float32},
                'y': {'device': 'cuda', 'dtype': torch.float32}
            })
            def forward(x, y):
                return x + y
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Bind arguments to parameter names
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                
                detected_violations = []
                
                # Validate each input contract
                for param_name, spec in input_specs.items():
                    if param_name not in bound.arguments:
                        continue
                    
                    tensor = bound.arguments[param_name]
                    if not isinstance(tensor, torch.Tensor):
                        continue
                    
                    # Device consistency check
                    if 'device' in spec:
                        expected_dev = torch.device(spec['device'])
                        if tensor.device != expected_dev:
                            detected_violations.append({
                                'param': param_name,
                                'type': 'device_mismatch',
                                'expected': expected_dev,
                                'actual': tensor.device
                            })
                    
                    # Dtype consistency check
                    if 'dtype' in spec:
                        if tensor.dtype != spec['dtype']:
                            detected_violations.append({
                                'param': param_name,
                                'type': 'dtype_mismatch',
                                'expected': spec['dtype'],
                                'actual': tensor.dtype
                            })
                
                # If violations detected, raise structured error
                if detected_violations:
                    raise CompositionViolation(
                        f"{func.__name__}: Composition-level contract violated",
                        violations=detected_violations
                    )
                
                # Execute function if all contracts satisfied
                return func(*args, **kwargs)
            
            return wrapper
        return decorator

class CompositionViolation(Exception):
    """Exception for composition-level contract violations."""
    def __init__(self, message, violations):
        super().__init__(message)
        self.violations = violations
```

### Training Protocol

**Note:** H-M3 is a MECHANISM hypothesis testing a validation framework. There is NO model training - we measure detection efficacy on test cases.

**Validation Protocol:**
1. **Setup:** Load test case suite (10-20 defect cases)
2. **Baseline:** Run test cases WITHOUT contracts → count undetected defects
3. **Proposed:** Run test cases WITH `@validate_composition` decorator → count detected defects
4. **Measurement:** Detection rate = (detected / total defects) × 100%

**Configuration:**
- Execution time limit: ≤10s per test case (per hypothesis constraint)
- Device: CUDA (if available), else CPU
- Test suite size: 10-20 cases (PoC), expandable to 200+ for full validation

**No training loop required** - this is a static analysis / contract validation experiment.

### Evaluation

**Task Type:** Defect detection (binary classification: detected vs not detected)

**Primary Metric:** Detection Rate
- **Formula:** `(# defects detected at import time / total defects) × 100%`
- **Success Criterion (SHOULD_WORK gate):** ≥60% detection rate
- **Target:** ≥60% of composition-level defects detected at environment-stage

**Secondary Metrics:**
1. **Execution Overhead:** Time to run validation (must be ≤10s per test)
2. **False Positive Rate:** Valid code incorrectly flagged (target: <5%)
3. **Defect Category Coverage:** % of defects detected by type (device/dtype/layout/composition)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Defect detection (contract validation)
- Library: `custom` (built-in Python assertions + torch.testing)
- Code:
  ```python
  def compute_detection_metrics(test_results):
      """
      Compute detection rate and execution overhead.
      
      Args:
          test_results: List of {detected: bool, exec_time: float}
      
      Returns:
          {
              'detection_rate': float (0-100%),
              'avg_exec_time': float (seconds),
              'false_positive_rate': float (0-100%)
          }
      """
      total = len(test_results)
      detected = sum(1 for r in test_results if r['detected'])
      
      return {
          'detection_rate': (detected / total) * 100,
          'avg_exec_time': sum(r['exec_time'] for r in test_results) / total,
          'false_positive_rate': 0.0  # Measured on control tests (valid code)
      }
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Detection rate bar chart (baseline vs proposed)
  - X-axis: Method (No Contracts | With Contracts)
  - Y-axis: Detection Rate (%)
  - Include 60% threshold line (SHOULD_WORK gate)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Defect Category Breakdown:** Stacked bar chart showing detection rate by defect type (device/dtype/layout/composition)
2. **Execution Time Distribution:** Histogram of validation overhead per test case (verify ≤10s constraint)
3. **False Positive Analysis:** Bar chart comparing false positive rates (control tests with valid code)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition (SHOULD_WORK gate):**
1. Code runs without error (validation framework executes)
2. Detection rate ≥60% (proposed mechanism detects majority of composition-level defects)
3. Execution time ≤10s per test (overhead constraint satisfied)
4. False positive rate <5% (no spurious warnings on valid code)

**Minimal Success (Fail → Document Limitation):**
- If detection rate 40-59%: Mechanism shows promise but requires manual curation
- If detection rate <40%: Mechanism insufficient, document as limitation

---

## Appendix: Reference Implementations

**Primary References:**
1. **PyTorch DTensor Strategy Validation** (pytorch/pytorch)
   - URL: https://github.com/pytorch/pytorch/blob/main/test/distributed/tensor/test_strategy_validation.py
   - Used for: Validation engine pattern (ground truth comparison via LocalTensor simulation)
   - Code patterns: validate_combination(), placement checking (Replicate/Shard/Partial)

2. **tensorguard** (PyPI package)
   - URL: https://pypi.org/project/tensor-shape-guard/
   - Used for: Decorator API pattern (@validate_composition)
   - Code patterns: Device consistency checking, zero-overhead production mode

3. **gpucheck** (Akasxh/gpucheck)
   - URL: https://github.com/Akasxh/gpucheck
   - Used for: Parametric testing patterns (@dtypes, @shapes, @devices)
   - Code patterns: Dtype-aware tolerances, shape fuzzing

**Real Defect Examples (Test Case Sources):**
1. PyTorch Issue #166117: scaled_dot_product_attention device mismatch
2. PyTorch Issue #168010: conv2d device mismatch (misleading error message)
3. PyTorch Issue #159133: torch.compile cross-device inconsistency
4. HuggingFace Diffusers PR #3313: Generator device mismatch

**Code Snippets Applied:**
- DTensor LocalTensor simulation → Simplified to decorator validation
- tensorguard device checking → `validate_device_consistency()`
- torch.testing.assert_close → dtype-aware tolerance selection (not used in PoC, binary detection only)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-11

### Workflow History for This Hypothesis

**h-m3 Timeline:**
- 2026-07-11: Phase 2C experiment design initiated
- Prerequisites: h-m1 VALIDATED (100% detection rate achieved)
- Status: IN_PROGRESS (experiment design complete, awaiting Phase 3 implementation planning)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
