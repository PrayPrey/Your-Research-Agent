---
source_paper: "arxiv_2406_09997.md"
generated_at: "2026-08-18T23:54:44.924746"
model: "openai/gpt-5.2"
summary_chars: 14166
---

# Towards Scalable and Versatile Weight Space Learning (SANE)

## Key Metadata
- **Authors:** Konstantin Schürholt et al.
- **Year:** 2024
- **Venue:** ICML 2024 (Proceedings of the 41st International Conference on Machine Learning; PMLR 235)
- **Core Contribution:** Introduces **SANE (Sequential Autoencoder for Neural Embeddings)**, a *task-agnostic, scalable* weight-space representation learner that tokenizes and **sequentially** autoencodes neural network weights, enabling both discriminative analysis and generative sampling for much larger models (e.g., ResNet-18/101) than prior hyper-representation methods.

## Section Summaries

### Abstract
Learning representations of well-trained neural
network models holds the promise to provide an
understanding of the inner workings of those mod-
els. However, previous work has either faced lim-
itations when processing larger networks or was
task-specific to either discriminative or generative
tasks. This paper introduces the SANE approach
to weight-space learning. SANE overcomes pre-
vious limitations by learning task-agnostic rep-
resentations of neural networks that are scalable
to larger models of varying architectures and
that show capabilities beyond a single task. Our
method extends the idea of hyper-representations
towards sequential processing of subsets of neu-
ral network weights, thus allowing one to em-
bed larger neural networks as a set of tokens into
the learned representation space. SANE reveals
global model information from layer-wise em-
beddings, and it can sequentially generate un-
seen neural network models, which was unattain-
able with previous hyper-representation learning
methods. Extensive empirical evaluation demon-
strates that SANE matches or exceeds state-of-the-
art performance on several weight representation
learning benchmarks, particularly in initialization
for new tasks and larger ResNet architectures.

### Introduction & Motivation
The paper targets **weight-space learning**: learning representations directly from populations (“model zoos”) of trained neural network parameters to predict properties (e.g., accuracy) and to generate new models. Prior “hyper-representation” approaches autoencode the **entire flattened weight vector**, which becomes infeasible for large networks and typically assumes fixed architecture/parameterization. Meanwhile, many generative weight methods (HyperNetworks, HyperGANs, etc.) rely on *dataset-level* supervision, whereas hyper-representations aim to learn directly from weights without data access. SANE addresses the gap by **tokenizing weights into sequences** and training a transformer autoencoder on **subsequences/windows**, enabling scalability and cross-architecture usage while supporting both **discriminative** (embedding → property prediction) and **generative** (latent sampling → weights) downstream tasks.

### Methodology
SANE extends prior **hyper-representations** (Schürholt et al., 2021; 2022a), which learn an autoencoder on flattened weights:
\[
z = g_\theta(W), \qquad \hat W = h_\psi(z),
\]
trained with reconstruction and contrastive guidance:
\[
L = (1-\gamma)L_{\text{rec}} + \gamma L_c,\quad 
L_{\text{rec}}=\|W-\hat W\|_2^2,\quad 
L_c=\mathrm{NTXent}(p_\phi(z_i),p_\phi(z_j)).
\]
SANE’s key change is to **tokenize** layer weights and train on **windows** of the token sequence so memory/compute depends on window length, not full model size. Tokenization: reshape each weight tensor \(W_{\text{raw}}\in \mathbb{R}^{c_{\text{out}}\times c_1\times\cdots\times c_{\text{in}}}\) into \(W\in \mathbb{R}^{c_{\text{out}}\times c_r}\) (flatten non-output dims), slice row-wise, split/pad to a global token width \(d_t\), yielding per-layer tokens \(T_l\in \mathbb{R}^{n_l\times d_t}\) with \(n_l=c_{\text{out},l}\left\lceil \frac{c_r}{d_t}\right\rceil\). Concatenate across layers to a model sequence \(T\in\mathbb{R}^{N\times d_t}\). Each token has a 3D position \(P_n=[n,l,k]\) (global index, layer index, within-layer index). Training uses random consecutive **windows** \(T_{s,n}\) of length \(w_s\), with mask \(M_{s,n}\) to ignore padding.

