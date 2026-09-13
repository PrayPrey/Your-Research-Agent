## Related Work

**Related Papers**

1. **Title**: Large Language Models(LLMs) on Tabular Data: Prediction, Generation, and Understanding - A Survey (2024)
   - **Authors**: Xi Fang, Weijie Xu, et al.
   - **Summary**: Comprehensive survey consolidating LLM techniques for tabular data generation. Establishes LLM capability for tabular data generation but fairness mechanisms are not addressed.
   - **Year**: 2024

2. **Title**: Generative adversarial networks vs large language models: a comparative study on synthetic tabular data generation (2025)
   - **Authors**: Austin A. Barr, Robert Rozman, E. Guo
   - **Summary**: Evidence showing GPT-4o outperforms CTGAN in zero-shot tabular generation, though no fairness metrics were evaluated. Demonstrates LLMs as emerging standard for synthetic data generation.
   - **Year**: 2025

3. **Title**: DP-Tabula: Differentially Private Synthetic Tabular Data Generation with Large Language Models (2025)
   - **Authors**: Weijie Niu, et al.
   - **Summary**: Integrates DP-SGD into LLMs for private tabular data generation. Technical precedent proving trustworthiness constraints (privacy via DP-SGD) can be integrated into LLM synthetic data generation, but fairness dimension is completely absent.
   - **Year**: 2025

4. **Title**: SafeSynthDP: Leveraging Large Language Models for Privacy-Preserving Synthetic Data Generation Using Differential Privacy (2024)
   - **Authors**: Mahadi Hasan Nahid, Sadid Bin Hasan
   - **Summary**: First LLM+DP work for medical datasets showing domain-specific precedent that LLM adaptation for trustworthiness is practical, not just theoretical. Does not address fairness constraints.
   - **Year**: 2024

5. **Title**: When Neutrality Conceals Bias: Perceived Discrimination in Algorithmic Decisions (2025)
   - **Authors**: Yingqi Li, Ruihua Lu
   - **Summary**: AI decisions perceived as less discriminatory due to inferred neutrality; identifies critical gap between perceived and actual fairness. Informs requirement for explicit fairness mechanisms and auditable reasoning traces.
   - **Year**: 2025

6. **Title**: Economics and Computation: An Introduction to Algorithmic Game Theory, Computational Social Choice, and Fair Division (2024)
   - **Authors**: Dirk Bergemann, Joan Feigenbaum
   - **Summary**: Game-theoretic frameworks for fairness mechanisms and mechanism design principles for fair resource allocation. Provides formal framework for thinking about fairness as an optimization problem with constraints.
   - **Year**: 2024

7. **Title**: Measuring and Improving Instruction Following in Large Language Models
   - **Authors**: Not specified
   - **Summary**: GPT-4 achieves 85% constraint satisfaction with instruction-tuning, confirming semantic constraint learning is achievable. Validates instruction-following mechanism for fairness constraints.
   - **Year**: Not specified

8. **Title**: Constrained Text Generation with Large Language Models
   - **Authors**: Not specified
   - **Summary**: Requires specialized decoding (NEUROLOGIC) for hard constraints; prompting alone is insufficient. Confirms need for constrained decoding approach, not just prompting.
   - **Year**: Not specified

9. **Title**: CTAB-GAN+: enhancing tabular data synthesis (2022)
   - **Authors**: Zilong Zhao, A. Kunar, R. Birke, L. Chen
   - **Summary**: SOTA GAN for tabular data with differential privacy achieving 21.9% higher F1-score than baselines under privacy budget. Represents current state-of-the-art GAN-based approach.
   - **Year**: 2022

10. **Title**: DECAF: Generating Fair Synthetic Data Using Causally-Aware Generative Networks (2021)
    - **Authors**: Not specified
    - **Summary**: Best-performing fairness algorithm using causal fairness approach for GAN-based synthetic data generation. Represents SOTA for fairness-aware GANs.
    - **Year**: 2021

11. **Title**: Can Synthetic Data be Fair and Private? A Comparative Study (2025)
    - **Authors**: Qinyi Liu, et al.
    - **Summary**: DECAF algorithm best balances privacy and fairness; pre-processing fairness algorithms more effective on synthetic data. Establishes benchmark for fairness-privacy trade-off evaluation.
    - **Year**: 2025

12. **Title**: Syntheval: a framework for detailed utility and privacy evaluation of tabular synthetic data (2024)
    - **Authors**: A. D. Lautrup, et al.
    - **Summary**: Unified metrics for fidelity, privacy, utility assessment (missing fairness dimension). Provides evaluation framework for synthetic data quality.
    - **Year**: 2024

13. **Title**: GReaT/be_great
    - **Authors**: Not specified
    - **Summary**: GPT-2 fine-tuned for tabular data enabling realistic generation but no fairness mechanisms. Demonstrates LLM capability for tabular data without fairness constraints.
    - **Year**: 2022

14. **Title**: MedEqualizer
    - **Authors**: Not specified
    - **Summary**: Model-agnostic augmentation framework for fairness in medical synthetic data. Domain-specific fairness approach for healthcare applications.
    - **Year**: 2025

15. **Title**: Generative AI mitigates representation bias and improves model fairness (CA-GAN)
    - **Authors**: Not specified
    - **Summary**: CA-GAN (conditional generation for fairness) reduces fairness gaps without utility loss, validating fairness-generation compatibility. Demonstrates fairness and utility are not fundamentally incompatible.
    - **Year**: 2025

**Key Challenges**

1. **Fairness Gap in LLM Synthetic Data Generation**: Current LLM-based tabular data generation methods lack explicit fairness mechanisms. While LLMs have been shown to generate high-quality synthetic data and privacy constraints have been successfully integrated (DP-Tabula, SafeSynthDP), the fairness dimension remains completely absent.

2. **Post-Hoc Correction Limitations**: Existing fairness approaches rely on reactive post-hoc correction (reweighting, resampling) which typically achieves 8-12% demographic parity difference but loses 5-10% utility due to distributional distortions from data manipulation.

3. **GAN Training Complexity**: GAN-based fairness methods (CTAB-GAN+, DECAF) require domain-specific architectures and high training costs (100+ epochs from scratch), limiting architectural flexibility and cross-domain transfer.

4. **Perceived vs. Actual Fairness**: AI systems perceived as neutral may still exhibit bias, creating a gap between perceived and actual fairness that requires explicit fairness mechanisms and auditable reasoning traces.

5. **Fairness Metric Conflicts**: Different fairness definitions (demographic parity vs. equalized odds) can conflict, requiring trade-off analysis that is not well-characterized in existing literature.

6. **Fairness-Utility Trade-off**: No published work directly measures fairness-utility trade-off for instruction-tuned LLM synthetic data generation, leaving a critical empirical evidence gap.

7. **Constraint Learning Mechanisms**: Unclear whether LLMs can reliably interpret and follow semantic fairness constraints through instruction-tuning, and whether 100-500 examples are sufficient for effective constraint learning.

8. **Intersectionality Handling**: Multiple protected attributes (race × gender × age) create exponential constraint complexity that is not adequately addressed by current methods.

9. **Evaluation Framework Gaps**: Existing evaluation frameworks (Syntheval) provide metrics for fidelity, privacy, and utility but lack comprehensive fairness dimension integration.

10. **Implementation Complexity vs. Accessibility**: High implementation complexity and training costs limit accessibility of fairness-aware ML for resource-constrained organizations, creating barriers to fair AI deployment.
