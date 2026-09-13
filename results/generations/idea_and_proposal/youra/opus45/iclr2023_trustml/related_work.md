## Related Work

**Related Papers**
1. **Title**: Smooth Tchebycheff Scalarization for Multi-Objective Optimization (arXiv:2402.19078)
   - **Authors**: Lin et al.
   - **Summary**: Proposes a lightweight gradient-based Pareto navigation method that achieves O(1) overhead for multi-objective optimization.
   - **Year**: 2024

2. **Title**: FairTrade: Achieving Pareto-Optimal Trade-Offs between Balanced Accuracy and Fairness in Federated Learning
   - **Authors**: Badar et al.
   - **Summary**: Demonstrates that gradient-based multi-objective optimization is feasible for balancing fairness and accuracy in federated learning settings.
   - **Year**: 2024

3. **Title**: A Closer Look at the Calibration of Differentially Private Learners (arXiv:2210.08248)
   - **Authors**: Zhang, Li, Sen, Roukos, Hashimoto
   - **Summary**: Investigates how DP-SGD causes miscalibration in differentially private models and shows that post-hoc calibration methods are effective remedies.
   - **Year**: 2022

4. **Title**: pytorch/opacus
   - **Authors**: Meta
   - **Summary**: Provides a production-ready implementation of DP-SGD with Fast Gradient Clipping for training differentially private models in PyTorch.
   - **Year**: 2024

5. **Title**: TrustFed: Navigating Trade-offs Between Performance, Fairness, and Privacy in FL
   - **Authors**: Badar et al.
   - **Summary**: Demonstrates that 3-objective Pareto optimization is feasible in federated learning but does not include calibration as an objective.
   - **Year**: 2024

6. **Title**: FedFDP: Fairness-Aware Federated Learning with Differential Privacy
   - **Authors**: Ling et al.
   - **Summary**: Proposes fairness-aware gradient clipping techniques that operate under differential privacy constraints in federated learning.
   - **Year**: 2024

7. **Title**: Optimizing Privacy, Utility and Efficiency in Constrained Multi-Objective FL
   - **Authors**: Kang et al.
   - **Summary**: Introduces CMOFL to address three objectives in federated learning but does not incorporate calibration or a unified gradient-based approach.
   - **Year**: 2023

8. **Title**: Differentially Private and Fair Classification via Calibrated Functional Mechanism
   - **Authors**: Ding et al.
   - **Summary**: Early work combining differential privacy with fairness in classification, highlighting the gap in integrating robustness and calibration.
   - **Year**: 2020

**Key Challenges**
1. **Calibration Under Differential Privacy**: DP-SGD training causes miscalibration in models, requiring additional post-hoc correction methods to restore reliable probability estimates.
2. **Incomplete Multi-Objective Coverage**: Existing multi-objective federated learning approaches address combinations of privacy, fairness, and utility but exclude calibration as an optimization objective.
3. **Lack of Unified Gradient-Based Approaches**: Current constrained multi-objective federated learning methods do not employ unified gradient-based optimization strategies that can simultaneously handle all trustworthiness dimensions.
4. **Robustness and Calibration Integration Gap**: Prior work on differential privacy and fairness has not adequately addressed the integration of robustness and calibration within a single framework.
