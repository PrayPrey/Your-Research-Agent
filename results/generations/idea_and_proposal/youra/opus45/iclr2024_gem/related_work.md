## Related Work

**Related Papers**
1. **Title**: Evidential deep learning-based drug-target interaction prediction (SS ID 963ffc0ebccb089ea69272c695657655d8483590)
   - **Authors**: Zhao et al.
   - **Summary**: Demonstrates that evidential deep learning achieves calibrated uncertainty for drug-target interaction prediction, enabling prioritization of high-confidence predictions and identifying novel tyrosine kinase modulators.
   - **Year**: 2025

2. **Title**: Uncertainty estimation with prediction-error circuits (SS ID 8e9c1b95c76bdebf6dfd63f82b7ef0aaf8281b1a)
   - **Authors**: Hertäg, Wilmes, Clopath
   - **Summary**: Shows how neural circuits decompose uncertainty into stimulus (aleatoric) and prediction (epistemic) components through positive and negative error neurons.
   - **Year**: 2025

3. **Title**: Calibrated Uncertainty for Molecular Property Prediction using Ensembles of MPNNs (http://mikkelschmidt.dk/papers/busk2021mlst.pdf)
   - **Authors**: Busk et al.
   - **Summary**: Presents ensemble-based calibrated uncertainty methods for molecular property prediction and demonstrates the importance of recalibration for reliable predictions.
   - **Year**: 2021

4. **Title**: Enhancing uncertainty quantification in drug discovery with censored labels (SS ID e6be012fd59c16afeb9e33e80383f9ae8a084ba1)
   - **Authors**: Svensson et al.
   - **Summary**: Develops methods for handling censored experimental data in uncertainty quantification for drug discovery applications.
   - **Year**: 2025

5. **Title**: Deep Ensembles
   - **Authors**: Lakshminarayanan et al.
   - **Summary**: Establishes a standard uncertainty quantification baseline that requires training and maintaining multiple models for reliable uncertainty estimates.
   - **Year**: 2017

6. **Title**: MC Dropout
   - **Authors**: Gal & Ghahramani
   - **Summary**: Proposes approximate Bayesian uncertainty estimation via dropout at inference time, providing a computationally efficient alternative to full Bayesian methods.
   - **Year**: 2016

7. **Title**: Comprehensive Benchmark Study of Diffusion-Based 3D Molecular Generation Models
   - **Authors**: Qin et al.
   - **Summary**: Demonstrates that 3D computational metrics poorly correlate with experimental outcomes, revealing a significant oracle gap in molecular generation evaluation.
   - **Year**: 2025

8. **Title**: Augmented Memory: Sample-Efficient Generative Molecular Design
   - **Authors**: Guo & Schwaller
   - **Summary**: Achieves state-of-the-art optimization performance against oracles but does not address the quality of oracle calibration.
   - **Year**: 2024

9. **Title**: On Calibration of Modern Neural Networks
   - **Authors**: Guo et al.
   - **Summary**: Defines the Expected Calibration Error (ECE) methodology and establishes the importance of calibration for modern neural networks.
   - **Year**: 2017

**Key Challenges**
1. **Oracle Gap**: 3D computational metrics used in molecular generation poorly correlate with experimental outcomes, creating a disconnect between in silico optimization and real-world performance.
2. **Oracle Calibration Quality**: State-of-the-art generative molecular design methods optimize against oracles without addressing whether those oracles provide well-calibrated uncertainty estimates.
3. **Computational Cost of Uncertainty Quantification**: Standard methods like deep ensembles require training and maintaining multiple models, creating significant computational overhead.
4. **Handling Censored Experimental Data**: Drug discovery datasets often contain censored labels that complicate uncertainty quantification and require specialized methods.
5. **Decomposition of Uncertainty Types**: Distinguishing between aleatoric (data-inherent) and epistemic (model-inherent) uncertainty remains challenging but is important for appropriate decision-making.
