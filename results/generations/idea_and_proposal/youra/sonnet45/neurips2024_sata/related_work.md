## Related Work

**Related Papers**

1. **Title**: AutoBackdoor: Dual-Modality Contextual Backdoor Attacks
   - **Authors**: Not specified
   - **Summary**: Demonstrates dual-modality contextual backdoor attacks that achieve 90%+ success rate on LLM embodied agents. Defines the threat model addressed in this research by exploiting vision-language gaps in autonomous systems.
   - **Year**: 2025

2. **Title**: BlindGuard: Unsupervised Runtime Defense for LLM Agents
   - **Authors**: Not specified
   - **Summary**: Proposes corruption-guided contrastive learning for unsupervised runtime defense. Achieves approximately 70% detection rate but lacks dual-modality coverage and adaptive learning capabilities. Primary baseline comparison target.
   - **Year**: 2025

3. **Title**: GANSA: AIS Algorithm for Network Intrusion Detection
   - **Authors**: Not specified
   - **Summary**: Artificial Immune System (AIS) algorithm achieving 99% DDoS detection accuracy with 0.0003 false positive rate in network security domain. Demonstrates precedent for AIS application in cybersecurity.
   - **Year**: 2025

4. **Title**: IPIGuard: Architectural Defense via Tool Dependency Graph
   - **Authors**: Not specified
   - **Summary**: Proposes architectural defense mechanism using Tool Dependency Graph for agent security. Represents orthogonal approach that can be combined with runtime defenses for defense-in-depth.
   - **Year**: 2025

5. **Title**: HarmBench: Evaluation Framework for Red Teaming LLM Agents
   - **Authors**: Not specified
   - **Summary**: Comprehensive evaluation framework providing 18 red team methods and 629 test cases for LLM agent security assessment. Used for adversarial training and evaluation in this research.
   - **Year**: 2024

6. **Title**: AgentDojo: Security Benchmark for LLM Agents
   - **Authors**: Not specified
   - **Summary**: Provides 97 realistic agent tasks and 629 security test cases for evaluating agent behavior. Used for normal behavior profiling and evaluation baseline in this research.
   - **Year**: 2024

7. **Title**: Agent Security Bench: Comprehensive Security Benchmark
   - **Authors**: Not specified
   - **Summary**: Benchmark with 10 scenarios, 400+ tools, and 27 methods for agent security evaluation. Contributes to taxonomy of agent defense methods.
   - **Year**: 2024

8. **Title**: SafeAgent: Rule-Based Guards for LLM Agents
   - **Authors**: Not specified
   - **Summary**: Proposes rule-based guard mechanisms for agent security. Achieves approximately 60% detection rate, demonstrating limitations of rule-based approaches compared to ML-based anomaly detection.
   - **Year**: 2024

9. **Title**: ALMA: Adaptive Layered Mutation Algorithm for Network Intrusion Detection
   - **Authors**: Not specified
   - **Summary**: Generates adversarial examples and updates intrusion detector in 2-3 cycles. Achieves 98% detection accuracy and 90%+ detection on novel attacks within 2-3 adaptation cycles. Inspiration for adaptive learning module.
   - **Year**: 2024

10. **Title**: Multisensory Fusion for Deepfake Detection
    - **Authors**: Not specified
    - **Summary**: Applies multisensory fusion to deepfake detection using audio-visual inconsistency. Achieves 92% accuracy on FaceForensics++ dataset, demonstrating precedent for cross-domain transfer from neuroscience to adversarial ML.
    - **Year**: 2024

11. **Title**: llm-attacks: Universal Adversarial Attacks
    - **Authors**: Not specified
    - **Summary**: Gradient-based jailbreak attack methodology for LLMs. Widely cited work (4,500+ GitHub stars) providing reference for attack methodologies. Informs understanding of adversarial threat landscape.
    - **Year**: 2023

12. **Title**: DroidAIS: AIS for Android Malware Detection
    - **Authors**: Not specified
    - **Summary**: Applies Artificial Immune System to Android malware detection. Achieves 97% accuracy, demonstrating successful AIS transfer from biology to cybersecurity domain.
    - **Year**: 2023

13. **Title**: Multisensory Fusion for Multimodal Hate Speech Detection
    - **Authors**: Not specified
    - **Summary**: Applies multisensory fusion to multimodal hate speech detection using text-image semantics. Achieves 88% F1 on HatefulMemes dataset, showing precedent for text-visual fusion in adversarial settings.
    - **Year**: 2023

14. **Title**: MAML: Meta-Learning for Adversarial Robustness
    - **Authors**: Not specified
    - **Summary**: Meta-learning approach achieving 85% accuracy in 5-shot adaptation for image classification. Demonstrates rapid adaptation capability in adversarial contexts.
    - **Year**: 2023

15. **Title**: BadNets: Backdoor Attacks in Neural Networks
    - **Authors**: Not specified
    - **Summary**: Foundational work on backdoor attacks in neural networks using visual triggers. Referenced as methodology for synthesizing dual-modality attack dataset via visual trigger generation.
    - **Year**: Not specified

16. **Title**: McGurk Effect: Multisensory Integration
    - **Authors**: Not specified
    - **Summary**: Neuroscience phenomenon demonstrating cross-modal mismatch detection (visual "ga" + auditory "ba" → perceived "da"). Biological inspiration for dual-modality fusion detector design.
    - **Year**: Not specified

**Key Challenges**

1. **Static vs. Runtime Defense Gap**: Existing evaluation frameworks (HarmBench, AgentDojo) focus on pre-deployment testing and cannot monitor agent behavior during execution. Runtime attacks can only be detected with continuous monitoring systems.

2. **Text-Only Defense Limitations**: Most existing defenses focus on text-based attacks and do not address dual-modality backdoor threats. AutoBackdoor's 90%+ success rate demonstrates the vulnerability of vision-language gaps.

3. **Unsupervised vs. Supervised Learning Trade-off**: Unsupervised runtime defenses (BlindGuard) learn only from normal behavior and cannot leverage attack examples. This limits detection rates compared to supervised approaches using adversarial training.

4. **Lack of Adaptive Learning**: Static defenses cannot adapt to evolving attack patterns. Fixed rule-based systems and pre-trained models degrade as adversaries develop new attack methodologies.

5. **Runtime Overhead Constraints**: Many proposed defense mechanisms introduce prohibitive computational overhead (>20%), making deployment impractical for real-time embodied agents in latency-sensitive applications.

6. **Normal Behavior Distribution Assumption**: Applying AIS negative selection requires that normal agent behavior forms distinguishable clusters in feature space. High variability in agent tasks may violate this assumption.

7. **Cross-Modal Coherence Evasion**: Sophisticated adversaries may adversarially train backdoor triggers to maintain high text-visual coherence, evading naive fusion detectors. Requires adversarial training to distinguish malicious coherent inputs from benign ones.

8. **Benchmark-to-Deployment Gap**: Academic benchmarks may not fully represent real-world agent deployment scenarios, leading to distribution shift and reduced generalization of defense systems.

9. **Attack Sophistication Arms Race**: Adversaries aware of defense mechanisms will design attacks to evade detection, requiring continuous defense evolution and defense-in-depth strategies.

10. **Multi-Framework Generalization**: Agent frameworks (Langchain, AutoGPT, BabyAGI) have different architectures and execution patterns. Defense systems must generalize across diverse implementations without framework-specific customization.
