## Related Work

**Related Papers**
1. **Title**: A simple general approach to inference about the tail of a distribution (Hill, B. M., 1975)
   - **Authors**: Hill, B. M.
   - **Summary**: Provides the core Hill estimator formula with asymptotic normality proof showing √k(α^(-1) - α_0^(-1)) → N(0, α_0^(-2)), establishing foundational methodology for tail-index estimation under i.i.d. samples and stationarity assumptions.
   - **Year**: 1975

2. **Title**: Extreme Value Theory: An Introduction (de Haan, L. & Ferreira, A., 2006)
   - **Authors**: de Haan, L. and Ferreira, A.
   - **Summary**: Textbook reference establishing second-order regular variation conditions for Hill estimator convergence with bias characterization of O(k^(-1)) under second-order conditions.
   - **Year**: 2006

3. **Title**: Weak Signals and Heavy Tails: Machine-learning meets Extreme Value Theory (Clémençon, S. & Sabourin, A., 2025)
   - **Authors**: Clémençon, S. and Sabourin, A.
   - **Summary**: Survey bridging EVT and statistical learning, providing non-parametric framework for learning from extreme data with exponential maximal deviation inequalities and validating Hill estimator application to ML contexts.
   - **Year**: 2025

4. **Title**: Hausdorff dimension, heavy tails, and generalization in neural networks (Simsekli et al., 2020)
   - **Authors**: Simsekli, U., Sener, O., Deligiannidis, G., and Erdogdu, M. A.
   - **Summary**: Establishes theoretical link between tail-index α and generalization via Hausdorff dimension D_H = d/α, proving generalization bound controlled by D_H where heavier tails (lower α) lead to better generalization.
   - **Year**: 2020

5. **Title**: Heavy Tails in SGD and Compressibility of Overparametrized Neural Networks (Barsbey et al., 2021)
   - **Authors**: Barsbey, M., Sefidgaran, M., Erdogdu, M. A., Richard, G., and Simsekli, U.
   - **Summary**: Proves α-stable limit for SGD with large η/B ratio (Theorem 3.2) with scaling law α ∝ (B/η)^(1/2), demonstrating heavier tails lead to more compressible networks and validating Pareto assumption for gradients.
   - **Year**: 2021

6. **Title**: Emergence of heavy tails in homogenized stochastic gradient descent (Jiao, Z. & Keller-Ressel, M., 2024)
   - **Authors**: Jiao, Z. and Keller-Ressel, M.
   - **Summary**: Theoretical characterization providing explicit upper/lower bounds on α for continuous-time SGD approximation but without practical estimation algorithm implementation.
   - **Year**: 2024

7. **Title**: Understanding Gradient Descent on Edge of Stability in Deep Learning (Arora et al., 2022)
   - **Authors**: Arora, S., Li, Z., and Panigrahi, A.
   - **Summary**: Mathematical analysis of Edge of Stability regime where sharpness stabilizes around 2/η, showing connection to heavy-tailed gradients often observed at EoS.
   - **Year**: 2022

8. **Title**: Optimization on multifractal loss landscapes explains a diverse range of geometrical and dynamical properties of deep learning (Ly, A. & Gong, P., 2025)
   - **Authors**: Ly, A. and Gong, P.
   - **Summary**: Unifying multifractal theory explaining EoS, heavy tails, and generalization together, showing loss landscapes are multifractal and optimization dynamics inherit scale-invariant properties justifying power-law Pareto assumptions.
   - **Year**: 2025

9. **Title**: Continuous Inspection Schemes (Page, E. S., 1954)
   - **Authors**: Page, E. S.
   - **Summary**: Original CUSUM control chart paper providing optimal sequential test for detecting mean shift under iid Gaussian noise (Neyman-Pearson), foundational for change-point detection methodology.
   - **Year**: 1954

10. **Title**: High-probability Bounds for Non-Convex Stochastic Optimization with Heavy Tails (Cutkosky, A. & Mehta, H., 2021)
    - **Authors**: Cutkosky, A. and Mehta, H.
    - **Summary**: Provides convergence guarantees for gradient clipping under heavy-tailed noise, proving clipping + momentum converges with high probability when gradients have bounded p-th moments (p ∈ (1, 2]).
    - **Year**: 2021

11. **Title**: Efficient Distributed Optimization under Heavy-Tailed Noise (Lee et al., 2025)
    - **Authors**: Lee, S. H., Zaheer, M., and Li, T.
    - **Summary**: Proposes TailOPT framework with coordinate-wise clipping (Bi²Clip) for heavy-tailed gradients, assuming heavy tails are present without detection mechanism.
    - **Year**: 2025

12. **Title**: Heavy-Tailed Regularization of Weight Matrices in Deep Neural Networks (Xiao et al., 2023)
    - **Authors**: Xiao, X., Li, Z., Xie, C., and Zhou, F.
    - **Summary**: Proposes explicit regularization terms to promote heavy-tailed weight spectra, requiring monitoring to verify regularization achieves desired tail behavior.
    - **Year**: 2023

**Key Challenges**
1. **Offline-Only Analysis**: Existing heavy-tail estimation methods (Simsekli et al. 2020, Barsbey et al. 2021) require batch/offline analysis on saved gradient history, preventing real-time monitoring and mid-training prediction capabilities.

2. **Non-Stationarity Assumption Violation**: Classical Hill estimator (Hill 1975) assumes i.i.d. samples and stationarity, but deep learning training exhibits phase transitions, learning rate schedules, and batch size changes that violate this assumption.

3. **Theory-Practice Gap**: Theoretical characterizations (Jiao & Keller-Ressel 2024) provide tail-index bounds but lack practical estimation algorithms for deployment in actual training pipelines.

4. **Computational Overhead**: Real-time tail monitoring must maintain negligible overhead (<2% of training time) while achieving sufficient accuracy for practical use, requiring efficient online algorithms.

5. **Hyperparameter Sensitivity**: Existing tail estimation methods require domain expertise in Extreme Value Theory for proper hyperparameter selection (k, window size), limiting accessibility to practitioners.

6. **Robustness to Distribution Deviations**: Hill estimator is designed for Pareto-type tails; robustness to non-Pareto distributions (log-normal, Weibull) in real gradients remains unclear.

7. **Predictive Validation**: While theoretical links exist between tail-index α and generalization (Simsekli et al. 2020), empirical validation of mid-training α estimates as predictors of final performance across diverse architectures is missing.

8. **Change-Point Detection Lag**: Adaptive methods for handling non-stationarity introduce detection delays (5-20 iterations) causing transient estimation errors during regime transitions like learning rate decay.
