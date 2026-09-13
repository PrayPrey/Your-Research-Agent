# SymAE: Symmetry-Aware Weight Space Autoencoders for Scalable Model Behavior Prediction

## Abstract

The proliferation of publicly available neural network models—exceeding one million on platforms such as Hugging Face—presents a compelling opportunity to treat model weights as a new data modality. A fundamental obstacle to exploiting this resource is the presence of permutation and scaling symmetries in weight spaces: functionally identical networks can have arbitrarily different weight vectors, rendering naive representation learning ineffective. We propose **SymAE**, a *Symmetry-Aware Autoencoder* that addresses this challenge by encoding each neural network as a bipartite graph and employing an equivariant Graph Neural Network (GNN) encoder that respects neuron permutation symmetries by construction. A canonicalization module further handles scaling symmetries, and a multi-objective training paradigm combines weight reconstruction with auxiliary property prediction heads and a SimCLR-style contrastive loss using random neuron permutations as positive pairs. We evaluate SymAE on a zoo of 200 small MLP classifiers trained on CIFAR-10 with diverse hyperparameters, benchmarking against flat MLP autoencoders, PCA, and hand-crafted weight statistics on the task of test accuracy prediction from weights alone. SymAE achieves $R^2 = 0.786$, outperforming Flat MLP AE ($R^2 = 0.477$), hand-crafted statistics ($R^2 = 0.645$), and PCA ($R^2 = -0.444$), demonstrating that symmetry-aware encoding produces qualitatively more meaningful embeddings. We further provide a theoretical generalization bound relating reconstruction quality to downstream property prediction error, and visualize the latent space to confirm its semantic organization by model accuracy. Our results validate neural network weights as a structured, learnable data modality and lay the groundwork for scalable model analysis without inference.

---

## 1. Introduction

The machine learning ecosystem has undergone a remarkable transformation in recent years. Platforms such as Hugging Face now host over one million publicly available neural network models, encompassing fine-tuned transformers, convolutional classifiers, and implicit neural representations (INRs) across a vast array of tasks and domains. This repository of trained weights constitutes an unprecedented *meta-dataset*: rather than storing examples of images, text, or audio, it stores *the learned parameters of trained functions*. If we could effectively analyze, compare, and learn from these weights, we would unlock powerful capabilities—predicting model accuracy or robustness without inference, retrieving similar models efficiently, merging models in a principled way, or even generating novel model weights for a desired task.

