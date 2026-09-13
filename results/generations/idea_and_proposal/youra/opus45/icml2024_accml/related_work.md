## Related Work

**Related Papers**
1. **Title**: Democratizing Protein Language Models with Parameter-Efficient Fine-Tuning
   - **Authors**: Sledzieski et al.
   - **Summary**: Demonstrates that LoRA achieves competitive performance with 3 orders of magnitude fewer parameters, and shows that PEFT outperforms traditional fine-tuning for protein-protein interaction prediction.
   - **Year**: 2023

2. **Title**: Active Learning Enables Extrapolation in Molecular Generative Models
   - **Authors**: Antoniuk et al.
   - **Summary**: Demonstrates that closed-loop active learning achieves 79% improvement in out-of-distribution classification for molecular generative models.
   - **Year**: 2025

3. **Title**: Mechanical Feedback Control for Multicellular Tissue Size Maintenance
   - **Authors**: Hirashima
   - **Summary**: Establishes that biological homeostasis through mechanical feedback provides a paradigm for control-theoretic frameworks in biological systems.
   - **Year**: 2022

4. **Title**: Multi-modal Transfer Learning between Biological Foundation Models
   - **Authors**: Garau-Luis et al.
   - **Summary**: Demonstrates that cross-modal DNA/RNA/protein transfer is feasible with LoRA fine-tuning between biological foundation models.
   - **Year**: 2024

5. **Title**: BALD (Bayesian Active Learning by Disagreement)
   - **Authors**: Houlsby et al.
   - **Summary**: Introduces an uncertainty-based active learning approach using Bayesian disagreement for sample selection.
   - **Year**: 2011

6. **Title**: BatchBALD
   - **Authors**: Kirsch et al.
   - **Summary**: Extends Bayesian active learning to batch-mode settings while maintaining diversity in selected samples.
   - **Year**: 2019

7. **Title**: DeepChem Active Learning Pipelines
   - **Authors**: Not specified
   - **Summary**: Provides baseline implementation for active learning pipelines specifically designed for drug discovery applications.
   - **Year**: Not specified

8. **Title**: Quantifying and managing uncertainty in systems biology
   - **Authors**: Balsa-Canto et al.
   - **Summary**: Reviews active learning and uncertainty quantification approaches for biology, identifying the absence of unified frameworks that combine these methods with efficient foundation models.
   - **Year**: 2025

9. **Title**: Combining Bayesian and Evidential UQ for Improved Bioactivity Modeling
   - **Authors**: Khalil et al.
   - **Summary**: Develops uncertainty quantification methods for drug discovery that exist separately from active learning frameworks.
   - **Year**: 2025

10. **Title**: AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning (arXiv:2303.10512)
    - **Authors**: Not specified
    - **Summary**: Introduces importance-based LoRA rank allocation for adaptive parameter-efficient fine-tuning, though not connected to active learning or biological applications.
    - **Year**: 2023

**Key Challenges**
1. **Lack of Unified Frameworks**: Existing work on active learning and uncertainty quantification for biology remains fragmented, with no unified framework combining these approaches with efficient foundation models.
2. **Disconnection Between UQ and Active Learning**: Uncertainty quantification methods for drug discovery have been developed separately from active learning frameworks, limiting their combined effectiveness.
3. **Gap Between Adaptive PEFT and Active Learning**: Importance-based adaptive LoRA rank allocation methods exist but have not been connected to active learning strategies or biological applications.
4. **Cross-Modal Integration**: While cross-modal transfer between biological foundation models is feasible, integration with active learning and uncertainty-aware adaptation remains unexplored.
