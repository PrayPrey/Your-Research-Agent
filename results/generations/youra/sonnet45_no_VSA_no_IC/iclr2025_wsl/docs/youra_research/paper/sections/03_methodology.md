# 3. Methodology

We introduce a Hierarchical Variational Autoencoder (VAE) for cross-architecture weight space learning. The architecture comprises three levels: (1) architecture-specific equivariant encoders preserving neuron permutation symmetries, (2) permutation-invariant pooling exposing task-relevant layer summaries, and (3) Transformer sequence modeling discovering relational structure across architectures. We train this VAE with three-level supervision (reconstruction loss, contrastive triplet loss, task classification loss) to enforce task-based clustering in latent space.

## 3.1 Problem Formulation

Let $\mathcal{M} = \{(\theta_i, a_i, t_i)\}_{i=1}^N$ be a heterogeneous model zoo containing $N$ neural networks, where $\theta_i$ denotes the weight parameters of model $i$, $a_i \in \mathcal{A}$ denotes its architecture family (CNN, ResNet, Transformer, MLP), and $t_i \in \mathcal{T}$ denotes its training task (CIFAR-10, ImageNet, etc.).

**Goal:** Learn an encoder $f: \Theta \times \mathcal{A} \rightarrow \mathbb{R}^D$ that maps weights $\theta_i$ and architecture type $a_i$ to a $D$-dimensional latent embedding $z_i = f(\theta_i, a_i)$ such that:

1. **Task-based clustering:** Models trained on the same task cluster tightly regardless of architecture: $d(z_i, z_j) < d(z_i, z_k)$ when $t_i = t_j \neq t_k$ (where $d$ is Euclidean distance).

2. **Architecture invariance:** Task structure dominates architecture variance: Within-Cluster Sum of Squares (WCSS) for same-task different-architecture clusters is significantly lower than WCSS for random or different-task clusters.

3. **Task signal preservation:** Latent embeddings $z_i$ retain sufficient task-relevant information for zero-shot task prediction: $\arg\max_{t \in \mathcal{T}} p(t | z_i) = t_i$ with high accuracy.

**Challenge:** Standard VAE architectures are not equivariant to neuron permutations (reordering neurons changes embedding), leading to sample inefficiency and poor generalization. Conversely, fully equivariant architectures (NFN, UNF) cannot compare across architectures without hand-designed alignment rules.

**Our Approach:** Hierarchical decomposition trading local equivariance (neuron-level symmetries within architectures) for global expressivity (cross-architecture generalization).

## 3.2 Architecture Design

### 3.2.1 Level 1: Architecture-Specific Equivariant Encoders

For each architecture family $a \in \mathcal{A}$, we train a dedicated NFN encoder $g_a: \Theta_a \rightarrow \mathbb{R}^{L \times d}$ that maps raw weight tensors to neuron-level embeddings while preserving permutation equivariance. Here $L$ denotes the number of layers, and $d$ denotes the neuron embedding dimension.

**NFN Layer Design:** Following Zhou et al. (2023), we use NPLinear layers that respect neuron permutation symmetries:

$$
\text{NPLinear}(W, b) = \sigma\left( \rho(W) \cdot X + \rho(b) \right)
$$

where $W, b$ are weight matrices and biases of the target network, $\rho$ denotes permutation-equivariant operations (implemented via DeepSets-style aggregation), and $\sigma$ is a nonlinearity (ReLU).

**Architecture-Specific Encoders:** We implement four encoders corresponding to our dataset architectures:

- **CNN-small encoder:** 3-layer NFN (input: conv kernels + biases, output: $L=8$ layer embeddings)
- **CNN-large encoder:** 4-layer NFN (handles deeper CNNs with $L=12$ layers)
- **ResNet-18 encoder:** 5-layer NFN with residual block handling (processes skip connections via separate channels)
- **ResNet-34 encoder:** 6-layer NFN (extends ResNet-18 to deeper networks with $L=20$ layers)

