1. **Title**: Scalable Data Attribution via Forward-Only Test-Time Inference (arXiv:2511.19803)
   - **Authors**: Sibo Ma, Julian Nyarko
   - **Summary**: This paper introduces a data attribution method that eliminates the need for per-query backward passes by simulating each training example's parameter influence through short-horizon gradient propagation during training. At inference, attributions are read out using only forward evaluations, achieving orders-of-magnitude lower inference cost while matching or surpassing state-of-the-art baselines.
   - **Year**: 2025

2. **Title**: Fast Data Attribution for Text-to-Image Models (arXiv:2511.10721)
   - **Authors**: Sheng-Yu Wang, Aaron Hertzmann, Alexei A. Efros, Richard Zhang, Jun-Yan Zhu
   - **Summary**: The authors propose a scalable and efficient data attribution approach for text-to-image models by distilling a slow, unlearning-based attribution method into a feature embedding space. This enables rapid retrieval of influential training images without running expensive attribution algorithms, achieving performance improvements up to 400,000x faster than existing methods.
   - **Year**: 2025

3. **Title**: Natural Geometry of Robust Data Attribution: From Convex Models to Deep Networks (arXiv:2512.09103)
   - **Authors**: Shihao Li, Jiachen Li, Dongmei Chen
   - **Summary**: This work presents a unified framework for certified robust attribution extending from convex models to deep networks. It introduces the Natural Wasserstein metric to measure perturbations in the geometry induced by the model's feature covariance, reducing worst-case sensitivity and stabilizing attribution estimates.
   - **Year**: 2025

4. **Title**: FPEdit: Robust LLM Fingerprinting through Localized Knowledge Editing (arXiv:2508.02092)
   - **Authors**: Shida Wang, Chaohu Liu, Yubo Wang, Linli Xu
   - **Summary**: FPEdit introduces a knowledge-editing framework that embeds semantically coherent natural language fingerprints into large language models by modifying a sparse subset of model weights. This approach ensures stealthy and precise ownership encoding without degrading core functionality, achieving high fingerprint retention under various adaptation scenarios.
   - **Year**: 2025

5. **Title**: EditMF: Drawing an Invisible Fingerprint for Your Large Language Models (arXiv:2508.08836)
   - **Authors**: Jiaxuan Wu, Yinghan Zhou, Wanli Peng, Yiming Xue, Juan Wen, Ping Zhong
   - **Summary**: EditMF proposes a training-free fingerprinting paradigm that embeds highly imperceptible fingerprints into large language models with minimal computational overhead. It maps ownership bits to compact, semantically coherent triples and injects the fingerprint without perturbing unrelated knowledge, ensuring robustness and imperceptibility.
   - **Year**: 2025

6. **Title**: FP-VEC: Fingerprinting Large Language Models via Efficient Vector Addition (arXiv:2409.08846)
   - **Authors**: Zhenhua Xu, Wenpeng Xing, Zhebo Wang, Chang Hu, Chen Jie, Meng Han
   - **Summary**: FP-VEC introduces a scalable and lightweight method for fingerprinting large language models by embedding a fingerprint vector through vector addition. This approach allows the same fingerprint to be seamlessly incorporated into multiple models, facilitating efficient ownership authentication.
   - **Year**: 2024

7. **Title**: Foundation Models and Fair Use (arXiv:2303.15715)
   - **Authors**: Peter Henderson, Xuechen Li, Dan Jurafsky, Tatsunori Hashimoto, Mark A. Lemley, Percy Liang
   - **Summary**: This paper discusses the legal and ethical implications of training foundation models on copyrighted material. It emphasizes the importance of data attribution for ensuring fair use and compliance with copyright laws, highlighting the need for transparent and efficient attribution methods.
   - **Year**: 2023

8. **Title**: An Efficient Framework for Crediting Data Contributors of Diffusion Models (arXiv:2407.03153)
   - **Authors**: Chris Lin, Mingyu Lu, Chanwoo Kim, Su-In Lee
   - **Summary**: The authors introduce a method to efficiently retrain and rerun inference for Shapley value estimation, enabling the appraisal of data contributors' impact on diffusion models. This framework facilitates fair compensation and incentivizes sharing quality data.
   - **Year**: 2024

9. **Title**: Unlocking the Effectiveness of LoRA-FP for Seamless Transfer (arXiv:2507.08459)
   - **Authors**: Zishan Xu, Shuyi Xie, Qingsong Lv, Shupei Xiao, Linlin Song, Sui Wenjuan, Fan Lin
   - **Summary**: LoRA-FP is a lightweight and modular framework that embeds backdoor fingerprints into LoRA adapters through constrained fine-tuning. These adapters can be fused into downstream models without full-parameter updates, achieving robustness under adversarial conditions and preserving model utility.
   - **Year**: 2025

10. **Title**: Architectures for Data-Aware LLMs: Models that Reason About Their Own Training Signal (arXiv:202512.0566)
    - **Authors**: Feng Chen
    - **Summary**: This paper outlines a paradigm of data-aware large language models that treat training data and learning history as first-class objects of computation. It emphasizes the need for models to reason about their own training signals to improve transparency and reliability.
    - **Year**: 2025

**Key Challenges:**

1. **Scalability of Attribution Methods**: Existing attribution techniques often require significant computational resources, making them impractical for large-scale foundation models. Developing efficient methods that can operate in real-time during inference is a critical challenge.

2. **Accuracy and Precision**: Balancing computational efficiency with the accuracy of attribution remains difficult. Simplified methods may lack precision, while precise methods can be computationally prohibitive.

3. **Robustness to Model Adaptations**: Ensuring that attribution methods remain effective under various model adaptations, such as fine-tuning or pruning, is essential for their reliability in dynamic deployment scenarios.

4. **Legal and Ethical Compliance**: As foundation models are trained on vast datasets, often including copyrighted material, ensuring compliance with legal frameworks and ethical standards through accurate data attribution is increasingly important.

5. **Integration with Existing Systems**: Developing attribution methods that can be seamlessly integrated into existing foundation model architectures without significant modifications poses a technical challenge. 