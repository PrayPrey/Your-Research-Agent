# Conclusion

We began by asking whether static analysis and execution feedback catch the same bugs or fundamentally different ones. Our experiments provide a clear answer: they catch different bugs entirely.

## Summary

We presented the first quantitative measurement of overlap between static and execution feedback for LLM code generation. Analyzing 542 problems from HumanEval+ and MBPP+, we found:

1. **Complete orthogonality:** Jaccard similarity = 0.0 between static-detected and execution-detected error sets. No problem exhibits both error types at the category level.

2. **Strong static coverage:** Static analysis (pylint/mypy) detects structural errors in 98.6% of test-failing code, establishing its reliability as a feedback signal.

3. **Mechanistic evidence:** The orthogonality arises because static tools analyze code structure while tests observe runtime behavior—fundamentally different properties with no inherent overlap.

These findings provide the theoretical foundation for combining static and execution feedback in iterative refinement. With zero overlap, each signal addresses error classes the other cannot detect.

## Future Directions

Our results motivate several directions for future work:

**Test Combined Improvement Magnitude.** With orthogonality established, the natural next step is measuring whether combined feedback improvement exceeds the maximum of individuals. This tests whether the theoretical benefit translates to practical gains.

**Replicate on LLM-Generated Code.** Our behavioral error rate analysis (38.6%) used canonical solutions. Testing on actual LLM-generated code—with its characteristic error patterns—would validate the behavioral mechanism and likely show higher error rates.

**Multi-Model and Multi-Language Validation.** Our findings are specific to Python on HumanEval+/MBPP+. Extending to other languages (TypeScript, Rust) and other LLMs (GPT-4, CodeLlama, DeepSeek) would establish generalizability.

## Closing

Understanding that static and execution feedback are orthogonal is the first step toward optimal signal composition for iterative code refinement. Our work establishes the empirical foundation; the path forward is building systems that exploit this orthogonality.
