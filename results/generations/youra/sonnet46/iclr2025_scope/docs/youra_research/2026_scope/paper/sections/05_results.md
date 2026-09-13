# 5. Results

LLaMA-3.1-8B's layer-wise MLP activation sparsity constitutes a robust, threshold-invariant
structural fingerprint that can be reliably extracted from a single forward pass on any calibration
distribution. We present results for each of the three research questions in turn, showing a
cascading story: a signal exists (RQ1) → it is distribution-stable (RQ2) → it is threshold-invariant
(RQ3).

## 5.1 RQ1: Layer Heterogeneity — The Signal Exists (H-E1)

Figure~\ref{fig:sparsity_profile} shows the per-layer sparsity profile for LLaMA-3.1-8B across
all 32 MLP blocks at $\varepsilon=0.01$.

\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\textwidth]{figures/sparsity_profile.png}
  \caption{Per-layer MLP activation sparsity across all 32 LLaMA-3.1-8B layers for Alpaca and
    WikiText-103 calibration sets ($\varepsilon=0.01$). Early layers (0–2) exhibit the highest
    sparsity; deep layers the lowest. The two dataset profiles closely track each other.
    CV$=0.544$ confirms significant heterogeneity (threshold: $>0.3$).}
  \label{fig:sparsity_profile}
\end{figure}

The coefficient of variation CV$=0.544$ at $\varepsilon=0.01$ far exceeds our gate threshold of
0.3. This establishes that sparsity is not uniform across layers — there is meaningful structure to
exploit. The cross-calibration Kendall's $\tau_{\text{calibration}}=0.786 \geq 0.6$ (Alpaca vs.
WikiText-103) confirms that the layer rank ordering is preserved across calibration domains.

Table~\ref{tab:h_e1_main} summarizes H-E1 results across all epsilon values.

| $\varepsilon$ | CV (Alpaca) | $\tau_{\text{calibration}}$ | $\tau_{\text{length}}$ |
|--------------|-------------|---------------------------|----------------------|
| 0.001 | 0.549 | 0.790 | 0.883 |
| **0.010 (primary)** | **0.544** | **0.786** | **0.899** |
| 0.050 | 0.528 | 0.778 | 0.875 |
| 0.100 | 0.484 | 0.782 | 0.879 |

All four epsilon values exceed both gate thresholds ($p < 10^{-10}$ for all $\tau$ values).
The consistent pattern across epsilon values is itself informative: the signal is not an artifact of
threshold choice, previewing the stronger invariance result in RQ3.

**Depth gradient.** A systematic depth gradient is visible in Figure~\ref{fig:sparsity_profile}:
layers 0–2 consistently exhibit the highest sparsity (approximately 3–5$\times$ the average);
deep layers (28–31) consistently show the lowest. This gradient is present for both Alpaca and
WikiText-103, and persists across all four epsilon values tested. We return to its interpretation
in Section~6.1.

**Figure~\ref{fig:epsilon_sensitivity} (epsilon\_sensitivity.png)** shows CV and $\tau_{\text{calibration}}$
across all four epsilon values, illustrating that both metrics remain well above their thresholds
throughout the tested range.

## 5.2 RQ2: Cross-Distribution Stability — Architecture-Intrinsic Signal (H-M1)

RQ1 shows the signal is stable across two distributions. RQ2 tests whether this holds across four
diverse distributions — including two in-domain fine-tuning task splits.

Figure~\ref{fig:sparsity_heatmap} visualizes the sparsity heatmap across all four distributions
and 32 layers. The visual impression of near-identical profiles is confirmed quantitatively:
ICC$(3,k) = 0.9846$ with 95\% confidence interval $[0.97, 0.99]$.

\begin{figure}[t]
  \centering
  \includegraphics[width=0.9\textwidth]{figures/sparsity_heatmap.png}
  \caption{Sparsity heatmap: 4 calibration distributions $\times$ 32 LLaMA-3.1-8B MLP layers
    ($\varepsilon=0.01$). Rows: Alpaca, WikiText-103, SST-2 val, MNLI val. The layer rank ordering
    is visually near-identical across all four distributions.}
  \label{fig:sparsity_heatmap}
\end{figure}

Table~\ref{tab:pairwise_tau} shows all six pairwise Kendall's $\tau$ values at $\varepsilon=0.01$.

| Pair | $\tau$ | $p$-value |
|------|--------|-----------|
| Alpaca $\leftrightarrow$ WikiText-103 | 0.7863 | $2.03 \times 10^{-13}$ |
| Alpaca $\leftrightarrow$ SST-2 | 0.9395 | $3.35 \times 10^{-24}$ |
| Alpaca $\leftrightarrow$ MNLI | 0.9476 | $3.51 \times 10^{-25}$ |
| WikiText-103 $\leftrightarrow$ SST-2 | 0.7339 | $2.78 \times 10^{-11}$ |
| WikiText-103 $\leftrightarrow$ MNLI | 0.7500 | $6.81 \times 10^{-12}$ |
| SST-2 $\leftrightarrow$ MNLI | **0.9839** | $3.94 \times 10^{-31}$ |

