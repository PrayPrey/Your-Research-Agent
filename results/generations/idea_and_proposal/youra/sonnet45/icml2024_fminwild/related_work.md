## Related Work

**Related Papers**

1. **Title**: LoRA - Low-Rank Adaptation of Large Language Models
   - **Authors**: Hu et al.
   - **Summary**: Introduces low-rank adapter matrices for parameter-efficient fine-tuning, reducing trainable parameters from billions to millions while maintaining 95-100% of full fine-tuning performance.
   - **Year**: 2021

2. **Title**: Visual Foundation Models Boost Cross-Modal Unsupervised Domain Adaptation (Semantic Scholar ID: 5209d1899833017170f32fa6b55774e04aed9b64)
   - **Authors**: Xu et al.
   - **Summary**: VFMSeg framework leveraging visual foundation model knowledge priors for accurate target domain labels in 3D semantic segmentation.
   - **Year**: 2025

3. **Title**: Improving Clinical Foundation Models with Multi-modal Learning and Domain Adaptation (Semantic Scholar ID: 96dbda920b0da577f4719117de0a2cc43700a1d8)
   - **Authors**: Hou et al.
   - **Summary**: MsHeCare framework combining multi-modal learning and multi-source domain adaptation for clinical chronic disease prediction.
   - **Year**: 2025

4. **Title**: Privacy Preserving Machine Learning with Homomorphic Encryption and Federated Learning (Semantic Scholar ID: 22170e4b89c2748bddb81ffccda1f2bcdfd8ebe6)
   - **Authors**: Fang & Qian
   - **Summary**: PFMLP framework combining homomorphic encryption with federated learning for multi-party privacy-preserving ML.
   - **Year**: 2021

5. **Title**: FedProx - Federated Optimization in Heterogeneous Networks
   - **Authors**: Li et al.
   - **Summary**: Proximal term regularization for federated learning under data heterogeneity (non-IID), proving convergence acceleration.
   - **Year**: 2020

6. **Title**: Deep Learning with Differential Privacy
   - **Authors**: Abadi et al.
   - **Summary**: DP-SGD algorithm providing (ε,δ)-differential privacy for deep learning via gradient clipping and noise addition.
   - **Year**: 2016

7. **Title**: Revisiting OOD Robustness in NLP: Benchmark, Analysis, and LLMs Evaluations (Semantic Scholar ID: 1a55d16c14587edda62dc9c9ff09e0b531dd169c)
   - **Authors**: Yuan et al.
   - **Summary**: BOSS benchmark suite for OOD robustness evaluation covering 5 tasks and 20 datasets.
   - **Year**: 2023

8. **Title**: Distilling OOD Robustness from Vision-Language Foundation Models (Semantic Scholar ID: f71ee484b9182cfe00ed260ae0c70014cabf9f59)
   - **Authors**: Zhou et al.
   - **Summary**: Discrete Adversarial Distillation (DAD) leveraging robust teacher models for OOD robustness.
   - **Year**: 2023

9. **Title**: MMDT - Decoding Trustworthiness and Safety of Multimodal Foundation Models (Semantic Scholar ID: 26c02dbc2f6db3e3b7acdb493a880a3456ff2cfd)
   - **Authors**: Xu et al.
   - **Summary**: First comprehensive safety/trustworthiness evaluation platform for multimodal FMs (hallucination, fairness, privacy, adversarial robustness, OOD generalization).
   - **Year**: 2025

10. **Title**: Mapping the Individual, Social and Biospheric Impacts of Foundation Models (Semantic Scholar ID: 0dfe5aa18508597b3e1de049326b2c5534e19a20)
    - **Authors**: Domínguez Hernández et al.
    - **Summary**: Critical framework mapping 14 categories of FM risks/harms to individual, social, and biospheric impacts.
    - **Year**: 2024

11. **Title**: LLM-NPU - Towards Efficient Foundation Model Inference on Low-Power NPUs (Semantic Scholar ID: f640d0de12e198aa724b9c39c6e7d8a1a2f17134)
    - **Authors**: Raha et al.
    - **Summary**: Software-hardware co-optimization for efficient LLM deployment on NPUs (fusion, quantization, PIM architectures).
    - **Year**: 2025

12. **Title**: Software Performance Engineering for Foundation Model-Powered Software (Semantic Scholar ID: b0d17cb116576239a868718af1c6a59c4f1e9ebd)
    - **Authors**: Zhang et al.
    - **Summary**: SPE framework for production-ready FMware systems (architecture design, communication, tuning, deployment).
    - **Year**: 2024

13. **Title**: PyTorch Adapt (KevinMusgrave/pytorch-adapt)
    - **Authors**: Not specified
    - **Summary**: Domain adaptation algorithms (ADDA, DANN, CDAN) with modular PyTorch implementation. GitHub repository with 391 stars.
    - **Year**: Not specified

14. **Title**: APPFL - Advanced Privacy-Preserving Federated Learning (APPFL/APPFL)
    - **Authors**: Not specified
    - **Summary**: Federated learning framework with privacy preservation focus. GitHub repository with 163 stars.
    - **Year**: Not specified

15. **Title**: Opacus - Privacy-Preserving PyTorch (pytorch/opacus)
    - **Authors**: Not specified
    - **Summary**: Differential privacy for PyTorch (DP-SGD implementation with privacy accounting). Official PyTorch library.
    - **Year**: Not specified

**Key Challenges**

1. **Foundation Model Centralized Data Assumption**: Existing foundation model adaptation methods (LoRA, VFMSeg, MsHeCare) assume centralized data access, making them unsuitable for privacy-constrained environments like healthcare (HIPAA) and finance (GDPR).

2. **Privacy-Utility Tradeoff**: Differential privacy noise required for privacy guarantees causes performance degradation. Current work lacks characterization of this tradeoff specifically for foundation model adaptation in federated settings.

3. **Data Heterogeneity in Federated Learning**: Non-IID data across institutions causes convergence issues in federated learning. While FedProx addresses this for classical ML, extension to foundation model low-rank adaptation remains unexplored.

4. **Communication Efficiency at Scale**: Standard federated learning with full model updates becomes prohibitive for billion-parameter foundation models. Parameter-efficient methods like LoRA have not been validated in federated privacy-preserving settings.

5. **Privacy Attack Vulnerability**: Federated learning systems are vulnerable to gradient inversion and membership inference attacks. Existing privacy-preserving ML frameworks (PFMLP, APPFL) are limited to classical ML scale and lack foundation model support.

6. **Adapter Aggregation Under Heterogeneity**: Low-rank adapters trained on heterogeneous distributions may introduce aggregation bias. Theoretical analysis of adapter aggregation geometry under differential privacy noise is missing.

7. **Deployment in Regulated Industries**: No existing framework combines foundation model adaptation, federated learning, differential privacy, and secure aggregation at scale, blocking deployment in regulated industries (healthcare, finance) where data sharing is legally prohibited.

8. **Real-World Scalability Validation**: Existing federated learning frameworks documented as "limited to classical ML models" (APPFL), requiring custom implementation for foundation model scale with LoRA adapters.
