# Research Idea

## Title
HITM: Curvature-Guided Hebbian Memory for Efficient Long-Range Temporal Graph Learning

## Motivation
Temporal graph learning faces a fundamental trade-off: capturing long-range dependencies (weeks-scale) typically requires O(T²) attention complexity, limiting scalability. Existing solutions either sacrifice adaptability through pre-computation (BigST) or ignore structural importance in temporal selection. We observe that structurally significant events—identifiable through graph curvature changes—carry disproportionate predictive information. This insight enables selective memory consolidation that achieves linear complexity while preserving critical temporal patterns.

## Main Idea
We propose HITM (Hebbian-Inspired Temporal Memory), a module that augments existing spatial-temporal GNNs through a biologically-inspired four-step mechanism: (1) compute Ollivier-Ricci curvature changes to detect structurally important events, (2) selectively consolidate high-curvature events into a compact memory bank via Hebbian learning rules, (3) retrieve relevant historical context through sparse top-k attention, and (4) integrate retrieved information for enhanced prediction.

The core hypothesis is that curvature-guided selection identifies temporally predictive events more effectively than uniform attention, enabling O(n) complexity scaling. We will validate on traffic forecasting benchmarks (METR-LA, PEMS-BAY), targeting ≥10% MAE improvement over STGCN baselines while demonstrating linear time scaling. Ablation studies will isolate each mechanism's contribution. Success would establish curvature as a principled criterion for temporal importance and provide a scalable framework for week-scale forecasting in dynamic networks.