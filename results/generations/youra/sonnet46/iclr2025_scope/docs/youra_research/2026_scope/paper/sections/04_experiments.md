# 4. Experimental Setup

We design three experiments to answer the following research questions, each testing one facet
of the structural fingerprint claim:

**RQ1 (Heterogeneity):** Do LLaMA-3.1-8B MLP layers exhibit significantly different activation
sparsity (CV$>0.3$), and is the initial two-distribution rank ordering stable (Kendall's
$\tau_{\text{calibration}} \geq 0.6$)?

**RQ2 (Cross-Distribution Stability):** Is the sparsity profile stable across four diverse
calibration distributions, as measured by ICC$(3,k) > 0.75$ and all six pairwise $\tau \geq 0.6$?

**RQ3 (Threshold Invariance):** Is the layer rank ordering invariant to epsilon threshold choice
across $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$, as measured by maximum adjacent-pair
$\tau \geq 0.7$?

Each RQ corresponds directly to a contribution claim in the Introduction and to a gate condition
in our verification pipeline (H-E1, H-M1, H-M2 respectively).

## 4.1 Model

All experiments use **meta-llama/Llama-3.1-8B** (uninstruction-tuned base model, float16,
\texttt{device\_map=auto}), loaded from local cache to avoid authentication dependencies.
Activation sparsity is measured exclusively in inference mode (no gradients). The GPU used is
an NVIDIA H100 NVL with 100 GB VRAM; VRAM utilization is approximately 18.4 GB.

## 4.2 Calibration Datasets

We use four calibration datasets chosen to span a range of domains and styles:

| Dataset | Source | Domain | Samples | Selection |
|---------|--------|---------|---------|-----------|
| Alpaca | tatsu-lab/alpaca | Instruction following | 512 | Random first 512 |
| WikiText-103 | wikitext-103-raw-v1 | General web text | 512 | First 512 chunks |
| SST-2 val | SetFit/sst2 (val split) | Sentiment classification | 512 | Full validation set |
| MNLI val | nyu-mll/multi\_nli (validation\_matched) | Natural language inference | 512 | First 512 samples |

**Dataset rationale:** Alpaca and WikiText-103 are commonly used for calibration in sparsity-based
methods (e.g., TEAL, SparseGPT); we include them as the primary pair (RQ1). SST-2 and MNLI are
the fine-tuning task domains from the main hypothesis — including them tests whether task-domain
data changes the fingerprint (RQ2). The breadth from general web text to instruction-following
to classification tasks provides a demanding test of distribution stability.

All datasets are processed with \texttt{max\_length=512} tokens, padding/truncating as needed.

## 4.3 Sparsity Measurement Implementation

Sparsity is measured using forward hooks attached to the \texttt{gate\_proj} module of each of
the 32 MLP blocks (layers 0–31). For each calibration sample, the hook records the full
intermediate activation tensor; we then compute the fraction below $\varepsilon$ across all
elements. Batch size is 8 (64 forward passes per dataset condition). A \texttt{finally} block
ensures hooks are removed after measurement — no orphaned state persists between conditions.

The complete pipeline executes in approximately 5 minutes per condition on H100.

## 4.4 Evaluation Metrics

**Experiment 1 (RQ1 — Heterogeneity, H-E1):**
- Coefficient of Variation (CV): $\sigma / \mu$ across 32 layer sparsity values. Gate: CV$>0.3$.
- Kendall's $\tau_{\text{calibration}}$: rank correlation between Alpaca and WikiText-103 profiles.
  Gate: $\tau \geq 0.6$.
- $\tau_{\text{length}}$: rank correlation across short (128-token) vs. long (512-token) inputs.
  Secondary metric.

**Experiment 2 (RQ2 — Stability, H-M1):**
- ICC$(3,k)$: intraclass correlation across all four distributions simultaneously. Computed via
  pingouin 0.6.1 with type "ICC(C,k)". Gate: ICC$>0.75$.
- All 6 pairwise Kendall's $\tau$ (C$(4,2)$=6 pairs). Gate: all $\tau \geq 0.6$.
- Sensitivity: ICC and $\tau_{\min}$ reported for each $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$.

**Experiment 3 (RQ3 — Threshold Invariance, H-M2):**
- CV per epsilon: Gate: CV$>0.3$ for $\geq 3/4$ values.
- Cross-epsilon $\tau$: all 6 pairs from $\varepsilon \in \{0.001, 0.01, 0.05, 0.1\}$.
  Gate: maximum adjacent-pair $\tau \geq 0.7$.
- Cross-distribution $\tau$ (Alpaca vs. WikiText) at each $\varepsilon$: secondary metric.

Statistical significance for all Kendall's $\tau$ values is reported via scipy \texttt{kendalltau}
two-tailed $p$-values (variant='b' for tie correction).

## 4.5 Reproducibility

All measurement code is implemented in Python 3.10 using PyTorch, HuggingFace Transformers,
pingouin 0.6.1 for ICC, and scipy.stats for Kendall's $\tau$. Conda environments are
\texttt{youra-h-e1}, \texttt{youra-h-m1}, \texttt{youra-h-m2}. Experiments are deterministic
(no sampling in sparsity measurement). Random seeds are not needed for the measurement step.