SANE’s windowed encoder/decoder operate as:
\[
z_{s,n}=g_\theta(T_{s,n},P_{s,n}),\qquad 
\hat T_{s,n}=h_\psi(z_{s,n},P_{s,n}),
\]
where \(z_{s,n}\in\mathbb{R}^{w_s\times d_z}\) is a per-token latent (obtained via linear maps to/from the bottleneck, \(d_t\to d_z\)). The sequence loss is:
\[
L_{\text{rec}}=\|M_{s,n}\odot(T_{s,n}-\hat T_{s,n})\|_2^2,\qquad
L_c=\mathrm{NTXent}(p_\phi(z_{s,n,i}),p_\phi(z_{s,n,j})).
\]
Architecture: encoder and decoder are **transformer blocks** (exact depth/heads not specified in the excerpt) with implementation optimizations (automatic mixed precision, **flash attention**). Augmentations include **noise** and **permutation**; contrastive views use an aligned model vs. a permuted view.

Three stabilizers address weight-space symmetries and long sequences:  
1) **Model Alignment** to a reference model \(A\): find permutation
\[
\pi=\arg\min_\pi \|\mathrm{vec}(\Theta(A))-\mathrm{vec}(\Theta(B))\|_2,
\]
then align each model \(B\) using \(\pi\) (Ainsworth et al., 2022).  
2) **Haloing** at inference: encode chunks with extra context \(h\) on both sides,
\(T^{h}_{s,n}=T_{n-h:\,n+w_s+h}\), dropping halo tokens after encoding/decoding to stitch coherent embeddings.  
3) **BatchNorm conditioning** during sampling: exclude BN parameters from representation learning; after sampling, run a few forward passes on target data to set BN statistics (without gradient updates).

Model-level embeddings for discriminative tasks are computed by encoding (possibly via haloed chunks) and aggregating token embeddings by the **center of gravity**:
\[
\bar z = \frac{1}{N}\sum_{n=1}^N z_n.
\]
Generative sampling uses few prompt examples \(W_e\): embed prompts \(z_e=g_\theta(T_e,P)\), fit **per-token KDE** distributions \(P_{e\in E}(z^e_n)\), sample
\[
z^k_n \sim P_{e\in E}(z^e_n),
\]
decode \(T^k=h_\psi(z^k,P)\to W^k\), then optionally **subsample** top models by a target metric and **bootstrap** by re-fitting the KDE on the best samples iteratively.

Training procedure & hyperparameters (as reported): model zoos split 70:15:15; train for **50 epochs** with **OneCycle LR** scheduling; hyperparameters tuned with **ray.tune**; data loading uses **FFCV** with “super-sampled” windows for coverage. (Optimizer, learning rate, batch size, transformer depth/width, \(d_t\), \(d_z\), \(w_s\), \(\gamma\) are not specified in the provided excerpt.)

### Experiments & Results
**Setup & data.** Experiments use the **model zoo dataset** (Schürholt et al., 2022c) with splits **70:15:15**. Two regimes:  
- **Small CNN zoos:** MNIST & SVHN LeNet-style (3 conv + 2 dense, ~2.5k params); CIFAR-10 & STL-10 wider variants (~12k params).  
- **Large ResNet zoos:** CIFAR-10/100 and Tiny-ImageNet with **ResNet-18** (~12M params). For ResNet zoos, they keep **140 models per zoo** for manageability. SANE is also analyzed out-of-distribution on ImageNet-trained ResNets/VGGs from `pytorchcv`.

