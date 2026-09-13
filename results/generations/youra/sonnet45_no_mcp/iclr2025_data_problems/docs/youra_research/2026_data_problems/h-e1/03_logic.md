# Logic Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Date:** 2026-04-15  
**Version:** 1.0  

Applied: **PyTorch Training Loop Pattern** - Standard deep learning training with distributed support

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A (no existing code)  
**Findings:** Green-field EXISTENCE hypothesis - designing minimal PoC architecture  

**Note:** MCP unavailable in test environment. Using standard PyTorch patterns from training data.

---

## Module APIs

### 1. Data Module (`data/loader.py`)

#### CurriculumDataLoader
```python
class CurriculumDataLoader:
    def __init__(
        self, 
        domains: Dict[str, Dataset],
        diversity_scores: Dict[str, float],
        condition: str,  # "static", "diversity_ranked", "reversed", "shuffled"
        batch_size: int,
        sequence_length: int = 2048
    ):
        """Initialize curriculum data loader with domain scheduling."""
        pass
    
    def get_domain_weights(self, training_progress: float) -> Dict[str, float]:
        """
        Calculate domain sampling weights based on training progress.
        
        Args:
            training_progress: Float in [0.0, 1.0] representing fraction of training complete
            
        Returns:
            Dict mapping domain name to sampling weight (sum to 1.0)
            
        Shapes:
            - Input: scalar float
            - Output: dict of 6 floats (one per domain)
        """
        pass
    
    def __iter__(self) -> Iterator[Dict[str, Tensor]]:
        """
        Yield batches with dynamic domain mixing.
        
        Returns:
            Dict with keys: 'input_ids' (B, L), 'labels' (B, L), 'domain' (B,)
            
        Shapes:
            - input_ids: (batch_size, sequence_length) int64
            - labels: (batch_size, sequence_length) int64
            - domain: (batch_size,) int64
        """
        pass
```

---

### 2. Model Module (`model/gpt.py`)

#### GPT2Model
```python
class GPT2Model(nn.Module):
    def __init__(
        self,
        vocab_size: int = 50257,
        n_layer: int = 24,
        n_head: int = 16,
        n_embd: int = 1536,
        n_positions: int = 2048,
        dropout: float = 0.1
    ):
        """GPT-2 style transformer decoder."""
        pass
    
    def forward(
        self,
        input_ids: Tensor,
        attention_mask: Optional[Tensor] = None
    ) -> Tensor:
        """
        Forward pass through transformer.
        
        Args:
            input_ids: Token indices (B, L)
            attention_mask: Causal mask (B, L, L)
            
        Returns:
            Logits over vocabulary (B, L, V)
            
        Shapes:
            - input_ids: (B, L) int64
            - attention_mask: (B, L, L) bool (optional)
            - output: (B, L, vocab_size) float32
        """
        pass
    
    def get_loss(self, input_ids: Tensor, labels: Tensor) -> Tensor:
        """
        Compute cross-entropy loss.
        
        Args:
            input_ids: Input tokens (B, L)
            labels: Target tokens (B, L)
            
        Returns:
            Scalar loss tensor
            
        Shapes:
            - input_ids: (B, L) int64
            - labels: (B, L) int64
            - loss: () float32 (scalar)
        """
        pass
```

---

### 3. Training Module (`train.py`)

#### Trainer
```python
class Trainer:
    def __init__(
        self,
        model: nn.Module,
        train_loader: CurriculumDataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        scheduler: torch.optim.lr_scheduler._LRScheduler,
        config: TrainConfig
    ):
        """Initialize trainer with model and data."""
        pass
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """
        Train for one epoch with curriculum scheduling.
        
        Returns:
            Metrics: {'loss': float, 'ppl': float, 'lr': float}
        """
        pass
    
    def validate(self) -> Dict[str, float]:
        """
        Validate on held-out validation set.
        
        Returns:
            Metrics: {'val_loss': float, 'val_ppl': float}
        """
        pass
    
    def save_checkpoint(self, path: str, metadata: Dict):
        """Save model checkpoint with training state."""
        pass
```

---

### 4. Evaluation Module (`evaluate.py`)

#### BenchmarkEvaluator
```python
class BenchmarkEvaluator:
    def __init__(
        self,
        model: nn.Module,
        benchmarks: List[str],  # ["mmlu", "bigbench", "hellaswag", ...]
        num_fewshot: int = 5
    ):
        """Initialize evaluator with lm-evaluation-harness."""
        pass
    
    def evaluate_all(self) -> Dict[str, float]:
        """
        Run all benchmarks and return composite score.
        
        Returns:
            Dict with keys: 'mmlu', 'bigbench', 'hellaswag', 'winogrande', 
                           'humaneval', 'mbpp', 'scienceqa', 'composite'
        """
        pass
    
    def compute_participation_ratio(
        self,
        probe_dataset: Dataset
    ) -> float:
        """
        Compute gradient covariance rank (Participation Ratio).
        
        Algorithm:
            1. Sample gradients on probe dataset
            2. Compute empirical covariance matrix
            3. Calculate eigenvalues
            4. PR = (sum(λ))² / sum(λ²)
            
        Returns:
            Participation ratio (scalar float)
            
        Complexity: O(N*D²) where N=probe_size, D=param_count
        """
        pass
    
    def compute_cka_similarity(
        self,
        model_checkpoint1: str,
        model_checkpoint2: str,
        dataloader: DataLoader
    ) -> np.ndarray:
        """
        Compute layer-wise CKA between two checkpoints.
        
        Returns:
            CKA matrix: (n_layers, n_layers) float
        """
        pass
```

---

### 5. Statistical Validation Module (`stats.py`)