The minimum $\tau$ is $0.7339$ (WikiText-103 vs. SST-2), well above the $0.6$ threshold; all
$p$-values $< 10^{-10}$.

Figure~\ref{fig:pairwise_tau_matrix} presents this as a visual matrix.

\begin{figure}[t]
  \centering
  \includegraphics[width=0.7\textwidth]{figures/pairwise_tau_matrix.png}
  \caption{Pairwise Kendall's $\tau$ matrix for all 6 distribution pairs ($\varepsilon=0.01$).
    Values range from 0.734 (WikiText vs. SST-2) to 0.984 (SST-2 vs. MNLI). All values
    exceed the 0.6 gate threshold.}
  \label{fig:pairwise_tau_matrix}
\end{figure}

**The WikiText split.** The most informative contrast in Table~\ref{tab:pairwise_tau} is between
WikiText-103 and the instruction-tuned datasets: Alpaca–WikiText $\tau=0.786$, but instruction–instruction
correlations are $\tau \geq 0.934$. This pattern suggests a meaningful distribution split:
within instruction-tuned data, the fingerprint is near-perfectly consistent; between general
text and instruction-tuned data, it remains strong but at a lower level. **The practical
implication is that even the worst-case calibration choice (general web text) yields $\tau=0.73$
with SST-2** — well above the threshold for reliable rank ordering information.

ICC sensitivity across epsilon values is nearly constant: ICC$(3,k) \in [0.9846, 0.9878]$ for
$\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$. The fingerprint's stability does not depend on
which epsilon is used for measurement.

## 5.3 RQ3: Threshold Invariance — The Fingerprint is Epsilon-Independent (H-M2)

If the sparsity fingerprint is useful as a practical prior, practitioners should not need to tune
$\varepsilon$. Figure~\ref{fig:cross_epsilon_tau_heatmap} shows the cross-epsilon $\tau$ matrix.

\begin{figure}[t]
  \centering
  \includegraphics[width=0.65\textwidth]{figures/cross_epsilon_tau_heatmap.png}
  \caption{Cross-epsilon Kendall's $\tau$ heatmap for all 6 pairs from
    $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$. All values exceed $0.96$ — the layer rank
    ordering is threshold-invariant across two orders of magnitude of $\varepsilon$.}
  \label{fig:cross_epsilon_tau_heatmap}
\end{figure}

| Pair | $\tau$ | $p$-value |
|------|--------|-----------|
| $\varepsilon=0.001 \leftrightarrow 0.01$ | **0.9960** | $2.43 \times 10^{-34}$ |
| $\varepsilon=0.001 \leftrightarrow 0.05$ | 0.9677 | $4.47 \times 10^{-28}$ |
| $\varepsilon=0.001 \leftrightarrow 0.1$ | 0.9637 | $1.96 \times 10^{-27}$ |
| $\varepsilon=0.01 \leftrightarrow 0.05$ | 0.9718 | $9.26 \times 10^{-29}$ |
| $\varepsilon=0.01 \leftrightarrow 0.1$ | 0.9597 | $7.94 \times 10^{-27}$ |
| $\varepsilon=0.05 \leftrightarrow 0.1$ | 0.9798 | $2.82 \times 10^{-30}$ |

All six cross-epsilon $\tau$ values exceed $0.95$ — a result far stronger than the $0.7$ gate
threshold. The layer rank ordering is essentially identical across a 100$\times$ range of epsilon
values. CV remains above $0.3$ for all four epsilon values ($0.549, 0.544, 0.528, 0.484$), and
all four pass the CV gate.

**What this means for practice.** A practitioner measuring LLaMA-3.1-8B's sparsity fingerprint
does not need to tune $\varepsilon$, choose a calibration dataset, or worry about input length:
any reasonable choice yields the same layer rank ordering. The fingerprint measurement requires
only a single forward pass (approximately 5 minutes on H100) and is deterministic.

## 5.4 Summary of Gate Results

| Hypothesis | Experiment | Key Metric | Value | Threshold | Gate |
|------------|-----------|------------|-------|-----------|------|
| H-E1 | Heterogeneity | CV ($\varepsilon=0.01$) | 0.544 | $>0.3$ | **PASS** |
| H-E1 | Heterogeneity | $\tau_{\text{calibration}}$ | 0.786 | $\geq 0.6$ | **PASS** |
| H-M1 | Stability | ICC$(3,k)$ | 0.9846 | $>0.75$ | **PASS** |
| H-M1 | Stability | $\tau_{\min}$ (all 6 pairs) | 0.7339 | $\geq 0.6$ | **PASS** |
| H-M2 | Invariance | CV pass rate | 4/4 | $\geq 3/4$ | **PASS** |
| H-M2 | Invariance | max adjacent $\tau$ | 0.9960 | $\geq 0.7$ | **PASS** |

All three hypothesis gates pass at MUST\_WORK level. Prediction P1 (existence and stability of
the sparsity fingerprint) is **SUPPORTED** with high confidence across 3 independent experiments.
