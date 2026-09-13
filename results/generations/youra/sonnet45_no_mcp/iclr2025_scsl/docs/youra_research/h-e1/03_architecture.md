# System Architecture Document
# Hypothesis h-e1: MI Growth Rate Asymmetry

**Version:** 1.0  
**Date:** 2026-04-24  
**Hypothesis:** h-e1 (EXISTENCE)  
**Task Budget:** LIGHT (4-8 Epic tasks, ≤15 total tasks)  
**Infrastructure Level:** minimal

---

## Codebase Analysis (Serena)

**Analysis Status:** Green-field implementation (no existing codebase)

**Foundation Hypothesis:** h-e1 is the first hypothesis with no prerequisites. All code will be implemented from scratch.

**External Dependencies Analysis:**
- torchvision.models.resnet18 - Standard PyTorch model
- torchvision.datasets.MNIST - Standard dataset loader
- sklearn.metrics.mutual_info_score - Standard MI estimator
- scipy.interpolate.UnivariateSpline - Standard spline fitting

**Serena Findings:** N/A (green-field project)

---

## Archon Knowledge Base Research

Applied: **DL Experiment Standard Structure Pattern**
- Source: Archon KB "DL experiment architecture"
- Pattern: data/ | models/ | training/ | evaluation/ structure
- Justification: Industry-standard organization for reproducible ML experiments

Applied: **Multi-Paradigm Training Architecture Pattern**
- Source: Archon KB "Cross-paradigm ML systems"
- Pattern: Shared encoder + paradigm-specific heads
- Justification: Enables fair MI comparison across supervised/SSL/RL

Applied: **Callback-Based Metric Tracking Pattern**
- Source: Archon KB "Training instrumentation"
- Pattern: Hook-based MI extraction without modifying core training loop
- Justification: Non-invasive observation infrastructure for EXISTENCE hypothesis

---

## System Architecture Overview

### High-Level Design Principles

1. **Minimal Infrastructure (LIGHT tier):**
   - Hardcoded configurations (no YAML parsers)
   - Print-based logging (no WandB/TensorBoard)
   - CSV output files (no databases)
   - Smoke tests only (no comprehensive test suite)

2. **Shared Encoder Pattern:**
   - Single ResNet-18 architecture
   - Three training scripts with paradigm-specific heads
   - Unified MI tracker for cross-paradigm consistency

3. **Observation-Only Design:**
   - MI tracker does NOT modify model or training
   - Passive measurement via forward hooks
   - Post-training derivative computation

---

## Module Structure

```
h-e1/
├── code/
│   ├── data/
│   │   ├── colored_mnist.py          # ColoredMNISTWrapper dataset
│   │   └── utils.py                  # Data loading utilities
│   ├── models/
│   │   ├── encoder.py                # ResNet-18 encoder (shared)
│   │   ├── supervised_head.py        # Classification head
│   │   ├── ssl_head.py               # Projection head (SimCLR)
│   │   └── rl_heads.py               # Actor-critic heads
│   ├── training/
│   │   ├── supervised_train.py       # Supervised training loop
│   │   ├── ssl_train.py              # SimCLR training loop
│   │   └── rl_train.py               # Policy gradient training loop
│   ├── tracking/
│   │   ├── mi_tracker.py             # MITracker class
│   │   └── derivative_estimator.py   # Spline fitting + derivatives
│   ├── evaluation/
│   │   ├── metrics.py                # Accuracy, episode return
│   │   └── visualization.py          # Figure generation
│   └── run_experiment.py             # Main entry point
├── figures/                          # Generated visualizations
├── results/                          # CSV outputs, MI trajectories
└── README.md                         # Execution instructions
```

---

## Module Responsibilities

### Module 1: Data Pipeline (`data/`)
**Responsibility:** Load MNIST, apply color correlation, provide train/test splits

