## Title
Versioned Living Benchmarks: Automated Saturation Detection for Sustainable ML Evaluation

## Motivation
ML benchmarks suffer from saturation—as models increasingly overfit to static datasets, performance variance compresses and benchmarks lose discriminative power. Despite awareness, benchmark concentration continues increasing due to structural incentives favoring familiar datasets. Current solutions require unsustainable manual curation effort. This research addresses a critical gap: how to automatically detect benchmark staleness and trigger principled dataset evolution while preserving historical comparability.

## Main Idea
We propose Versioned Living Benchmarks (VLB), a framework where automated variance monitoring triggers epoch transitions when benchmark saturation occurs. The core mechanism: continuous tracking of top-k model performance variance detects compression below a threshold (0.5× baseline), signaling saturation. This triggers an epoch transition introducing fresh data, restoring benchmark discriminative power while semantic versioning preserves cross-temporal comparability.

Key methodology: (1) implement variance-based saturation detection on tabular benchmarks, (2) validate that epoch transitions restore performance variance (>0.5× baseline, p<0.05), and (3) confirm cross-temporal rank correlation remains >0.7 across epochs via dual scoring.

Expected outcomes include sustainable benchmark maintenance with reduced manual overhead, preserved historical model comparisons, and a replicable framework for major repositories (OpenML, HuggingFace). If successful, VLB provides principled infrastructure for evolving benchmarks that remain relevant without sacrificing reproducibility.