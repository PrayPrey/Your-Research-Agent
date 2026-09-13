## Related Work

**Related Papers**
1. **Title**: Grokking as the Transition from Lazy to Rich Training Dynamics (arXiv:2310.06110)
   - **Authors**: Kumar, Bordelon, Gershman, Pehlevan
   - **Summary**: Demonstrates that grokking arises from the transition between lazy and rich training dynamics, providing a mechanistic foundation for understanding criticality control approaches in neural network training.
   - **Year**: 2023

2. **Title**: Critical dynamics governs deep learning (arXiv:2507.08527)
   - **Authors**: Vock & Meisel
   - **Summary**: Establishes that deep neural networks perform optimally near critical phase transitions, providing primary evidence for the link between criticality and network performance.
   - **Year**: 2025

3. **Title**: Neural activity responsiveness by maturation of inhibition (doi:10.3389/fncir.2024.1519704)
   - **Authors**: Matsumoto et al.
   - **Summary**: Investigates critical period timing through developmental processes in neural systems, offering cross-domain inspiration for optimizer scheduling strategies.
   - **Year**: 2025

4. **Title**: Phase diagram of early training dynamics (arXiv:2302.12250)
   - **Authors**: Kalra & Barkeshli
   - **Summary**: Demonstrates that Hessian eigenvalue tracking can identify distinct training regimes, validating the use of proxy metrics for monitoring training dynamics.
   - **Year**: 2023

5. **Title**: Let Me Grok for You: Accelerating Grokking via Embedding Transfer
   - **Authors**: Xu et al.
   - **Summary**: Proposes an alternative approach to accelerating grokking through embedding transfer, serving as a comparison baseline for grokking acceleration methods.
   - **Year**: 2025

6. **Title**: Standard Adam/AdamW with cosine schedule
   - **Authors**: Not specified
   - **Summary**: Default optimizer configuration commonly used as a baseline for comparing novel optimization approaches.
   - **Year**: Not specified

7. **Title**: Deep Double Descent
   - **Authors**: Nakkiran et al.
   - **Summary**: Established the double descent phenomenon in deep learning, where test error can decrease again after initially increasing with model complexity, representing a target phenomenon for criticality control methods.
   - **Year**: 2019

8. **Title**: A mean-field approach to criticality in spiking neural networks (arXiv:2025)
   - **Authors**: Freddi et al.
   - **Summary**: Provides an analytical framework for configuring neural networks at criticality, validating the computational tractability of criticality-based approaches.
   - **Year**: 2025

**Key Challenges**
1. **Lazy-to-Rich Training Transition**: Understanding and controlling the transition from lazy to rich training dynamics that underlies grokking behavior in neural networks.
2. **Optimal Criticality Maintenance**: Developing methods to maintain neural networks near critical phase transitions where optimal performance occurs during training.
3. **Training Regime Identification**: Creating reliable proxy metrics and monitoring approaches to identify distinct training regimes in real-time.
4. **Double Descent Mitigation**: Addressing the double descent phenomenon where test error exhibits non-monotonic behavior with respect to model complexity or training time.
5. **Computational Tractability of Criticality Control**: Ensuring that criticality-based optimization approaches remain computationally feasible for practical deep learning applications.
