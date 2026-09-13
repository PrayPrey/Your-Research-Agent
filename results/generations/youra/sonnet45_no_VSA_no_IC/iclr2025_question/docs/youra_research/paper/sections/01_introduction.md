# Introduction

Practitioners deploying LLMs for high-stakes applications face a budget-accuracy dilemma: zero-cost uncertainty methods promise efficiency but may lack precision, while expensive methods like MC dropout improve performance at 5-10× inference overhead—yet no systematic cost-performance benchmark exists to guide this choice. Current UQ research reports winner-take-all rankings without cost analysis, leaving practitioners unable to choose appropriately for their deployment budgets. A production system with 5× cost tolerance cannot determine if MC dropout k=5 justifies the overhead vs temperature scaling at 0× cost.

This problem extends beyond simple performance comparison. While prior work has established that more expensive methods generally achieve better AUROC than zero-cost alternatives, **no study maps the complete cost-performance space**. Researchers focus on "which method wins" rather than "which method for my budget," treating cost as a secondary optimization rather than a first-class deployment constraint. The result: practitioners waste compute on unnecessarily expensive methods or deploy insufficient uncertainty quality for high-stakes predictions.

The gap is concrete: **no systematic benchmark compares AUROC vs inference cost across UQ method variants on the same task**. Cost reporting is inconsistent—k-values vary across studies, FLOPs are rarely measured, and the winner-take-all mindset obscures trade-off information. Without this cost-performance map, practitioners cannot make informed decisions matching their deployment constraints.

Our key insight is that **cost-performance trade-offs exist because different UQ mechanisms operate in distinct efficiency zones**—no single method dominates across all budget constraints. If multiple methods occupy the Pareto frontier (no method strictly dominates another), practitioners can choose based on budget. Temperature scaling at 1× cost vs MC dropout k=5 at 5× cost: neither dominates if temp scaling achieves lower AUROC but at zero overhead. This parallels CPU-GPU trade-offs: CPU cheap but slower, GPU expensive but faster—neither "wins" universally.

Building on this insight, we make the following contributions:

**First systematic cost-performance benchmark for UQ on LLM selective prediction.** We compare 6 UQ method variants (temperature scaling, conformal prediction, MC dropout k=1/3/5/10) on TruthfulQA selective prediction (817 human-annotated questions), measuring both AUROC and FLOPs-normalized inference cost. This Pareto frontier framing reveals the complete trade-off space rather than declaring a single winner.

**MC dropout k=3 efficiency sweet spot identified.** We find that k=3 achieves AUROC 0.704 (exceeding the 0.70 threshold) at 3× cost, offering 40% cost savings vs k=5 (0.712 AUROC at 5× cost). This challenges prior work using k=30 or higher, showing Bayesian approximation converges faster at 8B model scale.

**Epistemic uncertainty threshold quantified.** Zero-cost methods (temperature scaling 0.682, conformal prediction 0.695) fall below the 0.70 AUROC threshold, while MC dropout k≥3 exceeds it. This establishes that post-hoc calibration (aleatoric uncertainty) is insufficient for high-stakes selective prediction at 8B scale—epistemic uncertainty via stochastic forward passes is required.

**5 Pareto-optimal methods across 3 cost zones.** Our results show temperature scaling, conformal prediction, and MC dropout k=3/5/10 all occupy the Pareto frontier, confirming no universal dominance. This validates budget-aware UQ selection as a necessary framework, opening research directions in adaptive k methods, hybrid approaches, and per-query budget allocation.

We organize the paper as follows: Section 2 reviews prior UQ methods and identifies the missing cost-performance analysis. Section 3 presents our Pareto frontier methodology. Section 4 describes experimental setup on TruthfulQA. Section 5 presents results showing 5 Pareto-optimal methods. Section 6 discusses epistemic vs aleatoric uncertainty at 8B scale. Section 7 concludes with implications for budget-aware UQ selection.
