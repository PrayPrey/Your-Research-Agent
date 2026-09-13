# Logic Design: h-e1

**Date:** 2026-04-20  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Logic Designer:** Logic Agent  
**Budget:** 6 subtasks (3 high-complexity modules)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - designing new APIs for LeanDojo integration  

**Note:** This is an EXISTENCE experiment with no base hypothesis or existing codebase. All APIs are designed from scratch based on LeanDojo official API patterns.

---

## Knowledge Base Patterns

**Applied:** Standard Python scientific computing pattern (numpy/scipy stack for numerical experiments)

---

## A-3: Confidence Extraction [Complexity: 10, Budget: 1 subtask]

**Applied:** Entropy computation pattern with sliding window monitoring

### API Signatures

```python
from typing import List, Tuple, Optional
import numpy as np
from scipy.stats import entropy

class ConfidenceTrajectoryExtractor:
    """Extract confidence derivatives from LeanDojo proof search trajectories."""
    
    def __init__(self, window_size: int = 15):
        """
        Initialize confidence extractor.
        
        Args:
            window_size: Number of proof steps to monitor for entropy trajectory
        """
        self.window_size = window_size
    
    def extract_confidence_trajectory(
        self, 
        proof_session
    ) -> Tuple[float, List[float]]:
        """
        Extract confidence derivative from proof search session.
        
        Args:
            proof_session: LeanDojo Dojo session with get_tactics() method
        
        Returns:
            confidence_derivative: std dev of entropy trajectory (scalar)
            entropies: entropy values for each step (list of floats, length ≤ window_size)
        """
        ...
    
    def compute_entropy(self, probabilities: np.ndarray) -> float:
        """
        Compute Shannon entropy from probability distribution.
        
        Args:
            probabilities: softmax probabilities, shape [num_tactics]
        
        Returns:
            entropy_value: Shannon entropy (scalar)
        """
        ...
    
    def compute_derivative(self, entropies: List[float]) -> float:
        """
        Compute confidence derivative as std dev of entropy trajectory.
        
        Args:
            entropies: entropy values over time, list of floats
        
        Returns:
            derivative: std dev of entropies (scalar)
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| probabilities | [num_tactics] | Normalized softmax probabilities from LeanDojo |
| entropies | [num_steps] | num_steps ≤ window_size (early termination possible) |
| confidence_derivative | scalar | std dev of entropies |

### Pseudo-code

```
FUNCTION extract_confidence_trajectory(proof_session):
    entropies = []
    
    FOR step_num IN range(window_size):
        # Get tactics with log probabilities from LeanDojo
        tactics_with_logprobs = proof_session.get_tactics()
        
        # Convert log probabilities to normalized softmax
        logprobs = [logprob for (tactic, logprob) in tactics_with_logprobs]
        probs = exp(logprobs)  # shape: [num_tactics]
        probs = probs / sum(probs)  # normalize
        
        # Compute Shannon entropy for current step
        step_entropy = -sum(p * log(p) for p in probs if p > 0)
        entropies.append(step_entropy)
        
        # Early termination if proof completes
        IF proof_session.is_done():
            BREAK
    
    # Compute confidence derivative (std dev)
    confidence_derivative = std_dev(entropies)
    
    RETURN confidence_derivative, entropies
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Entropy trajectory extraction | Implement extract_confidence_trajectory with LeanDojo API integration, entropy computation, and std dev calculation |

---

## A-4: Experiment Execution [Complexity: 12, Budget: 2 subtasks]

**Applied:** Batch processing pattern with timeout enforcement and error handling

### API Signatures

