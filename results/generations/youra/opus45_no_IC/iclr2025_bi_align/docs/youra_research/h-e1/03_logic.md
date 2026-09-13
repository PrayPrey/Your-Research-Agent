# Logic: H-E1 (Accommodation Patterns Detectable in LMSYS-Chat-1M)

**Type:** EXISTENCE (PoC) | DeBERTa formality scoring + statistical analysis.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## Data Flow

```
load_dataset_lmsys() -> Dataset
  -> filter_by_turns(min_turns=2)
  -> filter_english()
  -> filter_not_redacted()
  -> extract_turn_pairs(conv) per conversation -> list[(human_text, ai_text)]
  -> FormalityAccommodationAnalyzer.score_batch(texts) -> formality scores
  -> compute_accommodation_delta per pair -> observed_deltas
  -> create_shuffled_baseline(human, ai) -> shuffled_ai
  -> compute_shuffled_deltas -> shuffled_deltas
  -> compute_cohens_d(observed, shuffled) -> d
  -> compute_welch_ttest(observed, shuffled) -> (t_stat, p_value)
  -> check_gate(coverage, d, p) -> bool
  -> plot_delta_histogram / plot_gate_metrics
```

---

## data.py

**Applied:** Standard HuggingFace `datasets` loading.

```python
from datasets import load_dataset

def load_dataset_lmsys() -> Dataset:
    """Load LMSYS-Chat-1M from HuggingFace (requires license acceptance)."""
    return load_dataset("lmsys/lmsys-chat-1m", split="train")

def filter_by_turns(dataset: Dataset, min_turns: int = 2) -> Dataset:
    """Keep conversations with >= min_turns per role (user AND assistant)."""
    def has_sufficient_turns(example):
        conv = example['conversation']
        user_turns = sum(1 for t in conv if t['role'] == 'user')
        ai_turns = sum(1 for t in conv if t['role'] == 'assistant')
        return user_turns >= min_turns and ai_turns >= min_turns
    return dataset.filter(has_sufficient_turns)

def filter_english(dataset: Dataset) -> Dataset:
    """Keep conversations where language == 'English'."""
    return dataset.filter(lambda x: x.get('language') == 'English')

def filter_not_redacted(dataset: Dataset) -> Dataset:
    """Remove redacted conversations."""
    return dataset.filter(lambda x: not x.get('redacted', False))

def extract_turn_pairs(conversation: list[dict]) -> list[tuple[str, str]]:
    """Extract (human, ai) turn pairs preserving order."""
    human_turns = [t['content'] for t in conversation if t['role'] == 'user']
    ai_turns = [t['content'] for t in conversation if t['role'] == 'assistant']
    return list(zip(human_turns, ai_turns))
```

---

## E3: Formality Scoring [Complexity: 8]

**Applied:** DeBERTa-large formality ranker via HuggingFace Transformers per 02c_experiment_brief.

### API Signatures

```python
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class FormalityAccommodationAnalyzer:
    def __init__(self, model_name: str = "s-nlp/deberta-large-formality-ranker", device: str = "cuda"):
        """Load DeBERTa formality model."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()
        self.device = device

    def score_formality(self, text: str) -> float:
        """Get formality score (0-1, higher = more formal)."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            return probs[0, 1].item()  # index 1 = formal class

    def score_batch(self, texts: list[str], batch_size: int = 32) -> list[float]:
        """Batch scoring for efficiency."""
        scores = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(batch, return_tensors="pt", truncation=True, 
                                   max_length=512, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)
                scores.extend(probs[:, 1].cpu().tolist())
        return scores

    def compute_accommodation_delta(self, human_text: str, ai_text: str) -> float:
        """Compute formality delta (lower = more accommodation)."""
        h_formality = self.score_formality(human_text)
        ai_formality = self.score_formality(ai_text)
        return abs(ai_formality - h_formality)
```

