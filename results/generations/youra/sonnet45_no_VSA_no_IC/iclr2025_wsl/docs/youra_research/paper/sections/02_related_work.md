# 2. Related Work

Our work builds on three research directions: weight space learning architectures (NFN, UNF, DWSNets), model editing via task arithmetic, and model zoos for representation learning. We position our hierarchical VAE as the first method enabling cross-architecture weight space learning on heterogeneous collections.

## 2.1 Weight Space Learning

**Permutation Equivariance for Neural Networks.** Neural Functional Networks (NFN; Zhou et al., 2023) introduce permutation equivariant layers for processing MLP and CNN weights. NFN leverages neuron permutation symmetries — the fact that reordering neurons within a hidden layer does not change network function — to design sample-efficient architectures. NFN layers (NPLinear, NPPool) preserve this symmetry via group-theoretic constraints derived from Schur's lemma. This approach achieves strong performance on model property prediction tasks (architecture type, training dataset) but is limited to homogeneous model collections where all networks share the same architecture family.

Universal Neural Functionals (UNF; Zhou et al., 2024) generalize NFN to *any* single architecture by automatically constructing equivariant layers for RNNs, Transformers, and arbitrary computational graphs. UNF handles recurrent connections and residual blocks that NFN cannot process. However, UNF still operates on homogeneous collections — all models must use the same architecture. Extending UNF to heterogeneous zoos (mixing CNNs, Transformers, RNNs) requires training separate encoders per architecture, losing the ability to compare across families.

Deep Weight Space Networks (DWSNets; Navon et al., 2023) study equivariant architectures for *deep* weight spaces (e.g., processing weights of Implicit Neural Representations or NeRFs). DWSNets use block-structured layers respecting weight tensor hierarchies. While DWSNets handle network editing tasks (modifying INR weights), they focus on homogeneous INR collections and do not address cross-architecture generalization.

**Our Contribution:** We extend weight space learning to heterogeneous zoos via hierarchical composition. Level 1 uses architecture-specific NFN encoders (preserving local equivariance), Level 2 sacrifices neuron-level symmetries via permutation-invariant pooling (exposing global structure), and Level 3 learns relational correspondences across architectures via Transformer self-attention. This design enables cross-architecture comparison without hand-designed alignment rules.

## 2.2 Task Arithmetic and Model Editing

**Task Vectors.** Ilharco et al. (2022) demonstrate that fine-tuning directions in weight space (θ_finetuned - θ_pretrained) encode task-specific information. These "task vectors" can be arithmetically combined: adding task vectors merges capabilities, negating task vectors removes skills, and scaling task vectors controls task strength. Task arithmetic enables multi-task model construction, unlearning, and controlled forgetting. However, task arithmetic fundamentally requires a shared base model — all task vectors must originate from the same pretrained checkpoint (e.g., CLIP). This limitation prevents applying task arithmetic to heterogeneous model zoos where models are trained from scratch with different architectures.

**Tangent Space Linearization.** Ortiz-Jiménez et al. (2023) improve task arithmetic by linearizing models in the tangent space (first-order Taylor expansion around pretrained weights). Tangent space task vectors exhibit better disentanglement (task-specific directions are less entangled), leading to improved multi-task performance. Like standard task arithmetic, tangent space methods require shared base models.

**Model Merging and Model Soups.** Recent work explores merging independently trained models without shared bases. Wortsman et al. (2022) show that averaging weights from models trained with different hyperparameters (model soups) improves robustness and accuracy. Personalized Soups (2023) extend this to multi-objective RL via weighted averaging. However, model soup methods typically merge models with *identical architectures* (only hyperparameters vary). Cross-architecture merging remains an open challenge.

**Our Contribution:** We enable cross-architecture transfer without shared base models by discovering task-invariant structure in weight distributions. Our hierarchical VAE learns task vectors that generalize across architectures (CNN-to-ResNet transfer), demonstrating that task constraints dominate computational primitive variance at coarse-grained scale.

## 2.3 Model Zoos and Representation Learning

**Model Zoo Datasets.** ModelZooDataset (NeurIPS 2022 Dataset Track) provides large-scale collections of neural networks for weight space learning research. The dataset contains diverse populations trained on vision tasks (CIFAR-10, ImageNet) with varying architectures and hyperparameters. ModelZooDataset enables training meta-models that predict model properties (generalization performance, training data) from weights.

