---
name: "Logic Design: h-e1 Three-Tier Contamination Detection System"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
date: 2026-05-11
phase: Phase 3 - Logic Design
source: 03_architecture.md, 03_prd.md
allocated_budget: 5 subtasks (E-5 Tier3 Geometric, E-4 Tier2 TSG)
---

# Logic Design: h-e1

**Hypothesis Type:** EXISTENCE (PoC)
**Focus:** High-complexity tasks only (E-5, E-4)
**Budget:** 5 subtasks total

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation from scratch - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## E-5: Tier3GeometricDetection [Complexity: 16, Budget: 3/5]

**Applied**: Standard PyTorch gradient computation, Hessian eigenvalue patterns from pytorch-hessian-eigenthings

### API Signatures

```python
class Tier3GeometricDetection:
    """Geometric trajectory-based contamination detection via 4 metrics."""
    
    def __init__(
        self, 
        model: nn.Module, 
        benchmark_dataloader: DataLoader,
        device: str = "cuda"
    ):
        """
        Initialize detector with model and benchmark data.
        
        Args:
            model: Trained model to analyze
            benchmark_dataloader: DataLoader with benchmark samples (GSM8K)
            device: Compute device
        """
        self.model = model
        self.benchmark_dataloader = benchmark_dataloader
        self.device = device
    
    def compute_gradient_overlap(self) -> float:
        """
        Gradient subspace overlap metric.
        
        Returns:
            float: Cosine similarity ∈ [0,1]. grad: [P], update: [P]
        """
        ...
    
    def compute_hessian_concentration(self) -> float:
        """
        Hessian spectral concentration via Lanczos.
        
        Returns:
            float: Eigenvalue concentration ratio. top10_eigvals: [10]
        """
        ...
    
    def compute_cka_alignment(self) -> float:
        """
        CKA representational alignment.
        
        Returns:
            float: Centered kernel alignment ∈ [0,1]. activations: [N, H]
        """
        ...
    
    def compute_efficiency_zscore(
        self, 
        baseline_mean: float, 
        baseline_std: float
    ) -> float:
        """
        Information efficiency Z-score.
        
        Args:
            baseline_mean: Clean runs mean efficiency
            baseline_std: Clean runs std efficiency
        
        Returns:
            float: Z-score = (efficiency - mean) / std
        """
        ...
    
    def detect(self, thresholds: dict) -> dict:
        """
        Run detection with ≥2/4 threshold logic.
        
        Args:
            thresholds: {
                'gradient_overlap': 0.10,
                'hessian_concentration': 1.5,
                'cka_alignment': 0.15,
                'efficiency_zscore': 2.5
            }
        
        Returns:
            {
                'detected': bool,
                'metrics': {
                    'gradient_overlap': float,
                    'hessian_concentration': float,
                    'cka_alignment': float,
                    'efficiency_zscore': float
                },
                'num_exceeded': int  # How many metrics exceeded thresholds
            }
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model.parameters() | [P] | Flattened parameter vector |
| grad_benchmark | [P] | Gradient on benchmark data |
| param_update | [P] | Weight update direction |
| hessian_eigvals | [10] | Top-10 eigenvalues |
| activations | [N, H] | Layer activations for CKA |
| accuracy_gain | scalar | GSM8K acc improvement |
| tokens_seen | scalar | Total training tokens |

### Pseudo-code

```
# Metric 1: Gradient Overlap
1. Compute grad_benchmark on GSM8K data
2. Compute param_update = params_after - params_before
3. cosine_sim = dot(grad_benchmark, param_update) / (norm(grad) * norm(update))
4. Return cosine_sim

# Metric 2: Hessian Concentration
1. Use hessian_eigenthings.compute_hessian_eigenthings(model, dataloader, num_eigenthings=10)
2. Get top-10 eigenvalues λ_1 ≥ λ_2 ≥ ... ≥ λ_10
3. concentration = λ_1 / mean(λ_2...λ_10)
4. Return concentration

# Metric 3: CKA Alignment
1. Extract activations on clean data → A_clean [N, H]
2. Extract activations on benchmark data → A_bench [N, H]
3. Compute CKA(A_clean, A_bench) using centered kernel alignment
4. Return CKA score

# Metric 4: Efficiency Z-score
1. efficiency = (acc_after - acc_before) / tokens_seen
2. z_score = (efficiency - baseline_mean) / baseline_std
3. Return z_score

