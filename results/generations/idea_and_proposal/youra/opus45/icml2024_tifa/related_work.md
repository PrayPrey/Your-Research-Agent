## Related Work

**Related Papers**
1. **Title**: Understanding the Limits of VLMs Through the Lens of the Binding Problem (arXiv:2411.00238)
   - **Authors**: Campbell, Webb, Griffiths, Cohen et al.
   - **Summary**: Demonstrates that VLM failures mirror human perceptual binding limitations, providing a theoretical foundation for applying the binding framework to understand and address VLM vulnerabilities.
   - **Year**: 2024

2. **Title**: Cross-Modal Safety Mechanism Transfer in Large Vision-Language Models (ICLR 2025)
   - **Authors**: Xu, Pang, Zhu, Shen, Cheng
   - **Summary**: Reveals that hidden states at specific transformer layers activate safety mechanisms, and demonstrates that vision-language alignment fails to transfer safety patterns across modalities.
   - **Year**: 2025

3. **Title**: Revisiting Adversarial Robustness of VLMs: A Multimodal Perspective (arXiv:2404.19287)
   - **Authors**: Zhou, Bai, Zhao, Chen
   - **Summary**: Introduces the MMCoA framework for multimodal contrastive adversarial training, providing a methodological basis for binding-aware training approaches.
   - **Year**: 2024

4. **Title**: MMDT: Decoding Trustworthiness and Safety of Multimodal Foundation Models
   - **Authors**: Xu, Zhang, Chen, Li, Song et al.
   - **Summary**: Presents the first unified safety evaluation platform for multimodal foundation models, establishing benchmark infrastructure for safety assessment.
   - **Year**: 2025

5. **Title**: Stage-wise Attention-Guided Adversarial Attack on LVLMs (SAGA) (arXiv:2602.04356)
   - **Authors**: Kwak, Cao, Cho, Lee, Ahn, Yun
   - **Summary**: Demonstrates that attention scores positively correlate with adversarial loss sensitivity, validating attention-based approaches for measuring model vulnerability.
   - **Year**: 2026

6. **Title**: Cross-Modal Attention Guided Unlearning in Vision-Language Models (CAGUL) (arXiv:2510.07567)
   - **Authors**: Bhaila, Komanduri, Van, Wu
   - **Summary**: Shows that cross-modal attention can identify safety-relevant visual tokens, demonstrating the utility of attention mechanisms as a proxy for safety analysis.
   - **Year**: 2025

7. **Title**: Multimodal Safety Is Asymmetric
   - **Authors**: Wang et al.
   - **Summary**: Provides empirical evidence that visual alignment creates uneven safety constraints across modalities, validating claims of compositional safety failure in multimodal systems.
   - **Year**: 2025

8. **Title**: MMCoA GitHub Repository
   - **Authors**: Not specified
   - **Summary**: Provides the codebase for the MMCoA framework, serving as a foundation for extending and implementing binding-aware training methods.
   - **Year**: Not specified

**Key Challenges**
1. **Cross-Modal Safety Transfer Failure**: Vision-language alignment in current VLMs fails to transfer safety patterns learned in one modality to another, leaving compositional inputs vulnerable.

2. **Binding Problem in VLMs**: VLMs exhibit failures analogous to human perceptual binding limitations, struggling to correctly associate attributes with objects across modalities.

3. **Asymmetric Multimodal Safety**: Safety constraints are unevenly applied across visual and textual modalities, creating exploitable gaps when inputs are composed across modalities.

4. **Attention-Vulnerability Correlation**: Attention mechanisms correlate with adversarial sensitivity, indicating that current attention-based fusion approaches may inadvertently expose safety-critical pathways.

5. **Lack of Unified Evaluation Infrastructure**: Prior to recent benchmarking efforts, there was no unified platform for evaluating trustworthiness and safety across diverse multimodal foundation models.
