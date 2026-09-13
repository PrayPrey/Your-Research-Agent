# Mechanism Verification Protocol Template

> **Purpose:** Define HOW Phase 4 should verify that the mechanism actually works, not just that code runs.

## Why This Matters

- PoC must validate "mechanism works" not just "code runs without errors"
- Prevents false positives (e.g., code exists but mechanism never activates)
- Catches architecture mismatches early (e.g., KV cache on SSM models)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | [Verify architecture supports this mechanism] | {{UNFILLED:mechanism_exists}} |
| Mechanism Isolatable | [Can be enabled/disabled for comparison] | {{UNFILLED:mechanism_isolatable}} |
| Baseline Measurable | [Baseline without mechanism can be measured] | {{UNFILLED:baseline_measurable}} |

### Architecture Compatibility Check

{{UNFILLED:architecture_compatibility}}

**Required Features:**
- [e.g., Attention layers for KV cache, SSM for state compression]

**Incompatible Architectures:**
- [e.g., Pure SSM models for KV cache mechanism]

> ⚠️ If architecture is incompatible, Phase 4 MUST fail early!

---

### Mechanism Activation Indicators

**How to detect if mechanism is actually working:**

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | {{UNFILLED:mechanism_log_message}} | [logging location] |
| Tensor Shape | {{UNFILLED:tensor_shape_change}} | [model.py:forward()] |
| Metric Delta | {{UNFILLED:metric_delta_expected}} | [evaluate.py] |

**Activation Verification Code (Phase 4 must implement):**

```python
{{UNFILLED:mechanism_verification_code}}
```

**Example Implementation:**
```python
# Example: KV cache compression verification
def verify_mechanism_activated(experiment_log, results):
    indicators = {
        "log_found": "Compression applied" in experiment_log,
        "shape_changed": results["kv_shape_before"] != results["kv_shape_after"],
        "effect_measured": results.get("accuracy_with") != results.get("accuracy_without")
    }
    return all(indicators.values()), indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| No activation log | Log file missing expected message | FAIL: Mechanism not triggered |
| Tensor unchanged | Shape before == shape after | FAIL: Mechanism not applied |
| Zero effect | metric_with == metric_without | FAIL: Mechanism has no impact |
| Architecture mismatch | Required component missing | FAIL: Wrong model architecture |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Log/tensor check |
| Effect Measurable | Δ > 0 | Before/after comparison |
| Hypothesis Supported | {{UNFILLED:hypothesis_support_threshold}} | {{UNFILLED:hypothesis_support_metric}} |

---

## Placeholder Reference

| Placeholder | Description |
|-------------|-------------|
| `mechanism_exists` | TRUE if architecture supports the mechanism |
| `mechanism_isolatable` | TRUE if can be toggled on/off |
| `baseline_measurable` | TRUE if baseline can run independently |
| `architecture_compatibility` | Specific requirements description |
| `mechanism_log_message` | Expected log string when mechanism activates |
| `tensor_shape_change` | Expected shape transformation |
| `metric_delta_expected` | Expected performance difference |
| `mechanism_verification_code` | Pseudo-code for verification |
| `hypothesis_support_threshold` | Quantitative success threshold |
| `hypothesis_support_metric` | Which metric determines success |
