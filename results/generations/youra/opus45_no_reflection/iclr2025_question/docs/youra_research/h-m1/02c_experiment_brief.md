# Experiment Design: H-M1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** Forward pass with hooks extracts hidden states without affecting generation
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Validates technical foundation: hook extraction is non-intrusive.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 VALIDATED (AUROC=0.8854)
**Gate Status:** MUST_WORK (100% output identity required)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** 100% output identity with/without hooks
- **Secondary:** Overhead < 10% inference time
- **Fail Action:** PIVOT to gradient-free extraction methods

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Status:** VALIDATED
- **AUROC:** 0.8854 (gate threshold: 0.60)
- **Dataset:** TriviaQA + Natural Questions + TruthfulQA
- **Model:** Llama-3-8B-Instruct
- **Proven:** Hidden states encode correctness signal at middle layers (60% depth)

**Reuse for H-M1:**
- Same model (Llama-3-8B-Instruct)
- Same evaluation samples (subset for verification)
- Controlled comparison: only hook presence changes

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**PyTorch Forward Hooks (Verified Stable):**
- `register_forward_hook(hook)` attaches read-only interceptor to any `nn.Module`
- Hook signature: `hook(module, input, output) -> None | modified_output`
- Returning `None` leaves output unchanged (non-intrusive read)
- Returning tensor replaces output (intervention mode - NOT used here)
- Source: PyTorch docs, HuggingFace transformers output_capturing.py

**Key Implementation Pattern:**
```python
# Non-intrusive hook - returns None, only reads
def capture_hook(module, input, output):
    storage[layer_idx] = output[0].detach().cpu()
    return None  # <-- Critical: no modification
```

### Archon Code Examples

**T5/Transformer Hidden State Access:**
- `outputs.last_hidden_state` available via `output_hidden_states=True`
- Alternative: Manual hooks at layer level for finer control

**TransformerLens HookPoint System:**
- Named positions (`blocks.{i}.hook_resid_post`)
- Context-scoped lifecycle (auto-cleanup)
- Source: TransformerLensOrg/TransformerLens

### Exa GitHub Implementations

**1. OATML/semantic-entropy-probes** (65 stars)
- Exact use case: hidden state extraction for uncertainty probing
- Uses HuggingFace `output_hidden_states=True` parameter
- Proven non-intrusive on Llama models

**2. joey-david/latent-correctness-probe** (5 stars)
- Direct predecessor: hidden state extraction for correctness prediction
- Config-driven CLI with hidden-state-extraction command
- Tested on reasoning models (Qwen)

**3. ASSERT-KTH/program-probes** (8 stars)
- Linear probes on hidden states for output property prediction
- Records hidden states at every assistant turn
- SWE-bench integration

**4. IvoBrink/RACDH** (1 star)
- Real-time attribution classifier on decoder hidden states
- 96% Macro-F1 on LLaMA-3.1-8B
- "No extra forward/backward passes" - confirms hook efficiency

**5. multigrid.ai Recorder Pattern:**
```python
class Recorder:
    def __enter__(self):
        for i, block in enumerate(self.blocks):
            self.handles.append(block.register_forward_hook(
                self._store(self.residual, i)))
        return self
    
    def __exit__(self, *exc):
        for h in self.handles:
            h.remove()  # Critical: cleanup prevents leaks
```

### 🎯 Implementation Priority Assessment

**CRITICAL: This is infrastructure verification, not paper reproduction.**

**Recommended Implementation Path:**
- Primary: `output_hidden_states=True` (HuggingFace native)
- Fallback: Manual `register_forward_hook` with context manager
- Justification: HuggingFace parameter is simplest; manual hooks needed only for layer-specific extraction

### Code Analysis (Serena MCP)

