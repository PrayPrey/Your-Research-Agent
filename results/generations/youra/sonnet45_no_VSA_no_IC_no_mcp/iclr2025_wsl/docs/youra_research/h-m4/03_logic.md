# Logic Specification: h-m4 Meta-Research Validation

**Date:** 2026-08-25
**Hypothesis:** h-m4 (MECHANISM)
**Phase:** Phase 3 - Logic Design
**Budget:** 2 subtasks allocated (A-3 decomposition)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Reusing h-m3 confound detector + h-m1 KB structure
**Analyzed Path**: h-m3/src/ (detector, confound_db), h-m1/data/pwc_cache/
**Relevant Symbols**: ConfoundDetector.detect(), ConfoundDatabase.load_patterns(), kb.yaml structure

**Note**: h-m4 loads h-m3 code patterns directly (copy) and h-m1 KB file (YAML). No package imports needed.

---

## A-3: Experiment Executor [Complexity: 10, Budget: 2/2]

**Applied**: PoC experiment pattern (Archon KB)

### API Signatures

```python
from typing import Dict, List, Optional
import numpy as np
from scipy.stats import ttest_ind

class ExperimentExecutor:
    def __init__(self, seed: int = 42):
        """seed: reproducibility."""
        self.seed = seed
        np.random.seed(seed)
    
    def run_experiment(self, hypothesis: Dict) -> Dict:
        """Run simplified PoC experiment. Returns: {hypothesis_id, p_value, control_mean, treatment_mean}."""
        ...
    
    def _load_dataset(self, dataset_name: str) -> np.ndarray:
        """Load or mock dataset. Returns: [N, F] features."""
        ...
    
    def _run_control(self, data: np.ndarray) -> List[float]:
        """Run baseline model (5 trials). Returns: metrics list."""
        ...
    
    def _run_treatment(self, data: np.ndarray, intervention: str) -> List[float]:
        """Run intervention model (5 trials). Returns: metrics list."""
        ...
    
    def _compute_pvalue(self, control: List[float], treatment: List[float]) -> float:
        """Two-sample t-test. Returns: p-value."""
        ...
```

### Pseudo-code

```
__init__(seed):
    1. self.seed = seed
    2. np.random.seed(seed)

run_experiment(hypothesis):
    1. dataset = _load_dataset(hypothesis["expected_dbm"]["dataset"])
    2. control_metrics = _run_control(dataset)
    3. treatment_metrics = _run_treatment(dataset, hypothesis["intervention"])
    4. p_value = _compute_pvalue(control_metrics, treatment_metrics)
    5. Return {hypothesis_id, p_value, control_mean, treatment_mean}

_load_dataset(dataset_name):
    1. If dataset_name in ["CIFAR-10", "CIFAR-100", "Fashion-MNIST"]:
        - Return mock data: np.random.randn(100, 10)  # [N, F]
    2. Else: Return synthetic data

_run_control(data):
    1. metrics = []
    2. For trial in range(5):
        - Split data 80/20 (train/test)
        - Train simple linear model (sklearn.linear_model.LogisticRegression)
        - Evaluate on test split
        - metrics.append(test_accuracy)
    3. Return metrics

_run_treatment(data, intervention):
    1. metrics = []
    2. For trial in range(5):
        - Apply intervention (e.g., "dropout_increase" → add noise to data)
        - Split data 80/20
        - Train simple model
        - Evaluate
        - metrics.append(test_accuracy)
    3. Return metrics

_compute_pvalue(control, treatment):
    1. t_stat, p_value = scipy.stats.ttest_ind(control, treatment)
    2. Return p_value
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Dataset loading | Mock data generation for known datasets |
| L-3-2 | Experiment runner | Control/treatment trials + t-test |

---

## External Dependencies API (Base Hypotheses)

### API Signatures (From Actual Code)

```python
# From: h-m3/src/detector.py (ACTUAL CODE)
class ConfoundDetector:
    def __init__(self, pattern_db: Dict[str, List[Dict]]):
        """pattern_db: from ConfoundDatabase.load_patterns()."""
        self.patterns = pattern_db
    
    def detect(self, hypothesis_text: str) -> Tuple[str, Optional[str]]:
        """Returns: ('confounded', pattern_name) or ('unconfounded', None)."""
        ...

# From: h-m3/src/confound_db.py (ACTUAL CODE)
class ConfoundDatabase:
    def __init__(self):
        """Initialize with hard-coded patterns."""
        self.patterns = self._init_patterns()
    
    def load_patterns(self) -> Dict[str, List[Dict]]:
        """Returns: {domain: [patterns]}."""
        ...
    
    def get_all_patterns(self) -> List[Dict]:
        """Returns: [{domain, keywords, description}, ...]."""
        ...
```

**KB Structure** (h-m1/data/pwc_cache/kb.yaml):
```yaml
metadata:
  triple_count: 49
triples:
  - dataset: "CIFAR-10"
    benchmark: "image-classification"
    metric: "Accuracy"
```

**Verified from**: h-m3/src/ actual implementations, h-m1/data/ file structure

---

## Remaining Modules (Standard Python, No Subtask Allocation)

### HypothesisGenerator (src/generator.py)

**Applied**: LLM API pattern

```python
import requests
from typing import List, Dict

class HypothesisGenerator:
    def __init__(self, api_key: str, seed: int = 42):
        """api_key: Anthropic API key."""
        self.api_key = api_key
        self.seed = seed
    
    def generate_pool(self, n: int = 100) -> List[Dict]:
        """Generate n hypotheses. Returns: [{id, statement, domain, complexity, ...}, ...]."""
        ...
