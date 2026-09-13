## Related Work

**Related Papers**
1. **Title**: Fisher-Informed Parameterwise Aggregation (FIPA) (arXiv:2601.13608v1)
   - **Authors**: Chang, He, Hao (Penn State)
   - **Summary**: Demonstrates that Fisher Information Matrix provides principled parameter-specific importance weights for aggregation in federated learning, establishing a theoretical foundation for adaptive weighting schemes.
   - **Year**: 2026

2. **Title**: FederatedScope-LLM: A Comprehensive Package for Fine-tuning LLMs in FL
   - **Authors**: Kuang et al.
   - **Summary**: Provides end-to-end federated learning benchmarking for large language models, demonstrating that PEFT implementations can achieve less than 1% parameter communication overhead.
   - **Year**: 2023

3. **Title**: Communication-Efficient Adaptive Federated Learning (FedCAMS)
   - **Authors**: Wang, Lin, Chen
   - **Summary**: Achieves O(1/√TKm) convergence with gradient compression and establishes a theoretical framework for adaptive federated learning with communication efficiency.
   - **Year**: 2022

4. **Title**: FedPIA: Permuting and Integrating Adapters
   - **Authors**: Saha et al.
   - **Summary**: Proposes a Wasserstein barycenter approach for adapter aggregation in federated learning, offering an alternative to simpler Fisher-based weighting methods.
   - **Year**: 2024

5. **Title**: RoLoRA: Robust Federated Finetuning of LLMs (arXiv:2502.01755)
   - **Authors**: Chen et al.
   - **Summary**: Introduces an alternating optimization approach for robust federated fine-tuning of large language models; accepted at NeurIPS 2025.
   - **Year**: 2025

6. **Title**: Convergence Analysis of Aggregation-Broadcast in LoRA-enabled Distributed Fine-Tuning (arXiv:2508.01348)
   - **Authors**: Chen et al.
   - **Summary**: Analyzes convergence properties of different aggregation strategies (SP vs PS) in LoRA-enabled distributed fine-tuning, highlighting that aggregation method selection critically impacts convergence behavior.
   - **Year**: 2025

7. **Title**: On the Convergence of LoRA-based Federated Learning (OpenReview)
   - **Authors**: Not specified
   - **Summary**: Proposes a unified ABO framework for LoRA-based federated learning, identifying the need for principled aggregation methods in current approaches.
   - **Year**: 2026

**Key Challenges**
1. **Lack of Principled Aggregation Methods**: Current federated learning approaches for LoRA fine-tuning lack theoretically grounded aggregation strategies, with existing methods often relying on heuristic weighting schemes.

2. **Aggregation Strategy Selection**: The choice between different aggregation approaches (e.g., SP vs PS aggregation) significantly impacts convergence behavior, yet this remains understudied and poorly understood.

3. **Need for Unified Framework**: Existing methods operate under disparate frameworks, highlighting the need for a unified approach (such as ABO) that can provide consistent theoretical guarantees for LoRA-based federated learning.

4. **Communication Efficiency vs. Model Quality Trade-off**: While PEFT methods reduce communication to less than 1% of parameters, balancing this efficiency with effective aggregation and model quality remains challenging.