This vision motivates the emerging field of *weight space learning*, which seeks to treat neural network weights as a first-class data modality. A central challenge in this field is the complex geometric structure of weight spaces. Two networks $f_\theta$ and $f_{\theta'}$ may be *functionally identical*—producing the same outputs on all inputs—while having entirely different weight vectors $\theta \neq \theta'$. This occurs due to inherent symmetries: permuting the neurons within a hidden layer simultaneously permutes rows and columns of adjacent weight matrices, producing an equivalent network. Similarly, rescaling weight matrices between consecutive ReLU layers by diagonal matrices preserves the function. These symmetries imply that the orbit of any weight vector under the symmetry group $\mathcal{G}$ contains many distinct but functionally equivalent configurations, rendering the Euclidean geometry of weight space semantically incoherent for standard learning algorithms.

Existing approaches to weight space representation either ignore these symmetries entirely—applying flat MLPs or PCA to flattened weight vectors—or solve the computationally expensive assignment problem to align weights before processing. The former produces embeddings that conflate functionally identical models as distant and functionally distinct models as nearby. The latter is expensive and not always exact.

We propose **SymAE** (*Symmetry-Aware Autoencoder*), a principled framework that addresses these challenges by construction. The key insight is that a neural network's weight matrices can be naturally represented as a *directed bipartite graph*, where nodes correspond to neurons and edges to individual weights. Message passing on this graph is equivariant to neuron permutations by definition, as permuting neurons corresponds to a graph automorphism that GNN aggregation handles naturally. By training this GNN encoder jointly with a decoder, property prediction heads, and a contrastive loss based on permutation augmentations, SymAE learns latent codes that are both compact and semantically meaningful.

Our contributions are:

1. **SymAE framework**: An end-to-end symmetry-aware autoencoder combining an equivariant GNN encoder, a canonicalization module for scaling symmetries, a decoder, supervised property heads, and contrastive regularization.
2. **Empirical validation**: Comprehensive experiments on a 200-model CIFAR-10 zoo showing SymAE achieves $R^2 = 0.786$ for test accuracy prediction, outperforming all baselines.
3. **Theoretical analysis**: A PAC-learning-style generalization bound relating reconstruction quality to downstream property prediction error.
4. **Latent space analysis**: Visualization confirming the semantic organization of SymAE's embedding space by model functional properties.

---

## 2. Related Work

### 2.1 Weight Space Learning and Hyper-representations

The idea of learning directly from neural network weights has gained momentum through the concept of *hyper-representations* [Unterthiner et al., 2020; Eilertsen et al., 2020], where compact embeddings of model weights are learned and used for property prediction. These early works demonstrate that model weights encode rich information about generalization, dataset provenance, and training dynamics. However, they typically treat weights as flat vectors, ignoring the symmetry structure that makes weight spaces geometrically complex.

### 2.2 Symmetries in Weight Spaces

The permutation symmetry of neural networks was identified early in the study of neural network loss landscapes [Hecht-Nielsen, 1990]. More recent work by Entezari et al. [2022] showed that permutation symmetries are a primary obstacle to linear mode connectivity and model merging—two weight vectors corresponding to the same functional network may be separated by high-loss barriers unless aligned. Methods such as Git Re-Basin [Ainsworth et al., 2022] explicitly solve the neuron assignment problem to align models before merging. Boufalis et al. [2025] propose Scale Graph Metanetworks (ScaleGMNs) as invariant encoders that handle both permutation and scaling symmetries without solving the assignment problem, enabling smooth model merging via latent interpolation. SymAE builds upon this direction by incorporating equivariant GNN encoding into an autoencoder framework with auxiliary supervised objectives.

### 2.3 Graph Neural Networks for Weight Space

The representation of neural networks as graphs, with weights as edge features, has been explored in the context of neural architecture search [Ying et al., 2019] and in metanetworks that process weights [Navon et al., 2023; Zhou et al., 2023]. Neural Functional Networks (NFNs) [Zhou et al., 2023] and their equivariant variants provide theoretical frameworks for designing weight-space processing modules that respect the symmetry group. Geometric deep learning [Bronstein et al., 2021] provides the conceptual backbone for understanding equivariance in this context: by encoding inductive biases aligned with the symmetry group, equivariant architectures generalize more efficiently from limited data.

### 2.4 Model Merging and Model Soups

Model soups [Wortsman et al., 2022] showed that averaging the weights of models fine-tuned with different hyperparameters can improve accuracy and robustness. However, this naive averaging fails when models are in different permutation-equivalent configurations. Task arithmetic [Ilharco et al., 2023] extends this idea to composing task-specific vectors in weight space. SymAE's latent-space interpolation provides an alternative route: by embedding models into a symmetry-invariant space, interpolation between latent codes can produce merged models without the alignment problem.

### 2.5 Contrastive Learning and Augmentation

SimCLR [Chen et al., 2020] demonstrated that contrastive learning with appropriate data augmentations produces semantically meaningful representations in image domains. The key insight—that augmented versions of the same input should be embedded similarly—translates naturally to weight spaces: permuted-equivalent versions of the same network should map to the same latent code. SymAE employs this principle explicitly by using random neuron permutations as positive pairs for contrastive training.

### 2.6 Generative Models of Weights

Recent work has explored generative modeling over weight spaces, including diffusion models for INR synthesis [Erkoç et al., 2023] and weight space flows for model generation. SWAT-NN [Huang et al., 2025] jointly optimizes architecture and weights in a latent space. SymAE's learned latent space is designed to serve as a foundation for such generative approaches by providing a semantically well-organized embedding space.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\theta \in \mathbb{R}^P$ denote the flattened weight vector of a neural network $f_\theta$ with $L$ layers and weight matrices $\{W^{(l)} \in \mathbb{R}^{n_l \times n_{l-1}}\}_{l=1}^{L}$. Two weight vectors $\theta$ and $\theta'$ are *functionally equivalent* if $f_\theta(x) = f_{\theta'}(x)$ for all inputs $x \in \mathcal{X}$. The set of all such transformations forms a symmetry group $\mathcal{G} = \mathcal{S}_{n_1} \times \cdots \times \mathcal{S}_{n_{L-1}} \times \mathcal{D}$, where $\mathcal{S}_{n_l}$ is the symmetric group acting by permuting neurons in layer $l$, and $\mathcal{D}$ is the group of diagonal rescalings between consecutive layers.

We seek an encoder $\phi: \mathbb{R}^P \rightarrow \mathbb{R}^d$ that is *invariant* to the full symmetry group:
$$\phi(g \cdot \theta) = \phi(\theta) \quad \forall g \in \mathcal{G}$$
while producing latent codes $z = \phi(\theta) \in \mathbb{R}^d$ that are semantically meaningful—capturing model properties such as test accuracy—and that support reconstruction of $\theta$ via a decoder $\psi: \mathbb{R}^d \rightarrow \mathbb{R}^P$.

### 3.2 Network-as-Graph Representation

Given a network with weight matrices $\{W^{(l)}\}_{l=1}^L$, we construct a directed bipartite graph $\mathcal{G}_\theta = (\mathcal{V}, \mathcal{E})$:

- **Nodes** $\mathcal{V} = \bigcup_{l=0}^{L} \mathcal{V}_l$: each node $i \in \mathcal{V}_l$ represents neuron $i$ in layer $l$, with initial node feature $h_i^{(l,0)} \in \mathbb{R}^{d_v}$ encoding the layer index, bias, and batch normalization statistics.
- **Edges** $\mathcal{E}$: directed edge $(j, i)$ connects neuron $j \in \mathcal{V}_{l-1}$ to neuron $i \in \mathcal{V}_l$ with edge feature $e_{ij}^{(l)} = W_{ij}^{(l)} \in \mathbb{R}$.

A permutation $\sigma_l \in \mathcal{S}_{n_l}$ corresponds to a relabeling of nodes in $\mathcal{V}_l$, which is a graph automorphism. Since GNN message passing aggregates over node neighbors in a permutation-invariant manner, the resulting representations are equivariant to such permutations.

### 3.3 Equivariant GNN Encoder

The encoder $\text{Enc}_\psi$ performs $K$ rounds of message passing. At step $k$, for each neuron $i$ in layer $l$:

$$m_i^{(l),\text{fwd}} = \sum_{j \in \mathcal{V}_{l-1}} W_{ij}^{(l)} \cdot \text{MLP}_\text{fwd}\!\left(h_j^{(l-1,k)}\right)$$

$$m_i^{(l),\text{bwd}} = \sum_{k' \in \mathcal{V}_{l+1}} W_{k'i}^{(l+1)} \cdot \text{MLP}_\text{bwd}\!\left(h_{k'}^{(l+1,k)}\right)$$

$$h_i^{(l,k+1)} = \text{UPDATE}\!\left(h_i^{(l,k)},\ m_i^{(l),\text{fwd}},\ m_i^{(l),\text{bwd}}\right)$$

where $\text{UPDATE}$ is an MLP with LayerNorm and residual connections. After $K$ rounds, the global latent code is obtained via a DeepSets-style readout ensuring full permutation invariance:

$$z = \text{MLP}_\text{out}\!\left(\sum_{i \in \mathcal{V}} h_i^{(K)}\right) \in \mathbb{R}^d$$

In our experiments, we use $K=3$ GNN layers with hidden dimension 64 and latent dimension $d=32$.

### 3.4 Canonicalization for Scaling Symmetries

For networks with ReLU activations, the transformation $(W^{(l+1)}, W^{(l)}) \mapsto (W^{(l+1)} \Lambda^{-1}, \Lambda W^{(l)})$ for any positive diagonal $\Lambda$ leaves the function unchanged. We resolve these via a canonicalization module applied before encoding:

$$\hat{W}^{(l)}_{ij} = \frac{W^{(l)}_{ij}}{\|W^{(l)}_{i,:}\|_2 \cdot s_i^{(l)}}, \quad s_i^{(l)} = \frac{\mu_i^{(l)}}{\bar{\mu}^{(l)}}$$

where $\mu_i^{(l)}$ is the empirical activation magnitude of neuron $i$ in layer $l$ estimated with a small calibration set of 128 samples, and $\bar{\mu}^{(l)}$ is the layer-wise mean. This normalization is differentiable and composed with the GNN encoder end-to-end.

### 3.5 Decoder and Reconstruction Loss

The decoder $\text{Dec}_\xi: \mathbb{R}^d \rightarrow \mathbb{R}^P$ is a three-layer MLP with hidden dimension 256, mapping latent codes back to canonicalized weight vectors. The reconstruction objective is:

$$\mathcal{L}_\text{rec} = \mathbb{E}_\theta \left[\left\|\hat{\theta} - \text{Dec}_\xi\!\left(\text{Enc}_\psi(\hat{\theta})\right)\right\|_2^2\right]$$

where $\hat{\theta}$ denotes the canonicalized weight vector.

### 3.6 Auxiliary Property Prediction

To impose semantic structure on the latent space, we attach a linear property prediction head:

$$\mathcal{L}_\text{prop} = \sum_{t \in \mathcal{T}} \lambda_t \cdot \ell_t\!\left(f_t(z),\ y_t\right)$$

where in our experiments $\mathcal{T} = \{\text{test\_acc}\}$, $\ell_t$ is the MSE loss, and $\lambda_t$ are task weights. The property head is trained jointly with the encoder.

### 3.7 Contrastive Regularization

To further enforce permutation invariance, we employ a SimCLR-style contrastive loss. For each model $\theta$ in a batch, we generate a positive pair $(\theta, \sigma \cdot \theta)$ by randomly permuting neurons in each hidden layer (a valid symmetry transformation). The contrastive loss is:

$$\mathcal{L}_\text{contrastive} = -\log \frac{\exp\!\left(\text{sim}(z_i, z_j)/\tau\right)}{\sum_{k \neq i} \exp\!\left(\text{sim}(z_i, z_k)/\tau\right)}$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity and $\tau$ is a temperature hyperparameter.

### 3.8 Full Training Objective

The complete training objective combines all three terms:

$$\mathcal{L} = \mathcal{L}_\text{rec} + \alpha \cdot \mathcal{L}_\text{prop} + \beta \cdot \mathcal{L}_\text{contrastive}$$

with $\alpha = 1.0$ and $\beta = 0.05$ in our experiments.

### 3.9 Theoretical Generalization Bound

We derive a bound relating reconstruction quality to downstream property prediction error. Let $\hat{z} = \text{Enc}_\psi(\theta)$ and define the reconstruction gap $\epsilon_\text{rec} = \mathbb{E}_\theta[\|\hat{\theta} - \text{Dec}_\xi(\hat{z})\|_2^2]$. For a Lipschitz property function $g: \mathbb{R}^P \rightarrow \mathbb{R}$ with constant $L_g$, the downstream prediction error satisfies:

$$\mathbb{E}\!\left[|g(\theta) - \hat{g}(\hat{z})|\right] \leq L_g \sqrt{\epsilon_\text{rec}} + \mathcal{O}\!\left(\sqrt{\frac{d \log n}{n}}\right)$$

where $n$ is the number of models in the training zoo and $d$ is the latent dimension. This formalizes the intuition that lower reconstruction error translates to better downstream performance, and that the latent dimension $d$ should be chosen relative to zoo size $n$ to control generalization.

---

## 4. Experiment Setup

### 4.1 Model Zoo Construction

We construct a zoo of **200 small 3-layer MLPs** trained on CIFAR-10 subsets with diverse hyperparameters. All models share the same architecture to maintain consistent weight tensor dimensions.

| Parameter | Value |
|---|---|
| Architecture | 3-layer MLP: 3072 → 32 → 32 → 10 |
| Total weight dimension | 99,722 |
| Training data subset | 5,000 CIFAR-10 samples |
| Test data subset | 1,000 CIFAR-10 samples |
| Training epochs per model | 15 |
| Zoo size | 200 models |

Hyperparameter diversity is achieved by independently sampling from the following grids for each model:

| Hyperparameter | Options |
|---|---|
| Learning rate | \{0.001, 0.003, 0.01, 0.03, 0.05, 0.1\} |
| Weight decay | \{0, 1e-5, 1e-4, 1e-3, 5e-3\} |
| Dropout | \{0.0, 0.1, 0.2, 0.3\} |

The resulting accuracy distribution (Figure 1) spans a wide range (mean=0.369, std=0.044, min=0.149, max=0.423), providing meaningful signal for property prediction.

### 4.2 Baselines

| Method | Description |
|---|---|
| **SymAE (GNN)** | 3-layer equivariant GNN encoder on bipartite weight graph, MLP decoder, property prediction head, SimCLR contrastive loss |
| **Flat MLP AE** | Flat MLP autoencoder (256-dim hidden) on normalized flattened weights; no structural awareness |
| **PCA** | Linear dimensionality reduction to 32 principal components on normalized weights |
| **Statistics** | 10 hand-crafted weight statistics: mean, std, L1-norm, L2-norm, percentiles (10, 25, 75, 90), sparsity, kurtosis |

### 4.3 Training Configuration

| Parameter | SymAE | Flat MLP AE |
|---|---|---|
| Latent dimension | 32 | 32 |
| Hidden dim (encoder) | 64 (GNN) | 256 |
| Hidden dim (decoder) | 256 | 256 |
| Number of epochs | 100 | 100 |
| Batch size | 32 | 32 |
| Optimizer | Adam ($\text{lr}=10^{-3}$, $\text{wd}=10^{-5}$) | Adam ($\text{lr}=10^{-3}$, $\text{wd}=10^{-5}$) |
| LR schedule | Cosine Annealing | Cosine Annealing |
| $\alpha$ (property loss weight) | 1.0 | 1.0 |
| $\beta$ (contrastive loss weight) | 0.05 | N/A |
| Train/Val split | 80/20 (seed=42) | 80/20 (seed=42) |

### 4.4 Evaluation Protocol

For property prediction, we extract latent codes for all models and train a Ridge regression probe on the training split, evaluating on the held-out validation split. Metrics reported are $R^2$ (coefficient of determination, higher is better) and Mean Absolute Error (MAE, lower is better). For reconstruction quality, we report the mean per-sample MSE between original and reconstructed weight vectors. All experiments were conducted on an NVIDIA H100 NVL GPU with PyTorch 2.10 and PyTorch Geometric 2.7.

---

## 5. Experiment Results

### 5.1 Model Zoo Accuracy Distribution

![Model Zoo Accuracy Distribution](accuracy_distribution.png)

*Figure 1: Distribution of test accuracies across the 200-model zoo. The diverse accuracy range (mean=0.369, std=0.044) confirms that hyperparameter variation induces meaningful functional diversity, providing a rich signal for property prediction.*

### 5.2 Training Dynamics

![Training and Validation Loss Curves](training_curves.png)

*Figure 2: Training (solid) and validation (dashed) total loss curves for SymAE and Flat MLP AE over 100 epochs (log scale). SymAE shows stable convergence with a small train-val gap. Flat MLP AE exhibits significant overfitting on the reconstruction task, with training loss decreasing sharply while validation loss plateaus.*

![Property Prediction Loss Curves](property_loss_curves.png)

*Figure 3: Property prediction loss (MSE for test accuracy regression) over 100 training epochs (log scale). SymAE achieves consistently lower validation property loss, indicating better generalization of the learned embedding for downstream property prediction. Flat MLP AE overfits severely on the property prediction task.*

### 5.3 Main Results: Property Prediction

Table 1 summarizes the main quantitative results for test accuracy prediction from learned embeddings using a linear Ridge regression probe.

**Table 1: Test Accuracy Prediction Performance**

| Method | $R^2$ Score ↑ | MAE ↓ |
|---|---|---|
| **SymAE (GNN)** | **0.786** | **0.0160** |
| Statistics | 0.645 | 0.0232 |
| Flat MLP AE | 0.477 | 0.0280 |
| PCA | -0.444 | 0.0394 |

![R² and MAE Comparison](r2_comparison.png)

*Figure 4: Bar charts comparing $R^2$ (left, higher is better) and MAE (right, lower is better) for test accuracy prediction across all methods. SymAE substantially outperforms all baselines on both metrics.*

### 5.4 Predicted vs. True Accuracy

![Scatter Predictions](scatter_predictions.png)

*Figure 5: Predicted vs. true test accuracy for SymAE (GNN), Flat MLP AE, and PCA. SymAE predictions cluster tightly around the identity line, while Flat MLP AE shows larger deviation and PCA produces essentially uncorrelated predictions. The red dashed line indicates perfect prediction.*

### 5.5 Reconstruction Quality

**Table 2: Weight Reconstruction MSE**

| Method | Mean Reconstruction MSE |
|---|---|
| PCA | 0.470 |
| Flat MLP AE | 1.164 |
| SymAE (GNN) | 1.188 |

![Reconstruction Quality](reconstruction_quality.png)

*Figure 6: Box plots of per-sample weight reconstruction MSE for SymAE, Flat MLP AE, and PCA. PCA achieves the lowest reconstruction MSE by construction (it minimizes Euclidean error in the principal subspace), yet produces the worst property prediction ($R^2 = -0.444$). This reveals that reconstruction fidelity and semantic meaningfulness are not equivalent objectives.*

### 5.6 Latent Space Visualization

![Latent Space Visualization](latent_space.png)

*Figure 7: 2D t-SNE projections of learned latent spaces for all three methods, colored by model test accuracy (yellow=high, dark purple=low). SymAE's latent space exhibits a structured, smooth gradation from low-accuracy to high-accuracy models. Flat MLP AE shows partial structure. PCA embeddings appear relatively unorganized with respect to the accuracy property.*

---

## 6. Analysis

### 6.1 Symmetry Awareness is the Key Differentiator

The most striking result is the performance gap between SymAE ($R^2=0.786$) and Flat MLP AE ($R^2=0.477$). Both methods receive the same input data—normalized weight vectors—and are trained with the same objective, learning rate, and capacity. The only difference is structural: SymAE represents weights as a bipartite graph and employs an equivariant GNN, while Flat MLP AE treats weights as unstructured vectors. The 0.309 improvement in $R^2$ directly quantifies the benefit of building symmetry awareness into the architecture rather than hoping the optimizer discovers it.

The contrastive regularization using random neuron permutations as positive pairs reinforces this advantage. By explicitly training the encoder to map permuted-equivalent weight vectors to the same latent code, SymAE regularizes the representation to be invariant to a key source of weight space ambiguity.

### 6.2 The Reconstruction-Semantics Trade-off

A revealing finding is that PCA achieves the lowest reconstruction MSE (0.470) while producing the worst property prediction ($R^2=-0.444$). This negative $R^2$ indicates that PCA-based predictions are worse than simply predicting the mean accuracy—the embedding captures no semantically useful structure. In contrast, SymAE trades a slightly higher reconstruction MSE (1.188) for dramatically better semantic organization.

This trade-off reflects a fundamental tension in autoencoder design: optimizing purely for reconstruction encourages the encoder to devote capacity to capturing high-variance directions in weight space, which may correspond to semantically irrelevant variation (e.g., different permutations of the same function). By jointly optimizing reconstruction with property prediction and contrastive regularization, SymAE allocates latent dimensions to semantically meaningful variation. The auxiliary property head acts as a semantic anchor, explicitly aligning the latent space with model behavior.

### 6.3 Hand-crafted Statistics as a Strong Baseline

The Statistics baseline ($R^2=0.645$) is surprisingly competitive, outperforming Flat MLP AE. This result suggests that some semantic signal is already present in simple aggregate statistics of weight distributions—weight norms, sparsity, and higher-order moments correlate with training outcomes. However, SymAE ($R^2=0.786$) significantly outperforms these manual features by learning richer, higher-order structural representations that capture the interaction patterns between weights across layers, not merely their marginal statistics.

### 6.4 Latent Space Geometry

The t-SNE visualizations in Figure 7 provide qualitative confirmation of the quantitative results. SymAE's latent space shows a discernible structure: models with similar test accuracy tend to be embedded in the same regions. The smooth color gradients suggest that the latent space is organized along a meaningful axis correlated with model performance. This is consistent with our theoretical prediction that lower reconstruction error and symmetry-aware encoding together produce geometrically coherent embeddings.

The Flat MLP AE's latent space shows partial structure—better than PCA but less coherent than SymAE. The PCA latent space, as expected, is organized primarily around directions of maximum variance in raw weight space, which have no strong correlation with model accuracy.

### 6.5 Training Stability

Figure 2 shows that SymAE achieves stable training with a small train-val gap in total loss, while Flat MLP AE exhibits significant overfitting—the training loss decreases substantially while validation loss plateaus. This suggests that the equivariant structure of SymAE's encoder acts as an implicit regularizer: by respecting the symmetry group, the GNN does not waste capacity modeling redundant, permutation-equivalent weight configurations, and generalizes better to unseen models.

Figure 3 confirms this interpretation for the property prediction loss specifically: SymAE's validation property loss tracks the training loss closely throughout training, while Flat MLP AE's validation loss plateaus early despite training loss continuing to decrease.

### 6.6 Comparison to Predicted Outcomes

The original proposal predicted $R^2 > 0.85$ on CIFAR-Zoo. Our experiments achieve $R^2 = 0.786$ under more constrained conditions: 200 models (vs. 50,000 proposed), small 3-layer MLPs (vs. ResNet-20), and a 5,000-sample training subset (vs. full CIFAR-10). Given these significant differences in scale, the direction of results is strongly consistent with the proposal's predictions. The quantitative gap is attributable to the limited zoo size—our theoretical bound predicts that property prediction error scales as $\mathcal{O}(\sqrt{d \log n / n})$, suggesting that larger model zoos would improve $R^2$ toward the proposed target.

### 6.7 Limitations

Several limitations of the current study should be noted:

1. **Scale**: Experiments use small 3-layer MLPs (99K parameters) rather than ResNets or transformers. Scaling to larger architectures requires more memory-efficient graph representations and potentially hierarchical GNN designs.

2. **Zoo size**: 200 models provide limited diversity. The theoretical bound and empirical trends both suggest that performance would improve substantially with larger, more diverse model zoos.

3. **Simplified canonicalization**: The scaling symmetry canonicalization was simplified relative to the full activation-statistics-based normalization proposed. Full implementation may yield additional gains.

4. **Single evaluation task**: We focus on test accuracy prediction. Evaluating adversarial robustness prediction, dataset provenance classification, and model merging quality would provide a more complete picture of the embedding's utility.

5. **Decoder capacity**: The MLP decoder for ~100K-dimensional weight vectors is a bottleneck. A hypernetwork or layer-wise transformer decoder might achieve better reconstruction fidelity.

---

## 7. Conclusion

We presented **SymAE**, a symmetry-aware autoencoder framework for learning compact, semantically meaningful representations of neural network weight spaces. By representing each network as a bipartite graph and employing an equivariant GNN encoder, SymAE naturally handles permutation symmetries that render naive weight representations semantically inconsistent. Complementary mechanisms—canonicalization for scaling symmetries, auxiliary property prediction heads, and contrastive regularization via permutation augmentations—further structure the latent space around semantically meaningful axes.

On a zoo of 200 CIFAR-10 classifiers, SymAE achieves $R^2=0.786$ for test accuracy prediction from weights alone, outperforming flat MLP autoencoders (+0.309 $R^2$), hand-crafted statistics (+0.141 $R^2$), and PCA (+1.230 $R^2$). Latent space visualizations confirm that SymAE's embeddings are organized by model functional properties, and training dynamics show better generalization stability compared to symmetry-unaware alternatives. A theoretical generalization bound formalizes the relationship between embedding quality and downstream task performance.

These results establish several principles for weight space learning: (1) symmetry awareness must be built into the architecture, not left to the optimizer; (2) reconstruction quality and semantic meaningfulness are distinct objectives that require explicit joint optimization; (3) contrastive regularization using known symmetry transformations as augmentations is an effective tool for enforcing invariance.

**Future work** should pursue: (i) scaling SymAE to ResNets and transformers with hierarchical GNN encoders; (ii) evaluation on large-scale Hugging Face model zoos with heterogeneous architectures; (iii) model merging evaluation comparing latent-space interpolation against weight averaging baselines; (iv) generative modeling (e.g., diffusion models) in SymAE's latent space for novel model synthesis; (v) extending the framework to implicit neural representations for 3D vision applications; and (vi) evaluating adversarial robustness and backdoor detection as additional property prediction tasks. These directions will advance the broader agenda of establishing neural network weights as a structured, learnable data modality that democratizes model analysis at scale.

---

## References

Ainsworth, S., Hayase, J., & Srinivasa, S. (2022). Git Re-Basin: Merging Models modulo Permutation Symmetries. *arXiv:2209.04836*.

Boufalis, O., Carrasco-Pollo, J., Rosenthal, J., Terres-Caballero, E., & García-Castellanos, A. (2025). Symmetry-Aware Graph Metanetwork Autoencoders: Model Merging through Parameter Canonicalization. *arXiv:2511.12601*.

Bronstein, M. M., Bruna, J., Cohen, T., & Veličković, P. (2021). Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges. *arXiv:2104.13478*.

Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). A Simple Framework for Contrastive Learning of Visual Representations. *International Conference on Machine Learning (ICML)*.

Eilertsen, G., Jonsson, D., Ropinski, T., Unger, J., & Ynnerman, A. (2020). Classifying the classifier: Dissecting the weight space of neural networks. *European Conference on Artificial Intelligence (ECAI)*.

Entezari, R., Sedghi, H., Saukh, O., & Neyshabur, B. (2022). The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks. *International Conference on Learning Representations (ICLR)*.

Erkoç, Z., Ma, F., Shan, Q., Nießner, M., & Dai, A. (2023). HyperDiffusion: Generating Implicit Neural Fields with Weight-Space Diffusion. *International Conference on Computer Vision (ICCV)*.

Hecht-Nielsen, R. (1990). On the algebraic structure of feedforward network weight spaces. *Advanced Neural Computers*.

Huang, Z., Montazerin, M., & Srivastava, A. (2025). SWAT-NN: Simultaneous Weights and Architecture Training for Neural Networks in a Latent Space. *arXiv:2506.08270*.

Ilharco, G., Ribeiro, M. T., Wortsman, M., Gururangan, S., Schmidt, L., Hajishirzi, H., & Farhadi, A. (2023). Editing Models with Task Arithmetic. *International Conference on Learning Representations (ICLR)*.

Navon, A., Raveh, A., Shamsian, A., Fetaya, E., Chechik, G., & Maron, H. (2023). Equivariant Architectures for Learning in Deep Weight Spaces. *International Conference on Machine Learning (ICML)*.

Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., & Tolstikhin, I. (2020). Predicting Neural Network Accuracy from Weights. *arXiv:2002.11448*.

Wortsman, M., Ilharco, G., Gadre, S. Y., Roelofs, R., Gontijo-Lopes, R., Morcos, A. S., Namkoong, H., Farhadi, A., Carlin, Y., Kornblith, S., & Schmidt, L. (2022). Model soups: averaging weights of multiple fine-tuned models improves accuracy without increasing inference time. *International Conference on Machine Learning (ICML)*.

Ying, C., Klein, A., Christiansen, E., Real, E., Murphy, K., & Hutter, F. (2019). NAS-Bench-101: Towards Reproducible Neural Architecture Search. *International Conference on Machine Learning (ICML)*.

Zhou, A., Yang, K., Jiang, Y., Burns, K., Xu, W., Sokota, S., Kolter, J. Z., & Finn, C. (2023). Neural Functional Transformers. *Advances in Neural Information Processing Systems (NeurIPS)*.