**Key Components:**
- `ColoredMNISTWrapper`: Applies 90% spurious color correlation
- `get_dataloaders()`: Returns train/test loaders for each paradigm

**Interfaces:**
```python
class ColoredMNISTWrapper(torch.utils.data.Dataset):
    def __init__(self, mnist_dataset, spurious_prob=0.9, seed=1)
    def __getitem__(self, idx) -> Tuple[Tensor, int, int, int]
        # Returns: (colored_image, digit_label, color_factor, shape_factor)
```

### Module 2: Model Architectures (`models/`)
**Responsibility:** Define shared encoder and paradigm-specific heads

**Key Components:**
- `get_encoder()`: Modified ResNet-18 for 28×28 input
- `SupervisedHead`: Linear(512, 10) for classification
- `SSLHead`: MLP projection head for contrastive learning
- `ActorCriticHeads`: Policy and value heads for RL

**Interfaces:**
```python
def get_encoder() -> nn.Module:
    # Returns: ResNet-18 with conv1 modified, maxpool removed

class SupervisedHead(nn.Module):
    def forward(self, features: Tensor) -> Tensor:
        # Input: (B, 512), Output: (B, 10)
```

### Module 3: Training Loops (`training/`)
**Responsibility:** Implement paradigm-specific training protocols

**Key Components:**
- `train_supervised()`: Standard CE loss + SGD
- `train_ssl()`: NT-Xent loss + SGD
- `train_rl()`: Policy gradient + Adam

**Interfaces:**
```python
def train_supervised(
    model: nn.Module,
    train_loader: DataLoader,
    mi_tracker: MITracker,
    epochs: int = 200,
    seed: int = 1
) -> Dict[str, np.ndarray]:
    # Returns: {'loss': [...], 'accuracy': [...], 'mi_history': {...}}
```

### Module 4: MI Tracking (`tracking/`)
**Responsibility:** Extract representations, compute MI, estimate derivatives

**Key Components:**
- `MITracker`: Hooks into layer4, computes I(Z; H_t)
- `DerivativeEstimator`: Fits splines, extracts d/dt I

**Interfaces:**
```python
class MITracker:
    def __init__(self, model: nn.Module, checkpoint_steps: int = 50)
    def compute_mi_checkpoint(self, dataloader: DataLoader, step: int) -> Tuple[float, float]:
        # Returns: (mi_spurious, mi_causal)
    def get_mi_history(self) -> Dict[str, List[float]]:
        # Returns: {'Z_spurious': [...], 'Z_causal': [...], 'timesteps': [...]}

class DerivativeEstimator:
    def fit_spline(self, timesteps: np.ndarray, mi_values: np.ndarray, s: float = 0.1)
    def compute_derivative(self) -> np.ndarray:
        # Returns: mi_derivative array
```

### Module 5: Evaluation (`evaluation/`)
**Responsibility:** Compute metrics, generate visualizations

**Key Components:**
- `compute_metrics()`: Accuracy, episode return
- `plot_mi_trajectories()`: Required gate figure
- `plot_derivative_comparison()`: Cross-paradigm comparison

**Interfaces:**
```python
def plot_mi_trajectories(
    mi_history_supervised: Dict,
    mi_history_ssl: Dict,
    mi_history_rl: Dict,
    save_path: str
) -> None:
    # Generates 3-subplot figure saved to h-e1/figures/
```

---

## File Organization

### Configuration
- **Location:** Hardcoded in each training script
- **Rationale:** LIGHT tier - no external config files
- **Content:** Hyperparameters, paths, seeds

### Logging
- **Location:** Print statements + CSV files
- **Rationale:** LIGHT tier - no structured logging frameworks
- **Format:** `results/{paradigm}_metrics.csv`

### Checkpoints
- **Location:** Not saved (PoC focuses on MI dynamics, not final model)
- **Rationale:** Reduce storage, focus on trajectories
- **Exception:** MI history saved to CSV for plotting

