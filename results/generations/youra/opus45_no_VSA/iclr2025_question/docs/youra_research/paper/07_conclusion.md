# 7. Conclusion

We introduced Cross-Layer Trajectory Instability (CLTI), a framework for single-pass hallucination detection that measures how representations evolve across late transformer layers. Our experiments on TruthfulQA MC1 with LLaMA-2-7B validate the core hypothesis: Normalized Trajectory Instability (NTI) achieves AUROC 0.5657, and combined with Convergence Monotonicity Index (CMI) and final-layer entropy, improves detection by +7.1% over entropy alone (p = 1.15e-05).

Critically, we also report negative results. Trajectory metrics fail on low-entropy predictions (AUROC 0.5136), revealing fundamental coupling to the uncertainty regime. The Representational Competition Index (RCI) flip pattern appears in >90% of all responses regardless of correctness, exposing an architectural rather than epistemic phenomenon. These failures narrow the hypothesis scope: CLTI provides complementary signal for uncertain predictions, not a universal detector.

The callback to our opening observation: current hallucination detectors require either multiple forward passes or external knowledge bases. CLTI demonstrates that single-pass trajectory metrics add signal---with zero sampling overhead---but the signal is constrained to the high-entropy regime where the model already expresses uncertainty.

Future work should pursue entropy-orthogonal features (hidden state geometry, attention patterns) to address the confident-but-wrong failure mode, and validate on additional architectures. The RCI universality finding informs interpretability research: layer-wise token competition reflects iterative refinement in transformers, not epistemic uncertainty, and should be accounted for in future trajectory-based analyses.

Code and artifacts are available at [repository URL to be added].
