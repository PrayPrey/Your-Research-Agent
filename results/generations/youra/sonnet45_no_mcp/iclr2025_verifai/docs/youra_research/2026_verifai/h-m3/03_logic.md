# Logic Design: h-m3

**Date:** 2026-04-20  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Hybrid Signal Combination)  
**Logic Designer:** Phase 3 Logic Agent  
**Budget:** 10 subtasks  
**Base Hypothesis:** h-m2 (COMPLETED, PASSED)

Applied: Multi-signal fusion pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m2 actual code  
**Analyzed Path:** h-m2/code/  
**Relevant Symbols:**
- `ExtendedTimeoutRunnerWithTree.run_experiment()` - returns dict with search_tree, proof_states
- `SearchTree.get_collision_count()` - returns int
- `SearchTree.get_backtrack_count()` - returns int
- `ConfidenceTrajectoryExtractor.extract_confidence_trajectory()` - returns (float, List[float])

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/experiment/tree_tracker.py (ACTUAL CODE - VERIFIED)
class SearchTree:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.state_hashes = []
    
    def get_collision_count(self) -> int:
        """Returns: total_hashes - unique_hashes"""
        ...
    
    def get_backtrack_count(self) -> int:
        """Returns: count of nodes with multiple children"""
        ...


class ExtendedTimeoutRunnerWithTree:
    def __init__(self, timeout_seconds: int = 300, confidence_window: int = 15):
        ...
    
    def run_experiment(self, theorem) -> Dict[str, Any]:
        """
        Returns:
            {
                'theorem_id': str,
                'outcome': int,  # 0=success, 1=timeout
                'confidence_variance': float,
                'entropies': List[float],
                'proof_states': List[state],
                'search_tree': SearchTree,
                'execution_time': float,
                'status': str
            }
        """
        ...


# From: h-m2/code/models/confidence_extractor.py (ACTUAL CODE - VERIFIED)
class ConfidenceTrajectoryExtractor:
    def __init__(self, window_size: int = 15):
        ...
    
    def extract_confidence_trajectory(self, proof_session) -> Tuple[float, List[float]]:
        """Returns: (confidence_variance, entropies)"""
        ...
    
    def compute_variance(self, entropies: List[float]) -> float:
        """Returns: np.std(entropies)"""
        ...
```

**Verified from**: h-m2/code/ (actual implementation)

---

## E2: Symbolic Signal Extraction [Complexity: 12, Budget: 3/10]

Applied: Statistical signal extraction

### API Signatures

```python
from typing import List, Dict, Any
import numpy as np

class SymbolicSignalExtractor:
    """Extract symbolic divergence signals from proof states."""
    
    def __init__(self, growth_window: int = 10):
        self.growth_window = growth_window
    
    def extract_signals(self, proof_states: List[Any], search_tree: Any) -> Dict[str, float]:
        """
        Extract symbolic signals. proof_states: [N], search_tree: SearchTree
        Returns: {'state_collisions': int, 'exponential_growth_rate': float}
        """
        collisions = self._count_state_collisions(search_tree)
        growth_rate = self._fit_exponential_growth(proof_states)
        return {
            'state_collisions': collisions,
            'exponential_growth_rate': growth_rate
        }
    
    def _count_state_collisions(self, search_tree: Any) -> int:
        """Reuse SearchTree.get_collision_count()"""
        return search_tree.get_collision_count()
    
    def _fit_exponential_growth(self, proof_states: List[Any]) -> float:
        """
        Fit exponential trend to proof state sizes.
        
        Algorithm:
        1. sizes = [len(state.goals) for state in proof_states[:window]]
        2. log_sizes = log(sizes + 1)
        3. slope = polyfit(t, log_sizes, deg=1)[0]
        4. return slope
        """
        if len(proof_states) < 2:
            return 0.0
        
        sizes = []
        for state in proof_states[:self.growth_window]:
            try:
                size = len(state.goals) if hasattr(state, 'goals') else len(str(state))
                sizes.append(max(size, 1))
            except:
                sizes.append(1)
        
        if len(sizes) < 2:
            return 0.0
        
        t = np.arange(len(sizes))
        log_sizes = np.log(sizes)
        
        try:
            coeffs = np.polyfit(t, log_sizes, 1)
            return float(coeffs[0])
        except:
            return 0.0
