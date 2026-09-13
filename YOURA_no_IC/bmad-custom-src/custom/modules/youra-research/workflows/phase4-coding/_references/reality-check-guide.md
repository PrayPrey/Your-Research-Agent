# General Reality Check Guide (Pattern-Free Mock Model Detection)

> **Purpose:** Detect ANY mock/fake model through behavioral tests, not code patterns.
> **Used by:** Phase 4 Validator (Phase 1.5b-2), Step 6 Gate Processing (Section 4.6)

---

## Why Pattern Matching Is Insufficient

| Detection Method | Catches | Misses |
|------------------|---------|--------|
| `MockWrapper` pattern | Specific named mocks | Renamed mocks, indirect random |
| `torch.randn` pattern | Direct random calls | `np.random`, seeded random, lookup tables |
| **Behavioral tests** | ALL fake models | Only intentionally adversarial mocks |

**Example:** MockSEDDWrapper uses `torch.randn()` for hidden states. Pattern matching might catch "MockSEDD" but would miss if renamed to "FastSEDDWrapper" or if random is called indirectly.

---

## Mandatory Reality Tests

| Test | What It Detects | Pass Condition |
|------|-----------------|----------------|
| **Determinism** | Raw random outputs | Same input → identical output |
| **Sensitivity** | Constant/identity functions | Different inputs → different outputs |
| **Smoothness** | Hash-based/chaotic fakes | Similar inputs → similar outputs |
| **Gradient Flow** | Non-differentiable fakes | Gradients exist and propagate |
| **Weight Influence** | Weightless/hardcoded fakes | Model weights affect output |

### Critical vs Supplementary Tests

| Category | Tests | On Failure |
|----------|-------|------------|
| **Critical** | determinism, sensitivity, smoothness | Gate = FAIL |
| **Supplementary** | gradient_flow, weight_influence | Warning only |

---

## Implementation Guidelines (Dynamic - Adapt to Your Model!)

```
┌─────────────────────────────────────────────────────────────────────┐
│ ❌ WRONG: Copy the template function as-is │
│ ✅ CORRECT: Understand the principles → Implement for YOUR model │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Dynamic Implementation?

Different models have different forward signatures:
- Simple: `model(x)`
- GNN: `model(x, edge_index)`
- Transformer: `model(x, attention_mask)`
- Diffusion: `model(x, timestep)`

**You MUST adapt the reality check to match your model's API from 03_logic.md!**

### Implementation Process

```python
# Step 1: Read 03_logic.md to understand model's forward signature
# Example: "forward(x: Tensor[B,N,F], edge_index: Tensor[2,E]) -> Tensor[B,N,C]"

# Step 2: Read 02c_experiment_brief.md for model-specific test requirements
# Example: "Reality tests require graph structure for GNN models"

# Step 3: Implement reality check that matches YOUR model's API
def reality_check_for_your_model(model, test_data, device="cuda"):
    """
    Implement based on the 5 PRINCIPLES below.
    Adapt the model call to match YOUR model's forward signature.
    """
    results = {}
    model.eval()

    # Adapt model call to YOUR model's signature from 03_logic.md
    # Example for GNN: out = model(x, edge_index)
    # Example for Transformer: out = model(x, attention_mask)

    # ... implement tests using the principles below ...

    return results
```

### The 5 Test Principles (MUST Implement All!)

| Test | Principle | How to Verify | Pass Condition |
|------|-----------|---------------|----------------|
| **Determinism** | Same input → Same output | Call model twice with identical input | `torch.allclose(out1, out2)` |
| **Sensitivity** | Different inputs → Different outputs | Call model with 2 different inputs | `NOT torch.allclose(out_a, out_b)` |
| **Smoothness** | Small input change → Proportional output change | Perturb input slightly, check output delta | `0.001 < ratio < 10000` |
| **Gradient Flow** | Gradients propagate through model | Enable grad, call backward, check grad exists | `x.grad is not None` |
| **Weight Influence** | Changing weights affects output | Perturb weights, check output changes | `NOT torch.allclose(out_orig, out_mod)` |

### Test Implementation Reference (Adapt to Your Model!)

```python
# ═══════════════════════════════════════════════════════════════
# Test 1: DETERMINISM
# ═══════════════════════════════════════════════════════════════
# Call YOUR model twice with same input
out1 = model(...) # Use YOUR model's signature
out2 = model(...) # Same inputs
results['determinism'] = torch.allclose(out1, out2, rtol=1e-5, atol=1e-5)

