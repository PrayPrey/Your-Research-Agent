## Related Work

**Related Papers**
1. **Title**: CogDPM: Diffusion Probabilistic Models via Cognitive Predictive Coding (arXiv:2024)
   - **Authors**: Chen et al.
   - **Summary**: Demonstrates theoretical connection between diffusion and predictive coding, introducing precision weighting for diffusion guidance.
   - **Year**: 2024

2. **Title**: Constructing the hierarchy of predictive auditory sequences in the marmoset brain (eLife)
   - **Authors**: Jiang et al.
   - **Summary**: Reveals hierarchical gradient in auditory processing where midbrain handles local timescale and prefrontal handles global timescale, with prediction errors communicated via gamma oscillations and updates via beta oscillations.
   - **Year**: 2021

3. **Title**: AudioLDM: Text-to-Audio Generation with Latent Diffusion Models
   - **Authors**: Liu et al.
   - **Summary**: Achieves state-of-the-art latent diffusion for audio generation using CLAP embeddings for text-audio alignment.
   - **Year**: 2023

4. **Title**: SoundReactor: Frame-level Online Video-to-Audio Generation
   - **Authors**: Saito et al.
   - **Summary**: Introduces the first frame-level online video-to-audio generation system achieving 26.3ms latency using consistency training.
   - **Year**: 2025

5. **Title**: VoXtream: Full-Stream TTS with Extremely Low Latency (arXiv:2509.15969)
   - **Authors**: Not specified
   - **Summary**: Achieves 102ms initial delay for text-to-speech using a monotonic alignment scheme for streaming synthesis.
   - **Year**: 2025

6. **Title**: StreamMel: Real-Time Zero-shot TTS (arXiv:2506.12570)
   - **Authors**: Not specified
   - **Summary**: Proposes single-stage streaming text-to-speech using continuous mel-spectrograms without diffusion models.
   - **Year**: 2025

7. **Title**: Dynamic predictive coding across the left fronto-temporal language hierarchy
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates precision-weighted prediction error propagation in language processing, showing that unexpected signals require more processing resources.
   - **Year**: 2021

8. **Title**: KAD: Kernel Audio Distance (arXiv:2502.15602)
   - **Authors**: Not specified
   - **Summary**: Introduces a distribution-free, unbiased audio quality metric as an alternative to Fréchet Audio Distance (FAD).
   - **Year**: 2025

**Key Challenges**
1. **Latency-Quality Trade-off**: Existing streaming audio generation systems struggle to achieve both low latency and high audio quality simultaneously, with current approaches requiring compromises between real-time performance and generation fidelity.

2. **Hierarchical Temporal Processing**: Current audio generation models lack principled mechanisms for handling multiple temporal scales, unlike biological auditory systems that process local and global timescales through distinct hierarchical pathways.

3. **Adaptive Computation Allocation**: Existing diffusion-based audio systems do not dynamically allocate computational resources based on signal predictability, missing opportunities to optimize processing for unexpected versus predictable audio segments.

4. **Integration of Predictive Coding with Diffusion**: While theoretical connections between diffusion models and predictive coding have been established, practical implementations that leverage precision-weighted prediction errors for audio generation remain underexplored.

5. **Streaming Diffusion Architecture**: Adapting latent diffusion models designed for offline generation to streaming scenarios with frame-level online processing presents architectural challenges not fully addressed by current methods.
