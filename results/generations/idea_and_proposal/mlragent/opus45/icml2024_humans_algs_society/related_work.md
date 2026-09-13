1. **Title**: Drift: Decoding-time Personalized Alignments with Implicit User Preferences (arXiv:2502.14289)
   - **Authors**: Minbeom Kim, Kang-il Lee, Seongho Joo, Hwaran Lee, Kyomin Jung
   - **Summary**: This paper introduces Drift, a framework that personalizes large language models (LLMs) at decoding time using implicit user preferences. Unlike traditional reinforcement learning from human feedback (RLHF), which requires extensive annotated data and gradient updates, Drift operates in a training-free manner with minimal examples. It models user preferences through predefined, interpretable attributes and aligns them during decoding, enabling personalized generation. Experiments demonstrate that Drift outperforms RLHF baselines with significantly fewer examples, offering computational efficiency and interpretability.
   - **Year**: 2025

2. **Title**: CausalTAD: Causal Implicit Generative Model for Debiased Online Trajectory Anomaly Detection (arXiv:2412.18820)
   - **Authors**: Wenbin Li, Di Yao, Chang Gong, Xiaokai Chu, Quanliang Jing, Xiaolei Zhou, Yuxuan Zhang, Yunxia Fan, Jingping Bi
   - **Summary**: CausalTAD addresses trajectory anomaly detection by estimating anomaly risks of trajectories given source-destination pairs. The authors highlight that existing methods are confounded by road network preferences, leading to biases. CausalTAD employs do-calculus to eliminate this confounding bias, estimating the anomaly criterion as \( P(T|do(C)) \). Experiments show that CausalTAD achieves superior performance on both trained and out-of-distribution trajectories, improving generalization by mitigating confounding biases.
   - **Year**: 2024

3. **Title**: Walking the Tightrope: Disentangling Beneficial and Detrimental Drifts in Non-Stationary Custom-Tuning (arXiv:2505.13081)
   - **Authors**: Xiaoyu Yang, Jie Lu, En Yu
   - **Summary**: This paper uncovers detrimental concept drift within chain-of-thought reasoning during non-stationary reinforcement fine-tuning (RFT) in multi-modal large language models (MLLMs). The authors establish a theoretical connection between concept drift theory and RFT processes, formalizing autoregressive token streams as non-stationary distributions. They propose Counterfactual Preference Optimization (CPO), which decouples beneficial distribution adaptation from harmful concept drift using concept graph-empowered LLM experts generating counterfactual reasoning trajectories. Experiments demonstrate CPO's robustness and generalization in non-stationary environments, particularly in the medical domain.
   - **Year**: 2025

4. **Title**: DPR: An Algorithm Mitigate Bias Accumulation in Recommendation Feedback Loops (arXiv:2311.05864)
   - **Authors**: Hangtong Xu, Yuanbo Xu, Yongjian Yang, Fuzhen Zhuang, Hui Xiong
   - **Summary**: DPR addresses biases in recommendation models trained on user feedback, which are influenced by exposure mechanisms leading to false negative samples. The authors analyze data exposure mechanisms under the Missing Not At Random (MNAR) assumption and propose Dynamic Personalized Ranking (DPR), an unbiased algorithm using dynamic re-weighting to mitigate the effects of exposure mechanisms and feedback loops. They also introduce Universal Anti-False Negative (UFN) to address false negative issues. Theoretical and experimental results demonstrate that DPR effectively handles bias accumulation, improving recommendation quality.
   - **Year**: 2023

5. **Title**: On the Algorithmic Bias of Aligning Large Language Models with RLHF: Preference Collapse and Matching Regularization (arXiv:2405.16455)
   - **Authors**: Jiancong Xiao, Ziniu Li, Xingyu Xie, Emily Getzen, Cong Fang, Qi Long, Weijie J. Su
   - **Summary**: This paper examines the algorithmic bias in aligning large language models (LLMs) with human preferences using reinforcement learning from human feedback (RLHF). The authors identify a phenomenon termed "preference collapse," where minority preferences are disregarded due to KL-based regularization in RLHF. To mitigate this bias, they introduce preference matching (PM) RLHF, which aligns LLMs with the preference distribution of the reward model. The approach includes a PM regularizer balancing response diversification and reward maximization. Empirical validation shows a significant improvement in alignment with human preferences compared to standard RLHF.
   - **Year**: 2024

6. **Title**: Counteracting Duration Bias in Video Recommendation via Counterfactual Watch Time (arXiv:2406.07932)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study addresses duration bias in video recommendation systems, where longer videos may be favored due to their potential for higher watch time. The authors propose a method to counteract this bias by estimating counterfactual watch time, which reflects user interest independent of video duration. By incorporating this metric, the recommendation system can provide more balanced and fair content suggestions, enhancing user satisfaction and diversity in recommendations.
   - **Year**: 2024

7. **Title**: Using Human Feedback to Fine-tune Diffusion Models (arXiv:2311.13231)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper explores the integration of human feedback into the fine-tuning process of diffusion models. The authors present a method that leverages human preferences to guide the generation process, improving the alignment of model outputs with desired outcomes. The approach involves collecting human feedback on generated samples and using this information to adjust the model, resulting in enhanced performance and user satisfaction.
   - **Year**: 2023

8. **Title**: RLAIF: Scaling Reinforcement Learning from Human Feedback (arXiv:2309.00267)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: RLAIF addresses the challenges of scaling reinforcement learning from human feedback (RLHF) in large language models. The authors review the RLHF pipeline, including supervised fine-tuning, reward model training, and reinforcement learning. They identify position bias in LLM labelers and propose methods to mitigate this bias, enhancing the scalability and effectiveness of RLHF in aligning models with human preferences.
   - **Year**: 2023

9. **Title**: Counteracting Duration Bias in Video Recommendation via Counterfactual Watch Time (arXiv:2406.07932)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study addresses duration bias in video recommendation systems, where longer videos may be favored due to their potential for higher watch time. The authors propose a method to counteract this bias by estimating counterfactual watch time, which reflects user interest independent of video duration. By incorporating this metric, the recommendation system can provide more balanced and fair content suggestions, enhancing user satisfaction and diversity in recommendations.
   - **Year**: 2024

10. **Title**: Using Human Feedback to Fine-tune Diffusion Models (arXiv:2311.13231)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper explores the integration of human feedback into the fine-tuning process of diffusion models. The authors present a method that leverages human preferences to guide the generation process, improving the alignment of model outputs with desired outcomes. The approach involves collecting human feedback on generated samples and using this information to adjust the model, resulting in enhanced performance and user satisfaction.
    - **Year**: 2023

**Key Challenges:**

1. **Distinguishing Genuine Preference Evolution from Algorithm-Induced Drift**: Separating natural changes in user preferences from those influenced by algorithmic interventions remains complex, requiring sophisticated causal models and counterfactual analyses.

2. **Modeling Preference Dynamics Under Partial Observability**: Capturing the evolution of user preferences with limited or biased data poses significant challenges, necessitating advanced techniques in causal inference and representation learning.

3. **Mitigating Bias Accumulation in Feedback Loops**: Addressing the amplification of biases through iterative interactions between users and algorithms is critical to prevent unintended consequences and ensure fair outcomes.

4. **Ensuring Interpretability and Transparency**: Developing models that provide clear insights into how preferences are influenced and how decisions are made is essential for user trust and ethical considerations.

5. **Balancing Personalization with Preference Authenticity**: Designing systems that cater to individual user preferences while preserving the authenticity of those preferences without manipulation is a delicate and ongoing challenge. 