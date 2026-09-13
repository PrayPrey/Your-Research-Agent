# H-M3 Architecture: Representation Separation Analysis

**Applied**: Hidden-state probe pattern (extract last-layer reps, cosine separation, linear SVM probe) — standard RLHF interpretability approach.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1, H-M2)
**Status**: Patterns found from base code — read directly (Serena MCP unavailable per 02c brief)
**Analyzed Path**: `h-m1/code/`, `h-m2/code/`
**Findings**:
- H-M1 `results.json` `per_task` entries have `task_id`, `task_type` (A/B), `confidence_*` fields — **no question text cached**. Must reload raw text via H-M1 `data.py::load_all_tasks()` and join by `task_id`.
- H-M1 `inference.py::load_model()` gives exact model-loading pattern (fp16, `device_map="auto"`, eval mode) — reused for hidden-state extraction with `output_hidden_states=True` added.
- H-M2 `loader.py` shows the join/validation pattern against H-M1 `results.json` — reused for label loading.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Task loaders | `from h_m1.data import load_all_tasks, Task` | `h-m1/code/data.py` |
| Model loader | `from h_m1.inference import load_model` | `h-m1/code/inference.py` |
| H-M1 results (labels) | read via `json.load` | `h-m1/code/outputs/results.json` |

**Verified from**: `h-m1/code/` (actual implementation, not spec)

Note: `h-m1`/`h-m2` are sibling directories, not importable packages. Use `sys.path.insert` with `Path(__file__).parent.parent.parent / "h-m1" / "code"`, matching H-M2's `loader.py` pattern.

---

## Directory Structure

```
h-m3/
├── code/
│   ├── main.py
│   ├── data_loader.py
│   ├── hidden_state_extractor.py
│   ├── separation_analyzer.py
│   ├── linear_probe.py
│   ├── visualizer.py
│   └── outputs/
│       └── results.json
└── figures/
    ├── gate_metrics.png
    └── tsne_representation.png
```

---

## Data Flow

```
H-M1 data.py (load_all_tasks)  ---question text---\
                                                     >  data_loader.py --> tasks[task_id -> {text, type}]
H-M1 results.json (per_task)   ---task_type label--/

tasks --> hidden_state_extractor.py (per model, batch=8, no_grad)
       --> hidden_states[model_id] : (N, hidden_dim) + type_a/type_b split

hidden_states --> separation_analyzer.py --> separation_score (per model)
hidden_states --> linear_probe.py        --> probe_accuracy (5-fold CV, per model)

{separation_score, probe_accuracy} x 3 models --> main.py aggregates + gate check
                                               --> visualizer.py (t-SNE, gate bar chart)
                                               --> outputs/results.json
```

---

## Modules

### DataLoader (`data_loader.py`)

**Dependencies**: H-M1 `data.py`, H-M1 `results.json`

```python
class LabeledTask(TypedDict):
    task_id: str
    task_type: str  # "A" or "B"
    text: str        # question, used as probe prompt

def load_labeled_tasks(h_m1_results_path: str = None) -> List[LabeledTask]: ...
def split_by_type(tasks: List[LabeledTask]) -> Tuple[List[LabeledTask], List[LabeledTask]]: ...
```

### HiddenStateExtractor (`hidden_state_extractor.py`)

**Dependencies**: H-M1 `inference.py::load_model`

```python
def extract_hidden_states(
    model, tokenizer, texts: List[str], batch_size: int = 8
) -> torch.Tensor:
    """Batched last-layer, last-token hidden states. torch.no_grad(). Returns (N, hidden_dim)."""
    ...

def extract_for_model(
    model_id: str, tasks: List[LabeledTask], batch_size: int = 8
) -> Dict[str, torch.Tensor]:
    """Returns {'type_a': Tensor, 'type_b': Tensor, 'all': Tensor, 'labels': List[str]}."""
    ...
```

### SeparationAnalyzer (`separation_analyzer.py`)

**Dependencies**: none (torch, F)

```python
def compute_representation_separation(
    type_a_hidden: torch.Tensor, type_b_hidden: torch.Tensor
) -> Dict[str, float]:
    """intra/inter cosine similarity -> {'separation_score': float}."""
    ...
```

### LinearProbe (`linear_probe.py`)

**Dependencies**: sklearn.svm.LinearSVC

```python
def train_probe(
    hidden_states: np.ndarray, labels: List[str], cv: int = 5
) -> Dict[str, float]:
    """LinearSVC 5-fold cross_val_score -> {'probe_accuracy': float}."""
    ...
```

### Visualizer (`visualizer.py`)

**Dependencies**: matplotlib, sklearn.manifold.TSNE

```python
def plot_gate_metrics(results_per_model: Dict[str, Dict], out_path: str) -> None: ...
def plot_tsne(hidden_states: np.ndarray, labels: List[str], out_path: str) -> None: ...
```

### Main (`main.py`)

**Dependencies**: all modules above

```python
def run_model_analysis(model_id: str, tasks: List[LabeledTask]) -> Dict: ...
def aggregate_and_gate(per_model_results: Dict[str, Dict]) -> Dict:
    """gate_pass = any(sep < 0.1 or acc < 0.6 for model results), primary = Llama-2-7B-Chat."""
    ...
def main() -> None: ...  # loads tasks, loops 3 models, writes outputs/results.json, generates figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Data Loading | Load H-M1 raw tasks + join task_type labels from results.json | 5 | 2+2+1+0 |
| M3-2 | Model Setup | Load 3 models w/ output_hidden_states=True, fp16, device_map=auto | 4 | 2+1+1+0 |
| M3-3 | Hidden State Extraction | Batched (bs=8) last-layer last-token extraction, no_grad | 7 | 3+2+2+0 |
| M3-4 | Separation Analysis | Intra/inter cosine similarity, separation_score per model | 6 | 2+1+3+0 |
| M3-5 | Linear Probe | LinearSVC 5-fold CV probe_accuracy per model | 5 | 2+1+2+0 |
| M3-6 | Cross-Model Validation | Run M3-3 to M3-5 for all 3 models, aggregate | 6 | 3+2+1+0 |
| M3-7 | Gate Logic | Compute gate_pass per success criteria, compare to H-M1/H-M2 | 4 | 1+2+1+0 |
| M3-8 | Visualization | t-SNE plot + gate metrics bar chart, save to figures/ | 6 | 3+1+2+0 |
| M3-9 | Results Export | Serialize per-model + aggregate metrics to outputs/results.json | 3 | 1+1+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M3-1, M3-2, M3-3, M3-4, M3-5, M3-6, M3-7, M3-8, M3-9]

---

## Key Implementation Notes

- Reuse H-M1/H-M2 task type labels — no re-annotation. Question text is NOT cached in H-M1 `results.json`; reload via `h-m1/code/data.py::load_all_tasks()` and join on `task_id`.
- `torch.no_grad()` required for all hidden-state extraction (inference only, no training).
- Batch size 8 for extraction, matching H-M1 inference pattern.
- Hidden state = `outputs.hidden_states[-1][:, -1, :]` (last layer, last token) per 02c brief.
- Primary model for gate decision: `meta-llama/Llama-2-7b-chat-hf` (consistent with H-M1/H-M2 primary_model convention); other 2 models are cross-validation (Epic M3-6).
- Gate pass: `separation_score < 0.1 OR probe_accuracy < 0.6` for primary model.
