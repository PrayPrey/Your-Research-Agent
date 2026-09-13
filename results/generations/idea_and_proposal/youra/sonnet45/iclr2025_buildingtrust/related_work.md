## Related Work

**Related Papers**
1. **Title**: TrustLLM: Trustworthiness in Large Language Models (S2: fb4dc0178e5d7347b1615c48caf05347b6e5eb48)
   - **Authors**: Sun et al.
   - **Summary**: Foundation for 8-dimension trustworthiness framework (truthfulness, safety, fairness, robustness, privacy, machine ethics, explainability, regulatory compliance). Evaluates dimensions independently across 16 models and 30+ datasets, establishing the taxonomy this work adopts.
   - **Year**: 2024

2. **Title**: FairSISA: Ensemble Post-Processing to Improve Fairness of Unlearning in LLMs (S2: 46fb63b449a468600c4274823bbffb37b8a21d87)
   - **Authors**: Kadhe et al.
   - **Summary**: Demonstrates that unlearning interventions degrade fairness metrics by 8-15%, providing empirical evidence for cross-dimensional interactions (unlearning→fairness dependency edge). Validates the shared parameter effect across trustworthiness dimensions.
   - **Year**: 2023

3. **Title**: Evaluating Implicit Regulatory Compliance in LLM Tool Invocation via Logic-Guided Synthesis (LogiSafetyBench) (S2: edaa579b2f27355d7206d3b688d4f1c625723945)
   - **Authors**: Song et al.
   - **Summary**: Reveals that larger models prioritize task completion over safety compliance in agent scenarios, demonstrating safety↔functionality tradeoffs. Provides evidence for dependency modeling need between safety and robustness dimensions.
   - **Year**: 2026

4. **Title**: Sampling Preferences Yields Simple Trustworthiness Scores (S2: 7954a1bbedd702dd9a474064c2f6ee5480f83329)
   - **Authors**: Steinle
   - **Summary**: Proposes preference sampling method for scalar aggregation of multi-dimensional trustworthiness evaluations into single scores. Serves as comparison baseline for scalar aggregation approaches, contrasting with Pareto optimization that preserves multi-objective information.
   - **Year**: 2025

5. **Title**: Systems Biology: Pathway Crosstalk and Regulatory Networks
   - **Authors**: Not specified
   - **Summary**: Cross-domain theoretical foundation demonstrating how biological systems maintain homeostasis through interconnected regulatory networks with feedback loops. Provides conceptual transfer for trustworthiness dimensions as interacting pathways requiring balanced optimization under varying environmental conditions.
   - **Year**: Not specified

6. **Title**: Multi-Objective Optimization: NSGA-II and Pareto Frontier Analysis
   - **Authors**: Not specified
   - **Summary**: Engineering optimization framework for conflicting objectives (cost vs performance vs safety) proven to scale to 10+ objectives. Provides algorithmic foundation for 8-dimensional trustworthiness optimization while preserving multi-objective information and avoiding scalar aggregation pitfalls.
   - **Year**: Not specified

7. **Title**: HowieHwong/TrustLLM
   - **Authors**: Not specified
   - **Summary**: Official GitHub implementation of TrustLLM benchmark with 30+ datasets across 8 trustworthiness dimensions. Provides source for meta-learning training data and validation benchmark for dependency graph learning.
   - **Year**: Not specified

8. **Title**: thu-ml/MLA-Trust
   - **Authors**: Not specified
   - **Summary**: Multimodal agent trustworthiness benchmark across 4 dimensions. Serves as validation testbed for dependency framework application to multimodal agent scenarios.
   - **Year**: Not specified

**Key Challenges**
1. **Independent Dimension Evaluation Limitation**: Existing frameworks (TrustLLM, DecodingTrust) evaluate trustworthiness dimensions separately, assuming orthogonality. This assumption is empirically violated by observed cross-dimensional interactions (e.g., unlearning degrades fairness), leading to suboptimal configurations that ignore dimension tradeoffs.

2. **Cross-Dimensional Integration Gap**: No unified framework exists for modeling causal/correlational relationships between trustworthiness dimensions. Current approaches lack systematic methods to predict side-effects when optimizing one dimension (e.g., improving safety may degrade functionality).

3. **Scalar Aggregation Information Loss**: Existing methods reduce multi-dimensional trustworthiness to single scalar scores via weighted sums or preference sampling, losing critical tradeoff information. This prevents practitioners from understanding dimension conflicts and making informed deployment decisions.

4. **Context-Agnostic Configuration**: Current evaluation frameworks do not adapt trustworthiness priorities to deployment context (healthcare vs finance vs legal). Static configurations fail to meet domain-specific dimension thresholds (e.g., privacy≥90% for healthcare, safety≥95% for autonomous agents).

5. **Architecture-Specific Interaction Patterns**: Trustworthiness dimension interactions may vary across model architecture families (GPT-style, Llama-style, Claude-style) due to different training paradigms and attention mechanisms. Existing work does not account for architecture-adaptive dependency modeling.

6. **Benchmark Coverage Gaps for Interaction Learning**: While individual dimension benchmarks are well-developed (TrustLLM 30+ datasets), systematic benchmarks for measuring cross-dimensional interactions are sparse. Limited data for dimension pairs like privacy×explainability hinders reliable dependency learning.

7. **Tradeoff Navigation Without Systematic Framework**: Practitioners lack principled methods to navigate conflicting trustworthiness objectives during deployment. Current approaches rely on ad-hoc manual tuning rather than systematic Pareto frontier analysis for multi-objective optimization.
