## Related Work

**Related Papers**
1. **Title**: Federated Fine-tuning of Large Language Models under Heterogeneous Tasks and Client Resources (FlexLoRA)
   - **Authors**: Jiamu Bai, Daoyuan Chen, Bingchen Qian, Liuyi Yao, Yaliang Li
   - **Summary**: Proposes SVD-based rank redistribution to enable heterogeneous client participation in federated learning, with dynamic rank adjustment that prevents the "bucket effect" in aggregation.
   - **Year**: 2024

2. **Title**: Differential Privacy for Deep and Federated Learning: A Survey
   - **Authors**: Ahmed El Ouadrhiri, Ahmed M Abdelhadi
   - **Summary**: Provides a comprehensive survey of differential privacy mechanisms and privacy-utility tradeoffs in deep and federated learning, including Gaussian mechanism calibration formulas.
   - **Year**: 2022

3. **Title**: Efficient and Near-Optimal Noise Generation for Streaming Differential Privacy
   - **Authors**: K. Dvijotham, H. B. McMahan, Krishna Pillutla, Thomas Steinke, Abhradeep Thakurta
   - **Summary**: Introduces matrix factorization techniques for correlated noise generation that achieves near-optimal utility in streaming differential privacy settings, with Toeplitz factorization applicable to LoRA structure.
   - **Year**: 2024

4. **Title**: DP-FedLoRA: Privacy-Enhanced Federated Fine-Tuning for On-Device Large Language Models (arXiv:2509.09097)
   - **Authors**: Honghui Xu et al.
   - **Summary**: Demonstrates that uniform differential privacy applied to LoRA matrices achieves competitive performance and establishes variance bounds for noise in federated fine-tuning.
   - **Year**: 2025

5. **Title**: FedASK: Differentially Private Federated Low Rank Adaptation Beyond Fixed-Matrix (arXiv:2507.09990)
   - **Authors**: Not specified
   - **Summary**: Proposes double sketching techniques to reduce noise amplification in differentially private federated low-rank adaptation, offering a complementary approach to rank-aware methods.
   - **Year**: 2025

6. **Title**: Unlocking the Potential of Prompt-Tuning in Bridging Generalized and Personalized FL (SGPT)
   - **Authors**: Wenlong Deng, Christos Thrampoulidis, Xiaoxiao Li
   - **Summary**: Explores shared versus group-specific prompts for personalization in federated learning, though privacy implications of parameter splitting remain unanalyzed.
   - **Year**: 2023

7. **Title**: FedPIA - Permuting and Integrating Adapters leveraging Wasserstein Barycenters
   - **Authors**: Pramit Saha, Divyanshu Mishra, Felix Wagner, et al.
   - **Summary**: Introduces a novel adapter aggregation method using Wasserstein barycenters for federated learning with adapters.
   - **Year**: 2024

**Key Challenges**
1. **Privacy Implications of Parameter Splitting**: Existing work on shared versus personalized parameters (e.g., SGPT) does not analyze the privacy implications of splitting parameters between shared and group-specific components.
2. **Privacy Accounting for Permutation-Based Aggregation**: Methods like FedPIA that use permutation and integration of adapters lack clear privacy accounting mechanisms for the permutation operations.
3. **Heterogeneous Client Resources**: Federated fine-tuning must accommodate clients with varying computational capabilities, requiring dynamic adaptation of model complexity (e.g., LoRA rank).
4. **Privacy-Utility Tradeoffs in LoRA**: Applying differential privacy to low-rank adaptation introduces noise amplification challenges that affect model utility, requiring specialized noise generation techniques.
