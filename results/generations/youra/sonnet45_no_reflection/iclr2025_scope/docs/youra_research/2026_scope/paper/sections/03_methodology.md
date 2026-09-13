# Methodology

## Overview

Building on our observation that computational feasibility validation is missing from research workflows, we design a lightweight Phase 2C.5 feasibility gate that estimates total memory requirements and validates against available hardware before implementation begins. The gate integrates into existing research pipelines at minimal cost (~5 minutes, <1% of implementation time) while preventing potentially 100% wasted effort on infeasible configurations.

Our approach addresses the core tension: experiment designers prioritize scientific rigor and theoretical elegance during Phase 2C (experiment design), deferring practical constraints to implementation. This creates a gap where infeasible configurations can be approved and proceed through expensive planning (Phase 3: 2-3 hours) and coding (Phase 4: 4-6 hours) phases before resource violations are discovered. The feasibility gate closes this gap by adding a mandatory checkpoint between design approval and implementation initiation.

## Phase 2C.5 Feasibility Gate Design

### Gate Placement

**Decision:** Insert the feasibility checkpoint as Phase 2C.5—after experiment design finalizes model and dataset choices (Phase 2C), but before implementation planning begins (Phase 3).

**Rationale:** This timing minimizes wasted effort if reformulation is needed. Phase 2C outputs concrete specifications (model name, dataset requirements, task count), providing sufficient information for memory estimation. Catching infeasibility before Phase 3 prevents planning effort (PRD, architecture design) on unrunnable configurations. Earlier placement (Phase 2B) would be premature—model selection hasn't occurred yet. Later placement (Phase 3 or 4) defeats the purpose—planning or coding effort already sunk.

**Alternative Considered:** Phase 4 pre-execution validation. This catches infeasibility but only after full implementation (coding, testing). Our retrospective analysis shows this would still save execution time but waste the entire implementation effort—not optimal.

### Memory Estimation Formula

**Decision:** Estimate total memory as:
```
Total_VRAM = Model_params × dtype_size × (1 + optimizer_multiplier + gradient_multiplier) 
           + activation_estimate 
           + framework_overhead_percentage
```

Where:
- `Model_params`: Parameter count from model specification
- `dtype_size`: 2 bytes (BFloat16/FP16) or 4 bytes (FP32)
- `optimizer_multiplier`: 2.0 for AdamW (maintains two state tensors: momentum, variance)
- `gradient_multiplier`: 1.0 (gradients same size as model)
- `activation_estimate`: Context-dependent (batch_size × sequence_length × hidden_dim × layer_count × checkpoint_factor)
- `framework_overhead_percentage`: 10-15% (accounts for PyTorch/framework internals, inter-GPU communication buffers if multi-device)

**Rationale:** This formula accounts for all major memory consumers while remaining computationally cheap to evaluate. The naive "model parameters only" calculation underestimates by 3-4×, leading to false negatives (approving infeasible configs). Framework-specific profiling (running memory traces) would be accurate but expensive, defeating the purpose of a lightweight early check. Our conservative overhead estimate (10-15%) provides safety margin without excessive false positives.

