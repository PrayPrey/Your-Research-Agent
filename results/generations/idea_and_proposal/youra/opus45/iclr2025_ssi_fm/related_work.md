## Related Work

**Related Papers**
1. **Title**: Constitutional AI: Harmlessness from AI Feedback (arXiv:2212.08073)
   - **Authors**: Bai et al. (Anthropic)
   - **Summary**: Demonstrates that RLAIF enables self-improvement without human labels through self-critiques and revisions, providing the foundation for constitutional anchor approaches in AI alignment.
   - **Year**: 2022

2. **Title**: Is Model Collapse Inevitable? Breaking the Curse of Recursion by Accumulating Real and Synthetic Data (arXiv:2404.01413)
   - **Authors**: Gerstgrasser et al.
   - **Summary**: Shows that accumulation strategy provides finite error bounds compared to unbounded error with replacement, offering core evidence for accumulative training approaches to prevent model collapse.
   - **Year**: 2024

3. **Title**: How Bad is Training on Synthetic Data? A Statistical Analysis of Language Model Collapse (arXiv:2404.05090)
   - **Authors**: Seddik et al.
   - **Summary**: Provides theoretical analysis establishing maximal synthetic data ratios to avoid collapse, offering the theoretical basis for decay weighting strategies in synthetic data usage.
   - **Year**: 2024

4. **Title**: Weak-to-Strong Generalization (arXiv:2312.09390)
   - **Authors**: Burns et al. (OpenAI)
   - **Summary**: Demonstrates that weak models (GPT-2) can supervise strong models (GPT-4), recovering GPT-3.5 level performance, establishing the foundation for ensemble verification concepts.
   - **Year**: 2023

5. **Title**: Constitution or Collapse?
   - **Authors**: Zhang
   - **Summary**: Shows that Constitutional AI causes collapse in smaller models without accumulation, motivating the need for adaptive anchor weighting and minimum model scale requirements (≥13B parameters).
   - **Year**: 2025

6. **Title**: Leveraging Ensemble Diversity for Robust Self-Training (AISTATS 2024)
   - **Authors**: Odonnat et al.
   - **Summary**: Introduces T-similarity metric with theoretical guarantees for ensemble verification, which can be adopted for diversity-based verification components in self-improving systems.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Unified Framework**: No existing work provides a unified framework that combines AI feedback, weak-to-strong supervision, and collapse prevention into a single coherent approach.

2. **Model Collapse in Recursive Training**: Training on synthetic data leads to unbounded error accumulation when using replacement strategies, requiring careful accumulation approaches to maintain finite error bounds.

3. **Scale Sensitivity of Constitutional Methods**: Constitutional AI approaches cause collapse in smaller models, necessitating adaptive weighting mechanisms and minimum scale requirements for stable self-improvement.

4. **Synthetic Data Ratio Constraints**: There exist theoretical limits on the proportion of synthetic data that can be used in training before collapse occurs, requiring principled decay weighting strategies.
