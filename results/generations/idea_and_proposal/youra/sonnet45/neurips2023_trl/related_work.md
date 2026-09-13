## Related Work

**Related Papers**

1. **Title**: SAINT: Improved Neural Networks for Tabular Data via Row Attention and Contrastive Pre-Training (Somepalli et al., NeurIPS 2021)
   - **Authors**: Somepalli et al.
   - **Summary**: Hybrid deep learning with row/column attention and contrastive self-supervised pre-training for label-scarce scenarios. Used as base TRL model in FedTRL.
   - **Year**: 2021
   - **Citations**: 424 (highly influential)
   - **Semantic Scholar ID**: 5fa2103e36b3e76e49edb8433a1206a6b25e3ead

2. **Title**: TabPFN: A Transformer That Solves Small Tabular Classification Problems in a Second (Hollmann et al., NeurIPS 2022)
   - **Authors**: Hollmann et al.
   - **Summary**: Meta-learning approach with single forward pass inference for new tasks. FedTRL extends TabPFN with LoRA for continual learning.
   - **Year**: 2022
   - **Citations**: 6

3. **Title**: Generative Table Pre-training Empowers Models for Tabular Prediction (Zhang et al., CVPR 2023)
   - **Authors**: Zhang et al.
   - **Summary**: First table pre-training via synthetic data generation; trained models compete with original dataset. Inspires Schema-Synth component in FedTRL.
   - **Year**: 2023
   - **Citations**: 58
   - **Semantic Scholar ID**: 4e1cac32403c6caff15aa8c2a3560031bb05c6d4

4. **Title**: Table Foundation Models: on knowledge pre-training for tabular learning (Kim et al., ICLR 2025)
   - **Authors**: Kim et al.
   - **Summary**: TARTE foundation model transforming tables to knowledge-enhanced representations. Demonstrates foundation model potential for TRL.
   - **Year**: 2025
   - **Citations**: 5
   - **Semantic Scholar ID**: c470777164b26e0a26e4a0cb37ad86d8bd305379

5. **Title**: Communication-Efficient Learning of Deep Networks from Decentralized Data (McMahan et al., AISTATS 2017)
   - **Authors**: McMahan et al.
   - **Summary**: Foundational federated averaging (FedAvg) algorithm; reduces communication via local updates. FedTRL uses FedAvg as aggregation algorithm with LoRA extension.
   - **Year**: 2017
   - **Citations**: 17,000+

6. **Title**: Federated Optimization in Heterogeneous Networks (Li et al., MLSys 2020)
   - **Authors**: Li et al.
   - **Summary**: FedProx algorithm with proximal term for non-IID data convergence. FedTRL adds column-level Hetero-DP for tabular heterogeneity.
   - **Year**: 2020
   - **Citations**: 4,000+

7. **Title**: Deep Learning with Differential Privacy (Abadi et al., CCS 2016)
   - **Authors**: Abadi et al.
   - **Summary**: DP-SGD algorithm with gradient clipping and Gaussian noise for ε-DP training. FedTRL extends to column-level heterogeneous DP.
   - **Year**: 2016
   - **Citations**: 5,000+

8. **Title**: The Algorithmic Foundations of Differential Privacy (Dwork et al., 2014)
   - **Authors**: Dwork et al.
   - **Summary**: Composition theorem for sequential DP queries. FedTRL uses advanced composition to track ε_total across federated rounds.
   - **Year**: 2014

9. **Title**: Heterogeneous Differential Privacy for Federated Learning (Ling et al., ICML 2024)
   - **Authors**: Ling et al.
   - **Summary**: Client-specific privacy budgets based on data sensitivity. FedTRL adapts client-level hetero-DP to column-level hetero-DP for tabular data.
   - **Year**: 2024
   - **Citations**: 35

10. **Title**: Online-LoRA: Task-Adaptive Parameter-Efficient Fine-Tuning (Wei et al., CVPR 2024)
    - **Authors**: Wei et al.
    - **Summary**: Dynamic low-rank adaptation for continual learning in vision. FedTRL adapts vision LoRA to tabular LoRA with column-wise matrices.
    - **Year**: 2024
    - **Citations**: 14

11. **Title**: FedCTTA: Federated Test-Time Adaptation (Rajib et al., ICLR 2025)
    - **Authors**: Rajib et al.
    - **Summary**: Test-time error correction in federated setting via entropy minimization. FedTRL adapts entropy minimization to schema drift detection and constraint validation.
    - **Year**: 2025
    - **Citations**: 2

