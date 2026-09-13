# Logic Design: h-m2

**Date:** 2026-04-20  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Causal)  
**Logic Designer:** Phase 3 Orchestrator  
**Budget:** 8 subtasks (2 high-complexity modules)  
**Base Hypothesis:** h-m1

Applied: Incremental development pattern - extend h-m1 with divergence analysis layer

---

## Codebase Analysis (Serena)

**Project Type:** Incremental (extends h-m1)  
**Status:** Reuse h-m1 validated APIs  
**Analyzed Path:** h-m1/code/  
**Relevant Symbols:**
- `VarianceAnalyzer` (h-m1) - base class for variance calculation
- `ExtendedTimeoutRunner` (h-m1) - extend with search tree tracking
- `VarianceGroupAnalyzer` (h-m1) - pattern for subgroup analysis
- `TheoremSampler` (h-m1) - reused as-is

**Verified Import Paths from h-m1:**
```python
from h_m1.code.analysis.variance_analyzer import VarianceAnalyzer
from h_m1.code.experiment.runner import ExtendedTimeoutRunner
from h_m1.code.data.loader import TheoremSampler
```

---

## External Dependencies API

### From h-m1 Base Classes (Verified)

#### VarianceAnalyzer (h-m1)
```python
class VarianceAnalyzer:
    """Base class from h-m1 - provides variance calculation."""
    
    def __init__(self, window_size: int = 15): ...
    
    def compute_variance(self, entropies: List[float]) -> float:
        """
        Returns:
            variance: std dev of entropies (h-m1 validated metric)
        """
        ...
    
    def extract_variance(self, proof_session) -> Tuple[float, List[float]]:
        """
        Returns:
            variance: confidence variance
            entropies: entropy trajectory
        """
        ...
```

**Note:** h-m2 reuses h-m1's variance calculation completely - same metric, same implementation.

#### ExtendedTimeoutRunner (h-m1)
```python
class ExtendedTimeoutRunner:
    """Base class from h-m1 - runs proof search with extended timeout."""
    
    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15): ...
    
    def run_experiment(self, theorem) -> dict:
        """
        Returns:
            result: {
                'outcome': str ('success' or 'timeout'),
                'session': proof session,
                'theorem_id': str
            }
        """
        ...
```

**Note:** h-m2 extends this to add search tree tracking.

---

## Epic E2: Extend Proof Runner with Search Tree Tracking [Complexity: 13, Budget: 3 subtasks]

Applied: Class inheritance pattern for extending h-m1 runner

### API Signatures

```python
from typing import List, Tuple, Dict
import numpy as np
from h_m1.code.experiment.runner import ExtendedTimeoutRunner

class ExtendedTimeoutRunnerWithTree(ExtendedTimeoutRunner):
    """
    Extends h-m1 runner to capture search tree for divergence analysis.
    
    Adds search tree tracking without modifying core proof search logic.
    """
    
    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15):
        """
        Initialize runner with tree tracking.
        
        Args:
            timeout_seconds: Proof search timeout (inherited from h-m1)
            confidence_window: Number of steps to monitor (inherited from h-m1)
        """
        super().__init__(timeout_seconds, confidence_window)
        self.enable_tree_tracking = True
    
    def run_experiment(self, theorem) -> Dict:
        """
        Run experiment with search tree tracking.
        
        Extends h-m1 run_experiment() to capture:
        - Search tree structure (LeanDojo API)
        - Proof state sequences (for collision detection)
        
        Args:
            theorem: LeanDojo theorem object
        
        Returns:
            result: h-m1 result dict extended with:
                - 'search_tree': LeanDojo search tree structure
                - 'proof_states': List of visited proof states
                - 'state_sequence_length': int
        
        Example:
            >>> runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)
            >>> result = runner.run_experiment(theorem)
            >>> print(result.keys())
            ['outcome', 'session', 'theorem_id', 'search_tree', 'proof_states', ...]
        """
        # Call h-m1 base method
        base_result = super().run_experiment(theorem)
        
        # Add tree tracking
        search_tree, proof_states = self._track_search_tree(base_result['session'])
        
        # Extend result
        base_result['search_tree'] = search_tree
        base_result['proof_states'] = proof_states
        base_result['state_sequence_length'] = len(proof_states)
        
        return base_result
    
    def _track_search_tree(self, proof_session) -> Tuple:
        """
        Capture search tree and state sequence from proof session.
        
        Args:
            proof_session: LeanDojo Dojo session
        
        Returns:
            search_tree: LeanDojo search tree structure (nodes + edges)
            proof_states: List of visited proof states
        
        Implementation:
            Uses LeanDojo's internal search tree API to extract:
            - Tree nodes (proof states explored)
            - Tree edges (tactic applications)
            - Backtrack events (abandoned branches)
        """
        search_tree = proof_session.get_search_tree()
        proof_states = proof_session.get_state_sequence()
        return search_tree, proof_states
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| proof_states | [num_states] | Variable length, depends on search |
| search_tree.nodes | [num_nodes] | Tree nodes explored |
| search_tree.edges | [num_edges] | Tactic applications |

### Pseudo-code

```python
# E2-1: Initialize runner with tree tracking
runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)

