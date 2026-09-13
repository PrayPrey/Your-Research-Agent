# Logic Design: h-e1
**Hypothesis:** Reformulation rate decrease AND diversity correlation exist in HH-RLHF conversations with ≥5 turns
**Type:** EXISTENCE (LIGHT tier)
**Date:** 2026-08-25
**Subtask Budget:** 3 subtasks

---

## Codebase Analysis (Serena)

*Serena MCP not available - proceeding with green-field design*

**Analysis Type:** Green-field (no existing codebase)
**Base Hypothesis:** None (FOUNDATION hypothesis)

---

## Applied Patterns

**Applied:** Measurement Experiment API Pattern (manual reference)
- Detector pattern: binary classification per sample
- Aggregator pattern: slope computation via regression
- Statistical validator: hypothesis testing

**Applied:** Pipeline API Design
- ETL → Transform → Validate flow
- Stateless functional APIs

---

## API Specifications

### Module 1: Data Loading (`data/loader.py`)

#### `load_hh_rlhf`
```python
def load_hh_rlhf(dataset_name: str = "Anthropic/hh-rlhf") -> Dataset:
    """
    Load HH-RLHF dataset from Hugging Face.
    
    Args:
        dataset_name: HuggingFace dataset identifier
    
    Returns:
        Dataset: Raw HH-RLHF dataset (train + test splits)
    """
```

#### `filter_by_turn_count`
```python
def filter_by_turn_count(
    dataset: Dataset,
    min_turns: int = 5
) -> Dataset:
    """
    Filter conversations by minimum turn count.
    
    Args:
        dataset: Raw HH-RLHF dataset
        min_turns: Minimum number of turns required
    
    Returns:
        Filtered dataset with conversations >= min_turns
    """
```

### Module 2: Data Preprocessing (`data/preprocessor.py`)

#### `parse_conversation`
```python
def parse_conversation(raw: Dict[str, Any]) -> Conversation:
    """
    Parse raw HH-RLHF conversation into structured format.
    
    Args:
        raw: Raw conversation dict from dataset
            {
                "chosen": str (full conversation text),
                "rejected": str,
                "helpfulness": float,
                ...
            }
    
    Returns:
        Conversation object with parsed turns
    """
```

#### `extract_turns`
```python
def extract_turns(conversation_text: str) -> List[Turn]:
    """
    Extract user/AI turn pairs from conversation text.
    
    HH-RLHF format: "Human: <text>\n\nAssistant: <text>\n\n..."
    
    Args:
        conversation_text: Raw conversation string
    
    Returns:
        List of Turn objects with turn_index, user_query, ai_response
    """
```

### Module 3: Reformulation Analysis (`analysis/reformulation.py`)

#### `detect_reformulation`
```python
def detect_reformulation(
    query_t: str,
    query_t1: str,
    sbert_model: SentenceTransformer,
    threshold_semantic: float = 0.7,
    threshold_syntactic: float = 0.3
) -> bool:
    """
    Detect if query_t1 is a reformulation of query_t.
    
    Algorithm:
        1. Compute semantic similarity via SBERT embeddings
        2. Compute normalized edit distance (syntactic change)
        3. Reformulation = (semantic_sim > threshold_sem) AND (norm_edit > threshold_syn)
    
    Args:
        query_t: Query at turn t
        query_t1: Query at turn t+1
        sbert_model: Pre-loaded SentenceTransformer model
        threshold_semantic: Min cosine similarity for semantic match
        threshold_syntactic: Min normalized edit distance for syntactic change
    
    Returns:
        True if reformulation detected, False otherwise
    
    Tensor Shapes:
        emb_t: [768] (SBERT all-MiniLM-L6-v2 embedding dim)
        emb_t1: [768]
        semantic_sim: scalar ∈ [-1, 1]
        norm_edit: scalar ∈ [0, 1]
    """
```

