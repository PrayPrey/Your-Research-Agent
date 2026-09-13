1. **Title**: Fast and High-Performance Learned Image Compression With Improved Checkerboard Context Model, Deformable Residual Module, and Knowledge Distillation (arXiv:2309.02529)
   - **Authors**: Haisheng Fu, Feng Liang, Jie Liang, Yongqiang Wang, Guohe Zhang, Jingning Han
   - **Summary**: This paper introduces a learned image compression framework that balances performance and computational efficiency. Key innovations include a deformable convolutional module to enhance compression, a checkerboard context model for parallel decoding, and a three-step knowledge distillation training scheme. The proposed method achieves significant speed improvements in encoding and decoding while maintaining superior rate-distortion performance.
   - **Year**: 2023

2. **Title**: FEDS: Feature and Entropy-Based Distillation Strategy for Efficient Learned Image Compression (arXiv:2503.06399)
   - **Authors**: Haisheng Fu, Jie Liang, Zhenman Fang, Jingning Han
   - **Summary**: The authors propose FEDS, a distillation strategy that transfers knowledge from a high-capacity teacher model to a lightweight student model in learned image compression. By aligning intermediate feature representations and emphasizing informative latent channels through an entropy-based loss, the student model achieves near-teacher performance with reduced parameters and faster encoding/decoding, making it suitable for real-time applications.
   - **Year**: 2025

3. **Title**: Extreme Compression of Large Language Models via Additive Quantization (arXiv:2401.06118)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This work presents a method for extreme compression of large language models using additive quantization. The approach involves block-wise fine-tuning and knowledge distillation to minimize the loss between the quantized and original models. The method achieves significant compression ratios while maintaining performance, facilitating efficient deployment of large models.
   - **Year**: 2024

4. **Title**: Adaptive Estimators Show Information Compression in Deep Neural Networks (arXiv:1902.09037)
   - **Authors**: Ivan Chelombiev, Conor Houghton, Cian O'Donnell
   - **Summary**: The paper develops robust mutual information estimation techniques to explore information compression in neural networks with various activation functions. Findings indicate that compression is not solely dependent on activation function saturation and that L2 regularization enhances compression, correlating with improved generalization.
   - **Year**: 2019

5. **Title**: Compressing Neural Networks using the Variational Information Bottleneck (arXiv:1802.10399)
   - **Authors**: Bin Dai, Chen Zhu, David Wipf
   - **Summary**: This study applies the information bottleneck principle to neural network compression by minimizing a variational bound. The approach reduces redundancy between layers, leading to state-of-the-art compression rates across various datasets and architectures.
   - **Year**: 2018

6. **Title**: Pre-processing and Compression: Understanding Hidden Representation Refinement Across Imaging Domains via Intrinsic Dimension (arXiv:2408.08381)
   - **Authors**: Nicholas Konz, Maciej A. Mazurowski
   - **Summary**: The authors investigate how the intrinsic dimension of neural network representations evolves across layers in different imaging domains. They find that medical image models peak in representation intrinsic dimension earlier than natural image models, suggesting differences in feature abstraction and information content between domains.
   - **Year**: 2024

7. **Title**: Post-Training Quantization for Cross-Platform (arXiv:2202.07513)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This paper discusses post-training quantization techniques for neural networks, focusing on cross-platform deployment. It addresses challenges in maintaining model performance across different hardware platforms and proposes solutions to ensure consistency and efficiency.
   - **Year**: 2022

8. **Title**: Neural Compression: From Information Theory to Applications
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This workshop overview highlights the intersection of machine learning, data/model compression, and information theory. It emphasizes the need for improved compression techniques and efficient AI systems, discussing topics like learned data compression, large model acceleration, theoretical limits, and information-theoretic principles in learning and generalization.
   - **Year**: [Year not specified in the provided excerpt]

**Key Challenges:**

1. **Balancing Compression and Performance**: Achieving high compression ratios without significant degradation in model accuracy remains a primary challenge.

2. **Efficient Training and Inference**: Developing methods that reduce computational complexity during both training and inference while maintaining performance is crucial for practical deployment.

3. **Generalization Across Domains**: Ensuring that compression techniques generalize well across different data domains, such as natural and medical images, is essential for broad applicability.

4. **Robustness to Hardware Variability**: Maintaining model performance across various hardware platforms, especially when employing quantization and other compression methods, poses significant challenges.

5. **Theoretical Understanding**: Developing a deeper theoretical understanding of the trade-offs between compression, information retention, and model performance is necessary to guide future research and applications. 