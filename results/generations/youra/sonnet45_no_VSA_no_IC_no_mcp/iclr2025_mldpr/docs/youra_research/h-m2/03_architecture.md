# Architecture Document: h-m2

**Date:** 2026-08-24
**Hypothesis:** Context-aware successor graphs capture task-specific replacement paths via usage-pattern inference, providing more relevant recommendations than linear version-based succession with ≥ 70% context inference accuracy
**Phase:** 2C - Implementation Planning
**Author:** Phase 3 Planning Agent

---

## System Overview

Infrastructure validation experiment comparing context-aware successor graphs (proposed) against linear version-based succession (baseline). System components:

1. **Context Inference Module** - Python import history introspection
2. **Graph Construction Module** - Dataset card citation parsing
3. **Recommendation Module** - Context-aware graph lookup
4. **Baseline Module** - Linear version-based succession
5. **Evaluation Module** - Metrics computation and visualization

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXPERIMENT HARNESS                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌──────────────┐
│   BASELINE    │   │    PROPOSED      │   │  EVALUATION  │
│    SYSTEM     │   │     SYSTEM       │   │    MODULE    │
└───────────────┘   └──────────────────┘   └──────────────┘
        │                     │                     │
        │           ┌─────────┼─────────┐           │
        │           │         │         │           │
        │           ▼         ▼         ▼           │
        │    ┌─────────┐ ┌───────┐ ┌──────────┐    │
        │    │ CONTEXT │ │ GRAPH │ │   REC    │    │
        │    │INFERENCE│ │ BUILD │ │  LOOKUP  │    │
        │    └─────────┘ └───────┘ └──────────┘    │
        │           │         │         │           │
        │           └─────────┼─────────┘           │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   DATA SOURCES   │
                    │  - HF API        │
                    │  - PwC API       │
                    │  - Validation DS │
                    └──────────────────┘
```

---

## Component Specifications

### C1: Context Inference Module

**Purpose:** Infer user task context from Python import history

**Input:**
- `user_modules`: List[str] - Loaded module names from `sys.modules`

**Output:**
- `context`: str - Inferred task type ("classification", "pretraining", "robustness", "unknown")
- `confidence`: float - Pattern match confidence (0.0-1.0)

**Algorithm:**
```python
def infer_context(user_modules: List[str]) -> Tuple[str, float]:
    patterns = {
        'classification': ['sklearn', 'xgboost', 'lightgbm'],
        'pretraining': ['transformers', 'torchvision.models'],
        'robustness': ['foolbox', 'cleverhans']
    }
    for context, libs in patterns.items():
        if any(lib in user_modules for lib in libs):
            return context, 0.85  # Fixed confidence for pattern match
    return 'unknown', 0.0  # Explicit fallback
```

**Dependencies:**
- Python stdlib: `sys.modules`

**Error Handling:**
- Empty modules list → return ("unknown", 0.0)
- No pattern match → return ("unknown", 0.0)

---

### C2: Graph Construction Module

**Purpose:** Build successor graph from dataset card citations

**Input:**
- `dataset_cards`: List[DatasetCard] - HF metadata with descriptions

**Output:**
- `graph`: networkx.DiGraph - Directed graph with context-labeled edges

**Algorithm:**
```python
def build_graph(dataset_cards: List[DatasetCard]) -> nx.DiGraph:
    G = nx.DiGraph()
    for card in dataset_cards:
        # Parse citations from description
        successors = parse_citations(card.description)
        for succ in successors:
            G.add_edge(
                card.name, 
                succ['name'],
                context=succ['task_type'],
                precision_score=succ['confidence']
            )
    return G

def parse_citations(description: str) -> List[Dict]:
    # Pattern matching:
    # "improved version of X" → successor edge
    # "extends X for Y task" → successor edge with context Y
    # Extract: target dataset, task context, confidence
    ...
```

**Dependencies:**
- NetworkX: Graph construction
- HuggingFace API: Dataset cards
- Papers with Code API: Citation data

**Error Handling:**
- Invalid dataset card → skip
- No citations found → no edges added
- Ambiguous context → default to "unknown"

---

### C3: Recommendation Module

**Purpose:** Context-aware successor lookup

**Input:**
- `deprecated_dataset`: str - Dataset to find successor for
- `user_context`: str - Inferred task context
- `graph`: networkx.DiGraph - Successor graph

**Output:**
- `successor`: Optional[str] - Recommended replacement dataset

**Algorithm:**
```python
def recommend(graph: nx.DiGraph, deprecated: str, context: str) -> Optional[str]:
    # Filter edges by context match
    successors = [
        (n, graph[deprecated][n]['precision_score'])
        for n in graph.neighbors(deprecated)
        if graph[deprecated][n]['context'] == context
    ]
    if not successors:
        return None  # No context match
    # Rank by precision score
    return max(successors, key=lambda x: x[1])[0]
```

**Dependencies:**
- NetworkX: Graph traversal

**Error Handling:**
- Dataset not in graph → return None
- No context match → return None
- Tie in precision score → return first

---

### C4: Baseline Module

**Purpose:** Linear version-based succession

**Input:**
- `deprecated_dataset`: str - Dataset to find successor for

**Output:**
- `successor`: str - Versioned successor (always returns same result)

**Algorithm:**
```python
def baseline_recommend(deprecated: str) -> str:
    # Simple string suffix
    return f"{deprecated}-v2"
