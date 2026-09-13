# Introduction

Domain mixing ratios can make or break LLM performance—yet optimizing them typically costs hundreds of GPU-hours in proxy model training. What if we could predict optimal mixtures using only frozen embeddings?

The impact of training data composition on language model performance is well-established. DoReMi [Xie et al., 2023] demonstrated that optimized domain mixing yields 2-3% improvements over heuristic baselines on downstream benchmarks, while SlimPajama [Soboleva et al., 2023] showed that careful curation of domain ratios is essential for efficient pretraining. These findings confirm that *what* data we train on matters as much as *how much* we train.

Yet current optimization methods carry a significant computational burden. DoReMi requires training a reference model and proxy model before the main training run begins—a process that can consume 10-20% of the total training compute. For practitioners operating under compute constraints, this overhead represents a substantial barrier to optimizing data mixtures.

We observe a deeper problem: existing approaches fundamentally require training to evaluate domain utility. Perplexity-based selection needs model inference; proxy training needs gradient updates. No method currently predicts domain utility in a training-free manner.

This gap motivates our investigation: can embedding geometry—specifically, the similarity between domain samples and downstream task exemplars—provide a signal for domain utility without any training? Prior work in domain adaptation [DSIR; Park et al.] suggests that distributional alignment correlates with transfer performance. If embedding space proximity to task-relevant content predicts training utility, we could optimize domain mixtures using only frozen embedder inference.

We propose Embedding-guided Domain Mixing Prediction (EDMP), a training-free approach that scores domains by cosine similarity between domain sample embeddings and task exemplar embeddings. Our key insight is that embedding geometry may encode task-relevant information sufficient to rank domains by utility—though validating this predictive power requires careful empirical investigation.

In this work, we make the following contributions:

1. **Pipeline Validation:** We demonstrate that EDMP scores can be reliably computed for multi-domain corpora, producing statistically distinguishable domain rankings (ANOVA F=1242.59, p<0.001) with perfect reproducibility across seeds.

2. **Data Quality Dependency:** We identify that synthetic data with shared vocabulary produces insufficient cross-domain variance (std=0.007 vs. target 0.05), establishing that real domain data is necessary to test the predictive power hypothesis.

3. **Methodological Foundation:** We provide a reusable pipeline and experimental framework for embedding-based domain scoring, enabling future work to complete the validation chain.

We organize the remainder of this paper as follows: Section 2 discusses related work in domain mixing optimization and embedding-based selection methods. Section 3 presents the EDMP methodology. Section 4 describes our experimental setup. Section 5 presents results, and Section 6 discusses implications and limitations. Section 7 concludes with directions for future work.
