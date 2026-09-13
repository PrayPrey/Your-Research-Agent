---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3
created_at: 2026-05-12
author: logic-agent
---

# Logic Design: H-E1 Geometric Uncertainty Correlation

**Applied Patterns**: Standard PyTorch nn.Module design, inference-only computation

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: New implementation - designing APIs from scratch
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-4: Geometric Features [Complexity: 12, Budget: 2]

**Applied**: PyTorch tensor operations, eigenvalue decomposition patterns

### API Signatures

```python
class GeometricFeatureComputer:
    """Compute geometric features from hidden states."""
    
    def __init__(self, epsilon: float = 1e-12):
        """Initialize with numerical stability epsilon."""
        self.epsilon = epsilon
    
    def compute_covariance(self, hidden_states: List[torch.Tensor]) -> torch.Tensor:
        """
        Compute covariance matrix from multi-layer hidden states.
        
        Args:
            hidden_states: List of 8 tensors, each [N, 4096]
        
        Returns:
            Covariance matrix [4096, 4096]
        """
        pass
    
    def compute_eigenvalues(self, cov_matrix: torch.Tensor) -> torch.Tensor:
        """
        Compute eigenvalues of covariance matrix.
        
        Args:
            cov_matrix: [4096, 4096] symmetric matrix
        
        Returns:
            Eigenvalues [4096] sorted descending
        """
        pass
    
    def compute_participation_ratio(self, eigenvalues: torch.Tensor) -> float:
        """
        Compute participation ratio PR = (Σλᵢ)² / (Σλᵢ²).
        
        Args:
            eigenvalues: [4096] tensor
        
        Returns:
            PR scalar in [1, 4096]
        """
        pass
    
    def compute_eigenvalue_decay(self, eigenvalues: torch.Tensor) -> float:
        """
        Compute eigenvalue decay rate α via linear fit.
        
        Args:
            eigenvalues: [4096] tensor
        
        Returns:
            Slope α of log-eigenvalue spectrum
        """
        pass
    
    def compute_condition_number(self, eigenvalues: torch.Tensor) -> float:
        """
        Compute condition number κ = λ_max / λ_min.
        
        Args:
            eigenvalues: [4096] tensor
        
        Returns:
            Condition number κ >= 1
        """
        pass
    
    def compute_all_features(self, hidden_states: List[torch.Tensor]) -> Dict[str, float]:
        """
        Compute all geometric features in one pass.
        
        Args:
            hidden_states: List of 8 tensors [N, 4096] from layers 24-31
        
        Returns:
            {'pr': float, 'alpha': float, 'kappa': float}
        """
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states (input) | List[8 × [N, 4096]] | N questions, 8 layers |
| X_stacked | [N×8, 4096] | Concatenated layers |
| X_centered | [N×8, 4096] | Mean-centered |
| cov_matrix | [4096, 4096] | Symmetric covariance |
| eigenvalues | [4096] | Sorted descending |
| PR | scalar | Participation ratio |
| α | scalar | Decay rate |
| κ | scalar | Condition number |

### Pseudo-code

```
compute_all_features(hidden_states):
    1. Stack hidden states: X = concat(hidden_states, dim=0)  # [N×8, 4096]
    2. Center: X_c = X - mean(X, dim=0)  # [N×8, 4096]
    3. Covariance: C = (X_c^T @ X_c) / (N×8 - 1)  # [4096, 4096]
    4. Eigenvalues: λ = eigvalsh(C)  # [4096], sorted ascending
    5. Reverse sort: λ = flip(λ)  # descending order
    6. PR = (sum(λ))² / (sum(λ²) + ε)
    7. α = linear_fit(log(λ + ε), indices).slope
    8. κ = λ[0] / (λ[-1] + ε)
    9. Return {pr: PR, alpha: α, kappa: κ}

compute_covariance(hidden_states):
    1. X = torch.cat(hidden_states, dim=0)  # [N×8, 4096]
    2. X_c = X - X.mean(dim=0, keepdim=True)
    3. Return (X_c.T @ X_c) / (X.shape[0] - 1)

compute_eigenvalues(cov_matrix):
    1. λ = torch.linalg.eigvalsh(cov_matrix)  # symmetric solver
    2. Return torch.flip(λ, dims=[0])  # descending

