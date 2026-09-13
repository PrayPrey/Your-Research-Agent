## Related Work

**Related Papers**
1. **Title**: In-context Learning and Induction Heads
   - **Authors**: Olsson, Elhage, Nanda et al. (Anthropic)
   - **Summary**: Demonstrates that induction heads develop at precisely the same point as sharp ICL ability increase, presenting a circuit-level mechanism for in-context learning in smaller models.
   - **Year**: 2022

2. **Title**: Which Attention Heads Matter for In-Context Learning?
   - **Authors**: Yin & Steinhardt
   - **Summary**: Shows that Function Vector (FV) heads are primarily responsible for ICL in larger models, and reveals that many FV heads start as induction heads before transitioning to their final role.
   - **Year**: 2025

3. **Title**: What Can Transformers Learn In-Context?
   - **Authors**: Garg et al.
   - **Summary**: Provides a systematic study of ICL function classes and establishes a task benchmark framework for evaluating in-context learning capabilities.
   - **Year**: 2022

4. **Title**: What needs to go right for an induction head?
   - **Authors**: Singh, Moskovitz, Hill, Chan, Saxe
   - **Summary**: Identifies subcircuits that enable induction head formation using an optogenetics-inspired causal framework for mechanistic analysis.
   - **Year**: 2024

5. **Title**: TransformerLens
   - **Authors**: Neel Nanda
   - **Summary**: Open-source library serving as a primary ablation tool for mechanistic interpretability research on transformer models.
   - **Year**: Not specified

6. **Title**: Induction Heads Repository
   - **Authors**: Anthropic
   - **Summary**: Reference implementation for identifying and analyzing induction heads in transformer models.
   - **Year**: Not specified

**Key Challenges**
1. **Transition Dynamics Gap**: No existing work characterizes the transition dynamics between induction head mechanisms (dominant at small scale) and FV head mechanisms (dominant at large scale).
2. **Multi-Scale Methodological Gap**: No multi-scale ablation study exists that spans models from 100M to 7B parameters using consistent methodology to track mechanism evolution.
3. **Scale-Dependent Mechanism Understanding**: Current understanding is fragmented between small-model results showing induction head dominance and large-model results showing FV head dominance, without unified characterization of the intermediate regime.
