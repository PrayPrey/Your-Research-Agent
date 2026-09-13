## Related Work

**Related Papers**
1. **Title**: HI-TOM: A Benchmark for Evaluating Higher-Order Theory of Mind Reasoning in Large Language Models
   - **Authors**: He et al.
   - **Summary**: Establishes a benchmark for evaluating higher-order Theory of Mind reasoning in LLMs, demonstrating that LLMs show systematic accuracy decline on higher-order ToM tasks from 1st to 4th order.
   - **Year**: 2023

2. **Title**: Hierarchical Reasoning Model (HRM) (arXiv:2506.21734)
   - **Authors**: Wang et al.
   - **Summary**: Proposes a 27M parameter dual-timescale architecture that outperforms much larger models on complex reasoning tasks, proving the parameter efficiency of hierarchical approaches.
   - **Year**: 2025

3. **Title**: A unifying computational account of temporal context effects in language
   - **Authors**: Vo et al.
   - **Summary**: Demonstrates that multi-timescale RNNs capture temporal context effects that match human brain language processing, validating MTRNN architectures for the language domain.
   - **Year**: 2023

4. **Title**: Decompose-ToM
   - **Authors**: Sarangi et al.
   - **Summary**: Shows that recursive simulation through prompting improves Theory of Mind performance, serving as a baseline for prompting-based approaches to ToM.
   - **Year**: 2025

5. **Title**: ToM-LM: Delegating Theory of Mind Reasoning to External Symbolic Executors
   - **Authors**: Tang & Belle
   - **Summary**: Integrates SMCDEL symbolic executor for verifiable Theory of Mind reasoning, providing a baseline for symbolic approaches to ToM.
   - **Year**: 2024

6. **Title**: Think Twice: Perspective-Taking Improves Large Language Models' Theory-of-Mind Capabilities
   - **Authors**: Wilf et al.
   - **Summary**: Introduces SimToM showing that perspective-based filtering helps improve ToM capabilities but does not fully address underlying architectural limitations.
   - **Year**: 2023

7. **Title**: Learning mental states estimation through self-observation: a developmental synergy
   - **Authors**: Bianco et al.
   - **Summary**: Demonstrates developmental synergy between low-level (beliefs) and high-level (meta-beliefs) processing, providing support for dual-module architectural designs.
   - **Year**: 2024

**Key Challenges**
1. **Systematic Accuracy Decline on Higher-Order ToM**: LLMs exhibit systematic performance degradation as Theory of Mind reasoning progresses from 1st to 4th order, indicating fundamental limitations in handling nested belief structures.

2. **Architectural Limitations of Current Approaches**: Prompting-based methods like perspective-taking (SimToM) provide improvements but fail to address the underlying architectural constraints that limit ToM reasoning capabilities.

3. **Parameter Efficiency vs. Scale Trade-off**: Achieving strong reasoning performance typically requires very large models, though hierarchical architectures demonstrate that smaller, well-designed models can outperform larger counterparts.

4. **Integration of Symbolic and Neural Approaches**: Bridging symbolic executors with neural language models for verifiable ToM reasoning remains an open challenge requiring effective delegation mechanisms.

5. **Multi-Level Mental State Processing**: Effectively coordinating low-level belief estimation with high-level meta-belief reasoning requires specialized architectural designs that capture developmental synergies between processing levels.
