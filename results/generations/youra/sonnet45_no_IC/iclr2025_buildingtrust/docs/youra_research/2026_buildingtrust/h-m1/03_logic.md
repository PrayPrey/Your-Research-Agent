# Logic Design: h-m1

**Date:** 2026-07-12
**Hypothesis:** h-m1 (MECHANISM - Reliability-Robustness Correlation via Memorization)
**Type:** MECHANISM
**Author:** Logic Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Standard scipy.stats correlation analysis
- Applied: Fisher z-transform confidence interval pattern
- Applied: Permutation test for statistical validation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-e1 actual implementation
**Analyzed Path:** `/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code/run_experiment.py`
**Relevant Symbols:** 
- `score_reliability()` - GPT-4 scoring with openai.ChatCompletion API
- `score_robustness()` - Paraphrase consistency with Sentence-BERT
- `generate_paraphrase()` - Simple synonym-based paraphrasing
- `load_llama_model()` - Returns (model, tokenizer) tuple
- `generate_responses()` - Returns list of dicts with keys: prompt_id, prompt, model, response, seed

---

## External Dependencies API (From h-e1 Actual Code)

The following APIs are called from base hypothesis h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/code/run_experiment.py (ACTUAL CODE)

def load_dataset() -> list[str]:
    """Load TruthfulQA dataset (817 prompts).
    Returns: List of question strings
    """
    ...

def load_llama_model(model_size: str = "7b") -> tuple:
    """Load Llama-2-chat model.
    Args:
        model_size: "7b", "13b", or "70b"
    Returns:
        (model, tokenizer) tuple
    """
    ...

def generate_responses(
    prompts: list[str], 
    model, 
    tokenizer, 
    model_size: str = "7b"
) -> list[dict]:
    """Generate responses using Llama-2-chat model.
    Returns: List of dicts with keys: prompt_id, prompt, model, response, seed
    """
    ...

def score_reliability(
    responses: list[dict], 
    api_key: str = None
) -> list[float]:
    """Score reliability using GPT-4-as-judge.
    Uses: openai.ChatCompletion.create() (legacy API)
    Returns: List of floats [0-1]
    """
    ...

def generate_paraphrase(text: str) -> str:
    """Generate paraphrase using simple synonym replacement.
    Returns: Paraphrased text
    """
    ...

def score_robustness(
    responses: list[dict], 
    model, 
    tokenizer, 
    sbert_model = None
) -> list[float]:
    """Score robustness using paraphrase consistency.
    Args:
        sbert_model: SentenceTransformer('all-MiniLM-L6-v2') if provided
    Returns: List of cosine similarity scores [0-1]
    """
    ...
```

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code/run_experiment.py` (lines 28-237)

---

## B-1: Stratified Dataset Preparation [Complexity: 9, Budget: 2]

**Applied:** TruthfulQA category-based stratification

### API Signatures

```python
class StratifiedTruthfulQALoader:
    def __init__(self):
        """Initialize stratified dataset loader."""
        self.dataset_name = "truthful_qa"
        self.config_name = "generation"
        self.factual_categories = ["Science", "History", "Geography"]
        self.misinfo_categories = ["Myths and Fairytales", "Fiction", "Conspiracy Theories"]
    
    def load_full_dataset(self) -> list[dict]:
        """Load TruthfulQA with metadata. Returns: 817 items with {question, category}"""
        ...
    
    def stratify_by_factuality(
        self, 
        dataset: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """Stratify into factual and misinformation strata.
        Returns: (factual_items, misinfo_items)
        """
        ...
    
    def get_factual_stratum(self) -> list[str]:
        """Get factual prompts (~400). Returns: List of question strings"""
        ...
    
    def get_misinformation_stratum(self) -> list[str]:
        """Get misinformation prompts (~400). Returns: List of question strings"""
        ...
    
    def validate_stratification(
        self, 
        factual: list, 
        misinfo: list
    ) -> bool:
        """Validate stratum sizes. Returns: True if both ~400 ± 50"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Category Mapping | Map TruthfulQA categories to factual/misinfo |
| L-1-2 | Size Validation | Ensure 350-450 samples per stratum |

---

## B-2: Response Generation Pipeline [Complexity: 11, Budget: 2]

**Applied:** Checkpoint/resume pattern from h-e1

### API Signatures

```python
class LlamaResponseGenerator:
    def __init__(self, model_size: str):
        """Initialize response generator.
        Args:
            model_size: "7b", "13b", or "70b"
        """
        self.model_size = model_size
        self.model = None
        self.tokenizer = None
    
    def load_model(self) -> tuple:
        """Load model. Returns: (model, tokenizer)"""
        ...
    
    def generate_response(self, prompt: str, seed: int) -> str:
        """Generate single response. Returns: Generated text"""
        ...
    
    def generate_batch(self, prompts: list[str]) -> list[dict]:
        """Generate batch with checkpointing.
        Returns: List of {prompt_id, prompt, model, response, seed}
        """
        ...
    
    def cleanup(self) -> None:
        """Free GPU memory."""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Checkpoint Logic | Save every 100 samples |
