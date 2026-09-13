## Related Work

**Related Papers**
1. **Title**: UniGuard: Towards Universal Safety Guardrails for Jailbreak Attacks on Multimodal Large Language Models (arXiv:2411.01703)
   - **Authors**: Oh et al.
   - **Summary**: Proposes joint consideration of unimodal and cross-modal harmful signals for detecting jailbreak attacks on multimodal LLMs, achieving 74% detection rate as a primary baseline approach.
   - **Year**: 2024

2. **Title**: SafeWatch: An Efficient Safety-Policy Following Video Guardrail Model (arXiv:2412.06878)
   - **Authors**: Chen et al.
   - **Summary**: Introduces policy-aware token pruning for video guardrail models, achieving 28.2% SOTA improvement with efficiency techniques applicable to multimodal safety architectures.
   - **Year**: 2024

3. **Title**: Bioinspired multisensory neural network with crossmodal integration and recognition
   - **Authors**: Tan, Zhou, Tao, Rosen, van Dijken
   - **Summary**: Develops cross-modal binding circuits capable of detecting threats when individual sensory channels appear benign, providing theoretical foundation for attention-as-binding mechanisms in safety systems.
   - **Year**: 2021

4. **Title**: SpeechGuard: Exploring the Adversarial Robustness of Multimodal Large Language Models
   - **Authors**: Peri et al.
   - **Summary**: Demonstrates 90% white-box attack success rate on speech LLMs, revealing significant vulnerability in the audio modality of multimodal systems.
   - **Year**: 2024

**Key Challenges**
1. **Fragmented Modality-Specific Solutions**: Existing safety approaches treat each modality separately with individual guardrails, lacking a unified framework that can address cross-modal threats holistically.

2. **Cross-Modal Attack Vulnerability**: Current systems fail to detect harmful content when threats are distributed across modalities, with individual channels appearing benign while combined signals are malicious.

3. **Absence of Super-Additive Detection**: No existing approach achieves super-additive safety detection where cross-modal analysis provides greater protection than the sum of individual modality defenses.

4. **Audio Modality Vulnerability**: Speech and audio components of multimodal LLMs demonstrate particularly high susceptibility to adversarial attacks, with 90% attack success rates in white-box settings.

5. **High Baseline Attack Success**: Without dedicated defense mechanisms, multimodal systems exhibit 81.6% attack success rates, indicating substantial unaddressed safety gaps.
