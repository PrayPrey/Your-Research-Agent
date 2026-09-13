1. **Title**: Hybrid Machine Learning Based Scale Bridging Framework for Permeability Prediction of Fibrous Structures (arXiv:2502.05044)
   - **Authors**: Denis Korolev, Tim Schmidt, Dinesh K. Natarajan, Stefano Cassola, David May, Miro Duhovic, Michael Hintermüller
   - **Summary**: This study introduces a hybrid machine learning-based framework to predict the permeability of fibrous textile structures. It evaluates various scale-bridging methodologies that combine traditional surrogate models and physics-informed neural networks (PINNs) with numerical solvers, enabling accurate permeability predictions across micro- and mesoscales. The proposed approach balances computational cost and prediction reliability, advancing permeability modeling in fibrous composite manufacturing.
   - **Year**: 2025

2. **Title**: Likelihood Training of Cascaded Diffusion Models via Hierarchical Volume-preserving Maps (arXiv:2501.06999)
   - **Authors**: Henry Li, Ronen Basri, Yuval Kluger
   - **Summary**: This paper addresses the intractability of likelihood functions in probabilistic multi-scale models by modeling the diffusion process on latent spaces induced by hierarchical volume-preserving maps, such as Laplacian pyramids and wavelet transforms. This approach allows the likelihood function to be directly expressed as a joint likelihood over scales, leading to significant improvements in likelihood modeling benchmarks, including density estimation, lossless compression, and out-of-distribution detection.
   - **Year**: 2025

3. **Title**: Learning Joint Latent Space EBM Prior Model for Multi-layer Generator (arXiv:2306.06323)
   - **Authors**: Jiali Cui, Ying Nian Wu, Tian Han
   - **Summary**: This paper studies the problem of learning multi-layer generator models by proposing an energy-based model (EBM) on the joint latent space over all layers of latent variables. The approach captures intra-layer contextual relations through layer-wise energy terms and jointly corrects latent variables across different layers. A joint training scheme via maximum likelihood estimation is developed, involving Markov Chain Monte Carlo sampling for both prior and posterior distributions. The experiments demonstrate the model's expressiveness in generating high-quality images and capturing hierarchical features for better outlier detection.
   - **Year**: 2023

4. **Title**: A Multiscale Graph Convolutional Network Using Hierarchical Clustering (arXiv:2006.12542)
   - **Authors**: Alex Lipov, Pietro Liò
   - **Summary**: This work explores a novel architecture that exploits hierarchical topology through a multiscale decomposition. A dendrogram produced by a Girvan-Newman hierarchical clustering algorithm is segmented and fed through graph convolutional layers, allowing the architecture to learn multiple scale latent space representations of the network, from fine to coarse-grained. The architecture is tested on a benchmark citation network, demonstrating competitive performance.
   - **Year**: 2020

5. **Title**: Matryoshka Diffusion Models
   - **Authors**: Not specified
   - **Summary**: This technical report introduces Matryoshka Diffusion Models (MDM), a new class of diffusion models trained end-to-end in high-resolution space while exploiting the hierarchical structure of data formation. MDM generalizes standard diffusion models in the extended space and proposes specialized nested architectures and training procedures. The approach focuses on efficient network design and shifted noise schedules to adapt to high-resolution spaces, aiming to improve generation quality without relying on separate models.
   - **Year**: 2023

6. **Title**: MGNNI: Multiscale Graph Neural Networks with Implicit Layers
   - **Authors**: Not specified
   - **Summary**: This paper proposes multiscale graph neural networks with implicit layers (MGNNI) to expand the effective range of information propagation and capture multiscale information on graphs. MGNNI contains multiple propagation components with different scales and learns a trainable aggregation mechanism for mixing latent information at various scales. The approach aims to capture dependencies within a longer range over iterations and combines information at different scales of the graph.
   - **Year**: 2023

7. **Title**: LSCALE: Latent Space Clustering-Based Active Learning
   - **Authors**: Not specified
   - **Summary**: This paper introduces LSCALE, a latent space clustering-based active learning framework for node classification. The framework designs a suitable active learning latent space with two important properties: low label requirements and informative distances. LSCALE uses an unsupervised learning method to learn node representations based on graphs and node attributes, and applies a linear distance-based classifier to generate output predictions. Clustering is performed on the latent space using the distances to select informative nodes, with an incremental clustering method to ensure diversity in the selection process.
   - **Year**: 2023

**Key Challenges**:

1. **Automated Identification of Coarse-Grained Variables**: Developing methods to automatically identify relevant coarse-grained variables without domain expertise remains a significant challenge.

2. **Designing Scale-Bridging Functions**: Creating effective and generalizable scale-bridging functions that can accurately map dynamics between different scales is complex and often requires manual intervention.

3. **Preserving Conservation Laws**: Ensuring that learned models adhere to fundamental conservation laws during scale transitions is critical but difficult to enforce in machine learning frameworks.

4. **Adaptive Computation Across Scales**: Developing adaptive computation strategies that efficiently determine which scales require fine-grained computation versus coarse approximations based on local state complexity is an open problem.

5. **Generalization Across Scientific Domains**: Creating domain-agnostic tools that can be universally applied across various scientific fields without extensive customization poses a significant challenge. 