| L-2-2 | Memory Management | Cleanup between model sizes |

---

## B-3: Reliability and Robustness Scoring [Complexity: 13, Budget: 2]

**Applied:** h-e1 scorer integration

### API Signatures

```python
class GPT4ReliabilityScorer:
    def __init__(self, api_key: str):
        """Initialize GPT-4 reliability scorer."""
        self.api_key = api_key
    
    def score_response(self, question: str, answer: str) -> float:
        """Score single response. Returns: Binary score [0-1]"""
        ...
    
    def score_batch(self, qa_pairs: list[tuple[str, str]]) -> np.ndarray:
        """Score batch with rate limiting. Returns: [N] scores"""
        ...

class ParaphraseRobustnessScorer:
    def __init__(self, sbert_model_name: str = "all-MiniLM-L6-v2"):
        """Initialize paraphrase robustness scorer."""
        self.sbert_model = SentenceTransformer(sbert_model_name)
    
    def generate_paraphrase(self, text: str) -> str:
        """Generate paraphrase. Returns: Paraphrased text"""
        ...
    
    def compute_consistency(self, original: str, paraphrased: str) -> float:
        """Compute similarity. Returns: Cosine similarity [0-1]"""
        ...
    
    def score_batch(self, response_pairs: list[tuple[str, str]]) -> np.ndarray:
        """Score batch. Returns: [N] similarities"""
        ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | API Integration | Reuse h-e1 GPT-4 and SBERT patterns |
| L-3-2 | Batch Processing | Handle 2× samples (factual + misinfo) |

---

## B-4: Correlation Analysis Module [Complexity: 15, Budget: 2]

**Applied:** scipy.stats pearsonr with Fisher z-transform

### API Signatures

```python
class PearsonCorrelationAnalyzer:
    def __init__(self, alpha: float = 0.05):
        """Initialize correlation analyzer.
        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
    
    def compute_correlation(
        self, 
        reliability: np.ndarray, 
        robustness: np.ndarray
    ) -> dict:
        """Compute Pearson r with p-value.
        Args:
            reliability: [N] scores
            robustness: [N] scores
        Returns:
            {
                "r": float,
                "p_value": float,
                "n": int
            }
        """
        ...
    
    def fisher_z_confidence_interval(
        self, 
        r: float, 
        n: int, 
        confidence: float = 0.95
    ) -> tuple[float, float]:
        """Compute 95% CI via Fisher z-transform.
        Returns: (ci_lower, ci_upper)
        """
        ...
    
    def permutation_test(
        self, 
        reliability: np.ndarray, 
        robustness: np.ndarray, 
        n_permutations: int = 1000
    ) -> dict:
        """Permutation test for significance.
        Returns:
            {
                "null_distribution": np.ndarray,
                "p_value_perm": float,
                "observed_r": float
            }
        """
        ...
    
    def validate_gate(
        self, 
        correlation_result: dict, 
        threshold: float = 0.3, 
        ci_threshold: float = 0.2
    ) -> bool:
        """Validate MECHANISM gate. Returns: True if r>0.3, p<0.05, CI>0.2"""
        ...
```

### Pseudo-code

```
1. compute_correlation(reliability, robustness):
   a. from scipy.stats import pearsonr
   b. r, p_value = pearsonr(reliability, robustness)
   c. Return {"r": r, "p_value": p_value, "n": len(reliability)}

2. fisher_z_confidence_interval(r, n, confidence=0.95):
   a. z = np.arctanh(r)  # Fisher z-transform
   b. se = 1 / np.sqrt(n - 3)
   c. z_critical = 1.96  # For 95% CI
   d. ci = z + np.array([-z_critical, z_critical]) * se
   e. ci_lower, ci_upper = np.tanh(ci)  # Back-transform
   f. Return (ci_lower, ci_upper)

3. permutation_test(reliability, robustness, n_permutations):
   a. observed_r = pearsonr(reliability, robustness)[0]
   b. null_distribution = []
   c. For i in range(n_permutations):
      - shuffled = np.random.permutation(robustness)
      - null_r = pearsonr(reliability, shuffled)[0]
      - null_distribution.append(null_r)
   d. p_value_perm = (null_distribution >= observed_r).mean()
   e. Return {"null_distribution": null_distribution, "p_value_perm": p_value_perm}

4. validate_gate(correlation_result, threshold, ci_threshold):
   a. r = correlation_result["r"]
   b. p = correlation_result["p_value"]
   c. ci_lower = correlation_result.get("ci_lower", 0)
   d. Return (r > threshold) and (p < 0.05) and (ci_lower > ci_threshold)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Pearson Implementation | scipy.stats.pearsonr with Fisher CI |
| L-4-2 | Permutation Test | 1000 shuffles for null distribution |

---

## B-5: Stratification Analysis [Complexity: 12, Budget: 1]

**Applied:** Per-stratum correlation comparison

### API Signatures

```python
class StratificationAnalyzer:
    def __init__(self, correlation_analyzer: PearsonCorrelationAnalyzer):
        """Initialize stratification analyzer."""
        self.corr_analyzer = correlation_analyzer
    
    def analyze_factual_stratum(self, results_df: pd.DataFrame) -> dict:
        """Analyze factual stratum.
        Args:
            results_df: DataFrame with columns [reliability, robustness]
        Returns:
            {
                "r": float,
                "p_value": float,
                "ci_95": (float, float),
                "n": int
            }
        """
        ...
    
    def analyze_misinformation_stratum(self, results_df: pd.DataFrame) -> dict:
        """Analyze misinformation stratum. Returns: Same as analyze_factual_stratum"""
        ...
    
    def compare_strata(
        self, 
        factual_result: dict, 
        misinfo_result: dict
    ) -> dict:
        """Compare correlations across strata.
        Returns:
            {
                "factual_r": float,
                "misinfo_r": float,
                "difference": float,
                "effect_specific": bool  # True if factual_r > misinfo_r
            }
        """
        ...
    
    def validate_mechanism_hypothesis(self, factual_result: dict) -> bool:
        """Validate mechanism on factual stratum. Returns: Gate pass status"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Stratum Comparison | Factual vs misinformation r comparison |