```python
from typing import List, Dict, Any, Optional
import time

class ExtendedTimeoutRunner:
    """Execute proof search experiments with extended 300s timeout and confidence monitoring."""
    
    def __init__(
        self, 
        timeout_seconds: int = 300, 
        confidence_window: int = 15
    ):
        """
        Initialize experiment runner.
        
        Args:
            timeout_seconds: Maximum time per theorem (default 300s)
            confidence_window: Number of steps for confidence extraction
        """
        self.timeout_seconds = timeout_seconds
        self.confidence_window = confidence_window
        self.confidence_extractor = ConfidenceTrajectoryExtractor(confidence_window)
    
    def run_experiment(self, theorem) -> Dict[str, Any]:
        """
        Run single extended-timeout experiment with confidence extraction.
        
        Args:
            theorem: LeanDojo Theorem object
        
        Returns:
            result: {
                'theorem_id': str,
                'confidence_derivative': float,
                'outcome': int (0=success, 1=timeout),
                'execution_time': float (seconds),
                'entropies': List[float],
                'status': str ('success', 'timeout', 'error')
            }
        """
        ...
    
    def run_batch(
        self, 
        theorems: List, 
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch of experiments with progress tracking.
        
        Args:
            theorems: List of LeanDojo Theorem objects, length = num_theorems
            progress_callback: Optional function(current, total) for progress updates
        
        Returns:
            results: List of result dicts, length = num_theorems
        """
        ...
    
    def _enforce_timeout(self, proof_session, timeout: float) -> bool:
        """
        Enforce timeout on proof search session.
        
        Args:
            proof_session: LeanDojo Dojo session
            timeout: timeout in seconds
        
        Returns:
            success: True if proof completed, False if timeout
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| theorems | [num_theorems] | List of Theorem objects (100 for experiment) |
| results | [num_theorems] | List of result dicts |
| entropies | [num_steps] | Per-theorem entropy trajectory, num_steps ≤ 15 |
| confidence_derivative | scalar | Per-theorem confidence metric |

### Pseudo-code

```
FUNCTION run_experiment(theorem):
    result = {
        'theorem_id': theorem.id,
        'confidence_derivative': None,
        'outcome': None,
        'execution_time': None,
        'entropies': [],
        'status': 'running'
    }
    
    start_time = current_time()
    
    TRY:
        # Initialize LeanDojo proof session
        proof_session = Dojo(theorem)
        
        # Extract confidence trajectory during proof search
        confidence_derivative, entropies = confidence_extractor.extract_confidence_trajectory(proof_session)
        
        # Run proof search with timeout enforcement
        success = _enforce_timeout(proof_session, timeout_seconds)
        
        # Record results
        result['confidence_derivative'] = confidence_derivative
        result['entropies'] = entropies
        result['outcome'] = 0 if success else 1
        result['execution_time'] = current_time() - start_time
        result['status'] = 'success' if success else 'timeout'
        
    CATCH Exception as e:
        result['status'] = 'error'
        result['error_message'] = str(e)
        log_warning(f"Theorem {theorem.id} failed: {e}")
    
    RETURN result

FUNCTION run_batch(theorems, progress_callback):
    results = []
    
    FOR i, theorem IN enumerate(theorems):
        result = run_experiment(theorem)
        results.append(result)
        
        IF progress_callback:
            progress_callback(i + 1, len(theorems))
    
    RETURN results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Single experiment runner | Implement run_experiment with LeanDojo Dojo integration, confidence extraction, timeout enforcement, and error handling |
| L-4-2 | Batch execution | Implement run_batch with progress tracking, individual failure handling, and results aggregation |

---

## A-7: Integration & Execution [Complexity: 14, Budget: 3 subtasks]

**Applied:** Scientific experiment orchestration pattern with data pipeline and reproducibility

### API Signatures

```python
from typing import Tuple
import numpy as np
import json
import os

class ExperimentOrchestrator:
    """Orchestrate full experiment pipeline: sampling → execution → analysis → visualization."""
    
    def __init__(self, config: 'ExperimentConfig'):
        """
        Initialize orchestrator with experiment configuration.
        
        Args:
            config: ExperimentConfig object with all parameters
        """
        self.config = config
        self.sampler = None
        self.runner = None
        self.analyzer = None
        self.visualizer = None
    
    def run_full_experiment(self) -> Dict[str, Any]:
        """
        Execute full experiment pipeline.
        
        Returns:
            summary: {
                'correlation_pearson': {'r': float, 'p_value': float},
                'correlation_spearman': {'rho': float, 'p_value': float},
                'auc': float,
                'gate_result': str ('PASS' or 'FAIL'),
                'sample_size': int,
                'timeout_budget_seconds': int
            }
        """
        ...
    
    def save_results(
        self, 
        results: List[Dict[str, Any]], 
        metrics: Dict[str, Any]
    ) -> None:
        """
        Save experiment results to files.
        
        Args:
            results: List of per-theorem results, length = num_theorems
            metrics: Correlation metrics and gate evaluation
        """
        ...

def main():
    """Main entry point for experiment execution."""
    # Setup
    config = ExperimentConfig()
    set_random_seed(config.random_seed)
    check_gpu_availability()
    
    # Run experiment
    orchestrator = ExperimentOrchestrator(config)
    summary = orchestrator.run_full_experiment()
    
    # Report gate result
    print(f"Gate Result: {summary['gate_result']}")
    print(f"Pearson r = {summary['correlation_pearson']['r']:.3f}")
    print(f"Spearman ρ = {summary['correlation_spearman']['rho']:.3f}")
```

### Data Flow Shapes

