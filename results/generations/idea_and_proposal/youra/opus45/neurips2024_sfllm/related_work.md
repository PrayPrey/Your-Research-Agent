## Related Work

**Related Papers**
1. **Title**: Conformal Prediction with Large Language Models for Multi-Choice Question Answering (arXiv:2023)
   - **Authors**: Kumar, Lu, Gupta, Palepu, Bellamy, Raskar, Beam
   - **Summary**: First systematic application of conformal prediction to LLMs, demonstrating that uncertainty estimates correlate with accuracy in question answering tasks.
   - **Year**: 2023

2. **Title**: Audit Me If You Can: Query-Efficient Active Fairness Auditing
   - **Authors**: Hartmann, Pohlmann, Hanslik, Giessing, Berendt, Delobelle
   - **Summary**: Introduces BAFA, an active fairness auditing method that achieves 40× fewer queries than stratified sampling approaches.
   - **Year**: 2026

3. **Title**: Provable Robust Watermarking for AI-Generated Text
   - **Authors**: Zhao, Ananth, Li, Wang
   - **Summary**: Proposes Unigram-Watermark with theoretical guarantees for quality preservation, detection accuracy, and robustness against attacks.
   - **Year**: 2023

4. **Title**: An Improved Bonferroni Procedure for Multiple Tests of Significance
   - **Authors**: Simes
   - **Summary**: Develops a modified Bonferroni correction that is less conservative when dealing with correlated statistical tests.
   - **Year**: 1986

5. **Title**: Bonferroni Correction
   - **Authors**: Not specified
   - **Summary**: Naive multiple testing correction approach using the formula α_joint = k × α_i for controlling family-wise error rate.
   - **Year**: Not specified

6. **Title**: From Calibration to Collaboration: LLM UQ Should Be More Human-Centered
   - **Authors**: Devic et al.
   - **Summary**: Argues that current uncertainty quantification methods for LLMs are fragmented and advocates for more human-centered approaches.
   - **Year**: 2025

7. **Title**: Statistical Hypothesis Testing for Auditing Robustness in LMs
   - **Authors**: Rauba et al.
   - **Summary**: Proposes a unified statistical testing framework for auditing language model robustness, though limited to a single dimension.
   - **Year**: 2025

**Key Challenges**
1. **Fragmented UQ Methods**: Current uncertainty quantification approaches for LLMs are disconnected and lack integration, preventing comprehensive model assessment.
2. **No Unified Multi-Aspect Auditing Framework**: Existing methods do not provide a unified framework capable of simultaneously auditing multiple aspects of LLM behavior (uncertainty, fairness, watermarking).
3. **Single-Dimension Focus**: Current unified testing approaches are limited to auditing only one dimension (e.g., robustness) rather than addressing multiple safety and reliability concerns together.
4. **Lack of Composition Theory**: No existing theoretical framework addresses how to compose multiple audit certificates while maintaining statistical validity across correlated tests.
5. **Query Efficiency**: Traditional auditing approaches like stratified sampling require excessive queries, making comprehensive multi-aspect auditing computationally expensive.
