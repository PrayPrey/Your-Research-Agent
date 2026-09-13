# 3. Methodology

Our approach rests on a key observation: if LLaMA-3.1-8B's activation sparsity profile reflects
pre-training geometry rather than input content, it should be (a) significantly heterogeneous
across layers, (b) stable across calibration distributions, and (c) invariant to epsilon threshold
choice. These three properties together constitute a testable definition of a "reliable structural
fingerprint." We design our methodology to test each property with appropriate statistical rigor.

## 3.1 Sparsity Measurement

**Motivation.** We measure layer-wise MLP activation sparsity as the fraction of activations below
a near-zero threshold $\varepsilon$. The SiLU gating function in LLaMA's MLP layers creates
soft-thresholded outputs: for each layer $\ell$, we measure
$$s_\ell(\varepsilon) = \frac{1}{|S|} \sum_{x \in S} \frac{1}{d_{\text{ffn}}} \sum_{j=1}^{d_{\text{ffn}}} \mathbf{1}\left[|\text{gate\_proj}_\ell(x)_j| < \varepsilon\right],$$
where $S$ is a set of 512 calibration samples and $d_{\text{ffn}}$ is the feed-forward
intermediate dimension. This measures the proportion of near-zero intermediate activations in
each MLP block's gating layer.

**Implementation.** Sparsity is measured using PyTorch forward hooks attached to the
\texttt{gate\_proj} layer of each of the 32 MLP blocks in LLaMA-3.1-8B. Hooks accumulate
activation tensors across the calibration batch; no gradient computation is required. The model
is loaded in float16 with \texttt{device\_map=auto} for memory efficiency. The measurement
pipeline executes a single forward pass per dataset condition, requiring no training.

**Primary epsilon.** Following H-E1 results (cross-epsilon $\tau > 0.96$), we use $\varepsilon = 0.01$
as the primary threshold. All results are reported at $\varepsilon = 0.01$; Section~5.3 reports
full sensitivity across $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$.

**Figure~\ref{fig:rank_correlation} (rank\_correlation.png)** illustrates the rank correlation
between Alpaca and WikiText-103 sparsity profiles ($\tau=0.786$), motivating our cross-distribution
stability analysis.

## 3.2 Cross-Distribution Stability Protocol

**Motivation.** A sparsity fingerprint is useful as a practical prior only if it is stable across
arbitrary calibration datasets — practitioners should not need to match calibration to fine-tuning
task. We test four distributions chosen to span a wide range of domains: Alpaca (instruction
following), WikiText-103 (general web text), SST-2 validation (sentiment classification), and
MNLI validation (natural language inference). This breadth allows us to distinguish
architecture-intrinsic stability from domain-specific correlation.

**Protocol.**
\begin{enumerate}
  \item Measure the 32-dimensional sparsity profile $\mathbf{s}^{(d)} = [s_1^{(d)}, \ldots, s_{32}^{(d)}]$
    for each distribution $d \in \{\text{Alpaca}, \text{WikiText}, \text{SST-2}, \text{MNLI}\}$.
  \item Compute the intraclass correlation coefficient ICC$(3,k)$ \citep{shrout1979intraclass}
    across all four distributions. ICC$(3,k)$ measures the proportion of variance attributable
    to systematic between-layer differences versus noise — values $>0.75$ indicate good to
    excellent reliability.
  \item Compute all $\binom{4}{2} = 6$ pairwise Kendall's $\tau$ between distribution profiles.
    Kendall's $\tau$ is robust to monotone transformation and measures rank concordance, which
    is the property relevant for rank allocation ordering decisions.
\end{enumerate}

**Gate threshold.** ICC$(3,k) > 0.75$ and all six pairwise $\tau \geq 0.6$. These thresholds
follow psychometric conventions for "good" reliability \citep{koo2016guideline}.

**Design rationale.** We use ICC$(3,k)$ rather than Pearson $r$ because ICC accounts for
all four distributions simultaneously, provides confidence intervals, and has an established
psychometric interpretation. Pairwise $\tau$ is reported to allow inspection of which
distribution pairs are most correlated — specifically, whether instruction-tuned and general
text domains differ (they do, but remain above threshold).

## 3.3 Epsilon Threshold Invariance Protocol

**Motivation.** The epsilon parameter controls what fraction of activations count as "near-zero."
If practitioners must tune $\varepsilon$ to obtain a reliable fingerprint, the method loses
much of its practical appeal. We characterize threshold invariance explicitly.

**Protocol.**
\begin{enumerate}
  \item Measure sparsity profiles at four epsilon values: $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$.
  \item Compute all $\binom{4}{2} = 6$ cross-epsilon pairwise Kendall's $\tau$ between profiles.
  \item Report the minimum tau and the full $4 \times 4$ matrix.
\end{enumerate}

**Gate threshold.** Maximum adjacent-pair $\tau \geq 0.7$ (conservative; we require at least
monotone consistency between neighboring epsilon values). In practice, we report all-pair tau.

**Design rationale.** We include both fine ($\varepsilon = 0.001$) and coarse ($\varepsilon = 0.1$)
thresholds — spanning two orders of magnitude. Threshold invariance at this range provides
strong practical reassurance that epsilon does not need to be tuned.

## 3.4 Layer Heterogeneity Analysis

To confirm that the sparsity profile contains information (is not degenerate), we compute the
coefficient of variation $\text{CV} = \sigma / \mu$ across all 32 layers for each condition.
A CV $>0.3$ indicates meaningful cross-layer variation that could inform non-uniform allocation.
We also examine the per-layer profile for systematic structure — specifically, whether a depth
gradient (early layers vs. deep layers) exists across conditions.

## 3.5 Model and Calibration Details

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Llama-3.1-8B (float16, device\_map=auto) |
| GPU | NVIDIA H100 NVL (100 GB VRAM) |
| Calibration size | 512 samples per distribution |
| Sequence length | 512 tokens (max\_length) |
| Target layer | \texttt{gate\_proj} of each of 32 MLP blocks |
| Epsilon values | \{0.001, 0.01, 0.05, 0.1\} |
| Datasets | tatsu-lab/alpaca, wikitext-103-raw-v1, SetFit/sst2, nyu-mll/multi\_nli |

Note: LLaMA-3.1-8B was used in lieu of the originally specified LLaMA-3-8B due to model cache
availability. The architectures are functionally identical for the purposes of this study.

## 3.6 Connection to Rank Allocation (Future Work)

The validated sparsity fingerprint $\mathbf{s} = [s_1, \ldots, s_{32}]$ defines a natural
inverse-sparsity rank allocation: layers with lower sparsity (more active, potentially
higher-dimensional) receive higher rank, and vice versa. Under a fixed total parameter budget
$B = 0.60 \times \sum_\ell r_\ell^{\text{uniform}}$ (60\% of uniform $r=16$), the allocation is:
$$r_\ell^{\text{sparse}} = \text{round}\left(r_{\max} \cdot \frac{1 - s_\ell}{\max_k (1 - s_k)}\right), \quad \text{subject to } \sum_\ell r_\ell = B.$$
Whether this allocation achieves $\geq 95\%$ of oracle performance is the central question of
H-M3 (sparsity-rank correlation) and H-M4 (end-to-end performance) — both identified as
immediate future work in Section~6.