### Outputs
```
h-e1/
├── results/
│   ├── supervised_metrics.csv       # Loss, accuracy per epoch
│   ├── ssl_metrics.csv              # Contrastive loss, linear probe accuracy
│   ├── rl_metrics.csv               # Episode return, policy loss
│   ├── mi_supervised.csv            # MI trajectories (supervised)
│   ├── mi_ssl.csv                   # MI trajectories (SSL)
│   └── mi_rl.csv                    # MI trajectories (RL)
└── figures/
    ├── gate_metrics_comparison.png  # REQUIRED: Bar chart
    ├── mi_trajectories.png          # 3-subplot MI curves
    ├── derivative_comparison.png     # Cross-paradigm derivatives
    └── complexity_scatter.png       # Complexity vs MI growth rate
```

---

## Proposed Tasks (Epic Level)

### Epic 1: Data Pipeline Setup
**Complexity Score:** 4/20 (Module_Size: 1, Dependencies: 1, Algorithm: 1, Integration: 1)

**Description:** Implement Colored MNIST dataset with controlled spurious correlation.

**Subtasks:**
1. Load MNIST via torchvision
2. Implement ColoredMNISTWrapper class
3. Verify ground-truth factor access (color, shape)
4. Create train/test dataloaders

**Acceptance Criteria:**
- Dataset returns 4-tuple: (image, label, color, shape)
- 90% spurious correlation verified
- 60k train, 10k test samples

---

### Epic 2: Model Architecture Implementation
**Complexity Score:** 5/20 (Module_Size: 2, Dependencies: 1, Algorithm: 1, Integration: 1)

**Description:** Implement shared ResNet-18 encoder and paradigm-specific heads.

**Subtasks:**
1. Modify ResNet-18 for 28×28 input (conv1, remove maxpool)
2. Implement SupervisedHead (Linear 512→10)
3. Implement SSLHead (MLP projection for SimCLR)
4. Implement ActorCriticHeads (policy + value for RL)

**Acceptance Criteria:**
- Forward pass: (B, 3, 28, 28) → (B, 512) → task-specific output
- Encoder shared across all paradigms
- Heads match PRD specifications

---

### Epic 3: MI Tracking Infrastructure
**Complexity Score:** 8/20 (Module_Size: 2, Dependencies: 2, Algorithm: 3, Integration: 1)

**Description:** Implement MI tracker and derivative estimator.

**Subtasks:**
1. Implement MITracker class with forward hooks
2. Discretize representations (KBinsDiscretizer, n_bins=20)
3. Compute MI using sklearn.metrics.mutual_info_score
4. Implement DerivativeEstimator with spline fitting
5. Extract early-phase derivatives (first 10% of training)

**Acceptance Criteria:**
- MI computed every 50 steps
- Trajectories logged to CSV
- Derivatives computed via scipy.interpolate.UnivariateSpline
- Smoothing factor s=0.1

---

### Epic 4: Supervised Training Loop
**Complexity Score:** 4/20 (Module_Size: 1, Dependencies: 1, Algorithm: 1, Integration: 1)

**Description:** Implement supervised digit classification training.

**Subtasks:**
1. Setup optimizer: SGD(momentum=0.9, weight_decay=5e-4)
2. Setup learning rate scheduler: Cosine annealing
3. Training loop: 200 epochs, batch_size=128
4. Integrate MI tracker callback (every 50 steps)
5. Log metrics to CSV

**Acceptance Criteria:**
- CrossEntropyLoss minimized
- Test accuracy ~98-99%
- MI trajectories saved
- Seed=1 for reproducibility

---

### Epic 5: SSL Training Loop (SimCLR)
**Complexity Score:** 10/20 (Module_Size: 2, Dependencies: 2, Algorithm: 4, Integration: 2)

**Description:** Implement self-supervised contrastive learning.

