# Logic Design: h-e1

**Hypothesis:** Dimensional Separability in Trustworthiness Benchmarks  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-04-14  
**Budget:** 8 subtasks (E2: 4, E4: 2, E5: 2)

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - fresh PoC experiment

---

## Applied Knowledge Base Patterns

**Applied**: PyTorch evaluation pattern, statistical analysis module, benchmark integration pattern

---

## E2: Benchmark Evaluators [Complexity: 14, Budget: 4]

### API Signatures

```python
class TruthfulQAEvaluator:
    """Evaluator for TruthfulQA benchmark (truthfulness dimension)."""
    
    def __init__(self, cache_dir: str = "./data"):
        """Initialize evaluator and load dataset."""
        pass
    
    def evaluate(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> float:
        """
        Evaluate model on TruthfulQA.
        Returns: MC2 normalized probability mass score [0, 1]
        """
        pass


class BOLDEvaluator:
    """Evaluator for BOLD benchmark (fairness dimension)."""
    
    def __init__(self, cache_dir: str = "./data"):
        """Initialize evaluator and load dataset."""
        pass
    
    def evaluate(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> float:
        """
        Evaluate model on BOLD.
        Returns: Mean sentiment bias score [0, 1], lower = fairer
        """
        pass


class HaluEvalEvaluator:
    """Evaluator for HaluEval benchmark (hallucination dimension)."""
    
    def __init__(self, cache_dir: str = "./data"):
        """Initialize evaluator and load dataset."""
        pass
    
    def evaluate(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> float:
        """
        Evaluate model on HaluEval.
        Returns: Hallucination detection accuracy [0, 1]
        """
        pass


class TextAttackEvaluator:
    """Evaluator for TextAttack benchmark (robustness dimension)."""
    
    def __init__(self, attack_recipe: str = "textfooler", cache_dir: str = "./data"):
        """Initialize evaluator with attack recipe."""
        pass
    
    def evaluate(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer) -> float:
        """
        Evaluate model robustness under adversarial attacks.
        Returns: Attack success rate [0, 1], lower = more robust
        """
        pass
    
    def apply_perturbations(self, texts: List[str]) -> List[str]:
        """
        Apply TextFooler perturbations to input texts.
        Returns: List of perturbed texts (same length as input)
        """
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | Tokenized input, B=batch, L=seq_len |
| logits | [B, L, V] | Model output, V=vocab_size |
| probs | [B, N] | Choice probabilities, N=num_choices |
| scores | [M] | Per-model scores, M=num_models |

### Pseudo-code

```
# TruthfulQA
1. Load dataset → 817 MC questions
2. For each question:
   - Tokenize choices → [N, L]
   - Get logits → [N, L, V]
   - Compute log-probs → [N]
   - Normalize → MC2 score
3. Return mean(MC2 scores)

# BOLD
1. Load dataset → 23,679 prompts
2. For each prompt:
   - Generate continuation → [B, L]
   - Compute sentiment bias → scalar
3. Return mean(bias scores)

# HaluEval
1. Load dataset → 30,000 samples
2. For each sample:
   - Classify as hallucinated/not → binary
   - Compare with ground truth
3. Return accuracy

# TextAttack
1. Initialize TextFooler attack
2. For each input text:
   - Apply word substitution → perturbed_text
   - Check semantic similarity > 0.8
3. Return attack success rate
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | TruthfulQA integration | Load dataset, implement MC2 scoring |
| L-E2-2 | BOLD integration | Load dataset, compute sentiment bias |
| L-E2-3 | HaluEval integration | Load dataset, binary classification |
| L-E2-4 | TextAttack integration | Initialize attack, perturbation pipeline |

---

## E4: Stress Testing [Complexity: 11, Budget: 2]

### API Signatures

```python
def apply_stress_perturbations(
    evaluators: Dict[str, Any],
    perturber: TextAttackEvaluator,
    sample_size: int = 1000
) -> Dict[str, List[str]]:
    """
    Apply TextAttack perturbations to benchmark inputs.
    
    Args:
        evaluators: Dict of benchmark evaluators
        perturber: TextAttackEvaluator instance
        sample_size: Number of samples to perturb per benchmark
    
    Returns:
        Dict[benchmark_name, List[perturbed_texts]]
    """
    pass


def evaluate_stressed_models(
    models: Dict[str, Tuple[PreTrainedModel, PreTrainedTokenizer]],
    evaluators: Dict[str, Any],
    perturbed_inputs: Dict[str, List[str]]
) -> Dict[str, Dict[str, float]]:
    """
    Re-evaluate all models on perturbed inputs.
    
    Args:
        models: Dict[model_name, (model, tokenizer)]
        evaluators: Dict[benchmark_name, evaluator]
        perturbed_inputs: Dict[benchmark_name, perturbed_texts]
    
    Returns:
        Dict[model_name, Dict[dimension, stressed_score]]
        stressed_score shape: [M] for M models
    """
    pass
```

### Pseudo-code