compute_participation_ratio(eigenvalues):
    1. sum_λ = eigenvalues.sum()
    2. sum_λ² = (eigenvalues ** 2).sum()
    3. Return (sum_λ ** 2) / (sum_λ² + self.epsilon)

compute_eigenvalue_decay(eigenvalues):
    1. log_λ = torch.log(eigenvalues + self.epsilon)
    2. indices = torch.arange(len(eigenvalues), dtype=torch.float32)
    3. Fit: α = linear_regression(indices, log_λ).slope
    4. Return α

compute_condition_number(eigenvalues):
    1. λ_max = eigenvalues[0]
    2. λ_min = eigenvalues[-1]
    3. Return λ_max / (λ_min + self.epsilon)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Covariance & Eigenvalue | Implement covariance computation and symmetric eigenvalue decomposition |
| L-4-2 | Feature Extraction | Implement PR/α/κ computation with numerical stability |

---

## A-5: Semantic Entropy [Complexity: 14, Budget: 4]

**Applied**: HuggingFace transformers generation API, NLI clustering pattern

### API Signatures

```python
class SemanticEntropyComputer:
    """Compute semantic entropy via generation + NLI clustering."""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        nli_model: str = "microsoft/deberta-v3-base",
        device: str = "cuda"
    ):
        """Initialize generation model and NLI model."""
        self.device = device
        self.model = None
        self.tokenizer = None
        self.nli_model = None
        self.nli_tokenizer = None
    
    def load_models(self) -> None:
        """Load generation and NLI models."""
        pass
    
    def generate_samples(
        self,
        questions: List[str],
        k: int = 10,
        temperature: float = 0.7,
        max_new_tokens: int = 50
    ) -> Tuple[List[List[str]], List[List[float]]]:
        """
        Generate K samples per question with likelihoods.
        
        Args:
            questions: List of N question strings
            k: Number of samples per question
            temperature: Sampling temperature
            max_new_tokens: Max generation length
        
        Returns:
            generations: List of N × [K strings]
            likelihoods: List of N × [K floats]
        """
        pass
    
    def cluster_generations(
        self,
        generations: List[str],
        threshold: float = 0.5
    ) -> List[int]:
        """
        Cluster K generations via NLI entailment.
        
        Args:
            generations: K generation strings
            threshold: Entailment score threshold
        
        Returns:
            cluster_ids: K integers (cluster assignment)
        """
        pass
    
    def compute_entropy(
        self,
        cluster_ids: List[int],
        likelihoods: List[float]
    ) -> float:
        """
        Compute semantic entropy from clusters.
        
        Args:
            cluster_ids: K cluster assignments
            likelihoods: K generation likelihoods
        
        Returns:
            Semantic entropy in bits
        """
        pass
    
    def compute_all_entropies(
        self,
        questions: List[str],
        k: int = 10,
        temperature: float = 0.7
    ) -> List[float]:
        """
        Compute semantic entropy for all questions.
        
        Args:
            questions: N question strings
            k: Samples per question
            temperature: Sampling temperature
        
        Returns:
            entropies: N semantic entropy values
        """
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| questions | [N] | Input questions (strings) |
| input_ids | [N, L] | Tokenized, L=max length |
| generations | [N, K] | K samples per question (strings) |
| likelihoods | [N, K] | Generation log-probs |
| nli_input | [K×K, L_nli] | Pairwise NLI inputs |
| nli_scores | [K, K] | Entailment matrix |
| cluster_ids | [K] | Cluster assignments per question |
| entropy | scalar | Per-question SE |

### Pseudo-code

```
compute_all_entropies(questions, k, temperature):
    1. generations, likelihoods = generate_samples(questions, k, temperature)
    2. entropies = []
    3. For each question i:
        a. clusters = cluster_generations(generations[i])
        b. entropy = compute_entropy(clusters, likelihoods[i])
        c. entropies.append(entropy)
    4. Return entropies

