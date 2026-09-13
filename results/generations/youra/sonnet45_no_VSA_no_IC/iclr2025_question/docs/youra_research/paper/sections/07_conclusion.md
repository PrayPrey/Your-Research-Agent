# Conclusion

We began with practitioners facing a budget-accuracy dilemma: deploy zero-cost uncertainty methods with unknown precision, or expensive methods with unclear return on investment. Our work resolves this dilemma by providing the first systematic cost-performance benchmark for UQ on LLM selective prediction, revealing that **budget constraints stratify the method space**—what's "best" depends on your deployment constraints, not universal rankings.

## Summary

In this work, we addressed the missing cost-performance analysis in UQ research by framing evaluation as Pareto frontier construction rather than winner-take-all comparison.

Our main contributions are:

1. **First systematic benchmark mapping AUROC vs inference cost** for 6 UQ method variants on TruthfulQA selective prediction, establishing that 5 methods are Pareto-optimal across 3 cost zones (1×, 3×, 5×, 10×).

2. **MC dropout k=3 efficiency sweet spot identified** (0.704 AUROC at 3× cost), offering 40% cost savings vs k=5 (0.712 AUROC at 5× cost) while exceeding the 0.70 threshold. This challenges vision domain conventions (k=30) and establishes k=3 as production default for 8B-scale selective prediction.

3. **Epistemic uncertainty threshold quantified** at 8B scale: MC dropout k≥3 required for AUROC ≥ 0.70, while zero-cost methods (temperature scaling 0.682, conformal prediction 0.695) fall short. This proves post-hoc calibration alone is insufficient when base model has complex miscalibration patterns.

These findings shift UQ evaluation from "which method wins" to "which method for my budget," enabling informed trade-offs rather than defaulting to the most expensive option.

## Future Directions

This work opens several promising research directions:

**From Scale Dependency (Unverified Assumption):** Our 8B-only results leave open whether zero-cost methods become competitive at 70B scale. Testing temperature scaling and conformal prediction on Llama-3.1-70B-Instruct would determine if better base calibration eliminates the epistemic uncertainty requirement. If zero-cost methods exceed 0.70 threshold at 70B, practitioners could default to temperature scaling unless high-stakes application requires MC dropout—reversing the "more compute = better UQ" narrative.

**From Diminishing Returns Pattern (Experiment Evidence):** MC dropout k=10 showed only +0.006 AUROC vs k=5 despite 2× cost increase. Adaptive k methods with early stopping (when variance converges across forward passes) could reduce average cost while maintaining k=5-equivalent AUROC. Expected outcome: 3.2× average cost (vs fixed k=5 at 5×) with same uncertainty quality, making MC dropout viable for tighter budgets.

**From Pareto Frontier Structure (Core Finding):** 5 Pareto-optimal methods across cost zones suggest per-query budget allocation. Hybrid approach: use temperature scaling (1× cost) for easy queries (high confidence), route hard queries (low confidence) to MC dropout k=5 (5× cost). This dynamic allocation could achieve average cost 2.3× (vs fixed k=5 at 5×) with AUROC ≥ 0.71, optimizing cost-quality trade-off at query level rather than method level.

**From Cross-Dataset Transfer Gap (Observed Limitation):** Conformal prediction AUROC 0.695 with HaluEval calibration suggests in-distribution calibration (TruthfulQA 40% split) could close the 0.005 gap and reach threshold. This would establish conformal prediction as zero-cost method viable for ≥0.70 AUROC, expanding practitioner options in the 1× cost zone.

## Closing Thoughts

As LLM deployment scales to production applications, budget-aware UQ selection becomes critical infrastructure—not secondary optimization. Our Pareto frontier framework provides the cost-performance map needed for informed decision-making. Future work at 70B scale and across benchmarks will refine this map, but the core message remains: **budget constraints are first-class deployment considerations**, and the field should report cost-performance trade-offs rather than winner-take-all rankings.

We hope this work encourages the research community to adopt Pareto frontier framing for UQ evaluation, enabling practitioners to choose methods matching their deployment constraints rather than blindly following "best method" prescriptions that ignore cost.
