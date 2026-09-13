## Related Work

**Related Papers**

1. **Title**: Textual Bayes: Quantifying Uncertainty in LLM-Based Systems (SS ID: ba854a9128cf38d9e56ee6f16a239399228fe671)
   - **Authors**: Brendan Leigh Ross et al. (11 authors)
   - **Summary**: Introduces MHLP algorithm for Bayesian inference over LLM prompts (input space) to quantify uncertainty in LLM-based systems. Operates at prompt level rather than latent space, requiring multiple prompt variations for computational overhead.
   - **Year**: 2025

2. **Title**: LLM-Integrated Bayesian State Space Models for Multimodal Time-Series Forecasting (SS ID: 0ffd011cf4eb87ceb1a4edb4b7a1b51dbdb157ab)
   - **Authors**: Sungjun Cho et al. (6 authors)
   - **Summary**: Unifies LLMs and Bayesian State Space Models for joint numerical/textual prediction with uncertainty quantification in time-series forecasting. Validates that Bayesian components can be integrated with frozen LLMs via hybrid architectures.
   - **Year**: 2025

3. **Title**: Can Linear Probes Measure LLM Uncertainty? (SS ID: ddcbdd7d63c567da74d42446a5f128e389baa82b)
   - **Authors**: Dakhmouche et al.
   - **Summary**: Develops Bayesian linear models for layer-level uncertainty quantification in LLMs. Empirically demonstrates that LLM hidden activations encode uncertainty-relevant information and predict future outcome distributions.
   - **Year**: 2025

4. **Title**: Probabilistic Embeddings for Frozen Vision-Language Models (GroVE) (SS ID: 737430735c14d870ba980bdff50b433d4460148e)
   - **Authors**: Aishwarya Venkataramanan, P. Bodesheim, Joachim Denzler
   - **Summary**: Applies GP-GPLVM to frozen CLIP embeddings achieving SOTA uncertainty calibration on downstream tasks (retrieval, VQA, active learning) without retraining the base model. Validates GP inference on frozen embeddings for multimodal (vision-language) domain.
   - **Year**: 2025

5. **Title**: Semantic-Aware Gaussian Process Calibration with Structured Layerwise Kernels (SAL-GP)
   - **Authors**: Not specified
   - **Summary**: Introduces layer-wise GP calibration for deep neural networks (image classifiers). Validates GP-based calibration on DNN latent representations in vision domain and supports layer selection strategies.
   - **Year**: 2025

6. **Title**: Posterior Inference in Latent Space for Scalable Constrained Black-box Optimization (SS ID: b3c5a234add5ab2a3b9b83a75cb1759beaaf3a70)
   - **Authors**: Kiyoung Om, Kyuil Sim, Taeyoung Yun, Hyeongyu Kang, Jinkyoo Park
   - **Summary**: Proposes flow-based posterior inference in latent space for Bayesian optimization, demonstrating smoother and more tractable inference than data space. Validates that latent-space Bayesian inference is computationally tractable and effective.
   - **Year**: 2025

7. **Title**: Design and Evaluation of Brain-Inspired Predictive Coding Networks Based on the Free-Energy Principle (SS ID: a0222ef66cb0b31a66cf349c201817b88976f08b)
   - **Authors**: Naruki Hagiwara, Takafumi Kunimi, Kota Ando, M. Akai-Kasaya, Tetsuya Asai
   - **Summary**: Demonstrates biological brains implement predictive coding by maintaining uncertainty over high-level latent representations (not individual synaptic weights). Free energy minimization drives probabilistic inference over latent causes, providing theoretical foundation for latent-space UQ.
   - **Year**: 2024

8. **Title**: A Review of Uncertainty Quantification in Deep Learning: Techniques, Applications and Challenges (SS ID: f14fc9e399d44463a17cc47a9b339b58f6ef7502)
   - **Authors**: Moloud Abdar et al. (12 authors)
   - **Summary**: Comprehensive survey of UQ techniques including Bayesian Neural Networks, ensembles, MC dropout, and evidential deep learning. Identifies scalability as major challenge for Bayesian NNs, motivating dimensional reduction approaches.
   - **Year**: 2020