Each encoder outputs a sequence of layer-wise embeddings $h^{(a)} = [h_1, h_2, \ldots, h_L] \in \mathbb{R}^{L \times d}$, where $h_\ell \in \mathbb{R}^d$ encodes all neurons in layer $\ell$ via permutation-invariant pooling.

**Why This Works:** NFN encoders preserve neuron permutation symmetries *within* each architecture family. For example, permuting convolutional filters within a CNN layer does not change the NFN embedding. This equivariance property enables sample-efficient learning (Zaheer et al., 2017 prove DeepSets universality for permutation-invariant functions).

### 3.2.2 Level 2: Permutation-Invariant Hierarchical Pooling

NFN outputs $h^{(a)} \in \mathbb{R}^{L \times d}$ are architecture-specific: CNN layer embeddings have different semantics than ResNet layer embeddings (e.g., CNNs lack skip connections). To enable cross-architecture comparison, we apply permutation-invariant pooling that collapses neuron-level details to layer-summary statistics.

**Pooling Operation:** For each layer $\ell$, compute mean and standard deviation of neuron embeddings:

$$
s_\ell = \text{Concat}\left( \frac{1}{|h_\ell|} \sum_{i=1}^{|h_\ell|} h_{\ell,i}, \sqrt{\frac{1}{|h_\ell|} \sum_{i=1}^{|h_\ell|} (h_{\ell,i} - \mu_\ell)^2} \right)
$$

where $h_{\ell,i}$ denotes the $i$-th neuron embedding in layer $\ell$, and $\mu_\ell$ is the layer mean. This produces a fixed-size summary $s_\ell \in \mathbb{R}^{2d}$ regardless of layer width (number of neurons).

**Hierarchical Grouping:** We group layers into semantic blocks (early features, mid-level features, high-level features) and apply a second pooling stage:

$$
s_{\text{block}} = \text{MaxPool}([s_{\ell_1}, s_{\ell_2}, \ldots, s_{\ell_k}])
$$

This hierarchical design reduces sequence length from $L$ layers to $B$ blocks ($B \ll L$), making Transformer processing (Level 3) computationally feasible for deep networks.

**Why Pooling Sacrifices Equivariance:** Mean and max pooling are permutation-*invariant* (not equivariant) — they discard neuron identities, retaining only distributional statistics. This loss of equivariance is deliberate: layer summaries $s_\ell$ are architecture-agnostic, enabling comparison between CNN convolutional layers and ResNet residual blocks despite different internal structures.

**Information Loss Trade-off:** Pooling discards fine-grained neuron-level details (e.g., specific filter patterns in CNNs). We validate that this loss is acceptable via reconstruction task accuracy (Section 5.5): if reconstruction accuracy exceeds 60%, pooling retains sufficient task-relevant information for cross-architecture clustering.

### 3.2.3 Level 3: Transformer Sequence Modeling

Pooled layer summaries $s = [s_1, s_2, \ldots, s_B] \in \mathbb{R}^{B \times 2d}$ form a variable-length sequence (different architectures have different depths $B$). We apply Transformer sequence modeling to discover relational structure across layers and architectures.

**Architecture-Type-Aware Tokenization:** Concatenate pooled summaries with learnable architecture-type embeddings:

$$
\tilde{s}_\ell = s_\ell + e_a
$$

where $e_a \in \mathbb{R}^{2d}$ is a learned embedding for architecture family $a$ (four embeddings total: CNN, ResNet, MLP, ViT). This injects architecture awareness into sequence tokens, enabling the Transformer to learn architecture-specific relational patterns.

**Transformer Encoder:** 6-layer Transformer (8 attention heads, hidden dimension $D=512$) processes token sequences:

$$
z = \text{TransformerEncoder}(\tilde{s}, \text{mask}=\text{causal})
$$

The output $z \in \mathbb{R}^{B \times D}$ is a contextualized representation where each token attends to all previous layers (causal masking enforces architectural depth hierarchy).

**Global Pooling:** Extract latent code via mean pooling over sequence:

