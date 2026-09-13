# Logic Design Document
# Hypothesis h-e1: MI Growth Rate Asymmetry

**Version:** 1.0  
**Date:** 2026-04-24  
**Hypothesis:** h-e1 (EXISTENCE)  
**Subtask Budget:** 5 tasks (from 7 allocated)

---

## Codebase Analysis (Serena)

**Analysis Status:** Green-field implementation (no existing codebase)

**Foundation Hypothesis:** h-e1 is the first hypothesis with no prerequisites. No base code to analyze.

**Serena Findings:** N/A (green-field project)

---

## Archon Knowledge Base Research

Applied: **Type-Annotated API Pattern**
- Source: Archon KB "DL API design patterns"
- Pattern: Full type hints (PEP 484) for all function signatures
- Justification: Enables static type checking, improves IDE support, reduces runtime errors

Applied: **Tensor Shape Documentation Pattern**
- Source: Archon KB "Tensor shape tracking"
- Pattern: Inline comments documenting tensor shapes at each operation
- Justification: Critical for debugging shape mismatches in multi-paradigm training

Applied: **Hook-Based Callback Pattern**
- Source: Archon KB "Training instrumentation"
- Pattern: Register forward hooks for representation extraction
- Justification: Non-invasive MI tracking without modifying core training loop

---

## API Signatures

### Module 1: Data Pipeline

#### ColoredMNISTWrapper
```python
class ColoredMNISTWrapper(torch.utils.data.Dataset):
    """
    Wrapper around MNIST dataset that applies controlled color spurious correlation.
    
    Returns 4-tuple: (colored_image, digit_label, color_factor, shape_factor)
    for MI computation.
    """
    
    def __init__(
        self,
        mnist_dataset: torchvision.datasets.MNIST,
        spurious_prob: float = 0.9,
        seed: int = 1,
        color_palette: Optional[np.ndarray] = None
    ) -> None:
        """
        Args:
            mnist_dataset: Base MNIST dataset (60k train or 10k test)
            spurious_prob: Probability of spurious color-label correlation (default: 0.9)
            seed: Random seed for reproducibility
            color_palette: RGB colors for 10 digit classes (default: standard colormap)
        """
        pass
    
    def __len__(self) -> int:
        return len(self.mnist_dataset)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int, int]:
        """
        Returns:
            colored_image: (3, 28, 28) RGB tensor, normalized [0, 1]
            digit_label: int [0-9]
            color_factor: int [0-9] (color index)
            shape_factor: int [0-9] (same as digit_label for h-e1)
        """
        pass
    
    def _apply_color(
        self,
        grayscale_image: np.ndarray,  # (28, 28)
        digit_label: int,
        spurious: bool
    ) -> np.ndarray:  # (28, 28, 3)
        """
        Apply RGB color based on label and spuriousness.
        
        Args:
            grayscale_image: (28, 28) grayscale MNIST image
            digit_label: Ground-truth digit [0-9]
            spurious: If True, color matches digit; else random color
        
        Returns:
            (28, 28, 3) RGB image with color channel applied
        """
        pass
```

#### get_dataloaders
```python
def get_dataloaders(
    paradigm: str,  # "supervised" | "ssl" | "rl"
    batch_size: int,
    seed: int = 1,
    num_workers: int = 4
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and test dataloaders for specified paradigm.
    
    Args:
        paradigm: Training paradigm (supervised, ssl, rl)
        batch_size: Batch size (128 for supervised, 256 for SSL, 32 for RL)
        seed: Random seed
        num_workers: Number of data loading workers
    
    Returns:
        train_loader: DataLoader for training (60k samples)
        test_loader: DataLoader for testing (10k samples)
    
    Shapes:
        Batch: (B, 3, 28, 28), (B,), (B,), (B,)
               images,          labels, colors, shapes
    """
    pass
```

---

### Module 2: Model Architectures

#### get_encoder
```python
def get_encoder() -> nn.Module:
    """
    Create modified ResNet-18 encoder for 28×28 input.
    
    Modifications:
        - conv1: kernel_size=3, stride=1, padding=1 (instead of 7, 2, 3)
        - maxpool: Removed (replaced with Identity)
        - Final fc layer: Removed (will be replaced by paradigm-specific heads)
    
    Returns:
        encoder: ResNet-18 backbone outputting (B, 512) features
    
    Tensor Flow:
        Input: (B, 3, 28, 28)
        conv1: (B, 64, 28, 28)  # Modified for small images
        layer1: (B, 64, 28, 28)
        layer2: (B, 128, 14, 14)
        layer3: (B, 256, 7, 7)
        layer4: (B, 512, 4, 4)  # MI extraction point
        avgpool: (B, 512, 1, 1)
        flatten: (B, 512)  # Output
    """
    pass
```