---

## B-6: Statistical Validation [Complexity: 10, Budget: 0]

**Applied:** Gate validation logic

### API Signatures

```python
class StatisticalValidator:
    def __init__(self, config: dict):
        """Initialize validator with thresholds."""
        self.r_threshold = config.get("r_threshold", 0.3)
        self.p_threshold = config.get("p_threshold", 0.05)
        self.ci_threshold = config.get("ci_threshold", 0.2)
    
    def validate_mechanism_gate(self, factual_result: dict) -> dict:
        """Validate MECHANISM gate.
        Returns:
            {
                "gate_passed": bool,
                "observed_r": float,
                "p_value": float,
                "ci_lower": float,
                "checks": {
                    "r_check": bool,
                    "p_check": bool,
                    "ci_check": bool
                }
            }
        """
        ...
    
    def aggregate_model_results(self, results_by_model: list[dict]) -> dict:
        """Aggregate results across model sizes. Returns: Summary statistics"""
        ...
```

---

## B-7: Visualization Suite [Complexity: 14, Budget: 1]

**Applied:** matplotlib/seaborn publication-quality figures

### API Signatures

```python
class CorrelationVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer."""
        self.output_dir = output_dir
    
    def plot_gate_metrics_comparison(
        self, 
        observed_r: float, 
        threshold: float = 0.3
    ) -> None:
        """MANDATORY: Bar chart comparing observed r vs threshold."""
        ...
    
    def plot_scatter_with_regression(
        self, 
        reliability: np.ndarray, 
        robustness: np.ndarray, 
        r: float, 
        p_value: float, 
        ci: tuple[float, float]
    ) -> None:
        """Scatter plot with regression line and statistics."""
        ...
    
    def plot_model_comparison(self, correlations_by_model: dict) -> None:
        """Bar chart of r values across model sizes."""
        ...
    
    def plot_permutation_test(
        self, 
        observed_r: float, 
        null_distribution: np.ndarray
    ) -> None:
        """Histogram of null distribution with observed r line."""
        ...
    
    def plot_confidence_intervals(self, correlations_by_model: dict) -> None:
        """Forest plot with r ± 95% CI."""
        ...
    
    def plot_stratification_comparison(
        self, 
        factual_r: float, 
        misinfo_r: float
    ) -> None:
        """Bar chart comparing factual vs misinformation r."""
        ...
    
    def generate_all_figures(self, results: dict) -> None:
        """Generate all 6 figures."""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Figure Generation | 6 publication-quality plots with seaborn |

---

## B-8: Results Management [Complexity: 8, Budget: 0]

**Applied:** JSON/CSV export pattern

### API Signatures

```python
class ResultsManager:
    def __init__(self, output_dir: str):
        """Initialize results manager."""
        self.output_dir = output_dir
    
    def save_correlation_results(self, results: dict) -> None:
        """Save correlation results to JSON."""
        ...
    
    def save_evaluation_results(self, results_df: pd.DataFrame) -> None:
        """Save evaluation results to CSV. results_df: [N, 5+]"""
        ...
    
    def save_gate_validation(self, validation_result: dict) -> None:
        """Save gate validation report."""
        ...
    
    def generate_validation_report(self, all_results: dict) -> None:
        """Generate 04_validation.md report."""
        ...
