# Title
Contamination-Aware Training Data Attribution: Integrating Validity Assessment into Scalable Influence Estimation

# Motivation
Modern ML models trained on internet-scale datasets face inevitable data contamination—train-test leakage that inflates performance and produces misleading explanations. Existing attribution methods (TRAK, LoRIF) achieve O(n) scalability but ignore data quality, implicitly assuming clean training data. This creates a critical gap: practitioners cannot distinguish genuine model learning from circular memorization when attributing predictions to training examples. For GDPR compliance, benchmark integrity auditing, and trustworthy AI, we need attributions that quantify their own reliability.

# Main Idea
We hypothesize that **contamination-robustness can be achieved without sacrificing scalability** by jointly computing influence scores (gradient-based attribution) and contamination confidence (semantic similarity-based leakage detection) in a single O(n) pass. The core mechanism: pre-computed BERT/CLIP embeddings enable O(1) contamination detection per train-test pair, while TRAK projections compute influence scores—both decoupled yet unified via **attribution validity** V = 1 - C, where high contamination confidence inversely indicates explanation trustworthiness.

**Methodology**: Inject controlled contamination (exact duplicates, paraphrases) at 1-20% rates into CIFAR-10/MNLI benchmarks. Measure contamination detection (precision/recall) and attribution accuracy (linear datamodeling score) comparing contamination-aware filtering against baseline TRAK.

**Expected Impact**: Enable GDPR-compliant explanations, detect benchmark leakage, and provide validity-assessed attributions for internet-scale datasets—bridging data provenance principles with ML explainability while maintaining production-ready efficiency.