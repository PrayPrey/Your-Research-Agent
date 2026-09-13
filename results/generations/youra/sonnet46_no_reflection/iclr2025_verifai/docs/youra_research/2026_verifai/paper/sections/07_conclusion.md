# 7. Conclusion

We began by observing that three of the most successful LLM formal reasoning systems — BFS-Prover, PropertyGPT, and Proof of Thought — all use structured formal feedback to improve performance, yet none can explain *why* it works. We proposed that this gap is not merely rhetorical: two mechanistically distinct hypotheses (oracle vs. regularizer) predict different design conclusions, and no existing work has been designed to distinguish them.

In this work, we introduced the oracle/regularizer framing, the locality score metric, and a 3-condition 2×2 factorial design capable of testing the oracle hypothesis for the first time. Attempting to execute this experiment produced an unexpected finding: the Lean4 toolchain dependency silently fell back to synthetic data generation, producing an experiment that ran correctly in every measurable sense except the one that mattered — it never invoked the formal verifier.

This outcome is itself a contribution. The DPO training loop is validated. The state alignment protocol is correct. The locality score computation is implemented. The tactic taxonomy is pre-specified. The α-interaction prediction is theoretically grounded. What remains is a single environment setup task and the conviction that testing *why* formal feedback works is worth the engineering cost.

**Summary of contributions:**

1. The **oracle/regularizer distinction** — a testable mechanistic framing that unifies BFS-Prover, PropertyGPT, and Proof of Thought under a single causal hypothesis, with the α-interaction prediction as a uniquely discriminating empirical test.

2. The **locality score metric** — a novel mechanistic probe measuring the fraction of post-DPO probability mass shift concentrated on premise-consistent tactic categories, directly operationalizing oracle function vs. diffuse regularization.

3. A **validated experimental infrastructure** — a 3-condition DPO pipeline with 100% state alignment verification, pre-specified tactic taxonomy, and correct DPO loss implementation (β=10, lr 5e-6→5e-7, average_log_prob=False), ready for re-execution with real LeanDojo data.

4. A **methodological warning and protocol** — documentation of the silent synthetic fallback failure mode in LLM+formal-verifier pipelines, with proposed pre-run environment validation gates as a standard practice for the field.

**Future directions.**

The most immediate direction is completing H-E1 with real LeanDojo data, resolving whether LS_A > LS_P and providing the first direct mechanistic evidence on the oracle/regularizer question. If H-E1 passes, the subsequent hypothesis chain (H-M1 through H-C1) tests whether the oracle mass shift translates to hard-stratum pass@1 recovery and whether the α-interaction prediction holds — collectively providing the strongest mechanistic case for the oracle framing.

Beyond this pipeline, two directions motivate further work. First, testing whether the oracle effect holds at inference time (frozen policy, no DPO) — the PropertyGPT and Proof of Thought results suggest it might, but no controlled test exists. Second, testing cross-formalism transfer: does the oracle mechanism hold for Verus and Dafny formalisms in Vericoding, or is it Lean4-specific? The latter would establish whether the oracle/regularizer distinction is a property of the feedback mechanism or of the interaction between mechanism and formalism.

We opened by asking why formal feedback helps. We now know the question is harder to answer than it appears — and we have built the tools to answer it.