#### SupervisedHead
```python
class SupervisedHead(nn.Module):
    """Classification head for supervised digit recognition."""
    
    def __init__(self, input_dim: int = 512, num_classes: int = 10):
        """
        Args:
            input_dim: Encoder output dimension (512 for ResNet-18)
            num_classes: Number of digit classes (10 for MNIST)
        """
        pass
    
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: (B, 512) encoder output
        
        Returns:
            logits: (B, 10) class logits
        """
        pass
```

#### SSLHead
```python
class SSLHead(nn.Module):
    """Projection head for SimCLR contrastive learning."""
    
    def __init__(
        self,
        input_dim: int = 512,
        hidden_dim: int = 512,
        output_dim: int = 128
    ):
        """
        Args:
            input_dim: Encoder output dimension (512)
            hidden_dim: Hidden layer dimension (512)
            output_dim: Projection space dimension (128)
        """
        pass
    
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: (B, 512) encoder output
        
        Returns:
            projections: (B, 128) L2-normalized projections
        
        Tensor Flow:
            Input: (B, 512)
            Linear1 + ReLU: (B, 512)
            Linear2: (B, 128)
            L2-normalize: (B, 128) with ||z|| = 1
        """
        pass
```

#### ActorCriticHeads
```python
class ActorCriticHeads(nn.Module):
    """Policy and value heads for RL."""
    
    def __init__(
        self,
        input_dim: int = 512,
        num_actions: int = 4  # Up, Down, Left, Right
    ):
        """
        Args:
            input_dim: Encoder output dimension (512)
            num_actions: Action space size (4 for grid navigation)
        """
        pass
    
    def forward(
        self,
        features: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            features: (B, 512) encoder output
        
        Returns:
            action_logits: (B, 4) action probabilities (log_softmax)
            value: (B, 1) state value estimate
        """
        pass
```

---

### Module 3: MI Tracking

#### MITracker
```python
class MITracker:
    """
    Tracks mutual information between ground-truth factors and
    learned representations during training.
    """
    
    def __init__(
        self,
        model: nn.Module,
        layer_name: str = "layer4",
        checkpoint_steps: int = 50,
        n_bins: int = 20
    ):
        """
        Args:
            model: Neural network model (with named modules)
            layer_name: Layer to extract representations from (default: "layer4")
            checkpoint_steps: Frequency of MI computation
            n_bins: Number of bins for representation discretization
        """
        self.model = model
        self.layer_name = layer_name
        self.checkpoint_steps = checkpoint_steps
        self.n_bins = n_bins
        self.mi_history: Dict[str, List[float]] = {
            'Z_spurious': [],
            'Z_causal': [],
            'timesteps': []
        }
        self._register_hooks()
    
    def _register_hooks(self) -> None:
        """Register forward hook on specified layer."""
        pass
    
    def compute_mi_checkpoint(
        self,
        dataloader: DataLoader,
        step: int
    ) -> Tuple[float, float]:
        """
        Extract representations and compute MI for both factors.
        
        Args:
            dataloader: DataLoader providing (images, labels, colors, shapes)
            step: Current training step
        
        Returns:
            mi_spurious: I(Z_spurious; H_t) in bits
            mi_causal: I(Z_causal; H_t) in bits
        
        Algorithm:
            1. Extract representations H_t from layer4 via forward pass
            2. Flatten H_t: (N, 512, 4, 4) → (N, 8192)
            3. Discretize H_t using KBinsDiscretizer (n_bins=20)
            4. Compute MI using sklearn.mutual_info_score
            5. Store results and timestep
        
        Shapes:
            representations: (N, 512, 4, 4) → flatten → (N, 8192)
            Z_spurious: (N,) int [0-9]
            Z_causal: (N,) int [0-9]
            H_discrete: (N,) int [0-19] after discretization
        """
        pass
    
    def get_mi_history(self) -> Dict[str, List[float]]:
        """
        Returns:
            mi_history: Dict with keys 'Z_spurious', 'Z_causal', 'timesteps'
        """
        return self.mi_history
    
    def save_to_csv(self, save_path: str) -> None:
        """
        Save MI trajectories to CSV.
        
        Args:
            save_path: Path to save CSV (e.g., "results/mi_supervised.csv")
        
        CSV Format:
            timestep, mi_spurious, mi_causal
            0, 0.12, 0.08
            50, 0.45, 0.32
            ...
        """
        pass
```

