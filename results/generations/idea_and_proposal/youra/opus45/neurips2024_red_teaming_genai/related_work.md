## Related Work

**Related Papers**
1. **Title**: VLSU: Mapping the Limits of Joint Multimodal Understanding for AI Safety (Semantic Scholar ID: be87b8d00ee60927e2de2b2f3ab79e41750bb516)
   - **Authors**: Shruti Palaskar, Leon Gatys, et al.
   - **Summary**: Demonstrates that 34% of errors in joint image-text safety classification occur despite correct classification of individual modalities, revealing absent compositional reasoning capabilities in multimodal AI systems.
   - **Year**: 2025

2. **Title**: MM-RLHF: The Next Step Forward in Multimodal LLM Alignment (Semantic Scholar ID: bb6426f40b7a5323423826afa0485fd940ec3c78)
   - **Authors**: Yifan Zhang, Tao Yu, et al.
   - **Summary**: Achieves 60% improvement in safety through multimodal alignment techniques, though compositional vulnerabilities persist despite these advances.
   - **Year**: 2025

3. **Title**: Speech-Audio Compositional Attacks on Multimodal LLMs (SACRED-Bench) (arXiv:2511.10222)
   - **Authors**: Yudong Yang, Xuezhen Zhang, et al.
   - **Summary**: Demonstrates 66% attack success rate on compositional audio attacks against Gemini 2.5 Pro, validating the compositional attack surface across audio modalities.
   - **Year**: 2026

4. **Title**: The Alignment Curse: Cross-Modality Jailbreak Transfer in Omni-Models (arXiv:2602.02557)
   - **Authors**: Not specified
   - **Summary**: Shows that text vulnerabilities can transfer to audio modality in omni-models, focusing on cross-modality transfer mechanisms.
   - **Year**: 2026

5. **Title**: VLATTACK: Multimodal Adversarial Attacks on Vision-Language Tasks (NeurIPS 2023)
   - **Authors**: Not specified
   - **Summary**: Introduces dual-perturbation attacks on vision-language models, demonstrating adversarial vulnerabilities in multimodal tasks.
   - **Year**: 2023

6. **Title**: From LLMs to MLLMs to Agents: A Survey of Jailbreak Attacks and Defenses (Semantic Scholar ID: ccfabe9f33f11bd1fbc4ac2bf219fc29cc5fa96d)
   - **Authors**: Yanxu Mao, Tiehan Cui, et al.
   - **Summary**: Comprehensive survey finding that multimodal attacks are significantly underexplored compared to text-only jailbreak approaches.
   - **Year**: 2025

7. **Title**: Can LLMs Deceive CLIP? Benchmarking Adversarial Compositionality (ACL 2025) (arXiv:2505.22943)
   - **Authors**: Not specified
   - **Summary**: Establishes that compositional vulnerabilities exist in multimodal representations, particularly in CLIP-based models.
   - **Year**: 2025

**Key Challenges**
1. **Compositional Reasoning Failures**: A significant portion (34%) of safety classification errors occur when individual modalities are correctly classified but their composition is not, indicating fundamental gaps in joint multimodal understanding.

2. **Persistent Compositional Vulnerabilities**: Despite substantial improvements in multimodal alignment (60% safety improvement), compositional vulnerabilities remain unaddressed by current safety techniques.

3. **Underexplored Multimodal Attack Surface**: Research on multimodal jailbreak attacks lags significantly behind text-only approaches, leaving critical attack vectors insufficiently studied.

4. **Individually-Safe Input Exploitation**: Existing attack methods rely on perturbed or adversarial inputs, while attacks using individually-safe inputs that become harmful only through composition represent an unexplored threat model.

5. **Cross-Modal Compositional Vulnerabilities**: Compositional attack surfaces extend across multiple modality combinations (vision-language, speech-audio), suggesting a systemic rather than modality-specific weakness.