12. **Title**: TableDP: Private Discrete Table Synthesis (Hod et al., 2025)
    - **Authors**: Hod et al.
    - **Summary**: LLM-based synthetic table generation with differential privacy. FedTRL integrates TableDP into Schema-Synth component for federated augmentation.
    - **Year**: 2025
    - **Citations**: 0 (very recent)

13. **Title**: IMLP: Energy-Efficient Continual Learning for Tabular Data Streams (Wang et al., 2025)
    - **Authors**: Wang et al.
    - **Summary**: Tabular continual learning differs from vision; uses attention over feature buffers. Confirms tabular-specific design is critical; FedTRL designs tabular-specific LoRA.
    - **Year**: 2025
    - **Citations**: 0

14. **Title**: PraVFed: Adaptive Privacy-Preserving Vertical Federated Learning (Li et al., 2024)
    - **Authors**: Li et al.
    - **Summary**: Dynamic privacy budget allocation for vertical federated learning (features split across sites). Orthogonal to FedTRL which uses horizontal FL (samples split).
    - **Year**: 2024

15. **Title**: pytorch_tabular - Deep Learning Framework for Tabular Data
    - **Authors**: Not specified
    - **Summary**: Standard framework for tabular deep learning with multiple architectures. FedTRL integrates with pytorch_tabular as base framework.
    - **Year**: Not specified
    - **Repository**: https://github.com/pytorch-tabular/pytorch_tabular (1,600 stars)

16. **Title**: vanna-ai - Text-to-SQL with Retrieval
    - **Authors**: Not specified
    - **Summary**: Agentic retrieval for SQL generation from natural language. FedTRL integrates with vanna-ai for privacy-preserving text-to-SQL.
    - **Year**: Not specified
    - **Repository**: https://github.com/vanna-ai/vanna

**Key Challenges**

1. **Centralized TRL Models Lack Privacy and Federation**: Existing tabular representation learning models (SAINT, TabPFN, TapTap, TARTE) are centralized and do not support federated learning or differential privacy, making them unsuitable for production deployment in privacy-sensitive domains like healthcare and finance.

2. **High Communication Cost in Federated Learning**: Traditional federated learning algorithms (FedAvg, FedProx) transmit full model parameters, which is inefficient for production deployment. LoRA-based parameter-efficient approaches can reduce communication cost by 10x.

3. **Uniform Privacy Noise Suboptimal for Heterogeneous Tabular Data**: Standard DP-SGD applies uniform noise across all features, which is suboptimal for tabular data with heterogeneous column types (numerical, categorical, temporal). Column-level heterogeneous DP can improve privacy-utility tradeoff.

4. **Domain Transfer from Vision to Tabular Requires Adaptation**: Cross-domain techniques from computer vision (Online-LoRA, FedCTTA) cannot be directly applied to tabular data without tabular-specific adaptations due to structural differences (heterogeneous columns vs homogeneous tensors, schema constraints vs spatial structure).

5. **Schema Consistency Across Federated Sites**: Production federated learning for tabular data requires handling schema variations across sites (column name variations, type mismatches, missing columns), which is not addressed by existing federated learning frameworks.

6. **Test-Time Error Correction for Production TRL**: Deployed tabular models encounter schema drift, constraint violations, and missing values in production inference, requiring test-time error correction mechanisms that preserve privacy guarantees.

7. **Few-Shot Learning in Federated Tabular Settings**: Federated sites may have limited labeled data, requiring synthetic data augmentation that preserves differential privacy guarantees while improving model utility.

8. **Missing Theoretical Foundations**: No existing work provides convergence theory for federated LoRA-based tabular representation learning under heterogeneous differential privacy, leaving theoretical gaps for production deployment guarantees.

**Citation Gaps Identified for Phase 2B**

1. **LoRA Theoretical Foundations**: Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022 - Original LoRA paper needed for theoretical foundation of low-rank approximation.

2. **Schema Evolution in Databases**: Database schema change detection literature (e.g., Bernstein et al., "Schema Matching and Query Rewriting in Ontologies") - TTEC's schema drift detection builds on database schema evolution methods.

3. **Missing Value Imputation**: MICE (Multiple Imputation by Chained Equations), MissForest - TTEC's context-aware imputation should compare to statistical imputation baselines.

4. **Federated Tabular Learning Survey**: Systematic survey of federated learning for tabular data - Related work section should cover prior FL + tabular work comprehensively.
