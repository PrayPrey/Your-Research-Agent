1. **Title**: Elastic Representation: Mitigating Spurious Correlations for Group Robustness (arXiv:2502.09850)
   - **Authors**: Tao Wen, Zihan Wang, Quan Zhang, Qi Lei
   - **Summary**: This paper introduces Elastic Representation (ElRep), a method that applies Nuclear- and Frobenius-norm penalties to the final layer's representation in neural networks. ElRep aims to reduce reliance on spurious correlations by promoting feature diversity and importance, thereby enhancing group robustness without significantly affecting in-distribution performance.
   - **Year**: 2025

2. **Title**: Severing Spurious Correlations with Data Pruning (arXiv:2503.18258)
   - **Authors**: Varun Mulchandani, Jung-Eun Kim
   - **Summary**: The authors propose a data pruning technique that identifies and removes training samples containing spurious features. This method operates without prior knowledge of spurious attributes, effectively reducing the model's dependence on such correlations and improving robustness.
   - **Year**: 2025

3. **Title**: Correct-N-Contrast: A Contrastive Approach for Improving Robustness to Spurious Correlations (arXiv:2203.01517)
   - **Authors**: Michael Zhang, Nimit S. Sohoni, Hongyang R. Zhang, Chelsea Finn, Christopher Ré
   - **Summary**: This work presents Correct-N-Contrast (CNC), a contrastive learning method that identifies and pairs samples with the same class but differing spurious features. By aligning representations of these pairs, CNC reduces the model's reliance on spurious correlations, enhancing worst-group performance without requiring spurious attribute labels.
   - **Year**: 2022

4. **Title**: Avoiding Spurious Correlations via Logit Correction (arXiv:2212.01433)
   - **Authors**: Sheng Liu, Xu Zhang, Nitesh Sekhar, Yue Wu, Prateek Singhal, Carlos Fernandez-Granda
   - **Summary**: The authors introduce the Logit Correction (LC) loss, an improvement over the softmax cross-entropy loss, designed to correct sample logits. Minimizing the LC loss aligns with maximizing group-balanced accuracy, thereby mitigating the impact of spurious correlations without access to spurious attribute labels.
   - **Year**: 2022

5. **Title**: Learning Transferable Visual Models From Natural Language Supervision (arXiv:2103.00020)
   - **Authors**: Alec Radford, Jong Wook Kim, Chris Hallacy, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, Ilya Sutskever
   - **Summary**: This paper introduces CLIP, a model trained on a vast dataset of image-text pairs using natural language supervision. CLIP demonstrates strong zero-shot performance across various tasks, suggesting that large-scale language supervision can help models learn more robust and transferable visual representations, potentially reducing reliance on spurious correlations.
   - **Year**: 2021

6. **Title**: Meta-Learning with Adaptive Hyperparameters (arXiv:2011.00209)
   - **Authors**: Seungkwan Lee, Jinwoo Shin
   - **Summary**: The authors propose ALFA, a meta-learning algorithm that dynamically generates learning rates and weight decay coefficients during training. By adapting these hyperparameters per task and per step, ALFA aims to improve generalization and robustness, potentially mitigating the effects of spurious correlations.
   - **Year**: 2020

7. **Title**: Robustness Gym: Unifying the NLP Evaluation Landscape (arXiv:2101.04840)
   - **Authors**: Suchin Gururangan, Swabha Swayamdipta, Omer Levy, Roy Schwartz, Samuel R. Bowman, Noah A. Smith
   - **Summary**: Robustness Gym is a framework that consolidates various evaluation methods for natural language processing models. It provides tools to assess model performance across different scenarios, including those involving spurious correlations, facilitating the development of more robust models.
   - **Year**: 2021

8. **Title**: Statistical Mechanics and Artificial Neural Networks (arXiv:2405.10957)
   - **Authors**: [Authors not specified]
   - **Summary**: This work explores the application of statistical mechanics principles to understand the behavior of artificial neural networks. It discusses how concepts like loss landscape geometry can influence model training and generalization, providing insights into mitigating spurious correlations.
   - **Year**: 2024

9. **Title**: Exploring the Geometry and Topology of Neural Network Loss Landscapes (arXiv:2204.05133)
   - **Authors**: S. Horoi, J. Huang, B. Rieck, G. Lajoie, G. Wolf, S. Krishnaswamy
   - **Summary**: The authors investigate the geometric and topological properties of neural network loss landscapes. Their findings offer a deeper understanding of optimization dynamics, which can inform strategies to reshape loss landscapes and reduce reliance on spurious correlations.
   - **Year**: 2022

10. **Title**: Handling Spurious Correlations in Reinforcement Learning (arXiv:2401.11237)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper addresses the challenge of spurious correlations in reinforcement learning. It discusses methods to identify and mitigate these correlations, enhancing the robustness and generalization capabilities of reinforcement learning models.
    - **Year**: 2024

**Key Challenges**:

1. **Identification of Spurious Features**: Detecting spurious correlations without prior knowledge or annotations remains a significant challenge, as models may inadvertently learn and rely on these features during training.

2. **Loss Landscape Manipulation**: Effectively reshaping the loss landscape to discourage reliance on spurious correlations while promoting learning of core features requires a nuanced understanding of optimization dynamics and loss geometry.

3. **Generalization Across Domains**: Developing methods that generalize across various architectures and application domains without necessitating group labels or spurious feature annotations is complex and often context-dependent.

4. **Balancing Performance Metrics**: Ensuring that interventions to mitigate spurious correlations do not adversely affect overall model performance, especially in terms of in-distribution accuracy, poses a delicate balance.

5. **Theoretical Guarantees**: Providing robust theoretical foundations and guarantees for methods aimed at reducing reliance on spurious correlations is essential for their adoption and trustworthiness in practical applications. 