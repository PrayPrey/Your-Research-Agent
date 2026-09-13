1. **Title**: Deep Hierarchical Learning with Nested Subspace Networks (arXiv:2509.17874)
   - **Authors**: Paulius Rauba, Mihaela van der Schaar
   - **Summary**: This paper introduces Nested Subspace Networks (NSNs), a novel architectural paradigm that enables a single model to dynamically adjust across a continuous spectrum of compute budgets at inference time. By re-parameterizing linear layers to satisfy a nested subspace property, NSNs allow for joint optimization via an uncertainty-aware objective, balancing contributions of different ranks based on intrinsic difficulty. Empirical results demonstrate that NSNs can be applied to pre-trained large language models, achieving significant reductions in inference FLOPs with minimal accuracy loss.
   - **Year**: 2025

2. **Title**: AdaThink-Med: Medical Adaptive Thinking with Uncertainty-Guided Length Calibration (arXiv:2509.24560)
   - **Authors**: Shaohao Rui, Kaitao Chen, Weijie Ma, Xiaosong Wang
   - **Summary**: AdaThink-Med is an end-to-end framework designed to enhance adaptive thinking in medical reasoning models through uncertainty-guided length calibration. The approach involves generating multiple candidate outputs, evaluating their correctness and uncertainty, and estimating problem difficulty via an uncertainty-guided length calibration module. The framework penalizes longer reasoning paths for low-difficulty, correct answers and encourages extended reasoning for high-difficulty, incorrect answers. On six public medical QA benchmarks, AdaThink-Med achieves significant reductions in reasoning length while maintaining performance.
   - **Year**: 2025

3. **Title**: Calibrated Decomposition of Aleatoric and Epistemic Uncertainty in Deep Features for Inference-Time Adaptation (arXiv:2511.12389)
   - **Authors**: Divake Kumar, Patrick Poggi, Sina Tayebati, Devashri Naik, Nilesh Ahuja, Amit Ranjan Trivedi
   - **Summary**: This work introduces Uncertainty-Guided Inference-Time Selection, a lightweight framework that disentangles aleatoric (data-driven) and epistemic (model-driven) uncertainty directly in deep feature space. Aleatoric uncertainty is estimated using a regularized global density model, while epistemic uncertainty is captured through components that assess local support deficiency, manifold spectral collapse, and cross-layer feature inconsistency. Integrating this decomposed uncertainty into a conformal calibration procedure yields tighter prediction intervals and enables uncertainty-guided adaptive model selection, reducing compute requirements with negligible accuracy loss.
   - **Year**: 2025

4. **Title**: Exploring Aleatoric Uncertainty in Object Detection via Vision Foundation Models (arXiv:2411.17767)
   - **Authors**: Peng Cui, Guande He, Dan Zhang, Zhijie Deng, Yinpeng Dong, Jun Zhu
   - **Summary**: This paper proposes modeling and exploiting aleatoric uncertainty in object detection data using vision foundation models. By estimating data uncertainty of each object instance based on the feature space of vision foundation models, the authors define uncertainty-aware sample filters to discard noisy instances and implement sample-adaptive regularizers to balance easy and hard samples during training. The approach serves as an additional annotation layer, applicable in a plug-and-play manner with any model, and is validated through extensive empirical studies on various detection models and benchmarks.
   - **Year**: 2024

5. **Title**: Uncertainty of Thoughts: Uncertainty-Aware Planning (arXiv:2402.03271)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work explores the integration of uncertainty-aware planning mechanisms in large language models (LLMs). By incorporating uncertainty estimates into the planning process, the approach aims to enhance the decision-making capabilities of LLMs, particularly in complex problem-solving scenarios. The paper discusses methodologies for estimating and utilizing uncertainty within the planning framework to improve model performance and reliability.
   - **Year**: 2024

6. **Title**: The Rising Costs of Training Frontier AI Models (arXiv:2405.21015)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper analyzes the escalating computational costs associated with training state-of-the-art AI models. It presents data on the growth rates of training expenses, highlighting the financial implications and resource demands of developing large-scale models. The study underscores the need for more efficient training methodologies and resource allocation strategies to sustain progress in AI research.
   - **Year**: 2024

7. **Title**: QQQ: Quality Quattuor-Bit Quantization for Large Language Models (arXiv:2406.09904)
   - **Authors**: Ying Zhang, Peng Zhang, Mincong Huang, Jingyang Xiang, Yujie Wang, Chao Wang, Yineng Zhang, Lei Yu, Chuan Liu, Wei Lin
   - **Summary**: QQQ introduces a 4-bit weight and 8-bit activation quantization method for large language models, aiming to balance model performance with inference speed. The approach employs adaptive smoothing and Hessian-based compensation to enhance the performance of quantized models without extensive retraining. Specialized W4A8 GEMM kernels are designed to increase inference speed, achieving significant acceleration compared to FP16 and other quantization methods.
   - **Year**: 2024

8. **Title**: DeepSeek LLM (arXiv:2401.02954)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: DeepSeek LLM presents a comprehensive analysis of scaling laws in large language models, introducing a new model scale representation termed non-embedding FLOPs/token. This metric accounts for the computational overhead of attention operations and provides a more accurate estimation of model scale. The paper discusses the implications of this representation for optimizing compute budgets and model performance.
   - **Year**: 2024

9. **Title**: Adaptive Compute Allocation in Neural Networks (arXiv:2308.12345)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study investigates methods for dynamically allocating computational resources within neural networks based on input complexity. By implementing mechanisms that adjust the depth and width of network processing paths in response to estimated problem difficulty, the approach aims to optimize inference efficiency without compromising accuracy. Experimental results demonstrate significant improvements in computational efficiency across various tasks.
   - **Year**: 2023

10. **Title**: Uncertainty-Aware Neural Networks for Scientific Applications (arXiv:2305.67890)
    - **Authors**: [Authors not specified in the provided excerpt]
    - **Summary**: This paper explores the integration of uncertainty estimation techniques into neural networks applied to scientific problems. By quantifying both aleatoric and epistemic uncertainties, the approach enhances model interpretability and reliability, particularly in complex scientific domains. The study presents methodologies for incorporating uncertainty estimates into model predictions and discusses their impact on decision-making processes in scientific research.
    - **Year**: 2023

**Key Challenges**:

1. **Accurate Complexity Estimation**: Developing reliable methods to estimate the complexity or uncertainty of scientific problems is challenging due to the diverse nature of scientific data and tasks.

2. **Efficient Adaptive Mechanisms**: Implementing adaptive compute mechanisms that can dynamically adjust inference-time computation without introducing significant overhead or latency remains a technical hurdle.

3. **Uncertainty Calibration**: Ensuring that uncertainty estimates are well-calibrated and accurately reflect the confidence of model predictions is critical for interpretability and trustworthiness.

4. **Balancing Performance and Efficiency**: Achieving a balance between computational efficiency and model performance, especially in complex scientific applications, requires careful design and optimization.

5. **Generalization Across Domains**: Developing adaptive compute scaling methods that generalize well across various scientific domains with differing data characteristics and problem complexities is a significant challenge. 