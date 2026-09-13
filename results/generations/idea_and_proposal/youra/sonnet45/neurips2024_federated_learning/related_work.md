## Related Work

**Related Papers**

1. **Title**: Advances and Open Challenges in Federated Foundation Models (Ren et al., 2024)
   - **Authors**: Ren et al.
   - **Summary**: Comprehensive survey identifying multi-agent FM systems as critical open challenge, with no existing frameworks for inter-FM communication protocols, consensus mechanisms, or resource allocation across heterogeneous FMs.
   - **Year**: 2024

2. **Title**: Synergizing Foundation Models and Federated Learning: A Survey (Li et al., 2024)
   - **Authors**: Li et al.
   - **Summary**: Discusses FM-FL synergy and maintains updated paper collection at https://github.com/lishenghui/awesome-fm-fl, focusing on single global FM training rather than multi-agent collaboration.
   - **Year**: 2024

3. **Title**: FedPIA - Permuting and Integrating Adapters Leveraging Wasserstein Barycenters (Saha et al., 2025)
   - **Authors**: Saha et al.
   - **Summary**: Proposes Wasserstein barycenter aggregation for multi-modal FL adapters using optimal transport for heterogeneous adapter fusion, outperforming naive FL+PEFT on 48 medical datasets.
   - **Year**: 2025

4. **Title**: Communication-Efficient Learning of Deep Networks from Decentralized Data (McMahan et al., 2017)
   - **Authors**: McMahan et al.
   - **Summary**: Foundational work introducing FedAvg algorithm with uniform aggregation (w_i = 1/N) for federated learning.
   - **Year**: 2017

5. **Title**: Federated Optimization in Heterogeneous Networks (Li et al., 2020)
   - **Authors**: Li et al.
   - **Summary**: Introduces FedProx with proximal term (µ penalty) to handle client drift, achieving +3-5% improvement over FedAvg on Non-IID data.
   - **Year**: 2020

6. **Title**: A Survey on Parameter-Efficient Fine-Tuning for Foundation Models in FL (Bian et al., 2025)
   - **Authors**: Bian et al.
   - **Summary**: Comprehensive PEFT taxonomy covering Additive (LoRA, prompts), Selective (BitFit), and Reparameterized (Adapters) methods, reducing communication to 0.01%-2% of parameters.
   - **Year**: 2025

7. **Title**: FedPrompt: Communication-Efficient and Privacy-Preserving Prompt Tuning in Federated Learning (Zhao et al., 2022)
   - **Authors**: Zhao et al.
   - **Summary**: Achieves 0.01% parameter communication via prompt-only aggregation, demonstrating extreme communication efficiency while maintaining accuracy on IID and Non-IID data.
   - **Year**: 2022

8. **Title**: PriFFT: Privacy-preserving Federated Fine-tuning via Function Secret Sharing (You et al., 2025)
   - **Authors**: You et al.
   - **Summary**: Proposes hybrid secret sharing (ASS+FSS) reducing execution time 62.5% and communication 70.7%, protecting both model parameters and user data.
   - **Year**: 2025

9. **Title**: Differential Privacy (Dwork et al., 2014)
   - **Authors**: Dwork et al.
   - **Summary**: Foundational differential privacy framework providing theoretical foundations for privacy-preserving mechanisms.
   - **Year**: 2014

10. **Title**: Deep Learning with Differential Privacy (Abadi et al., 2016)
   - **Authors**: Abadi et al.
   - **Summary**: Introduces DP-SGD with Gaussian noise and composition theorems for privacy-preserving deep learning.
   - **Year**: 2016

11. **Title**: Byzantine-Robust Distributed Learning (Blanchard et al., 2017)
   - **Authors**: Blanchard et al.
   - **Summary**: Proposes geometric median aggregation that tolerates up to 50% Byzantine workers with provable robustness guarantees.
   - **Year**: 2017

12. **Title**: Federated Learning for Generalization, Robustness, Fairness (Huang et al., 2023)
   - **Authors**: Huang et al.
   - **Summary**: Comprehensive survey on robustness metrics and adversarial defenses in federated learning, covering Byzantine-robust techniques and agreement-based robustness metrics.
   - **Year**: 2023

