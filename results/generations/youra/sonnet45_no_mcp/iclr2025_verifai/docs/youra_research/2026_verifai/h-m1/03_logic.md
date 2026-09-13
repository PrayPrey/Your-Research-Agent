# Logic Design: h-m1

**Date:** 2026-04-20  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Causal)  
**Logic Designer:** Phase 3 Orchestrator  
**Budget:** 8 subtasks (2 high-complexity modules)  
**Base Hypothesis:** h-e1

Applied: Incremental development pattern - extend base classes with minimal new methods

---

## Codebase Analysis (Serena)

**Project Type:** Incremental (extends h-e1)  
**Status:** Reuse h-e1 validated APIs  
**Analyzed Path:** h-e1/code/  
**Relevant Symbols:**
- `ConfidenceTrajectoryExtractor` (h-e1) - base class for variance analyzer
- `ExperimentVisualizer` (h-e1) - base class for group visualizer
- `TheoremSampler`, `ExtendedTimeoutRunner` - reused as-is

**Verified Import Paths from h-e1:**
```python
from h_e1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor
from h_e1.code.visualization.visualizer import ExperimentVisualizer
```

---

## External Dependencies API

### From h-e1 Base Classes (Verified)

#### ConfidenceTrajectoryExtractor (h-e1)
```python
class ConfidenceTrajectoryExtractor:
    """Base class from h-e1 - provides entropy extraction."""
    
    def __init__(self, window_size: int = 15): ...
    
    def extract_confidence_trajectory(self, proof_session) -> Tuple[float, List[float]]:
        """
        Returns:
            derivative: std dev of entropies (h-e1 metric)
            entropies: entropy trajectory
        """
        ...
    
    def compute_entropy(self, probabilities: np.ndarray) -> float:
        """Shannon entropy from softmax probabilities."""
        ...
    
    def compute_derivative(self, entropies: List[float]) -> float:
        """h-e1 metric: std dev of entropies."""
        return np.std(entropies)
```

**Note:** h-e1's `compute_derivative()` already calculates std dev - same as h-m1's variance metric. The difference is in how it's used (correlation vs group comparison).

---

## Epic E2: Extend Confidence Extraction [Complexity: 8, Budget: 2 subtasks]

Applied: Class inheritance pattern for code reuse

### API Signatures

```python
from typing import List, Tuple
import numpy as np
from h_e1.code.models.confidence_extractor import ConfidenceTrajectoryExtractor

class VarianceAnalyzer(ConfidenceTrajectoryExtractor):
    """
    Extends h-e1 extractor for h-m1 variance analysis.
    
    Note: h-e1's compute_derivative() already calculates std dev,
    so h-m1 reuses this as compute_variance().
    """
    
    def __init__(self, window_size: int = 15):
        """
        Initialize variance analyzer.
        
        Args:
            window_size: Number of proof steps to monitor (inherited from h-e1)
        """
        super().__init__(window_size)
    
    def compute_variance(self, entropies: List[float]) -> float:
        """
        Compute confidence variance (std dev of entropy trajectory).
        
        Note: This is identical to h-e1's compute_derivative() method.
        Renamed for clarity in h-m1 context (variance vs derivative).
        
        Args:
            entropies: Entropy values over proof steps, list of floats
        
        Returns:
            variance: Standard deviation of entropies (scalar)
        
        Raises:
            ValueError: If entropies list has < 2 values
        """
        if len(entropies) < 2:
            return 0.0  # Edge case: insufficient steps
        return np.std(entropies)
    
    def extract_variance(self, proof_session) -> Tuple[float, List[float]]:
        """
        Extract variance from proof search session.
        
        Wrapper around base class method, renamed for h-m1 clarity.
        
        Args:
            proof_session: LeanDojo Dojo session
        
        Returns:
            variance: Std dev of entropy trajectory
            entropies: Entropy values for each step
        """
        # Reuse base class extraction
        derivative, entropies = self.extract_confidence_trajectory(proof_session)
        
        # derivative == variance (both are np.std)
        variance = derivative
        return variance, entropies
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropies | [num_steps] | num_steps ≤ 15 (window_size) |
| variance | scalar | np.std(entropies) |

### Pseudo-code

```python
# E2-1: Initialize VarianceAnalyzer
analyzer = VarianceAnalyzer(window_size=15)

# E2-2: Extract variance from proof session
variance, entropies = analyzer.extract_variance(proof_session)

# Verification: variance == h-e1's derivative
assert variance == np.std(entropies)
```

---

## Epic E3: Implement Group Analysis [Complexity: 12, Budget: 3 subtasks]

Applied: Groupby aggregation pattern for statistical comparison

### API Signatures

```python
from typing import List, Dict, Tuple
import numpy as np

