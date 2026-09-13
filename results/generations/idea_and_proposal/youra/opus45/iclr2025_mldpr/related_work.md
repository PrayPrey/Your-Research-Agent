## Related Work

**Related Papers**
1. **Title**: TabArena: A Living Benchmark for Machine Learning on Tabular Data (Semantic Scholar ID: cf69d81193ced740aec2fb9c01e1e6e94238f7b5)
   - **Authors**: Erickson, Purucker, Tschalzev, Holzmüller, Desai, Salinas, Hutter
   - **Summary**: Introduces the first living benchmark with maintenance protocols, demonstrating that continuous curation of benchmarks is feasible for machine learning evaluation.
   - **Year**: 2025

2. **Title**: Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research (Semantic Scholar ID: 1a23e78422fa03cbb7e5fed3c72cd64f00476346)
   - **Authors**: Koch, Denton, Hanna, Foster
   - **Summary**: Documents increasing concentration on fewer datasets in ML research and reveals elite institution bias in dataset creation, highlighting systemic issues in benchmark usage.
   - **Year**: 2021

3. **Title**: Accounting for Variance in Machine Learning Benchmarks (hal-03177159)
   - **Authors**: Bouthillier et al.
   - **Summary**: Demonstrates that variance from data sampling, initialization, and hyperparameters significantly impacts benchmark results, and provides methodology for measuring this variance.
   - **Year**: 2021

4. **Title**: Weak baselines and reporting biases lead to overoptimism in ML (Semantic Scholar ID: fda0812099547cd3b91031851f644e1929b4b77c)
   - **Authors**: McGreivy, Hakim
   - **Summary**: Finds that 79% of ML-for-PDE papers use weak baselines, revealing systematic overoptimism in reported results due to inadequate comparison standards.
   - **Year**: 2024

5. **Title**: Open Graph Benchmark (Semantic Scholar ID: 597bd2e45427563cdf025e53a3239006aa364cfc)
   - **Authors**: Hu et al.
   - **Summary**: Establishes a standard benchmark design with leaderboard for graph machine learning, representing a well-designed but static approach to benchmarking.
   - **Year**: 2020

6. **Title**: Quantifying Variance in Evaluation Benchmarks (arXiv:2406.10229)
   - **Authors**: Madaan, Singh, Schaeffer, et al.
   - **Summary**: Develops seed variance and monotonicity metrics for LLM benchmarks and proposes techniques to reduce variance in evaluation.
   - **Year**: 2024

**Key Challenges**
1. **Benchmark Saturation**: Increasing concentration on fewer datasets leads to overfitting to specific benchmarks, reducing the ability to measure genuine progress in the field.
2. **Elite Institution Bias**: Dataset creation is dominated by elite institutions, potentially limiting diversity and representativeness of evaluation benchmarks.
3. **Variance in Benchmark Results**: Significant variance from data sampling, initialization, and hyperparameters undermines the reliability of benchmark comparisons.
4. **Weak Baseline Comparisons**: Widespread use of weak baselines leads to overoptimistic reporting of improvements, obscuring true algorithmic advances.
5. **Static Benchmark Design**: Traditional benchmarks lack maintenance protocols and continuous curation, becoming outdated as the field progresses.
6. **Lack of Automated Quality Controls**: Absence of automated mechanisms to detect saturation and enforce quality standards in benchmarking practices.
