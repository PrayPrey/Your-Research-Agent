# Logic Design: h-m2

**Hypothesis:** Error Type Signature Analysis (MECHANISM)
**Type:** MECHANISM
**Date:** 2026-04-22
**Author:** Logic Agent

Applied: Multi-dataset comparison pattern, Statistical analysis template

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from base code
**Analyzed Path:** /home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_question_3/docs/youra_research/20260421_question/h-m1/code/
**Relevant Symbols:** MistralGenerator.generate_samples, SemanticEntropyEstimator.compute_uncertainty, SelfConsistencyEstimator.compute_uncertainty
**Verification:** Parameter names verified from actual implementation (not specs)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-m1. Signatures verified from actual implementation:

```python
# From: h-m1/code/models/generator.py (ACTUAL CODE)
class MistralGenerator:
    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        device: str = "cuda",
        dtype = torch.float16
    ):
        """Initialize Mistral-7B model."""
        ...
    
    def load(self) -> None:
        """Load model and tokenizer."""
        ...
    
    def generate_samples(
        self,
        question: str,
        k: int = 10,
        temperature: float = 0.7,
        max_new_tokens: int = 50,
        seed: int = 42
    ) -> List[str]:
        """Generate K diverse answers. Returns: List[str] with K answers."""
        ...

# From: h-m1/code/methods/uncertainty.py (ACTUAL CODE)
class SemanticEntropyEstimator:
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5
    ):
        """Initialize semantic entropy estimator."""
        ...
    
    def load(self) -> None:
        """Load embedding model."""
        ...
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """Compute semantic entropy. Returns: float (higher = more uncertain)."""
        ...

class SelfConsistencyEstimator:
    """Self-consistency via majority voting."""
    
    def compute_uncertainty(self, answers: List[str]) -> float:
        """
        Compute disagreement rate.
        
        Args:
            answers: List[str] - K generated answers
        Returns:
            float - Disagreement rate (1 - majority_fraction)
        """
        ...
```

**Verified from**: h-m1/code/ (actual implementation, NOT spec!)

---

## D-1: TruthfulQA Dataset Loader [Complexity: 7, Budget: 1]

**Applied:** HuggingFace datasets pattern

### API Signatures

```python
from datasets import load_dataset
from typing import List
import random

class TQADataLoader:
    """Load TruthfulQA dataset for confident misconception analysis."""
    
    def __init__(self, split: str = "validation", num_samples: int = 100, seed: int = 42):
        """
        Initialize TruthfulQA loader.
        
        Args:
            split: Dataset split (validation)
            num_samples: Number of samples to use
            seed: Random seed for reproducibility
        """
        self.split = split
        self.num_samples = num_samples
        self.seed = seed
        self.questions = None
    
    def load(self) -> None:
        """Load TruthfulQA dataset. questions: List[str]"""
        ...
    
    def get_questions(self) -> List[str]:
        """Return question strings. Returns: List[str] with num_samples questions."""
        ...
```

### Pseudo-code

```
1. dataset = load_dataset("truthful_qa", "generation", split="validation")
2. questions = [item['question'] for item in dataset]
3. random.seed(seed)
4. self.questions = random.sample(questions, num_samples)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | TQA Loading | Implement HuggingFace dataset loading and sampling |

---

## A-1: Error Signature Analyzer [Complexity: 9, Budget: 1]

**Applied:** Pipeline orchestration pattern

### API Signatures

```python
from typing import List, Dict

class ErrorSignatureAnalyzer:
    """Analyze uncertainty signatures across error types."""
    
    def __init__(self, semantic_estimator, consistency_estimator, generator):
        """
        Initialize analyzer with uncertainty methods.
        
        Args:
            semantic_estimator: SemanticEntropyEstimator instance
            consistency_estimator: SelfConsistencyEstimator instance
            generator: MistralGenerator instance
        """
        self.semantic = semantic_estimator
        self.consistency = consistency_estimator
        self.generator = generator
    
    def analyze_dataset(
        self,
        questions: List[str],
        dataset_name: str,
        k: int = 5,
        temperature: float = 0.7
    ) -> Dict[str, List[float]]:
        """
        Compute diversity and agreement scores for dataset.
        
        Args:
            questions: List[str] - Question list (100 samples)
            dataset_name: str - Dataset identifier for logging
            k: int - Samples per question (default 5)
            temperature: float - Sampling temperature
        
        Returns:
            Dict with keys: 'diversity', 'agreement'
            Each value: List[float] with 100 scores
        """
        ...
    
    def compare_signatures(
        self,
        nq_scores: Dict[str, List[float]],
        tqa_scores: Dict[str, List[float]]
    ) -> Dict[str, any]:
        """
        Compare signatures between datasets.
        
        Args:
            nq_scores: NaturalQuestions scores
            tqa_scores: TruthfulQA scores
        
        Returns:
            Dict with keys: 'nq_diversity_mean', 'tqa_diversity_mean',
                           'nq_agreement_mean', 'tqa_agreement_mean'
        """
        ...
