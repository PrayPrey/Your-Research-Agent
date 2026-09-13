# 3. Methodology

## 3.1 Hypothesis Structure

We formulate our research question as a structured hypothesis with testable predictions:

**Core Hypothesis (H-StaticFeedback-v1):** Under iterative LLM code repair on HumanEval/MBPP, integrating static analyzer feedback (pylint/mypy) alongside execution feedback improves pass@k compared to execution-only feedback, because static analysis provides mechanistic error explanations.

**Causal Mechanism:**
1. Static analyzer produces warnings on LLM-generated code
2. LLM receives mechanistic feedback (why, not just where)
3. Targeted repairs lead to higher pass@k

**Key Assumptions:**
- A1: Static analyzers produce meaningful warnings on LLM code
- A2: LLMs can interpret static warnings into fixes
- A3: Static and execution feedback catch non-overlapping errors
- A4: HumanEval contains problems with static-detectable errors
- A5: Pylint severity filtering (disable conventions) is effective

## 3.2 Gate-Based Validation

We employ a hierarchical gate structure:

| Gate | Type | Hypothesis | Criterion |
|------|------|------------|-----------|
| h-e1 | MUST_WORK | Existence | ≥30% of problems have actionable warnings |
| h-m1 | MUST_WORK | Mechanism | LLM interprets warnings into fixes |
| h-m2 | SHOULD_WORK | Mechanism | Static/execution non-overlapping |
| h-c1 | SHOULD_WORK | Comparison | Improvement stratified by warnings |

MUST_WORK gates block downstream experiments if failed. This design catches methodology issues early.

## 3.3 Experimental Design

**Variables:**
- Independent: Feedback type (execution-only vs. static+execution)
- Dependent: pass@1, pass@5, pass@10
- Controlled: Base LLM, iteration budget (5), prompt format, static analyzer (pylint)

**Dataset:** HumanEval (164 problems)

**Static Analysis Configuration:**
```python
pylint_config = {
    "disabled_categories": ["C", "R"],  # Convention, Refactoring
    "enabled_types": ["error", "warning"],
    "output_format": "json"
}
```

## 3.4 Existence Gate Protocol

Before full pass@k evaluation, we validate the existence assumption: do static analyzers produce actionable warnings on benchmark code?

**Protocol:**
1. Load all HumanEval problems
2. Extract code (canonical solutions or LLM generations)
3. Run pylint with configured filters
4. Count problems with ≥1 actionable warning
5. Gate passes if warning_rate ≥ 30%

**Rationale:** If most solutions have zero warnings, static analysis provides no signal—the intervention is null.

## 3.5 Metrics

- **Warning Rate:** Fraction of problems with ≥1 actionable warning
- **Warnings per Problem:** Average actionable warnings
- **Warning Distribution:** Breakdown by pylint code (bad-indentation, unused-import, etc.)

For future pass@k evaluation:
- **pass@k:** Fraction of problems solved within k attempts
- **Stratified Analysis:** pass@k on warning-present vs. warning-absent subsets
