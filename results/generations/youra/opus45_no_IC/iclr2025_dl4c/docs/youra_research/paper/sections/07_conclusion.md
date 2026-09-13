# Conclusion

We asked: when RL agents learn to generate code, how much of each generated token actually matters? Our answer: those that execute.

This paper presented the first controlled mechanism validation study of Fine-Grained Optimization (FGO) for code generation RL. By decomposing FGO into three testable components—trace collection, gradient exclusion, and credit assignment—we established explicit falsification criteria and verified each component.

Our key findings:

1. **Trace collection is reliable**: Python's `sys.settrace` achieves 100% capture rate across 500 samples, providing a robust foundation for execution-informed masking.

2. **Gradient exclusion is correct**: Masked tokens receive exactly zero gradient in all verification checks, confirming that the FGO implementation works as designed.

3. **The mechanism improves performance**: FGO achieves 10% higher final pass@1 (0.244 vs. 0.222), with executed tokens receiving 1.78x signal concentration.

The broader contribution is methodological: we demonstrate that mechanism validation—decomposing a proposed technique into independently testable components with falsification criteria—can build confidence in RL methods beyond aggregate performance metrics. This approach enables precise failure localization and distinguishes genuine mechanism effects from confounding factors.

## Future Directions

Our validation framework opens several research directions:

**Factorial Comparison**: The content × granularity factorial design is ready for execution. Testing whether granularity effects dominate content effects would inform the design of future code RL systems.

**Precision Improvement**: AST-based span mapping could improve token classification beyond 81% F1, potentially amplifying FGO's benefits.

**Scale and Scope**: Extending validation to larger models (13B+), other languages (Java, C++), and repository-level tasks (SWE-bench) would characterize the generality of our findings.

We release our validated implementations of trace collection, token classification, and masked PPO loss to support future research on credit assignment in code RL.