#### DerivativeEstimator
```python
class DerivativeEstimator:
    """Fits splines to MI trajectories and computes derivatives."""
    
    def __init__(self, smoothing_factor: float = 0.1):
        """
        Args:
            smoothing_factor: Spline smoothing parameter (s in UnivariateSpline)
                             Lower = tighter fit, Higher = smoother curve
        """
        self.smoothing_factor = smoothing_factor
        self.spline_spurious: Optional[UnivariateSpline] = None
        self.spline_causal: Optional[UnivariateSpline] = None
    
    def fit_splines(
        self,
        timesteps: np.ndarray,  # (T,)
        mi_spurious: np.ndarray,  # (T,)
        mi_causal: np.ndarray  # (T,)
    ) -> None:
        """
        Fit univariate splines to both MI trajectories.
        
        Args:
            timesteps: Training steps (e.g., [0, 50, 100, ...])
            mi_spurious: I(Z_s; H_t) values
            mi_causal: I(Z_c; H_t) values
        """
        pass
    
    def compute_derivatives(
        self,
        timesteps: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute d/dt I(Z; H_t) via analytic spline derivative.
        
        Args:
            timesteps: Points to evaluate derivative at
        
        Returns:
            deriv_spurious: d/dt I(Z_s; H_t) at each timestep
            deriv_causal: d/dt I(Z_c; H_t) at each timestep
        
        Shapes:
            timesteps: (T,)
            deriv_spurious: (T,)
            deriv_causal: (T,)
        """
        pass
    
    def get_early_phase_derivatives(
        self,
        timesteps: np.ndarray,
        deriv_spurious: np.ndarray,
        deriv_causal: np.ndarray,
        early_phase_fraction: float = 0.1
    ) -> Tuple[float, float]:
        """
        Extract average derivatives in early-phase window.
        
        Args:
            timesteps: All training steps
            deriv_spurious: d/dt I(Z_s; H_t)
            deriv_causal: d/dt I(Z_c; H_t)
            early_phase_fraction: Fraction of training (default: 0.1 = first 10%)
        
        Returns:
            avg_deriv_spurious: Mean derivative in early phase
            avg_deriv_causal: Mean derivative in early phase
        """
        pass
```

---

### Module 4: Training Loops

#### train_supervised
```python
def train_supervised(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    mi_tracker: MITracker,
    epochs: int = 200,
    lr: float = 0.1,
    momentum: float = 0.9,
    weight_decay: float = 5e-4,
    seed: int = 1,
    device: str = "cuda"
) -> Dict[str, np.ndarray]:
    """
    Supervised training loop for digit classification.
    
    Args:
        model: Encoder + SupervisedHead
        train_loader: Training data (60k samples, batch_size=128)
        test_loader: Test data (10k samples)
        mi_tracker: MITracker instance
        epochs: Number of training epochs (200)
        lr: Initial learning rate (0.1)
        momentum: SGD momentum (0.9)
        weight_decay: L2 regularization (5e-4)
        seed: Random seed
        device: "cuda" or "cpu"
    
    Returns:
        metrics: Dict with keys:
            'train_loss': (epochs,)
            'test_accuracy': (epochs,)
            'mi_spurious': (checkpoints,)
            'mi_causal': (checkpoints,)
            'timesteps': (checkpoints,)
    
    Algorithm:
        1. Setup: SGD optimizer, cosine annealing scheduler, CE loss
        2. For each epoch:
            a. Training: Forward pass, compute loss, backward, update
            b. Every 50 steps: Call mi_tracker.compute_mi_checkpoint()
            c. End of epoch: Evaluate test accuracy
        3. Save metrics to CSV
    """
    pass
```

