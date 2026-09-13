# 3. Methodology

Our benchmark design has one central goal: isolate the contribution of permutation-equivariant
inductive bias from capacity effects. This requires (1) matching encoder capacity across
architecturally dissimilar encoders, (2) measuring not just downstream performance ($\rho$)
but also the underlying mechanism (permutation sensitivity), and (3) mapping the full
symmetry spectrum rather than comparing only the extremes. We describe each component below.

## 3.1 Problem Formulation

Let $\mathcal{Z} = \{(w_i, a_i)\}_{i=1}^N$ denote a model zoo, where $w_i$ is the weight
tensor of the $i$-th trained network and $a_i \in [0,1]$ is its ground-truth test accuracy.
A weight-space encoder $f_\theta: \mathcal{W} \to \mathbb{R}^d$ maps weight tensors to
fixed-size embeddings, from which a prediction head $g_\psi: \mathbb{R}^d \to \mathbb{R}$
predicts accuracy. We evaluate encoder quality using Spearman rank correlation:

$$\rho = \text{Spearman}(\{g_\psi(f_\theta(w_i))\}_{i=1}^N, \{a_i\}_{i=1}^N)$$

For feedforward networks with $L$ hidden layers of widths $n_1, \ldots, n_L$, any permutation
$\pi_\ell \in S_{n_\ell}$ of neurons in layer $\ell$ produces a weight configuration $\sigma(w)$
that implements the same function as $w$. The size of the permutation orbit is
$\prod_{\ell=1}^L n_\ell!$, which grows factorially with network depth and width. A flat MLP
encoder receiving any $\sigma(w)$ as a distinct input vector must either learn to map all
orbit members to the same embedding (consuming capacity) or assign different embeddings to
functionally-identical networks (degrading prediction quality).

## 3.2 Encoder Architectures

We compare three encoders representing increasing levels of symmetry exploitation.

**Flat MLP (no symmetry exploitation).** Following Unterthiner et al. [2020], we concatenate
all weight tensors into a single vector $\mathbf{w}_{\text{flat}} \in \mathbb{R}^{2464}$
(for the Schurholt MNIST-CNN architecture) and pass it through a fully-connected MLP with
hidden dimensions $[193]$ and output embedding dimension 128. The hidden width 193 is
determined by the capacity matching grid search to achieve $\sim$500K total parameters.
This architecture has no structural constraint that encourages permutation invariance.

**Deep Sets (permutation-invariant).** We implement a Deep Sets encoder [Zaheer et al., 2017]
at the neuron level: a shared per-neuron MLP $\phi$ processes each neuron's weight vector
independently, and the resulting representations are summed across neurons to produce a
permutation-invariant embedding. The per-neuron MLP uses hidden dimension $\phi_{\text{hidden}} = 256$
(471,936 total parameters), providing permutation *invariance* — the embedding is unchanged
under any neuron permutation — but not equivariance.

**NFN (permutation-equivariant).** We implement the equivariant weight-space network of
Navon et al. [2023], which defines equivariant linear maps between spaces of weight tensors.
For the MNIST-CNN architecture, weight tensors have shapes $(32, 1, 3, 3)$, $(32,)$,
$(64, 32, 3, 3)$, $(64,)$, $(128, 1024)$, $(128,)$, $(10, 128)$, $(10,)$.
The NFN encoder uses $n_\text{layers} = 3$ equivariant layers with $\text{channel\_dim} = 112$,
yielding 521,953 total parameters. By construction, permuting neurons in the target network
produces a corresponding permutation in the NFN's internal representations, and the final
invariant embedding (obtained by summing over neuron dimensions) is identical for all
permutation-equivalent weight configurations.

## 3.3 Capacity Matching

Matching parameter counts across fundamentally different architectures requires per-architecture
grid search. We define the target range as $[475\text{K}, 525\text{K}]$ parameters ($500\text{K} \pm 5\%$).

For the **flat MLP**, we grid-search the single hidden layer width over integer values; the
width $h = 193$ achieves 500,577 parameters for a 2,464-dim input with embedding dim 128.

For **Deep Sets**, we grid-search $\phi_{\text{hidden}}$ over $\{128, 192, 256, 320\}$;
$\phi_{\text{hidden}} = 256$ achieves 471,936 parameters (within range).

