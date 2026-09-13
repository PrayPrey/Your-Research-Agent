## Related Work

**Related Papers**
1. **Title**: Metacognitive Capabilities of LLMs: An Exploration in Mathematical Problem Solving
   - **Authors**: Didolkar et al.
   - **Summary**: Demonstrates that LLMs possess metacognitive knowledge and shows that skill labeling improves mathematical accuracy, focusing on metacognitive knowledge rather than monitoring.
   - **Year**: 2024

2. **Title**: Exposing the Ghost in the Transformer: Abnormal Detection for LLMs via Hidden State Forensics
   - **Authors**: Zhou et al.
   - **Summary**: Achieves >95% detection accuracy for LLM anomalies through layer-specific activation patterns, providing technical foundation for hidden-state pattern detection.
   - **Year**: 2025

3. **Title**: Neural Breadcrumbs: Membership Inference Attacks via Hidden State and Attention Pattern Analysis
   - **Authors**: Makhija et al.
   - **Summary**: Demonstrates 0.85 AUC for detecting training data exposure via internal representations, supporting the assumption that hidden states exhibit separability.
   - **Year**: 2025

4. **Title**: Goedel-Prover-V2: Scaling Formal Theorem Proving
   - **Authors**: Lin et al.
   - **Summary**: Achieves 88.1% on MiniF2F using PRM-guided beam search, demonstrating the effectiveness of Process Reward Model approaches for step-level uncertainty estimation.
   - **Year**: 2025

5. **Title**: An Investigation of Robustness of LLMs in Mathematical Reasoning: PutnamGAP
   - **Authors**: Hao et al.
   - **Summary**: Shows that even O3 drops 10.5 percentage points on core-step variants, providing evaluation benchmarks and baseline drop rates for mathematical reasoning robustness.
   - **Year**: 2025

6. **Title**: Putnam-AXIOM: A Functional & Static Benchmark for Higher Level Mathematical Reasoning
   - **Authors**: Gulati et al.
   - **Summary**: Demonstrates O1-preview drops 46.8% on variations (41.9% → 22.3%), establishing contamination-resilient evaluation methodology for mathematical reasoning.
   - **Year**: 2025

7. **Title**: None of the Others: Distinguishing Reasoning from Memorization
   - **Authors**: Sánchez-Salido et al.
   - **Summary**: Identifies a 57% average accuracy drop under variation methods, establishing the problem definition and motivation for distinguishing genuine reasoning from memorization.
   - **Year**: 2025

8. **Title**: RV-BENCH: Benchmarking LLMs' Mathematical Reasoning with Unseen Random Variables
   - **Authors**: Hong et al.
   - **Summary**: Reveals that LLMs show proficiency imbalance between encountered and unseen distributions, providing evidence for the gap between pattern-matching and genuine reasoning.
   - **Year**: 2025

**Key Challenges**
1. **Metacognitive Monitoring vs. Knowledge**: Current approaches focus on metacognitive knowledge (skill labeling) rather than metacognitive monitoring, leaving a gap in real-time self-assessment of reasoning processes.

2. **Pattern-Matching vs. Genuine Reasoning**: LLMs exhibit significant performance drops (up to 57%) when problems are varied, suggesting reliance on pattern-matching rather than true mathematical reasoning.

3. **Robustness to Problem Variations**: State-of-the-art models including O3 and O1-preview show substantial accuracy degradation (10.5-46.8 percentage points) on modified versions of benchmark problems.

4. **Distribution Sensitivity**: LLMs demonstrate proficiency imbalance between encountered and unseen distributions, indicating limited generalization beyond training data patterns.

5. **Contamination in Evaluation**: Standard benchmarks may be compromised by training data contamination, necessitating contamination-resilient evaluation methodologies.