# E2-2: Run experiment (extends h-m1)
result = runner.run_experiment(theorem)

# E2-3: Verify tree tracking
assert 'search_tree' in result
assert 'proof_states' in result
assert len(result['proof_states']) > 0
```

---

## Epic E3: Implement Divergence Classifier [Complexity: 14, Budget: 3 subtasks]

Applied: Symbolic analysis pattern for divergence detection

### API Signatures

```python
from typing import List, Dict, Tuple
import numpy as np

class DivergenceClassifier:
    """
    Classify timeout proofs as divergent vs difficult.
    
    Divergence markers:
    - State hash collisions (cyclic behavior)
    - High backtrack frequency (search instability)
    """
    
    def __init__(self, collision_threshold: int = 2, backtrack_threshold: int = 5):
        """
        Initialize divergence classifier.
        
        Args:
            collision_threshold: Min collisions for divergence classification
            backtrack_threshold: Min backtracks for divergence classification
        
        Rationale:
            - collision_threshold=2: At least 2 repeated states (cyclic pattern)
            - backtrack_threshold=5: Significant search instability
            - Thresholds are PoC-level heuristics, validated empirically
        """
        self.collision_threshold = collision_threshold
        self.backtrack_threshold = backtrack_threshold
    
    def classify_timeout(
        self, 
        proof_states: List, 
        search_tree
    ) -> Tuple[bool, Dict[str, int]]:
        """
        Classify single timeout as divergent or difficult.
        
        Args:
            proof_states: List of visited proof states from runner
            search_tree: LeanDojo search tree structure from runner
        
        Returns:
            is_divergent: True if divergent, False if difficult
            markers: {
                'state_collisions': int (number of hash collisions),
                'backtrack_frequency': int (number of backtracks)
            }
        
        Classification Logic:
            is_divergent = (collisions > threshold) OR (backtracks > threshold)
            
            Divergent: Cyclic patterns, repeated states, high instability
            Difficult: Valid exploration, challenging but not cyclic
        
        Example:
            >>> classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)
            >>> is_divergent, markers = classifier.classify_timeout(states, tree)
            >>> if is_divergent:
            ...     print(f"Divergent: {markers['state_collisions']} collisions")
        """
        # Detect state collisions
        collisions = self._detect_state_collisions(proof_states)
        
        # Count backtracks
        backtracks = self._count_backtracks(search_tree)
        
        # Classification rule
        is_divergent = (
            collisions > self.collision_threshold or
            backtracks > self.backtrack_threshold
        )
        
        markers = {
            'state_collisions': collisions,
            'backtrack_frequency': backtracks
        }
        
        return is_divergent, markers
    
    def _detect_state_collisions(self, proof_states: List) -> int:
        """
        Count hash collisions (repeated states) in proof search.
        
        Args:
            proof_states: List of proof states explored
        
        Returns:
            collisions: Number of hash collisions (cyclic behavior indicator)
        
        Algorithm:
            1. Hash each proof state (str representation)
            2. Count unique hashes
            3. Collisions = total_states - unique_hashes
        
        Example:
            states = [s1, s2, s1, s3, s2]  # s1, s2 repeated
            hashes = [h1, h2, h1, h3, h2]
            unique = {h1, h2, h3} (3 unique)
            collisions = 5 - 3 = 2
        """
        # Hash-based collision detection
        state_hashes = [hash(str(state)) for state in proof_states]
        unique_hashes = set(state_hashes)
        collisions = len(state_hashes) - len(unique_hashes)
        
        return collisions
    
    def _count_backtracks(self, search_tree) -> int:
        """
        Count backtrack events from search tree.
        
        Args:
            search_tree: LeanDojo search tree structure
        
        Returns:
            backtrack_count: Number of abandoned branches
        
        Algorithm:
            1. Traverse search tree nodes
            2. For each branching point (node with multiple children):
                - Count abandoned children (not on success path)
            3. Sum abandoned branches = backtrack events
        
        Rationale:
            High backtrack frequency indicates search instability,
            exploring many paths but abandoning most (divergence marker)
        """
        backtrack_count = 0
        
        for node in search_tree.nodes:
            if len(node.children) > 1:
                # Branching point - check for abandoned branches
                abandoned = sum(1 for child in node.children if child.is_abandoned)
                backtrack_count += abandoned
        
        return backtrack_count
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| proof_states | [num_states] | Variable length |
| state_hashes | [num_states] | Hash for each state |
| unique_hashes | {num_unique} | Set of unique hashes |
| collisions | scalar | len(hashes) - len(unique) |
| backtracks | scalar | Count of abandoned branches |

