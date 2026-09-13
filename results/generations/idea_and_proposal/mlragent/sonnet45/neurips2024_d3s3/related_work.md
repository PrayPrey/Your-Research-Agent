1. **Title**: Light-Weight Diffusion Multiplier and Uncertainty Quantification for Fourier Neural Operators (arXiv:2508.00643)
   - **Authors**: Albert Matveev, Sanmitra Ghosh, Aamal Hussain, James-Michael Leahy, Michalis Michaelides
   - **Summary**: This paper introduces DINOZAUR, a diffusion-based neural operator parametrization that replaces the dense tensor multiplier in Fourier Neural Operators (FNOs) with a dimensionality-independent diffusion multiplier. This approach significantly reduces parameter count and memory footprint without compromising predictive performance. Additionally, by defining priors over time parameters, DINOZAUR is cast as a Bayesian neural operator, yielding spatially correlated outputs and calibrated uncertainty estimates. The method achieves competitive or superior performance across several PDE benchmarks while providing efficient uncertainty quantification.
   - **Year**: 2025

2. **Title**: Multi-Fidelity Prediction and Uncertainty Quantification with Laplace Neural Operators for Parametric Partial Differential Equations (arXiv:2502.00550)
   - **Authors**: Haoyang Zheng, Guang Lin
   - **Summary**: The authors propose Multi-Fidelity Laplace Neural Operators (MF-LNOs), which combine a low-fidelity base model with parallel linear/nonlinear high-fidelity correctors and dynamic inter-fidelity weighting. This framework exploits correlations between low- and high-fidelity datasets to achieve accurate inference of quantities of interest, even with sparse high-fidelity data. A modified replica exchange stochastic gradient Langevin algorithm is incorporated to enable effective posterior distribution estimation and uncertainty quantification. Validation across four canonical dynamical systems demonstrates significant improvements, with testing losses reduced by 40% to 80% compared to traditional approaches.
   - **Year**: 2025

3. **Title**: Surrogate Modelling and Uncertainty Quantification Based on Multi-Fidelity Deep Neural Network (arXiv:2308.01261)
   - **Authors**: Zhihui Li, Francesco Montomoli
   - **Summary**: This paper presents a new architecture of multi-fidelity deep neural network (MF-DNN) where a single subnetwork approximates both non-linear and linear correlations between high- and low-fidelity data simultaneously. The proposed MF-DNN autonomously learns arbitrary correlations without manual allocation of output weights. The model demonstrates excellent approximation capabilities for benchmark functions and efficiently predicts probability density distributions of quantities of interest in uncertainty quantification tasks. The approach is also applied to model the physical flow of turbine vane LS89, accurately predicting isentropic Mach number distributions.
   - **Year**: 2023

4. **Title**: A Multi-Fidelity Neural Network Surrogate Sampling Method for Uncertainty Quantification (arXiv:1909.01859)
   - **Authors**: Mohammad Motamed
   - **Summary**: The author proposes a multi-fidelity neural network surrogate sampling method for uncertainty quantification of systems described by differential equations. The method constructs a two-level neural network using low- and high-fidelity data to accelerate the creation of a high-fidelity surrogate model. This surrogate is then embedded in a Monte Carlo sampling framework. Numerical examples demonstrate that the approach achieves significant computational cost savings while maintaining accuracy within small tolerances.
   - **Year**: 2019

5. **Title**: The Cost-Accuracy Trade-Off in Operator Learning with Neural Networks (arXiv:2203.13181)
   - **Authors**: Maarten V. de Hoop, Daniel Zhengyu Huang, Elizabeth Qian, Andrew M. Stuart
   - **Summary**: This study provides a numerical analysis of various neural network architectures for operator approximation across problems arising from PDE models in continuum mechanics. The authors assess the cost required to achieve a given level of accuracy, offering insights into the relative merits of different approaches to surrogate modeling for PDEs.
   - **Year**: 2022

6. **Title**: Neural Importance Sampling for Rapid and Reliable Gravitational-Wave Inference (arXiv:2210.05686)
   - **Authors**: Maximilian Dax, Stephen R. Green, Jonathan Gair, Michael Pürrer, Jonas Wildberger, Jakob H. Macke, Alessandra Buonanno, Bernhard Schölkopf
   - **Summary**: The authors combine amortized neural posterior estimation with importance sampling for fast and accurate gravitational-wave inference. By generating a rapid proposal for the Bayesian posterior using neural networks and attaching importance weights based on the underlying likelihood and prior, the method provides corrected posteriors free from network inaccuracies, performance diagnostics, and unbiased estimates of the Bayesian evidence. The approach demonstrates significant improvements in computational efficiency and accuracy over standard samplers.
   - **Year**: 2022

7. **Title**: Unmatched Uncertainty Mitigation Through Neural Network Supported Model Predictive Control (arXiv:2304.11315)
   - **Authors**: Mateus V. Gasparino, Prabhat K. Mishra, Girish Chowdhary
   - **Summary**: This paper presents a deep learning-based model predictive control (MPC) algorithm for systems with unmatched and bounded state-action dependent uncertainties of unknown structure. A deep neural network (DNN) serves as an oracle in the optimization problem of learning-based MPC to estimate unmatched uncertainties. The approach employs a dual-timescale adaptation mechanism, updating the weights of the last layer of the neural network in real time while training the inner layers on a slower timescale using online-collected data. Numerical experiments validate the method's real-time implementability and theoretical guarantees.
   - **Year**: 2023

8. **Title**: Multi-Fidelity Surrogate Modeling for Temperature Field Prediction in Additive Manufacturing (arXiv:2301.06674)
   - **Authors**: [Authors not specified]
   - **Summary**: This work introduces a deep multi-fidelity model with a pre-train and fine-tune paradigm for temperature field prediction in additive manufacturing. The model leverages low-fidelity data to pre-train a backbone network, which is then fine-tuned using high-fidelity data. This approach effectively captures the complex relationships between process parameters and temperature fields, achieving accurate predictions while reducing computational costs.
   - **Year**: 2023

**Key Challenges**:

1. **Balancing Accuracy and Computational Cost**: Developing surrogate models that maintain high accuracy while significantly reducing computational expenses remains a primary challenge.

2. **Effective Uncertainty Quantification**: Ensuring that surrogate models provide reliable and calibrated uncertainty estimates is crucial for their applicability in safety-critical applications.

3. **Adaptive Fidelity Selection**: Creating frameworks that can dynamically select between different fidelity levels based on uncertainty estimates to optimize resource allocation is complex and requires sophisticated decision-making algorithms.

4. **Data Efficiency**: Surrogate models often require substantial amounts of high-fidelity training data, which can be expensive or impractical to obtain. Developing methods that can learn effectively from limited high-fidelity data is essential.

5. **Generalization Across Domains**: Ensuring that surrogate models trained on specific datasets or problem domains can generalize well to other related but unseen scenarios is a significant hurdle in the development of robust and versatile models. 