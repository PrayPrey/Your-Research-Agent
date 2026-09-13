# 2. Related Work

We organize prior work by the type of signal used for rank selection, showing that all existing approaches require training or calibration data, and identify the structural approach as a novel alternative.

## 2.1 Gradient-Based Adaptive Rank Methods

The dominant approach to per-layer rank selection uses gradient signals during training to estimate layer importance.

**AdaLoRA** [Zhang et al., 2023] parameterizes weight updates in singular value decomposition form and prunes singular values based on importance scores derived from gradient magnitudes. Its rank allocation is dynamic, changing during training. While effective, AdaLoRA requires training through the adaptive phase and carries substantial optimizer overhead. Critically, the singular values being pruned belong to $\Delta W$ (the learned update), not $W_0$ (the pretrained weights) — a fundamental architectural difference from our approach.

**DyLoRA** [Valipour et al., 2022] trains the LoRA adapter simultaneously across a range of ranks, enabling rank selection post-training by truncating the adapter. This eliminates grid search but still requires full training before the optimal rank is known.

**La-LoRA** [Chen et al., 2025] uses norm-based signals derived from layer activations during training to assign adaptive ranks. Like AdaLoRA, it requires in-training signals.

**LAARA** [Tripathi et al., 2026] provides a formal theoretical foundation for per-layer allocation using Fisher information and proves that uniform rank is suboptimal. Its implementation uses gradient warmup to estimate layer importance, followed by allocation. LAARA is the closest theoretical peer: it proves that per-layer allocation is optimal, while we investigate whether the allocation can be derived from $W_0$ alone.

**IGU-LoRA** [Jiang et al., 2026] identifies a gradient bias in AdaLoRA's importance scores and proposes integrated gradient corrections. This motivates $W_0$-based approaches: if gradient-based signals are biased, structural signals may be more reliable.

## 2.2 Calibration-Based Methods

A second family uses a calibration pass over representative data before fine-tuning.

**IFCLoRA** [Zhang et al., 2026] is the closest methodological peer to our work. It computes per-layer importance from Information Flow Centrality (IFC) scores derived from a calibration forward pass. IFCLoRA demonstrates that pre-fine-tuning signals can predict rank need, motivating our hypothesis. The key difference: IFCLoRA requires calibration data and a forward pass; erank requires only the pretrained weight matrices. We view IFCLoRA as validating the principle and erank as testing its zero-data extreme.

## 2.3 Structural Methods: W₀ as Initialization

A third family uses $W_0$'s singular structure, but for adapter initialization rather than rank selection.

**PiSSA** [Meng et al., 2024] initializes LoRA matrices $A, B$ from the principal singular vectors of $W_0$, achieving faster convergence than random initialization. Rank is still set uniformly; the SVD of $W_0$ informs initialization, not rank.

**LoRA-XS** [Banaei et al., 2024] freezes the full $W_0$ SVD as a structured matrix and trains only a small $r \times r$ core adapter. Like PiSSA, it uses $W_0$ structure for adapter design, not for rank selection.

These works establish that $W_0$'s singular structure contains adaptation-relevant information but do not test whether it predicts optimal per-layer rank.

## 2.4 Intrinsic Dimensionality of Pretrained Representations

**Aghajanyan et al.** [2021] showed that the intrinsic dimensionality of fine-tuning loss landscapes varies by layer, with $d_{90}$ (dimension containing 90% of gradient variance) differing substantially between attention and FFN layers. This is the foundational motivation for our hypothesis: if intrinsic dimensionality varies by layer, and erank of $W_0$ captures the geometric complexity shaped by pretraining, erank may proxy for $d_{90}$.

## 2.5 Effective Rank as a Matrix Metric

**Roy and Vetterli** [2007] define effective rank $\text{erank}(A) = \exp(H(\sigma/\|\sigma\|_1))$ where $H$ is Shannon entropy. This metric is bounded $[1, \text{rank}(A)]$, scale-invariant (depending only on singular value ratios), and provides wider dynamic range than stable rank or nuclear/spectral norm ratios. Prior work on LoRA has used spectral entropy [Aghajanyan et al., 2021] and stable rank [Tian et al., 2026] as structural metrics; we use erank for its superior normalization properties.

## 2.6 Our Position

We are the first to test whether $\text{erank}(W_0)$ — a single number computed from pretrained weights before any fine-tuning — correlates significantly with per-layer PARA oracle ranks. This places us in a novel position: using structural weight geometry as a zero-cost, zero-data rank predictor, motivated by IFCLoRA's success with calibration-based signals and grounded in the intrinsic dimensionality results of Aghajanyan et al. [2021].
