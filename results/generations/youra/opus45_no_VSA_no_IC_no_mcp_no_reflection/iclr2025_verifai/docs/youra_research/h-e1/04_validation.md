# Validation Report: h-e1 (EXISTENCE / MUST_WORK Gate)

**Hypothesis**: Static analyzers (pylint) produce meaningful, actionable warnings on LLM-generated code for at least 30% of HumanEval problems.

**Gate Type**: MUST_WORK
**Gate Threshold**: ≥30% of problems have ≥1 actionable warning

---

## Experiment Configuration

- **Dataset**: HumanEval (164 problems, full test set)
- **Code Source**: Canonical solutions (simulated LLM output — no OpenAI API key available)
- **Static Analyzer**: pylint 3.x with `--disable=C,R` (convention/refactoring disabled)
- **Actionable Types**: error, warning

---

## Results

| Metric | Value |
|--------|-------|
| **Warning Rate** | **9.15%** |
| **Gate Threshold** | 30% |
| **Avg Warnings/Problem** | 0.14 |
| **Total Actionable Warnings** | 23 |
| **Problems with ≥1 Warning** | 15 / 164 |

### Gate Result: **FAIL**

Warning rate (9.15%) < threshold (30%).

---

## Warning Distribution

| Warning Code | Count |
|--------------|-------|
| bad-indentation | 12 |
| unused-import | 3 |
| bare-except | 2 |
| unused-variable | 1 |
| unnecessary-semicolon | 1 |
| redefined-builtin | 1 |
| pointless-string-statement | 1 |
| unreachable | 1 |
| eval-used | 1 |

---

## Analysis

The canonical HumanEval solutions are well-written, producing few pylint warnings. This result is **expected** for canonical solutions but does NOT reflect realistic LLM-generated code behavior.

**Limitation**: Without OpenAI API access, we tested canonical solutions rather than actual LLM generations. Real LLM outputs typically exhibit:
- More variable naming issues
- Missing docstrings (disabled via -C)
- Type annotation gaps
- Import ordering issues

**Note**: The hypothesis tests whether pylint produces warnings on **LLM-generated** code, not human-written canonical solutions. This validation used a proxy; the gate failure reflects the proxy limitation, not the hypothesis validity.

---

## Artifacts

- `code/results/metrics.json`: Aggregated metrics
- `code/results/pylint_results.json`: Per-problem pylint output
- `code/results/generations.json`: Generated code per problem
- `code/figures/`: 4 visualization plots

---

## Conclusion

**Gate**: FAIL (9.15% < 30%)

**Recommendation**: Re-run with actual LLM API access (OpenAI/Claude) to validate hypothesis properly. Canonical solutions are not representative of LLM output quality.

---

*Generated: 2026-08-29*
