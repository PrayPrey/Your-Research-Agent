## Related Work

**Related Papers**

1. **Title**: Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects
   - **Authors**: Rao, R. P., & Ballard, D. H.
   - **Summary**: Foundational predictive coding theory demonstrating that error signals drive representational updates in cortical hierarchy, establishing biological plausibility of error-driven mechanisms in neural computation.
   - **Year**: 1999

2. **Title**: DINO-WM: World Models on Pre-trained Visual Features enable Zero-shot Planning
   - **Authors**: Zhou, G., Pan, H., LeCun, Y., Pinto, L.
   - **Summary**: Demonstrates that patch feature prediction enables zero-shot planning via forward models, validating prediction-based planning feasibility with 118 citations.
   - **Year**: 2024

3. **Title**: Fine-Tuning Large Vision-Language Models as Decision-Making Agents via Reinforcement Learning
   - **Authors**: Zhai, Y., Bai, H., Lin, Z., et al.
   - **Summary**: Shows that Chain-of-Thought (CoT) reasoning improves decision-making when grounded in observations, demonstrating reasoning benefits from execution feedback with 142 citations.
   - **Year**: 2024

4. **Title**: Predictive Coding: A Theoretical and Experimental Review
   - **Authors**: Millidge, B., Seth, A., Buckley, C. L.
   - **Summary**: Provides modern computational perspective on predictive coding in deep learning, offering theoretical framework for error minimization objectives.
   - **Year**: 2021

5. **Title**: OmniJARVIS: Unified Vision-Language-Action Tokenization Enables Open-World Instruction Following Agents
   - **Authors**: Wang, Z., Cai, S., Mu, Z., et al.
   - **Summary**: Achieves strong performance with unified tokenization for multimodal agents using sequential reasoning→planning→acting phases, serving as baseline for synchronous coupling comparison with 26 citations.
   - **Year**: 2024

6. **Title**: CivRealm: A Learning and Reasoning Odyssey in Civilization for Decision-Making Agents
   - **Authors**: Qi, S., et al.
   - **Summary**: Presents complex strategy game environment requiring both learning and reasoning, providing benchmark for testing multi-scale hierarchical reasoning on strategic tasks with 31 citations.
   - **Year**: 2024

7. **Title**: FeUdal Networks for Hierarchical Reinforcement Learning (FuN)
   - **Authors**: Vezhnevets, A. S., et al.
   - **Summary**: Demonstrates that multi-scale temporal abstraction using 10-step hierarchy improves hierarchical reinforcement learning performance, justifying multi-scale temporal design choices.
   - **Year**: 2017

8. **Title**: AgentGym-RL: Training LLM Agents for Long-Horizon Decision Making through Multi-Turn Reinforcement Learning
   - **Authors**: Xi, Z., et al.
   - **Summary**: Shows that multi-turn reasoning enables long-horizon tasks but reasoning and action occur in separate turns rather than synchronously coupled, with 21 citations.
   - **Year**: 2025

9. **Title**: HIRO (Hierarchical Reinforcement Learning)
   - **Authors**: Not specified
   - **Summary**: Validates multi-scale abstractions in hierarchical reinforcement learning contexts.
   - **Year**: Not specified

10. **Title**: Options Framework
    - **Authors**: Not specified
    - **Summary**: Validates temporal abstraction principles in reinforcement learning.
    - **Year**: Not specified

11. **Title**: StreamDiffusion
    - **Authors**: Not specified
    - **Summary**: Demonstrates dual-stream architectures can handle bidirectional information flow, supporting feasibility of dual-stream transformer designs.
    - **Year**: Not specified

12. **Title**: Text2Video-Zero
    - **Authors**: Not specified
    - **Summary**: Shows dual-stream architectures handle bidirectional flow in video generation contexts.
    - **Year**: Not specified

13. **Title**: CLIP
    - **Authors**: Not specified
    - **Summary**: Uses cross-attention for multi-modal fusion in vision-language models.
    - **Year**: Not specified

14. **Title**: DALL-E
    - **Authors**: Not specified
    - **Summary**: Employs cross-attention mechanisms for multi-modal fusion in generative models.
    - **Year**: Not specified

**Key Challenges**

1. **Sequential vs Synchronous Reasoning-Action Integration**: Existing approaches like OmniJARVIS perform reasoning, planning, and acting in separate sequential phases rather than maintaining continuous bidirectional coupling, potentially limiting real-time adaptation capabilities.

2. **Unidirectional Prediction Limitations**: World models like DINO-WM demonstrate unidirectional prediction (state → future state) for planning but lack backward error propagation to update reasoning based on execution outcomes.

3. **Lack of Principled Multi-Scale Integration**: While hierarchical RL methods (FuN, HIRO, Options) validate multi-scale temporal abstractions, they lack integration with reasoning systems at architectural level for open-world agents.

4. **Training Stability in Joint Optimization**: Jointly optimizing prediction streams and decision streams with bidirectional coupling via cross-attention presents training stability challenges that require careful curriculum design and loss weighting.

5. **Prediction Error Informativeness**: Ensuring prediction errors contain actionable signals for reasoning updates rather than noise, particularly in high-dimensional or stochastic action spaces.

6. **Cross-Attention Saturation and Divergence**: Risk that cross-attention layers may saturate, vanish gradients, or create training instability when implementing bidirectional information exchange, preventing effective coupling.

7. **Temporal Scale Alignment**: Predetermined temporal scales (0.1s, 1s, 10s) may not align with task structure across different domains, and current approaches lack adaptive scale learning mechanisms.

8. **Adaptation Without Full Replanning**: Sequential approaches require full recomputation for plan adaptation after environment changes, lacking incremental update mechanisms within single forward passes.

9. **Curriculum Dependency**: Performance of complex multi-stream architectures heavily depends on careful curriculum design, with poor stage transitions or loss weighting causing convergence failures.

10. **Scalability to Extreme Action Spaces**: Unclear how prediction-error coupling scales to very high-dimensional continuous action spaces (>100 dimensions) or highly stochastic environments where signal-to-noise ratio may be problematic.
