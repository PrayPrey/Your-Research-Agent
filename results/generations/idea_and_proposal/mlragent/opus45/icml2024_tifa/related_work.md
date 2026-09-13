1. **Title**: CAMME: Adaptive Deepfake Image Detection with Multi-Modal Cross-Attention (arXiv:2505.18035)
   - **Authors**: Naseem Khan, Tuan Nguyen, Amine Bermak, Issa Khalil
   - **Summary**: This paper introduces CAMME, a framework that integrates visual, textual, and frequency-domain features using a multi-head cross-attention mechanism to detect deepfake images. It demonstrates robust cross-domain generalization and resilience against adversarial attacks, achieving over 91% accuracy under natural image perturbations and high accuracy against PGD and FGSM adversarial attacks.
   - **Year**: 2025

2. **Title**: MMCert: Provable Defense against Adversarial Attacks to Multi-modal Models (arXiv:2403.19080)
   - **Authors**: Yanting Wang, Hongye Fu, Wei Zou, Jinyuan Jia
   - **Summary**: MMCert is the first certified defense against adversarial attacks targeting multi-modal models. It provides a lower bound on performance under arbitrary adversarial attacks with bounded perturbations across modalities. Evaluations on multi-modal road segmentation and emotion recognition tasks show that MMCert outperforms existing certified defenses extended from unimodal models.
   - **Year**: 2024

3. **Title**: Breaking the Illusion: Consensus-Based Generative Mitigation of Adversarial Illusions in Multi-Modal Embeddings (arXiv:2511.21893)
   - **Authors**: Fatemeh Akbarian, Anahita Baninajjar, Yingyi Zhang, Ananth Balashankar, Amir Aminifar
   - **Summary**: This work addresses adversarial illusions in multi-modal embeddings by proposing a task-agnostic mitigation mechanism that reconstructs inputs through generative models to maintain natural alignment. A consensus-based aggregation scheme over generated samples effectively reduces attack success rates and improves cross-modal alignment, providing a model-agnostic defense against adversarial illusions.
   - **Year**: 2025

4. **Title**: Jailbreak in Pieces: Compositional Adversarial Attacks on Multi-Modal Language Models (arXiv:2307.14539)
   - **Authors**: Erfan Shayegani, Yue Dong, Nael Abu-Ghazaleh
   - **Summary**: The authors introduce cross-modality attacks on vision-language models by pairing adversarial images with textual prompts to break model alignment. The attacks employ a compositional strategy combining images targeted towards toxic embeddings with generic prompts, achieving high success rates across different VLMs and highlighting the need for new alignment approaches in multi-modal models.
   - **Year**: 2023

5. **Title**: Learning to Attack: Towards Textual Adversarial Attacking in Real-world Situations (arXiv:2009.09192)
   - **Authors**: Yuan Zang, Bairu Hou, Fanchao Qi, Zhiyuan Liu, Xiaojun Meng, Maosong Sun
   - **Summary**: This paper proposes a reinforcement learning-based attack model that learns from attack history to launch more efficient textual adversarial attacks. Evaluations on sentiment analysis, text classification, and natural language inference tasks demonstrate better attack performance and higher efficiency compared to baseline methods, contributing to the understanding of adversarial vulnerabilities in NLP systems.
   - **Year**: 2024

6. **Title**: A∋D: A Platform of Searching for Robust Neural Architectures (arXiv:2203.03128)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The paper introduces a platform called Auto Adversarial Attack and Defense (A∋D), which integrates auto adversarial defense and attack mechanisms. It provides a fair comparison environment for research on AutoML for adversarial attack and defense, aiming to improve the robustness of neural architectures and the effectiveness of adversarial attacks.
   - **Year**: 2024

7. **Title**: Knowledge as Priors: Cross-Modal Knowledge Generalization for Datasets without Superior Knowledge (arXiv:2004.00176)
   - **Authors**: Long Zhao, Xi Peng, Yuxiao Chen, Mubbasir Kapadia, Dimitris N. Metaxas
   - **Summary**: This work proposes a scheme to train models in target datasets where superior knowledge is unavailable by generalizing cross-modal knowledge learned from source datasets. The method models knowledge as priors on parameters, demonstrating competitive performance for 3D hand pose estimation on benchmark datasets.
   - **Year**: 2024

8. **Title**: Multi-Modal Bias: Introducing a Framework for Stereotypical Bias Assessment beyond Gender and Race in Vision–Language Models (arXiv:2303.12734)
   - **Authors**: Sepehr Janghorbani, Gerard de Melo
   - **Summary**: The authors present MMBias, a benchmark dataset covering 14 population subgroups to assess bias in vision-language models. Evaluations of models like CLIP, ALBEF, and ViLT reveal meaningful biases favoring certain groups. A debiasing method is introduced to mitigate bias while preserving model accuracy.
   - **Year**: 2023

9. **Title**: Learning Transferable Visual Models From Natural Language Supervision (arXiv:2103.00020)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper explores training visual models using natural language supervision by predicting which text is paired with which image, rather than the exact words. The approach leverages a contrastive objective, resulting in efficient learning of transferable visual representations.
   - **Year**: 2024

10. **Title**: When Text and Images Don’t Mix: Uncovering and Mitigating the Impact of Modality Biases in Vision-Language Models (arXiv:2407.17083)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: The paper identifies a peculiarity in the CLIP latent space where text embeddings are highly clustered together, affecting anomaly detection performance. The authors propose BLISS, an anomaly scoring approach that addresses this bias by measuring similarities against a large, external source of text inputs, achieving state-of-the-art performance on benchmark datasets.
    - **Year**: 2024

**Key Challenges**:

1. **Cross-Modal Adversarial Vulnerabilities**: Multi-modal models are susceptible to adversarial attacks that exploit the shared representation space, leading to misalignment and erroneous outputs across modalities.

2. **Detection and Defense Mechanisms**: Developing effective real-time monitoring and defense mechanisms to detect and mitigate cross-modal adversarial attacks remains a significant challenge.

3. **Bias and Fairness**: Ensuring that multi-modal models do not perpetuate or amplify biases present in training data, especially across diverse population subgroups, is crucial for trustworthy deployment.

4. **Robustness to Unseen Attacks**: Models need to maintain performance and reliability when exposed to novel or unseen adversarial attacks, requiring adaptive and generalizable defense strategies.

5. **Efficient Training and Evaluation**: Balancing the computational cost of training robust multi-modal models with the need for comprehensive evaluation against a wide range of adversarial scenarios is a persistent challenge. 