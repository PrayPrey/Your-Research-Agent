# Research Idea

## Title
IB-FAIR-SYNTH: Information Bottleneck with Ensemble Teacher Distillation for Privacy-Fair Synthetic Tabular Data Generation

## Motivation
Synthetic data generation promises to address data scarcity, privacy, and fairness challenges in high-stakes ML applications. However, existing approaches optimize these objectives separately, creating fundamental conflicts—privacy mechanisms often suppress minority group information needed for fairness. Current LLM-based tabular generators achieve high fidelity but neglect privacy-fairness trade-offs, while privacy/fairness research focuses on discriminative rather than generative settings. A unified framework that simultaneously achieves differential privacy, demographic fairness, and data utility remains an open challenge.

## Main Idea
We propose IB-FAIR-SYNTH, a framework combining variational Information Bottleneck (IB) compression with ensemble teacher distillation for LLM-based tabular data generation. The core mechanism operates in four stages: (1) LLM encodes tabular data into sequence representations, (2) IB layer compresses representations to suppress individual-identifying and sensitive-attribute information while preserving task-relevant features, (3) specialized privacy and fairness teachers optimize their respective objectives independently, and (4) weighted distillation balances both teachers into a unified student generator.

We will validate on standard fairness benchmarks (Adult, COMPAS, German Credit) measuring: differential privacy (ε ≤ 8.0), fairness (SPD < 0.1), and utility (accuracy within 5% of baseline). The key testable prediction is that ensemble distillation resolves privacy-fairness conflicts that naive sequential approaches cannot, enabling trustworthy synthetic data for sensitive domains like healthcare and finance.