## Related Work

**Related Papers**
1. **Title**: C-LoRA: Contextual Low-Rank Adaptation for Uncertainty Estimation (NeurIPS 2025)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that contextualized LoRA modules can achieve well-calibrated uncertainties, proving that calibration can be effectively captured in the LoRA parameter space.
   - **Year**: 2025

2. **Title**: Domain generalization through meta-learning: a survey
   - **Authors**: Khoee et al.
   - **Summary**: Shows that meta-learning enables fast adaptation while preserving desired properties across domains through learned initializations.
   - **Year**: 2024

3. **Title**: Restoring Calibration for Aligned Large Language Models: A Calibration-Aware Fine-Tuning Approach (ICML 2025)
   - **Authors**: Xiao et al.
   - **Summary**: Demonstrates that ECE regularization in fine-tuning loss maintains low calibration error and categorizes models into calibratable and non-calibratable regimes.
   - **Year**: 2025

4. **Title**: Uncertainty quantification in fine-tuned LLMs using LoRA ensembles (arXiv:2402.12264)
   - **Authors**: Balabanov et al.
   - **Summary**: Shows that uncertainty can be modeled in the LoRA parameter space through ensemble methods.
   - **Year**: 2024

5. **Title**: Functional-Level Uncertainty Quantification for Calibrated Fine-Tuning (UQ4CT) (ICLR 2026 submission)
   - **Authors**: Not specified
   - **Summary**: Achieves 25% ECE reduction through a Mixture-of-Experts framework with hierarchical decomposition.
   - **Year**: 2026

6. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
   - **Authors**: Hu et al.
   - **Summary**: Introduces the standard LoRA method for parameter-efficient fine-tuning without calibration awareness; serves as primary baseline.
   - **Year**: 2021

7. **Title**: On Calibration of Modern Neural Networks
   - **Authors**: Guo et al.
   - **Summary**: Proposes temperature scaling as a classical post-hoc calibration method for neural networks.
   - **Year**: 2017

8. **Title**: AlignGuard-LoRA
   - **Authors**: Das et al.
   - **Summary**: Uses Fisher Information Matrix-based regularization for alignment preservation during fine-tuning; targets alignment rather than calibration.
   - **Year**: 2025

9. **Title**: Calibration-Tuning: Teaching LLMs to Know What They Don't Know (UncertaiNLP Workshop)
   - **Authors**: Kapoor et al.
   - **Summary**: Demonstrates that existing language models are poorly calibrated after fine-tuning.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Calibration Awareness in Standard PEFT**: Standard LoRA and other parameter-efficient fine-tuning methods have no uncertainty or calibration component, leading to poorly calibrated models after fine-tuning.

2. **Calibration Degradation During Fine-Tuning**: Existing language models become poorly calibrated after fine-tuning, indicating that current fine-tuning approaches do not preserve pre-trained calibration properties.

3. **Alignment vs. Calibration Trade-off**: Existing methods like AlignGuard-LoRA target alignment preservation but do not address calibration, suggesting a gap in methods that jointly optimize for both properties.

4. **Domain Generalization of Calibration**: While meta-learning enables adaptation across domains, maintaining calibration properties during domain transfer remains an open challenge.
