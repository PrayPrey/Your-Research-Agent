1. **Title**: Guided Self-Evolving LLMs with Minimal Human Supervision (arXiv:2512.02472)
   - **Authors**: Wenhao Yu, Zhenwen Liang, Chengsong Huang, Kishan Panaganti, Tianqing Fang, Haitao Mi, Dong Yu
   - **Summary**: This paper introduces R-Few, a framework that enables large language models (LLMs) to self-evolve with minimal human oversight. It employs a Self-Play Challenger-Solver mechanism where the Challenger generates synthetic questions guided by a small set of human-labeled examples, and the Solver trains on both human and synthetic data using an online, difficulty-based curriculum. This approach addresses issues like concept drift and diversity collapse, leading to consistent improvements in reasoning tasks.
   - **Year**: 2025

2. **Title**: Learning to Pose Problems: Reasoning-Driven and Solver-Adaptive Data Synthesis for Large Reasoning Models (arXiv:2511.09907)
   - **Authors**: Yongxian Wei, Yilin Zhao, Li Shen, Xinrui Chen, Runxi Cheng, Sinan Du, Hao Yu, Gang Liu, Jiahong Yan, Chun Yuan, Dian Li
   - **Summary**: The authors propose a problem generator that explicitly reasons to plan problem directions before synthesis and adapts difficulty to the solver's ability. By constructing related problem pairs and augmenting them with intermediate problem-design chains of thought, the generator calibrates difficulty based on solver feedback, producing problems near the solver's competence edge. This method achieves notable improvements across multiple reasoning benchmarks.
   - **Year**: 2025

3. **Title**: Learning Like Humans: Advancing LLM Reasoning Capabilities via Adaptive Difficulty Curriculum Learning and Expert-Guided Self-Reformulation (arXiv:2505.08364)
   - **Authors**: Enci Zhang, Xingang Yan, Wei Lin, Tianxiang Zhang, Qianchun Lu
   - **Summary**: Inspired by human learning strategies, this work introduces Adaptive Difficulty Curriculum Learning (ADCL) and Expert-Guided Self-Reformulation (EGSR) to enhance LLMs' reasoning abilities. ADCL addresses the dynamic perception of problem difficulty by periodically re-estimating it to align with the model's evolving capabilities. EGSR guides models to reformulate expert solutions within their own framework, fostering deeper understanding. Combined, these strategies significantly improve performance on challenging mathematical reasoning benchmarks.
   - **Year**: 2025

4. **Title**: AugGen: Synthetic Augmentation Can Improve Discriminative Models (arXiv:2503.11544)
   - **Authors**: Parsa Rahimi, Damien Teney, Sebastien Marcel
   - **Summary**: This paper presents a self-contained synthetic augmentation technique that samples from a conditional generative model trained solely on the target dataset. Applied to face recognition, this method achieves 1–12% performance improvements on benchmarks, outperforming models trained only on real data and existing synthetic data generation baselines. The findings highlight the significant impact of synthetic augmentation in data-scarce environments.
   - **Year**: 2025

5. **Title**: SK-VQA: Synthetic Knowledge Generation at Scale for Training Context-Augmented Multimodal LLMs (arXiv:2406.19593)
   - **Authors**: Xin Su, Man Luo, Kris W Pan, Tien Pei Chou, Vasudev Lal, Phillip Howard
   - **Summary**: The authors introduce SK-VQA, a large synthetic multimodal dataset containing over 2 million question-answer pairs requiring external knowledge. This dataset is designed to train multimodal LLMs for context-augmented generation, addressing the scarcity of naturally occurring data of this kind. Experiments demonstrate that SK-VQA serves as a challenging benchmark and effectively adapts generative multimodal models for retrieval-augmented generation settings.
   - **Year**: 2024

6. **Title**: Heterogeneous Face Recognition via Face Synthesis with Identity-Attribute Disentanglement (arXiv:2206.04854)
   - **Authors**: Ziming Yang, Jian Liang, Chaoyou Fu, Mandi Luo, Xiao-Yu Zhang
   - **Summary**: This work addresses heterogeneous face recognition by proposing a method that disentangles identity-related and identity-unrelated representations (attributes) in face images. A face synthesis module generates images with diverse attribute combinations, enriching the training data and improving recognition performance across different domains. The approach effectively tackles challenges like cross-domain discrepancy and limited heterogeneous data.
   - **Year**: 2022

7. **Title**: Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models (arXiv:2401.01335)
   - **Authors**: Zixiang Chen, Yihe Deng, Huizhuo Yuan, Kaixuan Ji, Quanquan Gu
   - **Summary**: The authors propose SPIN, a fine-tuning method that enables LLMs to self-improve without additional human-annotated data. SPIN employs a self-play mechanism where the model generates its own training data from previous iterations, refining its policy by distinguishing self-generated responses from human-annotated ones. This approach significantly enhances LLM performance across various benchmarks, demonstrating the potential of self-play in achieving human-level performance autonomously.
   - **Year**: 2024

8. **Title**: Ciliate: Towards Fairer Class-based Incremental Learning by Dataset and Training Refinement (arXiv:2304.04222)
   - **Authors**: Xuanqi Gao, Juan Zhai, Shiqing Ma, Chao Shen, Yufei Chen, Shiwei Wang
   - **Summary**: Ciliate is an automated technique designed to improve fairness in class-based incremental learning models. It identifies important samples and employs a debiased training method on these samples, effectively addressing fairness issues in incremental learning systems. The approach achieves comparable accuracy to existing methods while significantly enhancing fairness performance.
   - **Year**: 2023

**Key Challenges:**

1. **Model Collapse**: Repeated training on self-generated data can lead to models reinforcing their own biases, resulting in degraded performance or convergence towards low-entropy behaviors.

2. **Difficulty Calibration**: Determining the appropriate difficulty level of synthetic data is complex, as static metrics may not adapt to the model's evolving capabilities, leading to either redundant or misleading training data.

3. **Verification Reliability**: Relying on learned verifiers or reward models introduces the risk of inaccuracies, as these models can fail arbitrarily, potentially leading to mis-evolution or concept drift.

4. **Data Scarcity and Quality**: Generating high-quality synthetic data that effectively contributes to model improvement is challenging, especially in data-scarce environments where the diversity and representativeness of synthetic data are critical.

5. **Ethical and Safety Considerations**: Ensuring that self-improvement methods do not inadvertently introduce biases or unsafe behaviors is crucial, necessitating frameworks that prioritize safety, transparency, and societal well-being. 