```

**Dependencies:** None (pure string manipulation)

**Error Handling:** None (always returns string)

---

### C5: Evaluation Module

**Purpose:** Compute metrics and generate visualizations

**Input:**
- `ground_truth_contexts`: List[str] - Test set labels
- `inferred_contexts`: List[str] - Model predictions
- `expert_labels`: List[bool] - Edge validation labels
- `inferred_edges`: List[bool] - Edge predictions
- `override_counts`: Dict[str, Tuple[int, int]] - (manual, total) per context

**Output:**
- `accuracy`: float - Context inference accuracy
- `precision`: float - Edge precision
- `override_rate`: float - User override rate
- Saved figures (4 visualizations)

**Metrics:**
```python
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix

# Context inference accuracy
accuracy = accuracy_score(ground_truth_contexts, inferred_contexts)

# Edge precision
precision = precision_score(expert_labels, inferred_edges, average='binary')

# Override rate
override_rate = sum(manual for manual, total in override_counts.values()) / \
                sum(total for manual, total in override_counts.values())
```

**Visualizations:**
1. **Confusion Matrix** - `confusion_matrix()` + `matplotlib.pyplot.imshow()`
2. **Precision-Recall Curve** - `precision_recall_curve()` + plot
3. **Override Rate Bar Chart** - Per-context override percentages
4. **Graph Visualization** - `nx.draw()` with context-colored edges

**Dependencies:**
- sklearn.metrics: Accuracy, precision, confusion matrix
- matplotlib: Plotting
- NetworkX: Graph visualization

---

## Data Flow

### 1. Data Collection Phase
```
HF API → Dataset Cards → Graph Construction Module → Successor Graph
PwC API → Citations → Graph Construction Module → Successor Graph
Manual Labeling → Validation Dataset → Train/Test Split (70/30)
```

### 2. Training Phase (Pattern Library)
```
Validation Dataset (70%) → Pattern Extraction → Context Patterns Dict
```

### 3. Evaluation Phase
```
Test Set → Context Inference → Inferred Contexts
         → Baseline System → Baseline Predictions
         → Proposed System → Proposed Predictions
         → Evaluation Module → Metrics + Figures
```

---

## File Structure

```
h-m2/
├── src/
│   ├── context_inference.py      # C1: Context Inference Module
│   ├── graph_construction.py     # C2: Graph Construction Module
│   ├── recommendation.py          # C3: Recommendation Module
│   ├── baseline.py                # C4: Baseline Module
│   ├── evaluation.py              # C5: Evaluation Module
│   └── experiment.py              # Main experiment harness
├── data/
│   ├── dataset_cards/             # HF metadata (collected)
│   ├── citations/                 # PwC data (collected)
│   └── validation_dataset.json    # Labeled contexts (manual)
├── results/
│   ├── metrics.json               # Computed metrics
│   └── figures/                   # 4 required visualizations
└── docs/
    ├── 02c_prd.md
    ├── 02c_architecture.md (this file)
    └── 02c_experiment_brief.md
```

---

## Implementation Priorities

**Phase 4 Implementation Order:**

1. **Data Collection** (foundational)
   - HuggingFace API scraper
   - Papers with Code API scraper
   - Validation dataset labeling

2. **Baseline System** (simplest)
   - Linear version-based succession

3. **Core Modules** (parallel)
   - Context Inference Module
   - Graph Construction Module
   - Recommendation Module

4. **Evaluation** (final)
   - Metrics computation
   - Visualization generation
   - Statistical tests

---

## Testing Strategy

**Unit Tests:**
- Context inference: Known module lists → expected context
- Graph construction: Sample dataset cards → expected edges
- Recommendation: Known graph + context → expected successor
- Baseline: Any dataset → versioned successor

**Integration Tests:**
- End-to-end: Validation dataset → metrics computation
- API access: HF + PwC endpoints → metadata retrieval

**Validation Tests:**
- Context accuracy ≥70% on test set
- Edge precision ≥60% on expert validation
- Override rate <50% on telemetry

---

## Performance Considerations

**Scalability:**
- Graph construction: O(n) dataset cards, O(m) edges
- Context inference: O(k) pattern checks (k=3 contexts)
- Recommendation: O(d) edges per deprecated dataset

**Bottlenecks:**
- API rate limits: Daily scraping with caching
- Manual labeling: 500+ samples (one-time cost)
- Expert validation: Sample-based (not full edge set)

**Optimization:**
- Cache dataset cards locally
- Precompute successor graph
- Batch API requests

---

## Error Scenarios

| Scenario | Handling | Fallback |
|----------|----------|----------|
| HF API timeout | Retry with exponential backoff | Local cache |
| No pattern match | Return "unknown" context | Manual specification |
| No context match in graph | Return None | Baseline recommendation |
| Empty validation dataset | Error (cannot compute accuracy) | N/A (critical) |

---

## Traceability

| Component | PRD Requirement | Experiment Brief Section |
|-----------|----------------|--------------------------|
| C1 (Context Inference) | F1: Python Import Introspection | Core Mechanism (Step 2) |
| C2 (Graph Construction) | F2: Dataset Card Citation Parser | Core Mechanism (Step 1) |
| C3 (Recommendation) | F3: Context-Aware Graph Lookup | Core Mechanism (Step 3) |
| C4 (Baseline) | F4: Baseline System | Baseline Model |
| C5 (Evaluation) | F6: Evaluation Metrics | Evaluation (Primary Metrics) |

---

*Architecture document generated from 02c_experiment_brief.md + 02c_prd.md*
*Next: Peer Review Protocol (02c_prp.md)*