**Metrics & tasks.**  
1) **Discriminative** linear probing on model embeddings \(\bar z\) to predict properties: **test accuracy (Acc)**, **epoch (Ep)**, **generalization gap (Ggap)**; metric is regression **\(R^2\)** on test split. Baselines include raw weights \(W\) (when feasible) and weight statistics \(s(W)\) (Unterthiner et al., 2020), plus prior hyper-representations (Schürholt et al., 2021; 2022a) in broader comparisons (Fig. 1, Appendix).  
2) **Embedding analysis** vs **WeightWatcher** (Martin et al., 2021): compare trends of SANE layerwise dispersion vs WW’s log spectral norm \(\log(\|W\|_2)\) and weighted power-law exponent \(\alpha\). They define per-layer spread from token embeddings:
\[
z^t_m=g(W^t_m),\qquad \hat z_l=\mathrm{std}_t(z^t_m).
\]
SANE shows similar global trends across layer index (low early layers, sharp increase late layers) and correlates with accuracy, including OOD architectures.  
3) **Generative** tasks: sample weights and evaluate **initialization** (epoch 0 accuracy) and fine-tuning/transfer (accuracy after 1/5/10/25 epochs depending on setting). Sampling baselines: prior **SKDE30** (Schürholt et al., 2022a), **SANE+KDE30**, and new **SANE SUB** (subsampling) and **SANE BOOT** (bootstrapped refinement), plus **SANE GAUSS** (bootstrap from Gaussian prior, mostly feasible for small models).

**Key results (compact tables).**

**(A) Property prediction \(R^2\) (linear probe).**

| Zoo | Feature | Acc \(R^2\) | Ep \(R^2\) | Ggap \(R^2\) |
|---|---:|---:|---:|---:|
| MNIST (CNN) | \(W\) | 0.965 | 0.953 | 0.246 |
|  | \(s(W)\) | 0.987 | 0.974 | 0.393 |
|  | **SANE** | 0.978 | 0.958 | **0.402** |
| SVHN (CNN) | \(W\) | 0.910 | 0.833 | 0.479 |
|  | \(s(W)\) | 0.985 | 0.953 | 0.711 |
|  | **SANE** | **0.991** | 0.930 | **0.760** |
| CIFAR-10 (CNN) | \(W\) | -7.580 | 0.636 | 0.324 |
|  | \(s(W)\) | 0.965 | 0.923 | 0.909 |
|  | **SANE** | 0.885 | 0.771 | 0.772 |
| CIFAR-10 (ResNet-18) | \(s(W)\) | 0.880 | 0.999 | 0.490 |
|  | **SANE** | 0.879 | 0.999 | **0.512** |
| CIFAR-100 (ResNet-18) | \(s(W)\) | 0.802 | 0.999 | 0.704 |
|  | **SANE** | 0.795 | 0.980 | 0.699 |
| Tiny-ImageNet (ResNet-18) | \(s(W)\) | 0.923 | 0.999 | 0.882 |
|  | **SANE** | 0.922 | 0.992 | 0.879 |

Takeaway: On small CNNs, SANE is competitive with strong hand-designed statistics \(s(W)\). On ResNet-18, SANE matches \(s(W)\) while raw \(W\) is infeasible due to dimensionality.

**(B) Generative sampling (initialization and fine-tuning).**

*Small CNNs (selected epoch-0 accuracies, mean±std):*

| Method | MNIST | SVHN | CIFAR-10 (CNN) | STL |
|---|---:|---:|---:|---:|
| SKDE30 (prior) | 68.6±6.7 | 54.5±5.9 | 56.3±0.5 | 39.2±0.8 |
| SANE KDE30 | 84.8±0.8 | 70.7±1.4 | 57.9±0.2 | 43.5±1.0 |
| **SANE SUB** | **86.7±0.8** | **72.3±1.6** | **58.2±0.2** | **43.5±0.7** |
| SANE GAUSS | 20.8±0.1 | 21.6±0.5 | 19.3±0.2 | 17.5±1.5 |

SANE substantially improves zero-shot initialization over prior SKDE30 (notably MNIST/SVHN).

*ResNet-18 sampling (epoch-0 / epoch-10 accuracies, mean±std):*