9. **Title**: A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification (SS ID: c3ea8eb80bc8ca0b21efa273b9e4a9fd059c65be)
   - **Authors**: Anastasios Nikolas Angelopoulos, Stephen Bates
   - **Summary**: Introduces distribution-free uncertainty quantification via conformal prediction, providing coverage guarantees without distributional assumptions. Offers model-agnostic alternative to Bayesian approaches.
   - **Year**: 2021

10. **Title**: Bayesian Inference for Non-Linear Forward Model by Using a VAE-Based Neural Network Structure (SS ID: 14353ef090b7f0d817bba1379db498c7e7dc3a26)
   - **Authors**: Yechuan Zhang, Jian-Qing Zheng, Michael Chappell
   - **Summary**: Develops VAE-based Bayesian inference on latent representations achieving 100ms/image overhead for medical imaging analysis (perfusion MRI) on 1K-4K dimensional latent spaces. Provides computational feasibility benchmark for similar-dimensionality latent space inference.
   - **Year**: 2024

11. **Title**: BoTorch: Bayesian Optimization in PyTorch
   - **Authors**: Not specified
   - **Summary**: Production-ready Bayesian optimization framework with scalable GPs via GPyTorch backend, sparse inducing points, and stochastic variational inference. Provides implementation tools for sparse GP training with O(m²n) complexity.
   - **Year**: Not specified

12. **Title**: Uncertainty Toolbox
   - **Authors**: Not specified
   - **Summary**: Model-agnostic toolbox for predictive uncertainty quantification, providing calibration metrics (ECE, Brier score, NLL) and visualization tools for evaluating uncertainty estimates.
   - **Year**: Not specified

**Key Challenges**

1. **Scalability of Bayesian Inference for Large Models**: Traditional Bayesian inference on billion-parameter LLMs is computationally intractable (O(n³) complexity). Dimensional reduction via latent space inference needed to achieve tractable deployment.

2. **Text-Only vs Multimodal Embedding Structures**: Existing GP-based UQ methods validated on multimodal embeddings (CLIP, contrastive learning) may not transfer directly to text-only LLMs trained via autoregressive next-token prediction. Training objective mismatch poses validation risk.

3. **Calibration vs Computational Cost Trade-off**: SOTA methods like Deep Ensembles achieve strong calibration (ECE ≈ 0.08-0.12) but require 5× training and inference cost. Need for methods achieving comparable calibration with lower computational overhead.

4. **Hidden State Information Sufficiency**: Uncertainty whether frozen LLM hidden states (without fine-tuning) contain sufficient task-relevant semantic and uncertainty information for calibrated predictions. Requires empirical validation across layers.

5. **Layer Selection for Optimal Uncertainty**: Unknown which transformer layers (early, middle, late) encode optimal uncertainty-relevant information for GP-based UQ. Middle layers hypothesized but requires systematic validation.

6. **OOD Detection with Latent Space Uncertainty**: Distribution shift affects both LLM embeddings (OOD for LLM) and GP extrapolation (OOD for GP), potentially compounding errors. Effectiveness of GP epistemic uncertainty for OOD detection needs validation.

7. **Sparse GP Approximation Quality**: Trade-off between computational tractability (sparse GP with inducing points) and calibration quality (full GP). Need to determine optimal number of inducing points (m) that maintains calibration while achieving <200ms inference.

8. **Statistical Power with Limited Benchmark Tasks**: Standard UQ evaluation uses limited tasks (SST-2, MNLI), providing low statistical power for generalizable conclusions. Need for expanded task coverage across diverse domains.

9. **Integration with Production LLM Systems**: Research prototypes may not be deployment-ready without engineering effort to integrate with existing LLM serving systems (vLLM, TensorRT-LLM, HuggingFace Inference).

10. **Kernel Expressiveness for Text Semantics**: Uncertainty whether Gaussian Processes (even with expressive kernels) can model complex semantic dependencies in text understanding tasks compared to deep neural networks. May require deep kernels or hybrid approaches.