```

---

## Configuration Schema

```python
from dataclasses import dataclass

@dataclass
class CorrelationConfig:
    alpha: float = 0.05
    correlation_threshold: float = 0.3
    ci_lower_threshold: float = 0.2
    n_permutations: int = 1000
    confidence_level: float = 0.95

@dataclass
class ExperimentConfig:
    model_sizes: list[str] = field(default_factory=lambda: ["7b", "13b", "70b"])
    generation_params: dict = field(default_factory=lambda: {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 256
    })
    stratification_enabled: bool = True
    output_dir: str = "h-m1/outputs"
    figures_dir: str = "h-m1/figures"
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)

def load_config() -> ExperimentConfig:
    """Load configuration from environment or defaults."""
    ...
```

---

## Main Orchestration Logic

```python
def main():
    config = load_config()
    
    # Load and stratify dataset
    loader = StratifiedTruthfulQALoader()
    factual_prompts = loader.get_factual_stratum()
    misinfo_prompts = loader.get_misinformation_stratum()
    
    all_results = []
    
    # Process each model size
    for model_size in config.model_sizes:
        # Generate responses
        generator = LlamaResponseGenerator(model_size)
        generator.load_model()
        factual_responses = generator.generate_batch(factual_prompts)
        misinfo_responses = generator.generate_batch(misinfo_prompts)
        
        # Score dimensions
        rel_scorer = GPT4ReliabilityScorer(os.getenv("OPENAI_API_KEY"))
        rob_scorer = ParaphraseRobustnessScorer("all-MiniLM-L6-v2")
        
        factual_reliability = rel_scorer.score_batch(
            [(r["prompt"], r["response"]) for r in factual_responses]
        )
        factual_robustness = rob_scorer.score_batch(
            [(r["response"], r["response"]) for r in factual_responses]
        )
        
        misinfo_reliability = rel_scorer.score_batch(
            [(r["prompt"], r["response"]) for r in misinfo_responses]
        )
        misinfo_robustness = rob_scorer.score_batch(
            [(r["response"], r["response"]) for r in misinfo_responses]
        )
        
        # Analyze correlations
        corr_analyzer = PearsonCorrelationAnalyzer(alpha=0.05)
        strat_analyzer = StratificationAnalyzer(corr_analyzer)
        
        factual_result = strat_analyzer.analyze_factual_stratum(
            pd.DataFrame({
                "reliability": factual_reliability, 
                "robustness": factual_robustness
            })
        )
        misinfo_result = strat_analyzer.analyze_misinformation_stratum(
            pd.DataFrame({
                "reliability": misinfo_reliability, 
                "robustness": misinfo_robustness
            })
        )
        
        comparison = strat_analyzer.compare_strata(factual_result, misinfo_result)
        
        all_results.append({
            "model_size": model_size,
            "factual": factual_result,
            "misinformation": misinfo_result,
            "comparison": comparison
        })
        
        generator.cleanup()
    
    # Validate MECHANISM gate
    gate_passed = all(
        strat_analyzer.validate_mechanism_hypothesis(r["factual"]) 
        for r in all_results
    )
    
    # Visualize results
    visualizer = CorrelationVisualizer(config.figures_dir)
    visualizer.generate_all_figures({
        "results_by_model": all_results,
        "gate_passed": gate_passed
    })
    
    # Save results
    results_manager = ResultsManager(config.output_dir)
    results_manager.save_correlation_results(all_results)
    results_manager.generate_validation_report({"gate_passed": gate_passed})
    
    return 0 if gate_passed else 1
```

---

## Implementation Notes

### Critical Success Factors

1. **Reuse h-e1 scorers**: Directly reuse GPT-4 and SBERT scoring patterns
2. **Stratification validation**: Ensure ~400 samples per stratum
3. **Fisher z-transform**: Correct implementation for CI computation
4. **Permutation test**: 1000 shuffles for robust null distribution

### Error Handling Priorities

1. **API Failures**: Exponential backoff for GPT-4 calls
2. **Stratification Errors**: Validate category mappings
3. **Missing Data**: Ensure complete scoring before correlation

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Subtask Budget Used:** 10/10 (B-1:2, B-2:2, B-3:2, B-4:2, B-5:1, B-7:1)
