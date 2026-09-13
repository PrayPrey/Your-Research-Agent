# SANE: Scalable Autoencoder for Neural Embeddings (Hyper-Representations)

## Key Metadata
- **Authors:** Schürholt et al.
- **Year:** 2024
- **Venue:** ICML 2024
- **Core Contribution:** Scalable SSL autoencoder for learning weight-space representations from large heterogeneous model zoo populations.

## Section Summaries

### Abstract
Learning representations from populations of neural networks (hyper-representations) enables downstream tasks like property prediction and model generation. Prior work was limited to small homogeneous model families. SANE (Scalable Autoencoder for Neural Embeddings) scales SSL weight-space learning to large, heterogeneous model zoos by using a transformer-based autoencoder with chunked weight tokenization, enabling processing of networks with different architectures and sizes. SANE achieves strong property prediction performance across diverse model zoos.

### Introduction & Motivation
The Hyper-Representations line (Schürholt 2021, 2022) showed SSL on weight populations recovers hyperparameters, accuracy, and generalization gaps. The main bottleneck was homogeneity: prior methods required all networks to share the same architecture. With millions of diverse models on Hugging Face, a scalable heterogeneous approach is essential. SANE addresses this by tokenizing weight chunks and using a transformer to encode arbitrary-length sequences.

### Methodology
SANE uses a transformer encoder-decoder architecture. Weight tokenization: each weight tensor is split into fixed-size chunks (e.g., 256 elements), flattened, and projected to a token embedding. Position embeddings encode which layer and position each chunk comes from. The encoder processes the sequence of weight tokens via multi-head self-attention. The decoder reconstructs weight chunks from the latent code. Training: masked weight modeling (MAE-style) — randomly mask 75% of weight tokens, train the decoder to reconstruct masked tokens. No permutation or scale equivariance is enforced: the model learns implicit invariances from data augmentation (random permutations applied at training time as augmentation). Latent code: CLS token embedding used for downstream tasks. Fine-tuning: linear probe on frozen latent for property prediction.

### Experiments & Results
Datasets: MNIST model zoo (10k MLPs), FashionMNIST zoo (5k MLPs), heterogeneous multi-zoo (mixed architectures, 3 datasets, total ~30k models). Tasks: accuracy prediction, generalization gap, hyperparameter recovery (learning rate, batch size), model generation (sample from latent). Results: accuracy prediction R²=0.85 on MNIST zoo; on heterogeneous zoo R²=0.72, outperforming architecture-specific baselines. Generation quality: sampled models achieve within 3% accuracy of zoo mean. Key finding: scale of zoo data matters — more diverse zoo → better generalization of latent space.

### Discussion & Conclusion
SANE demonstrates SSL scaling to heterogeneous model populations. Primary limitation: no explicit symmetry enforcement — relies on data augmentation for permutation invariance, ignores scale symmetry entirely. The paper acknowledges that equivariance-by-construction would likely improve representation quality, especially for cross-architecture generalization. Future work listed: equivariant encoder, larger zoos (Hugging Face scale).

## Key Contributions
- Transformer-based weight tokenization enabling heterogeneous architecture processing
- Masked weight modeling pre-training (MAE analogue for weight space)
- Scalable SSL demonstrated on multi-zoo populations
- First property prediction generalization to unseen architecture families

## Potential Relevance
SANE's masked weight modeling objective is directly combinable with ScaleGMN's equivariant encoder. The key question: can the transformer tokenizer be replaced with an equivariant graph encoder (ScaleGMN-style) while preserving the masked modeling pre-training? The multi-zoo dataset construction in SANE is the exact training setup needed for Gap 1's unified SSL framework experiment.
