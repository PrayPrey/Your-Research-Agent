## Related Work

**Related Papers**
1. **Title**: NLP Evaluation in trouble: On the Need to Measure LLM Data Contamination for each Benchmark (SS ID: cd2f4aaf98bb1e020cff310000c8049d3460c54e)
   - **Authors**: Sainz et al.
   - **Summary**: Defines contamination levels and argues for community effort to detect exposure, establishing the foundational problem that contamination-aware evaluation systems must address.
   - **Year**: 2023

2. **Title**: LiveBench: A Challenging, Contamination-Limited LLM Benchmark (SS ID: 774d01e152003f342596031c0c0fbf1936dee41a)
   - **Authors**: White et al.
   - **Summary**: Demonstrates dynamic benchmark design with monthly updates and objective scoring, providing design principles for contamination resistance in LLM evaluation.
   - **Year**: 2024

3. **Title**: GeomVerse: A Systematic Evaluation of Large Models for Geometric Reasoning (SS ID: 608a2b333fd8262e8c918f36c5700bafd3ea3cdd)
   - **Authors**: Kazemi et al.
   - **Summary**: Uses procedural generation with controllable depth to reveal VLM limitations, validating depth-based evaluation approaches for systematic reasoning assessment.
   - **Year**: 2023

4. **Title**: Measuring Compositional Generalization: A Comprehensive Method on Realistic Data (arXiv:1912.09713)
   - **Authors**: Keysers et al. (Google)
   - **Summary**: Introduces the compound divergence metric and CFQ benchmark, establishing systematic methods for measuring compositionality in neural models.
   - **Year**: 2020

5. **Title**: SCAN Benchmark
   - **Authors**: Lake & Baroni
   - **Summary**: Foundational compositional generalization test that established early methods for evaluating systematic generalization in neural sequence models.
   - **Year**: 2018

6. **Title**: COGS Dataset
   - **Authors**: Not specified
   - **Summary**: Provides compositional generalization splits for semantic parsing tasks, enabling evaluation of systematic generalization capabilities.
   - **Year**: Not specified

7. **Title**: FuncBenchGen
   - **Authors**: Not specified
   - **Summary**: DAG-based evaluation framework for function calling capabilities in language models.
   - **Year**: 2026 (ICLR)

8. **Title**: Faith and Fate: Limits of Transformers on Compositionality
   - **Authors**: Dziri et al.
   - **Summary**: Demonstrates that transformers use linearized subgraph matching rather than systematic composition, establishing the need for better evaluation methods to distinguish reasoning strategies.
   - **Year**: 2023

9. **Title**: Benchmark Data Contamination Survey
   - **Authors**: Xu et al.
   - **Summary**: Provides a comprehensive review of contamination detection methods and highlights limitations of current approaches for identifying training data leakage.
   - **Year**: 2024

**Key Challenges**
1. **Data Contamination in Benchmarks**: Current LLM evaluation suffers from training data contamination, where models may have been exposed to benchmark data during training, compromising the validity of performance measurements.

2. **Distinguishing Memorization from Reasoning**: Transformers may rely on linearized subgraph matching rather than true systematic composition, making it difficult to determine whether models genuinely reason or simply pattern-match from training data.

3. **Static Benchmark Limitations**: Traditional static benchmarks become increasingly contaminated over time, necessitating dynamic evaluation approaches with regular updates to maintain validity.

4. **Measuring Compositional Generalization**: Evaluating whether models can systematically combine learned primitives in novel ways remains challenging, requiring specialized metrics and controlled evaluation frameworks.

5. **Contamination Detection Limitations**: Existing methods for detecting benchmark contamination have significant limitations, leaving gaps in our ability to verify the integrity of evaluation results.