$$
z_{\text{global}} = \frac{1}{B} \sum_{\ell=1}^B z_\ell \in \mathbb{R}^D
$$

This produces a fixed-size embedding $z_{\text{global}} \in \mathbb{R}^{512}$ suitable for downstream tasks (clustering, task prediction).

**Why Transformers for Cross-Architecture Alignment:** Self-attention mechanisms naturally discover correspondence rules between layer types. For example, attention analysis (not shown in PoC but planned) may reveal that CNN convolutional layers attend strongly to ResNet residual blocks — implying functional similarity. This learned alignment is more flexible than hand-designed correspondence rules (e.g., "layer 3 in CNN = layer 5 in ResNet").

### 3.2.4 Decoder Architecture

We use a shared MLP decoder (architecture-agnostic) to reconstruct layer summaries from latent codes:

$$
\hat{s} = \text{MLP}(z_{\text{global}}) \in \mathbb{R}^{B \times 2d}
$$

The MLP has two hidden layers (512 → 2048 → $B \times 2d$) with ReLU activations. Reconstruction loss (Mean Squared Error between $s$ and $\hat{s}$) ensures latent codes retain information about layer-level weight distributions.

**Why Shared Decoder:** Architecture-specific decoders would prevent cross-architecture comparison (different architectures would use different latent space regions). A shared decoder forces the encoder to map all architectures into a unified latent space where geometric distances reflect task similarity.

## 3.3 Training Protocol

### 3.3.1 Loss Function Design

We train the hierarchical VAE with three loss components enforcing complementary objectives:

**1. Reconstruction Loss (Preserve Layer-Level Structure):**

$$
\mathcal{L}_{\text{recon}} = \frac{1}{B} \sum_{\ell=1}^B \| s_\ell - \hat{s}_\ell \|_2^2
$$

This MSE loss ensures latent codes $z$ retain layer-summary statistics. High reconstruction accuracy indicates pooling does not lose critical task-relevant information.

**2. KL Divergence (Regularization):**

$$
\mathcal{L}_{\text{KL}} = \text{KL}\left( q(z | \theta, a) \| p(z) \right)
$$

where $q(z | \theta, a)$ is the encoder posterior (Gaussian with diagonal covariance) and $p(z) = \mathcal{N}(0, I)$ is the standard normal prior. KL divergence prevents posterior collapse and encourages smooth latent space geometry.

**3. Contrastive Triplet Loss (Enforce Task-Based Clustering):**

$$
\mathcal{L}_{\text{triplet}} = \sum_{i} \max(0, d(z_i, z_i^+) - d(z_i, z_i^-) + m)
$$

where $z_i^+$ is a same-task different-architecture anchor (positive sample), $z_i^-$ is a different-task sample (negative), $d$ is Euclidean distance, and $m=0.3$ is the margin. This loss explicitly pulls same-task embeddings together while pushing different-task embeddings apart.

**4. Task Classification Loss (Auxiliary Supervision):**

$$
\mathcal{L}_{\text{task}} = -\sum_{i} \log p(t_i | z_i)
$$

A linear classifier (512 → 9 classes for 9 tasks) predicts task labels from latent codes. This auxiliary loss provides direct supervision signal beyond triplet loss.

**Total Loss:** Weighted combination with hyperparameters $\alpha, \beta, \gamma, \delta$:

$$
\mathcal{L}_{\text{total}} = \alpha \mathcal{L}_{\text{recon}} + \beta \mathcal{L}_{\text{KL}} + \gamma \mathcal{L}_{\text{triplet}} + \delta \mathcal{L}_{\text{task}}
$$

We set $\alpha=1.0, \gamma=0.5, \delta=0.1$ and anneal $\beta$ from 1.0 to 0.1 over training (prevents posterior collapse early, then prioritizes reconstruction).

### 3.3.2 Optimization Details