### Edge Cases
- Empty text: return 0.5 (neutral formality)
- Text > 512 tokens: truncated by tokenizer
- Batch with variable lengths: padded

---

## E4: Accommodation Delta [Complexity: 4]

```python
def compute_all_deltas(analyzer: FormalityAccommodationAnalyzer, 
                       turn_pairs: list[tuple[str, str]]) -> np.ndarray:
    """Compute |AI - Human| formality for all turn pairs."""
    human_texts = [p[0] for p in turn_pairs]
    ai_texts = [p[1] for p in turn_pairs]
    
    human_scores = np.array(analyzer.score_batch(human_texts))
    ai_scores = np.array(analyzer.score_batch(ai_texts))
    
    deltas = np.abs(ai_scores - human_scores)
    return deltas, human_scores, ai_scores
```

---

## E5: Shuffled Baseline [Complexity: 4]

**Applied:** NumPy random permutation per 02c_experiment_brief.

```python
import numpy as np

def create_shuffled_baseline(human_formality: np.ndarray, ai_formality: np.ndarray, 
                            seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Shuffle AI formality to destroy real pairing."""
    rng = np.random.default_rng(seed)
    shuffled_ai = rng.permutation(ai_formality)
    return human_formality, shuffled_ai

def compute_shuffled_deltas(human_formality: np.ndarray, shuffled_ai: np.ndarray) -> np.ndarray:
    """Compute deltas from shuffled pairs."""
    return np.abs(shuffled_ai - human_formality)
```

---

## E6: Statistical Analysis [Complexity: 5]

**Applied:** scipy.stats for Cohen's d and Welch's t-test per 02c_experiment_brief.

```python
from scipy import stats

def compute_cohens_d(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray) -> float:
    """
    Effect size: positive d = observed < shuffled (accommodation exists).
    Formula: (mean_shuffled - mean_observed) / pooled_std
    """
    pooled_std = np.sqrt((np.var(observed_deltas) + np.var(shuffled_deltas)) / 2)
    if pooled_std == 0:
        return 0.0
    d = (np.mean(shuffled_deltas) - np.mean(observed_deltas)) / pooled_std
    return d

def compute_welch_ttest(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray) -> tuple[float, float]:
    """Welch's t-test for unequal variances."""
    t_stat, p_value = stats.ttest_ind(shuffled_deltas, observed_deltas, equal_var=False)
    return t_stat, p_value

def check_gate(coverage: float, cohens_d: float, p_value: float) -> bool:
    """
    Gate condition per PRD:
    - Coverage >= 50%
    - Cohen's d > 0.3
    - p-value < 0.001
    """
    return coverage >= 0.50 and cohens_d > 0.30 and p_value < 0.001

def generate_statistics(observed_deltas: np.ndarray, shuffled_deltas: np.ndarray, 
                       coverage: float) -> dict:
    """Generate full statistics report."""
    cohens_d = compute_cohens_d(observed_deltas, shuffled_deltas)
    t_stat, p_value = compute_welch_ttest(observed_deltas, shuffled_deltas)
    
    return {
        'coverage': coverage,
        'n_observations': len(observed_deltas),
        'mean_observed': float(np.mean(observed_deltas)),
        'mean_shuffled': float(np.mean(shuffled_deltas)),
        'std_observed': float(np.std(observed_deltas)),
        'std_shuffled': float(np.std(shuffled_deltas)),
        'cohens_d': cohens_d,
        't_statistic': t_stat,
        'p_value': p_value,
        'gate_pass': check_gate(coverage, cohens_d, p_value)
    }
```

---

