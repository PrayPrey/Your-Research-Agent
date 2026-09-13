# Title: Information-Theoretic Framework for Predicting Auxiliary Task Effectiveness in Self-Supervised Learning

## Motivation
A fundamental open question in SSL is: *why do certain auxiliary tasks outperform others?* Currently, practitioners rely on empirical trial-and-error to design pretext tasks, which is computationally expensive and lacks principled guidance. While tasks like contrastive learning and masked prediction have proven effective, we lack theoretical tools to predict task effectiveness *before* training. Understanding what properties make auxiliary tasks successful would enable theory-driven task design and reduce wasted computational resources.

## Main Idea
We propose an information-theoretic framework to quantify and predict auxiliary task effectiveness based on three measurable properties: (1) **task-relevant information preservation**—how much mutual information the learned representation retains about downstream-relevant features; (2) **invariance-discrimination trade-off**—the balance between discarding nuisance factors and preserving discriminative signals; and (3) **task difficulty calibration**—whether the auxiliary task sits in the optimal difficulty regime (neither trivial nor impossible).

We will derive theoretical bounds connecting these quantities to downstream performance and validate them empirically across vision (MAE, SimCLR), language (BERT, GPT), and speech (wav2vec) domains. We will develop a lightweight proxy metric computable on small data subsets that predicts full-scale SSL performance.

**Expected Impact**: A practical scoring function for auxiliary task selection, reducing hyperparameter search costs and enabling principled SSL design for new domains.