SANE (Schürholt et al., 2024) introduces sequential weight processing for scalable model zoo learning. SANE treats large models as token sequences (processing weight subsets sequentially), enabling self-supervised pretraining on model zoos. SANE extends ModelZooDataset to inhomogeneous populations (mixing architectures), but their cross-architecture alignment mechanism remains incomplete — SANE processes different architectures separately, lacking unified embedding space.

Phase Transitions Model Zoo (Schürholt et al., 2025) systematically covers loss landscape phases (lazy regime, feature learning, kernel regime) across computer vision, NLP, and scientific ML tasks. This controlled diversity enables studying how training phase affects weight space representations.

**Our Contribution:** We leverage heterogeneous model zoo datasets (ModelZooDataset + SANE) to demonstrate cross-architecture task clustering. Our coverage audit (Section 4.1) validates that real model zoos contain sufficient architecture-task diversity (72.2% of cells with ≥30 models) for statistical validity. Unlike SANE, our hierarchical VAE embeds all architectures into a unified latent space.

## 2.4 Equivariant Graph Neural Networks (Geometric Deep Learning)

E(3)-equivariant GNNs (Batzner et al., 2021; Satorras et al., 2021) achieve state-of-the-art performance on molecular property prediction by preserving 3D rotation and translation symmetries. NequIP (Batzner et al., 2021) uses tensor field networks to construct E(3)-equivariant message passing layers for interatomic potentials. While E(3)-GNNs operate on geometric data (atomic coordinates), the underlying principle — preserving symmetries to improve sample efficiency — directly inspires our hierarchical design. Level 1 NFN encoders preserve neuron permutation symmetries (analogous to E(3) rotational symmetry), while Level 2 pooling sacrifices symmetries for cross-domain generalization (analogous to invariant molecular fingerprints).

## 2.5 Positioning Our Work

Our hierarchical VAE occupies a unique position in the weight space learning landscape:

| Method | Architectures Handled | Shared Base Required | Equivariance Preserved | Cross-Architecture Alignment |
|--------|----------------------|----------------------|------------------------|------------------------------|
| NFN (Zhou 2023) | MLP, CNN (single family) | No | Yes (neuron permutation) | No |
| UNF (Zhou 2024) | Any (single architecture) | No | Yes (automatic construction) | No |
| DWSNets (Navon 2023) | Deep weight spaces (INRs) | No | Yes (block-structured) | No |
| Task Arithmetic (Ilharco 2022) | Any | **Yes** (same pretrained base) | No | N/A (same architecture) |
| SANE (Schürholt 2024) | Heterogeneous (separate processing) | No | No | Incomplete |
| **Ours (Hierarchical VAE)** | **Heterogeneous (unified embedding)** | **No** | **Partial (Level 1 only)** | **Yes (learned via Level 3 Transformer)** |

Existing methods fall into two categories: (1) equivariant architectures (NFN, UNF, DWSNets) limited to homogeneous collections, or (2) heterogeneous support (SANE, task arithmetic) sacrificing equivariance or requiring shared bases. Our hierarchical VAE is the first to combine equivariant encoding (Level 1) with cross-architecture generalization (Level 2-3), enabling unified weight space embeddings for heterogeneous model zoos without shared base models.

**Key Novelty:** We frame cross-architecture weight space learning as a *hierarchical equivariance tradeoff*: preserve local symmetries at micro-level (neuron permutations within layers), sacrifice them at macro-level (cross-architecture pooling) to expose task-invariant global structure. This design is operationalized via a three-level VAE where each level addresses a specific sub-problem: Level 1 handles within-architecture equivariance (reusing NFN/UNF theory), Level 2 handles cross-architecture compatibility (permutation-invariant pooling), and Level 3 handles relational discovery (Transformer self-attention learns correspondence rules, e.g., CNN conv ≈ Transformer MLP).

This positioning distinguishes our work from concurrent developments in model merging (which focus on same-architecture averaging) and weight space augmentation (which improve NFN/UNF generalization but do not address heterogeneity). Our validation demonstrates that this hierarchical design successfully extracts task-invariant structure: same-task different-architecture models cluster with large effect size (Cohen's d=1.45), confirming that task constraints dominate architectural variance at layer-summary granularity.
