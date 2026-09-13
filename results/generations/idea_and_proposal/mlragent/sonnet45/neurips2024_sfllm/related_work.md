1. **Title**: Wasserstein-regularized Conformal Prediction under General Distribution Shift (arXiv:2501.13430)
   - **Authors**: Rui Xu, Chao Chen, Yue Sun, Parvathinathan Venkitasubramaniam, Sihong Xie
   - **Summary**: This paper introduces a conformal prediction method that remains valid under general distribution shifts by utilizing a Wasserstein distance-based upper bound on the coverage gap. The authors propose an algorithm combining importance weighting and regularized representation learning to minimize this bound, achieving a balance between accuracy and efficiency. Experiments demonstrate reduced coverage gaps and smaller prediction sets compared to worst-case approaches.
   - **Year**: 2025

2. **Title**: Conformal Prediction under Lévy-Prokhorov Distribution Shifts: Robustness to Local and Global Perturbations (arXiv:2502.14105)
   - **Authors**: Liviu Aolaritei, Michael I. Jordan, Youssef Marzouk, Zheyu Oliver Wang, Julie Zhu
   - **Summary**: The authors address the robustness of conformal prediction under distribution shifts by modeling these shifts using Lévy-Prokhorov ambiguity sets, which capture both local and global perturbations. They develop robust conformal prediction intervals that maintain validity under such shifts, linking ambiguity set parameters to interval width and confidence levels. Experimental results on real-world datasets validate the effectiveness of the proposed approach.
   - **Year**: 2025

3. **Title**: Neural Network-Based Change Point Detection for Large-Scale Time-Evolving Data (arXiv:2503.09541)
   - **Authors**: Jialiang Geng, George Michailidis
   - **Summary**: This paper presents a method for detecting change points in multivariate time-evolving data using feed-forward neural networks. The proposed strategy involves training the network over a specified window and calibrating its test error function over another window. The test error function is then used over a moving window to identify change points. The method is shown to consistently estimate the number and locations of change points under temporal dependence.
   - **Year**: 2025

4. **Title**: Conformal Prediction Adaptive to Unknown Subpopulation Shifts (arXiv:2506.05583)
   - **Authors**: Nien-Shao Wang, Duygu Nur Yaldiz, Yavuz Faruk Bakman, Sai Praneeth Karimireddy
   - **Summary**: The authors propose methods to adapt conformal prediction to subpopulation shifts, ensuring valid coverage without explicit knowledge of subpopulation structures. Their algorithms scale to high-dimensional settings and perform effectively in realistic machine learning tasks. Experiments on vision and language benchmarks demonstrate that the methods reliably maintain coverage and control risk where standard conformal prediction fails.
   - **Year**: 2025

5. **Title**: Multi-Source Conformal Inference Under Distribution Shift
   - **Authors**: Yi Liu, Alexander Levis, Sharon-Lise Normand, Larry Han
   - **Summary**: This paper addresses the challenge of obtaining distribution-free prediction intervals for a target population by leveraging multiple potentially biased data sources. The authors derive efficient influence functions for quantiles of unobserved outcomes and propose a data-adaptive strategy to upweight informative data sources for efficiency gain and downweight non-informative sources for bias reduction. The methodology is validated through synthetic experiments and real data applications.
   - **Year**: 2024

6. **Title**: Conformal Prediction for Natural Language Processing: A Survey
   - **Authors**: Margarida Campos
   - **Summary**: This survey provides a comprehensive overview of conformal prediction methods applied to natural language processing (NLP). It discusses the theoretical foundations, extensions, and applications of conformal predictors in NLP tasks, highlighting challenges and future directions in the field.
   - **Year**: 2024

7. **Title**: Divide and Conquer Dynamic Programming: An Almost Linear Time Change Point Detection Methodology in High Dimensions (arXiv:2301.10942)
   - **Authors**: Wanshan Li, Daren Wang, Alessandro Rinaldo
   - **Summary**: The authors develop a computationally efficient framework called Divide and Conquer Dynamic Programming (DCDP) for localizing change points in high-dimensional time series data. DCDP applies to various statistical models and achieves almost linear computational complexity. The method consistently estimates change points with sharp rates while incurring significantly smaller computational costs than existing algorithms.
   - **Year**: 2023

8. **Title**: Robust Mean Change Point Testing in High-Dimensional Data with Heavy Tails (arXiv:2305.18987)
   - **Authors**: Mengchu Li, Yudong Chen, Tengyao Wang, Yi Yu
   - **Summary**: This paper studies mean change point testing for high-dimensional data with heavy-tailed distributions. The authors characterize the boundary between dense and sparse regimes and propose novel testing procedures that attain optimal rates in each regime. The results quantify the impact of heavy-tailedness on the difficulty of change point testing in high-dimensional data.
   - **Year**: 2023

9. **Title**: Online Detection for Black-Box Large Language Models with Adaptive Prompt Selection
   - **Authors**: Anonymous
   - **Summary**: The authors propose an online change-point detection method for black-box large language models (LLMs). The method derives a CUSUM-type detection statistic based on entropy and the Gini coefficient of the response distribution and utilizes an adaptive prompt selection strategy to enhance detection. Evaluations demonstrate the method's ability to detect changes quickly while controlling the false alarm rate.
   - **Year**: 2025

10. **Title**: Not All Distributional Shifts Are Equal: Fine-Grained Robust Conformal Inference
    - **Authors**: Jiahao Ai, Zhimei Ren
    - **Summary**: This paper introduces a framework for uncertainty quantification of predictive models under distributional shifts, distinguishing between shifts in covariate distributions and shifts in the conditional relationship between outcome and covariates. The authors propose an algorithm that outputs valid and efficient prediction intervals in the presence of distributional shifts, applying the framework to sensitivity analysis of individual treatment effects with hidden confounding.
    - **Year**: 2024

**Key Challenges:**

1. **Assumption of Exchangeability**: Traditional conformal prediction methods rely on the assumption of exchangeability, which is often violated under distribution shifts, leading to invalid uncertainty quantification.

2. **Computational Efficiency**: Detecting distribution shifts and recalibrating models in real-time, especially in high-dimensional settings, poses significant computational challenges.

3. **Limited Knowledge of Subpopulation Structures**: Adapting conformal prediction to unknown subpopulation shifts without explicit knowledge of subpopulation structures remains a complex problem.

4. **Robustness to Heavy-Tailed Distributions**: Developing change point detection methods that are robust to heavy-tailed distributions in high-dimensional data is challenging.

5. **Balancing Coverage and Efficiency**: Ensuring valid coverage while maintaining efficient prediction intervals under various types of distribution shifts requires careful balancing and innovative methodological approaches. 