# Detection Logic
1. Compute all 4 metrics
2. Count how many exceed thresholds
3. If count ≥ 2: detected=True
4. Return {detected, metrics, num_exceeded}
```

### Subtasks [3/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Gradient/Hessian computation | Implement gradient overlap + Hessian concentration using pytorch-hessian-eigenthings |
| L-5-2 | CKA alignment | Implement centered kernel alignment for representational similarity |
| L-5-3 | Detection logic | Implement efficiency Z-score + ≥2/4 threshold logic |

---

## E-4: Tier2TSGProbes [Complexity: 13, Budget: 2/5]

**Applied**: Standard PyTorch loss tracking, differential alignment pattern

### API Signatures

```python
class Tier2TSGProbes:
    """Task Signature Graph probe-based detection."""
    
    def __init__(
        self, 
        benchmark_samples: List[dict],
        num_invariant: int = 1000,
        num_neighbor: int = 1000,
        num_broken: int = 1000
    ):
        """
        Initialize probe generator.
        
        Args:
            benchmark_samples: GSM8K test samples
            num_invariant: Number of TSG-aligned probes
            num_neighbor: Number of off-manifold neighbor probes
            num_broken: Number of broken-control probes
        """
        self.benchmark_samples = benchmark_samples
        self.num_invariant = num_invariant
        self.num_neighbor = num_neighbor
        self.num_broken = num_broken
    
    def extract_tsg_invariants(self, samples: List[dict]) -> List[dict]:
        """
        Extract invariant probes from GSM8K samples.
        
        Args:
            samples: [{'question': str, 'answer': str}, ...]
        
        Returns:
            List[dict]: Invariant probes aligned with task signature
        """
        ...
    
    def generate_neighbor_probes(self, samples: List[dict]) -> List[dict]:
        """
        Generate off-manifold neighbor probes.
        
        Args:
            samples: Source samples for perturbation
        
        Returns:
            List[dict]: Neighbor probes (similar but off-TSG)
        """
        ...
    
    def generate_broken_probes(self, samples: List[dict]) -> List[dict]:
        """
        Generate broken-control probes with constraint violations.
        
        Args:
            samples: Source samples for violation
        
        Returns:
            List[dict]: Broken probes (invalid constraints)
        """
        ...
    
    def evaluate_probes(
        self, 
        model: nn.Module, 
        probes: List[dict],
        tokenizer: Any
    ) -> List[float]:
        """
        Evaluate probe losses on model.
        
        Args:
            model: Model to evaluate
            probes: List of probe samples
            tokenizer: Tokenizer for encoding
        
        Returns:
            List[float]: Per-probe losses. losses: [num_probes]
        """
        ...
    
    def compute_differential_alignment(
        self, 
        model: nn.Module, 
        tokenizer: Any,
        clean_mean: float,
        clean_std: float
    ) -> dict:
        """
        Compute differential alignment Δ and detect contamination.
        
        Args:
            model: Trained model to analyze
            tokenizer: Tokenizer for encoding
            clean_mean: Baseline mean Δ from clean runs
            clean_std: Baseline std Δ from clean runs
        
        Returns:
            {
                'detected': bool,  # Δ > 2σ threshold
                'delta': float,    # Differential alignment
                'z_score': float,  # (Δ - mean) / std
                'losses': {
                    'invariant': List[float],
                    'neighbor': List[float],
                    'broken': List[float]
                }
            }
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| probes (invariant/neighbor/broken) | List[dict] | 1000 samples each |
| probe_losses | [num_probes] | Per-probe loss values |
| loss_invariant | [1000] | Invariant probe losses |
| loss_neighbor | [1000] | Neighbor probe losses |
| delta_loss_invariant | scalar | Mean loss change for invariant |
| delta_loss_neighbor | scalar | Mean loss change for neighbor |
| differential_alignment | scalar | Δ = delta_loss_invariant - delta_loss_neighbor |

### Pseudo-code

```
# Probe Generation
1. extract_tsg_invariants: Sample 1000 from benchmark, apply minimal perturbation
2. generate_neighbor_probes: Perturb constraint structure (off-manifold)
3. generate_broken_probes: Introduce solution/constraint violations

# Probe Evaluation
1. For each probe in [invariant, neighbor, broken]:
   a. Tokenize probe text
   b. Forward pass through model
   c. Compute loss on answer tokens
   d. Store loss value
2. Return losses array [num_probes]

# Differential Alignment Detection
1. Evaluate invariant probes → loss_invariant [1000]
2. Evaluate neighbor probes → loss_neighbor [1000]
3. Compute delta_loss_invariant = mean(loss_invariant)
4. Compute delta_loss_neighbor = mean(loss_neighbor)
5. Differential alignment Δ = delta_loss_invariant - delta_loss_neighbor
6. Z-score = (Δ - clean_mean) / clean_std
7. If Z-score > 2.0: detected=True
8. Return {detected, delta, z_score, losses}
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Probe generation | Implement invariant/neighbor/broken probe generation from GSM8K samples |
| L-4-2 | Differential alignment | Implement probe evaluation + differential alignment Δ computation with threshold detection |

---

## Summary

**Total Subtasks Used**: 5/5
- E-5 Tier3 Geometric: 3 subtasks
- E-4 Tier2 TSG: 2 subtasks

**Key APIs for Phase 4 Coder:**
- `Tier3GeometricDetection.__init__()` → 4 metric methods → `detect()`
- `Tier2TSGProbes.__init__()` → 3 probe generators → `evaluate_probes()` → `compute_differential_alignment()`

**Critical Dependencies:**
- `pytorch-hessian-eigenthings` for Hessian computation
- Standard PyTorch for gradients, loss tracking
- CKA implementation for representational alignment

**Detection Thresholds (from PRD):**
- Tier 2: Δ > 2σ (clean baseline)
- Tier 3: ≥2/4 metrics exceed thresholds

---

*Generated by Phase 3 Logic Agent | Hypothesis: h-e1 (EXISTENCE) | Budget: 5 subtasks | Focus: E-5, E-4 high-complexity tasks*
