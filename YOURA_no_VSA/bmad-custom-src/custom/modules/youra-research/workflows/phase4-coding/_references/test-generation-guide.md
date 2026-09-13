# Test Generation Guide

> **Reference Document** - Used by step-02-coder-loop.md (Section 2c TEST Phase)

---

## SDD Philosophy: SPEC → TEST → IMPL → VERIFY

```
┌────────────────────────────────────────────────────────────────────┐
│ 🧪 SDD (Specification-Driven Development) Workflow │
├────────────────────────────────────────────────────────────────────┤
│ │
│ 📋 SPEC PHASE │
│ 0. Read and understand specs (03_logic.md, 03_config.md, etc.) │
│ │
│ 🧪 TEST PHASE (This Guide) │
│ 1. Generate tests dynamically based on spec understanding │
│ 2. Run pytest → EXPECT ImportError (module not exist yet) │
│ │
│ ⚙️ IMPL PHASE (code-generation-guide.md) │
│ 3. Search Archon KB → Exa fallback │
│ 4. Implement code to match specifications │
│ 5. Run pytest → MUST PASS │
│ │
│ ✅ VERIFY PHASE │
│ 6. Polish code (Archon best practices) │
│ 7. Run pytest → STILL PASS (spec compliance verified) │
├────────────────────────────────────────────────────────────────────┤
│ ⚠️ PYTEST SCOPE │
│ Coder (Step 2): pytest test_{module}.py (per-task file) │
│ Validator (Step 3): pytest tests/ (full integration) │
└────────────────────────────────────────────────────────────────────┘
```

---

## Core Principle: Spec Compliance Testing

```
┌─────────────────────────────────────────────────────────────────────┐
│ ❌ WRONG: Copy template → Replace variables (mechanical) │
│ ❌ WRONG: Write generic tests without reading specs │
│ │
│ ✅ CORRECT: Read spec files → Extract requirements → Generate │
│ tests that VERIFY implementation matches specs │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Test Generation from Spec Files

### 1. From 03_logic.md → API Compliance Tests

**Extract from spec:**
- Class names and method signatures
- Input/output tensor shapes (e.g., `[B, N, F] → [B, N, C]`)
- Parameter types and constraints

**Generate tests that verify:**
- Method exists with correct signature
- Input shape accepted matches spec
- Output shape matches spec annotation
- Parameter types enforced

```python
# Process:
# 1. Read 03_logic.md
# 2. Find: "class EncoderLayer" with "forward(x: Tensor[B,N,F]) -> Tensor[B,N,C]"
# 3. Generate test that:
# - Instantiates EncoderLayer with config from 03_config.md
# - Passes input with shape [B, N, F] where F matches spec
# - Asserts output.shape[-1] == C from spec
```

### 2. From 03_config.md → Config Validation Tests

**Extract from spec:**
- Dataclass field names and types
- Default values
- Value constraints (e.g., `hidden_dim > 0`)

**Generate tests that verify:**
- Config instantiates with defaults
- Field types match spec
- Default values match spec
- Invalid values raise appropriate errors

```python
# Process:
# 1. Read 03_config.md
# 2. Find: "hidden_dim: int = 256", "dropout: float = 0.1"
# 3. Generate test that:
# - Creates config with no args → check defaults match
# - Creates config with args → check values stored correctly
# - Passes invalid type → check TypeError raised
```

### 3. From 03_architecture.md → Structure Validation Tests

**Extract from spec:**
- Module file paths
- Import dependencies
- Component relationships

**Generate tests that verify:**
- Modules can be imported
- Expected classes exist in modules
- Dependencies resolve correctly

```python
# Process:
# 1. Read 03_architecture.md
# 2. Find: "models/encoder.py contains EncoderLayer"
# 3. Generate test that:
# - Imports from models.encoder
# - Asserts EncoderLayer is accessible
# - Verifies inheritance if specified
```

### 4. From 02c_experiment_brief.md → Reality Tests

**Extract from spec:**
- Mechanism verification protocol
- Expected behaviors

**Generate tests that verify:**
- Model is not a mock/fake (determinism, sensitivity, gradient flow)
- Mechanism activates as described

---

## Forbidden Test Patterns

```python
# ❌ FORBIDDEN - These are NOT real tests!

def test_placeholder(self):
    pass # ← FORBIDDEN

def test_todo(self):
    ... # ← FORBIDDEN

def test_always_passes(self):
    assert True # ← FORBIDDEN

def test_no_assertion(self):
    result = compute()
    # Missing assert! # ← FORBIDDEN
```

---

## Test Gate Requirements

| Check | Requirement | On Failure |
|-------|-------------|------------|
| **File exists** | `tests/test_{module}.py` | Block → Generate |
| **Real assertions** | No `pass`, `...`, `assert True` only | Block → Regenerate |
| **Minimum count** | ≥ 3 test methods | Block → Add more |
| **Spec coverage** | Tests reference spec requirements | Block → Add spec-based tests |

---

## Placeholder Detection Patterns

```python
placeholder_patterns = [
    r"def test_.*:\n\s+pass", # Empty with pass
    r"def test_.*:\n\s+\.\.\.", # Empty with ellipsis
    r"def test_.*:\n\s+assert True", # Always-pass assertion
    r"def test_.*:\n\s+#.*\n\s+pass", # Comment then pass
]
```

---

## Reality Tests (Mechanism Verification)

| Test Type | Purpose | Spec Source |
|-----------|---------|-------------|
| **Determinism** | Same input → same output | 02c_experiment_brief.md |
| **Sensitivity** | Different inputs → different outputs | 02c_experiment_brief.md |
| **Gradient Flow** | Gradients propagate | 02c_experiment_brief.md |
| **Weight Influence** | Weight changes affect output | 02c_experiment_brief.md |

> Generate based on "Mechanism Verification Protocol" section in 02c_experiment_brief.md

---

## Integration

| Phase | Guide | Focus |
|-------|-------|-------|
| 🧪 TEST | **This Guide** | Spec compliance test generation |
| ⚙️ IMPL | code-generation-guide.md | Implementation with Archon KB → Exa |
| ✅ VERIFY | mcp-tools-guide.md | Serena analysis, best practices |