### Pseudo-code

```python
# E3-1: Initialize classifier
classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)

# E3-2: Classify timeout
is_divergent, markers = classifier.classify_timeout(proof_states, search_tree)

# E3-3: Interpret markers
if is_divergent:
    print(f"Divergent: {markers['state_collisions']} collisions, "
          f"{markers['backtrack_frequency']} backtracks")
else:
    print(f"Difficult: {markers['state_collisions']} collisions, "
          f"{markers['backtrack_frequency']} backtracks")
```

---

## Epic E4: Implement Timeout Subgroup Analysis [Complexity: 10, Budget: 2 subtasks]

Applied: Subgroup comparison pattern (extends h-m1's group analysis)

### API Signatures

```python
from typing import List, Dict
import numpy as np

class TimeoutSubgroupAnalyzer:
    """
    Analyze variance differences within timeout group.
    
    Extends h-m1's VarianceGroupAnalyzer pattern for h-m2's
    divergent vs difficult comparison.
    """
    
    def __init__(self):
        """Initialize subgroup analyzer."""
        pass
    
    def analyze_variance_by_divergence(
        self, 
        timeout_results: List[Dict]
    ) -> Dict[str, any]:
        """
        Subdivide timeout group and compare variance.
        
        Args:
            timeout_results: List of timeout experiments, each dict with:
                - 'variance': float (confidence variance from h-m1)
                - 'is_divergent': bool (divergence classification)
                - 'divergence_markers': dict (collisions, backtracks)
                - 'theorem_id': str
        
        Returns:
            analysis: {
                'divergent': {
                    'count': int,
                    'mean_variance': float,
                    'std_variance': float,
                    'variance_values': List[float]
                },
                'difficult': {
                    'count': int,
                    'mean_variance': float,
                    'std_variance': float,
                    'variance_values': List[float]
                },
                'difference': float (divergent_mean - difficult_mean),
                'gate_satisfied': bool (divergent_mean > difficult_mean)
            }
        
        Example:
            >>> timeout_results = [
            ...     {'variance': 0.35, 'is_divergent': True},
            ...     {'variance': 0.20, 'is_divergent': False},
            ...     ...
            ... ]
            >>> analysis = analyzer.analyze_variance_by_divergence(timeout_results)
            >>> print(analysis['gate_satisfied'])  # True if divergent > difficult
        """
        # Separate by divergence classification
        divergent_vars, difficult_vars = self._separate_by_divergence(timeout_results)
        
        # Calculate statistics
        divergent_stats = {
            'count': len(divergent_vars),
            'mean_variance': np.mean(divergent_vars) if divergent_vars else 0.0,
            'std_variance': np.std(divergent_vars) if divergent_vars else 0.0,
            'variance_values': divergent_vars
        }
        
        difficult_stats = {
            'count': len(difficult_vars),
            'mean_variance': np.mean(difficult_vars) if difficult_vars else 0.0,
            'std_variance': np.std(difficult_vars) if difficult_vars else 0.0,
            'variance_values': difficult_vars
        }
        
        # Gate evaluation
        difference = divergent_stats['mean_variance'] - difficult_stats['mean_variance']
        gate_satisfied = self.evaluate_gate(
            divergent_stats['mean_variance'],
            difficult_stats['mean_variance']
        )
        
        return {
            'divergent': divergent_stats,
            'difficult': difficult_stats,
            'difference': difference,
            'gate_satisfied': gate_satisfied
        }
    
    def _separate_by_divergence(
        self, 
        timeout_results: List[Dict]
    ) -> Tuple[List[float], List[float]]:
        """
        Separate variance values by divergence classification.
        
        Args:
            timeout_results: List of timeout experiment results
        
        Returns:
            divergent_variances: Variance values for divergent timeouts
            difficult_variances: Variance values for difficult timeouts
        """
        divergent_variances = [
            r['variance'] for r in timeout_results if r['is_divergent']
        ]
        difficult_variances = [
            r['variance'] for r in timeout_results if not r['is_divergent']
        ]
        return divergent_variances, difficult_variances
    
    def evaluate_gate(
        self, 
        mean_divergent: float, 
        mean_difficult: float
    ) -> bool:
        """
        Test gate condition: divergent timeouts have higher variance.
        
        Args:
            mean_divergent: Mean variance for divergent timeouts
            mean_difficult: Mean variance for difficult timeouts
        
        Returns:
            True if mean_divergent > mean_difficult (gate passed)
            False otherwise (gate failed)
        
        Note: This is a direction check only (PoC), no p-value required.
        
        Interpretation:
            - Gate PASS: Confidence instability specifically signals divergence
            - Gate FAIL: Confidence variance reflects general difficulty, not divergence
        """
        return mean_divergent > mean_difficult
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| timeout_results | [num_timeouts] | List of dicts |
| divergent_variances | [num_divergent] | Variance values for divergent group |
| difficult_variances | [num_difficult] | Variance values for difficult group |
| mean_divergent | scalar | Mean of divergent_variances |
| mean_difficult | scalar | Mean of difficult_variances |

### Pseudo-code

```python
# E4-1: Separate timeout group
divergent_vars, difficult_vars = analyzer._separate_by_divergence(timeout_results)

# E4-2: Calculate subgroup statistics
mean_divergent = np.mean(divergent_vars)
mean_difficult = np.mean(difficult_vars)
difference = mean_divergent - mean_difficult

# E4-3: Evaluate gate
gate_satisfied = analyzer.evaluate_gate(mean_divergent, mean_difficult)

# Return analysis
return {
    'divergent': {'count': len(divergent_vars), 'mean_variance': mean_divergent, ...},
    'difficult': {'count': len(difficult_vars), 'mean_variance': mean_difficult, ...},
    'difference': difference,
    'gate_satisfied': gate_satisfied
}
```

---

## Epic E6: Main Experiment Script [Complexity: 11, Budget: 3 subtasks]

Applied: Orchestration pattern with h-m1 reuse optimization

### API Signatures

```python
import sys
import os
from typing import List, Dict
import pickle
import json

# E6-1: Import h-m1 modules
sys.path.append('../h-m1')
from h_m1.code.data.loader import TheoremSampler
from h_m1.code.analysis.variance_analyzer import VarianceAnalyzer

def load_h_m1_results(results_path: str = '../h-m1/results/experiment_results.pkl') -> List[Dict]:
    """
    Load h-m1 saved results to reuse theorems and variance calculations.
    
    Args:
        results_path: Path to h-m1 saved results
    
    Returns:
        h_m1_results: List of dicts with 'variance', 'outcome', 'theorem_id', 'entropies'
    
    Raises:
        FileNotFoundError: If h-m1 results not available
    """
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"h-m1 results not found at {results_path}")
    
    with open(results_path, 'rb') as f:
        h_m1_results = pickle.load(f)
    
    return h_m1_results