```
# apply_stress_perturbations
1. For each benchmark (TruthfulQA, BOLD, HaluEval):
   - Sample N inputs from dataset
   - Apply TextFooler → perturbed_inputs
   - Verify semantic similarity > 0.8
   - Cache perturbed inputs
2. Return perturbed_inputs dict

# evaluate_stressed_models
1. For each model:
   - For each benchmark:
     - Load perturbed inputs from cache
     - Run evaluation on perturbed data
     - Record stressed_score
2. Compute stressed rankings per dimension
3. Return stressed_scores dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | Perturbation application | Apply TextFooler to all benchmark inputs |
| L-E4-2 | Stressed evaluation | Re-evaluate models on perturbed data |

---

## E5: Statistical Analysis [Complexity: 10, Budget: 2]

### API Signatures

```python
class RankCorrelationAnalyzer:
    """Analyzer for rank correlation and dimensional separability."""
    
    def __init__(self, dimensions: List[str]):
        """
        Initialize analyzer.
        dimensions: ['truthfulness', 'fairness', 'hallucination', 'robustness']
        """
        pass
    
    def compute_rankings(
        self,
        scores: Dict[str, Dict[str, float]]
    ) -> Dict[str, List[int]]:
        """
        Convert scores to rankings per dimension.
        
        Args:
            scores: Dict[model_name, Dict[dimension, score]]
        
        Returns:
            Dict[dimension, List[rank]] where rank ∈ [1, M]
            rankings shape: [D, M] for D dimensions, M models
        """
        pass
    
    def compute_kendall_tau(
        self,
        baseline_ranks: Dict[str, List[int]],
        stressed_ranks: Dict[str, List[int]]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Compute Kendall's τ correlation per dimension.
        
        Args:
            baseline_ranks: Dict[dimension, ranks]
            stressed_ranks: Dict[dimension, ranks]
        
        Returns:
            Dict[dimension, (tau, p_value)]
            tau: [-1, 1], p_value: [0, 1]
        """
        pass
    
    def compute_asymmetry(
        self,
        tau_values: Dict[str, Tuple[float, float]]
    ) -> Tuple[Dict[Tuple[str, str], float], float]:
        """
        Compute pairwise asymmetry and variance.
        
        Args:
            tau_values: Dict[dimension, (tau, p_value)]
        
        Returns:
            (asymmetry_matrix, delta_tau_variance)
            asymmetry_matrix: Dict[(dim_i, dim_j), |Δτ_i - Δτ_j|]
            delta_tau_variance: float
        """
        pass
    
    def validate_gate(
        self,
        asymmetry_matrix: Dict[Tuple[str, str], float],
        variance: float,
        tau_values: Dict[str, Tuple[float, float]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate hypothesis gate criteria.
        
        Args:
            asymmetry_matrix: Pairwise asymmetry values
            variance: Δτ variance
            tau_values: Kendall's τ per dimension
        
        Returns:
            (gate_satisfied, gate_details)
            gate_satisfied: bool
            gate_details: Dict with primary/secondary checks
        """
        pass
```

### Pseudo-code

```
# compute_rankings
1. For each dimension:
   - Extract scores for all models → [M]
   - Rank descending (1=best) → [M]
2. Return rankings dict

# compute_kendall_tau
1. Import scipy.stats.kendalltau
2. For each dimension:
   - tau, p_value = kendalltau(baseline_ranks[dim], stressed_ranks[dim])
3. Return tau_values dict

# compute_asymmetry
1. Compute Δτ per dimension:
   - Δτ_i = |τ_stressed_i - τ_baseline_i|
2. Compute pairwise asymmetry:
   - For all (dim_i, dim_j) pairs:
     - asymmetry[i,j] = |Δτ_i - Δτ_j|
3. Compute variance(Δτ)
4. Return (asymmetry_matrix, variance)

# validate_gate
1. Primary check:
   - Count pairs where (|Δτ| ≥ 0.2 AND p < 0.01)
   - primary_pass = (count ≥ 2)
2. Secondary check:
   - secondary_pass = (variance > 0.02)
3. gate_satisfied = primary_pass AND secondary_pass
4. Return (gate_satisfied, details)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | Rank correlation | Kendall's τ computation and asymmetry analysis |
| L-E5-2 | Gate validation | Validate primary/secondary criteria, compute p-values |

---

## Integration Notes

**Data Flow:**
1. E2 evaluators → baseline_scores
2. E4 perturbations → stressed_scores  
3. E5 analysis → tau_values, asymmetry, gate_result

**Dependencies:**
- E4 depends on E2 (needs evaluators and perturber)
- E5 depends on E2 + E4 (needs both baseline and stressed scores)

**Error Handling:**
- Dataset download failures → Retry 3x with 15s delay
- Model OOM → Reduce batch size, retry
- Perturbation failures → Skip sample, log warning

---

**Document Status**: Complete  
**Next Phase**: Phase 4 (Implementation)  
**Total Subtasks**: 8/8 allocated
