1. **Title**: A Function Centric Perspective On Flat and Sharp Minima (arXiv:2510.12451)
   - **Authors**: Israel Mason-Williams, Gabryel Mason-Williams, Helen Yannakoudakis
   - **Summary**: This paper challenges the traditional view that flat minima correlate with better generalization. Through extensive empirical studies, the authors demonstrate that sharp minima can emerge when models are regularized and that these sharp minima can coincide with improved generalization, calibration, robustness, and functional consistency.
   - **Year**: 2025

2. **Title**: Flatness After All? (arXiv:2506.17809)
   - **Authors**: Neta Shoham, Liron Mor-Yosef, Haim Avron
   - **Summary**: The authors propose that generalization can be assessed by measuring flatness using a soft rank measure of the Hessian. They establish a connection between this measure and the Takeuchi Information Criterion, providing reliable estimates of generalization gaps for models that are not overly confident.
   - **Year**: 2025

3. **Title**: Gradient Norm Aware Minimization Seeks First-Order Flatness and Improves Generalization (arXiv:2303.03108)
   - **Authors**: Xingxuan Zhang, Renzhe Xu, Han Yu, Hao Zou, Peng Cui
   - **Summary**: This work introduces first-order flatness, focusing on the maximal gradient norm within a perturbation radius, and presents Gradient norm Aware Minimization (GAM) to seek minima with uniformly small curvature across all directions. Experimental results show that GAM improves generalization across various datasets and networks.
   - **Year**: 2023

4. **Title**: Flatness-Aware Stochastic Gradient Langevin Dynamics (arXiv:2510.02174)
   - **Authors**: Stefano Bruno, Youngsik Hwang, Jaehyeon An, Sotirios Sabanis, Dong-Young Lim
   - **Summary**: The authors introduce Flatness-Aware Stochastic Gradient Langevin Dynamics (fSGLD), designed to efficiently seek flat minima in high-dimensional nonconvex optimization problems. They provide theoretical explanations for the benefits of random weight perturbation and demonstrate superior generalization and robustness in various tasks.
   - **Year**: 2025

5. **Title**: Deep Linear Networks for Regression Are Implicitly Regularized Towards Flat Minima (arXiv:2405.13456)
   - **Authors**: Pierre Marion, Lénaïc Chizat
   - **Summary**: This paper studies the sharpness of deep linear networks for univariate regression, showing that minimizers can have arbitrarily large sharpness but not an arbitrarily small one. The authors demonstrate an implicit regularization towards flat minima, with sharpness of the minimizer bounded by a constant times the lower bound.
   - **Year**: 2024

6. **Title**: Sharp Minima Can Generalize: A Loss Landscape Perspective On Data (arXiv:2511.04808)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper finds that sharp minima discovered with large datasets can generalize well despite their small basin volumes. It employs Monte Carlo basin volume estimation and rigorous empirical evaluation to contrast sharp minima with flat minima, revealing a power-law decay in basin volume with increasing data.
   - **Year**: 2025

7. **Title**: Stochastic Gradient Descent Introduces an Effective Landscape-Dependent Regularization Favoring Flat Solutions (DOI: 10.1103/physrevlett.130.237101)
   - **Authors**: Ning Yang, Chao Tang, Yuhai Tu
   - **Summary**: The authors construct a simple model to show that the noise introduced by stochastic gradient descent (SGD) serves as an effective regularization for finding flat solutions. They demonstrate that SGD noise introduces an additional effective loss term that decreases with flatness, breaking degeneracy and favoring flat minima.
   - **Year**: 2023

8. **Title**: Flat Minima and Generalization in Deep Learning: A Case Study in Low Rank Matrix Recovery
   - **Authors**: [Authors not specified]
   - **Summary**: Focusing on overparameterized nonlinear models arising in low-rank matrix recovery, this work shows that flat minima, measured by the trace of the Hessian, exactly recover the ground truth under standard statistical assumptions. The results suggest a theoretical basis for favoring methods that bias iterates towards flat solutions.
   - **Year**: [Year not specified]

9. **Title**: Sharp Minima Can Generalize For Deep Nets
   - **Authors**: Laurent Dinh, Razvan Pascanu, Samy Bengio, Yoshua Bengio
   - **Summary**: This paper argues that most notions of flatness are problematic for deep models and cannot be directly applied to explain generalization. The authors exploit the geometry of parameter space induced by inherent symmetries in deep networks to build equivalent models corresponding to arbitrarily sharper minima, challenging the traditional view that flatness correlates with better generalization.
   - **Year**: 2017

10. **Title**: A Reparameterization-Invariant Flatness Measure for Deep Neural Networks (arXiv:1912.00058)
    - **Authors**: Henning Petzka, Linara Adilova, Michael Kamp, Cristian Sminchisescu
    - **Summary**: The authors propose a modification of existing flatness measures that results in invariance to reparameterization, addressing the issue that existing measures cannot be directly related to generalization due to a lack of invariance with respect to reparameterizations.
    - **Year**: 2019

**Key Challenges:**

1. **Scale Sensitivity of Flatness Measures**: Traditional flatness metrics are sensitive to model scale and can be manipulated without affecting generalization, leading to inconsistencies in their predictive power.

2. **Sharp Minima with Good Generalization**: Empirical observations show that large models can converge to sharp minima yet generalize well, contradicting the conventional belief that flat minima are necessary for good generalization.

3. **Impact of Regularization Techniques**: Regularization methods like weight decay and data augmentation can lead to sharper minima while improving generalization, challenging the direct correlation between flatness and generalization.

4. **Batch Size Variability**: Models trained with different batch sizes exhibit similar generalization despite vastly different flatness characteristics, indicating that flatness may not be a reliable predictor of generalization across varying training conditions.

5. **Reparameterization Invariance**: Existing flatness measures lack invariance to reparameterization, making it difficult to relate them directly to generalization and necessitating the development of reparameterization-invariant metrics. 