**Subtasks:**
1. Implement NT-Xent loss (temperature=0.5)
2. Setup data augmentation (preserve spurious correlation)
3. Setup optimizer: SGD(momentum=0.9, lr=0.03)
4. Training loop: 200 epochs, batch_size=256
5. Integrate MI tracker callback
6. Implement linear probing for evaluation

**Acceptance Criteria:**
- Contrastive loss minimized
- Linear probe accuracy ~95%+
- MI trajectories saved
- Augmentations don't break color correlation

---

### Epic 6: RL Training Loop (Policy Gradient)
**Complexity Score:** 15/20 (Module_Size: 3, Dependencies: 3, Algorithm: 6, Integration: 3)

**Description:** Implement policy gradient RL with grid navigation.

**Subtasks:**
1. Implement grid environment (10×10 grid)
2. Colored digit state representations
3. Setup optimizer: Adam(lr=3e-4)
4. Policy gradient loss + value loss
5. Entropy regularization (coeff=0.01)
6. Training loop: 200 episodes, batch_size=32
7. Integrate MI tracker callback

**Acceptance Criteria:**
- Policy converges within 200 episodes
- Episode return increases
- MI trajectories saved
- Exploration balanced (entropy regularization working)

---

### Epic 7: Evaluation Metrics
**Complexity Score:** 3/20 (Module_Size: 1, Dependencies: 1, Algorithm: 0, Integration: 1)

**Description:** Compute standard task performance metrics.

**Subtasks:**
1. Supervised: Test accuracy (torchmetrics)
2. SSL: Linear probing accuracy
3. RL: Episode return, policy convergence
4. Save all metrics to CSV

**Acceptance Criteria:**
- Metrics logged for all 3 paradigms
- CSV files in results/

---

### Epic 8: Visualization Generation
**Complexity Score:** 6/20 (Module_Size: 2, Dependencies: 1, Algorithm: 2, Integration: 1)

**Description:** Generate required and recommended figures.

**Subtasks:**
1. Gate metrics bar chart (d/dt I comparison) - REQUIRED
2. MI trajectory curves (3 subplots)
3. Derivative comparison across paradigms
4. Complexity vs MI growth rate scatter
5. Gradient norm validation plot

**Acceptance Criteria:**
- All figures saved to h-e1/figures/
- Gate figure shows effect direction (Blue > Orange in 2+ paradigms)
- Matplotlib/seaborn used for plotting

---

## Task Budget Summary

**Total Epic Tasks:** 8  
**Budget Range:** 4-8 (LIGHT tier for EXISTENCE hypothesis)  
**Status:** ✅ Within budget

**Complexity Distribution:**
- Very High (12-20): 1 task (Epic 6: RL training)
- High (8-11): 1 task (Epic 5: SSL training)
- Medium (4-7): 4 tasks (Epic 1, 2, 4, 8)
- Low (1-3): 2 tasks (Epic 3, 7)

**Total Complexity Score:** 55/160 (Average: 6.9 per Epic)

---

## Integration Points

### 1. Data → Model
- ColoredMNISTWrapper provides (image, label, color, shape)
- Model encoder processes RGB images
- Ground-truth factors used for MI computation

### 2. Model → Training
- Shared encoder used across all 3 paradigms
- Paradigm-specific heads swapped based on task
- Encoder weights trained separately for each paradigm (no transfer)

### 3. Training → MI Tracking
- MI tracker hooks into encoder layer4
- Callback invoked every 50 training steps
- No modification to training loop logic

### 4. MI Tracking → Evaluation
- MI trajectories saved to CSV
- Derivative estimator loads trajectories
- Spline fitting + derivative extraction
- Results fed to visualization

### 5. Evaluation → Output
- Metrics saved to CSV
- Figures saved to h-e1/figures/
- Gate condition checked: Effect direction in 2+ paradigms

---

## External Dependencies

### PyTorch Ecosystem
- `torch` (≥1.12): Core framework
- `torchvision`: ResNet-18, MNIST dataset
- `torchmetrics`: Accuracy computation

