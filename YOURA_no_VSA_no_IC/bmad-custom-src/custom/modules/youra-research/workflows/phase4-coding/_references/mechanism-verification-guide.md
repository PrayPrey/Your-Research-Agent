# Mechanism Verification Guide

> **Purpose:** Verify the hypothesis mechanism is ACTUALLY implemented, not just infrastructure.
> **Used by:** Phase 4 Validator (Phase 1.5b)

---

## Why Mechanism Verification Matters

- PoC must validate "mechanism works" not just "code runs"
- Prevents false positives (e.g., "compression code exists but never executes")
- Catches architecture mismatches early (e.g., KV cache on SSM models)

---

## Verification Steps

### Step 1: Load Mechanism Protocol

```python
experiment_brief = Read("{hypothesis_folder}/02c_experiment_brief.md")
mechanism_protocol = extract_section("Mechanism Verification Protocol")
```

### Step 2: Verify Pre-conditions

```python
preconditions = mechanism_protocol.preconditions
FOR condition in preconditions:
    IF condition.status != "TRUE":
        FAIL(f"Pre-condition not met: {condition.description}")
```

### Step 3: Search for Mechanism Activation Code

```python
activation_patterns = mechanism_protocol.activation_indicators
FOR indicator in activation_patterns:
    IF indicator.type == "log_message":
        mcp__serena__search_for_pattern(
            substring_pattern=indicator.expected_signal,
            relative_path=code_folder
        )
        IF no_match:
            FAIL(f"Mechanism log not found: {indicator.expected_signal}")

    IF indicator.type == "tensor_shape":
        mcp__serena__search_for_pattern(
            substring_pattern=indicator.tensor_shape_change,
            relative_path=code_folder
        )
```

### Step 4: Architecture Compatibility Check

```python
architecture_check = mechanism_protocol.architecture_compatibility

IF "SSM" in model_type AND "KV cache" in mechanism_required:
    FAIL("Architecture mismatch: SSM models do not have KV cache")

IF "Attention" in mechanism_required AND NOT has_attention_layer:
    FAIL("Architecture mismatch: Model lacks required Attention layers")
```

### Step 5: Verify Mechanism Toggle

```python
# Check if mechanism can be toggled for comparison
mcp__serena__search_for_pattern(
    substring_pattern="(enable_mechanism|use_compression|apply_method).*=.*(True|False)",
    relative_path=code_folder
)

IF no_toggle_found:
    WARN("No mechanism toggle found - cannot compare with/without")
```

---

## Result Schema

```json
{
  "mechanism_verification": {
    "passed": true|false,
    "preconditions_satisfied": true|false,
    "activation_code_found": true|false,
    "indicators_verifiable": true|false,
    "architecture_compatible": true|false,
    "issues": [
      {
        "type": "architecture_mismatch|missing_activation|no_toggle|precondition_failed",
        "description": "Detailed explanation",
        "file": "model.py",
        "line": 42,
        "suggested_fix": "Use Attention-based model instead of SSM"
      }
    ]
  }
}
```

---

## FAIL Conditions (IMMEDIATE STOP!)

| Condition | Description |
|-----------|-------------|
| Architecture mismatch | KV cache on Mamba, Attention on non-Transformer |
| Mechanism activation code not found | Core mechanism logic missing |
| Pre-conditions not satisfied | From 02c_experiment_brief.md |
| No way to measure effect | Cannot compare with/without mechanism |
| Required component missing | E.g., Attention layer for attention-based mechanism |

---

## Common Architecture Mismatches

| Mechanism | Requires | Incompatible With |
|-----------|----------|-------------------|
| KV Cache Compression | Transformer/Attention | SSM (Mamba), RNN |
| Attention Pattern Modification | Multi-Head Attention | Linear layers only |
| Gradient Checkpointing | Standard backprop | Non-differentiable ops |
| Speculative Decoding | Autoregressive model | Non-AR models |

---

*Reference file for Phase 4 Mechanism Verification*