- **Optimizer:** AdamW with learning rate $10^{-4}$, weight decay $10^{-5}$
- **Batch Size:** 32 models per batch (stratified sampling: 16 same-task pairs, 16 different-task pairs)
- **Beta Annealing Schedule:** $\beta(t) = 0.1 + 0.9 \cdot \exp(-t / T)$ where $T=10$ epochs
- **Gradient Clipping:** Max norm 1.0 (prevents gradient explosions in Transformer)
- **Training Duration:** 10 epochs (PoC demonstration; full-scale: 200 epochs)

### 3.3.3 Dataset Splits

- **Train:** 70% (1,484 models)
- **Validation:** 15% (318 models, for hyperparameter tuning and early stopping)
- **Test:** 15% (318 models, for final WCSS clustering evaluation)

Splits are stratified by task to ensure balanced representation in each split.

## 3.4 Evaluation Metrics

### 3.4.1 Primary Metric: Within-Cluster Sum of Squares (WCSS)

WCSS measures clustering tightness. For a cluster $C$ of latent embeddings $\{z_i\}_{i \in C}$:

$$
\text{WCSS}(C) = \sum_{i \in C} \| z_i - \mu_C \|_2^2
$$

where $\mu_C = \frac{1}{|C|} \sum_{i \in C} z_i$ is the cluster centroid.

**Hypothesis Test:** Compare WCSS for same-task different-architecture clusters vs random baseline clusters via bootstrap resampling (30 iterations):

- **Null Hypothesis (H0):** $\text{WCSS}_{\text{same-task}} \geq \text{WCSS}_{\text{random}}$ (task structure does not influence clustering)
- **Alternative Hypothesis (H1):** $\text{WCSS}_{\text{same-task}} < \text{WCSS}_{\text{random}}$ (same-task clusters tighter)

We compute two-tailed t-test p-value and Cohen's d effect size. Success criterion: $p < 0.01$ and $d > 0.5$ (medium effect).

### 3.4.2 Secondary Metric: Centered Kernel Alignment (CKA)

CKA (Kornblith et al., 2019) measures representation similarity between architecture-specific encoders. For two sets of neuron embeddings $H^{(a)}, H^{(a')} \in \mathbb{R}^{n \times d}$:

$$
\text{CKA}(H^{(a)}, H^{(a')}) = \frac{\| H^{(a)T} H^{(a')} \|_F^2}{\| H^{(a)T} H^{(a)} \|_F \cdot \| H^{(a')T} H^{(a')} \|_F}
$$

where $\| \cdot \|_F$ denotes Frobenius norm.

**Feasibility Gate:** Before expensive VAE training, validate that architecture subspaces are compatible:

- **Same-task CKA:** Median $> 0.6$ (strong similarity)
- **Different-task CKA:** Median $< 0.4$ (weak similarity)

If this gate fails (same-task CKA $< 0.5$), architecture subspaces are not metrically compatible — cross-architecture bridge is infeasible, hypothesis rejected early.

### 3.4.3 Auxiliary Metric: Reconstruction Task Accuracy

Decode task labels from reconstructed layer summaries $\hat{s}$ using a fixed linear probe (trained on validation set). Accuracy $> 60\%$ indicates pooling retains task-relevant information despite neuron-level information loss. Accuracy $< 50\%$ (near random) indicates critical information destroyed by pooling — hierarchical design fails.

## 3.5 Implementation Details

- **Framework:** PyTorch 2.0, accelerated with mixed-precision training (FP16)
- **Hardware:** CPU-only for PoC (10 epochs, 18 minutes). Full-scale: 2×V100 GPUs (200 epochs, 7 days, estimated $700 AWS p3.8xlarge)
- **Code Availability:** [To be released upon publication]
- **Reproducibility:** Fixed random seeds (42 for train/val/test split, 123 for model initialization)

This methodology establishes a rigorous protocol for validating cross-architecture task clustering: CKA feasibility gate detects mechanism failure early (before wasting compute), WCSS bootstrap test provides statistical rigor (p-values + effect sizes), and reconstruction task accuracy validates information preservation. Section 4 describes dataset construction and coverage audit, while Section 5 presents results across these evaluation metrics.
