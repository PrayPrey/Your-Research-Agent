# Experiment Brief: H-M1 — Error Traces Contain Counterfactual Information

**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate:** MUST_WORK
**Prerequisites:** h-e1 (VALIDATED)
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

Under execution on buggy code, if compiler/test output is generated, then error traces contain counterfactual information ("if X were different, Y would not have failed"), because traces include line numbers, variable values, and expected vs actual outputs.

## 2. Research Background

### 2.1 Key Prior Work

| Source | Key Finding | Relevance |
|--------|-------------|-----------|
| LDB (ACL 2024) | Runtime execution traces with variable values at basic block boundaries enable step-by-step debugging | Direct: shows variable values are extractable from traces |
| Self-Debug (Chen 2023) | Execution feedback guides specific line edits | Supports: traces provide localization |
| CausalFlow (2025) | Counterfactual intervention on execution traces identifies failure-inducing steps | Direct: counterfactual structure in traces |
| InspectCoder (2025) | Log-augmented debugging collects dynamic variable info | Supports: variable state extraction |

### 2.2 Counterfactual Information Definition

Counterfactual information in error traces includes:
1. **Line localization**: "Error at line X" → "if line X were different..."
2. **Variable state**: "Expected Y, got Z" → "if variable were Y instead of Z..."
3. **Stack trace**: Call chain shows causal path to failure
4. **Type mismatch**: "Cannot add int to str" → "if type were correct..."

## 3. Experimental Design

### 3.1 Dataset

| Dataset | Size | Bug Types | Source |
|---------|------|-----------|--------|
| HumanEval-Bugs | 164 problems | Induced bugs (syntax, logic, type, off-by-one) | Generate from HumanEval correct solutions |
| MBPP-Bugs | 500 problems | Same bug categories | Generate from MBPP correct solutions |

**Bug Generation Protocol:**
1. Take correct solution from HumanEval/MBPP
2. Inject one bug per category:
   - **Syntax**: Missing colon, parenthesis, indentation
   - **Logic**: Wrong operator (< vs <=), wrong condition
   - **Type**: Wrong type conversion, type mismatch
   - **Off-by-one**: Index boundary errors, range endpoint

### 3.2 Variables

| Variable | Type | Operationalization |
|----------|------|-------------------|
| **IV: Execution feedback presence** | Binary | Code executed with test vs. no execution |
| **DV: Counterfactual information content** | Continuous | Counterfactual density score (0-1) |
| **Control: Bug type** | Categorical | 4 categories |
| **Control: Code complexity** | Continuous | LOC, cyclomatic complexity |

### 3.3 Procedure

**Step 1: Bug Injection (Automated)**
```python
def inject_bug(correct_code, bug_type):
    # Syntax: remove colon from if/for/def
    # Logic: flip comparison operator
    # Type: change int() to str() or vice versa
    # Off-by-one: change range(n) to range(n-1)
    return buggy_code, bug_location, bug_description
```

**Step 2: Execute and Collect Traces**
```python
def execute_and_trace(buggy_code, test_cases):
    result = sandbox.execute(buggy_code, test_cases)
    return {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'exit_code': result.exit_code,
        'traceback': result.traceback
    }
```

**Step 3: Annotate Counterfactual Structure**

For each error trace, annotate:
- **HAS_LINE**: Contains line number? (Y/N)
- **HAS_EXPECTED**: Contains expected value? (Y/N)
- **HAS_ACTUAL**: Contains actual value? (Y/N)
- **HAS_TYPE_INFO**: Contains type information? (Y/N)
- **HAS_VARIABLE_STATE**: Contains variable values? (Y/N)
- **IDENTIFIES_ROOT_CAUSE**: Points to actual bug location? (Y/N)

**Counterfactual Density Score:**
```
CF_score = (HAS_LINE + HAS_EXPECTED + HAS_ACTUAL + HAS_TYPE_INFO + HAS_VARIABLE_STATE) / 5
```

**Step 4: Validation**
- 100-sample human annotation for inter-rater reliability (κ > 0.7)
- Compare automated extraction to human annotation

### 3.4 Sample Size

