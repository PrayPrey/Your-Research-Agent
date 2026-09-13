# Phase 2C: Experiment Brief — H-E1

**Generated:** 2026-08-24
**Hypothesis ID:** h-e1
**Type:** EXISTENCE | **Gate:** MUST_WORK

## Hypothesis Statement

Pylint, mypy, and radon produce valid numeric outputs on ≥95% of LLM-generated code samples without crashing or null values.

## Success Criterion

≥95% valid output rate across all three SA tools (pylint, mypy, radon)

---

## 1. Dataset Specification

| Field | Value |
|-------|-------|
| **Name** | HumanEval + MBPP (combined) |
| **Type** | standard |
| **Source** | `openai/human-eval` (GitHub), `google-research-datasets/mbpp` (HuggingFace) |
| **Sample Count** | 164 (HumanEval) + 500 (MBPP test split: task_ids 11-510) = **664 total** |
| **Format** | JSONL with `task_id`, `prompt`, `canonical_solution` |

### Data Preparation Steps

1. Clone `openai/human-eval` repository
2. Load MBPP from HuggingFace: `datasets.load_dataset("google-research-datasets/mbpp")`
3. Extract canonical solutions as standalone Python files
4. Verify each file is syntactically valid Python (`ast.parse`)

---

## 2. Static Analysis Tools

| Tool | Version | Metric | Output Format |
|------|---------|--------|---------------|
| **pylint** | ≥2.17 | Score (0-10 float) | `--output-format=json` |
| **mypy** | ≥1.0 | Error count (int) | `--output=json` |
| **radon** | ≥6.0 | Cyclomatic complexity (int) | `radon cc --json` |

### Tool Wrapper Requirements

```python
def run_sa_tool(tool: str, code_path: str, timeout: int = 30) -> dict:
    """
    Returns:
        {"success": bool, "metric": float|int|None, "error": str|None}
    """
```

- Timeout: 30 seconds per file
- Exception handling: catch subprocess errors, parse errors
- Null detection: metric must be numeric, not None/NaN

---

## 3. Experiment Protocol

### 3.1 Procedure

1. **For each code sample** (N=664):
   - Write canonical solution to temp file
   - Run pylint, capture score
   - Run mypy, capture error count
   - Run radon cc, capture average complexity
   - Record success/failure per tool

2. **Aggregate metrics**:
   - `valid_rate_pylint = count(pylint_success) / N`
   - `valid_rate_mypy = count(mypy_success) / N`
   - `valid_rate_radon = count(radon_success) / N`
   - `overall_valid_rate = count(all_three_success) / N`

### 3.2 Success Definition

A tool run is "successful" if:
- No timeout (< 30s)
- No crash/exception
- Returns valid numeric metric (not None, not NaN)

### 3.3 Pass Criterion

**H-E1 PASSES if:** `min(valid_rate_pylint, valid_rate_mypy, valid_rate_radon) ≥ 0.95`

---

## 4. Baseline Comparison

Not applicable for EXISTENCE hypothesis. This tests tool coverage, not comparative performance.

---

## 5. Expected Outputs

| Output | Description |
|--------|-------------|
| `results/h_e1_coverage.json` | Per-sample success/failure for each tool |
| `results/h_e1_summary.json` | Aggregate valid rates |
| `results/h_e1_failures.json` | Failed samples with error messages |

### Summary Schema

```json
{
  "hypothesis": "h-e1",
  "n_samples": 664,
  "valid_rates": {
    "pylint": 0.98,
    "mypy": 0.97,
    "radon": 0.99
  },
  "min_valid_rate": 0.97,
  "pass": true
}
```

---

## 6. Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Malformed code crashes tools | Timeout + exception wrapper |
| Tool version incompatibility | Pin versions in requirements.txt |
| Encoding issues | Force UTF-8 encoding |
| Empty/stub solutions | Pre-filter with ast.parse |

---

## 7. Implementation Complexity

**Tier:** LOW
- No model training
- No GPU required
- Standard subprocess calls
- ~1 hour runtime estimate

---

## 8. References

- HumanEval: https://github.com/openai/human-eval (Chen et al., 2021)
- MBPP: https://huggingface.co/datasets/google-research-datasets/mbpp (Austin et al., 2021)
- Pylint: https://pylint.readthedocs.io/
- Mypy: https://mypy.readthedocs.io/
- Radon: https://radon.readthedocs.io/
- Related work: "Static Analysis as a Feedback Loop" (arXiv:2508.14419, 2025)
