## Related Work

**Related Papers**

1. **Title**: Reasoning Paths with Reference Objects Elicit Quantitative Spatial Reasoning in Large Vision-Language Models (SpatialPrompt) (2024)
   - **Authors**: Liao, Y., et al.
   - **Summary**: Demonstrates that instructing VLMs to use reference objects improves Gemini 1.5 spatial reasoning by +56.2 points and GPT-4V by +28.5 points WITHOUT fine-tuning, establishing that prompting is superior to adaptation for spatial reasoning tasks.
   - **Year**: 2024

2. **Title**: Few-shot Adaptation for Manipulating Granular Materials Under Domain Shift (CoDeGa) (2023)
   - **Authors**: Zhu, Y., Thangeda, P., Ornik, M., Hauser, K.
   - **Summary**: Introduces Deep Gaussian process with meta-learning (CoDeGa: Controlled Deployment Gaps) that learns robustly under LARGE domain shifts, validated through 6,700 scoops on diverse materials, establishing methodological basis for perception meta-learning under significant sim-to-real gaps.
   - **Year**: 2023

3. **Title**: MetaCropFollow: Few-Shot Adaptation with Meta-Learning for Under-Canopy Navigation (2024)
   - **Authors**: Woehrle, T., Sivakumar, A., Uppalapati, N., Chowdhary, G.
   - **Summary**: Demonstrates that meta-learning overcomes agricultural outdoor domain shift (lighting, season, soil, crop variations) with minimal data, providing cross-domain validation for outdoor navigation challenges.
   - **Year**: 2024

4. **Title**: CityEQA: Hierarchical Multi-Modal City Environment Question Answering (2025)
   - **Authors**: Not specified
   - **Summary**: Introduces Hierarchical Planner-Manager-Actor architecture achieving 60.7% human-level performance in city navigation across 1,412 test scenarios, validating hierarchical LLM agent architectures and establishing simulation-only performance baseline.
   - **Year**: 2025

5. **Title**: MetaUrban: A Simulation Platform for Embodied AI in Autonomous Driving (2025, ICLR)
   - **Authors**: Not specified
   - **Summary**: Provides high-fidelity urban micromobility simulation with realistic agent behaviors, serving as the primary simulation platform for meta-training with potential weather/season capability.
   - **Year**: 2025

6. **Title**: SimToRealTransfer-Outdoor (Repository)
   - **Authors**: Not specified
   - **Summary**: Establishes baseline outdoor domain adaptation achieving approximately 55% mIoU without LLM or meta-learning, providing comparison baseline for direct sim-to-real transfer approaches.
   - **Year**: 2024

7. **Title**: Embodied Domain Adaptation for Object Detection (EDAOD) (2025)
   - **Authors**: Shi, X., Qiao, Y., Liu, L., Dayoub, F.
   - **Summary**: Validates source-free domain adaptation approach for embodied robots in indoor environments using temporal clustering, though outdoor and LLM integration remain novel extensions.
   - **Year**: 2025

8. **Title**: Embodied AI in Indoor and Outdoor Environments (Survey) (2021)
   - **Authors**: Not specified
   - **Summary**: Establishes that outdoor embodied AI introduces unique challenges including lighting variations, weather conditions, and dynamic elements that are not systematically addressed in existing literature, demonstrating the research gap.
   - **Year**: 2021

9. **Title**: MIFormer: Multi-Teacher Intermediate Domain Adaptation for Foggy Weather (2024)
   - **Authors**: Ge, S., Huo, W., Lu, B., Gong, G.
   - **Summary**: Validates multi-teacher distillation approach for weather adaptation achieving 69.1 mIoU on foggy scenes, though limited to vision-only applications without LLM integration.
   - **Year**: 2024

10. **Title**: SORT3D: Spatial Object-centric Reasoning Toolbox for Zero-Shot 3D Grounding (2025)
    - **Authors**: Zantout, N., et al.
    - **Summary**: Demonstrates that LLM combined with heuristics toolbox achieves zero-shot spatial reasoning without 3D training, supporting modular architecture with separation between LLM reasoning and perception components.
    - **Year**: 2025

11. **Title**: Adversarial Domain Adaptation (Autonomous Driving Context) (2025)
    - **Authors**: Jiang (reference incomplete)
    - **Summary**: Demonstrates GAN-based style transfer for handling changing weather, lighting, and tunnel conditions in autonomous driving, providing foundation for intermediate domain bridging approaches.
    - **Year**: 2025

12. **Title**: SpatialPrompting (Keyframe-based Spatial Reasoning) (2025)
    - **Authors**: Taguchi et al.
    - **Summary**: Achieves state-of-the-art keyframe-driven zero-shot spatial reasoning without 3D training, further validating prompting-based approaches for embodied spatial reasoning tasks.
    - **Year**: 2025

**Key Challenges**

1. **Outdoor Sim-to-Real Gap**: Large domain shifts between simulation and real-world outdoor environments due to weather variations (clear, fog, rain, snow), lighting conditions (day, dusk, night), and dynamic elements create perception accuracy degradation from simulation (~85%) to real-world (~55% mIoU baseline).

2. **LLM Reasoning Adaptation Dilemma**: Existing approaches assume LLM reasoning requires fine-tuning or adaptation for domain transfer, but recent evidence (SpatialPrompt +56.2 points) suggests prompting strategies may be superior, creating tension in architectural design decisions.

3. **Multi-Teacher Distillation for LLMs**: While multi-teacher knowledge distillation is validated for vision-only perception (MIFormer: 69.1 mIoU), no evidence exists for applying multi-teacher approaches when the student is an LLM with different learning dynamics.

4. **Sample Efficiency Requirements**: Practical deployment of outdoor embodied agents requires few-shot adaptation (10-50 samples per condition) to be feasible, but achieving this efficiency while maintaining performance across 4-5 weather/lighting conditions remains challenging.

5. **Progressive Domain Bridging**: GAN-based intermediate domain generation for weather/lighting variations must preserve semantic content while introducing gradual distribution shifts, but acceptable levels of visual artifacts and semantic preservation validation protocols are not well established.

6. **Source-Free Real-World Adaptation**: Deploying embodied agents without access to original simulation data (for privacy or practical reasons) requires source-free domain adaptation techniques, but integration with LLM-based hierarchical architectures in outdoor environments is not validated.

7. **Hierarchical Architecture Integration**: Determining which components in LLM-based embodied agents require domain adaptation (perception modules) versus which can use zero-shot transfer (reasoning modules) lacks systematic framework, especially for outdoor navigation scenarios.

8. **Real-World Validation Infrastructure**: Collecting real-world outdoor data across diverse weather conditions (fog, rain, night) within practical timelines faces logistical challenges due to weather dependency and opportunistic sampling requirements.

9. **Modality-Agnostic Reasoning Transfer**: Validating that LLM spatial reasoning strategies (prompting, keyframe selection) work equally well with real-world sensor data as with simulation data lacks empirical evidence in outdoor embodied navigation contexts.

10. **Computational Feasibility**: Meta-training across diverse weather/lighting conditions requires significant computational resources (4-8 A100 GPUs, 2-3 weeks), while LLM API costs during deployment ($0.01-0.05 per query) create practical deployment constraints for outdoor navigation applications.
