## Related Work

**Related Papers**
1. **Title**: UniGuard: Towards Universal Safety Guardrails for Jailbreak Attacks on Multimodal Large Language Models (arXiv:2411.01703)
   - **Authors**: Oh et al.
   - **Summary**: Proposes joint unimodal and cross-modal guardrails that minimize harmful response likelihood, demonstrating generalization across GPT-4o, LLaVA, and Gemini Pro.
   - **Year**: 2024

2. **Title**: Towards Robust Multimodal Large Language Models Against Jailbreak Attacks (SafeMLLM) (arXiv:2502.00653)
   - **Authors**: Yin et al.
   - **Summary**: Introduces contrastive embedding attack (CoE-Attack) with adversarial training that provides robust defense across 6 MLLMs and 6 jailbreak methods.
   - **Year**: 2025

3. **Title**: E²AT: Multimodal Jailbreak Defense via Dynamic Joint Optimization (arXiv:2503.04833)
   - **Authors**: Lu et al.
   - **Summary**: Presents Dynamic Joint Multimodal Optimization achieving 34% improvement over baselines, demonstrating the value of multimodal coordination for defense.
   - **Year**: 2025

4. **Title**: AGH-MAT
   - **Authors**: Not specified
   - **Summary**: Proposes an attention-only defense mechanism for multimodal jailbreak attacks.
   - **Year**: 2025 (CVPR 2025)

5. **Title**: TIM
   - **Authors**: Not specified
   - **Summary**: Introduces a test-time-only immunization approach for defending against jailbreak attacks.
   - **Year**: 2025

6. **Title**: JailBreakV-28K
   - **Authors**: Luo et al.
   - **Summary**: Presents a 28K benchmark revealing that LLM jailbreak techniques transfer to MLLMs with high attack success rates.
   - **Year**: 2024

7. **Title**: ASR Standardization Challenges
   - **Authors**: Chouldechova et al.
   - **Summary**: Demonstrates that attack success rate (ASR) measurements are not comparable across papers without a shared threat model.
   - **Year**: 2025 (NeurIPS 2025)

**Key Challenges**
1. **Fragmented Defense Landscape**: Current defenses against multimodal jailbreak attacks are fragmented, with individual approaches addressing only specific attack vectors rather than providing comprehensive protection.
2. **Limited Operational Scope**: Existing methods like TIM operate only at test-time, while comprehensive defense requires protection across both training and inference phases.
3. **Incomplete Protection Coverage**: Attention-only mechanisms like AGH-MAT provide partial protection rather than full-stack defense across all model components.
4. **Lack of Unified Evaluation Framework**: ASR measurements are inconsistent across research papers due to the absence of shared threat models, making it difficult to compare defense effectiveness.
5. **Cross-Modal Attack Transfer**: LLM jailbreak techniques successfully transfer to multimodal LLMs with high success rates, requiring defenses that address both unimodal and cross-modal vulnerabilities.
