# Results

## Main Finding: Extraction Rate Failure

The existence test (H-E1) **failed** the primary criterion. Overall extraction rate was 49.5%, well below the 95% target.

| Component | Extraction Rate |
|-----------|-----------------|
| AS_loc | 49.5% |
| AS_state | 2.7% |
| AS_causal | 15.5% |

**Figure 1** shows extraction rates by component. The critical finding is the near-zero AS_state extraction (2.7%), indicating that variable-value information is almost never extractable from standard signals.

## Error Type Distribution

Analysis of the 639 collected failures reveals why extraction fails:

| Error Type | Count | Percentage |
|------------|-------|------------|
| Assertion | 341 | 53.4% |
| Other | 171 | 26.8% |
| Type | 116 | 18.2% |
| Syntax | 5 | 0.8% |

**Assertion errors dominate** (53.4%) and produce output like `AssertionError` or `assert X == Y` without file:line traceback frames in standard format. The regex patterns, designed for `File "X", line Y, in func` format, cannot extract location from assertion output.

## AS Ordering Preserved

Despite low absolute values, the expected ordering held:

| Condition | Mean AS_state |
|-----------|---------------|
| C1 | 0.09 |
| C2 | 0.09 |
| C3 | 0.00 |
| C4 | 0.00 |

**Ordering C1≥C2≥C3≥C4: PASS**

This suggests the AS *concept* may be valid—conditions designed to have higher AS do produce higher values—but the absolute extraction rate is insufficient for hypothesis testing.

## Component Independence

| | AS_loc | AS_state | AS_causal |
|---|--------|----------|-----------|
| AS_loc | 1.00 | 0.16 | 0.43 |
| AS_state | 0.16 | 1.00 | 0.17 |
| AS_causal | 0.43 | 0.17 | 1.00 |

All correlations < 0.5, confirming components are reasonably independent. **Figure 4** shows the correlation matrix.

## Extraction Success by Condition

**Figure 3** (extraction heatmap) reveals the condition × component success matrix. C1 and C2 show ~80% AS_loc extraction on type/runtime errors but <20% on assertion errors. The diagonal pattern confirms that higher-AS conditions achieve higher extraction *when extraction is possible*, but assertion errors block extraction across all conditions.

## Root Cause Analysis

The extraction failure traces to a **mismatch between pattern design and error output format**:

1. **Regex patterns assume full tracebacks:** `File "X", line Y, in func` format
2. **Assertion errors produce minimal output:** `AssertionError: assert expected == actual`
3. **No traceback frames in assertions:** pytest captures assertions differently than exceptions

This is not a bug in our implementation but a **boundary condition** of the regex operationalization: it requires traceback-rich error types.
