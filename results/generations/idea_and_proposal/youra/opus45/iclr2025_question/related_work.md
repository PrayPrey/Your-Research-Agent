## Related Work

**Related Papers**
1. **Title**: Conformal Prediction for Natural Language Processing: A Survey (arXiv:2405.01976)
   - **Authors**: Campos et al.
   - **Summary**: Establishes that conformal prediction is model-agnostic and distribution-free, providing a foundation for uncertainty quantification in NLP applications.
   - **Year**: 2024

2. **Title**: Large language model validity via enhanced conformal prediction methods
   - **Authors**: Candès, Cherian, Gibbs (Stanford)
   - **Summary**: Demonstrates that enhanced conformal prediction methods can achieve conditional validity for LLMs, with a filtering approach that preserves model utility.
   - **Year**: 2025

3. **Title**: ConU: Conformal Uncertainty in Large Language Models with Correctness Coverage Guarantees (arXiv:2407.00499)
   - **Authors**: Wang et al.
   - **Summary**: Combines self-consistency with conformal prediction to achieve strict coverage guarantees, validated across 7 LLMs and 4 datasets at EMNLP 2024.
   - **Year**: 2024

4. **Title**: ResCP: Reservoir Conformal Prediction for Time Series (arXiv:2510.05060)
   - **Authors**: Neglia et al.
   - **Summary**: Introduces position-adaptive reweighting to achieve asymptotic conditional coverage with a training-free design for time series applications.
   - **Year**: 2025

5. **Title**: Generating with Confidence: Uncertainty Quantification for Black-box LLMs
   - **Authors**: Lin et al.
   - **Summary**: Proposes semantic dispersion as an uncertainty predictor for selective natural language generation in black-box LLM settings.
   - **Year**: 2023

6. **Title**: SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection
   - **Authors**: Manakul et al.
   - **Summary**: Develops sampling consistency methods for hallucination detection, serving as a baseline for coverage comparison in LLM uncertainty quantification.
   - **Year**: 2023

7. **Title**: Uncertainty Quantification and Confidence Calibration in LLMs: A Survey
   - **Authors**: Liu et al.
   - **Summary**: Provides a taxonomy of uncertainty quantification methods and identifies the need for theoretically-grounded UQ approaches in LLMs.
   - **Year**: 2025

8. **Title**: A Survey on Uncertainty Quantification of Large Language Models
   - **Authors**: Shorinwa et al.
   - **Summary**: Surveys uncertainty quantification methods for LLMs and explicitly identifies the need for distribution-free UQ methods.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Theoretically-Grounded UQ Methods**: Existing uncertainty quantification approaches for LLMs often lack rigorous theoretical foundations, as identified in recent survey literature.
2. **Need for Distribution-Free Methods**: Current UQ methods frequently rely on distributional assumptions that may not hold in practice, highlighting the need for distribution-free approaches.
3. **Conditional Validity**: Achieving conditional coverage guarantees (rather than just marginal coverage) remains challenging for LLM uncertainty quantification.
4. **Black-Box Accessibility**: Many LLMs are deployed as black-box systems without access to internal probabilities, requiring uncertainty methods that work without model internals.
5. **Preserving Model Utility**: Uncertainty quantification methods must balance providing reliable coverage guarantees while maintaining the practical utility of LLM outputs.
