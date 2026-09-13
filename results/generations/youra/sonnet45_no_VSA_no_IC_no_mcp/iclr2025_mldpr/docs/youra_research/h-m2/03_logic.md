# Logic Document: h-m2

**Date:** 2026-08-24
**Hypothesis:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy
**Phase:** 3 - Implementation Planning
**Author:** Phase 3 Planning

---

## API Signatures

### C1: Context Inference Module

```python
def infer_context(user_modules: List[str]) -> Tuple[str, float]:
    """
    Infer user task context from Python import history.
    
    Args:
        user_modules: Loaded module names from sys.modules
        
    Returns:
        context: Task type ("classification", "pretraining", "robustness", "unknown")
        confidence: Pattern match confidence (0.0-1.0)
    """
    pass
```

### C2: Graph Construction Module

```python
def build_graph(dataset_cards: List[DatasetCard]) -> nx.DiGraph:
    """
    Build successor graph from dataset card citations.
    
    Args:
        dataset_cards: HF metadata with descriptions
        
    Returns:
        graph: Directed graph with context-labeled edges
    """
    pass

def parse_citations(description: str) -> List[Dict[str, Any]]:
    """
    Extract successor relationships from dataset description.
    
    Args:
        description: Dataset card description text
        
    Returns:
        List of dicts with keys: name, task_type, confidence
    """
    pass
```

### C3: Recommendation Module

```python
def recommend(graph: nx.DiGraph, deprecated: str, context: str) -> Optional[str]:
    """
    Context-aware successor lookup.
    
    Args:
        graph: Successor graph
        deprecated: Dataset to find successor for
        context: Inferred task context
        
    Returns:
        successor: Recommended replacement dataset or None
    """
    pass
```

### C4: Baseline Module

```python
def baseline_recommend(deprecated: str) -> str:
    """
    Linear version-based succession (no context).
    
    Args:
        deprecated: Dataset to find successor for
        
    Returns:
        successor: Versioned successor (e.g., "dataset-v2")
    """
    pass
```

### C5: Evaluation Module

```python
def compute_metrics(
    ground_truth_contexts: List[str],
    inferred_contexts: List[str],
    expert_labels: List[bool],
    inferred_edges: List[bool],
    override_counts: Dict[str, Tuple[int, int]]
) -> Dict[str, float]:
    """
    Compute evaluation metrics.
    
    Args:
        ground_truth_contexts: Test set labels
        inferred_contexts: Model predictions
        expert_labels: Edge validation labels
        inferred_edges: Edge predictions
        override_counts: (manual, total) per context
        
    Returns:
        Dict with keys: accuracy, precision, override_rate
    """
    pass

def generate_visualizations(
    ground_truth_contexts: List[str],
    inferred_contexts: List[str],
    override_counts: Dict[str, Tuple[int, int]],
    graph: nx.DiGraph,
    output_dir: str
) -> None:
    """
    Generate 4 required visualizations.
    
    Args:
        ground_truth_contexts: Test set labels
        inferred_contexts: Model predictions
        override_counts: (manual, total) per context
        graph: Successor graph
        output_dir: Directory to save figures
    """
    pass
```

---

## Tensor Shapes

N/A (Infrastructure validation, not neural network)

---

## Algorithms

### Context Inference (Pattern Matching)

```
Input: user_modules (List[str])
Output: (context: str, confidence: float)

patterns = {
    'classification': ['sklearn', 'xgboost', 'lightgbm'],
    'pretraining': ['transformers', 'torchvision.models'],
    'robustness': ['foolbox', 'cleverhans']
}

for context, libs in patterns.items():
    if any(lib in user_modules for lib in libs):
        return (context, 0.85)

return ('unknown', 0.0)
```

### Graph Construction (Citation Parsing)

```
Input: dataset_cards (List[DatasetCard])
Output: nx.DiGraph

G = nx.DiGraph()

for card in dataset_cards:
    successors = parse_citations(card.description)
    for succ in successors:
        G.add_edge(
            card.name,
            succ['name'],
            context=succ['task_type'],
            precision_score=succ['confidence']
        )

return G
```

### Recommendation (Context Filtering)

```
Input: graph, deprecated, context
Output: Optional[str]

successors = [
    (n, graph[deprecated][n]['precision_score'])
    for n in graph.neighbors(deprecated)
    if graph[deprecated][n]['context'] == context
]

if not successors:
    return None

return max(successors, key=lambda x: x[1])[0]
```

---

## Subtasks

### C1 Subtasks (3)
1. Implement pattern dictionary with task-specific library lists
2. Implement pattern matching logic with confidence scoring
3. Add explicit fallback for unknown contexts

### C2 Subtasks (4)
1. Implement dataset card citation parsing (regex patterns)
2. Implement NetworkX graph construction with edge attributes
3. Add validation for malformed dataset cards
4. Implement precision score calculation for inferred edges

### C3 Subtasks (3)
1. Implement context filtering logic for graph edges
2. Implement precision-based ranking for multiple successors
3. Add None return for no context match

### C4 Subtasks (1)
1. Implement simple string concatenation for versioned successor

### C5 Subtasks (4)
1. Implement accuracy computation via sklearn.metrics
2. Implement precision computation for edge validation
3. Implement override rate calculation from telemetry
4. Implement 4 visualization generators (confusion matrix, P-R curve, override bar chart, graph viz)

Total: 15 subtasks