| Stage | Input | Output | Note |
|-------|-------|--------|------|
| Sampling | benchmark | [100] theorems | Random sample with seed=42 |
| Execution | [100] theorems | [100] results | Each result has confidence_derivative, outcome |
| Analysis | [100] derivatives, [100] outcomes | metrics dict | Pearson r, Spearman ρ, p-values, AUC |
| Visualization | [100] derivatives, [100] outcomes | 5 PNG files | Saved to figures/ directory |

### Pseudo-code

```
FUNCTION run_full_experiment():
    print("Starting h-e1 experiment...")
    
    # Stage 1: Sample theorems
    print("Stage 1: Sampling 100 theorems from LeanDojo Benchmark...")
    sampler = TheoremSampler(
        repo_url=config.repo_url,
        commit_hash=config.commit_hash,
        sample_size=config.sample_size,
        seed=config.random_seed
    )
    benchmark = sampler.load_benchmark()
    theorems = sampler.sample_theorems(benchmark)  # [100]
    print(f"Sampled {len(theorems)} theorems")
    
    # Stage 2: Run experiments with confidence extraction
    print("Stage 2: Running extended-timeout experiments (300s per theorem)...")
    runner = ExtendedTimeoutRunner(
        timeout_seconds=config.timeout_seconds,
        confidence_window=config.confidence_window
    )
    results = runner.run_batch(theorems, progress_callback=print_progress)  # [100]
    print(f"Completed {len(results)} experiments")
    
    # Stage 3: Extract data for analysis
    confidence_derivatives = [r['confidence_derivative'] for r in results]  # [100]
    outcomes = [r['outcome'] for r in results]  # [100]
    
    # Stage 4: Compute correlations
    print("Stage 3: Computing correlations...")
    analyzer = CorrelationAnalyzer()
    r, p_r = analyzer.compute_pearson(confidence_derivatives, outcomes)
    rho, p_rho = analyzer.compute_spearman(confidence_derivatives, outcomes)
    auc = analyzer.compute_auc(confidence_derivatives, outcomes)
    gate_result = analyzer.evaluate_gate(r, rho)
    
    print(f"Pearson r = {r:.3f} (p = {p_r:.4f})")
    print(f"Spearman ρ = {rho:.3f} (p = {p_rho:.4f})")
    print(f"AUC = {auc:.3f}")
    
    # Stage 5: Generate visualizations
    print("Stage 4: Generating visualizations...")
    visualizer = ExperimentVisualizer(output_dir=config.figures_dir)
    visualizer.plot_gate_metrics(r, rho, target=0.3)  # MANDATORY
    visualizer.plot_scatter(confidence_derivatives, outcomes)
    visualizer.plot_distributions(confidence_derivatives, outcomes)
    visualizer.plot_trajectory_examples(
        [r['entropies'] for r in results[:10]], 
        outcomes[:10]
    )
    visualizer.plot_roc_curve(confidence_derivatives, outcomes)
    print("All figures saved to figures/")
    
    # Stage 6: Save results
    print("Stage 5: Saving results...")
    metrics = {
        'correlation_pearson': {'r': r, 'p_value': p_r},
        'correlation_spearman': {'rho': rho, 'p_value': p_rho},
        'auc': auc,
        'gate_result': 'PASS' if gate_result else 'FAIL',
        'sample_size': config.sample_size,
        'timeout_budget_seconds': config.timeout_seconds
    }
    save_results(results, metrics)
    print("Results saved to results/")
    
    # Stage 7: Gate evaluation
    print(f"\nGate Evaluation: {metrics['gate_result']}")
    IF NOT gate_result:
        print("WARNING: Gate condition FAILED (r ≤ 0.3 AND ρ ≤ 0.3)")
        print("Hypothesis h-e1 REJECTED - consider alternative approaches")
    
    RETURN metrics
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Pipeline orchestration | Implement run_full_experiment with 7-stage data flow (sampling → execution → analysis → visualization → saving → gate evaluation) |
| L-7-2 | Results persistence | Implement save_results with CSV export (results_raw.csv), JSON metrics (metrics_summary.json), and metadata logging |
| L-7-3 | Gate evaluation | Implement gate condition check (r > 0.3 OR ρ > 0.3), status reporting, and failure warnings |

---

## Supporting Modules (Low Complexity - No Subtasks Allocated)

### TheoremSampler (A-2: Data Loading)

```python
class TheoremSampler:
    """Sample theorems from LeanDojo Benchmark."""
    
    def __init__(self, repo_url: str, commit_hash: str, sample_size: int = 100, seed: int = 42):
        """Initialize sampler with dataset parameters."""
        ...
    
    def load_benchmark(self) -> List:
        """Load LeanDojo Benchmark dataset. Returns: list of Theorem objects"""
        ...
    
    def sample_theorems(self, benchmark: List) -> List:
        """Random sample from benchmark. Input: [N] theorems → Output: [sample_size] theorems"""
        ...