```

### Pseudo-code

```
analyze_dataset:
1. diversity_scores = []
2. agreement_scores = []
3. For each question in questions:
   a. answers = generator.generate_samples(question, k=k, temperature=temperature)
   b. diversity = semantic.compute_uncertainty(answers)
   c. agreement = 1.0 - consistency.compute_uncertainty(answers)  # Invert to get agreement
   d. diversity_scores.append(diversity)
   e. agreement_scores.append(agreement)
4. return {'diversity': diversity_scores, 'agreement': agreement_scores}

compare_signatures:
1. nq_div_mean = mean(nq_scores['diversity'])
2. tqa_div_mean = mean(tqa_scores['diversity'])
3. nq_agr_mean = mean(nq_scores['agreement'])
4. tqa_agr_mean = mean(tqa_scores['agreement'])
5. return summary dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Signature Pipeline | Implement answer generation and metric computation loop |

---

## S-1: Statistical Comparison [Complexity: 8, Budget: 1]

**Applied:** Scipy t-test pattern

### API Signatures

```python
from scipy.stats import ttest_ind
import numpy as np
from typing import Dict, List

class StatisticalAnalyzer:
    """Perform statistical tests for error signature comparison."""
    
    def __init__(self):
        """Initialize statistical analyzer."""
        pass
    
    def independent_ttest(
        self,
        group1: List[float],
        group2: List[float]
    ) -> Dict[str, float]:
        """
        Perform independent samples t-test.
        
        Args:
            group1: List[float] - First group scores (100 samples)
            group2: List[float] - Second group scores (100 samples)
        
        Returns:
            Dict with keys: 't_statistic', 'p_value', 'mean1', 'mean2'
        """
        ...
    
    def evaluate_gate(
        self,
        diversity_test: Dict[str, float],
        threshold: float = 0.05
    ) -> bool:
        """
        Evaluate SHOULD_WORK gate condition.
        
        Args:
            diversity_test: Dict with t-test results
            threshold: float - Significance threshold (default 0.05)
        
        Returns:
            bool - True if (p < 0.05) AND (mean_nq > mean_tqa)
        """
        ...
    
    def save_results(self, results: Dict, output_path: str):
        """Save statistical results to JSON."""
        ...
```

### Pseudo-code

```
independent_ttest:
1. t_stat, p_val = ttest_ind(group1, group2)
2. return {'t_statistic': t_stat, 'p_value': p_val, 
           'mean1': mean(group1), 'mean2': mean(group2)}

evaluate_gate:
1. p_value = diversity_test['p_value']
2. mean_nq = diversity_test['mean1']
3. mean_tqa = diversity_test['mean2']
4. gate_pass = (p_value < threshold) and (mean_nq > mean_tqa)
5. return gate_pass
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | T-test Implementation | Implement scipy t-test and gate evaluation logic |

---

## V-1: Signature Visualization [Complexity: 10, Budget: 0]

**Applied:** Matplotlib/Seaborn plotting pattern

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict

class SignatureVisualizer:
    """Generate visualizations for error signature analysis."""
    
    def __init__(self):
        """Initialize visualizer."""
        pass
    
    def plot_gate_comparison(
        self,
        nq_div_mean: float,
        tqa_div_mean: float,
        output_path: str
    ):
        """
        Generate gate metrics comparison bar chart.
        
        Args:
            nq_div_mean: NQ diversity mean
            tqa_div_mean: TQA diversity mean
            output_path: Path to save figure
        """
        ...
    
    def plot_diversity_distributions(
        self,
        nq_scores: List[float],
        tqa_scores: List[float],
        output_path: str
    ):
        """Generate box plots for diversity distributions. nq/tqa_scores: [100]"""
        ...
    
    def plot_agreement_distributions(
        self,
        nq_scores: List[float],
        tqa_scores: List[float],
        output_path: str
    ):
        """Generate box plots for agreement distributions. nq/tqa_scores: [100]"""
        ...
    
    def plot_signature_space(
        self,
        nq_diversity: List[float],
        nq_agreement: List[float],
        tqa_diversity: List[float],
        tqa_agreement: List[float],
        output_path: str
    ):
        """
        Generate 2D signature space scatter plot.
        
        Args:
            nq_diversity: [100] NQ diversity scores
            nq_agreement: [100] NQ agreement scores
            tqa_diversity: [100] TQA diversity scores
            tqa_agreement: [100] TQA agreement scores
            output_path: Path to save figure
        """
        ...
```

### Pseudo-code