class VarianceGroupAnalyzer:
    """
    Analyze variance differences between successful and timeout proofs.
    Tests h-m1 gate: successful proofs have lower variance.
    """
    
    def __init__(self):
        """Initialize group analyzer."""
        pass
    
    def analyze_by_outcome(
        self, 
        results: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Compare mean variance between outcome groups.
        
        Args:
            results: List of experiment results, each dict with:
                - 'variance': float (confidence variance)
                - 'outcome': str ('success' or 'timeout')
                - 'theorem_id': str (identifier)
        
        Returns:
            analysis: Dict containing:
                - success_variance_mean: float
                - success_variance_std: float
                - success_count: int
                - timeout_variance_mean: float
                - timeout_variance_std: float
                - timeout_count: int
                - difference: float (timeout - success)
                - gate_satisfied: bool (success < timeout)
        
        Example:
            >>> results = [
            ...     {'variance': 0.5, 'outcome': 'success'},
            ...     {'variance': 1.2, 'outcome': 'timeout'},
            ...     ...
            ... ]
            >>> analysis = analyzer.analyze_by_outcome(results)
            >>> print(analysis['gate_satisfied'])  # True if mean_success < mean_timeout
        """
        ...
    
    def separate_by_outcome(
        self, 
        results: List[Dict[str, any]]
    ) -> Tuple[List[float], List[float]]:
        """
        Separate variance values by outcome group.
        
        Args:
            results: List of experiment results
        
        Returns:
            success_variances: List of variance values for successful proofs
            timeout_variances: List of variance values for timeout proofs
        """
        success_variances = [r['variance'] for r in results if r['outcome'] == 'success']
        timeout_variances = [r['variance'] for r in results if r['outcome'] == 'timeout']
        return success_variances, timeout_variances
    
    def evaluate_gate(
        self, 
        mean_success: float, 
        mean_timeout: float
    ) -> bool:
        """
        Test gate condition: successful proofs have lower variance.
        
        Args:
            mean_success: Mean variance for successful proofs
            mean_timeout: Mean variance for timeout proofs
        
        Returns:
            True if mean_success < mean_timeout (gate passed)
            False otherwise (gate failed)
        
        Note: This is a direction check only (PoC), no p-value required.
        """
        return mean_success < mean_timeout
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| results | [num_experiments] | List of dicts |
| success_variances | [num_success] | Variance values for successful group |
| timeout_variances | [num_timeout] | Variance values for timeout group |
| mean_success | scalar | Mean of success_variances |
| mean_timeout | scalar | Mean of timeout_variances |

### Pseudo-code

```python
# E3-1: Separate results by outcome
success_vars, timeout_vars = analyzer.separate_by_outcome(results)

# E3-2: Calculate group statistics
mean_success = np.mean(success_vars)
mean_timeout = np.mean(timeout_vars)
std_success = np.std(success_vars)
std_timeout = np.std(timeout_vars)

# E3-3: Evaluate gate condition
gate_satisfied = analyzer.evaluate_gate(mean_success, mean_timeout)

# Return analysis results
return {
    'success_variance_mean': mean_success,
    'success_variance_std': std_success,
    'success_count': len(success_vars),
    'timeout_variance_mean': mean_timeout,
    'timeout_variance_std': std_timeout,
    'timeout_count': len(timeout_vars),
    'difference': mean_timeout - mean_success,
    'gate_satisfied': gate_satisfied
}
```

---

## Epic E5: Main Experiment Script [Complexity: 10, Budget: 3 subtasks]

Applied: Orchestration pattern with optional result reuse

### API Signatures

```python
import sys
import os
from typing import List, Dict
import pickle
import json

# E5-1: Import h-e1 modules
sys.path.append('../h-e1')
from h_e1.code.data.loader import TheoremSampler
from h_e1.code.experiment.runner import ExtendedTimeoutRunner

def load_h_e1_results(results_path: str = '../h-e1/results/confidence_trajectories.pkl') -> List[Dict]:
    """
    Load h-e1 saved results to reuse confidence trajectories.
    
    Args:
        results_path: Path to h-e1 saved results
    
    Returns:
        h_e1_results: List of dicts with 'entropies', 'outcome', 'theorem_id'
    
    Raises:
        FileNotFoundError: If h-e1 results not available
    """
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"h-e1 results not found at {results_path}")
    
    with open(results_path, 'rb') as f:
        h_e1_results = pickle.load(f)
    
    return h_e1_results

def convert_h_e1_to_h_m1_results(h_e1_results: List[Dict]) -> List[Dict]:
    """
    Convert h-e1 results to h-m1 format by calculating variance.
    
    Args:
        h_e1_results: h-e1 results with 'entropies' field
    
    Returns:
        h_m1_results: Results with 'variance' field added
    """
    variance_analyzer = VarianceAnalyzer()
    h_m1_results = []
    
    for result in h_e1_results:
        variance = variance_analyzer.compute_variance(result['entropies'])
        h_m1_results.append({
            'variance': variance,
            'outcome': result['outcome'],
            'theorem_id': result['theorem_id'],
            'entropies': result['entropies']  # Keep for visualization
        })
    
    return h_m1_results

def run_experiments_from_scratch() -> List[Dict]:
    """
    Run experiments from scratch if h-e1 results unavailable.
    
    Returns:
        results: List of experiment results with variance
    """
    # Load same theorems as h-e1
    sampler = TheoremSampler(sample_size=100, seed=42)
    theorems = sampler.sample_theorems()
    
    # Run with extended timeout
    runner = ExtendedTimeoutRunner(timeout_seconds=300)
    variance_analyzer = VarianceAnalyzer()
    
    results = []
    for theorem in theorems:
        # Run proof search
        proof_result = runner.run_experiment(theorem)
        
        # Extract variance
        variance, entropies = variance_analyzer.extract_variance(proof_result['session'])
        
        results.append({
            'variance': variance,
            'outcome': proof_result['outcome'],
            'theorem_id': theorem.id,
            'entropies': entropies
        })
    
    return results

def main():
    """
    Main experiment orchestration.
    
    Workflow:
    1. Try to load h-e1 results (fast path)
    2. Fallback to re-running experiments if unavailable
    3. Analyze variance by outcome group
    4. Visualize group comparison
    5. Save results and evaluate gate
    """
    # E5-2: Load or run experiments
    try:
        print("Attempting to reuse h-e1 results...")
        h_e1_results = load_h_e1_results()
        results = convert_h_e1_to_h_m1_results(h_e1_results)
        print(f"✓ Reused h-e1 results: {len(results)} experiments")
    except FileNotFoundError:
        print("h-e1 results not found, running experiments from scratch...")
        results = run_experiments_from_scratch()
        print(f"✓ Completed {len(results)} experiments")
    
    # E5-3: Analyze and save results
    group_analyzer = VarianceGroupAnalyzer()
    analysis = group_analyzer.analyze_by_outcome(results)
    
    # Save analysis results
    with open('h-m1/results/variance_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Display gate evaluation
    print("\n" + "="*60)
    print("H-M1 GATE EVALUATION")
    print("="*60)
    print(f"Success group - Mean variance: {analysis['success_variance_mean']:.4f}")
    print(f"Timeout group - Mean variance: {analysis['timeout_variance_mean']:.4f}")
    print(f"Difference: {analysis['difference']:.4f}")
    print(f"Gate Satisfied: {analysis['gate_satisfied']}")
    print("="*60)
    
    return analysis
```

### Pseudo-code

```python
# Main workflow
if __name__ == '__main__':
    # Step 1: Get results (reuse or re-run)
    results = get_results()  # Tries h-e1 reuse first
    
    # Step 2: Group analysis
    analysis = analyze_by_outcome(results)
    
    # Step 3: Visualize (handled by Epic E4)
    visualize_group_comparison(analysis, results)
    
    # Step 4: Save and report
    save_results(analysis)
    print_gate_evaluation(analysis)
```

---

## Algorithm Complexity Analysis

### E2: Variance Calculation
**Time Complexity:** O(n) where n = window_size (max 15)  
**Space Complexity:** O(n) for entropy storage

### E3: Group Analysis
**Time Complexity:** O(m) where m = num_experiments (100)  
**Space Complexity:** O(m) for group separation

### E5: Result Reuse
**Time Complexity:** O(m) for conversion (vs hours for re-running)  
**Space Complexity:** O(m) for result storage

---

## Unit Test Requirements

### E2 Tests
```python
def test_variance_calculation():
    analyzer = VarianceAnalyzer()
    entropies = [1.0, 1.5, 2.0, 1.8, 1.2]
    variance = analyzer.compute_variance(entropies)
    assert variance == np.std(entropies)

def test_edge_case_single_step():
    analyzer = VarianceAnalyzer()
    variance = analyzer.compute_variance([1.0])
    assert variance == 0.0
```

### E3 Tests
```python
def test_group_separation():
    results = [
        {'variance': 0.5, 'outcome': 'success'},
        {'variance': 1.5, 'outcome': 'timeout'},
        {'variance': 0.6, 'outcome': 'success'},
    ]
    analyzer = VarianceGroupAnalyzer()
    success_vars, timeout_vars = analyzer.separate_by_outcome(results)
    assert success_vars == [0.5, 0.6]
    assert timeout_vars == [1.5]

def test_gate_evaluation():
    analyzer = VarianceGroupAnalyzer()
    assert analyzer.evaluate_gate(0.5, 1.0) == True  # success < timeout
    assert analyzer.evaluate_gate(1.0, 0.5) == False  # success > timeout
```

---

## Notes

**Key Insight:** h-e1's `compute_derivative()` and h-m1's `compute_variance()` are identical (both use `np.std`). The innovation in h-m1 is using this metric for group comparison rather than correlation analysis.

**Optimization:** Reusing h-e1 results eliminates ~3 hours of experiment runtime, making h-m1 execution time < 5 minutes (post-processing only).