```

### CorrelationAnalyzer (A-5: Correlation Analysis)

```python
class CorrelationAnalyzer:
    """Compute correlation metrics and gate evaluation."""
    
    def compute_pearson(self, derivatives: np.ndarray, outcomes: np.ndarray) -> Tuple[float, float]:
        """Pearson correlation. Input: [N], [N] → Output: (r, p_value)"""
        ...
    
    def compute_spearman(self, derivatives: np.ndarray, outcomes: np.ndarray) -> Tuple[float, float]:
        """Spearman correlation. Input: [N], [N] → Output: (rho, p_value)"""
        ...
    
    def compute_auc(self, derivatives: np.ndarray, outcomes: np.ndarray) -> float:
        """ROC-AUC score. Input: [N], [N] → Output: scalar"""
        ...
    
    def evaluate_gate(self, r: float, rho: float, threshold: float = 0.3) -> bool:
        """Gate condition. Returns: True if r > 0.3 OR rho > 0.3"""
        ...
```

### ExperimentVisualizer (A-6: Visualization)

```python
class ExperimentVisualizer:
    """Generate experiment figures."""
    
    def __init__(self, output_dir: str):
        """Initialize with output directory for figures."""
        ...
    
    def plot_gate_metrics(self, r: float, rho: float, target: float = 0.3) -> None:
        """MANDATORY gate metrics bar chart. Saves: gate_metrics.png"""
        ...
    
    def plot_scatter(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None:
        """Scatter plot. Input: [N], [N]. Saves: scatter_plot.png"""
        ...
    
    def plot_distributions(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None:
        """Distribution comparison. Input: [N], [N]. Saves: distributions.png"""
        ...
    
    def plot_trajectory_examples(self, trajectories: List[List[float]], outcomes: List[int]) -> None:
        """Entropy trajectories. Input: M × [num_steps], [M]. Saves: trajectory_examples.png"""
        ...
    
    def plot_roc_curve(self, derivatives: np.ndarray, outcomes: np.ndarray) -> None:
        """ROC curve. Input: [N], [N]. Saves: roc_curve.png"""
        ...
```

---

## Budget Summary

**Total Budget:** 6 subtasks  
**Allocated:**
- A-3 (Confidence Extraction): 1 subtask
- A-4 (Experiment Execution): 2 subtasks
- A-7 (Integration & Execution): 3 subtasks

**Total Used:** 6/6 subtasks

---

## Implementation Notes

### LeanDojo API Integration

```python
# Key LeanDojo API patterns verified from official repository

from lean_dojo import LeanGitRepo, Theorem, Dojo

# 1. Load benchmark
repo = LeanGitRepo("https://github.com/leanprover-community/mathlib", commit_hash)
theorems = repo.get_traced_theorems()

# 2. Initialize proof session
dojo = Dojo(theorem)

# 3. Get tactics with confidence scores
tactics_with_logprobs = dojo.get_tactics()  # Returns: [(tactic_str, logprob), ...]

# 4. Extract probabilities for entropy
import numpy as np
logprobs = np.array([logprob for _, logprob in tactics_with_logprobs])
probs = np.exp(logprobs)
probs = probs / probs.sum()  # Normalize to valid probability distribution

# 5. Check completion status
is_complete = dojo.is_done()
```

### Edge Cases

1. **Early proof termination:** If proof completes before 15 steps, use available entropy values (handle variable-length trajectories)
2. **Empty tactics list:** If get_tactics() returns empty list, skip theorem and log warning
3. **Timeout enforcement:** Use threading or asyncio to enforce 300s hard limit
4. **Memory management:** Clear Dojo session after each theorem to prevent memory leaks

### Reproducibility

```python
# Set all random seeds
import numpy as np
import random

def set_random_seed(seed: int = 42):
    np.random.seed(seed)
    random.seed(seed)
    # Note: LeanDojo proof search may have non-deterministic components
```

---

## Validation Checklist

- [ ] All API signatures include type hints
- [ ] Tensor/array shapes documented in comments and tables
- [ ] Pseudo-code provided for complex algorithms (A-3, A-4, A-7)
- [ ] Budget exactly matches allocation (6/6 subtasks)
- [ ] LeanDojo API integration patterns verified from official repository
- [ ] Edge cases documented (early termination, empty tactics, timeout)
- [ ] EXISTENCE constraints followed (no training, no ablation, minimal design)
- [ ] Codebase Analysis section included (green-field status noted)

---

*Logic design optimized for EXISTENCE (PoC) tier - minimal but complete API specifications*  
*Next Phase: Phase 4 - Implementation (Coder will match these signatures exactly)*
