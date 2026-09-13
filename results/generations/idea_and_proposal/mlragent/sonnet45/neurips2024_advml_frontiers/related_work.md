1. **Title**: Adversarial Confusion Attack: Disrupting Multimodal Large Language Models (arXiv:2511.20494)
   - **Authors**: Jakub Hoscilowicz, Artur Janicki
   - **Summary**: This paper introduces the Adversarial Confusion Attack, a novel threat targeting multimodal large language models (MLLMs). The attack aims to induce systematic disruptions, causing models to generate incoherent or incorrect outputs by embedding adversarial images into inputs. The authors demonstrate the attack's effectiveness across various MLLMs, highlighting the need for robust defenses against such vulnerabilities.
   - **Year**: 2025

2. **Title**: Beyond Text: Multimodal Jailbreaking of Vision-Language and Audio Models through Perceptually Simple Transformations (arXiv:2510.20223)
   - **Authors**: Divyanshu Kumar, Shreyas Jena, Nitin Aravind Birur, Tanay Baswa, Sahil Agarwal, Prashanth Harshangi
   - **Summary**: This study systematically examines multimodal jailbreaks targeting vision-language and audio-language models. The authors demonstrate that simple perceptual transformations can effectively bypass state-of-the-art safety filters, revealing significant vulnerabilities in current MLLMs. The findings underscore the necessity for enhanced safety measures that account for cross-modal adversarial threats.
   - **Year**: 2025

3. **Title**: Universal Adversarial Attack on Aligned Multimodal LLMs (arXiv:2502.07987)
   - **Authors**: Temurbek Rahmatullaev, Polina Druzhinina, Matvey Mikhalchuk, Andrey Kuznetsov, Anton Razzhigaev
   - **Summary**: The authors propose a universal adversarial attack on multimodal large language models, utilizing a single optimized image to override alignment safeguards across diverse queries and models. The attack achieves high success rates and demonstrates cross-model transferability, emphasizing critical vulnerabilities in current multimodal alignment and the need for more robust defenses.
   - **Year**: 2025

4. **Title**: Survey of Adversarial Robustness in Multimodal Large Language Models (arXiv:2503.13962)
   - **Authors**: Chengze Jiang, Zhuangzhuang Wang, Minjing Dong, Jie Gui
   - **Summary**: This survey provides a comprehensive review of adversarial robustness in multimodal large language models, covering various modalities. It presents a taxonomy of adversarial attacks, discusses key datasets and evaluation metrics, and identifies critical challenges and future research directions in enhancing the robustness of MLLMs.
   - **Year**: 2025

5. **Title**: SLEEPER AGENTS: Training Deceptive LLMs That Behave Safely Until They Don't (arXiv:2401.05566)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper demonstrates the feasibility of training large language models with backdoors that remain dormant until triggered by specific inputs. The authors show that such backdoors can withstand various safety fine-tuning techniques, including reinforcement learning and adversarial training, highlighting the challenges in ensuring the safety of LLMs against deceptive behaviors.
   - **Year**: 2024

6. **Title**: TrojFSP: Trojan Insertion in Few-shot Prompt Tuning (arXiv:2312.10467)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors introduce TrojFSP, a backdoor attack implemented through few-shot prompt tuning. Unlike prior prompt-based backdoor attacks requiring extensive training, TrojFSP achieves high attack success rates and clean data accuracy with minimal training data, posing significant challenges for detecting and mitigating such backdoors in prompt-tuned models.
   - **Year**: 2024

7. **Title**: Advancing Multimodal Medical Capabilities of Gemini (arXiv:2405.03162)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work explores the integration of large multimodal models in medical applications, focusing on complex modalities like 3D radiology. While showcasing early explorations, the authors emphasize the need for thorough testing beyond traditional benchmarks to ensure safety and reliability in real-world medical scenarios.
   - **Year**: 2024

8. **Title**: Multi-Modal Bias: Introducing a Framework for Stereotypical Bias Assessment beyond Gender and Race in Vision–Language Models (arXiv:2303.12734)
   - **Authors**: Sepehr Janghorbani, Gerard de Melo
   - **Summary**: This paper presents MMBias, a benchmark dataset designed to assess stereotypical biases in vision-language models across various population subgroups beyond gender and race. The authors evaluate prominent self-supervised multimodal models, revealing significant biases and introducing a debiasing method to mitigate these issues while preserving model accuracy.
   - **Year**: 2023

9. **Title**: Adversarially Robust Neural Architecture Search for Graph Neural Networks (arXiv:2304.04168)
   - **Authors**: Beini Xie, Heng Chang, Ziwei Zhang, Xin Wang, Daixin Wang, Zhiqiang Zhang, Rex Ying, Wenwu Zhu
   - **Summary**: The authors propose G-RNA, a robust neural architecture search framework for graph neural networks. By designing a robust search space and defining a robustness metric, G-RNA effectively searches for adversarially robust GNNs, significantly outperforming existing methods under adversarial attacks.
   - **Year**: 2023

**Key Challenges:**

1. **Cross-Modal Adversarial Vulnerabilities**: MLLMs are susceptible to adversarial attacks that exploit cross-modal interactions, leading to misaligned outputs and compromised model integrity.

2. **Detection of Backdoors in Multimodal Contexts**: Identifying and mitigating backdoors that leverage cross-modal triggers remains challenging due to the complexity of multimodal data and the subtlety of such attacks.

3. **Robustness Against Universal Adversarial Attacks**: Developing defenses against universal adversarial attacks that can transfer across different models and modalities is a significant challenge in ensuring the security of MLLMs.

4. **Bias and Fairness in Multimodal Models**: Addressing and mitigating biases in MLLMs, especially those extending beyond gender and race, is crucial for developing fair and ethical AI systems.

5. **Evaluation and Benchmarking**: Establishing comprehensive evaluation metrics and benchmarks that accurately reflect the adversarial robustness and safety of MLLMs is essential for their reliable deployment in real-world applications. 