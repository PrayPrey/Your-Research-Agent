# Conclusion

We opened by asking: what if we could catch ML reproducibility failures in seconds before training begins, rather than discovering them hours into experiments? Our results demonstrate this is achievable for 74.8% of environment-stage API defects through executable behavioral contracts.

We introduced three-tier contract validation—structural (import-time), metamorphic (runtime probes), and composition (bidirectional propagation)—achieving 80.46% detection rate with 72% false-negative-rate reduction versus CI-only baselines. Most critically, contracts shift defect detection from training-stage (67.9% baseline) to environment-stage (75.0%), reducing median time-to-first-failure from 10.08 hours to 0.51 hours—a 95% improvement validated through prospective trial simulation.

Our compositional design iteration (0% → 89.7% contractability via bidirectional propagation) illustrates a broader principle: early proof-of-concept limitations often reflect insufficient architectures rather than fundamental impossibility. By validating both forward compatibility (downstream libraries can consume upstream outputs) and backward recovery (upstream libraries handle downstream failures gracefully), we resolved what initially appeared to be a non-contractable defect category.

API contracts provide the missing reproducibility tier between dependency pinning and integration testing: library-level behavioral validation that generalizes across repositories while executing in <10 seconds at environment-setup. With 75% of ML repositories lacking testing infrastructure (Wolter et al.), contracts target the majority rather than the well-tested minority.

**Future Directions:** Immediate work includes auto-contract generation from docstrings (targeting ≥60% coverage), NLP/RL domain validation, and production inference deployment. Longer-term, we envision contract-aware library ecosystems where behavioral specifications ship alongside code—enabling install-time compatibility checking and semantic drift detection. Trace-based contract synthesis could address the 25.2% of defects involving undocumented or implicit invariants.

The path from late detection to early prevention is now clear: validate API behavioral assumptions at environment-setup, not hours into training. API contracts make this shift practical, systematic, and measurable.
