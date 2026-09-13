## Related Work

**Related Papers**
1. **Title**: Mamba: Linear-Time Sequence Modeling with Selective State Spaces (arXiv:2312.00752)
   - **Authors**: Albert Gu, Tri Dao
   - **Summary**: Introduces selective state space models (SSM) that achieve 5x faster inference than Transformers while maintaining content-based reasoning capabilities, establishing the foundation for SSM-based sequence modeling.
   - **Year**: 2023

2. **Title**: Video Diffusion Models (arXiv:2204.03458)
   - **Authors**: Jonathan Ho, Tim Salimans, et al.
   - **Summary**: Presents the first diffusion model for video generation with spatial-temporal extension, establishing foundational techniques for diffusion-based video synthesis.
   - **Year**: 2022

3. **Title**: Duet model unifies diverse neuroscience experimental findings on predictive coding
   - **Authors**: J. Meng, Jordan M. Ross, Jordan P. Hamm, Xiao-Jing Wang
   - **Summary**: Demonstrates that the brain uses dual prediction error signals (positive/negative) for deviance detection, providing neuroscience-inspired motivation for functional separation in computational models.
   - **Year**: 2025

4. **Title**: StateSpaceDiffuser: Bringing Long Context to Diffusion World Models
   - **Authors**: INSAIT Research Team
   - **Summary**: Combines SSM for memory and context handling within diffusion models, serving as a baseline for comparing memory versus dynamics separation approaches in world models.
   - **Year**: 2025

5. **Title**: STORM: Efficient Stochastic Transformer based World Models
   - **Authors**: Weipu Zhang, Gang Wang, et al.
   - **Summary**: Achieves 126.7% human performance on Atari 100k benchmark using a Transformer-based world model architecture.
   - **Year**: 2023

6. **Title**: DIAMOND: Diffusion for World Modeling
   - **Authors**: Not specified
   - **Summary**: Achieves 1.46 human-normalized score on Atari 100k using a diffusion-only world model approach.
   - **Year**: 2024

7. **Title**: Vision Mamba: Efficient Visual Representation Learning
   - **Authors**: Lianghui Zhu, Bencheng Liao, et al.
   - **Summary**: Demonstrates 2.8x faster processing than Vision Transformer with 86.8% memory reduction, validating SSM effectiveness for visual understanding tasks.
   - **Year**: 2024

8. **Title**: Is Sora a World Simulator?
   - **Authors**: Zheng Zhu, Xiaofeng Wang, et al.
   - **Summary**: Analyzes video generation models and identifies physical simulation and causality as key open challenges in video world models.
   - **Year**: 2024

9. **Title**: state-spaces/mamba (GitHub Repository)
   - **Authors**: Not specified
   - **Summary**: Official Mamba implementation providing hardware-aware selective scan operations for efficient SSM computation.
   - **Year**: Not specified

10. **Title**: huggingface/diffusers (GitHub Repository)
    - **Authors**: Not specified
    - **Summary**: Comprehensive library providing video diffusion pipelines, consistency models, and DiT implementations for diffusion-based generation.
    - **Year**: Not specified

**Key Challenges**
1. **Physical Simulation Fidelity**: Current video world models struggle to accurately simulate physical dynamics and maintain physical plausibility over extended sequences.

2. **Causality Modeling**: Existing approaches have difficulty capturing and representing causal relationships in world model predictions.

3. **Memory vs. Dynamics Separation**: Prior work combining SSM and diffusion lacks clear functional separation between memory/context handling and dynamics generation.

4. **Computational Efficiency Trade-offs**: Balancing high-quality generation (diffusion) with efficient long-context processing (SSM) remains an open architectural challenge.

5. **Long-Context Handling**: Effectively maintaining and utilizing long temporal context in world models while preserving computational efficiency is not fully solved.