#### train_ssl
```python
def train_ssl(
    model: nn.Module,  # Encoder + SSLHead
    train_loader: DataLoader,
    mi_tracker: MITracker,
    epochs: int = 200,
    lr: float = 0.03,
    momentum: float = 0.9,
    temperature: float = 0.5,
    seed: int = 1,
    device: str = "cuda"
) -> Dict[str, np.ndarray]:
    """
    Self-supervised training loop (SimCLR).
    
    Args:
        model: Encoder + SSLHead
        train_loader: Training data (60k samples, batch_size=256)
        mi_tracker: MITracker instance
        epochs: Number of training epochs (200)
        lr: Initial learning rate (0.03)
        momentum: SGD momentum (0.9)
        temperature: NT-Xent temperature (0.5)
        seed: Random seed
        device: "cuda" or "cpu"
    
    Returns:
        metrics: Dict with MI trajectories and contrastive loss
    
    Algorithm:
        1. Setup: SGD optimizer, cosine annealing, NT-Xent loss
        2. For each batch:
            a. Create two augmented views (preserve color correlation!)
            b. Forward pass through encoder + projection head
            c. Compute NT-Xent loss
            d. Every 50 steps: MI checkpoint
        3. Linear probing evaluation at end
    
    NT-Xent Loss:
        For batch of size N, create 2N views (i, j positive pairs)
        loss = -log(exp(sim(z_i, z_j)/τ) / Σ_k exp(sim(z_i, z_k)/τ))
        where sim(u, v) = u·v / (||u|| ||v||)
    """
    pass
```

#### train_rl
```python
def train_rl(
    model: nn.Module,  # Encoder + ActorCriticHeads
    env: GridNavEnv,
    mi_tracker: MITracker,
    episodes: int = 200,
    lr: float = 3e-4,
    entropy_coeff: float = 0.01,
    value_loss_coeff: float = 0.5,
    seed: int = 1,
    device: str = "cuda"
) -> Dict[str, np.ndarray]:
    """
    Policy gradient RL training loop.
    
    Args:
        model: Encoder + ActorCriticHeads
        env: Grid navigation environment
        mi_tracker: MITracker instance
        episodes: Number of episodes (200)
        lr: Adam learning rate (3e-4)
        entropy_coeff: Entropy regularization (0.01)
        value_loss_coeff: Value loss weight (0.5)
        seed: Random seed
        device: "cuda" or "cpu"
    
    Returns:
        metrics: Dict with episode returns and MI trajectories
    
    Algorithm:
        1. Setup: Adam optimizer, GridNavEnv
        2. For each episode:
            a. Collect trajectory: (states, actions, rewards)
            b. Compute returns (discounted rewards)
            c. Forward pass: action_logits, values
            d. Policy loss: -log π(a|s) * advantage
            e. Value loss: MSE(value, return)
            f. Entropy loss: -H(π) for exploration
            g. Total loss: policy + value_coeff * value + entropy_coeff * entropy
            h. Every 50 steps: MI checkpoint
        3. Track episode return for convergence
    
    Tensor Shapes:
        states: (T, 3, 28, 28) episode trajectory
        actions: (T,) int [0-3]
        rewards: (T,) float
        returns: (T,) float (discounted)
        advantages: (T,) = returns - values
    """
    pass
```

---

### Module 5: Evaluation

#### compute_metrics
```python
def compute_metrics(
    paradigm: str,
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cuda"
) -> Dict[str, float]:
    """
    Compute task performance metrics.
    
    Args:
        paradigm: "supervised" | "ssl" | "rl"
        model: Trained model
        test_loader: Test data
        device: "cuda" or "cpu"
    
    Returns:
        metrics: Dict with paradigm-specific metrics
            Supervised: {'test_accuracy': float}
            SSL: {'linear_probe_accuracy': float}
            RL: {'avg_episode_return': float}
    """
    pass
```

#### plot_gate_metrics
```python
def plot_gate_metrics(
    results_supervised: Dict[str, np.ndarray],
    results_ssl: Dict[str, np.ndarray],
    results_rl: Dict[str, np.ndarray],
    save_path: str
) -> None:
    """
    Generate required gate figure: d/dt I comparison bar chart.
    
    Args:
        results_*: Training results with MI derivatives
        save_path: Path to save figure (e.g., "figures/gate_metrics_comparison.png")
    
    Figure Spec:
        - X-axis: Paradigm (Supervised, SSL, RL)
        - Y-axis: MI derivative (bits/step)
        - Two bars per paradigm: Spurious (blue) vs Causal (orange)
        - Success indicator: Blue > Orange in 2+ paradigms
        - Title: "MI Growth Rate Comparison (Early Phase)"
    """
    pass
```

---

## Pseudo-code for Key Algorithms