def rerun_with_tree_tracking(h_m1_results: List[Dict]) -> List[Dict]:
    """
    Re-run h-m1 timeout group with search tree tracking.
    
    Args:
        h_m1_results: h-m1 results (to reuse theorems and variance)
    
    Returns:
        h_m2_results: Results extended with search tree tracking
    
    Strategy:
        - Reuse h-m1 variance values (validated)
        - Re-run ONLY timeout group to capture search trees
        - Significantly faster than full re-run
    """
    timeout_results = [r for r in h_m1_results if r['outcome'] == 'timeout']
    
    runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)
    h_m2_results = []
    
    for result in timeout_results:
        # Re-run to get search tree
        tree_result = runner.run_experiment(result['theorem'])
        
        # Combine h-m1 variance with h-m2 tree
        h_m2_results.append({
            'variance': result['variance'],  # Reuse h-m1
            'outcome': 'timeout',
            'theorem_id': result['theorem_id'],
            'search_tree': tree_result['search_tree'],  # NEW
            'proof_states': tree_result['proof_states']  # NEW
        })
    
    return h_m2_results

def main():
    """
    Main experiment orchestration.
    
    Workflow:
    1. Load h-m1 results (reuse theorems and variance)
    2. Re-run timeout group with search tree tracking
    3. Classify each timeout as divergent vs difficult
    4. Analyze variance by divergence classification
    5. Visualize subgroup comparison
    6. Save results and evaluate gate
    """
    # E6-2: Load h-m1 results and extend with tree tracking
    print("Loading h-m1 results...")
    h_m1_results = load_h_m1_results()
    print(f"✓ Loaded {len(h_m1_results)} h-m1 results")
    
    print("Re-running timeout group with search tree tracking...")
    timeout_results = rerun_with_tree_tracking(h_m1_results)
    print(f"✓ Captured search trees for {len(timeout_results)} timeouts")
    
    # E6-3: Classify divergence
    print("Classifying timeouts as divergent vs difficult...")
    classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)
    
    for result in timeout_results:
        is_divergent, markers = classifier.classify_timeout(
            result['proof_states'],
            result['search_tree']
        )
        result['is_divergent'] = is_divergent
        result['divergence_markers'] = markers
    
    divergent_count = sum(1 for r in timeout_results if r['is_divergent'])
    print(f"✓ Classified: {divergent_count} divergent, {len(timeout_results) - divergent_count} difficult")
    
    # E6-4: Analyze variance by divergence
    print("Analyzing variance by divergence classification...")
    subgroup_analyzer = TimeoutSubgroupAnalyzer()
    analysis = subgroup_analyzer.analyze_variance_by_divergence(timeout_results)
    
    # Save results
    with open('h-m2/results/timeout_subgroup_analysis.json', 'w') as f:
        json.dump({
            'divergent_mean_variance': analysis['divergent']['mean_variance'],
            'divergent_count': analysis['divergent']['count'],
            'difficult_mean_variance': analysis['difficult']['mean_variance'],
            'difficult_count': analysis['difficult']['count'],
            'difference': analysis['difference'],
            'gate_satisfied': analysis['gate_satisfied']
        }, f, indent=2)
    
    # Display gate evaluation
    print("\n" + "="*60)
    print("H-M2 GATE EVALUATION")
    print("="*60)
    print(f"Divergent group - Mean variance: {analysis['divergent']['mean_variance']:.4f}")
    print(f"Difficult group - Mean variance: {analysis['difficult']['mean_variance']:.4f}")
    print(f"Difference: {analysis['difference']:.4f}")
    print(f"Gate Satisfied: {analysis['gate_satisfied']}")
    print("="*60)
    
    return analysis