| Component | Count | Rationale |
|-----------|-------|-----------|
| HumanEval problems | 164 | Full dataset |
| MBPP problems | 500 | Full dataset |
| Bug types per problem | 4 | Syntax, logic, type, off-by-one |
| Total buggy samples | 2,656 | (164 + 500) × 4 |
| Human annotation sample | 100 | For validation |

### 3.5 Success Criteria

**Primary (PoC Direction):**
- >70% of error traces contain extractable counterfactual information (CF_score ≥ 0.4)

**Secondary:**
- Counterfactual information correctly identifies bug root cause in >60% cases
- Inter-rater reliability κ > 0.7 on annotation scheme

**Failure Threshold:**
- <50% traces with CF_score ≥ 0.4 → EXPLORE alternative signal types

## 4. Implementation Specification

### 4.1 Data Pipeline

```
[Correct Solutions] → [Bug Injector] → [Buggy Code]
                                            ↓
[Test Cases] + [Sandbox] → [Execution Traces]
                                            ↓
[Trace Parser] → [Counterfactual Annotations]
                                            ↓
[Metrics Calculator] → [CF Density Scores]
```

### 4.2 Core Components

**TraceParser:**
- Input: Raw stderr/stdout from execution
- Output: Structured trace with line numbers, expected/actual values
- Reference: LDB trace parsing (github.com/FloridSleeves/LLMDebugger)

**CounterfactualAnnotator:**
- Input: Parsed trace
- Output: CF annotation vector [HAS_LINE, HAS_EXPECTED, ...]
- Method: Regex patterns + heuristic rules

**BugInjector:**
- Input: Correct code, bug_type
- Output: Buggy code with known bug location
- Validation: Verify bug causes test failure

### 4.3 Execution Environment

| Component | Specification |
|-----------|---------------|
| Sandbox | Docker container with Python 3.10 |
| Timeout | 10s per execution |
| Memory limit | 512MB |
| Test framework | pytest with captured output |

## 5. Baseline & Controls

### 5.1 Baselines

| Baseline | Purpose |
|----------|---------|
| No execution (static analysis only) | Control for execution-independent info |
| Execution without tests (compile only) | Isolate test-based counterfactual signal |

### 5.2 Controls

- Bug type stratified analysis
- Code complexity normalization
- Test coverage (problems with >1 test case)

## 6. Analysis Plan

### 6.1 Primary Analysis

1. Calculate CF_score distribution across all traces
2. Report: mean, median, std, 70th percentile
3. Hypothesis test: H0: mean CF_score ≤ 0.4 vs H1: mean CF_score > 0.4

### 6.2 Secondary Analysis

1. CF_score by bug type (ANOVA)
2. Root cause identification accuracy by bug type
3. Correlation: CF_score vs code complexity

### 6.3 Validation Analysis

1. Human vs automated annotation agreement (Cohen's κ)
2. Error analysis on disagreements

## 7. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Bug injection produces non-failing code | Verify each injected bug causes test failure |
| Trace parsing misses information | Manual validation on 100-sample subset |
| Annotation scheme ambiguity | Pre-register annotation guidelines, pilot with 20 samples |

## 8. Resource Requirements

| Resource | Estimate |
|----------|----------|
| Compute | ~3 hours (2,656 executions × 10s max) |
| Human annotation | ~4 hours (100 samples × 2-3 min) |
| Total duration | 1-2 days |

## 9. Output Artifacts

1. `h-m1/data/buggy_samples.jsonl` — All buggy code samples
2. `h-m1/data/execution_traces.jsonl` — Raw traces
3. `h-m1/data/cf_annotations.jsonl` — Counterfactual annotations
4. `h-m1/results/cf_scores.csv` — CF density scores
5. `h-m1/results/analysis_report.md` — Statistical analysis

---

## Sources

- [LDB: Large Language Model Debugger](https://arxiv.org/html/2402.16906v1)
- [LDB GitHub Implementation](https://github.com/FloridSleeves/LLMDebugger)
- [Revisit Self-Debugging with Self-Generated Tests](https://arxiv.org/abs/2501.12793)
- [CausalFlow: Counterfactual Repair for LLM Agent Failures](https://arxiv.org/pdf/2605.25338)
- [InspectCoder: Dynamic Analysis-Enabled Self Repair](https://arxiv.org/html/2510.18327v1)
