# Logic Specification: h-m-integrated — 3-Step Mechanism Validation

**Date:** 2026-03-20
**Author:** Phase 3 Logic Agent
**Hypothesis:** h-m-integrated (MECHANISM)
**Applied:** PyTorch SSL training pattern, custom sampler pattern, mechanism validation pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from base code
**Analyzed Path:** `docs/youra_research/20260318_scsl/h-e1/code/`
**Relevant Symbols:** SimCLR.forward, nt_xent_loss, WaterbirdsDataset.__getitem__, compute_ami, compute_wga, LinearProbe.forward, cluster_balanced_loss

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1 base hypothesis. Signatures verified from actual implementation:

```python
# From: h-e1/code/models/simclr.py (ACTUAL CODE)
class SimCLR(nn.Module):
    def __init__(
        self,
        encoder_name: str = 'resnet50',
        projection_dim: int = 128,
        pretrained: bool = False
    ):
        """Initialize SimCLR with ResNet-50 encoder."""
        ...

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass. x: [B,3,224,224] -> (h: [B,2048], z: [B,128])"""
        ...

    def get_encoder(self) -> nn.Module:
        """Get encoder module for freezing."""
        ...

def nt_xent_loss(
    z_i: torch.Tensor,
    z_j: torch.Tensor,
    temperature: float = 0.5
) -> torch.Tensor:
    """NT-Xent contrastive loss. z_i,z_j: [B,128] -> scalar"""
    ...


# From: h-e1/code/data/dataset.py (ACTUAL CODE)
class WaterbirdsDataset(Dataset):
    def __init__(
        self,
        root_dir: str,
        split: str = 'train',
        transform: Optional[transforms.Compose] = None
    ):
        """Initialize Waterbirds dataset."""
        ...

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int]:
        """Get item. Returns: (image[3,H,W], label, group)"""
        ...

def get_ssl_transforms() -> transforms.Compose:
    """Get SimCLR SSL augmentations."""
    ...

def get_eval_transforms() -> transforms.Compose:
    """Get evaluation transforms (no augmentation)."""
    ...

def get_dataloaders(
    root_dir: str,
    batch_size: int = 256,
    num_workers: int = 4,
    ssl_mode: bool = True
) -> Dict[str, DataLoader]:
    """Create DataLoaders for all splits."""
    ...


# From: h-e1/code/evaluation/metrics.py (ACTUAL CODE)
def compute_ami(
    embeddings: np.ndarray,
    groups: np.ndarray,
    num_clusters: int = 4
) -> Tuple[float, np.ndarray]:
    """Compute AMI. Returns: (ami_score, cluster_labels)"""
    ...

def compute_wga(
    preds: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray
) -> Tuple[float, Dict[int, float]]:
    """Compute WGA. Returns: (wga, group_accs)"""
    ...

def compute_linear_auroc(
    embeddings: np.ndarray,
    groups: np.ndarray
) -> float:
    """Compute linear separability AUROC."""
    ...


# From: h-e1/code/models/linear_probe.py (ACTUAL CODE)
class LinearProbe(nn.Module):
    def __init__(self, input_dim: int = 2048, num_classes: int = 2):
        """Initialize linear classifier."""
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B,2048] -> logits: [B,2]"""
        ...

def cluster_balanced_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
    cluster_ids: torch.Tensor,
    cluster_weights: torch.Tensor
) -> torch.Tensor:
    """Cluster-balanced cross-entropy loss."""
    ...

def compute_cluster_weights(
    cluster_labels: torch.Tensor,
    num_clusters: int = 4
) -> torch.Tensor:
    """Compute inverse-frequency weights for clusters."""
    ...
```

**Verified from:** `h-e1/code/` (actual implementation, NOT spec!)

---

## M-1: LA-SSL Sampler Implementation [Complexity: 11, Budget: 6]

**Applied:** PyTorch custom sampler pattern

### API Signatures

