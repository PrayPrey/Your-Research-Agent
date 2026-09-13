## Related Work

**Related Papers**

1. **Title**: Robust uncertainty principles: Exact signal reconstruction from highly incomplete frequency information
   - **Authors**: Candès, E. J., Romberg, J., & Tao, T.
   - **Summary**: Foundation of compressed sensing theory; provides RIP definition and probabilistic guarantees for signal reconstruction from incomplete measurements.
   - **Year**: 2006

2. **Title**: A simple proof of the restricted isometry property for random matrices
   - **Authors**: Baraniuk, R., Davenport, M., DeVore, R., & Wakin, M.
   - **Summary**: Proves RIP for Gaussian/Rademacher random matrices, guaranteeing that random projections satisfy RIP with high probability for appropriate compression parameters.
   - **Year**: 2008

3. **Title**: The information bottleneck method
   - **Authors**: Tishby, N., Pereira, F. C., & Bialek, W.
   - **Summary**: Introduces the information bottleneck principle demonstrating how to compress data while preserving predictive information.
   - **Year**: 1999

4. **Title**: Elements of Information Theory (2nd ed.)
   - **Authors**: Cover, T. M., & Thomas, J. A.
   - **Summary**: Foundational textbook providing Data Processing Inequality which establishes conservative bounds showing compression never artificially increases mutual information.
   - **Year**: 2006

5. **Title**: Estimating mutual information
   - **Authors**: Kraskov, A., Stögbauer, H., & Grassberger, P.
   - **Summary**: Develops the k-NN mutual information estimator, currently a standard method for low-dimensional MI estimation.
   - **Year**: 2004

6. **Title**: Mutual Information Neural Estimation
   - **Authors**: Belghazi, M. I., Baratin, A., Rajeshwar, S., et al.
   - **Summary**: MINE - neural network-based MI estimator that scales to high-dimensional data using dual representation.
   - **Year**: 2018

7. **Title**: infomeasure: a comprehensive Python package for information theory measures and estimators
   - **Authors**: Büth, C. M., Acharya, K., & Zanin, M.
   - **Summary**: State-of-the-art Python implementation providing unified framework with 15+ information theory measures and GPU acceleration.
   - **Year**: 2025

8. **Title**: High Dimensional Statistical Estimation Under Uniformly Dithered One-Bit Quantization
   - **Authors**: Chen, J., Wang, C., Ng, M. K., & Wang, D.
   - **Summary**: Proves minimax rates for covariance estimation under compressed sensing with quantization, demonstrating second moment preservation.
   - **Year**: 2022

9. **Title**: Cascaded compressed-sensing single-pixel camera for high-dimensional optical imaging
   - **Authors**: Park, J., & Gao, L.
   - **Summary**: Multi-stage cascaded compressed sensing exploiting compressibility in multiple domains for optical imaging applications.
   - **Year**: 2023

10. **Title**: Distributed State Estimation for Sparse Stochastic Systems Based on Compressed Sensing
    - **Authors**: Li, R., Gan, D., Gu, H., & Lü, J.
    - **Summary**: Applies compressed sensing to non-stationary stochastic systems with error bounds, enabling real-time adaptive modeling.
    - **Year**: 2024

11. **Title**: Mutual Information of Multiple Rhythms for EEG Signals
    - **Authors**: Ibáñez-Molina, A., Soriano, M. F., & Iglesias-Parro, S.
    - **Summary**: MIMR measure for multi-frequency EEG analysis (3-5 bands), demonstrating current methods are limited to low-dimensional analysis.
    - **Year**: 2020

12. **Title**: Early MS Identification Using Non-linear Functional Connectivity and Graph-theoretic Measures of Cognitive Task-fMRI Data
    - **Authors**: Azarmi, F., Shalbaf, A., et al.
    - **Summary**: Uses kernel MI for nonlinear brain connectivity in fMRI data, representing current best practice for clinical applications but requiring large sample sizes.
    - **Year**: 2023

13. **Title**: Integrated Phenomenology and Brain Connectivity Demonstrate Changes in Nonlinear Processing in Jhana Advanced Meditation
    - **Authors**: Potash, R. M., van Mil, S. D., Estarellas, M., et al.
    - **Summary**: Develops weighted symbolic MI for nonlinear cognitive state transitions in meditation, currently limited to single-subject analysis.
    - **Year**: 2025

14. **Title**: Tighter Bounds on the Information Bottleneck with Application to Deep Learning
    - **Authors**: Weingarten, N. Z., Yakhini, Z., Butman, M., & Gilad-Bachrach, R.
    - **Summary**: Provides improved variational bounds for information bottleneck showing compression preserves predictive information in deep learning contexts.
    - **Year**: 2024

15. **Title**: A relevance model of human sparse communication in cooperation
    - **Authors**: Jiang, K., Jiang, B., Sadaghdar, A., et al.
    - **Summary**: Information-theoretic model of communication efficiency in human-AI teams, demonstrating sparse communication principles.
    - **Year**: 2025

**Key Challenges**

1. **No finite-sample guarantees for IT estimation on brain data**: Current information-theoretic estimation methods lack explicit finite-sample error bounds when applied to high-dimensional brain data, making reliability assessment difficult.

2. **Scalability bottleneck for whole-brain IT analysis**: Existing methods require prohibitively large sample sizes (N~50,000) for whole-brain mutual information computation, limiting practical applications.

3. **Lack of theoretically grounded dimensionality reduction for IT preservation**: Standard dimensionality reduction methods (PCA, ICA) do not provide theoretical guarantees for preserving information-theoretic quantities like mutual information.

4. **No adaptive estimator selection framework**: Current approaches use fixed estimation methods without data-driven selection based on signal characteristics (sparsity, dimension, noise level).

5. **Missing real-time capability for IT-based BCI**: Computational complexity of existing MI estimators (O(N²) for kernel methods) prevents real-time brain-computer interface applications requiring <100ms latency.

6. **Limited applicability beyond Gaussian regime**: Most theoretical guarantees for IT estimation assume specific data distributions, with limited extension to nonlinear dependencies and non-Gaussian data.

7. **Sample complexity not characterized**: Many state-of-the-art Python implementations lack characterization of sample complexity requirements for achieving target accuracy levels.

8. **Single-subject limitation in nonlinear methods**: Advanced nonlinear MI methods (e.g., symbolic MI) are currently restricted to single-subject analysis and cannot scale to population studies.

9. **Cascaded error accumulation in multi-modal data**: Multi-modal neuroimaging (fMRI+EEG) lacks principled frameworks for dimensionality reduction that control error propagation across modalities.

10. **Unknown true MI in real data validation**: Validating MI estimators on real brain data requires reliance on behavioral proxies or ROI comparisons rather than ground truth, complicating accuracy assessment.