```
plot_gate_comparison:
1. fig, ax = plt.subplots()
2. bars = ax.bar(['NQ (Knowledge Gaps)', 'TQA (Misconceptions)'], 
                  [nq_div_mean, tqa_div_mean])
3. ax.set_ylabel('Mean Semantic Diversity')
4. plt.savefig(output_path)

plot_signature_space:
1. plt.scatter(nq_diversity, nq_agreement, label='NQ', alpha=0.6)
2. plt.scatter(tqa_diversity, tqa_agreement, label='TQA', alpha=0.6)
3. plt.xlabel('Semantic Diversity')
4. plt.ylabel('Sampling Agreement')
5. plt.legend()
6. plt.savefig(output_path)
```

---

## E-1: Experiment Runner [Complexity: 11, Budget: 0]

**Applied:** Experiment orchestration pattern

### API Signatures

```python
from typing import Dict
import sys

class ExperimentRunner:
    """Orchestrate error signature comparison experiment."""
    
    def __init__(self, config: Dict):
        """
        Initialize experiment with configuration.
        
        Args:
            config: Dict with keys: h_m1_code_path, datasets, model_name,
                   k_samples, temperature, significance_threshold, output_dir
        """
        self.config = config
        self.nq_loader = None
        self.tqa_loader = None
        self.generator = None
        self.semantic_estimator = None
        self.consistency_estimator = None
        self.analyzer = None
        self.stats = None
        self.visualizer = None
    
    def setup_components(self):
        """
        Initialize all pipeline components.
        
        Sets up:
        - sys.path for h-m1 imports
        - Data loaders (NQ, TQA)
        - Generator from h-m1
        - Uncertainty estimators from h-m1
        - Analyzer, statistics, visualizer
        """
        ...
    
    def run_experiment(self) -> Dict[str, any]:
        """
        Run full experiment pipeline.
        
        Returns:
            Dict with keys: 'nq_scores', 'tqa_scores', 'diversity_test',
                           'agreement_test', 'gate_pass', 'figures'
        """
        ...
    
    def generate_visualizations(
        self,
        nq_scores: Dict[str, List[float]],
        tqa_scores: Dict[str, List[float]],
        stats_results: Dict
    ):
        """Generate all required figures (4 plots)."""
        ...
```

### Pseudo-code

```
setup_components:
1. sys.path.insert(0, config['h_m1_code_path'])
2. from models.generator import MistralGenerator
3. from methods.uncertainty import SemanticEntropyEstimator, SelfConsistencyEstimator
4. Initialize all components with config parameters

run_experiment:
1. setup_components()
2. nq_questions = nq_loader.get_questions()  # 100
3. tqa_questions = tqa_loader.get_questions()  # 100
4. nq_scores = analyzer.analyze_dataset(nq_questions, "NaturalQuestions")
5. tqa_scores = analyzer.analyze_dataset(tqa_questions, "TruthfulQA")
6. diversity_test = stats.independent_ttest(nq_scores['diversity'], tqa_scores['diversity'])
7. agreement_test = stats.independent_ttest(nq_scores['agreement'], tqa_scores['agreement'])
8. gate_pass = stats.evaluate_gate(diversity_test)
9. generate_visualizations(nq_scores, tqa_scores, stats_results)
10. save_results()
11. return results
```

---

## G-1: Gate Verification [Complexity: 5, Budget: 0]

**Applied:** Validation reporting pattern

### API Signatures

```python
from typing import Dict

def verify_gate(
    diversity_test: Dict[str, float],
    threshold: float = 0.05
) -> bool:
    """
    Verify SHOULD_WORK gate condition.
    
    Args:
        diversity_test: Dict with 't_statistic', 'p_value', 'mean1', 'mean2'
        threshold: Significance threshold
    
    Returns:
        bool - True if (p < 0.05) AND (mean_nq > mean_tqa)
    """
    ...

def print_gate_report(
    diversity_test: Dict,
    agreement_test: Dict,
    gate_pass: bool
):
    """
    Print formatted gate verification report.
    
    Displays:
    - Diversity comparison (NQ vs TQA)
    - Agreement comparison (NQ vs TQA)
    - Statistical significance (p-values)
    - Gate result (PASS/FAIL)
    """
    ...
```

### Pseudo-code

```
verify_gate:
1. p_value = diversity_test['p_value']
2. mean_nq = diversity_test['mean1']
3. mean_tqa = diversity_test['mean2']
4. return (p_value < threshold) and (mean_nq > mean_tqa)

print_gate_report:
1. Print diversity means and p-value
2. Print agreement means and p-value
3. Check gate condition
4. Display PASS/FAIL with reasoning
5. Save to verification_state.yaml
```

---

## Summary

**Total Subtasks:** 3 (L-1-1, L-2-1, L-3-1)
**Budget Compliance:** 3/4 used (within allocation)
**API Completeness:** All tasks have copy-paste ready signatures
**Base Hypothesis Integration:** Verified parameter names from actual h-m1 code
**Codebase Type:** Extends base_hypothesis h-m1 with new TQA dataset and statistical comparison
**Key Design Decision:** Reuse h-m1 via sys.path to avoid code duplication