| Dataset | From scratch @ ep0 | SANE KDE30 @ ep0 | **SANE SUB @ ep0** | **SANE BOOT @ ep0** | From scratch @ ep10 | SANE SUB @ ep10 |
|---|---:|---:|---:|---:|---:|---:|
| CIFAR-10 | ~10% | 64.8±2.0 | 68.1±0.7 | **68.6±1.2** | 85.5±1.5 | **92.14±0.2** |
| CIFAR-100 | ~1% | 19.8±2.5 | 19.8±1.3 | 20.4±1.3 | 56.5±2.0 | **72.9±0.1** |
| Tiny-ImageNet | ~0.5% | 8.4±0.9 | 11.1±0.5 | **11.7±0.5** | 43.3±1.9 | **64.0±0.2** |

These demonstrate SANE’s primary scalability claim: it can **sample competitive ResNet-18 initializations** from a weight-space model—previous hyper-representation generators could not feasibly operate at ~12M parameters.

**Few-shot transfer to new tasks/architectures.** With very few prompt examples (e.g., 5 prompts at epoch 25), SANE sampling transfers across tasks (e.g., pretrain on CIFAR-100 ResNet-18 zoo, sample for Tiny-ImageNet ResNet-18). Example (Table 5, accuracy on Tiny-ImageNet): at epoch 0, from scratch 10.4±2.2 vs **SANE 39.4±1.5**; at epoch 1, 28.5±0.9 vs **61.0±0.2**. They also report cross-architecture sampling (e.g., ResNet-18 → ResNet-34) and combined task+architecture shift (Fig. 5), with gains diminishing as architectural distance increases.

**Ablations / components.** The paper notes evaluations of alignment, haloing, and BN-conditioning in Appendix A (not included here), and qualitatively argues they stabilize scaling/sampling. The main in-text comparisons show subsampling/bootstrapping improves over KDE30-style sampling and reduces reliance on high-quality prompt examples.

**Uncertainty & significance.** Many generative results report mean±std across runs/samples (e.g., ±0.2 to ±2.9), but no formal hypothesis tests or confidence intervals are reported in the excerpt.

**Compute / efficiency.** No GPU-hours are provided. Engineering choices include: windowed training (reducing memory), **FFCV** precompiled window datasets, AMP, flash attention, and OneCycle schedule. Inference uses haloing to embed long sequences (e.g., ~50k tokens mentioned for long ResNet sequences).

### Discussion & Conclusion
SANE demonstrates that **sequential, token-based** autoencoding of network weights can preserve global/layerwise model-quality signals while scaling to **orders-of-magnitude larger** models than prior hyper-representations. It enables both strong property prediction and practical **model sampling** for initialization/transfer, including limited cross-architecture generalization. Limitations include training mostly on **homogeneous (single-architecture) zoos**, reliance on **prompt examples** for large-model sampling (Gaussian bootstrapping becomes expensive), and experiments restricted to **computer vision** tasks.

## Key Contributions
- **Sequential tokenization + windowed transformer autoencoding** of weights, decoupling representation learning memory from base-model size and enabling embeddings for large models (e.g., ResNet-18/101).
- A unified **task-agnostic** framework supporting both **discriminative** (linear probing for accuracy/epoch/generalization gap) and **generative** (sampling weights for initialization/transfer) uses of weight-space embeddings.
- Practical add-ons for scaling and stability: **model alignment** (permutation symmetries), **haloing** (context for chunked inference), and **batch-norm conditioning**, plus **subsampling/bootstrapped** sampling that reduces reliance on many high-quality prompt models.

## Potential Relevance
SANE provides a concrete recipe for representing a trained network as a **sequence of weight tokens** that can be processed by transformers—useful if your hypothesis involves (i) scalable “model-as-data” learning, (ii) cross-model diagnostics without training-data access, or (iii) generating weight initializations for rapid adaptation. The sampling strategy (per-token KDE + subsampling/bootstrapping) is a pragmatic baseline for “few prompt models → many candidate initializations,” and the WeightWatcher-aligned analysis suggests a bridge between learned embeddings and classical spectral metrics for interpretability or theory-driven probing.