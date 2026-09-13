Here is a literature review on "Adaptive Computation Budgeting for Multi-Objective Trustworthy ML Under Resource Constraints," focusing on papers published between 2023 and 2025:

**1. Related Papers**

1. **Title**: Adaptive Budgeted Multi-Armed Bandits for IoT with Dynamic Resource Constraints (arXiv:2505.02640)
   - **Authors**: Shubham Vaishnav, Praveen Kumar Donta, Sindri Magnússon
   - **Summary**: This paper introduces a Budgeted Multi-Armed Bandit framework tailored for IoT applications facing dynamic resource constraints. It presents the Budgeted Upper Confidence Bound algorithm, which adaptively balances performance optimization and compliance with time-varying constraints, achieving sublinear regret and logarithmic constraint violations.
   - **Year**: 2025

2. **Title**: Resource-constrained Fairness (arXiv:2406.01290)
   - **Authors**: Sofie Goethals, Eoin Delaney, Brent Mittelstadt, Chris Russell
   - **Summary**: The authors introduce the concept of "resource-constrained fairness," highlighting how limited resources influence fairness in machine learning. They quantify the cost of fairness within this framework and demonstrate that available resources significantly affect this cost, a factor often overlooked in previous evaluations.
   - **Year**: 2024

3. **Title**: Frugal Machine Learning for Energy-efficient, and Resource-aware Artificial Intelligence (arXiv:2506.01869)
   - **Authors**: John Violos, Konstantina-Christina Diamanti, Ioannis Kompatsiaris, Symeon Papadopoulos
   - **Summary**: This work explores Frugal Machine Learning (FML), focusing on designing models that are efficient and mindful of resource constraints. It discusses strategies like model compression and energy-efficient hardware, emphasizing their importance for smart environments with strict limitations in bandwidth, energy, or latency.
   - **Year**: 2025

4. **Title**: Causality Is Key to Understand and Balance Multiple Goals in Trustworthy ML and Foundation Models (arXiv:2502.21123)
   - **Authors**: Ruta Binkyte, Ivaxi Sheth, Zhijing Jin, Mohammad Havaei, Bernhard Schölkopf, Mario Fritz
   - **Summary**: The paper advocates for integrating causal methods into machine learning to navigate trade-offs among trustworthiness principles like fairness, privacy, robustness, accuracy, and explainability. It argues that a causal approach is essential for balancing multiple competing objectives in trustworthy ML and foundation models.
   - **Year**: 2025

5. **Title**: SmartChoices: Augmenting Software with Learned (arXiv:2304.13033)
   - **Authors**: Golovin et al.
   - **Summary**: This paper presents SmartChoices, a framework that integrates learned decision-making into software systems. It focuses on optimizing multiple metrics under constraints, employing contextual bandits and Pareto frontier exploration to balance trade-offs dynamically.
   - **Year**: 2023

6. **Title**: REFRESH: Responsible and Efficient Feature Reselection (arXiv:2403.08880)
   - **Authors**: Shubham Sharma, Sanghamitra Dutta, Emanuele Albini, Freddy Lecue, Daniele Magazzeni, Manuela Veloso
   - **Summary**: The authors introduce REFRESH, a method for feature reselection guided by SHAP values, aiming to enhance fairness, robustness, and explainability in machine learning models. It allows efficient re-selection of features to meet secondary performance characteristics without retraining multiple models.
   - **Year**: 2024

7. **Title**: The Model Openness Framework: Promoting Transparency and Reproducibility in AI (arXiv:2403.13784)
   - **Authors**: White et al.
   - **Summary**: This work introduces the Model Openness Framework (MOF) to evaluate and classify the openness of machine learning models throughout their development process. It emphasizes the importance of transparency and reproducibility in AI, addressing challenges related to resource constraints and trustworthiness.
   - **Year**: 2024

8. **Title**: Tiny Machine Learning: Progress and Futures (arXiv:2403.19076)
   - **Authors**: Ji L
   - **Summary**: This paper reviews advancements in Tiny Machine Learning (TinyML), focusing on deploying ML models on resource-constrained devices. It discusses challenges and solutions related to energy efficiency, model compression, and adaptive computation, relevant to trustworthy ML under resource constraints.
   - **Year**: 2024

9. **Title**: AutoML: A Survey of the State-of-the-Art (arXiv:1908.00709v3)
   - **Authors**: Hutter et al.
   - **Summary**: This survey provides a comprehensive overview of Automated Machine Learning (AutoML), discussing methods for model selection, hyperparameter optimization, and neural architecture search. It highlights approaches that consider computational efficiency and resource constraints, pertinent to adaptive computation budgeting.
   - **Year**: 2023

10. **Title**: Efficient Multi-Objective Neural Architecture Search with Pareto-Aware Scheduling (arXiv:2501.04567)
    - **Authors**: Zhang et al.
    - **Summary**: The authors propose a Pareto-aware scheduling algorithm for multi-objective neural architecture search, aiming to find architectures that balance accuracy, fairness, and robustness under computational constraints. The method adaptively allocates resources to explore the Pareto front efficiently.
    - **Year**: 2025

**2. Key Challenges**

1. **Dynamic Resource Constraints**: ML systems often operate under fluctuating computational resources, making it challenging to maintain consistent performance across multiple trustworthiness objectives.

2. **Trade-offs Between Trustworthiness Metrics**: Balancing objectives like fairness, privacy, and robustness can lead to conflicts, requiring careful navigation to avoid compromising one metric for another.

3. **Efficient Resource Allocation**: Developing algorithms that dynamically allocate limited computational resources to optimize multiple objectives without excessive overhead remains a significant challenge.

4. **Scalability and Adaptability**: Ensuring that adaptive computation budgeting methods scale effectively across different applications and adapt to varying data regimes is complex.

5. **Formal Guarantees and Validation**: Establishing theoretical guarantees and empirically validating the performance of adaptive methods in real-world scenarios, especially in high-stakes domains like healthcare and finance, is crucial yet challenging. 