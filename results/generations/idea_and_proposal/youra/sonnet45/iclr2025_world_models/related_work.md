## Related Work

**Related Papers**

1. **Title**: HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution (arXiv:2306.15794)
   - **Authors**: Eric Nguyen, Michael Poli, et al.
   - **Summary**: Provides Hyena operator architecture with implicit long convolutions achieving O(N log N) complexity and data-controlled gating, demonstrating 1M-token genomic sequence processing at single-nucleotide resolution.
   - **Year**: 2023

2. **Title**: Hamiltonian Neural Networks
   - **Authors**: Samuel Greydanus, Misko Dzamba, Jason Yosinski
   - **Summary**: Establishes Hamiltonian formulation for neural ODEs, proving energy conservation by construction (dE/dt = {H,H} = 0 via Poisson bracket) and demonstrating that physics constraints can be enforced as architectural inductive biases.
   - **Year**: 2019

3. **Title**: Transformers are Sample-Efficient World Models (IRIS)
   - **Authors**: Vincent Micheli, Eloi Alonso, François Fleuret
   - **Summary**: SOTA transformer-based world model achieving sample efficiency through discrete autoregressive modeling, limited to 64-frame horizons due to O(T²) complexity.
   - **Year**: 2023

4. **Title**: Is Sora a World Simulator? A Comprehensive Survey on General World Models and Beyond (arXiv:2405.03520)
   - **Authors**: Zheng Zhu, Xiaofeng Wang, et al. (17 authors)
   - **Summary**: Defines Gap 2: long-horizon temporal consistency challenge, identifying error accumulation in autoregressive rollouts and 64-frame practical limit for transformers, documenting physics violations in large models despite massive scale.
   - **Year**: 2024

5. **Title**: Understanding World or Predicting Future? A Comprehensive Survey of World Models (arXiv:2411.14499)
   - **Authors**: Jingtao Ding, Yunke Zhang, Yu Shang, et al.
   - **Summary**: Comprehensive taxonomy of world models distinguishing understanding present vs. predicting future, categorizing evaluation metrics (pixel fidelity vs. physics consistency vs. task performance).
   - **Year**: 2024

6. **Title**: PhyT2V: LLM-Guided Iterative Self-Refinement for Physics-Grounded Text-to-Video Generation (arXiv:2412.00596)
   - **Authors**: Qiyao Xue, Xiangyu Yin, Boyuan Yang, Wei Gao
   - **Summary**: Uses LLM chain-of-thought reasoning to improve physical adherence in video generation, achieving 2.3x improvement in physics consistency, but requires expensive LLM reasoning (~1-2s per frame inference).
   - **Year**: 2024

7. **Title**: Physics-Guided Learning-based Adaptive Control / Physics-Guided AI for Large-Scale Spatiotemporal Data
   - **Authors**: Various (multiple papers)
   - **Summary**: Demonstrates principle-based integration of physics knowledge into AI architectures improves generalization and interpretability, showing physics constraints as architectural inductive biases provide strongest guarantees.
   - **Year**: 2024

8. **Title**: Accelerating Model-Based Reinforcement Learning with State-Space World Models
   - **Authors**: Maria Krinner, Elie Aljalbout, Angel Romero, Davide Scaramuzza
   - **Summary**: Uses state-space models (SSMs) for 10x dynamics training speedup and 4x overall MBRL speedup, operating on state-space (not video) without physics guarantees.
   - **Year**: 2025

9. **Title**: Hyena Hierarchy: Towards Larger Convolutional Language Models
   - **Authors**: Michael Poli, Stefano Massaroli, et al.
   - **Summary**: Original Hyena paper introducing implicit long convolutions with sub-quadratic complexity, demonstrating Hyena operators can replace attention in language models with O(N log N) complexity while matching or exceeding performance.
   - **Year**: 2023

10. **Title**: Navigation World Models (arXiv:2412.03572)
    - **Authors**: Amir Bar, Gaoyue Zhou, Danny Tran, Trevor Darrell, Yann LeCun
    - **Summary**: 1B-param Conditional Diffusion Transformer for navigation video prediction achieving high visual fidelity but requiring massive compute with iterative denoising.
    - **Year**: 2024

11. **Title**: Vid2World: Transforming Video Diffusion Models into Interactive World Models
    - **Authors**: Tsinghua University Team
    - **Summary**: Adapts video diffusion models (full-sequence generation) to interactive world models (causal autoregressive) for action-conditioned generation, showing video diffusion can be adapted but requires architectural modifications for causality.
    - **Year**: 2024

12. **Title**: A Comprehensive Survey on World Models for Embodied AI
    - **Authors**: Xinqing Li, Xin He, Le Zhang, Yun Liu
    - **Summary**: Unified framework for world models in embodied AI distinguishing decision-coupled vs. general-purpose, covering temporal modeling approaches and spatial representations with comprehensive coverage of robotics and autonomous driving.
    - **Year**: 2025

