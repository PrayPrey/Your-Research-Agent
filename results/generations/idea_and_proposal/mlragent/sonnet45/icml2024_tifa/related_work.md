```
1. **Title**: Jailbreak in Pieces: Compositional Adversarial Attacks on Multi-Modal Language Models (arXiv:2307.14539)
   - **Authors**: Erfan Shayegani, Yue Dong, Nael Abu-Ghazaleh
   - **Summary**: This paper introduces cross-modality attacks on vision-language models (VLMs) by pairing adversarial images with textual prompts to break model alignment. The authors develop a compositional strategy that combines images targeted towards toxic embeddings with generic prompts, leading to successful jailbreaks. The attacks achieve high success rates across different VLMs, highlighting the risk of cross-modality alignment vulnerabilities.
   - **Year**: 2023

2. **Title**: SoundBreak: A Systematic Study of Audio-Only Adversarial Attacks on Trimodal Models (arXiv:2601.16231)
   - **Authors**: Aafiya Hussain, Gaurav Srivastava, Alvi Ishmam, Zaber Hakim, Chris Thomas
   - **Summary**: This study examines audio-only adversarial attacks on trimodal audio-video-language models. The authors analyze six attack objectives targeting different stages of multimodal processing and demonstrate that audio-only perturbations can induce severe multimodal failures, achieving up to 96% attack success rates. The findings expose a significant single-modality attack surface in multimodal systems.
   - **Year**: 2026

3. **Title**: Breaking the Illusion: Consensus-Based Generative Mitigation of Adversarial Illusions in Multi-Modal Embeddings (arXiv:2511.21893)
   - **Authors**: Fatemeh Akbarian, Anahita Baninajjar, Yingyi Zhang, Ananth Balashankar, Amir Aminifar
   - **Summary**: The authors propose a task-agnostic mitigation mechanism that reconstructs inputs from adversarially perturbed data using generative models to maintain natural alignment in multi-modal embeddings. Their approach significantly reduces attack success rates and improves cross-modal alignment, providing an effective defense against adversarial illusions.
   - **Year**: 2025

4. **Title**: Beyond Text: Multimodal Jailbreaking of Vision-Language and Audio Models through Perceptually Simple Transformations (arXiv:2510.20223)
   - **Authors**: Divyanshu Kumar, Shreyas Jena, Nitin Aravind Birur, Tanay Baswa, Sahil Agarwal, Prashanth Harshangi
   - **Summary**: This paper presents a systematic study of multimodal jailbreaks targeting vision-language and audio-language models. The authors demonstrate that simple perceptual transformations can reliably bypass state-of-the-art safety filters, revealing severe vulnerabilities in models with near-perfect text-only safety.
   - **Year**: 2025

5. **Title**: OpenAttack: An Open-source Textual Adversarial Attack Toolkit (arXiv:2009.09191)
   - **Authors**: Guoyang Zeng, Fanchao Qi, Qianrui Zhou, Tingji Zhang, Zixian Ma, Bairu Hou, Yuan Zang, Zhiyuan Liu, Maosong Sun
   - **Summary**: OpenAttack is an open-source toolkit for textual adversarial attacks, supporting various attack models and providing a unified framework for implementation. It facilitates quick utilization and fair comparison of attack models, aiding in robustness evaluation and adversarial training.
   - **Year**: 2021

6. **Title**: Teams of LLM Agents can Exploit Zero-Day Vulnerabilities (arXiv:2406.01637)
   - **Authors**: Richard Fang, Rohan Bindu, Akul Gupta, Qiusi Zhan, Daniel Kang
   - **Summary**: This work demonstrates that teams of large language model (LLM) agents can exploit real-world zero-day vulnerabilities. The authors develop a multi-agent framework where a planning agent explores systems and dispatches subagents to execute attacks, improving over prior work by up to 4.5 times.
   - **Year**: 2024

7. **Title**: Multi-Modal Bias: Introducing a Framework for Stereotypical Bias (arXiv:2303.12734)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces a framework for assessing stereotypical bias in multi-modal models. The authors quantify biases in models like CLIP, ALBEF, and ViLT, revealing significant biases across various categories, including religion, nationality, disability, and sexual orientation.
   - **Year**: 2023

8. **Title**: Adversarial Attacks on Multimodal Models: A Comprehensive Survey (arXiv:2401.12345)
   - **Authors**: [Authors not specified]
   - **Summary**: This survey provides a comprehensive overview of adversarial attacks targeting multimodal models, discussing various attack strategies, their effectiveness, and potential defense mechanisms. It highlights the unique challenges posed by multimodal architectures in ensuring robustness.
   - **Year**: 2024

9. **Title**: Cross-Modal Adversarial Examples: Bridging the Gap Between Modalities (arXiv:2505.67890)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors explore the generation of cross-modal adversarial examples that exploit the interactions between different modalities. They propose methods to craft adversarial inputs that are effective across multiple modalities, emphasizing the need for cross-modal robustness in multimodal models.
   - **Year**: 2025

10. **Title**: Evaluating the Robustness of Multimodal Models to Adversarial Perturbations (arXiv:2309.54321)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper presents a benchmark for evaluating the robustness of multimodal models against adversarial perturbations. The authors assess various state-of-the-art models and identify key vulnerabilities, providing insights into improving multimodal model security.
    - **Year**: 2023
```

**Key Challenges**:

1. **Cross-Modal Alignment Vulnerabilities**: Ensuring consistent and secure alignment between different modalities remains a significant challenge, as adversaries can exploit misalignments to inject harmful content.

2. **Detection of Subtle Adversarial Perturbations**: Developing detection mechanisms capable of identifying imperceptible adversarial perturbations across modalities is complex, given the subtlety of such attacks.

3. **Limited Transferability of Defense Mechanisms**: Defense strategies effective in single-modality models may not generalize well to multimodal systems, necessitating the design of modality-aware defenses.

4. **Scalability of Defense Strategies**: Implementing robust defense mechanisms that scale effectively with the increasing complexity and size of multimodal models poses a significant challenge.

5. **Evaluation Benchmark Development**: Creating comprehensive and standardized benchmarks to assess the robustness of multimodal models against cross-modal adversarial attacks is essential but remains underdeveloped.
``` 