## Related Work

**Related Papers**

1. **Title**: Communication-Efficient Learning of Deep Networks from Decentralized Data
   - **Authors**: McMahan et al.
   - **Summary**: Introduced FedAvg algorithm where clients perform local SGD and server averages model updates. Achieved 10× communication reduction vs naive approach but assumes homogeneous clients and uses synchronous aggregation without compression.
   - **Year**: 2017

2. **Title**: Federated Optimization in Heterogeneous Networks (FedProx)
   - **Authors**: Li et al.
   - **Summary**: Addresses system heterogeneity through proximal term in local objective to handle variable compute and data. Improved convergence 20% faster than FedAvg on heterogeneous data but still synchronous with no compression.
   - **Year**: 2020

3. **Title**: Asynchronous Federated Optimization (FedAsync)
   - **Authors**: Xie et al.
   - **Summary**: Enables asynchronous aggregation allowing clients to update global model independently with staleness weighting. Converges 2-3× faster wall-clock time by eliminating synchronization barrier but lacks compression and uses random client selection.
   - **Year**: 2019

4. **Title**: Federated Learning with Non-IID Data
   - **Authors**: Zhao et al.
   - **Summary**: Analyzed FedAvg degradation on non-IID data (11% accuracy drop on CIFAR-10 with extreme non-IID). Proposed data sharing strategy which violates privacy assumptions.
   - **Year**: 2018

5. **Title**: Ditto: Fair and Robust Federated Learning Through Personalization
   - **Authors**: Li et al.
   - **Summary**: Personalized FL where each client maintains local and global models. Improves fairness by reducing accuracy variance 40% across clients but requires 2× model storage and communication.
   - **Year**: 2021

6. **Title**: QSGD: Communication-Efficient SGD via Gradient Quantization
   - **Authors**: Alistarh et al.
   - **Summary**: Stochastic quantization with unbiased encoding to quantize gradients to 1-8 bits. Achieved 32× compression with <1% accuracy loss on ResNet-50 but designed for centralized parameter server setting, not federated.
   - **Year**: 2017

7. **Title**: FedPAQ: A Communication-Efficient Federated Learning Method with Periodic Averaging and Quantization
   - **Authors**: Reisizadeh et al.
   - **Summary**: Combines gradient quantization with periodic averaging for 10× communication reduction with <2% accuracy drop. Uses fixed quantization for all clients and remains synchronous with no active learning.
   - **Year**: 2020

8. **Title**: Characterizing Deep Learning Model Compression with Post-Training Quantization
   - **Authors**: Rachmanto et al.
   - **Summary**: Empirical study of post-training quantization on edge devices showing 4-bit PTQ achieves 2-5% accuracy drop and 2-bit PTQ shows 8-12% drop. Validates INT quantization feasibility for embedded devices.
   - **Year**: 2024

9. **Title**: Federated Active Learning (FEAL)
   - **Authors**: Shin et al.
   - **Summary**: Active learning for client selection in FL based on uncertainty of model predictions. Achieves 90% accuracy with 50% less labeled data but uses uncertainty only without diversity consideration.
   - **Year**: 2020

10. **Title**: Asynchronous Federated Active Learning (AFL)
    - **Authors**: Zhang et al.
    - **Summary**: Combines asynchronous FL with active learning for 40% faster convergence with 45% data reduction. Uses random diversity sampling rather than principled scoring and no compression.
    - **Year**: 2021

11. **Title**: LLMs in the Loop: Active Learning in Low-Resource Languages
    - **Authors**: Kholodna et al.
    - **Summary**: Active learning for low-resource NLP using LLMs for pseudo-labels with diversity sampling. Achieved 42× cost reduction in annotation but is NLP-specific and centralized, not federated.
    - **Year**: 2024

12. **Title**: A policy framework on AI usage in developing countries
    - **Authors**: Folorunso et al.
    - **Summary**: Identifies infrastructure barriers to AI adoption in developing countries including unreliable power, intermittent connectivity, and limited compute. Proposes policy recommendations but provides no technical solution.
    - **Year**: 2024

13. **Title**: Federated Learning in IoT: A Survey from a Resource-Constrained Perspective
    - **Authors**: Kaur & Jadhav
    - **Summary**: Comprehensive survey of FL techniques for IoT devices covering compression, asynchronous aggregation, and energy efficiency. Identified gap that no unified framework addresses data, compute, AND communication constraints simultaneously.
    - **Year**: 2023

14. **Title**: Adaptive Machine Learning for Resource-Constrained Environments
    - **Authors**: Ordóñez et al.
    - **Summary**: Adaptive ML on IoT devices that dynamically selects model architecture based on available compute budget. Achieved 40% energy reduction but is single-device, not federated.
    - **Year**: 2025

**Key Challenges**

1. **Synchronous FL bottleneck**: Slow clients delay entire training round in synchronous approaches like FedAvg and FedProx, limiting scalability in heterogeneous environments.

2. **Fixed compression limitations**: Existing quantization methods (FedPAQ, QSGD) apply uniform bit-width across all clients, failing to adapt to infrastructure heterogeneity.

3. **Data inefficiency in FL**: Random client selection ignores data distribution diversity, leading to 100% data requirement even when active learning could reduce this significantly.

4. **Non-IID degradation**: Federated learning accuracy drops 11% on extreme non-IID data, and existing mitigation strategies (data sharing) violate privacy assumptions.

5. **Staleness-quantization interaction**: No existing work analyzes how staleness and quantization errors compound in asynchronous FL with compressed gradients.

6. **Multi-constraint gap**: No unified framework co-optimizes data scarcity, compute limits, and connectivity constraints simultaneously—existing work optimizes one dimension at expense of others.

7. **Infrastructure assumptions**: Existing ML frameworks assume reliable infrastructure, treating connectivity loss and power outages as exceptions rather than design constraints, limiting applicability to developing countries.

8. **Uncertainty-only active learning**: Approaches like FEAL use uncertainty scoring only, failing on extreme non-IID scenarios where diversity is critical.

9. **Quantization drift**: Long-term quantization introduces accumulated rounding errors that cause model drift, not addressed in prior FL quantization work.

10. **Theoretical gaps in heterogeneous FL**: Existing convergence analysis assumes homogeneous clients (same update rule, synchronous); no analysis for discrete heterogeneous tiers with mixed synchronous/asynchronous and mixed quantization levels.
