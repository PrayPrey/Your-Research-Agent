1. **Title**: Conformal Safety Shielding for Imperfect-Perception Agents (arXiv:2506.17275)
   - **Authors**: William Scarbro, Calum Imrie, Sinem Getir Yaman, Kavan Fatehi, Corina S. Pasareanu, Radu Calinescu, Ravi Mangal
   - **Summary**: This paper introduces a safety shield for autonomous agents with imperfect perception, utilizing conformal prediction to quantify uncertainty in state estimation. The shield restricts actions based on state estimates, ensuring safety despite perception errors.
   - **Year**: 2025

2. **Title**: SUPER-AD: Semantic Uncertainty-aware Planning for End-to-End Robust Autonomous Driving (arXiv:2511.22865)
   - **Authors**: Wonjeong Ryu, Seungjun Yu, Seokha Moon, Hojun Choi, Junsung Park, Jinkyu Kim, Hyunjung Shim
   - **Summary**: The authors propose an end-to-end autonomous driving framework that estimates aleatoric uncertainty in bird's-eye view space and incorporates it into planning. The method produces a dense, uncertainty-aware drivability map, enhancing trajectory planning robustness.
   - **Year**: 2025

3. **Title**: State-Dependent Conformal Perception Bounds for Neuro-Symbolic Verification of Autonomous Systems (arXiv:2502.21308)
   - **Authors**: Thomas Waite, Yuang Geng, Trevor Turnquist, Ivan Ruchkin, Radoslav Ivanov
   - **Summary**: This work presents an approach to synthesize state-dependent perception error bounds using conformal prediction, facilitating tighter safety guarantees in neuro-symbolic verification of autonomous systems.
   - **Year**: 2025

4. **Title**: SPARC: Prediction-Based Safe Control for Coupled Controllable and Uncontrollable Agents with Conformal Predictions (arXiv:2410.15660)
   - **Authors**: Shuqi Wang, Shaoyuan Li, Xiang Yin
   - **Summary**: The paper introduces SPARC, a framework ensuring safe control in environments with coupled uncontrollable agents. It leverages conformal prediction to quantify uncertainty in agent behavior prediction, integrating control barrier functions for safety guarantees.
   - **Year**: 2024

5. **Title**: ScenarioNet: Open-Source Platform for Large-Scale Traffic Scenario Simulation and Modeling (arXiv:2306.12241)
   - **Authors**: Quanyi Li, Zhenghao Peng, Lan Feng, Zhizheng Liu, Chenda Duan, Wenjie Mo, Bolei Zhou
   - **Summary**: ScenarioNet is an open-source platform that collects and simulates large-scale real-world traffic scenarios, providing a benchmark for evaluating autonomous driving systems' safety and performance in diverse conditions.
   - **Year**: 2023

6. **Title**: MetaDrive: Composing Diverse Driving Scenarios for Generalizable Reinforcement Learning (arXiv:2109.12674)
   - **Authors**: Quanyi Li, Zhenghao Peng, Lan Feng, Qihang Zhang, Zhenghai Xue, Bolei Zhou
   - **Summary**: MetaDrive is a driving simulation platform that generates diverse traffic scenarios through procedural generation and real data importing, supporting research in generalizable reinforcement learning for autonomous driving.
   - **Year**: 2023

7. **Title**: Quantifying Safety of Learning-based Self-Driving Control Using Almost-Barrier Functions (arXiv:2207.13891)
   - **Authors**: Zhizhen Qin, Tsui-Wei Weng, Sicun Gao
   - **Summary**: This study proposes methods for quantitative safety analysis of neural controllers in self-driving vehicles by synthesizing and certifying neural almost-barrier functions, providing safety guarantees in path-tracking control.
   - **Year**: 2023

**Key Challenges**:

1. **Uncertainty Quantification**: Accurately modeling and propagating uncertainty through hierarchical scene representations remains complex, impacting the reliability of autonomous driving systems.

2. **Joint Optimization Complexity**: Training perception and prediction modules end-to-end while maintaining interpretable graph structures poses significant computational and algorithmic challenges.

3. **Safety Assurance**: Implementing conformal prediction techniques to provide finite-sample coverage guarantees requires careful calibration and validation to ensure safety in high-uncertainty scenarios.

4. **Data Diversity and Generalization**: Ensuring that hierarchical scene representations generalize across diverse driving environments necessitates extensive and varied datasets, which can be resource-intensive to collect and process.

5. **Interpretability vs. Performance Trade-off**: Balancing the interpretability of hierarchical scene graphs with the performance of end-to-end learning systems is challenging, as increased complexity can lead to reduced transparency. 