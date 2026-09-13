# Research Idea: Temporal-Causal VAE for Video Representation Learning

## Title
T-CausalVAE: Leveraging Temporal Consistency for Identifiable Causal Representation Learning in Video

## Motivation
Deep generative models excel at capturing statistical dependencies but fail to establish causal relationships, leading to spurious correlations and limited interpretability. While causal representation learning (CRL) shows promise for discovering latent causal structures, existing methods require interventional data or strong distributional assumptions rarely available in practice. Video data presents an untapped opportunity: consecutive frames naturally provide multi-view observations of shared latent causal variables, with temporal ordering offering directional constraints that could substitute for interventions.

## Main Idea
We propose T-CausalVAE, a variational autoencoder that exploits temporal structure in video for identifiable causal representation learning. The core hypothesis is that consecutive video frames share latent causal structure, and temporal ordering provides asymmetric constraints enabling causal direction recovery without interventions.

**Methodology:** The model processes frame pairs (t, t+1) through a VAE with (1) temporal consistency constraints enforcing shared latent structure across frames, and (2) NOTEARS-style differentiable DAG learning for explicit causal graph discovery.

**Evaluation:** We measure Structural Hamming Distance (SHD) against ground-truth causal graphs and Mean Correlation Coefficient (MCC) for latent recovery on synthetic video benchmarks, targeting SHD reduction ≥20% over single-frame baselines and MCC >0.7.

**Expected Impact:** T-CausalVAE would enable causal discovery from observational video data while maintaining generative capabilities for counterfactual video synthesis, advancing interpretable video understanding in domains like robotics and medical imaging.