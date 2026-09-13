# Title
**Multi-Fidelity Active Learning for Molecular Property Prediction: Bridging Quantum Simulations and Experimental Validation**

## Motivation
A critical bottleneck in translating ML for chemistry from theory to industry is the scarcity of high-quality experimental data and the computational expense of quantum simulations (DFT, QM). Industry applications require models that can reliably predict properties with limited labeled data while maintaining trust through uncertainty quantification. Current approaches either rely solely on expensive high-fidelity data or struggle to effectively combine multiple data sources with varying accuracy levels.

## Main Idea
Develop a multi-fidelity active learning framework that strategically combines:
1. **Hierarchical data sources**: cheap force-field simulations, mid-cost DFT calculations, and expensive experimental measurements
2. **Graph neural networks** with built-in uncertainty estimation to model molecular properties across fidelity levels
3. **Intelligent acquisition functions** that balance exploration-exploitation while accounting for computational/experimental costs

The methodology includes: (a) training uncertainty-aware models on multi-fidelity datasets with correlation modeling between fidelity levels, (b) developing cost-aware acquisition strategies that decide which molecules to evaluate at which fidelity level, (c) creating benchmarks using existing multi-fidelity molecular databases.

**Expected outcomes**: 10-100x reduction in experimental costs for property optimization, validated on drug discovery and materials design tasks. This directly addresses dataset curation challenges while providing practical tools for industry deployment.