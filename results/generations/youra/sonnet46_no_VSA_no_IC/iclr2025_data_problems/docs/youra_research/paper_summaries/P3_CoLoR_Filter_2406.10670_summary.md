# Paper Summary: CoLoR-Filter: Conditional Loss Reduction Filtering
**arXiv:** 2406.10670 | **Citations:** 19 | **Year:** 2024
**Authors:** David Brandfonbrener et al.

### Key Contributions
- 11-25x data efficiency via loss differential filtering: select data that reduces target task loss
- Per-task targeted selection from C4 dataset
- Shows filtering can be conditioned on specific downstream tasks/benchmarks
- Demonstrates task-specific data attribution is feasible at moderate scale

### Methodology
- For each target task, compute: loss(datum | model trained on S) - loss(datum | reference model)
- Select data with highest loss reduction score for target task
- Applied to Books, QA, code tasks from C4
- Compared against random selection, PPL-based filtering, DSIR

### Experiments & Results
- 11-25x data reduction with matched or better performance on target tasks
- Task-specific filtering outperforms general quality filtering for targeted benchmarks
- PPL-based quality filtering is not task-aware — treats all benchmarks equally
- Books-targeted filter improves BoolQ/reading comprehension more than MMLU knowledge tasks

### Limitations & Gaps
- Requires target task proxy at filtering time — not available in pre-training at scale
- Applied to C4, not The Pile — cannot directly use Pythia infrastructure
- Does not provide cross-filter × cross-benchmark correlation matrix

### Potential Relevance to Gap 1
HIGH — directly shows that filter choice affects different benchmarks differently. The task-conditioned approach provides a hypothesis about the mechanism: different filters select for different capability-relevant data distributions.
