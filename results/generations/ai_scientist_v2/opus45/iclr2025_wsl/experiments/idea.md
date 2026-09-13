## Name

checkpoint_trajectory_forecasting

## Title

Learning from Training Trajectories: Forecasting Model Properties from Early Weight Checkpoints

## Short Hypothesis

The sequence of neural network weight checkpoints during early training contains predictive signals about the final model's properties (generalization, robustness, task performance) that can be extracted using sequence models operating on weight-space embeddings. This enables early stopping decisions, hyperparameter selection, and architecture search without completing full training runs.

## Related Work

Existing weight space learning methods (SANE, Neural Graphs, ProbeGen) primarily analyze single trained models as static snapshots, ignoring the rich temporal structure of training. Gradient Flow Matching (GFM) models weight trajectories but focuses on predicting final weights rather than model properties. Loss landscape studies examine interpolation between checkpoints but don't leverage sequential checkpoint information for property prediction. Model zoo datasets contain only final trained models. Our work uniquely treats the checkpoint sequence as a multivariate time series in weight space, learning to forecast downstream properties from partial training trajectories—a fundamentally different task from weight generation or single-model analysis.

## Abstract

The proliferation of neural network training runs generates vast sequences of intermediate checkpoints, yet most weight space learning methods analyze only final trained models. We propose Checkpoint Trajectory Forecasting (CTF), a framework that treats sequences of training checkpoints as temporal data to predict properties of the final model from early training stages. Our approach first embeds each checkpoint using a permutation-equivariant weight encoder, then processes the sequence of embeddings with a temporal model to forecast properties like final test accuracy, robustness to distribution shift, or calibration quality. We construct a new benchmark dataset containing checkpoint trajectories from diverse architectures trained on multiple tasks, with associated final model properties. Our experiments demonstrate that CTF can predict final model generalization with high accuracy using only 10-20% of training checkpoints, enabling significant computational savings for hyperparameter search and neural architecture search. We further show that trajectory-based features outperform single-checkpoint baselines, confirming that training dynamics contain unique predictive information. Analysis reveals that CTF learns to identify characteristic patterns in weight evolution—such as the rate of weight norm growth and layer-wise convergence patterns—that correlate with final model quality. This work establishes training trajectories as a valuable data modality for efficient model development.

## Experiments

1. **Dataset Construction**: Create checkpoint trajectory datasets by training CNNs (ResNet-18/34) and Transformers (ViT-Tiny) on CIFAR-10/100 and TinyImageNet with varying hyperparameters (learning rates, batch sizes, optimizers, augmentation). Save checkpoints every epoch. Record final properties: test accuracy, calibration error (ECE), robustness to corruptions (CIFAR-C), and out-of-distribution detection (AUROC on near-OOD).

2. **Weight Embedding**: Use SANE-style layer-wise embeddings or simplified statistics (mean, std, spectral norm per layer) to convert each checkpoint to a fixed-size vector. Compare embedding strategies.

3. **Temporal Model**: Train sequence models (LSTM, Transformer, or simple MLPs on concatenated early checkpoints) to predict final properties from the first k checkpoints (k=5,10,20 out of 100 epochs).

4. **Baselines**: (a) Single checkpoint at epoch k; (b) Training loss/accuracy curves only (no weight information); (c) Random forest on hand-crafted trajectory statistics.

5. **Evaluation Metrics**: Spearman correlation between predicted and true properties; ranking accuracy for top-10% model selection; computational savings (fraction of training needed).

6. **Ablations**: (a) Which layers' trajectories are most predictive? (b) Does trajectory shape matter more than absolute values? (c) Transfer across architectures and datasets.

7. **Application**: Demonstrate early stopping for hyperparameter search—show that CTF-guided selection matches exhaustive search quality with 5x fewer total training FLOPs.

## Risk Factors And Limitations

1. **Dataset scale**: Generating sufficient checkpoint trajectories requires substantial computation; we mitigate by focusing on smaller models and leveraging existing training infrastructure.

2. **Generalization across architectures**: Trajectory patterns may be architecture-specific; we explicitly test transfer and may need architecture-conditioned models.

3. **Checkpoint storage**: Full weight trajectories are storage-intensive; we explore compressed representations and statistical summaries.

4. **Predictive ceiling**: Some final properties may genuinely be unpredictable from early training; we quantify uncertainty and identify which properties are forecastable.

5. **Permutation symmetry**: Weight permutation symmetries complicate trajectory comparison; we use permutation-equivariant encoders but this adds complexity.