13. **Title**: Genie Envisioner: A Unified World Foundation Platform for Robotic Manipulation
    - **Authors**: Yue Liao, Pengfei Zhou, Siyuan Huang, et al. (15 authors)
    - **Summary**: Unified platform with video diffusion model (GE-Base), action decoder (GE-Act), neural simulator (GE-Sim), introducing EWMBench benchmark for robotics world models requiring visual fidelity + physical consistency + instruction-action alignment.
    - **Year**: 2025

14. **Title**: Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling (arXiv:2403.03234)
    - **Authors**: Yair Schiff, Chia-Hsiang Kao, et al.
    - **Summary**: Demonstrates RC (reverse complement) equivariance + bidirectionality enhances long-range DNA modeling, showing domain-appropriate symmetries improve efficiency and suggesting architectural symmetries/equivariances should match domain structure.
    - **Year**: 2024

15. **Title**: VideoMamba / VideoMambaPro
    - **Authors**: Various
    - **Summary**: Mamba (Hyena's SSM cousin) applied to video understanding (classification, action recognition, anomaly detection), proving SSMs successfully work for video tasks and demonstrating feasibility of sub-quadratic architectures for visual temporal modeling.
    - **Year**: 2024

16. **Title**: HyenaPixel
    - **Authors**: Various
    - **Summary**: Hyena adapted to image generation via causal token mixing, focusing on spatial autoregressive modeling (not temporal video), proving Hyena successfully transfers from language (original domain) to vision (images).
    - **Year**: 2024

17. **Title**: stable-worldmodel
    - **Authors**: Not specified
    - **Summary**: Minimal scalable library for world model evaluation, includes physics violation detection (penetration, floating), providing standardized physics metrics beyond pixel fidelity.
    - **Year**: Not specified

18. **Title**: EWMBench (from Genie Envisioner)
    - **Authors**: Not specified
    - **Summary**: Standardized benchmark for embodied world models measuring visual fidelity + physical consistency + instruction-action alignment, providing robotics-specific evaluation requiring multi-dimensional metrics.
    - **Year**: Not specified

19. **Title**: DreamerV3
    - **Authors**: Hafner et al.
    - **Summary**: SOTA model-based RL world model using transformers, serving as baseline for comparison.
    - **Year**: 2023

20. **Title**: Video Diffusion Models
    - **Authors**: Ho et al.
    - **Summary**: Foundation for diffusion-based video generation, representing alternative approach using iterative denoising vs. direct prediction.
    - **Year**: 2022

21. **Title**: S4/Mamba Papers
    - **Authors**: Gu et al. (S4), Gu & Dao (Mamba)
    - **Summary**: State-space model foundations where Mamba is alternative SSM architecture to Hyena.
    - **Year**: 2022 (S4), 2023 (Mamba)

22. **Title**: World Models
    - **Authors**: Ha & Schmidhuber
    - **Summary**: Classic VAE + MDN-RNN + Controller architecture providing historical foundation, now superseded by transformer-based approaches.
    - **Year**: 2018

**Key Challenges**

1. **Long-Horizon Temporal Consistency**: Current transformer-based models are limited to 64-256 frames due to O(T²) complexity, with error accumulation in autoregressive rollouts preventing scalable 1000+ frame prediction.

2. **Physics Violations in Large Models**: Despite massive scale and training data, current models (including Sora, Genie) exhibit physics violations (penetration, floating objects, momentum errors) due to lack of architectural conservation constraints.

3. **Computational Scalability vs. Quality Trade-off**: High-quality video generation (diffusion models) requires massive compute (1B+ params, iterative denoising), while efficient models (SSMs) lack physics guarantees and explicit long-horizon capability.

4. **Cross-Domain Transfer**: Architectures proven in one domain (e.g., Hyena for genomics, transformers for language) require validation when adapted to video temporal modeling with different pattern structures.

5. **Physics Constraint Integration Cost**: LLM-based physics reasoning (PhyT2V) improves consistency but is expensive (~1-2s per frame), requiring architectural alternatives that provide physics guarantees without computational overhead.

6. **Sim-to-Real Transfer Gap**: Physics-consistent simulation models must generalize to real robots, but domain gap and real-world dissipative forces (friction, damping) challenge pure Hamiltonian conservative force assumptions.

7. **Evaluation Metric Fragmentation**: World models evaluated on disparate metrics (pixel fidelity FVD/LPIPS, physics violations, task success, computational cost) without unified benchmarks combining all dimensions.

8. **Limited Robotic Application Validation**: Most world models demonstrated on game environments or simple datasets, lacking comprehensive validation on multi-step robotic manipulation and navigation tasks requiring long-horizon planning.
