## Related Work

**Related Papers**
1. **Title**: Not an Illusion but a Manifestation: Understanding Large Language Model Reasoning Limitations Through Dual-Process Theory (2025)
   - **Authors**: Boris Gorelik
   - **Summary**: Demonstrates that LLM performance collapse under cognitive load mirrors human bounded rationality, where System 2 disengagement is a feature, not a bug. Proposes computational rest may restore reasoning performance.
   - **Year**: 2025

2. **Title**: CogniDual Framework: Self-Training Large Language Models within a Dual-System Theoretical Framework for Improving Cognitive Tasks (2024)
   - **Authors**: Yongxin Deng, Xihe Qiu, et al.
   - **Summary**: Shows LLMs can learn System 1→2 transitions through self-training, emulating human deliberate→intuitive learning process, demonstrating feasibility of dual-system LLM architecture.
   - **Year**: 2024

3. **Title**: Large language models for artificial general intelligence (AGI): A survey of foundational principles and approaches (2025)
   - **Authors**: A. Mumuni, F. Mumuni
   - **Summary**: Identifies symbol grounding and causal reasoning as 2 of 4 foundational requirements for LLM-based AGI, establishing research priorities for advancing toward artificial general intelligence.
   - **Year**: 2025

4. **Title**: On Measuring Grounding and Generalizing Grounding Problems (arXiv:2512.06205, 2026)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that simple accuracy metrics are inadequate for grounding evaluation, highlighting need for robustness, compositional understanding, and context stability in symbol grounding assessment.
   - **Year**: 2026

5. **Title**: Peirce - Neuro-Symbolic AI Framework
   - **Authors**: Not specified
   - **Summary**: Static neuro-symbolic system with pre-defined task routing to symbolic reasoners without adaptive switching mechanisms, representing current baseline approach to neural-symbolic integration.
   - **Year**: Not specified

6. **Title**: SymbolicAI
   - **Authors**: ExtensityAI
   - **Summary**: Static neuro-symbolic framework using fixed task classification for routing between neural and symbolic components, lacking dynamic cognitive load-based switching.
   - **Year**: Not specified

**Key Challenges**
1. **Symbol Grounding Problem**: Symbol grounding remains a central challenge in AI evaluation; existing benchmarks show LLMs struggle with precise symbolic reasoning under cognitive constraints (Emergent Mind, 2026).

2. **Bounded Rationality under Cognitive Load**: LLMs exhibit performance collapse when context saturates (>70% utilization), uncertainty increases (>0.3 logprobs), or reasoning chains exceed working memory capacity (>5 steps), mirroring human System 2 disengagement.

3. **Semantic Parsing Translation Errors**: Neural-to-symbolic translation (natural language to formal logic) introduces errors that can undermine symbolic precision, requiring validation mechanisms to prevent error propagation.

4. **Static vs. Dynamic System Switching**: Existing neuro-symbolic approaches use pre-defined task routing rather than adaptive switching based on real-time cognitive load indicators, limiting responsiveness to dynamic reasoning demands.

5. **Lack of Empirical Validation for Computational Rest**: The hypothesis that computational rest during symbolic processing restores neural reasoning capacity (proposed by Gorelik 2025) requires empirical validation through controlled before/after performance measurement.

6. **Inadequate Grounding Evaluation Metrics**: Simple accuracy metrics fail to capture robustness, compositional understanding, and context stability required for comprehensive symbol grounding assessment.

7. **Integration Complexity**: Combining LLM + symbolic reasoner + monitoring + validation requires significant engineering effort and introduces latency overhead (1-5 seconds per query) that may limit real-time applications.

8. **Human-in-Loop Requirements**: Low-confidence semantic parsing cases require human validation, reducing full automation and potentially limiting practical deployment scalability.