**Alternative Considered:** Framework-specific memory profiling via torch.cuda.memory_summary or similar tools. Rejected because: (1) requires model instantiation (expensive for large models), (2) framework-dependent (doesn't generalize), (3) too slow for early gate (~minutes to profile vs ~seconds to estimate).

**Example Calculation (Our Failure Case):**
```
Model: Mixtral-8x7B (47B parameters)
dtype: BFloat16 (2 bytes)

Model_memory = 47B × 2B = 94 GB
Optimizer_memory = 47B × 2B × 2 (AdamW states) = 188 GB
Gradient_memory = 47B × 2B × 1 = 94 GB
Activation_estimate = 50-100 GB (conservative, depends on batch size)
Framework_overhead = (94 + 188 + 94) × 0.10 = 37.6 GB

Total_required = 94 + 188 + 94 + 75 (mid-range activations) + 37.6 ≈ 488.6 GB
Available = 5× H100 (95GB each) = 475 GB
Status: INFEASIBLE (exceeds capacity by ~14 GB)
```

### Validation Threshold

**Decision:** Flag configurations requiring >85% of available VRAM capacity.

**Rationale:** Conservative threshold provides safety margin for estimation errors and dynamic memory fluctuations. In practice, frameworks often allocate memory in chunks, experience fragmentation, and require workspace buffers that aren't captured by static formulas. Using 100% threshold risks false negatives (approving borderline cases that fail at runtime). Using lower thresholds (70-75%) increases false positives unnecessarily, forcing reformulation of feasible experiments.

**Alternative Considered:** Dynamic threshold based on multi-GPU setup (stricter for distributed training due to inter-GPU communication overhead). We chose fixed 85% for simplicity, but this could be refined with framework-specific data.

### Gate Integration Protocol

**Workflow Integration:**
1. **Input:** Phase 2C experiment design specification (model name, dataset, task count, training steps)
2. **Estimation:** Apply memory formula using public model metadata (parameter count from model cards, HuggingFace repos)
3. **Validation:** Compare estimated requirement vs available hardware (query from system: nvidia-smi, resource allocation)
4. **Output:** PASS (≤85% capacity) or FAIL (>85% capacity)
5. **Action on FAIL:** 
   - Block Phase 3 approval
   - Surface reformulation options: (a) scale-down model, (b) reduce batch size, (c) justify expensive optimization investments, (d) secure additional hardware
   - Require explicit override with rationale if proceeding despite warning

**Cost:** ~5 minutes (fetch model specs, run calculation, generate report)
**Benefit:** Prevents 10-16 hours implementation waste (our case), or forces early hardware justification

## Retrospective Validation: Would This Have Caught Our Failure?

Applying the proposed gate to our failed experiment:

**Phase 2C Output:**
- Model: Mixtral-8x7B-v0.1 (47B parameters, BFloat16)
- Dataset: GLUE + SuperGLUE (17 tasks)
- Training: 5 epochs, batch size 32, gradient accumulation 4 steps
- Available hardware: 5× H100 NVL (95GB VRAM each = 475GB total)

**Gate Estimation (Phase 2C.5):**
- Model memory: 94 GB
- Optimizer memory (AdamW): 188 GB
- Gradient memory: 94 GB
- Activation estimate: ~75 GB (17 tasks, batch 32)
- Framework overhead: ~40 GB (10% of base)
- **Total required: ~491 GB**
- **Available: 475 GB**
- **Utilization: 103%** → **FAIL (exceeds 85% threshold)**

**Gate Action:**
- Block Phase 3 approval with message: "Estimated memory (491GB) exceeds available capacity (475GB, 103% utilization). Reformulation required."
- Suggest alternatives:
  - Scale-down to Mixtral-4x7B or GPT-2 (1.5B params)
  - Reduce task count from 17 to 3-5 (proof-of-concept scope)
  - Enable 8-bit quantization (reduces model to ~47GB, total ~350GB)
  - Justify acquiring additional GPUs or cloud capacity

**Outcome:** Would have prevented 10-16 hours of Phase 3-4 implementation on an infeasible configuration. Designer would have either: (a) reformulated to practical scale (scientific question preserved), or (b) explicitly justified resource expansion (informed decision).

## Design Considerations and Limitations

**Activation Memory Uncertainty:** Our formula uses a conservative estimate for activations because exact values depend on runtime factors (actual batch size, sequence lengths, gradient checkpointing strategy). False positives (flagging feasible configs as infeasible) could occur if actual activations are much smaller than estimated. Mitigation: provide override mechanism with rationale.

**Framework Variability:** PyTorch, JAX, and TensorFlow have different memory management strategies and overhead characteristics. Our 10-15% overhead is an approximation. Future work could maintain framework-specific calibration tables.

**Multi-GPU Efficiency Gap:** The formula assumes perfect parallelism (e.g., 5× 95GB = 475GB usable). In practice, inter-GPU communication buffers, activation synchronization, and framework-specific limitations reduce effective capacity. Our 85% threshold partially compensates but may still underestimate this gap for complex parallelism strategies.

**Optimizer-Specific Assumptions:** Formula assumes AdamW (2× parameters for momentum + variance). Other optimizers have different multipliers (SGD: 1×, Adafactor: ~0.5×). Gate should query optimizer from experiment specification.

Despite these limitations, the gate provides substantial value: catching egregious infeasibility cases (like our Mixtral-8x7B example) before implementation, at minimal cost. Refinements can improve accuracy, but even conservative estimates prevent the worst-case scenario of complete implementation on unrunnable configurations.
