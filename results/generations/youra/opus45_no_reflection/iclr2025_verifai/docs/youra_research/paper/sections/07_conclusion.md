# Conclusion

We introduced the Actionable Specificity (AS) framework to explain why different verification signals yield different repair success rates in LLM-based code repair. AS decomposes feedback informativeness into localization (file:line presence), state exposure (variable values), and causal context (trace depth)—properties hypothesized to enable LLMs to localize bugs and infer fixes.

Our existence test on HumanEval and MBPP revealed a boundary condition: regex-based AS extraction achieves only 49.5% coverage, with near-zero state extraction (2.7%). The root cause is that assertion errors—which constitute 53% of benchmark failures and have the lowest repair success rates—produce minimal traceback output that standard patterns cannot parse.

This negative result resolves the paradox we opened with: the most difficult errors to repair are precisely those whose output format prevents extraction of actionable information. The mismatch is structural, not accidental.

**Contributions:**
1. The AS framework provides a principled decomposition for analyzing feedback informativeness.
2. We documented a boundary condition: assertion-dominated benchmarks require alternative operationalization.
3. We established that AS ordering holds (C1≥C2≥C3≥C4), suggesting the concept is valid even where extraction fails.

**Future Work:** Testing AS on traceback-rich error subsets (type errors, runtime exceptions), LLM-based extraction to parse assertion messages semantically, and richer diagnostic formats (structured assertion output with expected/actual values) represent promising directions.

The AS framework may yet explain feedback effectiveness—but only after addressing the extraction barrier that standard benchmarks impose.
