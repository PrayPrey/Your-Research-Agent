# 5. Results

## 5.1 Existence Gate Outcome

**Gate Result: FAIL**

| Metric | Value | Threshold |
|--------|-------|-----------|
| Warning Rate | 9.15% | ≥30% |
| Problems with ≥1 Warning | 15 / 164 | — |
| Total Warnings | 23 | — |
| Avg Warnings/Problem | 0.14 | — |

The existence gate failed: only 9.15% of canonical solutions had actionable pylint warnings, well below the 30% threshold.

## 5.2 Warning Distribution

| Warning Code | Count | Description |
|--------------|-------|-------------|
| bad-indentation | 12 | Incorrect indentation |
| unused-import | 3 | Imported but unused |
| bare-except | 2 | Catching all exceptions |
| unused-variable | 1 | Defined but unused |
| unnecessary-semicolon | 1 | Trailing semicolon |
| redefined-builtin | 1 | Shadowing builtin |
| pointless-string-statement | 1 | String with no effect |
| unreachable | 1 | Code after return |
| eval-used | 1 | Using eval() |

**Figure 1:** Warning type breakdown (see `warning_type_breakdown.png`)

## 5.3 Analysis

The low warning rate on canonical solutions is **expected behavior**. HumanEval canonical solutions are curated, high-quality reference implementations written by humans. They represent a floor, not a ceiling, for static warning rates.

**Key insight:** Canonical solutions ≠ LLM-generated code. This proxy does not test the hypothesis.

LLM-generated code typically exhibits:
- More undefined variable issues
- Type annotation gaps
- Incomplete edge-case handling
- Import ordering problems

The 9.15% rate establishes a baseline but cannot predict LLM output behavior.

## 5.4 Gate Mechanism Validation

The MUST_WORK gate correctly halted the pipeline:
- h-e1 FAIL → h-m1, h-m2, h-c1 blocked
- No downstream experiments wasted on invalid proxy
- Methodology limitation identified before full evaluation

This demonstrates the gate design working as intended—catching issues early rather than propagating through expensive experiments.
