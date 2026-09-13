1. **Title**: Beyond Overconfidence: Foundation Models Redefine Calibration in Deep Neural Networks (arXiv:2506.09593)
   - **Authors**: Achim Hekler, Lukas Kuhn, Florian Buettner
   - **Summary**: This paper investigates the calibration behavior of foundation models, revealing that they tend to be underconfident in in-distribution predictions, leading to higher calibration errors. However, they demonstrate improved calibration under distribution shifts. The study highlights the complex effects of architectural and training innovations on calibration, challenging established narratives of continuous improvement.
   - **Year**: 2025

2. **Title**: Conformal Prediction Adaptive to Unknown Subpopulation Shifts (arXiv:2506.05583)
   - **Authors**: Nien-Shao Wang, Duygu Nur Yaldiz, Yavuz Faruk Bakman, Sai Praneeth Karimireddy
   - **Summary**: This work addresses subpopulation shifts where the test environment exhibits an unknown and differing mixture of subpopulations compared to the calibration data. The authors propose methods that adapt conformal prediction to such shifts, ensuring valid coverage without requiring explicit knowledge of subpopulation structure. The algorithms scale to high-dimensional settings and perform effectively in realistic machine learning tasks.
   - **Year**: 2025

3. **Title**: Improving Self-Training Under Distribution Shifts via Anchored Confidence with Theoretical Guarantees (arXiv:2411.00586)
   - **Authors**: Taejong Joo, Diego Klabjan
   - **Summary**: This paper develops a method to improve self-training under distribution shifts based on temporal consistency. The approach builds an uncertainty-aware temporal ensemble with relative thresholding, smoothing noisy pseudo labels to promote selective temporal consistency. The method consistently improves self-training performances across diverse distribution shift scenarios without computational overhead.
   - **Year**: 2024

4. **Title**: Adaptive Calibrator Ensemble for Model Calibration Under Distribution Shift (arXiv:2303.05331)
   - **Authors**: Yuli Zou, Weijian Deng, Liang Zheng
   - **Summary**: The authors propose a method named Adaptive Calibrator Ensemble (ACE) to calibrate models on out-of-distribution datasets. ACE trains two calibration functions for in-distribution and severely out-of-distribution data, respectively. It uses an adaptive weighting method to balance the two functions, improving calibration performance on out-of-distribution benchmarks without compromising in-distribution calibration accuracy.
   - **Year**: 2023

5. **Title**: Frustratingly Easy Uncertainty Estimation for Distribution Shift (arXiv:2106.03762)
   - **Authors**: Tiago Salvador, Vikram Voleti, Alexander Iannantuono, Adam Oberman
   - **Summary**: This paper presents a simple method for uncertainty estimation under distribution shifts. By exposing the original model to corrupted images and performing statistical calibration on the outputs, the approach demonstrates superior performance on a wide range of distribution shifts and unsupervised domain adaptation tasks.
   - **Year**: 2021

6. **Title**: Covariance-Aware Feature Alignment with Pre-Computed Source
   - **Authors**: Not specified
   - **Summary**: The paper proposes Covariance-Aware Feature Alignment (CAFe), a test-time adaptation method that aligns feature distributions without accessing the source dataset. CAFe incorporates pre-computed source statistics to match the mean and covariance of features, effectively adapting to target domains with multiple types of corruption.
   - **Year**: Not specified

7. **Title**: Meta-Learning to Calibrate Gaussian Processes with Deep Kernels for Regression Uncertainty Estimation
   - **Authors**: Not specified
   - **Summary**: This work introduces a meta-learning approach to calibrate Gaussian Processes with deep kernels for regression uncertainty estimation. The method aims to improve uncertainty estimation performance by adapting to new tasks without iterative optimization, connecting differentiable approaches for regression and calibration.
   - **Year**: Not specified

**Key Challenges**:

1. **Dynamic Distribution Shifts**: Foundation models often encounter inputs that differ from their training distribution, leading to overconfident yet incorrect predictions. Existing calibration methods assume static test distributions and fail when data shifts dynamically.

2. **Underconfidence in In-Distribution Predictions**: Some foundation models exhibit underconfidence in in-distribution predictions, resulting in higher calibration errors. This challenges the assumption that larger models are inherently better calibrated.

3. **Scalability of Calibration Methods**: Ensuring that calibration methods scale effectively to high-dimensional settings and large datasets remains a significant challenge.

4. **Computational Overhead**: Developing calibration methods that improve performance without introducing significant computational overhead is crucial for practical deployment.

5. **Generalization to Unseen Scenarios**: Creating calibration techniques that generalize well to unseen distribution shifts and subpopulation variations is essential for reliable real-world applications. 