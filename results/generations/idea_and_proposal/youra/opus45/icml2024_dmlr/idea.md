# Research Idea

## Title
Marginal Value Data Curation: Compute-Aware Filtering via Proxy-Based Bayesian Threshold Optimization

## Motivation
Foundation model training faces a critical quality-quantity tradeoff: aggressive filtering improves data quality but reduces dataset size, while lenient filtering causes wasteful compute on low-value samples. Current approaches use fixed filtering thresholds regardless of compute budget, ignoring that optimal thresholds should adapt—larger budgets can tolerate more data since repetition penalties decrease. This gap between static curation and compute-aware optimization leaves significant efficiency gains unrealized.

## Main Idea
We propose Marginal Value Data Curation (MVDC), which dynamically optimizes filtering thresholds based on compute budget using pre-computed quality proxies. The core mechanism operates in three steps: (1) aggregate proxy signals (CLIP scores, perplexity) at cluster granularity for scalable value estimation, (2) apply Bayesian optimization over scaling law parameters to find the optimal threshold τ* under uncertainty, and (3) filter data adaptively to maximize performance-per-FLOP.

We will validate on DataComp-medium, targeting >38.5% ImageNet zero-shot accuracy (vs. 36% baseline) with <5% filtering overhead. Key predictions include monotonic threshold-compute relationships and 5-15% efficiency gains over fixed baselines. This approach bridges data valuation theory with practical foundation model training, enabling compute-aware curation at billion-scale without expensive gradient-based methods.