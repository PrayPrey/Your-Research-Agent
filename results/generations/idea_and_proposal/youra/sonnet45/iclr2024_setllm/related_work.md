## Related Work

**Related Papers**

1. **Title**: A Survey on Large Language Model (LLM) Security and Privacy: The Good, the Bad, and the Ugly
   - **Authors**: Yao et al.
   - **Summary**: Provides a seminal taxonomy of LLM security and privacy challenges, establishing the need for comprehensive trustworthiness solutions and identifying gaps in unified approaches.
   - **Year**: 2023

2. **Title**: LLM-Based Edge Intelligence: A Comprehensive Survey on Architectures, Applications, Security and Trustworthiness
   - **Authors**: Friha et al.
   - **Summary**: Surveys privacy, security, and interpretability for edge-deployed LLMs, identifying the lack of a unified framework for addressing these dimensions together.
   - **Year**: 2024

3. **Title**: FL-DPLoRA: An Integrated and Efficient Privacy-Preserving Training Framework for Large Language Models
   - **Authors**: Yang et al.
   - **Summary**: Introduces LoRA-based federated learning with differential privacy, achieving 99.7% communication reduction for privacy-preserving LLM training.
   - **Year**: 2025

4. **Title**: OpenFedLLM
   - **Authors**: Rui Ye et al.
   - **Summary**: Provides a complete federated learning framework for LLMs with LoRA, serving as an implementation baseline for privacy-preserving training.
   - **Year**: 2024

5. **Title**: APPFL
   - **Authors**: Not specified
   - **Summary**: Implements advanced privacy-preserving federated learning with differential privacy and secure aggregation mechanisms.
   - **Year**: Not specified

6. **Title**: UniGuardian: A Unified Defense for Detecting Prompt Injection, Backdoor Attacks and Adversarial Attacks in Large Language Models
   - **Authors**: Lin et al.
   - **Summary**: Presents the first unified defense system capable of detecting multiple attack types (prompt injection, backdoor, adversarial) simultaneously in LLMs.
   - **Year**: 2025

7. **Title**: llm-guard (protectai)
   - **Authors**: Not specified
   - **Summary**: Offers a production security toolkit with modular scanners for prompt injection, PII filtering, and toxicity detection in LLM deployments.
   - **Year**: Not specified

8. **Title**: BAIT: Large Language Model Backdoor Scanning by Inverting Attack Target
   - **Authors**: Shen et al.
   - **Summary**: Introduces black-box backdoor detection via target inversion, achieving top rankings in TrojAI competition for LLM backdoor detection.
   - **Year**: 2025

9. **Title**: Beyond Input Attribution: A Hands-On Tutorial to Concept-Based Explainable AI and Mechanistic Interpretability
   - **Authors**: Pastor et al.
   - **Summary**: Provides a comprehensive tutorial on mechanistic interpretability methods including attention analysis for understanding LLM behavior.
   - **Year**: 2025

10. **Title**: Spectral Zones-Based SHAP/LIME: Enhancing Interpretability in Spectral Deep Learning Models
    - **Authors**: Contreras et al.
    - **Summary**: Presents modified SHAP/LIME methods for grouped feature perturbations to enhance interpretability in deep learning models.
    - **Year**: 2024

11. **Title**: TrustLLM
    - **Authors**: HowieHwong
    - **Summary**: Establishes a comprehensive benchmark for evaluating LLM trustworthiness across dimensions including truthfulness, safety, fairness, robustness, privacy, and ethics.
    - **Year**: 2024

12. **Title**: Towards Unification of Hallucination Detection and Fact Verification for Large Language Models (UniFact)
    - **Authors**: Su et al.
    - **Summary**: Proposes a unified framework for hallucination detection and fact verification in LLMs, addressing trustworthiness from the factuality perspective.
    - **Year**: 2025

**Key Challenges**

1. **Lack of Unified Framework**: Existing approaches address privacy, security, and interpretability dimensions separately rather than in an integrated manner, creating gaps in comprehensive trustworthiness solutions.

2. **Runtime Security Monitoring**: Current systems lack continuous threat learning mechanisms that can adapt to evolving attack patterns during LLM deployment.

3. **Siloed Dimension Solutions**: Even recent unified approaches (2025) remain siloed by specific dimensions, failing to integrate privacy-security-interpretability in a single cohesive framework.

4. **Limited Cross-Layer Integration**: Existing benchmarks and frameworks evaluate trustworthiness dimensions independently without cross-layer metrics or integrated evaluation approaches.

5. **Adaptive Privacy Mechanisms**: Current privacy-preserving training methods lack client-aware sensitivity and adaptive differential privacy budget allocation for heterogeneous deployment contexts.

6. **Interpretability for Security Events**: Mechanistic interpretability has not been systematically applied to explain security events and threats in LLM systems, limiting transparency in security decision-making.

7. **Proactive Copyright Protection**: Existing frameworks do not adequately address proactive copyright protection mechanisms for LLM outputs and training data.
