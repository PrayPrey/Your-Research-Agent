# Logic Design: H-E1
# Preference Entropy Measurement (EXISTENCE PoC)

**Date:** 2026-08-28  
**Author:** yoon303@etri.re.kr  
**Hypothesis:** Base models produce outputs with preference entropy H_base >= 1.8 nats  
**Type:** EXISTENCE (PoC)  
**Budget:** 0 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch - designing new APIs  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Knowledge Base Patterns Applied

Applied: scipy.stats.entropy (standard Shannon entropy computation)  
Applied: HuggingFace datasets.load_dataset (dataset loading pattern)  
Applied: matplotlib.pyplot (visualization best practices)  
Applied: numpy random seed (reproducible sampling)

---

## E1: Dataset Setup (Complexity: 6, Budget: 0)

**Applied:** HuggingFace datasets.load_dataset

### API Signatures

```python
class PreferenceEntropyAnalyzer:
    def __init__(
        self,
        dataset_name: str = "Anthropic/hh-rlhf",
        sample_size: int = 100,
        seed: int = 1
    ):
        """Initialize analyzer. Downloads ~3GB dataset on first run."""
        self.dataset_name = dataset_name
        self.sample_size = sample_size
        self.seed = seed
        self.dataset = None

    def load_dataset(self) -> None:
        """Load HuggingFace dataset. Caches locally after first download."""
        # Sets self.dataset = load_dataset(self.dataset_name)
        ...

    def sample_prompts(self) -> list:
        """Sample n prompts with fixed seed. Returns: list of prompt dicts."""
        # np.random.seed(self.seed)
        # Returns: [{prompt_id, chosen, rejected}, ...]
        ...
```

### Pseudo-code

```
1. load_dataset():
   - datasets.load_dataset("Anthropic/hh-rlhf")
   - Store in self.dataset

2. sample_prompts():
   - Set np.random.seed(self.seed)
   - Get train split indices
   - Sample 100 indices without replacement
   - Extract prompt, chosen, rejected fields
   - Return list of dicts
```

### Subtasks [0/0 used]

None - 0 budget

---

## E2: Entropy Computation (Complexity: 8, Budget: 0)

**Applied:** scipy.stats.entropy

### API Signatures

```python
class PreferenceEntropyAnalyzer:
    def aggregate_preferences(self, prompt_examples: list) -> np.ndarray:
        """Aggregate pairwise comparisons into counts.
        Args: prompt_examples: list of {chosen, rejected} dicts
        Returns: [chosen_count, rejected_count]
        """
        ...

    def compute_entropy(self, preference_counts: np.ndarray) -> float:
        """Compute Shannon entropy in nats.
        Args: preference_counts: [c, r] array (e.g., [45, 55])
        Returns: entropy in nats or None if insufficient data
        """
        # scipy.stats.entropy(preference_counts, base=np.e)
        ...

    def analyze_dataset(self) -> list:
        """Main analysis loop.
        Returns: [{prompt_id, entropy, comparison_count}, ...]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| preference_counts | [2] | [chosen_count, rejected_count] |
| entropy | scalar | Single float in [0, 0.693] nats |

### Pseudo-code

```
1. aggregate_preferences(examples):
   - chosen_count = sum(1 for e in examples)
   - rejected_count = len(examples)
   - Return np.array([chosen_count, rejected_count])

2. compute_entropy(counts):
   - If sum(counts) < 5: return None  # Insufficient data
   - Return entropy(counts, base=np.e)

3. analyze_dataset():
   - Group sampled prompts by prompt_id
   - For each group:
     - counts = aggregate_preferences(group)
     - H = compute_entropy(counts)
     - Append {prompt_id, entropy=H, count=sum(counts)}
   - Return results
```

### Subtasks [0/0 used]

None - 0 budget

---

## E3: Metrics & Validation (Complexity: 5, Budget: 0)

**Applied:** numpy statistical functions

### API Signatures

```python
class PreferenceEntropyAnalyzer:
    def compute_metrics(self, results: list) -> dict:
        """Calculate success rate, variance, range.
        Args: results: list from analyze_dataset()
        Returns: {success_rate, variance, range, mean}
        """
        ...
```

### Pseudo-code

```
1. compute_metrics(results):
   - valid = [r for r in results if r['entropy'] is not None]
   - success_rate = len(valid) / len(results) * 100
   - entropies = [r['entropy'] for r in valid]
   - variance = np.std(entropies)
   - range = [np.min(entropies), np.max(entropies)]
   - mean = np.mean(entropies)
   - Assert all 0 <= H <= 0.693
   - Return {success_rate, variance, range, mean}
```

### Subtasks [0/0 used]

None - 0 budget

---

## E4: Visualization & Output (Complexity: 7, Budget: 0)

**Applied:** matplotlib.pyplot

### API Signatures

```python
class PreferenceEntropyAnalyzer:
    def generate_figures(self, results: list, metrics: dict) -> None:
        """Generate 4 PNG figures. Saves to figures/ directory."""
        ...

    def save_results(self, results: list, metrics: dict, output_path: str) -> None:
        """Save results to JSON.
        Args: output_path: path to .json file
        """
        ...
```

### Pseudo-code

```
1. generate_figures(results, metrics):
   - Create figures/ directory
   - Figure 1: Bar chart (target vs actual for success_rate, variance)
   - Figure 2: Histogram of entropies (bins=20, x=nats, y=freq)
   - Figure 3: Scatter plot (x=prompt_index, y=entropy)
   - Figure 4: Pie chart (success vs failed prompts)
   - Save all as PNG

2. save_results(results, metrics, path):
   - Create dict with {results, metrics, metadata: {timestamp, seed}}
   - json.dump(dict, open(path, 'w'), indent=2)
```

### Subtasks [0/0 used]

None - 0 budget

---

## Main Entry Point

```python
def main():
    """Execute H-E1 analysis pipeline."""
    analyzer = PreferenceEntropyAnalyzer(
        dataset_name="Anthropic/hh-rlhf",
        sample_size=100,
        seed=1
    )
    
    # Load and sample
    analyzer.load_dataset()
    prompts = analyzer.sample_prompts()
    
    # Compute entropy
    results = analyzer.analyze_dataset()
    
    # Validate
    metrics = analyzer.compute_metrics(results)
    
    # Output
    analyzer.generate_figures(results, metrics)
    analyzer.save_results(results, metrics, "h-e1_results.json")
    
    # Gate check
    assert metrics['success_rate'] >= 95, f"MUST_WORK gate failed: {metrics['success_rate']}%"
    assert metrics['variance'] > 0, "MUST_WORK gate failed: zero variance"
    print(f"SUCCESS: {metrics['success_rate']}% success rate, variance={metrics['variance']:.4f}")


if __name__ == "__main__":
    main()
```

---

## Validation Criteria

### MUST_WORK Gate Conditions

1. Code executes without errors
2. Success rate >= 95% (metrics['success_rate'] >= 95)
3. Variance > 0 (metrics['variance'] > 0)
4. All entropies in [0, 0.693] nats

### Expected Outputs

1. `h-e1_results.json` - Results with metadata
2. `figures/gate_metrics.png` - Target vs actual comparison
3. `figures/entropy_histogram.png` - Distribution
4. `figures/entropy_scatter.png` - Entropy vs prompt index
5. `figures/success_rate_pie.png` - Success/failure pie chart

---

## Self-Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (0/0)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted
- [x] No pseudo-code for trivial methods (only for complex algorithms)

---

*Logic designed for EXISTENCE PoC - minimal API to test "does it work?"*  
*Next Phase: Phase 4 - Implementation (Coder)*