#### StatisticalValidator
```python
class StatisticalValidator:
    def __init__(
        self,
        results: Dict[str, List[float]]  # condition -> list of 5 seed results
    ):
        """Initialize with experimental results."""
        pass
    
    def paired_t_test(
        self,
        condition_a: str,
        condition_b: str,
        bonferroni_correction: bool = True
    ) -> Dict[str, float]:
        """
        Perform paired t-test with optional Bonferroni correction.
        
        Returns:
            {'t_statistic': float, 'p_value': float, 'ci_lower': float, 'ci_upper': float}
        """
        pass
    
    def check_gate_condition(
        self,
        scale: str  # "1B" or "7B"
    ) -> Dict[str, Any]:
        """
        Validate MUST_WORK gate condition.
        
        For 1B: diversity_ranked > static + 2.0% (p<0.05)
        For 7B: diversity_ranked > static + 0.5% (p<0.05)
        
        Returns:
            {'passed': bool, 'improvement': float, 'p_value': float, 'threshold': float}
        """
        pass
```

---

## Algorithm Pseudo-code

### Curriculum Weight Computation
```python
def get_domain_weights(training_progress: float, condition: str) -> Dict[str, float]:
    """
    Compute domain sampling weights for current training step.
    
    Conditions:
        - static: uniform 16.67% throughout
        - diversity_ranked: Gaussian peaks from high→low diversity
        - reversed: Gaussian peaks from low→high diversity
        - shuffled: random order, same Gaussian scheduling
    """
    
    # Diversity scores (precomputed)
    diversity = {
        "Pile-CC": 0.92, "StackExchange": 0.88, "Wikipedia": 0.75,
        "ArXiv": 0.58, "Github": 0.42, "PubMed": 0.35
    }
    
    if condition == "static":
        return {d: 1.0/6 for d in diversity.keys()}
    
    # Sort by diversity
    if condition == "diversity_ranked":
        ranked = sorted(diversity.keys(), key=lambda d: diversity[d], reverse=True)
    elif condition == "reversed":
        ranked = sorted(diversity.keys(), key=lambda d: diversity[d], reverse=False)
    else:  # shuffled
        ranked = random.shuffle(list(diversity.keys()))
    
    # Gaussian scheduling
    weights = {}
    for i, domain in enumerate(ranked):
        peak_time = i / len(ranked)  # When this domain peaks
        weight = exp(-((training_progress - peak_time) / 0.3) ** 2)
        weights[domain] = max(weight, 0.05)  # Minimum 5%
    
    # Normalize
    total = sum(weights.values())
    return {d: w / total for d, w in weights.items()}
```

### Participation Ratio Computation
```python
def compute_participation_ratio(model: nn.Module, probe_data: DataLoader) -> float:
    """
    Measure gradient covariance rank via Participation Ratio.
    
    Steps:
        1. Collect gradients on fixed probe dataset
        2. Flatten gradients to vectors
        3. Compute empirical covariance
        4. Extract eigenvalues
        5. Calculate PR = (Σλ)² / Σ(λ²)
    """
    
    gradients = []
    for batch in probe_data:
        loss = model.get_loss(batch['input_ids'], batch['labels'])
        loss.backward()
        
        # Flatten all gradients to single vector
        grad_vector = torch.cat([p.grad.flatten() for p in model.parameters()])
        gradients.append(grad_vector)
        
        model.zero_grad()
    
    # Stack: (n_samples, n_params)
    G = torch.stack(gradients)
    
    # Empirical covariance: (n_params, n_params)
    cov = torch.cov(G.T)
    
    # Eigenvalues
    eigenvalues = torch.linalg.eigvalsh(cov)
    
    # Participation Ratio
    pr = (eigenvalues.sum() ** 2) / (eigenvalues ** 2).sum()
    
    return pr.item()
```

---

## Tensor Shape Reference

### Training Loop Shapes
```
Input Batch:
- input_ids: (batch_size, 2048) int64
- labels: (batch_size, 2048) int64

Model Forward:
- embeddings: (B, L, n_embd)
- attention: (B, n_head, L, L)
- hidden: (B, L, n_embd) × n_layer
- logits: (B, L, vocab_size)

Loss:
- cross_entropy: () scalar
```

### Gradient Geometry Shapes
```
Gradient Collection:
- per_batch_grad: (n_params,) float32
- all_grads: (n_samples, n_params) float32

Covariance:
- cov_matrix: (n_params, n_params) float32
- eigenvalues: (n_params,) float32
- PR: () scalar float32
```

### CKA Computation Shapes
```
Layer Activations:
- layer_i_activations: (n_samples, hidden_dim) float32
- layer_j_activations: (n_samples, hidden_dim) float32

CKA Matrix:
- similarity: (n_layers, n_layers) float32
```

---

## Subtask Breakdown

### E-3: Model + Training (4 subtasks)
1. **GPT-2 Model Implementation** - Transformer decoder with multi-head attention
2. **Training Loop** - Distributed training with gradient accumulation
3. **Checkpointing** - Save at 10%, 25%, 50%, 75%, 100% progress
4. **Optimizer Setup** - AdamW with cosine learning rate decay

### E-4: Evaluation Harness (3 subtasks)
1. **Benchmark Integration** - lm-evaluation-harness for MMLU, Big-Bench, domain tasks
2. **Gradient Geometry** - Participation Ratio computation
3. **Statistical Tests** - Paired t-tests with Bonferroni correction

---

## Dependencies

**External Libraries:**
- PyTorch >= 2.0
- transformers (Hugging Face)
- lm-evaluation-harness
- numpy, scipy
- datasets (Hugging Face)

**Internal Modules:**
- data.loader → model.gpt (for training)
- model.gpt → evaluate (for benchmarks)
- train → evaluate (for PR computation)

---

**Total Subtasks:** 7 (within budget of 7)
