# Related Work

Our work builds on three lines of research: (1) studies of benchmark generalization and distribution shift, (2) analyses of benchmark concentration and selection bias, and (3) methods for measuring ranking stability across evaluation contexts.

## Benchmark Generalization and Distribution Shift

Recht et al. (2019) created ImageNet-V2 by replicating the original ImageNet data collection methodology a decade later. They found that all tested models experienced 11-14% accuracy drops on the new test set, demonstrating that performance gains on ImageNet do not fully transfer to independently-collected data with the same task semantics. Crucially, they observed that "accuracy gains on the original test set translate to roughly the same gain on the new test set," suggesting proportional degradation—a finding our work quantifies via ranking correlation.

Taori et al. (2020) introduced the concept of "effective robustness," showing a linear relationship between in-distribution accuracy and out-of-distribution accuracy across multiple distribution shifts. Their work implies that if the relationship is linear, rankings should be preserved—consistent with our findings. However, they did not explicitly compute ranking correlations.

Miller et al. (2021) studied distribution shift in question answering, finding that model rankings can shift substantially when evaluation data changes. Their finding of ranking instability in NLP contrasts with our finding of stability in vision, suggesting domain-specific effects worthy of further investigation.

## Benchmark Concentration and Selection Bias

Koch et al. (2021) documented the "reduced, reused, and recycled" nature of machine learning datasets, showing that the top 10% of NLP datasets account for the same usage as the remaining 90% combined. This concentration creates conditions for benchmark-specific optimization.

Dehghani et al. (2021) formalized the "benchmark lottery" phenomenon, demonstrating that model rankings on SuperGLUE tasks depend heavily on which tasks are selected. By re-computing aggregate scores with different task combinations, they showed that apparent leaders may be artifacts of task selection. While their work focused on task selection within a benchmark, ours focuses on generalization across benchmark variants.

Beyer et al. (2020) asked "Are we done with ImageNet?" and documented ceiling effects and label noise issues, questioning whether continued progress on ImageNet reflects genuine capability improvements. Their concerns motivate our investigation of whether ImageNet-based rankings transfer to cleaner evaluation settings.

## Ranking Stability Measurement

Kendall-τ and Spearman-ρ are standard metrics for comparing rankings across contexts. Prior work in information retrieval has used these metrics to assess ranking stability under query variations [Voorhees, 2000]. In machine learning evaluation, these metrics are less commonly applied—our work fills this gap for benchmark comparison.

## Our Position

Existing work established that (1) accuracy drops on alternative benchmarks, (2) benchmark concentration is severe, and (3) task selection affects rankings. However, no prior study systematically computed ranking correlations between ImageNet and ImageNet-V2 leaderboards. We address this gap, finding—contrary to intuition from accuracy drops—that rankings are highly stable. This extends Recht et al.'s work from accuracy measurement to ranking stability analysis.
