# Research Idea: Domain-Agnostic Backdoor Detection via Geometric Manifold Analysis

## Title
NAMA: Neuron Activation Manifold Analysis for Cross-Domain Backdoor Detection Using Riemannian Geometry and Persistent Homology

## Motivation
Current backdoor defenses are domain-specific—separate toolkits exist for computer vision, NLP, and federated learning—creating fragmented security workflows and limiting cross-domain robustness evaluation. With widespread adoption of pre-trained models from untrusted sources, a unified detection framework is critical. Existing methods rely on domain-specific features (pixel patterns, token embeddings, gradient norms) that don't transfer across modalities. This research addresses the fundamental question: Can we detect backdoors using intrinsic geometric properties of neural networks that are independent of input representation?

## Main Idea
We hypothesize that backdoor triggers create detectable geometric distortions in neuron activation manifolds, regardless of input domain. Specifically, backdoor neurons must form activation pathways geometrically distinct from clean data to reliably trigger misclassification, manifesting as: (1) increased Riemannian curvature in trigger-affected regions, and (2) anomalous topological structures (persistent holes/clusters) detectable via persistent homology.

**Methodology**: NAMA embeds neuron activations into Riemannian manifolds using Isomap, then computes sectional curvature (via geomstats) and persistence diagrams (via Ripser). Models exceeding learned thresholds (99th percentile curvature, 95th percentile persistence from clean models) are flagged as backdoored. We test across CV (CIFAR-10+BadNets), NLP (SST-2+word triggers), and FL (MNIST+gradient poisoning) using 600 models.

**Expected Impact**: NAMA achieves TPR>0.90, FPR<0.05 with <5% variance across domains, providing the first domain-agnostic backdoor detector. This unifies security auditing workflows and enables zero-clean-data detection via synthetic inputs, advancing ML supply chain security.