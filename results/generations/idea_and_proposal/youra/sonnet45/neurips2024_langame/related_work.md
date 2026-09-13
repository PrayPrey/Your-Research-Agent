## Related Work

**Related Papers**

1. **Title**: The Symbol Grounding Problem (Harnad, 1990)
   - **Authors**: Harnad
   - **Summary**: Formalized the problem of connecting symbolic representations to meaning through grounding in perceptual/embodied experience. Establishes the theoretical foundation for symbol grounding requiring embodied perception.
   - **Year**: 1990

2. **Title**: Emergent language: a survey and taxonomy (Peters et al., 2024)
   - **Authors**: Peters et al.
   - **Summary**: Provides comprehensive taxonomy of emergent language metrics including compositionality (topographic similarity, context independence), stability, and convergence. Metrics originally designed for discrete symbolic languages with small vocabularies.
   - **Year**: 2024

3. **Title**: Compositionality in Neural Language Models (Supplementary Research)
   - **Authors**: Not specified
   - **Summary**: Provides methods for measuring compositionality in pretrained LLMs using semantic decomposition and substitution tests. Enables measurement of compositionality in natural language context rather than just symbolic emergent languages.
   - **Year**: 2023

4. **Title**: Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models (SPIN)
   - **Authors**: Chen et al.
   - **Summary**: Demonstrated self-play training paradigm where LLM improves by playing against previous versions and proved global optimum alignment with target distribution. Shows interactive training works for capability improvement through downstream task performance.
   - **Year**: 2024

5. **Title**: SPIRAL: Self-Play on Zero-Sum Games Incentivizes Reasoning
   - **Authors**: Liu et al.
   - **Summary**: Zero-sum game self-play produces transferable reasoning improvements (8.6% math improvement from Kuhn Poker alone). Demonstrates game-based training produces generalizable improvements beyond the training game context.
   - **Year**: 2025

6. **Title**: Language games meet multi-agent reinforcement learning
   - **Authors**: Van Eecke et al.
   - **Summary**: Explicit bridge between language games theoretical framework (Steels, Wittgenstein) and multi-agent reinforcement learning formulation. Provides theoretical justification for language games as training paradigm.
   - **Year**: 2023

7. **Title**: Towards Efficient LLM Grounding for Embodied Multi-Agent Collaboration
   - **Authors**: Zhang et al.
   - **Summary**: ReAd framework for LLM grounding in embodied multi-agent tasks using advantage feedback. Addresses grounding in embodied domain and validates grounding via task success.
   - **Year**: 2024

8. **Title**: Context Sensitivity in Large Language Models (Supplementary Research)
   - **Authors**: Not specified
   - **Summary**: Demonstrates measurable adaptation in LLMs to different contexts. Provides evidence for natural language LLMs exhibiting context-sensitive behavior.
   - **Year**: 2024

9. **Title**: LOOP algorithm (Referenced in causal mechanism)
   - **Authors**: Not specified
   - **Summary**: Demonstrates LLMs improve through interactive feedback loops. Supports the feedback-driven optimization pathway in the proposed causal mechanism.
   - **Year**: 2025

10. **Title**: Wittgenstein's language games theory (Foundational Philosophy)
   - **Authors**: Wittgenstein
   - **Summary**: Foundational theory that meaning emerges through use and social response in language games. Provides cognitive science foundation for interactive language training improving grounding.
   - **Year**: Not specified

11. **Title**: Kolling et al. - LLM in-context learning and associative learning connection
   - **Authors**: Kolling et al.
   - **Summary**: Connects LLM in-context learning to associative learning via feedback mechanisms. Supports plasticity assumption that LLMs can adapt through feedback signals.
   - **Year**: 2025

12. **Title**: Mordatch & Abbeel - Compositional language in referential games
   - **Authors**: Mordatch & Abbeel
   - **Summary**: Shows compositional language develops in referential games through emergent communication. Demonstrates language emergence in controlled symbolic grounding situations.
   - **Year**: Not specified

**Key Challenges**

1. **Measurement Gap for Interactive Training**: No existing framework systematically measures grounding improvements from interactive training vs. corpus training using theory-grounded, validated metrics. Prior work either applied cognitive principles informally without operationalized metrics or used task performance as indirect grounding proxy.

2. **Natural Language Compositionality Sensitivity**: Emergent language compositionality metrics were designed for discrete symbolic languages with small vocabularies. Measuring emergent compositionality in natural language LLMs may lack sensitivity since natural language is already highly compositional.

3. **Embodiment vs. Language-Only Grounding**: Symbol grounding theory (Harnad) requires embodied perception for "true" grounding. Language-only interaction may be insufficient compared to embodied perception, creating risk that neither language games nor corpus training achieves genuine grounding.

4. **Training Data Equivalence**: Challenge in fairly matching language game episodes to corpus tokens - quality vs. quantity trade-off where fewer high-quality interactive episodes may outperform more corpus tokens, confounding volume comparisons.

5. **Metric Validation for Grounding**: Need to validate that proposed CALM dimensions (CAS, PCI, ETA) actually capture what humans perceive as "grounded" language use, not just correlated constructs.

6. **Dimension Redundancy Risk**: Three CALM dimensions may show high inter-correlation indicating measurement redundancy rather than capturing independent aspects of grounding.

7. **Implementation Adaptation Gap**: Emergent language metrics designed for symbolic systems need adaptation to continuous natural language embeddings, requiring methodological innovation for topographic similarity and context independence in LLM context.

8. **Corpus Training Counter-Argument**: LLMs trained on diverse text corpora already encounter varied contexts and implicit communicative intents through reading, questioning whether explicit interaction improves grounding beyond corpus exposure.