**Not applicable for H-M1:** This hypothesis tests PyTorch/HuggingFace standard API behavior, not codebase-specific implementation. The mechanism is fully documented in PyTorch and HuggingFace official sources.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA (subset)
**Type:** standard
**Source:** HuggingFace `trivia_qa`
**Sample Size:** 1000 examples (verification subset from H-E1's 17K validation)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `trivia_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc", split="validation[:1000]")
```

**Justification:** Same data as H-E1. 1000 samples sufficient for 100% identity verification (if any differs, test fails).

### Models

#### Baseline Model

**Architecture:** Llama-3-8B-Instruct (same as H-E1)
**Configuration:** 
- Layers: 32 transformer blocks
- Hidden dim: 4096
- Attention heads: 32

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
```

#### Proposed Model

**Architecture:** Same Llama-3-8B-Instruct WITH forward hooks attached

**Core Mechanism Implementation:**

```python
# Core Mechanism: Non-Intrusive Hidden State Extraction via Hooks
# Based on: PyTorch register_forward_hook, HuggingFace transformers
# Sources: TransformerLens, semantic-entropy-probes, multigrid Recorder

import torch
from contextlib import contextmanager

class HiddenStateExtractor:
    """
    Extract hidden states from transformer layers without affecting generation.
    Verified non-intrusive: hook returns None, only stores detached copy.
    """
    def __init__(self, model, layer_indices=None):
        self.model = model
        self.layer_indices = layer_indices or list(range(len(model.model.layers)))
        self.hidden_states = {}
        self.handles = []
    
    def _create_hook(self, layer_idx):
        def hook(module, input, output):
            # output is tuple: (hidden_state, ...)
            hidden = output[0] if isinstance(output, tuple) else output
            # .detach() breaks autograd graph (memory safety)
            # .cpu() moves off GPU (memory safety)
            # Returns None - NO modification to forward pass
            self.hidden_states[layer_idx] = hidden.detach().cpu()
            return None  # Critical: non-intrusive
        return hook
    
    def __enter__(self):
        self.hidden_states.clear()
        for idx in self.layer_indices:
            layer = self.model.model.layers[idx]
            handle = layer.register_forward_hook(self._create_hook(idx))
            self.handles.append(handle)
        return self
    
    def __exit__(self, *exc):
        for handle in self.handles:
            handle.remove()
        self.handles.clear()

# Usage (generation unchanged):
# with HiddenStateExtractor(model, layer_indices=[19]) as extractor:
#     output = model.generate(**inputs)
#     hidden_19 = extractor.hidden_states[19]
```

### Training Protocol

**N/A for H-M1:** This is a verification experiment, not a training experiment.

**Verification Protocol:**
1. Generate 1000 answers WITHOUT hooks (baseline)
2. Generate same 1000 answers WITH hooks attached
3. Compare outputs byte-by-byte
4. Measure inference time overhead

**Configuration:**
- Decoding: Greedy (deterministic for comparison)
- Max new tokens: 128
- Temperature: N/A (greedy)
- Seed: 42 (fixed for reproducibility)

### Evaluation

**Primary Metric:** Output Identity Rate
- Definition: % of generations that are byte-identical with/without hooks
- Target: 100.0%

**Secondary Metric:** Inference Time Overhead
- Definition: (time_with_hooks - time_without_hooks) / time_without_hooks × 100
- Target: < 10%

**Tertiary Metric:** Memory Overhead
- Definition: Peak GPU memory increase with hooks
- Target: < 20% (storing detached tensors on CPU)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Verification/Identity comparison
- Library: Built-in Python (no ML metrics needed)
- Code:
```python
def check_output_identity(outputs_without_hooks, outputs_with_hooks):
    """Returns (identity_rate, mismatches)"""
    assert len(outputs_without_hooks) == len(outputs_with_hooks)
    matches = sum(a == b for a, b in zip(outputs_without_hooks, outputs_with_hooks))
    return matches / len(outputs_without_hooks), [
        i for i, (a, b) in enumerate(zip(outputs_without_hooks, outputs_with_hooks))
        if a != b
    ]
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Output identity rate (100% target), Inference overhead (< 10%)

#### Additional Figures (LLM Autonomous)
- Inference time histogram: with vs without hooks
- Memory profile over generation steps
- Per-layer extraction overhead (if multiple layers tested)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: True (PyTorch hooks are standard API)
- `mechanism_isolatable`: True (hook vs no-hook is clean IV)
- `baseline_measurable`: True (outputs without hooks)

### Architecture Compatibility
- Llama-3-8B uses standard `nn.Module` layers
- All layers support `register_forward_hook`
- No custom CUDA kernels that bypass hooks

### Activation Indicators
- `mechanism_log_message`: "Hook registered for layer {idx}"
- `tensor_shape_change`: None expected (hooks read-only)
- `metric_delta_expected`: Identity rate = 100%, Overhead < 10%

### Mechanism Verification Code
```python
def verify_hook_non_intrusiveness(model, tokenizer, sample_texts):
    """
    Verify that hooks do not alter generation.
    Returns: (pass: bool, identity_rate: float, overhead_pct: float)
    """
    import time
    
    outputs_without = []
    outputs_with = []
    
    # Phase 1: Generate without hooks
    t0 = time.time()
    for text in sample_texts:
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
        outputs_without.append(tokenizer.decode(output[0], skip_special_tokens=True))
    time_without = time.time() - t0
    
    # Phase 2: Generate with hooks
    t0 = time.time()
    with HiddenStateExtractor(model, layer_indices=[19]) as extractor:
        for text in sample_texts:
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
            outputs_with.append(tokenizer.decode(output[0], skip_special_tokens=True))
    time_with = time.time() - t0
    
    # Verification
    identity_rate, _ = check_output_identity(outputs_without, outputs_with)
    overhead_pct = (time_with - time_without) / time_without * 100
    
    passed = (identity_rate == 1.0) and (overhead_pct < 10.0)
    return passed, identity_rate, overhead_pct
```

### Success Criteria
- `hypothesis_support_metric`: output_identity_rate
- `hypothesis_support_threshold`: 1.0 (100% identity required)
- Secondary: inference_overhead_pct < 10.0

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `output_identity_rate == 1.0` (100% identical outputs)
3. `inference_overhead < 10%` (secondary)

**Gate Result Interpretation:**
- PASS: Hooks are non-intrusive, proceed to H-M2
- FAIL: PIVOT to alternative extraction (gradient checkpointing, explicit layer calls)

---

## Appendix: Reference Implementations

### Primary References

1. **PyTorch Forward Hooks Documentation**
   - URL: https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.register_forward_hook
   - Key: Returns None for non-intrusive read

2. **HuggingFace Transformers output_capturing.py**
   - URL: https://github.com/huggingface/transformers/blob/main/src/transformers/utils/output_capturing.py
   - Key: Thread-safe hook collector pattern

3. **TransformerLens Hook System**
   - URL: https://transformerlensorg.github.io/TransformerLens/content/hook_system.html
   - Key: Context-scoped lifecycle, auto-cleanup

### Implementation References

4. **OATML/semantic-entropy-probes**
   - URL: https://github.com/OATML/semantic-entropy-probes
   - Key: Proven on Llama for uncertainty probing

5. **multigrid.ai Recorder Pattern**
   - URL: https://multigrid.ai/learn/visualize-llm-internals
   - Key: `.detach().cpu()` pattern, handle cleanup

6. **joey-david/latent-correctness-probe**
   - URL: https://github.com/joey-david/latent-correctness-probe
   - Key: Config-driven hidden-state-extraction for correctness probing

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18T15:03:08+00:00

### Workflow History for This Hypothesis
- 2026-08-18: H-M1 set to IN_PROGRESS by hypothesis loop
- Prerequisite H-E1: VALIDATED (AUROC=0.8854)
- Phase 2C: Experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