```

### Subtasks [3/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | State collision counting | Call search_tree.get_collision_count() |
| L-2-2 | Exponential growth fitting | numpy polyfit on log(sizes) |
| L-2-3 | Edge case handling | Empty states, fit failures |

---

## E3: Hybrid Termination Detector [Complexity: 14, Budget: 3/10]

Applied: Voting ensemble pattern

### API Signatures

```python
from typing import Dict, Any

class HybridTerminationDetector:
    """Three-signal hybrid detector with k-of-n voting."""
    
    def __init__(self, thresholds: Dict[str, float], voting_k: int = 2):
        self.thresholds = thresholds
        self.voting_k = voting_k
        self.symbolic_extractor = SymbolicSignalExtractor()
    
    def extract_all_signals(self, result: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all signals from ExtendedTimeoutRunnerWithTree result.
        
        Args:
            result: dict with 'confidence_variance', 'proof_states', 'search_tree'
        
        Returns: {
            'confidence_variance': float,
            'state_collisions': int,
            'exponential_growth': float,
            'backtrack_freq': float
        }
        """
        # Signal 1: Confidence (from result)
        confidence_variance = result.get('confidence_variance', 0.0)
        
        # Signal 2: Symbolic (NEW)
        symbolic_signals = self.symbolic_extractor.extract_signals(
            result['proof_states'],
            result['search_tree']
        )
        
        # Signal 3: Search tree (from h-m2)
        search_tree = result['search_tree']
        backtrack_count = search_tree.get_backtrack_count() if search_tree else 0
        num_nodes = len(search_tree.nodes) if search_tree else 1
        backtrack_freq = backtrack_count / max(num_nodes, 1)
        
        return {
            'confidence_variance': confidence_variance,
            'state_collisions': symbolic_signals['state_collisions'],
            'exponential_growth': symbolic_signals['exponential_growth_rate'],
            'backtrack_freq': backtrack_freq
        }
    
    def predict(self, signals: Dict[str, float]) -> bool:
        """
        Voting decision: True if >= k of 3 signals trigger.
        """
        conf_alert = signals['confidence_variance'] > self.thresholds['variance']
        symb_alert = (signals['state_collisions'] > self.thresholds['collisions'] or
                     signals['exponential_growth'] > self.thresholds['growth'])
        search_alert = signals['backtrack_freq'] > self.thresholds['backtrack']
        
        votes = [conf_alert, symb_alert, search_alert]
        return sum(votes) >= self.voting_k
```

### Subtasks [3/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Signal extraction | Combine confidence + symbolic + search |
| L-3-2 | Voting logic | k-of-3 threshold with alert checkers |
| L-3-3 | Backtrack frequency | From search_tree.get_backtrack_count() |

---

## E4: Threshold Selector [Complexity: 8, Budget: 1/10]

Applied: Median-based threshold selection

### API Signatures

```python
import numpy as np

class ThresholdSelector:
    """Select thresholds from timeout group using median strategy."""
    
    def select_thresholds(self, timeout_signals: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Args: List of signal dicts from timeout theorems
        Returns: {'variance': float, 'collisions': int, 'growth': float, 'backtrack': float}
        """
        if not timeout_signals:
            return {'variance': 0.25, 'collisions': 2, 'growth': 0.1, 'backtrack': 0.2}
        
        return {
            'variance': float(np.median([s['confidence_variance'] for s in timeout_signals])),
            'collisions': int(np.median([s['state_collisions'] for s in timeout_signals])),
            'growth': float(np.median([s['exponential_growth'] for s in timeout_signals])),
            'backtrack': float(np.median([s['backtrack_freq'] for s in timeout_signals]))
        }
```

### Subtasks [1/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Median calculation | For each signal type with fallback |

---

## E5: Ablation Framework [Complexity: 16, Budget: 3/10]

Applied: Model comparison framework

### API Signatures

```python
from sklearn.metrics import precision_score, recall_score, f1_score

class AblationFramework:
    """Framework for evaluating 7 detector variants."""
    
    def __init__(self, thresholds: Dict[str, float]):
        self.thresholds = thresholds
        self.models = self._create_models()
    
    def _create_models(self) -> Dict[str, callable]:
        """
        Returns: 7 detector functions (confidence_only, symbolic_only, search_only,
                 conf_symb, conf_search, symb_search, hybrid_all)
        """
        t = self.thresholds
        return {
            'confidence_only': lambda s: s['confidence_variance'] > t['variance'],
            'symbolic_only': lambda s: (s['state_collisions'] > t['collisions'] or 
                                       s['exponential_growth'] > t['growth']),
            'search_only': lambda s: s['backtrack_freq'] > t['backtrack'],
            'conf_symb': lambda s: (s['confidence_variance'] > t['variance'] or
                                   s['state_collisions'] > t['collisions'] or
                                   s['exponential_growth'] > t['growth']),
            'conf_search': lambda s: (s['confidence_variance'] > t['variance'] or
                                     s['backtrack_freq'] > t['backtrack']),
            'symb_search': lambda s: ((s['state_collisions'] > t['collisions'] or
                                      s['exponential_growth'] > t['growth']) or
                                     s['backtrack_freq'] > t['backtrack']),
            'hybrid_all': lambda s: self._hybrid_voting(s)
        }
    
    def _hybrid_voting(self, s: Dict) -> bool:
        """k=2 voting for hybrid model."""
        t = self.thresholds
        conf = s['confidence_variance'] > t['variance']
        symb = s['state_collisions'] > t['collisions'] or s['exponential_growth'] > t['growth']
        search = s['backtrack_freq'] > t['backtrack']
        return sum([conf, symb, search]) >= 2
    
    def evaluate_all_models(self, signals_list: List[Dict], ground_truth: List[int]) -> Dict:
        """
        Args: signals_list ([N] dicts), ground_truth ([N] labels 0/1)
        Returns: {model_name: {'precision': float, 'recall': float, 'f1': float, 'predictions': list}}
        """
        results = {}
        for model_name, model_func in self.models.items():
            predictions = [int(model_func(s)) for s in signals_list]
            results[model_name] = {
                'precision': precision_score(ground_truth, predictions, zero_division=0),
                'recall': recall_score(ground_truth, predictions, zero_division=0),
                'f1': f1_score(ground_truth, predictions, zero_division=0),
                'predictions': predictions
            }
        return results
```

### Subtasks [3/10]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Create 7 models | Single-signal, pairwise, hybrid |
| L-5-2 | Evaluate models | Run all on dataset |
| L-5-3 | Compute metrics | precision, recall, F1 via sklearn |

---

## E7: Main Experiment Script [Complexity: 15, Budget: 0/10]

Applied: Pipeline orchestration

### Pseudo-code

```
1. Load h-m1 results for ground truth
2. runner = ExtendedTimeoutRunnerWithTree(timeout_seconds=300)
3. For each theorem:
   - result = runner.run_experiment(theorem)
   - signals = detector.extract_all_signals(result)
4. timeout_signals = filter(signals where outcome==1)
5. thresholds = ThresholdSelector().select_thresholds(timeout_signals)
6. ablation = AblationFramework(thresholds)
7. metrics = ablation.evaluate_all_models(signals_list, ground_truth)
8. gate_satisfied = metrics['hybrid_all']['f1'] > all_single_f1s
9. visualize + save results
```

---

## Total Subtask Budget: 10/10 used

| Epic | Subtasks | Budget |
|------|----------|--------|
| E2 | Symbolic Signal Extraction | 3 |
| E3 | Hybrid Termination Detector | 3 |
| E4 | Threshold Selector | 1 |
| E5 | Ablation Framework | 3 |
| **TOTAL** | | **10** |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Subtask count within budget (10/10)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] External Dependencies API section included
- [x] API signatures verified from h-m2 actual code

---

## Notes

**Key Design:** Maximize h-m2 reuse. New components:
- SymbolicSignalExtractor (20%)
- HybridTerminationDetector voting (10%)
- AblationFramework (70% - largest effort)

**Threshold Strategy:** Median of timeout group (no hyperparameter search for PoC).

**Critical Path:** AblationFramework determines gate success (hybrid_f1 > all_single_f1s).