##### Subtask 3.1: Semantic Similarity Computation
```python
def compute_semantic_similarity(
    q1: str,
    q2: str,
    sbert_model: SentenceTransformer
) -> float:
    """
    Compute cosine similarity between SBERT embeddings.
    
    Args:
        q1, q2: Query strings
        sbert_model: Pre-loaded SBERT model
    
    Returns:
        Cosine similarity ∈ [-1, 1]
    
    Tensor Shapes:
        emb1: [768]
        emb2: [768]
        sim: scalar
    """
```

##### Subtask 3.2: Syntactic Distance Computation
```python
def compute_syntactic_distance(q1: str, q2: str) -> float:
    """
    Compute normalized Levenshtein edit distance.
    
    Args:
        q1, q2: Query strings
    
    Returns:
        Normalized edit distance ∈ [0, 1]
        (0 = identical, 1 = completely different)
    
    Formula:
        norm_edit = Levenshtein(q1, q2) / max(len(q1), len(q2))
    """
```

#### `compute_reformulation_slope`
```python
def compute_reformulation_slope(
    queries: List[str],
    sbert_model: SentenceTransformer,
    threshold_semantic: float = 0.7,
    threshold_syntactic: float = 0.3
) -> float:
    """
    Compute reformulation rate decline slope via linear regression.
    
    Algorithm:
        1. For each consecutive pair (q_i, q_{i+1}), detect reformulation
        2. Create binary reformulation rates: [0 or 1] per turn
        3. Fit linear regression: rate ~ turn_index
        4. Return slope coefficient
    
    Args:
        queries: List of query strings in turn order
        sbert_model: Pre-loaded SBERT model
        threshold_semantic: Semantic similarity threshold
        threshold_syntactic: Syntactic distance threshold
    
    Returns:
        Slope coefficient (negative = reformulation rate decreasing)
    
    Tensor Shapes:
        reformulation_rates: [T-1] where T = len(queries)
        turn_indices: [T-1]
        slope: scalar
    """
```

##### Subtask 3.3: Slope Regression
```python
def fit_slope(
    reformulation_rates: np.ndarray,
    turn_indices: np.ndarray
) -> Tuple[float, float, float]:
    """
    Fit linear regression: rate ~ turn_index.
    
    Args:
        reformulation_rates: Binary rates [T-1]
        turn_indices: [0, 1, 2, ..., T-2]
    
    Returns:
        (slope, intercept, r_squared)
    
    Uses: scipy.stats.linregress
    """
```

### Module 4: Diversity Analysis (`analysis/diversity.py`)

#### `compute_diversity`
```python
def compute_diversity(texts: List[str]) -> float:
    """
    Compute distinct-1 (lexical diversity).
    
    Args:
        texts: List of strings (queries or responses)
    
    Returns:
        Diversity score ∈ [0, 1]
        (distinct_tokens / total_tokens)
    
    Algorithm:
        1. Tokenize all texts (whitespace split)
        2. Count total tokens
        3. Count distinct tokens (set)
        4. Return distinct / total
    """
```

### Module 5: Statistical Validation (`analysis/statistics.py`)

#### `test_slope_significance`
```python
def test_slope_significance(
    slopes: np.ndarray,
    baseline_mean: float = 0.0,
    alpha: float = 0.05
) -> Dict[str, float]:
    """
    Test if slopes are significantly < baseline_mean.
    
    H0: mean(slopes) >= baseline_mean
    H1: mean(slopes) < baseline_mean (one-tailed)
    
    Args:
        slopes: Array of slope coefficients (one per conversation)
        baseline_mean: Expected mean under H0 (default 0 for no learning)
        alpha: Significance level
    
    Returns:
        {
            "t_statistic": float,
            "p_value": float,
            "mean_slope": float,
            "std_slope": float,
            "significant": bool (p < alpha)
        }
    
    Uses: scipy.stats.ttest_1samp (one-sample t-test)
    """
```

#### `compute_effect_size`
```python
def compute_effect_size(
    slopes: np.ndarray,
    baseline_mean: float = 0.0
) -> float:
    """
    Compute Cohen's d effect size.
    
    Args:
        slopes: Observed slope distribution
        baseline_mean: Baseline value (null hypothesis mean)
    
    Returns:
        Cohen's d = (mean(slopes) - baseline_mean) / std(slopes)
    
    Interpretation:
        d < 0.2: negligible
        0.2 ≤ d < 0.5: small
        0.5 ≤ d < 0.8: medium
        d ≥ 0.8: large
    """
```