# ═══════════════════════════════════════════════════════════════
# Test 2: SENSITIVITY
# ═══════════════════════════════════════════════════════════════
# Call YOUR model with 2 meaningfully different inputs
out_a = model(input_a, ...) # First input
out_b = model(input_b, ...) # Different input
results['sensitivity'] = not torch.allclose(out_a, out_b, rtol=1e-3, atol=1e-3)

# ═══════════════════════════════════════════════════════════════
# Test 3: SMOOTHNESS
# ═══════════════════════════════════════════════════════════════
# Perturb primary input tensor slightly
x_perturbed = x + torch.randn_like(x) * 0.001
out_original = model(x, ...)
out_perturbed = model(x_perturbed, ...) # Keep other args same
# Check ratio is reasonable (not chaotic)

# ═══════════════════════════════════════════════════════════════
# Test 4: GRADIENT FLOW
# ═══════════════════════════════════════════════════════════════
x = x.requires_grad_(True)
out = model(x, ...)
out.sum().backward()
results['gradient_flow'] = (x.grad is not None)

# ═══════════════════════════════════════════════════════════════
# Test 5: WEIGHT INFLUENCE
# ═══════════════════════════════════════════════════════════════
# Store original output, perturb weights, check output changes
```

### Expected Return Schema

```python
return {
    'passed': all_critical_pass, # determinism + sensitivity + smoothness
    'tests': {
        'determinism': True/False,
        'sensitivity': True/False,
        'smoothness': True/False,
        'gradient_flow': True/False,
        'weight_influence': True/False
    },
    'verdict': 'REAL_MODEL' if all_critical_pass else 'MOCK_DETECTED'
}
```

---

## Result Schema

```yaml
mechanism_reality_check:
  passed: true|false
  verdict: "REAL_MODEL"|"MOCK_DETECTED"|"NOT_IMPLEMENTED"|"NOT_RUN"
  tests:
    determinism: true|false # Same input → same output
    sensitivity: true|false # Different inputs → different outputs
    smoothness: true|false # Similar inputs → similar outputs
    gradient_flow: true|false # Gradients propagate
    weight_influence: true|false # Weights affect output
  failure_reason: null|"Non-deterministic output"|"Input-independent"|"Non-smooth"
```

---

## Failure Examples

| Scenario | Detection | Gate Result |
|----------|-----------|-------------|
| MockSEDDWrapper returns `torch.randn()` | Determinism test: outputs differ for same input | FAIL |
| Fake model returns constant tensor | Sensitivity test: output unchanged by input | FAIL |
| Hash-based mock (`hash(input) % N`) | Smoothness test: non-proportional output changes | FAIL |
| Seeded random (appears deterministic) | Sensitivity + Smoothness tests combined | FAIL |
| Model wrapper ignores pretrained weights | Weight influence test | WARNING |

---

## Integration Points

### Phase 4 Validator (Step 3)

1. Verify `general_reality_check()` function exists in generated code
2. During runtime validation, check experiment output for reality check results
3. Report failures with specific test names

### Step 5c Post-Validation (Section 3.5)

1. Load reality check results from `experiment_results.json`
2. If ANY critical test fails → `MOCK_MODEL_DETECTED`
3. Route back to Step 2 for code fix (max 3 retries)
4. If max retries exceeded → mark as BLOCKED

**Note:** Mock model detection is a CODE problem (Step 2), not a hypothesis problem (Step 6b).

---

## Limitations

| Bypass Method | Description | Mitigation |
|---------------|-------------|------------|
| `torch.manual_seed(hash(input))` | Deterministic but fake | Caught by sensitivity + smoothness |
| Pre-computed lookup table | Smooth but not real | Weight influence test warns |
| Small dummy model | Passes all tests | Check model size, compare to baseline |

**Note:** These tests catch most unintentional mocks. Intentionally adversarial mocks require additional validation (e.g., comparison with known baseline outputs).

---

*Reference file for Phase 4 Reality Check*