```

### VerificationPipeline (src/verifier.py)

**Applied**: KB lookup + confound detection pattern

```python
import yaml

class VerificationPipeline:
    def __init__(self, kb_path: str, confound_db: ConfoundDatabase):
        """kb_path: path to h-m1 kb.yaml."""
        self.kb = self._load_kb(kb_path)
        self.detector = ConfoundDetector(confound_db.load_patterns())
    
    def classify_hypothesis(self, hypothesis: Dict) -> Tuple[str, str]:
        """Returns: ('testable', reason) or ('not-testable', reason)."""
        ...
    
    def _check_dbm_exists(self, dbm_triple: Dict) -> bool:
        """Check if triple exists in KB. Returns: bool."""
        ...
    
    def _flag_confounds(self, hypothesis_text: str) -> Tuple[bool, str]:
        """Returns: (is_confounded, pattern_name)."""
        ...
```

### RandomSampler (src/sampler.py)

**Applied**: stdlib random.sample

```python
import random

class RandomSampler:
    def __init__(self, seed: int = 42):
        """seed: reproducibility."""
        self.seed = seed
        random.seed(seed)
    
    def sample_testable(self, hypotheses: List[Dict], k: int = 20) -> List[Dict]:
        """Sample k from testable subset. Returns: sampled hypotheses."""
        testable = [h for h in hypotheses if h["system_classification"] == "testable"]
        return random.sample(testable, min(k, len(testable)))
```

### StatisticalValidator (src/validator.py)

**Applied**: binomial test pattern

```python
from scipy.stats import binom_test

class StatisticalValidator:
    def __init__(self, gate_threshold: float = 0.65, baseline: float = 0.50):
        """gate_threshold: 0.65, baseline: 0.50."""
        self.gate_threshold = gate_threshold
        self.baseline = baseline
    
    def compute_success_rate(self, p_values: List[float], alpha: float = 0.05) -> float:
        """Returns: proportion of p < alpha."""
        return sum([p < alpha for p in p_values]) / len(p_values)
    
    def binomial_test(self, successes: int, n: int, p0: float = 0.50) -> float:
        """Returns: binomial test p-value."""
        return binom_test(successes, n, p0, alternative='greater')
    
    def check_gate(self, success_rate: float) -> Dict:
        """Returns: {success_rate, gate_passed, poc_passed}."""
        ...
```

### Visualizer (src/visualizer.py)

**Applied**: matplotlib pattern

```python
import matplotlib.pyplot as plt
from pathlib import Path

class Visualizer:
    def __init__(self, output_dir: str):
        """output_dir: save path for figures."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_gate_comparison(self, baseline: float, proposed: float, threshold: float) -> str:
        """Bar chart. Returns: saved file path."""
        ...
    
    def plot_success_by_domain(self, results: List[Dict], hypotheses: List[Dict]) -> str:
        """Domain breakdown. Returns: saved file path."""
        ...
    
    def plot_classification_dist(self, hypotheses: List[Dict]) -> str:
        """Pie chart. Returns: saved file path."""
        ...
    
    def plot_pvalue_dist(self, p_values: List[float]) -> str:
        """Histogram. Returns: saved file path."""
        ...
```

### ExperimentRunner (src/main.py)

**Applied**: pipeline pattern

```python
import json
from pathlib import Path

def run_pipeline(config: Dict) -> Dict:
    """Execute complete pipeline. Returns: {success_rate, gate_passed, metrics}."""
    
    # 1. Generate hypothesis pool
    generator = HypothesisGenerator(config["api_key"], config["seed"])
    hypotheses = generator.generate_pool(n=100)
    
    # 2. Verify hypotheses
    confound_db = ConfoundDatabase()
    verifier = VerificationPipeline(config["kb_path"], confound_db)
    for h in hypotheses:
        h["system_classification"], h["classification_reason"] = verifier.classify_hypothesis(h)
    
    # 3. Sample testable hypotheses
    sampler = RandomSampler(config["seed"])
    sampled = sampler.sample_testable(hypotheses, k=20)
    
    # 4. Run experiments
    executor = ExperimentExecutor(config["seed"])
    results = [executor.run_experiment(h) for h in sampled]
    
    # 5. Validate
    validator = StatisticalValidator()
    p_values = [r["p_value"] for r in results]
    success_rate = validator.compute_success_rate(p_values)
    successes = sum([p < 0.05 for p in p_values])
    binomial_p = validator.binomial_test(successes, len(p_values))
    gate_status = validator.check_gate(success_rate)
    
    # 6. Visualize
    viz = Visualizer(config["figures_dir"])
    viz.plot_gate_comparison(0.50, success_rate, 0.65)
    viz.plot_success_by_domain(results, hypotheses)
    viz.plot_classification_dist(hypotheses)
    viz.plot_pvalue_dist(p_values)
    
    # 7. Save
    output = {
        "success_rate": success_rate,
        "gate_passed": gate_status["gate_passed"],
        "poc_passed": gate_status["poc_passed"],
        "binomial_p": binomial_p,
        "baseline": 0.50
    }
    
    Path(config["output_dir"]).mkdir(parents=True, exist_ok=True)
    with open(Path(config["output_dir"]) / "results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    return output
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Subtask count within budget (2/2 used for A-3 only)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies API section with verified signatures
- [x] Base hypothesis APIs verified from actual code (h-m3/src/)

---

**Total Subtasks Used**: 2/2 (A-3 decomposition only)
**Key Design Choices**:
- Mock data for PoC (no full training runs)
- 5 trials per condition (control/treatment)
- @lru_cache skipped (experiments run once)
- sklearn.linear_model for baseline (simplest PoC model)