## E7: Visualization [Complexity: 5]

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_delta_histogram(observed: np.ndarray, shuffled: np.ndarray, save_path: str) -> None:
    """Overlay histogram: observed vs shuffled deltas."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(observed, bins=50, alpha=0.5, label=f'Observed (mean={np.mean(observed):.3f})', density=True)
    ax.hist(shuffled, bins=50, alpha=0.5, label=f'Shuffled (mean={np.mean(shuffled):.3f})', density=True)
    ax.set_xlabel('Formality Delta |AI - Human|')
    ax.set_ylabel('Density')
    ax.set_title('Formality Accommodation: Observed vs Shuffled Baseline')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_gate_metrics(stats: dict, save_path: str) -> None:
    """Bar chart: target vs actual for coverage and Cohen's d."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    
    # Coverage
    axes[0].bar(['Target', 'Actual'], [0.50, stats['coverage']], color=['gray', 'blue'])
    axes[0].set_ylabel('Coverage')
    axes[0].set_title('Coverage Gate')
    axes[0].axhline(y=0.50, color='r', linestyle='--', label='Threshold')
    
    # Cohen's d
    axes[1].bar(['Target', 'Actual'], [0.30, stats['cohens_d']], color=['gray', 'green'])
    axes[1].set_ylabel("Cohen's d")
    axes[1].set_title("Effect Size Gate")
    axes[1].axhline(y=0.30, color='r', linestyle='--', label='Threshold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
```

---

## E8: Run Experiment [Complexity: 5]

```python
def main() -> dict:
    """Orchestrate full H-E1 experiment."""
    from config import *
    
    # Load and filter
    print("Loading LMSYS-Chat-1M...")
    dataset = load_dataset_lmsys()
    total_before = len(dataset)
    
    dataset = filter_by_turns(dataset, MIN_TURNS_PER_SIDE)
    dataset = filter_english(dataset)
    dataset = filter_not_redacted(dataset)
    total_after = len(dataset)
    
    coverage = total_after / total_before
    print(f"Coverage: {coverage:.2%} ({total_after:,}/{total_before:,})")
    
    # Extract turn pairs
    print("Extracting turn pairs...")
    all_turn_pairs = []
    for example in dataset:
        pairs = extract_turn_pairs(example['conversation'])
        all_turn_pairs.extend(pairs)
    
    # Score formality
    print(f"Scoring {len(all_turn_pairs):,} turn pairs...")
    analyzer = FormalityAccommodationAnalyzer(MODEL_NAME, DEVICE)
    observed_deltas, human_scores, ai_scores = compute_all_deltas(analyzer, all_turn_pairs)
    
    # Shuffled baseline
    print("Computing shuffled baseline...")
    _, shuffled_ai = create_shuffled_baseline(human_scores, ai_scores, SEED)
    shuffled_deltas = compute_shuffled_deltas(human_scores, shuffled_ai)
    
    # Statistics
    stats = generate_statistics(observed_deltas, shuffled_deltas, coverage)
    
    # Visualizations
    print("Generating figures...")
    os.makedirs('h-e1/figures', exist_ok=True)
    plot_delta_histogram(observed_deltas, shuffled_deltas, 'h-e1/figures/delta_histogram.png')
    plot_gate_metrics(stats, 'h-e1/figures/gate_metrics.png')
    
    # Report
    print("\n=== H-E1 RESULTS ===")
    print(f"Coverage: {stats['coverage']:.2%}")
    print(f"Mean observed delta: {stats['mean_observed']:.4f}")
    print(f"Mean shuffled delta: {stats['mean_shuffled']:.4f}")
    print(f"Cohen's d: {stats['cohens_d']:.4f}")
    print(f"p-value: {stats['p_value']:.2e}")
    print(f"GATE PASS: {stats['gate_pass']}")
    
    # Save results
    import json
    with open('h-e1/experiment_results.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats
```

---

## Tensor/Value Shapes

| Variable | Type | Shape/Range |
|----------|------|-------------|
| formality_score | float | [0.0, 1.0] |
| delta | float | [0.0, 1.0] |
| observed_deltas | np.ndarray | (n_pairs,) |
| shuffled_deltas | np.ndarray | (n_pairs,) |
| cohens_d | float | typically [-1, +3] |
| p_value | float | [0, 1] |