For the **NFN**, we jointly grid-search \{channel\_dim, n\_layers\} over
$\text{channel\_dim} \in \{24, 32, 40, 48, 56, 112\}$ and $n\_layers \in \{2, 3, 4\}$;
channel\_dim = 112, n\_layers = 3 achieves 521,953 parameters (within range).

All three encoders are within the $\pm5\%$ target range (Table 1).

**Table 1:** Encoder capacity summary.

| Encoder | Architecture | Parameters | In Range? |
|---------|-------------|------------|-----------|
| Flat MLP | hidden\_dims=[193], embed\_dim=128 | 500,577 | ✓ |
| Deep Sets | $\phi_{\text{hidden}}$=256, embed\_dim=128 | 471,936 | ✓ |
| NFN | channel\_dim=112, n\_layers=3 | 521,953 | ✓ |

## 3.4 Permutation Sensitivity Score

To directly measure the capacity-wasting mechanism, we define a permutation sensitivity
score that quantifies whether an encoder distinguishes functionally-equivalent weight
configurations.

**Construction.** We first identify permutation-equivalent model pairs: networks in the same
accuracy decile with high cosine distance in weight space (cosine\_distance $> 0.1$), serving
as empirical proxies for permutation-equivalent but distinctly-represented weight configurations.
For each such pair $(w, \sigma(w))$, we apply a random neuron permutation $\sigma$ to the
weight tensors of the first model to generate the second.

**Sensitivity score.** For $n = 500$ sampled pairs, we compute:

$$\text{sensitivity\_score} = \frac{\mathbb{E}[\|f(w) - f(\sigma(w))\|_2]}{\mathbb{E}[\|f(w) - f(w')\|_2]}$$

where the numerator is the mean L2 distance between embeddings of permutation-equivalent
pairs $(w, \sigma(w))$, and the denominator is the mean L2 distance between embeddings of
random non-equivalent pairs $(w, w')$ sampled across accuracy deciles. A score near 0 indicates
the encoder maps permutation-equivalent weights to identical embeddings (equivariant);
a score near 1 indicates it cannot distinguish them from random pairs.

Figure 7 shows the distribution of cosine distances between same-accuracy-decile model pairs
in the MNIST-CNN zoo, confirming the empirical basis for the sensitivity probe.

## 3.5 Training Protocol

All three encoders are trained under identical conditions to ensure a fair comparison:

- **Optimizer:** Adam [Kingma \& Ba, 2015], $\beta_1 = 0.9$, $\beta_2 = 0.999$
- **Learning rate:** $10^{-3}$ with cosine annealing to $\eta_{\min} = 10^{-6}$ over 150 epochs
- **Batch size:** 32
- **Weight decay:** $10^{-4}$
- **Training epochs:** 150 (same for all encoders)
- **Loss:** Mean squared error on accuracy prediction
- **Random seed:** 42

The dataset is the Schurholt et al. MNIST-CNN zoo (hyp\_rand variant), split into
train/test sets following the standard Schurholt et al. [2022] protocol. We use 2,249
training checkpoints in the hyp\_rand variant (976 for the seed-only subset used in H-E1).

## 3.6 Evaluation Protocol

We evaluate each encoder on the held-out test split using Spearman rank correlation $\rho$.
For the primary $\Delta\rho$ comparison (H-M3), we compute bootstrap 95% confidence intervals
using $n = 1{,}000$ resamples of the test set, reporting the 2.5th and 97.5th percentiles of
the bootstrap distribution of $\Delta\rho = \rho(\text{NFN}) - \rho(\text{flat MLP})$.

For the permutation sensitivity score (H-M1, H-M2), we sample 500 pairs stratified across
10 accuracy deciles (50 pairs per decile) and compute the sensitivity score for each encoder.
Gate criteria: flat MLP sensitivity $> 0.3$ (sensitivity PASS); NFN sensitivity $< 0.1$
(equivariance PASS).

Figure 8 shows the per-decile orbit proportion in the MNIST-CNN zoo (all deciles = 1.0),
confirming that the precondition for the sensitivity probe is universally satisfied.