### Module 6: Visualization (`visualization/plots.py`)

#### `plot_gate_metrics`
```python
def plot_gate_metrics(
    actual_slope: float,
    target_slope: float = 0.0,
    output_path: str = "figures/gate_metrics.png"
) -> None:
    """
    Generate required gate metric comparison (bar chart).
    
    Args:
        actual_slope: Measured reformulation slope
        target_slope: Gate criterion (< 0 for EXISTENCE check)
        output_path: Save path for figure
    
    Visual:
        Bar chart with two bars: [Target, Actual]
        Horizontal line at y=0 for reference
        Color: green if actual < target, red otherwise
    """
```

#### `plot_reformulation_over_turns`
```python
def plot_reformulation_over_turns(
    conversations: List[Conversation],
    sbert_model: SentenceTransformer,
    output_path: str = "figures/reformulation_over_turns.png"
) -> None:
    """
    Plot average reformulation rate vs turn index.
    
    Args:
        conversations: List of Conversation objects
        sbert_model: SBERT model for reformulation detection
        output_path: Save path
    
    Visual:
        Line plot: x=turn_index, y=avg_reformulation_rate
        Shows decline if hypothesis holds
    """
```

### Module 7: Orchestration (`main.py`)

#### `run_experiment`
```python
def run_experiment(config: ExperimentConfig) -> ExperimentResults:
    """
    End-to-end pipeline execution.
    
    Args:
        config: ExperimentConfig instance
    
    Returns:
        ExperimentResults with:
            - slope_mean: float
            - slope_std: float
            - p_value: float
            - effect_size: float
            - gate_passed: bool
            - figure_paths: Dict[str, str]
    
    Pipeline:
        1. Load + filter dataset
        2. Parse conversations
        3. Compute slopes for all conversations
        4. Statistical validation
        5. Generate visualizations
        6. Return results
    """
```

---

## Tensor Shape Reference

| Variable | Shape | Description |
|----------|-------|-------------|
| `sbert_embedding` | `[768]` | SBERT all-MiniLM-L6-v2 output |
| `reformulation_rates` | `[T-1]` | Binary rates per turn (T = turn count) |
| `slopes` | `[N]` | Slope per conversation (N = conversation count) |
| `turn_indices` | `[T-1]` | Turn position indices |

---

## Pseudo-code Flow

```python
# Main Pipeline
def run_experiment(config):
    # 1. ETL
    dataset = load_hh_rlhf()
    filtered = filter_by_turn_count(dataset, config.min_turns)
    conversations = [parse_conversation(row) for row in filtered]
    
    # 2. Load SBERT
    sbert_model = SentenceTransformer(config.sbert_model_name)
    
    # 3. Compute slopes
    slopes = []
    for conv in conversations:
        queries = [turn.user_query for turn in conv.turns]
        slope = compute_reformulation_slope(queries, sbert_model)
        slopes.append(slope)
    
    # 4. Statistical validation
    stats = test_slope_significance(np.array(slopes))
    effect = compute_effect_size(np.array(slopes))
    
    # 5. Gate check
    gate_passed = stats["mean_slope"] < 0
    
    # 6. Visualization
    plot_gate_metrics(stats["mean_slope"])
    plot_reformulation_over_turns(conversations, sbert_model)
    # ... other plots ...
    
    return ExperimentResults(
        slope_mean=stats["mean_slope"],
        p_value=stats["p_value"],
        effect_size=effect,
        gate_passed=gate_passed
    )
```

---

## External Dependencies

None (FOUNDATION hypothesis - no base code)

---

## Subtask Summary

**Total Subtasks:** 3 (within budget)

1. **Subtask 3.1:** Semantic similarity computation (SBERT)
2. **Subtask 3.2:** Syntactic distance computation (Levenshtein)
3. **Subtask 3.3:** Slope regression (linear fit)

---

**Logic Status:** Complete
**Next:** Configuration Design (03_config.md)
