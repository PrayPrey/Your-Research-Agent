## Related Work

**Related Papers**

1. **Title**: MMCert: Provable Defense Against Adversarial Attacks to Multi-Modal Models
   - **Authors**: Yanting Wang, Hongye Fu, Wei Zou, Jinyuan Jia
   - **Summary**: First certified defense with provable robustness guarantees for multi-modal models using randomized smoothing. Focuses on input-level certification with provable robustness guarantees.
   - **Year**: 2024 (CVPR 2024)

2. **Title**: On the Adversarial Robustness of Multi-Modal Foundation Models
   - **Authors**: Christian Schlarmann, Matthias Hein
   - **Summary**: Demonstrates that imperceptible image perturbations can manipulate multi-modal model text outputs and proves that alignment does not equal adversarial robustness in multi-modal systems.
   - **Year**: 2023 (ICCVW 2023)

3. **Title**: Robust-LLaVA: On the Effectiveness of Large-Scale Robust Image Encoders for Multi-modal Large Language Models
   - **Authors**: H. Malik, Fahad Shamshad, Muzammal Naseer, Karthik Nandakumar, F. Khan, Salman H. Khan
   - **Summary**: Adversarially pre-trained vision encoders improve MLLM robustness with 2x gain and 10% jailbreak improvement through encoder-hardening approach.
   - **Year**: 2025

4. **Title**: Adversarial Robustness for Visual Grounding of Multimodal Large Language Models
   - **Authors**: Kuofeng Gao, Yang Bai, Jiawang Bai, Yong Yang, Shu-Tao Xia
   - **Summary**: First exploration of adversarial robustness for visual grounding; proposes untargeted, targeted, and permuted attack paradigms for multi-modal models.
   - **Year**: 2024

5. **Title**: Cross-Modal Safety Alignment: Is textual unlearning all you need?
   - **Authors**: Trishna Chakraborty, Erfan Shayegani, Zikui Cai, et al. (8 authors)
   - **Summary**: Demonstrates that textual unlearning transfers to multi-modal safety (ASR<8%) and shows that multi-modal datasets offer no benefit over text-only approaches for safety alignment.
   - **Year**: 2024

6. **Title**: MDAPT: Multi-Modal Depth Adversarial Prompt Tuning to Enhance the Adversarial Robustness of Visual Language Models
   - **Authors**: Chao Li, Yonghao Liao, Caichang Ding, Zhiwei Ye
   - **Summary**: Multi-modal fine-tuning improves accuracy (17.84%) and robustness (10.85%) through prompt tuning approach at the input level.
   - **Year**: 2025

7. **Title**: Explaining and Harnessing Adversarial Examples
   - **Authors**: Goodfellow et al.
   - **Summary**: Foundational work introducing FGSM attack and establishing core concepts in adversarial robustness.
   - **Year**: 2015

8. **Title**: Towards Deep Learning Models Resistant to Adversarial Attacks
   - **Authors**: Madry et al.
   - **Summary**: Introduces PGD adversarial training as a foundational defense method against adversarial attacks.
   - **Year**: 2018

9. **Title**: Certified Adversarial Robustness via Randomized Smoothing
   - **Authors**: Cohen et al.
   - **Summary**: Establishes randomized smoothing as a foundation for certified defenses, which MMCert builds upon for multi-modal models.
   - **Year**: 2019

10. **Title**: Learning Transferable Visual Models From Natural Language Supervision (CLIP)
    - **Authors**: Radford et al.
    - **Summary**: Foundational multi-modal architecture using contrastive learning for vision-language alignment. Defines fusion-layer structures that require defense.
    - **Year**: 2021

11. **Title**: Visual Instruction Tuning (LLaVA)
    - **Authors**: Liu et al.
    - **Summary**: Multi-modal large language model architecture that combines vision encoders with language models, representing architectures that ICMD-Net aims to defend.
    - **Year**: 2023

12. **Title**: Attention Is All You Need
    - **Authors**: Vaswani et al.
    - **Summary**: Introduces attention mechanisms inspired by neuroscience, establishing precedent for biological analogies in machine learning (relevant to immune-inspired defense architecture).
    - **Year**: 2017

13. **Title**: SafeTensors Security Audit
    - **Authors**: Not specified
    - **Summary**: Security audit of model serialization format addressing supply chain attacks in model distribution, complementary to runtime adversarial defenses.
    - **Year**: Not specified

**Key Challenges**

1. **Fusion Layer Vulnerability (Gap 1)**: Existing adversarial defenses do not explicitly protect fusion layers in multi-modal models where cross-modal attacks propagate. No prior work has formalized cross-modal attack propagation mechanisms or developed fusion-layer-specific defenses.

2. **Single-Layer Defense Limitation (Gap 2)**: Current defenses operate at single layers (MMCert: input-level smoothing only, Robust-LLaVA: vision encoder only) without coordinated multi-layer protection, leaving multi-modal models vulnerable to attacks that bypass individual defenses.

3. **Lack of Cross-Modal Attack Databases (Gap 3)**: Attack databases exist for single-modality scenarios (e.g., ImageNet-C) but not for cross-modal attacks, limiting systematic evaluation and defense development for multi-modal adversarial robustness.

4. **Fusion-Layer Certification Gap (Gap 4)**: Certified defenses have been proven at the input level (randomized smoothing), but fusion-layer certification remains unexplored, leaving uncertainty about whether robustness guarantees propagate through encoder and fusion layers.

5. **Adaptive Attack Resilience**: Known attack pattern databases can be circumvented by adaptive attackers who generate novel attacks outside known clusters, requiring continuous defense evolution.

6. **Architectural Dependency**: Fusion consistency verification mechanisms may be architecture-dependent, potentially limiting applicability across different multi-modal model designs.

7. **Performance-Security Trade-offs**: Defense mechanisms introduce computational overhead (latency, complexity) that must be balanced against security requirements, particularly for real-time applications.

8. **Cross-Modal Inconsistency Exploitation**: Adversarial attacks exploit semantic inconsistencies between modalities (e.g., imperceptible image perturbations that fool vision encoders while text encoders expect different semantic content), requiring cross-modal verification approaches.