```

### Pseudo-code

```python
# Main workflow
if __name__ == '__main__':
    # Step 1: Reuse h-m1 results
    h_m1_results = load_h_m1_results()
    
    # Step 2: Re-run timeout group with tree tracking
    timeout_results = rerun_with_tree_tracking(h_m1_results)
    
    # Step 3: Classify divergence
    for result in timeout_results:
        result['is_divergent'], result['markers'] = classify_timeout(result)
    
    # Step 4: Subgroup analysis
    analysis = analyze_variance_by_divergence(timeout_results)
    
    # Step 5: Visualize (handled by Epic E5)
    visualize_divergence_comparison(analysis, timeout_results)
    
    # Step 6: Save and report
    save_results(analysis)
    print_gate_evaluation(analysis)
```

---

## Algorithm Complexity Analysis

### E2: Search Tree Tracking
**Time Complexity:** O(n) where n = num_proof_states (linear tracking overhead)  
**Space Complexity:** O(n + m) where m = num_tree_nodes (stores states + tree)

### E3: Divergence Classification
**Time Complexity:** O(n) for hash collision detection + O(m) for backtrack counting  
**Space Complexity:** O(n) for hash storage

### E4: Subgroup Analysis
**Time Complexity:** O(k) where k = num_timeouts (< 100, subset of h-m1)  
**Space Complexity:** O(k) for group separation

### E6: Result Reuse Optimization
**Time Complexity:** O(k) for timeout re-run (vs O(100) for full re-run)  
**Space Complexity:** O(k) for timeout results only

---

## Unit Test Requirements

### E2 Tests
```python
def test_tree_tracking():
    runner = ExtendedTimeoutRunnerWithTree()
    result = runner.run_experiment(mock_theorem)
    assert 'search_tree' in result
    assert 'proof_states' in result
    assert len(result['proof_states']) > 0