13. **Title**: Federated Transfer Learning for Domain Adaptation (Zhang et al., 2025)
   - **Authors**: Zhang et al.
   - **Summary**: Presents cross-domain knowledge transfer with prior alignment and feature adaptation for heterogeneous FL across domains, applied to remaining useful life prediction.
   - **Year**: 2025

14. **Title**: RFL-HA: Resource-Efficient FL with Hierarchical Aggregation (Wang et al., 2021)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates cluster + global aggregation reducing completion time 34.8%-70% and communication savings 33.8%-56.5%.
   - **Year**: 2021

15. **Title**: On Calibration of Modern Neural Networks (Guo et al., 2017)
   - **Authors**: Guo et al.
   - **Summary**: Introduces temperature scaling for post-hoc calibration, reducing overconfidence and improving calibration error by 50%+ on ImageNet.
   - **Year**: 2017

16. **Title**: Humans Integrate Visual and Haptic Information Optimally (Ernst & Banks, 2002)
   - **Authors**: Ernst & Banks
   - **Summary**: Demonstrates optimal multi-sensory integration via reliability-weighted fusion in human perception, showing the brain upweights more reliable sensory signals matching maximum-likelihood estimation.
   - **Year**: 2002

17. **Title**: Multisensory Integration: Current Issues from Single Neuron Perspective (Stein & Stanford, 2008)
   - **Authors**: Stein & Stanford
   - **Summary**: Describes neural mechanisms of cross-modal integration in superior colliculus, establishing neurobiological foundation for attention-based gating of sensory inputs.
   - **Year**: 2008

18. **Title**: NetCal
   - **Authors**: Not specified
   - **Summary**: Provides mature implementations for neural network calibration with empirical validation.
   - **Year**: Not specified

19. **Title**: Client Selection for Federated Learning (Nishio & Yonetani, 2019)
   - **Authors**: Nishio & Yonetani
   - **Summary**: Shows selective participation methods reduce communication in federated learning.
   - **Year**: 2019

20. **Title**: Ensemble Methods in Machine Learning (Dietterich, 2000)
   - **Authors**: Dietterich
   - **Summary**: Demonstrates that low-agreement predictions in ensemble methods correlate with errors.
   - **Year**: 2000

21. **Title**: Advanced Composition Theorems for Differential Privacy (Kairouz et al., 2015)
   - **Authors**: Kairouz et al.
   - **Summary**: Provides theoretical framework for composing multiple differentially private mechanisms.
   - **Year**: 2015

22. **Title**: Membership Inference Attacks Against Machine Learning Models (Shokri et al., 2017)
   - **Authors**: Shokri et al.
   - **Summary**: Introduces membership inference attack methodology for empirical privacy validation using shadow models.
   - **Year**: 2017

**Key Challenges**

1. **Multi-Agent Foundation Model Coordination Gap**: No existing frameworks for inter-FM communication protocols, consensus mechanisms, or resource allocation across heterogeneous foundation models in federated settings.

2. **Privacy-Utility Trade-off in Attention Weighting**: Fine-grained attention weights require sharing information about FM outputs and performance, creating tension between maximizing accuracy gains and maintaining federated privacy principles.

3. **Heterogeneous FM Reliability**: Foundation models trained on different data distributions have varying performance across tasks, requiring reliability-weighted aggregation rather than uniform averaging.

4. **Byzantine Robustness in Multi-FM Settings**: Existing federated learning methods lack robust mechanisms to handle adversarial or malicious foundation models in multi-agent federations.

5. **Scalability of Weighted Aggregation**: Geometric median aggregation has O(n²) complexity, limiting scalability beyond 10-15 foundation models without specialized optimization.

6. **Calibration Quality for Confidence Signals**: Uncertainty quantification in foundation models requires effective calibration methods to provide reliable confidence scores for attention weighting.

7. **Cold Start Problem for New FMs**: Integrating new foundation models into existing federations requires strategies to handle the lack of historical performance data.

8. **Output Space Heterogeneity**: Multi-modal federations with different output formats (text, vision, audio) pose challenges for cross-FM agreement scoring and consensus mechanisms.

9. **Communication Efficiency with Privacy Constraints**: Secure aggregation protocols add computational overhead (10-20%) while attempting to reduce communication rounds.

10. **Generalization Beyond Medical Imaging**: Most weighted aggregation methods (like FedPIA) focus on single-domain applications without demonstrating cross-domain generalization.