generate_samples(questions, k, temperature):
    1. tokenize: input_ids = tokenizer(questions)  # [N, L]
    2. generations = []
    3. likelihoods = []
    4. For each question:
        a. samples = model.generate(
            input_ids[i],
            num_return_sequences=k,
            do_sample=True,
            temperature=temperature,
            return_dict_in_generate=True,
            output_scores=True
        )
        b. Decode samples → K strings
        c. Compute log-likelihoods from scores
        d. generations.append(K strings)
        e. likelihoods.append(K likelihoods)
    5. Return generations, likelihoods

cluster_generations(generations):
    1. K = len(generations)
    2. entailment_matrix = zeros([K, K])  # [K, K]
    3. For i in range(K):
        For j in range(K):
            a. premise = generations[i]
            b. hypothesis = generations[j]
            c. nli_input = f"{premise} [SEP] {hypothesis}"
            d. logits = nli_model(nli_input)  # [3] (entail, neutral, contradict)
            e. entailment_matrix[i, j] = softmax(logits)[0]  # entailment prob
    4. Cluster via threshold:
        a. clusters = []
        b. assigned = [False] * K
        c. cluster_id = 0
        d. For i in range(K):
            If not assigned[i]:
                cluster_id++
                clusters[i] = cluster_id
                assigned[i] = True
                For j in range(i+1, K):
                    If entailment_matrix[i,j] > threshold and entailment_matrix[j,i] > threshold:
                        clusters[j] = cluster_id
                        assigned[j] = True
    5. Return clusters

compute_entropy(cluster_ids, likelihoods):
    1. Normalize likelihoods → probabilities p = exp(likelihoods) / sum(exp(likelihoods))
    2. Aggregate probabilities by cluster:
        cluster_probs = {}
        For i, cluster in enumerate(cluster_ids):
            cluster_probs[cluster] += p[i]
    3. Compute entropy:
        SE = -sum(p_c * log(p_c) for p_c in cluster_probs.values())
    4. Return SE
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Generation Sampling | Implement K-sample generation with temperature sampling |
| L-5-2 | NLI Clustering | Implement pairwise NLI entailment scoring and clustering |
| L-5-3 | Entropy Computation | Compute semantic entropy from cluster probabilities |
| L-5-4 | Integration | End-to-end pipeline for batch processing questions |

---

## Supporting Modules (Low Complexity - Not Detailed)

### A-3: Hidden State Extraction

**Brief API** (implemented by Phase 4 directly):
```python
class HiddenStateExtractor:
    def extract_hidden_states(self, questions: List[str], batch_size: int) -> Dict[int, List[torch.Tensor]]:
        """Extract layers 24-31 final token states. Returns {layer_id: [N, 4096]}"""
        pass
```

### A-6: Correlation Analysis

**Brief API** (implemented by Phase 4 directly):
```python
class CorrelationAnalyzer:
    def compute_spearman(self, features: np.ndarray, entropies: np.ndarray) -> Tuple[float, float]:
        """Returns (rho, p_value)"""
        pass
    
    def bootstrap_ci(self, features: np.ndarray, entropies: np.ndarray, n_resamples: int = 1000) -> Tuple[float, float]:
        """Returns (ci_lower, ci_upper)"""
        pass
```

---

## Integration Flow

```
1. Load TruthfulQA → questions: [N]
2. Extract hidden states → hidden_states: {layer: [N, 4096]} for layers 24-31
3. Compute geometric features → features: [N, 3] (PR, α, κ)
4. Compute semantic entropy → entropies: [N]
5. Correlation analysis → results: {rho, p_value, ci_95}
6. Gate evaluation → PASS/FAIL
```

---

## Numerical Stability Notes

### Eigenvalue Computation
- Use `torch.linalg.eigvalsh` for symmetric matrices (numerically stable)
- Float32 precision for covariance/eigenvalue steps
- Epsilon handling: Add ε=1e-12 to denominators

### Generation Likelihood
- Store log-probabilities to avoid underflow
- Convert to probabilities only during entropy computation
- Use `torch.logsumexp` for stable normalization

### NLI Scores
- Apply softmax to NLI logits for calibrated probabilities
- Threshold bidirectional entailment (both i→j and j→i)

---

*Generated by logic-agent*
*Date: 2026-05-12*
*Budget Used: 6/6 subtasks*
*Next: Phase 4 - Task Implementation*
