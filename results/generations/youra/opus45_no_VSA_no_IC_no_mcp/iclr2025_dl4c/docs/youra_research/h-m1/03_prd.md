# Product Requirements Document: H-M1 — Error Traces Contain Counterfactual Information

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Version:** 1.0
**Date:** 2026-08-28

---

## 1. Executive Summary

This PRD defines requirements for validating H-M1: "Error traces contain counterfactual information that enables targeted code repair." The experiment will inject known bugs into correct solutions, execute buggy code, collect error traces, and measure the density of counterfactual information (line numbers, expected/actual values, type info, variable state).

**Success Criteria:** >70% of error traces contain extractable counterfactual information (CF_score ≥ 0.4).

---

## 2. Problem Statement

**Research Question:** Do execution error traces provide counterfactual signals ("if X were different, Y would not have failed") that can guide code repair?

**Hypothesis:** Under execution on buggy code, compiler/test output contains counterfactual information because traces include line numbers, variable values, and expected vs actual outputs.

**Gap:** Prior work (Self-Debug, LDB) assumes traces are useful but hasn't quantified counterfactual information density across bug types.

---

## 3. Functional Requirements

### FR-1: Bug Injection System
- **FR-1.1:** Inject syntax bugs (missing colon, parenthesis, indentation)
- **FR-1.2:** Inject logic bugs (wrong operator: < vs <=, wrong condition)
- **FR-1.3:** Inject type bugs (wrong type conversion, type mismatch)
- **FR-1.4:** Inject off-by-one bugs (index boundary, range endpoint)
- **FR-1.5:** Track bug location and description for ground truth

### FR-2: Execution and Trace Collection
- **FR-2.1:** Execute buggy code in sandboxed environment
- **FR-2.2:** Capture stdout, stderr, exit code, traceback
- **FR-2.3:** Handle timeout (10s) and memory limit (512MB)
- **FR-2.4:** Support pytest test framework

### FR-3: Counterfactual Annotation
- **FR-3.1:** Extract HAS_LINE (line number present)
- **FR-3.2:** Extract HAS_EXPECTED (expected value present)
- **FR-3.3:** Extract HAS_ACTUAL (actual value present)
- **FR-3.4:** Extract HAS_TYPE_INFO (type information present)
- **FR-3.5:** Extract HAS_VARIABLE_STATE (variable values present)
- **FR-3.6:** Calculate CF_score = sum(features) / 5

### FR-4: Root Cause Identification
- **FR-4.1:** Compare trace line number to actual bug location
- **FR-4.2:** Calculate root cause identification accuracy
- **FR-4.3:** Stratify by bug type

### FR-5: Human Validation
- **FR-5.1:** Sample 100 traces for human annotation
- **FR-5.2:** Calculate inter-rater reliability (Cohen's κ)
- **FR-5.3:** Target κ > 0.7

---

## 4. Data Specification

### 4.1 Input Datasets

| Dataset | Size | Source | Download |
|---------|------|--------|----------|
| HumanEval | 164 problems | OpenAI | Auto (datasets library) |
| MBPP | 500 problems | Google | Auto (datasets library) |

### 4.2 Generated Datasets

| Dataset | Size | Generation |
|---------|------|------------|
| HumanEval-Bugs | 164 × 4 = 656 | Bug injection from correct solutions |
| MBPP-Bugs | 500 × 4 = 2000 | Bug injection from correct solutions |
| Total Buggy Samples | 2,656 | 4 bug types per problem |

### 4.3 Output Artifacts

| Artifact | Format | Path |
|----------|--------|------|
| Buggy samples | JSONL | h-m1/data/buggy_samples.jsonl |
| Execution traces | JSONL | h-m1/data/execution_traces.jsonl |
| CF annotations | JSONL | h-m1/data/cf_annotations.jsonl |
| CF scores | CSV | h-m1/results/cf_scores.csv |
| Analysis report | Markdown | h-m1/results/analysis_report.md |

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Execution timeout: 10s per sample
- Total runtime: ~8 hours (2,656 × 10s max + parsing)
- Memory limit: 512MB per execution

### NFR-2: Reproducibility
- Fixed random seed for bug injection
- Deterministic trace parsing
- Version-locked dependencies

### NFR-3: Safety
- Docker sandbox for code execution
- No network access during execution
- Resource limits enforced

---

## 6. Success Criteria

### Primary Metrics
| Metric | Target | Threshold |
|--------|--------|-----------|
| CF_score ≥ 0.4 rate | >70% | ≥50% |
| Mean CF_score | >0.5 | ≥0.4 |

### Secondary Metrics
| Metric | Target |
|--------|--------|
| Root cause accuracy | >60% |
| Inter-rater κ | >0.7 |

### Gate Criteria
- **PASS:** >70% traces have CF_score ≥ 0.4
- **EXPLORE:** 50-70% traces have CF_score ≥ 0.4
- **FAIL:** <50% traces have CF_score ≥ 0.4

---

## 7. Dependencies

### 7.1 Python Packages
```
datasets>=2.14.0
pytest>=7.0.0
docker>=6.0.0
pandas>=1.5.0
numpy>=1.24.0
scipy>=1.10.0
pyyaml>=6.0
```

### 7.2 External References
| Reference | Purpose |
|-----------|---------|
| LDB (github.com/FloridSleeves/LLMDebugger) | Trace parsing patterns |
| HumanEval (github.com/openai/human-eval) | Dataset format |

### 7.3 Infrastructure
- Docker for sandboxed execution
- Python 3.10+ runtime

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bug injection produces passing code | Invalid samples | Verify each bug causes test failure |
| Trace parsing misses info | Undercount CF | Manual validation on 100 samples |
| Annotation ambiguity | Low κ | Pre-register guidelines, pilot 20 samples |

---

## 9. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup | 0.5 day | Environment, datasets loaded |
| Bug injection | 0.5 day | 2,656 buggy samples |
| Execution | 1 day | All traces collected |
| Annotation | 0.5 day | CF scores computed |
| Human validation | 0.5 day | κ calculated |
| Analysis | 0.5 day | Report complete |
| **Total** | **3 days** | |

---

## Appendix A: Bug Injection Examples

### Syntax Bug
```python
# Original
def add(a, b):
    return a + b

# Injected (missing colon)
def add(a, b)
    return a + b
```

### Logic Bug
```python
# Original
def is_positive(x):
    return x > 0

# Injected (wrong operator)
def is_positive(x):
    return x >= 0  # off-by-one at zero
```

### Type Bug
```python
# Original
def double(x):
    return x * 2

# Injected (wrong type)
def double(x):
    return str(x) * 2  # "33" instead of 6
```

### Off-by-One Bug
```python
# Original
def get_last(lst):
    return lst[len(lst) - 1]

# Injected
def get_last(lst):
    return lst[len(lst)]  # IndexError
```