def test_tree_structure():
    runner = ExtendedTimeoutRunnerWithTree()
    result = runner.run_experiment(mock_theorem)
    tree = result['search_tree']
    assert hasattr(tree, 'nodes')
    assert hasattr(tree, 'edges')
```

### E3 Tests
```python
def test_collision_detection():
    classifier = DivergenceClassifier()
    states = ['s1', 's2', 's1', 's3']  # 1 collision
    collisions = classifier._detect_state_collisions(states)
    assert collisions == 1

def test_divergence_classification():
    classifier = DivergenceClassifier(collision_threshold=2, backtrack_threshold=5)
    # High collisions → divergent
    is_div1, _ = classifier.classify_timeout(cyclic_states, mock_tree)
    assert is_div1 == True
    # Low collisions, low backtracks → difficult
    is_div2, _ = classifier.classify_timeout(linear_states, simple_tree)
    assert is_div2 == False
```

### E4 Tests
```python
def test_subgroup_separation():
    timeout_results = [
        {'variance': 0.35, 'is_divergent': True},
        {'variance': 0.20, 'is_divergent': False},
        {'variance': 0.40, 'is_divergent': True},
    ]
    analyzer = TimeoutSubgroupAnalyzer()
    divergent_vars, difficult_vars = analyzer._separate_by_divergence(timeout_results)
    assert divergent_vars == [0.35, 0.40]
    assert difficult_vars == [0.20]

def test_gate_evaluation():
    analyzer = TimeoutSubgroupAnalyzer()
    assert analyzer.evaluate_gate(0.35, 0.20) == True  # divergent > difficult
    assert analyzer.evaluate_gate(0.20, 0.35) == False  # divergent < difficult
```

---

## Notes

**Key Insight:** h-m2 extends h-m1 by adding divergence classification layer to timeout group. Variance metric is identical (h-m1 validated), only subdivision changes.

**Optimization:** Reusing h-m1 variance values + re-running ONLY timeout group (~30-40 experiments) reduces runtime from hours to ~30-60 minutes.

**Divergence Detection:** Combines symbolic markers (state collisions, backtracks) with confidence variance to test whether high variance specifically signals divergence vs general difficulty.
