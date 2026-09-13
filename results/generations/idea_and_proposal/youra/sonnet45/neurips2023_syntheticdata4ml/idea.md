# Title
Fairness-by-Design Synthetic Data Generation: Instruction-Tuned LLMs with Constrained Decoding for Equitable Machine Learning

# Motivation
As LLMs replace GANs for synthetic data generation, a critical gap emerges: existing methods achieve only 10-15% demographic parity while post-hoc corrections sacrifice 5-10% utility. High-stakes domains (healthcare, finance, criminal justice) require synthetic data that addresses bias and under-representation without compromising model performance. Current approaches treat fairness as an afterthought rather than a design principle, limiting their effectiveness in creating truly equitable training datasets.

# Main Idea
We propose a dual-mechanism approach combining **fairness-aware instruction-tuning** (teaching LLMs semantic fairness understanding through 100-500 examples) with **constrained decoding** (enforcing formal demographic balance guarantees). Drawing from procedural justice theory, this fairness-by-design paradigm targets <5% demographic parity difference (vs. baseline 15-25%) while preserving data utility within 2-5% of unconstrained generation—a 40-60% fairness improvement over state-of-the-art.

**Methodology**: Test on standard fairness benchmarks (Adult, COMPAS, German Credit) using 2×2 factorial design comparing instruction-tuning and constrained decoding effects. Measure demographic parity difference, downstream classifier accuracy, and constraint satisfaction rates.

**Expected Impact**: Enable cost-effective generation of fair synthetic datasets for under-represented groups, providing architectural flexibility across LLM families while establishing quantitative fairness-utility trade-off thresholds for trustworthy ML development.