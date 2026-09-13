```
1. **Title**: $\mathbf{Li_2}$: A Framework on Dynamics of Feature Emergence and Delayed Generalization (arXiv:2509.21519)
   - **Authors**: Yuandong Tian
   - **Summary**: This paper introduces the $\mathbf{Li_2}$ framework, which delineates three stages in the grokking behavior of two-layer nonlinear networks: (I) Lazy learning, (II) Independent feature learning, and (III) Interactive feature learning. The study provides insights into the roles of hyperparameters like weight decay and learning rate in grokking, offering provable scaling laws for memorization and generalization.
   - **Year**: 2025

2. **Title**: GrokAlign: Geometric Characterisation and Acceleration of Grokking (arXiv:2506.12284)
   - **Authors**: Thomas Walker, Ahmed Imtiaz Humayun, Randall Balestriero, Richard Baraniuk
   - **Summary**: The authors propose GrokAlign, a method that aligns a network's Jacobians with training data to ensure grokking under a low-rank Jacobian assumption. They demonstrate that Jacobian regularization can induce grokking more efficiently than traditional regularizers like weight decay.
   - **Year**: 2025

3. **Title**: The Geometry of Grokking: Norm Minimization on the Zero-Loss Manifold (arXiv:2511.01938)
   - **Authors**: Tiberiu Musat
   - **Summary**: This work interprets post-memorization learning as constrained optimization, where gradient descent minimizes the weight norm on the zero-loss manifold. The author provides a closed-form expression for the post-memorization dynamics of the first layer in a two-layer network, reproducing the delayed generalization characteristic of grokking.
   - **Year**: 2025

4. **Title**: A Rationale from Frequency Perspective for Grokking in Training Neural Network (arXiv:2405.17479)
   - **Authors**: Zhangchen Zhou, Yaoyu Zhang, Zhi-Qin John Xu
   - **Summary**: This paper offers a frequency-based explanation for grokking, suggesting that networks initially learn less salient frequency components present in the test data. The authors observe this phenomenon across both synthetic and real datasets, providing a novel viewpoint on grokking through frequency dynamics during training.
   - **Year**: 2024

5. **Title**: Delays in Generalization Match Delayed Changes in Representational Geometry
   - **Authors**: Xingyu Zheng, Kyle Daruwalla, Ari S Benjamin, David Klindt
   - **Summary**: The authors present an empirical study on image classification tasks, demonstrating that grokking coincides with a rapid increase in manifold capacity and improved effective geometry metrics. This suggests that changes in representational geometry are closely linked to delayed generalization.
   - **Year**: 2024

6. **Title**: Grokking as the Transition from Lazy to Rich Training Dynamics
   - **Authors**: Tanishq Kumar, Blake Bordelon, Samuel J. Gershman, Cengiz Pehlevan
   - **Summary**: This study proposes that grokking arises due to a transition from lazy training dynamics to a rich, feature-learning regime. The authors identify key determinants of grokking, including the rate of feature learning and the alignment of initial features with the target function.
   - **Year**: 2024

7. **Title**: Emergence in Non-Neural Models: Grokking Modular Arithmetic via Average Gradient Outer Product
   - **Authors**: Neil Rohit Mallinar, Daniel Beaglehole, Libin Zhu, Adityanarayanan Radhakrishnan, Parthe Pandit, Mikhail Belkin
   - **Summary**: This work demonstrates that grokking is not exclusive to neural networks or gradient descent-based optimization. The authors show that grokking occurs in learning modular arithmetic with Recursive Feature Machines, highlighting the broader applicability of the phenomenon.
   - **Year**: 2025

8. **Title**: Complexity Dynamics of Grokking
   - **Authors**: [Authors not specified]
   - **Summary**: The paper investigates generalization through the lens of compression, introducing a new measure of intrinsic complexity based on Kolmogorov complexity. Tracking this metric during training reveals a rise and fall in complexity corresponding to memorization followed by generalization, providing insights into the dynamics of grokking.
   - **Year**: 2024

9. **Title**: Towards Understanding Grokking: An Effective Theory of Representation Learning
   - **Authors**: Ziming Liu, Michaud, E. J., Tegmark, M.
   - **Summary**: This study presents both microscopic and macroscopic analyses of grokking, identifying four learning phases: comprehension, grokking, memorization, and confusion. The authors propose an effective theory to predict when generalization occurs based on structured representations.
   - **Year**: 2022

10. **Title**: Grokking in Neural Networks: Effective Representation
    - **Authors**: [Authors not specified]
    - **Summary**: The paper identifies four distinct learning phases, highlighting a 'Goldilocks zone' where structured representations enable delayed generalization. It employs phase diagrams and critical point analysis to demonstrate how hyperparameter tuning steers models between memorization and confusion.
    - **Year**: 2022
```

**Key Challenges:**

1. **Lack of Unified Theoretical Framework**: Despite various studies, there is no comprehensive theory that explains the precise conditions and mechanisms leading to grokking.

2. **Dependence on Hyperparameters**: Grokking is sensitive to hyperparameters like weight decay, learning rate, and initialization, making it challenging to predict and control.

3. **Representation Dynamics Understanding**: The transition from memorization to generalization involves complex changes in internal representations, which are not yet fully understood.

4. **Task and Architecture Specificity**: Grokking behavior varies across different tasks and network architectures, complicating the development of generalizable insights.

5. **Computational Cost**: Prolonged training required to observe grokking is computationally expensive, limiting the feasibility of extensive empirical studies.
``` 