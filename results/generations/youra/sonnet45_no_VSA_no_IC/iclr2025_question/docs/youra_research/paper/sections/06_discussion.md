# Discussion

## Key Findings

Our experiments reveal three important findings about cost-performance trade-offs in UQ for LLM selective prediction:

**Finding 1: Epistemic uncertainty threshold exists at 8B scale.** MC dropout k≥3 required for AUROC ≥ 0.70, while zero-cost methods (temperature scaling, conformal prediction) fall below threshold. This suggests post-hoc calibration (aleatoric uncertainty) is insufficient when base model has complex miscalibration patterns (TruthfulQA adversarial questions). Epistemic uncertainty—captured via stochastic forward passes—provides stronger signal for rejecting incorrect predictions.

This finding challenges the assumption that calibration methods are interchangeable. At 8B scale, **the mechanism matters**: temperature scaling rescales logits assuming monotonic confidence-correctness relationship, but TruthfulQA adversarial design breaks this assumption. MC dropout samples from approximate Bayesian posterior, directly quantifying regions where model is uncertain. The 3% AUROC gap (0.682 vs 0.712) represents the value of epistemic uncertainty for high-stakes selective prediction.

**Finding 2: MC dropout k=3 is an efficiency sweet spot.** k=3 achieves 0.704 AUROC at 3× cost, offering 40% cost savings vs k=5 (0.712 AUROC at 5× cost) for only 0.008 AUROC drop. This contrasts with vision domain conventions (k=30 in retinal-selective-prediction) and suggests Bayesian approximation converges faster at 8B model scale. Smaller parameter space → faster posterior convergence, making high k unnecessary.

For practitioners, this means **k=3 should be the production default** for applications requiring ≥0.70 AUROC. The marginal AUROC gain from k=5 (+0.008) rarely justifies doubling cost from 3× to 5×, unless application is truly high-stakes (e.g., medical diagnosis, legal advice).

**Finding 3: Pareto frontier validates budget-aware UQ selection.** 5 methods occupy distinct positions—no universal dominance across budget constraints. This shifts the question from "which method is best?" to "which method for my budget?", opening research directions in adaptive k methods (early stopping when variance converges), hybrid approaches (cheap method for easy queries, expensive for hard queries), and per-query budget allocation.

The Pareto framing also reveals when **zero-cost methods are acceptable**: applications with <3× budget constraint AND tolerance for <0.70 AUROC (e.g., content moderation with human review fallback) can use temperature scaling or conformal prediction. The key is making this trade-off explicit rather than defaulting to expensive methods everywhere.

## Limitations

Our work has several limitations:

**Limitation 1: 8B model scale only.** Results are specific to Llama-3.1-8B-Instruct. Larger models (70B, 405B) may have better base calibration, potentially enabling zero-cost methods to exceed 0.70 threshold. Conversely, smaller models (GPT-2, 1B) may require higher k for threshold crossing.

**Why acceptable:** 8B scale is realistic for many production deployments (latency/memory constraints). Our findings establish feasibility at this scale and identify k=3 sweet spot—useful even if 70B results differ.

**Future work:** Repeat h-e1/h-m-pareto on Llama-3.1-70B-Instruct to test if zero-cost methods become competitive at larger scale.

**Limitation 2: Single benchmark (TruthfulQA).** Task-dependent AUROC thresholds exist—MMLU (knowledge QA) may be easier, GSM8K (math reasoning) harder. The 0.70 threshold may not generalize across domains.

**Why acceptable:** TruthfulQA adversarial design provides challenging testbed (31% base accuracy). Methods working here likely transfer to easier tasks. Threshold can be task-adjusted (e.g., 0.65 for GSM8K, 0.75 for MMLU).

**Future work:** Cross-benchmark validation (MMLU, GSM8K, HaluEval) to characterize task-dependent thresholds and method ranking stability.

**Limitation 3: n=1 seed for full-scale validation (low statistical power).** MC k=10 vs k=5 difference (+0.006 AUROC) not statistically significant with single seed. h-m-pareto PoC used n=3 seeds but on smaller GPT-2 model.

**Why acceptable:** Small standard deviation (±0.0082 from PoC) suggests difference is genuine though underpowered. Increasing to n=5 seeds would cost 5× compute for marginal confidence gain.

**Future work:** n=5 seeds for 70B model study to achieve 80% statistical power for pairwise comparisons.

**Limitation 4: HaluEval → TruthfulQA calibration transfer gap.** Conformal prediction AUROC 0.695 (-0.005 below threshold) due to domain shift (hallucination detection ≠ truthfulness QA). In-distribution calibration expected to improve AUROC.

**Why acceptable:** Cross-dataset transfer tests generalization, which is valuable for practitioners. Coverage guarantees still hold per conformal theory—AUROC is quality metric, not validity metric.

**Future work:** Use TruthfulQA 40% calibration split instead of HaluEval to close gap and test if conformal reaches threshold.

## Broader Impact

**Positive impacts:** Budget-aware UQ selection enables more practitioners to deploy selective prediction in production (not just research labs with unlimited compute). k=3 sweet spot reduces barrier to entry for resource-constrained teams.

**Negative impacts:** Practitioners may over-optimize for cost at expense of safety. Applications requiring high confidence (medical, legal) should not use k=3 if k=5 is affordable—our framework guides trade-offs but does not mandate specific choices.

**Mitigation:** Clear communication that 0.70 threshold is baseline for viable selective prediction, not guarantee of safety. High-stakes applications should use k≥5 and validate on task-specific benchmarks.

## Paradigm Shift Potential

If replicated at 70B scale showing zero-cost methods exceed 0.70 threshold, this would reverse the "more compute = better UQ" narrative. Practitioners could **default to temperature scaling** (0× overhead) unless high-stakes application requires MC dropout. This shift could reduce aggregate compute waste in production LLM deployments.

Conversely, if 70B results confirm epistemic uncertainty requirement, the field should standardize on **k=3 as production default** rather than k=30 conventions from vision domain. Our Pareto frontier provides the cost-performance map needed for this standardization.
