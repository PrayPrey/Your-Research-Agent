## Related Work

**Related Papers**
1. **Title**: Carbon Emissions and Large Neural Network Training (arXiv:2104.10350)
   - **Authors**: Patterson et al. (Google)
   - **Summary**: Establishes that DNN architecture, datacenter location, and processor choice can reduce carbon emissions by 100-1000x, providing the foundation for carbon-aware ML research.
   - **Year**: 2021

2. **Title**: The Carbon Footprint of ML Training Will Plateau, Then Shrink (arXiv:2204.05149)
   - **Authors**: Patterson et al.
   - **Summary**: Identifies four best practices for emission reduction in ML training: sparse models, geographic location selection, cloud computing, and specialized accelerators.
   - **Year**: 2022

3. **Title**: EcoServe: Designing Carbon-Aware AI Inference Systems (arXiv:2502.05043)
   - **Authors**: Li et al.
   - **Summary**: Proposes a 4R framework (Reduce, Reuse, Rightsize, Recycle) that achieves 47% carbon reduction in AI serving, demonstrating that GPUs dominate operational carbon while CPUs dominate embodied carbon.
   - **Year**: 2025

4. **Title**: OpenCarbonEval: A Unified Carbon Emission Estimation Framework (arXiv:2405.12843)
   - **Authors**: Yu et al.
   - **Summary**: Develops dynamic throughput modeling that enables accurate carbon prediction across different model scales.
   - **Year**: 2024

5. **Title**: LCA Methodology for Carbon Payback Period and Lifecycle Cost Analysis
   - **Authors**: Gacula; Wang
   - **Summary**: Introduces carbon amortization concepts and lifecycle cost analysis methodologies that are transferable to ML systems.
   - **Year**: 2025-2026

6. **Title**: CarbonGearRL
   - **Authors**: Not specified
   - **Summary**: Applies reinforcement learning-based optimization for training carbon reduction, achieving 52% emission reduction.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Unified Carbon Lifecycle Optimization**: Limited implementations exist that address carbon optimization across the entire ML lifecycle in a unified manner.
2. **Disconnected Training and Serving Optimization**: No existing framework connects training decisions to their downstream impact on serving carbon emissions, treating these phases independently.
3. **Suboptimal Sequential Optimization**: Current approaches apply training and serving optimizations sequentially (e.g., CarbonGearRL followed by EcoServe) without joint optimization, missing potential synergies.
