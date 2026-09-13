## Related Work

**Related Papers**

1. **Title**: A Complexity-Based Theory of Compositionality
   - **Authors**: Elmoznino et al.
   - **Summary**: Provides formal theoretical foundation for compositional representations defined via algorithmic information theory, establishing expressiveness, re-describability, and simple semantics properties.
   - **Year**: 2024

2. **Title**: How to Plant Trees in Language Models
   - **Authors**: Mueller & Linzen
   - **Summary**: Establishes the depth > width architectural principle for hierarchical generalization, showing deeper models with fewer parameters per layer outperform wider shallow models on hierarchical linguistic tasks.
   - **Year**: 2023

3. **Title**: The Algebraic Approach to Compositional Semantics
   - **Authors**: Liang & Potts
   - **Summary**: Foundational work demonstrating how algebraic compositional functions enable systematic meaning composition.
   - **Year**: 2015

4. **Title**: Unlocking Out-of-Distribution Generalization in Transformers via Recursive Latent Space Reasoning
   - **Authors**: Altabaa et al.
   - **Summary**: Introduces 4 mechanisms (recurrence, algorithmic supervision, discrete bottleneck, error-correction) to improve OOD generalization in transformers through recursive latent space reasoning.
   - **Year**: 2025

5. **Title**: Complexity Control Facilitates Reasoning-Based Compositional Generalization in Transformers
   - **Authors**: Zhang et al.
   - **Summary**: Demonstrates that architectural parameters (initialization, regularization) significantly affect compositional reasoning by shifting models from memorization to rule learning.
   - **Year**: 2025

6. **Title**: Compositional Program Generation for Few-Shot Systematic Generalization
   - **Authors**: Klinger et al.
   - **Summary**: Neuro-symbolic approach achieving 1000x sample efficiency via compositional modules using modular architecture for strong few-shot generalization.
   - **Year**: 2023

7. **Title**: Measuring Compositional Generalization: A Comprehensive Method on Realistic Data
   - **Authors**: Kim & Linzen
   - **Summary**: Established methodology for systematic compositional splits using atom recombination splits (primitive, compound, template) to measure different compositional generalization dimensions.
   - **Year**: 2020

8. **Title**: OMEGA: Can LLMs Reason Outside the Box in Math?
   - **Authors**: Sun et al.
   - **Summary**: Primary benchmark revealing compositional reasoning failures in frontier LLMs through 3-axis evaluation (compositional, procedural, knowledge), showing current LLMs achieve only 30-40% on compositional axis.
   - **Year**: 2025

9. **Title**: SCAN: Learning Compositional Skills in a Supervised Task
   - **Authors**: Lake & Baroni
   - **Summary**: Classic compositional generalization benchmark demonstrating that standard sequence-to-sequence models fail on compositional splits for linguistic commands to actions.
   - **Year**: 2018

10. **Title**: Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
    - **Authors**: Wei et al.
    - **Summary**: Demonstrates that explicit intermediate reasoning steps improve mathematical problem-solving through step-by-step reasoning chains.
    - **Year**: 2022

11. **Title**: Tree of Thoughts: Deliberate Problem Solving with Large Language Models
    - **Authors**: Yao et al.
    - **Summary**: Introduces tree-structured reasoning for complex problem-solving where exploring multiple reasoning branches improves solution quality.
    - **Year**: 2023

12. **Title**: Working Memory Hierarchy Models (multiple works)
    - **Authors**: Baddeley & Hitch
    - **Summary**: Cognitive psychology model of human working memory structure with hierarchical organization including specialized subsystems (phonological loop, visuospatial sketchpad, episodic buffer, central executive).
    - **Year**: 1974-2000

13. **Title**: Hierarchical Processing in Prefrontal Cortex
    - **Authors**: Badre & D'Esposito, Koechlin et al.
    - **Summary**: Neuroscience evidence for hierarchical cognitive control showing rostro-caudal PFC hierarchy processes progressively abstract cognitive control.
    - **Year**: 2000s

14. **Title**: Swin Transformer: Hierarchical Vision Transformer using Shifted Windows
    - **Authors**: Liu et al.
    - **Summary**: Hierarchical attention in computer vision using local-to-global hierarchical attention (window-based) to improve vision tasks.
    - **Year**: 2021

15. **Title**: HuggingFace Flash Attention 2 Implementation
    - **Authors**: Not specified
    - **Summary**: Efficient attention computation with optimized CUDA kernels where SDPA (Scaled Dot-Product Attention) and Flash Attention 2 backends enable efficient multi-head attention.
    - **Year**: Not specified

**Key Challenges**

1. **Lack of Mathematical-Specific Hierarchical Attention**: No hierarchical attention architecture specifically designed for mathematical compositional reasoning. Existing hierarchical attention (vision, NLP) lacks explicit composition operators and mathematical specialization.

2. **Limited Dynamic Routing for Compositional Skills**: Limited work on dynamic routing for compositional skill combinations. MoE architectures exist but focus on general expert specialization, not compositional reasoning.

3. **Interpretability-Performance Trade-offs**: Insufficient understanding of interpretability-performance trade-offs in compositional architectures. Deeper interpretability research needed beyond attention pattern analysis.

4. **Unknown Scaling Laws**: Scaling laws for hierarchical compositional architectures unknown. How do benefits scale with model size, hierarchy depth, and expert count?

5. **Compositional Generalization Failures**: Current frontier LLMs achieve only 30-40% accuracy on compositional axis of mathematical reasoning tasks (OMEGA benchmark), revealing significant gaps in compositional reasoning capabilities.

6. **Structure vs Scale Tension**: Debate between explicit architectural structure (hierarchy + routing) versus emergent capabilities from scale alone for achieving compositional generalization.

7. **Gradient Flow in Deep Hierarchies**: Very deep hierarchies may suffer from optimization difficulties despite mitigation strategies like residual connections and layer-wise learning rate scheduling.

8. **Training Complexity**: Compositional architectures require specialized training methodologies including compositional structure annotations, increasing data preparation costs and implementation difficulty.