### Scientific Computing
- `numpy`: Array operations
- `scipy`: Spline fitting (UnivariateSpline)
- `sklearn`: MI computation (mutual_info_score), discretization (KBinsDiscretizer)

### Visualization
- `matplotlib`: Figure generation
- `seaborn`: Statistical plotting (optional for scatter plots)

### Standard Library
- `random`: Seed setting
- `csv`: Metrics logging
- `pathlib`: Path handling

**Installation:**
```bash
pip install torch torchvision torchmetrics numpy scipy scikit-learn matplotlib seaborn
```

---

## Risk Mitigation Architecture Decisions

### R1: MI Estimator Inaccuracy
**Architecture Decision:** Use histogram-based MI (exact for discrete factors)  
**Implementation:** sklearn.metrics.mutual_info_score with KBinsDiscretizer  
**Validation:** Log discretization quality metrics

### R2: Early-Phase Misidentification
**Architecture Decision:** Dual-criteria detection + gradient norm validation  
**Implementation:** Track both 10% steps AND 30% performance criteria  
**Fallback:** Manual inspection of MI trajectories if criteria disagree

### R3: RL Exploration Bias
**Architecture Decision:** Entropy regularization in policy loss  
**Implementation:** Entropy coefficient=0.01, log exploration metrics  
**Monitoring:** Track entropy over training to ensure exploration

### R4: Derivative Instability
**Architecture Decision:** Spline smoothing + sufficient checkpoint frequency  
**Implementation:** s=0.1 smoothing, checkpoint every 50 steps  
**Validation:** Visual inspection of fitted splines vs raw MI values

---

## Testing Strategy (LIGHT Tier)

### Smoke Tests Only
1. **Data loading:** Verify dataset returns correct shapes
2. **Model forward pass:** (B, 3, 28, 28) → (B, 10) for supervised
3. **MI tracker:** Verify MI values are non-negative
4. **Training loop:** Run 1 epoch without errors

**No comprehensive testing:** Unit tests, integration tests, or performance benchmarks are out of scope for LIGHT tier PoC.

---

## Deployment & Execution

### Environment Setup
```bash
# Set GPU
export CUDA_VISIBLE_DEVICES=0

# Create directories
mkdir -p h-e1/code h-e1/results h-e1/figures

# Install dependencies
pip install torch torchvision torchmetrics numpy scipy scikit-learn matplotlib seaborn
```

### Execution Sequence
```bash
# Run all 3 paradigms sequentially
python h-e1/code/run_experiment.py --paradigm supervised
python h-e1/code/run_experiment.py --paradigm ssl
python h-e1/code/run_experiment.py --paradigm rl

# Generate visualizations
python h-e1/code/evaluation/visualization.py
```

### Expected Outputs
- 6 CSV files in results/
- 4-5 PNG files in figures/
- Console logs showing training progress
- Total runtime: ~6-12 hours on single GPU

---

## Success Criteria Validation

### Code Execution Check
- All 3 paradigms complete without errors
- No CUDA OOM errors
- MI values logged at all checkpoints

### Effect Direction Check
- Load MI derivatives from results/
- Check: d/dt I(Z_s) > d/dt I(Z_c) for each paradigm
- Gate passes if TRUE for ≥2 paradigms

### Gate Decision
```python
# Pseudocode for gate validation
paradigms = ['supervised', 'ssl', 'rl']
passes = 0

for paradigm in paradigms:
    deriv_s = load_derivative(paradigm, 'Z_spurious')
    deriv_c = load_derivative(paradigm, 'Z_causal')
    if deriv_s > deriv_c:
        passes += 1

gate_passed = (passes >= 2)
```

---

**Document Status:** Complete  
**Epic Task Count:** 8 (within budget 4-8)  
**Complexity Score:** 55/160  
**Next Phase:** Step 4 - Budget Allocation
