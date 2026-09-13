# Methodology

We now present the Difficulty-Normalized Saturation Index (DNSI), motivated by our key observation: benchmark saturation manifests as entropy compression in improvement patterns. We first define the metric, then justify each design decision.

## Overview

DNSI quantifies benchmark saturation by measuring the entropy of performance improvements over time, normalized by task difficulty:

$$\text{DNSI} = \frac{H(\Delta_{\text{observed}})}{H_{\text{expected}}(D)}$$

where $H(\Delta_{\text{observed}})$ is the entropy of observed improvement deltas and $H_{\text{expected}}(D)$ is the expected entropy given difficulty proxy $D$.

**Intuition:** A healthy benchmark exhibits diverse improvements — many research directions, substantial gains — producing high improvement entropy. A saturated benchmark shows clustered, incremental improvements — narrow optimization of similar approaches — producing low entropy. By normalizing by difficulty, we separate true saturation from benchmark hardness: a 100-class task naturally has different improvement dynamics than a 10-class task.

## DNSI Computation

### Step 1: Extract SOTA History

From PapersWithCode or equivalent repositories, we extract the time series of SOTA performance:

$$S = \{(t_1, p_1), (t_2, p_2), \ldots, (t_n, p_n)\}$$

where $t_i$ is the submission timestamp and $p_i$ is the reported performance (e.g., top-1 accuracy).

**Rationale:** PapersWithCode provides dense SOTA histories for major benchmarks, enabling entropy computation without proprietary data access.

### Step 2: Compute Improvement Deltas

We compute windowed improvement deltas using 6-month aggregation:

$$\Delta_w = \sum_{t_i \in w} (p_i - p_{i-1})^+$$

where $w$ indexes 6-month windows and $(x)^+ = \max(0, x)$ ensures we count only improvements.

**Rationale:** 6-month windowing smooths conference clustering (major venues release results in bursts) while preserving temporal dynamics. Counting only positive deltas focuses on genuine progress rather than noise.

### Step 3: Compute Improvement Entropy

We discretize deltas into bins and compute Shannon entropy:

$$H(\Delta) = -\sum_{b} p_b \log_2 p_b$$

where $p_b$ is the proportion of deltas falling in bin $b$.

**Rationale:** Entropy naturally captures the "diversity" of improvements. Diverse improvements (many approaches with varied gains) yield high entropy; concentrated improvements (similar approaches with small gains) yield low entropy.

### Step 4: Difficulty Normalization

We normalize by expected entropy given task difficulty:

$$H_{\text{expected}}(D) = \log_2(D)$$

where $D$ is a difficulty proxy. For image classification, we use the number of classes:

$$D_{\text{vision}} = N_{\text{classes}}$$

**Rationale:** A 100-class benchmark allows more diverse improvement patterns than a 10-class benchmark. Without normalization, raw entropy conflates saturation with task complexity. Information-theoretic bounds relate class count to achievable distinctions in the output space.

### Final DNSI Formula

$$\text{DNSI} = \frac{H(\Delta_{\text{observed}})}{\log_2(N_{\text{classes}})}$$

**Interpretation:**
- DNSI ≈ 1.0: Improvement entropy matches expected diversity — healthy benchmark
- DNSI < 0.5: Improvement entropy significantly below expected — saturated benchmark
- DNSI > 1.0: More diversity than expected — rapidly evolving benchmark

## Algorithm

**Algorithm 1: DNSI Computation**

```
Input: SOTA history S = {(t_i, p_i)}, difficulty proxy D
Output: DNSI value

1. Filter S to entries with t > t_min and valid performance
2. Compute deltas: Δ_i = max(0, p_i - p_{i-1}) for i > 1
3. Aggregate into 6-month windows: Δ_w = sum of deltas in window w
4. Discretize Δ_w into B bins (uniform width)
5. Compute probabilities: p_b = count(Δ in bin b) / total windows
6. Compute entropy: H = -sum(p_b * log2(p_b)) for p_b > 0
7. Compute expected entropy: H_exp = log2(D)
8. Return DNSI = H / H_exp
```

**Complexity:** O(n log n) for sorting SOTA entries by timestamp, O(n) for delta computation, O(W) for window aggregation where W = number of 6-month windows.

## Design Decisions

### Why 6-Month Windows?

Major ML conferences (NeurIPS, ICML, ICLR, ACL, CVPR) cluster submissions, creating artificial periodicity in raw SOTA histories. 6-month windows smooth this clustering while preserving the overall saturation signal. Sensitivity analysis (Appendix) confirms robustness to 3-12 month window sizes.

### Why Class Count as Difficulty Proxy?

For classification tasks, the number of classes provides an information-theoretic bound on output complexity. Alternative proxies (dataset size, human baseline, theoretical bounds) may improve normalization for non-classification tasks; we leave this extension to future work.

### Minimum History Requirements

We require >15 SOTA entries over >3 years to ensure sufficient data for reliable entropy estimation. Benchmarks with sparse histories produce unstable DNSI estimates and are excluded from analysis.

## Scope and Limitations

DNSI as currently defined applies to:
- Classification benchmarks with discrete class labels (providing natural difficulty proxy)
- Benchmarks with dense SOTA histories on PapersWithCode (>15 entries, >3 years)

DNSI does not currently handle:
- Generative tasks (no discrete class structure)
- NLP tasks without class-count equivalents (see Discussion for proposed extensions)
- Benchmarks with sparse or inconsistent SOTA tracking
