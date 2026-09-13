# Experimental Setup

We design experiments to test three claims: (1) minority samples show detectably different loss trajectories, (2) simplicity bias explains this difference, and (3) the effect is statistically robust.

## Research Questions

**RQ1**: Do minority and majority samples exhibit statistically different loss distributions at early epochs?

**RQ2**: Does simplicity bias cause representations to encode spurious features more accurately than core features?

**RQ3**: Is the detection signal practically useful (precision/recall vs. random baseline)?

## Dataset

We use **Waterbirds** (Sagawa et al., 2019), a canonical benchmark for spurious correlation research. The dataset combines bird images from CUB-200 with backgrounds from Places:

| Group | Bird | Background | Training | % |
|-------|------|------------|----------|---|
| Majority | Waterbird | Water | 3,498 | 73.0% |
| Majority | Landbird | Land | 1,057 | 22.0% |
| Minority | Waterbird | Land | 184 | 3.8% |
| Minority | Landbird | Water | 56 | 1.2% |

Total training samples: 4,795 (5% minority rate). The spurious correlation is 95%: birds appear on "expected" backgrounds 95% of the time.

**Rationale**: Waterbirds is the standard benchmark for spurious correlation methods, enabling direct comparison with JTT, SPARE, and DFR. The 95% correlation rate creates clear majority/minority structure, and ground-truth group labels enable evaluation without being used during training.

## Model and Training

- **Architecture**: ResNet-18 pretrained on ImageNet (torchvision IMAGENET1K_V1)
- **Training**: 100 epochs, SGD (lr=0.001, momentum=0.9, weight decay=1e-4)
- **Loss logging**: Per-sample cross-entropy loss recorded every epoch
- **Checkpoints**: Model weights saved at epochs 5, 20, 50, 81, 100

We train with standard ERM (no group balancing or reweighting) to observe natural learning dynamics.

## Baselines

**Random Selection**: Selecting 5% of samples uniformly at random as minority candidates yields 5% precision (matching the true minority rate by chance).

**ERM Misclassification (JTT-style)**: Identifying misclassified samples at convergence provides a comparison to established methods. Note that our goal is *earlier* detection, not better final detection.

## Evaluation Metrics

### Detection Metrics

- **Precision**: Of samples predicted as minority, what fraction are truly minority?
- **Recall**: Of true minority samples, what fraction are detected?
- **F1**: Harmonic mean of precision and recall

### Statistical Metrics

- **Mann-Whitney U**: Non-parametric test for distribution difference
- **Effect size**: Ratio of minority to majority mean loss

### Probe Metrics

- **Spurious accuracy**: Linear probe accuracy for predicting background
- **Core accuracy**: Linear probe accuracy for predicting bird type
- **Accuracy gap**: Spurious accuracy − core accuracy

## Experimental Protocol

### Experiment 1: Loss Distribution Analysis (H-E1)

1. Train ResNet-18 for 100 epochs, logging per-sample loss
2. At epoch 5, compute loss for all training samples
3. Threshold at 95th percentile (top 5% high-loss samples)
4. Compute precision and recall against ground-truth minority labels
5. Run Mann-Whitney U test comparing minority vs. majority losses

**Success criteria**: Mann-Whitney *p* < 0.05 (statistical significance), recall > 0.3 (practical utility).

### Experiment 2: Simplicity Bias Verification (H-M1)

1. Load frozen checkpoints from epochs 5, 20, 50
2. Extract 512-dim avgpool features for all training samples
3. Train logistic regression probe for spurious feature (background)
4. Train logistic regression probe for core feature (bird type)
5. Evaluate both probes on test set

**Success criteria**: Spurious accuracy > core accuracy at epoch 5 (confirms simplicity bias).

### Experiment 3: Timing Analysis (H-M2)

1. Train probes at every 5 epochs (1-100)
2. Record peak accuracy epoch for spurious and core probes
3. Apply 5-epoch smoothing window to reduce noise
4. Compare peak epochs

**Success criteria (original)**: Spurious peak epoch < core peak epoch (timing gap).
**Alternative**: If peaks coincide, magnitude gap (spurious > core throughout) still supports mechanism.

## Hardware

Experiments run on NVIDIA H100 GPU with 80GB memory. Training takes ~20 minutes per run; full 100-epoch probe analysis takes ~30 minutes.