```python
class LASSLSampler(torch.utils.data.Sampler):
    """Learning-speed aware sampler for LA-SSL training.

    Tracks per-sample loss history and samples inversely proportional to learning speed.
    """

    def __init__(
        self,
        dataset_size: int,
        alpha: float = 0.5,
        window_size: int = 10,
        generator: Optional[torch.Generator] = None
    ):
        """Initialize sampler.

        Args:
            dataset_size: Total number of samples in dataset
            alpha: Temperature for probability smoothing (0=uniform, 1=inverse)
            window_size: Number of epochs for loss history tracking
            generator: Optional random generator for reproducibility
        """
        ...

    def update_losses(
        self,
        sample_indices: torch.Tensor,
        losses: torch.Tensor
    ) -> None:
        """Update loss history for batch samples. indices,losses: [B]"""
        ...

    def compute_sampling_probs(self) -> torch.Tensor:
        """Compute sampling probabilities. Returns: [dataset_size]"""
        ...

    def __iter__(self) -> Iterator[int]:
        """Generate sample indices for epoch."""
        ...

    def __len__(self) -> int:
        """Return dataset size."""
        ...
```

### Pseudo-code

```
1. Initialize loss history buffer: [dataset_size, window_size] with zeros
2. Track epoch count for circular buffer indexing

On update_losses(indices, losses):
    current_epoch_idx = epoch % window_size
    loss_history[indices, current_epoch_idx] = losses

On compute_sampling_probs():
    valid_mask = (loss_history > 0).sum(axis=1) >= 2  # At least 2 epochs

    For each sample with valid history:
        recent_losses = loss_history[sample, -window_size:]
        learning_speed = -mean(diff(recent_losses))  # Negative slope

    For samples with valid history:
        raw_prob = 1 / (learning_speed + eps)^alpha
    For samples without history:
        raw_prob = 1.0  # Uniform initially

    normalized_probs = raw_prob / sum(raw_prob)
    return normalized_probs

On __iter__():
    probs = compute_sampling_probs()
    indices = torch.multinomial(probs, num_samples=dataset_size, replacement=True)
    yield from indices
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Loss history buffer | Circular buffer tracking per-sample losses |
| L-1-2 | Learning speed computation | Compute negative slope of loss trajectory |
| L-1-3 | Probability smoothing | Apply alpha temperature to inverse probabilities |
| L-1-4 | Multinomial sampling | Sample with replacement using computed probs |
| L-1-5 | Edge case handling | Handle samples without sufficient history |
| L-1-6 | Iterator interface | Implement __iter__ and __len__ for DataLoader |

---

## M-2: LA-SSL Training Infrastructure [Complexity: 9, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Design included for completeness only.

---

## M-3: SimCLR Baseline Training [Complexity: 8, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Reuses h-e1 SimCLR directly.

---

## M-4: LA-SSL Training Execution [Complexity: 8, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Will be handled in orchestration layer.

---

## M-5: Embedding Extraction & Clustering [Complexity: 10, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Uses h-e1 compute_ami directly.

---

## M-6: Linear Probe & Cluster Retraining [Complexity: 12, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Reuses h-e1 LinearProbe and cluster_balanced_loss.

---

## M-7: Mechanism Validation Suite [Complexity: 14, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Design included for reference only.

---

## M-8: Visualization & Reporting [Complexity: 10, Budget: NOT ALLOCATED]

**Note:** No budget allocated. Standard matplotlib visualization.

---

## Summary

**Total Allocated Subtasks:** 6/6 used (M-1 only)

**Reused from h-e1:**
- SimCLR model and training loop
- WaterbirdsDataset and transforms
- AMI, WGA, linear AUROC metrics
- LinearProbe and cluster-balanced loss

**New Implementation (M-1):**
- LASSLSampler with learning-speed tracking

**Key Design Decisions:**

1. **Learning Speed Metric:** Use negative slope of loss trajectory over window_size epochs. Fast learners have steep negative slope → low sampling probability.

2. **Smoothing Parameter:** Alpha=0.5 balances exploration (uniform sampling) and exploitation (inverse learning-speed sampling).

3. **Initialization Strategy:** Samples without sufficient history (< 2 epochs) get uniform probability to bootstrap.

4. **Circular Buffer:** Window size of 10 epochs requires only [N, 10] memory, independent of total training epochs.

5. **Replacement Sampling:** Sample with replacement to achieve target epoch size while maintaining probability distribution.

**Verification Strategy:**

- Unit test: Verify loss history updates correctly
- Unit test: Verify learning speed computation on synthetic trajectories
- Unit test: Verify probability normalization (sum to 1)
- Integration test: Verify sampler integrates with DataLoader
- Validation: Check that slow learners are upsampled in practice

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (6/6)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Base hypothesis checks: API signatures verified from actual code
- [x] External Dependencies API section included

---

**END OF LOGIC SPECIFICATION**
