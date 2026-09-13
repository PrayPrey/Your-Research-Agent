## Related Work

**Related Papers**

1. **Title**: Sparse coding theory (Olshausen & Field 1996)
   - **Authors**: Olshausen & Field
   - **Summary**: Foundational work on sparse coding demonstrating how monosemantic representations emerge from sparsity constraints. Provides theoretical basis for SAE architecture and interpretability claims.
   - **Year**: 1996

2. **Title**: Campbell 2023 - Activation patching for behavior localization
   - **Authors**: Campbell et al.
   - **Summary**: Demonstrates activation patching methodology for validating causal relationships in neural networks. Shows behaviors can be localized to specific layers (15-25). Provides empirical foundation for causal validation framework.
   - **Year**: 2023

3. **Title**: Abdulaal 2024 - SAE-Rad: SAE for radiology task
   - **Authors**: Abdulaal et al.
   - **Summary**: Applies sparse autoencoders to vision domain for radiology tasks. Demonstrates SAE features achieve monosemanticity through empirical validation with human annotation protocol (inter-rater agreement >0.7). Provides evidence for SAE interpretability in domain-specific applications.
   - **Year**: 2024

4. **Title**: Villegas Garcia 2025 - SAE steering in protein generation
   - **Authors**: Villegas Garcia et al.
   - **Summary**: Demonstrates SAE features can guide protein generation toward specific domains (zinc finger domains). Shows feature manipulation in activation space achieves targeted control. Provides proof-of-concept for feature-space intervention design.
   - **Year**: 2025

5. **Title**: SafeSteer (Ghosh 2025) - Gradient-free category steering for safety
   - **Authors**: Ghosh et al.
   - **Summary**: Achieves 87% toxicity reduction on RealToxicityPrompts using heuristic category contrasts (harmful vs. neutral prompts). Achieves 96% text quality (MAUVE). Notes steering failures lack interpretable debugging mechanisms. Represents SOTA heuristic steering baseline.
   - **Year**: 2025

6. **Title**: Dubey 2025 - Probe-guided steering for bias mitigation
   - **Authors**: Dubey et al.
   - **Summary**: Uses linear probes to identify bias-relevant directions, then converts probe directions to steering vectors. Achieves 94% bias detection accuracy, 85% bias mitigation effectiveness, ~97% MMLU retention. Demonstrates single-objective probe-based steering. Represents SOTA probe-only baseline.
   - **Year**: 2025

7. **Title**: Bereska & Gavves 2024 - Mechanistic Interpretability for AI Safety Survey
   - **Authors**: Bereska & Gavves
   - **Summary**: Survey paper identifying theoretical foundations for interpretability-guided interventions. Documents gap in systematic integration of interpretability methods with intervention design. Motivates need for unified frameworks connecting analysis to control.
   - **Year**: 2024

**Key Challenges**

1. **Gap 1: Unified Framework for Interpretability-Guided Interventions**: Prior work treats interpretability (SAE analysis) and intervention (activation steering) as separate tasks. No systematic framework integrates feature discovery → steering design → validation in closed loop.

2. **Heuristic vs. Principled Intervention Design**: Current SOTA methods (SafeSteer) rely on heuristic category contrasts without mechanistic grounding. Steering failures lack interpretable diagnosis or debugging mechanisms.

3. **Single-Objective Limitations**: Existing probe-based steering (Dubey 2025) focuses on single objectives (bias mitigation). Multi-objective steering and cross-objective interference remain unexplored.

4. **Capability Preservation vs. Control Trade-off**: Prior work shows capability degradation with aggressive steering (Dubey: ~97% MMLU retention). Need for methods that achieve stronger control while better preserving capabilities (≥98% target).

5. **Feature Causality Validation**: SAE features may be correlational rather than causal. While activation patching methodology exists (Campbell 2023), integration of causal validation into systematic intervention frameworks is lacking.

6. **Interpretability Measurement**: No established benchmark or protocol for measuring interpretability gains in intervention methods. Expert rating protocols and inter-rater agreement standards need development.

7. **Scalability to Large Models**: SAE training demonstrated at medium scale (GPT-2-large 774M, LLaMA-7B). Scaling to 70B+ models requires efficiency innovations (selective layer SAEs, sparse caching) beyond current research budgets.

8. **Feature Monosemanticity Assumption**: While sparse coding theory (Olshausen & Field 1996) and empirical results (Abdulaal 2024) suggest SAE features are monosemantic, this assumption requires systematic validation across different domains and models.

9. **Multi-Objective Interference**: Cross-objective interference patterns unknown. No prior work tests whether safety steering degrades factuality or vice versa. Feature-space monitoring for detecting unintended changes unexplored.

10. **Production Deployment Gap**: Research demonstrations often lack rigorous capability validation, latency optimization, and adversarial robustness testing needed for real-world deployment.
