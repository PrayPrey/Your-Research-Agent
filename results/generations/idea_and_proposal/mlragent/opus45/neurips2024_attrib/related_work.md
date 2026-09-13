1. **Title**: Toward Efficient Influence Function: Dropout as a Compression Tool (arXiv:2509.15651)
   - **Authors**: Yuchen Zhang, Mohammad Mohammadi Amiri
   - **Summary**: This paper introduces a novel approach that leverages dropout as a gradient compression mechanism to compute influence functions more efficiently. The method significantly reduces computational and memory overhead during influence function computation and gradient compression, preserving critical components of data influence and enabling application to large-scale models.
   - **Year**: 2025

2. **Title**: Scalable Data Attribution via Forward-Only Test-Time Inference (arXiv:2511.19803)
   - **Authors**: Sibo Ma, Julian Nyarko
   - **Summary**: The authors propose a data attribution method that eliminates per-query backward passes by simulating each training example's parameter influence during training. This design shifts computation from inference to simulation, allowing real-time data attribution in large pretrained models with significantly lower inference costs.
   - **Year**: 2025

3. **Title**: Detecting Instruction Fine-tuning Attack on Language Models with Influence Function (arXiv:2504.09026)
   - **Authors**: Jiawei Li
   - **Summary**: This work presents an approach to detect and mitigate instruction fine-tuning attacks on language models using influence functions. By leveraging the EK-FAC approximation method, the study efficiently computes influence scores to identify and remove poisoned data points, recovering model performance to near-clean levels.
   - **Year**: 2025

4. **Title**: Fast Data Attribution for Text-to-Image Models (arXiv:2511.10721)
   - **Authors**: Sheng-Yu Wang, Aaron Hertzmann, Alexei A. Efros, Richard Zhang, Jun-Yan Zhu
   - **Summary**: The authors propose a scalable and efficient data attribution method for text-to-image models by distilling a slow, unlearning-based attribution method to a feature embedding space. This approach enables rapid retrieval of influential training images without running expensive attribution algorithms, achieving significant speedups over existing methods.
   - **Year**: 2025

5. **Title**: Studying Large Language Model Generalization with Influence Functions (arXiv:2308.03296)
   - **Authors**: Roger Grosse, Juhan Bae, Cem Anil, Nelson Elhage, Alex Tamkin, Amirhossein Tajdini, Benoit Steiner, Dustin Li, Esin Durmus, Ethan Perez, Evan Hubinger, Kamilė Lukošiūtė, Karina Nguyen, Nicholas Joseph, Sam McCandlish, Jared Kaplan, Samuel R. Bowman
   - **Summary**: This research explores the application of influence functions, using the EK-FAC approximation, to analyze the contribution of training examples in large language models. The study provides insights into the generalization patterns and limitations of these models.
   - **Year**: 2023

6. **Title**: Do Influence Functions Work on Large Language Models? (arXiv:2025.findings-emnlp.775)
   - **Authors**: Zhe Li, Wei Zhao, Yige Li, Jun Sun
   - **Summary**: The paper systematically evaluates influence functions across multiple tasks in large language models, finding that they consistently perform poorly in most settings. The study attributes this to approximation errors, uncertain convergence during fine-tuning, and the definition itself, suggesting the need for alternative approaches for identifying influential samples.
   - **Year**: 2025

7. **Title**: Influence Functions for Scalable Data Attribution in Diffusion Models (arXiv:2410.13850v5)
   - **Authors**: Bruno Mlodozeniec, Runa Eschenhagen, Juhan Bae, Alexander Immer, David Krueger, Richard Turner
   - **Summary**: This paper develops an influence functions framework to address challenges in data attribution and interpretability in diffusion models. The approach aims to provide scalable data attribution methods suitable for large-scale generative models.
   - **Year**: 2025

8. **Title**: Revisiting Data Attribution for Influence Functions (arXiv:2508.07297)
   - **Authors**: Hongbo Zhu, Angelo Cangelosi
   - **Summary**: The authors comprehensively review the data attribution capability of influence functions in deep learning, discussing theoretical foundations, recent algorithmic advances, and evaluating their effectiveness for data attribution and mislabel detection. The paper highlights current challenges and promising directions for influence functions in large-scale, real-world deep learning scenarios.
   - **Year**: 2025

9. **Title**: Understanding Impact of Human Feedback via Influence Functions (arXiv:2025.acl-long.1333)
   - **Authors**: Taywon Min, Haeone Lee, Yongchan Kwon, Kimin Lee
   - **Summary**: This study explores the use of influence functions to measure the impact of human feedback on the performance of reward models in Reinforcement Learning from Human Feedback (RLHF). The authors propose a compute-efficient approximation method, enabling the application of influence functions to large-scale preference datasets and LLM-based reward models.
   - **Year**: 2025

10. **Title**: Towards Robust Influence Functions with Flat Validation Minima (arXiv:2505.19097)
    - **Authors**: Xichen Ye, Yifan Wu, Weizhong Zhang, Cheng Jin
    - **Summary**: The paper addresses the limitations of existing influence function methods in deep neural networks, particularly when applied to noisy training data. The authors propose an approach that aims to provide robust influence estimates by focusing on flat validation minima, enhancing the reliability of influence functions in practical applications.
    - **Year**: 2025

**Key Challenges:**

1. **Computational Complexity**: Traditional influence function methods are computationally intensive, making them impractical for large-scale models and datasets.

2. **Approximation Errors**: Efficient computation of influence functions often relies on approximations that can introduce errors, affecting the accuracy of data attribution.

3. **Scalability**: Existing methods struggle to scale effectively with the increasing size of models and datasets, limiting their applicability in real-world scenarios.

4. **Robustness to Noisy Data**: Influence functions can be sensitive to noisy or mislabeled data, leading to unreliable attribution results.

5. **Interpretability**: Ensuring that the results of influence functions are interpretable and actionable remains a significant challenge, especially in complex models. 