### Algorithm 1: MI Computation (Histogram-Based)
```python
def compute_mutual_information(
    factors: np.ndarray,  # (N,) discrete [0-9]
    representations: np.ndarray,  # (N, D) continuous
    n_bins: int = 20
) -> float:
    """
    Compute I(Z; H) using histogram-based MI.
    
    Pseudo-code:
        1. Discretize continuous representations:
           discretizer = KBinsDiscretizer(n_bins=20, encode='ordinal')
           H_discrete = discretizer.fit_transform(representations).ravel()
        
        2. Compute joint histogram:
           p_ZH = histogram2d(factors, H_discrete)
           p_ZH /= p_ZH.sum()  # Normalize to probabilities
        
        3. Compute marginals:
           p_Z = p_ZH.sum(axis=1)
           p_H = p_ZH.sum(axis=0)
        
        4. MI formula:
           MI = 0
           for z in range(10):
               for h in range(n_bins):
                   if p_ZH[z, h] > 0:
                       MI += p_ZH[z, h] * log(p_ZH[z, h] / (p_Z[z] * p_H[h]))
        
        5. Return MI in bits (base 2 logarithm)
    
    Alternative (sklearn):
        from sklearn.metrics import mutual_info_score
        return mutual_info_score(factors, H_discrete)
    """
    pass
```

### Algorithm 2: Derivative Estimation (Spline Fitting)
```python
def estimate_derivative(
    timesteps: np.ndarray,  # (T,)
    mi_values: np.ndarray,  # (T,)
    smoothing: float = 0.1
) -> np.ndarray:  # (T,)
    """
    Estimate d/dt I(Z; H_t) via spline derivative.
    
    Pseudo-code:
        1. Fit univariate spline:
           from scipy.interpolate import UnivariateSpline
           spline = UnivariateSpline(timesteps, mi_values, s=smoothing)
        
        2. Compute analytic derivative:
           derivative_spline = spline.derivative()
           mi_derivative = derivative_spline(timesteps)
        
        3. Return derivative array
    
    Smoothing parameter:
        s = 0.1: Balances fidelity vs smoothness
        Too low → overfitting to noise
        Too high → over-smoothing (misses dynamics)
    """
    pass
```

### Algorithm 3: Early-Phase Detection
```python
def detect_early_phase(
    timesteps: np.ndarray,
    performance: np.ndarray,  # Loss or accuracy
    method: str = "fraction"  # "fraction" or "performance"
) -> int:
    """
    Detect early-phase window t_0.
    
    Method 1 (fraction):
        t_0 = timesteps[int(0.1 * len(timesteps))]  # First 10% of training
    
    Method 2 (performance):
        final_perf = performance[-1]
        threshold = 0.3 * final_perf
        t_0 = timesteps[np.argmax(performance >= threshold)]
    
    Return: t_0 (timestep marking end of early phase)
    """
    pass
```

---

## Tensor Shape Summary

| Module | Input Shape | Output Shape | Notes |
|--------|-------------|--------------|-------|
| ColoredMNISTWrapper | - | (3, 28, 28) | RGB colored MNIST |
| Encoder (layer4) | (B, 3, 28, 28) | (B, 512, 4, 4) | MI extraction point |
| Encoder (final) | (B, 3, 28, 28) | (B, 512) | After avgpool |
| SupervisedHead | (B, 512) | (B, 10) | Logits |
| SSLHead | (B, 512) | (B, 128) | L2-normalized |
| ActorCriticHeads | (B, 512) | (B, 4), (B, 1) | Policy, value |
| MITracker (raw) | (B, 512, 4, 4) | (B, 8192) | Flattened |
| MITracker (discrete) | (B, 8192) | (B,) | Discretized [0-19] |

---

## External Dependencies

### PyTorch Ecosystem
- `torch.nn`: Neural network modules
- `torch.optim.SGD`: Supervised/SSL optimizer
- `torch.optim.Adam`: RL optimizer
- `torchvision.models.resnet18`: Baseline architecture
- `torchmetrics.Accuracy`: Evaluation metric

### Scientific Computing
- `sklearn.metrics.mutual_info_score`: MI computation
- `sklearn.preprocessing.KBinsDiscretizer`: Representation discretization
- `scipy.interpolate.UnivariateSpline`: Spline fitting for derivatives
- `numpy`: Array operations

### Visualization
- `matplotlib.pyplot`: Figure generation
- `seaborn`: Statistical plotting

---

**Document Status:** Complete  
**Subtask Count:** 5 (within budget)  
**Next:** Configuration Design (03_config.md)
