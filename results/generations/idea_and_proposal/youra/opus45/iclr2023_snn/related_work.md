## Related Work

**Related Papers**
1. **Title**: Successive Pruning for Model Compression via Rate Distortion Theory (2021)
   - **Authors**: Isik, No, Weissman
   - **Summary**: Demonstrates that rate-distortion theory provides fundamental limits on neural network compression and shows that pruning can achieve these theoretical limits.
   - **Year**: 2021

2. **Title**: Consistent Sparse Deep Learning: Theory and Computation (2021)
   - **Authors**: Sun, Song, Liang
   - **Summary**: Establishes that sparse DNNs with O(n/log(n)) connections achieve posterior consistency and asymptotically optimal generalization bounds.
   - **Year**: 2021

3. **Title**: Norm-based Generalization Bounds for Sparse Neural Networks (NeurIPS 2023)
   - **Authors**: Galanti, Xu, Galanti, Poggio
   - **Summary**: Shows that sparsity structure enables tighter generalization bounds than standard norm-based approaches.
   - **Year**: 2023

4. **Title**: Neural Estimation of the Rate-Distortion Function (NERD) (2022)
   - **Authors**: Lei, Hassani, Saeedi Bidokhti
   - **Summary**: Demonstrates the computational tractability of rate-distortion estimation for high-dimensional neural data.
   - **Year**: 2022

5. **Title**: The Lottery Ticket Hypothesis (2018)
   - **Authors**: Frankle, Carlin
   - **Summary**: Establishes the existence of trainable sparse subnetworks through Iterative Magnitude Pruning (IMP), serving as a primary baseline for sparse network research.
   - **Year**: 2018

6. **Title**: Linear Mode Connectivity and the Lottery Ticket Hypothesis (2019)
   - **Authors**: Frankle et al.
   - **Summary**: Provides SGD stability analysis for pruning timing and understanding of when pruning succeeds.
   - **Year**: 2019

**Key Challenges**
1. **Lack of Constructive Bounds for Sparsity at Scale**: Theoretical guarantees for sparsity at scale remain limited to existence proofs (such as the Lottery Ticket Hypothesis) without providing constructive bounds that can guide practical implementation.
2. **Different Complexity Measures**: Existing norm-based generalization bounds use different complexity measures (Schatten norms) compared to rate-distortion approaches, making direct theoretical comparisons challenging and leaving gaps in unified understanding of sparse network generalization.
