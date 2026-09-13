## Related Work

**Related Papers**
1. **Title**: Privacy-preserving federated learning for collaborative medical data mining ([Haripriya et al. 2025](https://www.semanticscholar.org/paper/8b908dad98440050849541548bfee26f48a40e40))
   - **Authors**: Haripriya et al.
   - **Summary**: Validates federated learning feasibility for medical domain and motivates adaptive aggregation strategies using FedAvg/FedSGD switching for collaborative medical data mining while preserving privacy.
   - **Year**: 2025

2. **Title**: Evaluating Fine-Tuning Strategies for Medical LLMs: Full-Parameter vs. PEFT (Med42) ([Christophe et al. 2024](https://www.semanticscholar.org/paper/2ddef4301dc9f9ef0f36e111e83cf8428716c562))
   - **Authors**: Christophe et al.
   - **Summary**: Proves that LoRA rank-16 parameter-efficient fine-tuning achieves 72% USMLE accuracy and establishes medical PEFT baseline, demonstrating that PEFT can match full fine-tuning performance in medical language models.
   - **Year**: 2024

3. **Title**: Federated Optimization in Heterogeneous Networks (FedProx) ([Li et al. 2020](Not specified))
   - **Authors**: Li et al.
   - **Summary**: Provides proximal term (μ) regularization for heterogeneous federated learning convergence, establishing theoretical foundation for handling non-IID data distributions across federated clients.
   - **Year**: 2020

4. **Title**: One Size Fits None: Rethinking Fairness in Medical AI ([Roller et al. 2025](https://www.semanticscholar.org/paper/f543ce81141972a1e0182afe4f8590e1dac7902f))
   - **Authors**: Roller et al.
   - **Summary**: Demonstrates subgroup performance disparities in medical AI systems and justifies the need for subgroup-specific model adaptations to achieve equitable performance across demographic groups.
   - **Year**: 2025

5. **Title**: Optimizing Parameter Efficient Fine Tuning for Fairness in Medical Image Analysis (FairTune) ([Dutt et al. 2023](https://www.semanticscholar.org/paper/394e1bb117311a69dcaa7bacf3ffeb9fc76b9f1e))
   - **Authors**: Dutt et al.
   - **Summary**: Provides fairness mechanism through bi-level optimization and equalized odds constraint for parameter-efficient fine-tuning in centralized medical imaging, achieving <5% fairness gap across demographic subgroups.
   - **Year**: 2023

6. **Title**: The Algorithmic Foundations of Differential Privacy ([Dwork & Roth 2014](Not specified))
   - **Authors**: Dwork & Roth
   - **Summary**: Foundational work on differential privacy composition theory, establishing how privacy budgets can be allocated across multiple mechanisms while maintaining overall privacy guarantees.
   - **Year**: 2014

7. **Title**: HuggingFace PEFT ([github.com/huggingface/peft](https://github.com/huggingface/peft))
   - **Authors**: HuggingFace Team
   - **Summary**: Open-source library implementing LoRA and other parameter-efficient fine-tuning methods, serving as the primary codebase for adapter training implementations.
   - **Year**: Not specified

8. **Title**: Flower Federated Learning Framework ([github.com/adap/flower](https://github.com/adap/flower))
   - **Authors**: Not specified
   - **Summary**: Federated learning coordination framework that handles multi-client aggregation and provides infrastructure for distributed machine learning across heterogeneous clients.
   - **Year**: Not specified

9. **Title**: Opacus Differential Privacy ([github.com/pytorch/opacus](https://github.com/pytorch/opacus))
   - **Authors**: PyTorch Team
   - **Summary**: PyTorch differential privacy library that applies Gaussian mechanism to gradients during training, enabling privacy-preserving machine learning with formal DP guarantees.
   - **Year**: Not specified

**Key Challenges**
1. **Privacy-Fairness Trade-off**: Achieving fairness requires access to sensitive demographic information, while maintaining privacy forbids centralized sharing of such labels. This fundamental tension has not been addressed in prior federated learning frameworks for medical AI.

2. **Parameter Efficiency in Federated Learning**: Prior federated learning work (Haripriya et al. 2025) uses full model fine-tuning which requires 150MB communication per round, making it impractical for multi-hospital deployments with limited bandwidth.

3. **Fairness Guarantees in Federated Settings**: Existing fairness methods (FairTune) operate in centralized settings and do not address the challenges of achieving demographic parity when data is distributed across hospitals with heterogeneous subgroup distributions.

4. **Convergence in Multi-Adapter Federated Learning**: Standard FedProx provides convergence guarantees for single model aggregation, but aggregating K separate adapter sets (one per demographic subgroup) introduces new theoretical challenges not addressed in prior work.

5. **Differential Privacy Budget Allocation**: No prior work addresses how to optimally allocate privacy budget between demographic routing information (ε_local) and model gradient updates (ε_adapters) in fairness-aware federated learning.

6. **Clinical Acceptability of Fairness-Accuracy Trade-offs**: Determining what level of accuracy degradation is acceptable in exchange for improved fairness requires clinical stakeholder input, which has not been systematically addressed in medical AI fairness literature.

7. **Subgroup Routing Under Privacy Constraints**: Existing federated learning systems do not address how to perform privacy-preserving patient-to-subgroup routing when demographic labels must remain local to each hospital.

8. **Unified Framework Gap**: No existing work simultaneously addresses federated learning, parameter efficiency (PEFT), and explicit fairness guarantees for medical foundation models - prior approaches address these challenges in isolation.
