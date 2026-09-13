## Related Work

**Related Papers**
1. **Title**: Towards Bidirectional Human-AI Alignment: A Systematic Review, Framework, and Research Agenda (Semantic Scholar ID: c11d885b219e817bdb3d4e95c0307e7f987d3bba)
   - **Authors**: Shen et al.
   - **Summary**: Systematic review of 400+ papers identifying theory-practice gap in bidirectional alignment and framing the problem space for bidirectional human-AI alignment research.
   - **Year**: 2024

2. **Title**: Co-Alignment: Rethinking Alignment as Bidirectional Human-AI Cognitive Adaptation (BiCA) (Semantic Scholar ID: f7d47ea116ff69201be7fb67fcd67976fdcdf5c8)
   - **Authors**: Li & Song
   - **Summary**: Introduces learnable RLHF protocols achieving 85.5% success vs 70.3% baseline with 230% mutual adaptation improvement and emergent protocols outperforming handcrafted ones by 84%.
   - **Year**: 2025

3. **Title**: Intent-aligned AI systems deplete human agency (Semantic Scholar ID: 1e603f3254bc0e0dbcf9d1170f968b45d502d557)
   - **Authors**: Mitelut et al.
   - **Summary**: Formalizes agency depletion risk in alignment systems, warning that standard alignment approaches may lead to learned helplessness and deskilling through agency-depleting interactions.
   - **Year**: 2023

4. **Title**: Rewards-in-Context: Multi-objective Alignment with Dynamic Preference Adjustment (RiC) (Semantic Scholar ID: 9637ef9019671034912ea0f506ae67c3f2fc4689)
   - **Authors**: Yang et al.
   - **Summary**: Multi-objective RLHF achieving Pareto-optimal solutions with dynamic preference adjustment and 10% GPU hours vs multi-objective RL baseline.
   - **Year**: 2024

5. **Title**: MO-ODPO: Robust Multi-Objective Preference Alignment (Semantic Scholar ID: ed034fff0b46b7b375befb284f3591b022e38def)
   - **Authors**: Gupta et al.
   - **Summary**: Robust multi-objective preference alignment with inference-time steerability, validating dynamic weight adjustment for handling preference conflicts.
   - **Year**: 2025

6. **Title**: Measuring AI Alignment with Human Flourishing: FAI Benchmark (Semantic Scholar ID: 502f37ca5f3790639660f41d87add3e89573f828)
   - **Authors**: Hilliard et al.
   - **Summary**: Proposes 7-dimensional flourishing assessment including autonomy, decision-making, competence, relatedness, vitality, self-actualization, and flourishing as measurable constructs for AI alignment.
   - **Year**: 2025

7. **Title**: Cybernetics: Or Control and Communication in the Animal and the Machine
   - **Authors**: Wiener, Norbert
   - **Summary**: Classic foundation establishing homeostatic control systems that maintain equilibrium via reflexive feedback loops, providing theoretical grounding for feedback control mechanisms.
   - **Year**: 1948

8. **Title**: Adaptive Control Systems: Theory and Applications
   - **Authors**: Åström & Wittenmark
   - **Summary**: Establishes Model Reference Adaptive Control (MRAC) which continuously adjusts parameters to match desired reference behavior with Lyapunov stability proofs for non-linear systems.
   - **Year**: Not specified

9. **Title**: Situated Reinforcement Learning from Human Feedback (Semantic Scholar ID: 08628008504b19f811fd6498b2f6fa6c4703b29c)
   - **Authors**: Arzberger et al.
   - **Summary**: Demonstrates context-aware value alignment in RLHF, suggesting users value agency-preserving interactions in different contexts.
   - **Year**: 2024

10. **Title**: BiCA Framework
    - **Authors**: Li & Song
    - **Summary**: Implementation framework featuring learnable protocols, representation mapping, and KL-budget constraints for bidirectional human-AI adaptation.
    - **Year**: 2025

11. **Title**: align-anything (PyTorch framework)
    - **Authors**: Not specified
    - **Summary**: Any-to-any alignment infrastructure providing modularity design patterns for production implementation of alignment systems.
    - **Year**: Not specified

**Key Challenges**
1. **Theory-Practice Gap in Bidirectional Alignment**: Systematic reviews identify a gap between theoretical frameworks for bidirectional alignment and concrete operational implementations that can be deployed in practice.

2. **Agency Depletion Risk**: Standard alignment approaches may inadvertently deplete human agency through learned helplessness and deskilling, creating tension between alignment quality and agency preservation.

3. **Lack of Standardized Agency Metrics**: No validated metrics exist for measuring agency preservation in human-AI interactions, making it difficult to quantify whether systems maintain user autonomy.

4. **Behavioral Proxy Validity (Goodhart's Law)**: Risk that optimizing behavioral proxies for agency may not preserve actual subjective agency experience if proxy-to-truth correlation is insufficient.

5. **Multi-Objective Optimization Trade-offs**: Fundamental tension may exist between alignment quality and agency preservation, requiring Pareto-optimal solutions rather than perfect outcomes on both dimensions.

6. **Cold-Start Problem**: Difficulty establishing reliable baseline agency profiles for new users with insufficient interaction history (<50 interactions).

7. **Computational Overhead for Production**: Real-time agency monitoring and dynamic weight adjustment must remain computationally feasible (≤15% overhead) for production deployment at scale.

8. **Non-Stationary User Dynamics**: User preferences and behavior patterns may change rapidly over time, causing baseline agency measurements to become stale and invalidating deviation tracking.

9. **Cybernetic Control Transfer to Non-Linear RL**: Uncertainty about whether feedback control principles from linear/near-linear systems transfer effectively to chaotic non-linear RL optimization dynamics.

10. **Safety vs. Agency Conflicts**: In safety-critical domains, preventing harmful user requests may require reducing agency, creating fundamental goal conflicts that no trade-off weight can resolve.
