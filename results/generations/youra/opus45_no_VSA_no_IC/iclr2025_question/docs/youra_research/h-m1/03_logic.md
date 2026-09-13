# Logic: h-m1 (MECHANISM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: No `h-e1/code/` directory exists on disk (glob confirmed empty) — h-e1's own 03_logic.md documents a green-field implementation with no `code/` output yet. Serena/find_symbol has nothing to query; API signatures below are taken from h-e1's `02c_experiment_brief.md` reference implementation and `03_logic.md` pseudo-code (the only available source of truth), and from h-m1's own `03_architecture.md` which already reconciled naming.
**Analyzed Path**: `h-e1/code/` (attempted, not found), `h-e1/03_logic.md` (used)
**Relevant Symbols**: `SemanticEntropyBaseline` (h-e1 A-3), `run_pipeline_for_model` (h-e1 A-5) — reused as `SemanticEntropyLabels` / hidden-state extraction pattern here.

Archon KB: `rag_search_knowledge_base("logistic regression probe cross-dataset transfer")` returned only unrelated diffusers train_text_to_image.py pages (similarity ~0.37) — no applicable pattern found, consistent with h-e1 and architecture.md notes.

---

## M-1: Setup + Config [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/HF config module (no KB match).

### API Signatures

```python
# config.py — constants only, no functions
SEED: int = 42
MODEL_ID: str = "meta-llama/Meta-Llama-3-8B-Instruct"
N_LAYERS: int = 32
HIDDEN_DIM: int = 4096
TRAIN_DATASET: str = "trivia_qa"
EVAL_DATASET: str = "truthful_qa"
NLI_MODEL_ID: str = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
N_SAMPLES: int = 5
TEMPERATURE: float = 1.0
LAYER_IDX: int = -1
TORCH_DTYPE: str = "float16"
DEVICE_MAP: str = "auto"
RESULTS_DIR: str = "h-m1/results"
FIGURES_DIR: str = "h-m1/figures"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | Constants above |
| L-1-2 | Copy models.py | `ModelWrapper` verbatim from h-e1 spec (see External Dependencies) |
| L-1-3 | Copy sep.py | `SemanticEntropyProbe` verbatim from h-e1 spec |
| L-1-4 | dirs | `os.makedirs(RESULTS_DIR/FIGURES_DIR, exist_ok=True)` |

---

## M-2: Data Pipeline [Complexity: 6, Budget: 6]

**Applied**: HF `datasets.load_dataset` standard pattern.

### API Signatures

```python
def load_triviaqa(n_samples: int = 11000) -> "datasets.Dataset":
    """load_dataset('trivia_qa','rc.nocontext',split=f'train[:{n_samples}]')."""

def load_truthfulqa() -> "datasets.Dataset":
    """load_dataset('truthful_qa','generation',split='validation') -> 817 rows."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| triviaqa["question"] | list[str], len=11000 | field: `question` |
| truthfulqa["question"] | list[str], len=817 | field: `question` |
| truthfulqa["best_answer"] | list[str], len=817 | reference for correctness labels |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_triviaqa | HF load + slice |
| L-2-2 | load_truthfulqa | HF load validation split |
| L-2-3 | field extraction | pull `question`/`best_answer`/`correct_answers` columns |
| L-2-4 | seed set | `datasets.disable_progress_bar()` optional; set numpy/torch seed=42 |

---

## M-3: SE Label Generation [Complexity: 13, Budget: 13]

**Applied**: linear-probe-on-frozen-hidden-states / NLI-clustering pattern, reused verbatim from h-e1 A-3 (`SemanticEntropyBaseline`), renamed `SemanticEntropyLabels`. Extended with `correctness_labels` (new — h-e1 didn't need this since it evaluated only TruthfulQA in-distribution against dataset's own truthful/untruthful field; h-m1 needs cross-dataset ground truth via answer matching).

### API Signatures

```python
class SemanticEntropyLabels:
    def __init__(self, nli_model_id: str):
        """Load DeBERTa-v3-large-mnli for entailment scoring."""

    def cluster_responses(self, responses: list[str]) -> list[int]:
        """Bidirectional NLI entailment clustering. len(responses)=N -> len(cluster_ids)=N."""

    def compute_entropy(self, cluster_ids: list[int]) -> float:
        """H = -sum p(c) log p(c) over cluster distribution."""

    def compute_se_scores(self, model: "ModelWrapper", questions: list[str]) -> list[float]:
        """generate(N_SAMPLES, TEMPERATURE) -> cluster_responses -> compute_entropy, per question."""

    def binarize(self, se_scores: list[float]) -> list[int]:
        """1 if score > median(se_scores) else 0 (median computed per-dataset, i.e. separately for train/eval)."""

    def correctness_labels(
        self, model: "ModelWrapper", questions: list[str], references: list[str]
    ) -> list[int]:
        """Greedy-decode (temperature=0/n_samples=1) answer, exact/substring match vs reference -> binary."""
```

### Pseudo-code (new logic only — cluster/entropy identical to h-e1)

```
correctness_labels(model, questions, references):
  labels = []
  for q, ref in zip(questions, references):
    answer = model.generate(q, n_samples=1, temperature=0.0)[0]   # greedy
    match = normalize(ref) in normalize(answer) or normalize(answer) in normalize(ref)
    labels.append(1 if match else 0)
  return labels                                                    # len = len(questions)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| se_scores (train) | list[float], len=11000 | TriviaQA |
| se_scores (eval) | list[float], len=817 | TruthfulQA |
| correctness_labels (eval) | list[int], len=817 | AUROC ground truth |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | NLI clustering | `cluster_responses` (copy from h-e1 A-3) |
| L-3-2 | Entropy + binarize | `compute_entropy`, `binarize` (copy from h-e1 A-3) |
| L-3-3 | SE pipeline | `compute_se_scores`: generate→cluster→entropy |
| L-3-4 | Correctness labels | new: greedy decode + string match vs reference (TruthfulQA only) |

---

## M-4: Hidden State Extraction [Complexity: 9, Budget: 9]

**Applied**: frozen-hidden-state-extraction pattern from h-e1 A-5 (`extract_hidden_state` loop).

### API Signatures

```python
def extract_all_hidden_states(
    probe: "SemanticEntropyProbe", model: "ModelWrapper", questions: list[str]
) -> "np.ndarray":
    """Loop extract_hidden_state(model, *tokenize(q)) over questions. Returns [N, HIDDEN_DIM]."""
```

### Pseudo-code

```
extract_all_hidden_states(probe, model, questions):
  states = []
  for q in questions:
    input_ids, attention_mask = tokenize(q)              # via model.tokenizer
    h = probe.extract_hidden_state(model, input_ids, attention_mask)  # [1, HIDDEN_DIM]
    states.append(h)
  return np.vstack(states)                                # [N, HIDDEN_DIM]
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_hidden | [11000, 4096] | TriviaQA, LAYER_IDX |
| eval_hidden | [817, 4096] | TruthfulQA, LAYER_IDX |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Tokenize helper | wrap `model.tokenizer(q, return_tensors='pt')` |
| L-4-2 | Train extraction | `extract_all_hidden_states` over TriviaQA (11000) |
| L-4-3 | Eval extraction | `extract_all_hidden_states` over TruthfulQA (817) |
| L-4-4 | Cache to disk | optional `np.save` to avoid recompute on reruns |

---

## M-5: Probe Training + Cross-Dataset Eval [Complexity: 8, Budget: 8]

**Applied**: `SemanticEntropyProbe` (LogisticRegression, LBFGS, C=1.0) reused verbatim from h-e1.

### API Signatures

```python
# from h-e1 sep.py (verbatim, see External Dependencies)
probe = SemanticEntropyProbe(layer_idx=LAYER_IDX, token_position="last")
probe.fit(train_hidden, train_se_binary)              # train_hidden: [11000,4096], labels: [11000]
eval_proba = probe.predict_proba(eval_hidden)[:, 1]   # eval_hidden: [817,4096] -> [817]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Instantiate probe | `SemanticEntropyProbe(LAYER_IDX, 'last')` |
| L-5-2 | Fit | `.fit(train_hidden, train_se_binary)` |
| L-5-3 | Predict | `.predict_proba(eval_hidden)[:, 1]` |
| L-5-4 | Sanity check | assert `np.std(eval_proba) > 0.01` (non-constant, per experiment brief verification) |

---

## M-6: Gate Check + evaluate.py [Complexity: 4, Budget: 4]

**Applied**: sklearn `roc_auc_score` standard pattern.

### API Signatures

```python
def compute_auroc(y_true: list[int], y_pred_proba: "np.ndarray") -> float:
    """sklearn.metrics.roc_auc_score(y_true, y_pred_proba)."""

def check_gate(auroc: float) -> dict:
    """{'status': 'pass'|'fail'|'inconclusive', 'auroc': auroc}. pass if >0.70, fail if <0.60."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | compute_auroc | wrap `roc_auc_score` |
| L-6-2 | check_gate | threshold logic |
| L-6-3 | JSON assembly | `{"auroc": ..., "gate": ..., "layer_idx": ...}` |
| L-6-4 | Save | `json.dump` to `RESULTS_DIR/results.json` |

---

## M-7: Layer Ablation [Complexity: 10, Budget: 10]

**Applied**: per-layer probe sweep (new — not in h-e1, needed for FR-6 layer analysis figure).

### API Signatures

```python
def per_layer_auroc(
    model: "ModelWrapper",
    train_questions: list[str],
    eval_questions: list[str],
    train_se_binary: list[int],
    eval_correctness: list[int],
    candidate_layers: list[int] = list(range(20, 32)),
) -> dict[int, float]:
    """Extract hidden states + fit/eval probe per candidate layer. Returns {layer_idx: auroc}."""
```

### Pseudo-code

```
per_layer_auroc(model, train_q, eval_q, train_labels, eval_correct, candidate_layers):
  results = {}
  for L in candidate_layers:
    probe_L = SemanticEntropyProbe(layer_idx=L, token_position="last")
    train_h = extract_all_hidden_states(probe_L, model, train_q)   # [n_train, 4096]
    eval_h  = extract_all_hidden_states(probe_L, model, eval_q)    # [n_eval, 4096]
    probe_L.fit(train_h, train_labels)
    proba = probe_L.predict_proba(eval_h)[:, 1]
    results[L] = compute_auroc(eval_correct, proba)
  return results
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| candidate_layers | list[int], len<=12 | default [20..31] |
| results | dict[int, float] | one AUROC per layer |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Candidate layer list | `range(20, 32)` (per PRD note "typically layer 20-28") |
| L-7-2 | Per-layer extraction | reuse `extract_all_hidden_states` with varying `layer_idx` |
| L-7-3 | Per-layer fit/eval | new probe instance per layer |
| L-7-4 | Aggregate dict | `{layer: auroc}` for visualize.plot_layer_analysis |

---

## M-8: Visualization Suite [Complexity: 9, Budget: 9]

**Applied**: matplotlib standard bar/line/scatter plots (no KB match).

### API Signatures

```python
def plot_gate_metric(auroc: float, threshold: float, out_path: str) -> None:
    """Mandatory: bar chart [auroc, threshold] with pass/fail color."""

def plot_roc_curve(y_true: list[int], y_pred_proba: "np.ndarray", out_path: str) -> None:
    """sklearn.metrics.roc_curve -> plt.plot(fpr, tpr)."""

def plot_layer_analysis(layer_aurocs: dict[int, float], out_path: str) -> None:
    """Line plot: layer_idx (x) vs AUROC (y)."""

def plot_calibration(y_true: list[int], y_pred_proba: "np.ndarray", out_path: str) -> None:
    """sklearn.calibration.calibration_curve -> reliability diagram."""

def plot_distribution_comparison(train_proba: "np.ndarray", eval_proba: "np.ndarray", out_path: str) -> None:
    """Overlaid histograms: train (TriviaQA) vs eval (TruthfulQA) probe outputs."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | plot_gate_metric | mandatory bar chart |
| L-8-2 | plot_roc_curve | ROC on eval set |
| L-8-3 | plot_layer_analysis + plot_calibration | two functions, similar effort |
| L-8-4 | plot_distribution_comparison | needs train_proba (predict_proba on train_hidden with final probe) |

---

## M-9: Orchestration + Integration [Complexity: 12, Budget: 12]

**Applied**: h-e1 A-5 `run_pipeline_for_model`/`main` orchestration pattern, adapted for single cross-dataset run (no per-model loop needed — single fixed model).

### API Signatures

```python
def main() -> None: ...
```

### Pseudo-code

```
main():
  model = ModelWrapper(MODEL_ID); model.load()
  train_data = load_triviaqa(11000)
  eval_data = load_truthfulqa()

  se_labels = SemanticEntropyLabels(NLI_MODEL_ID)
  train_se = se_labels.compute_se_scores(model, train_data["question"])     # len=11000
  eval_se  = se_labels.compute_se_scores(model, eval_data["question"])      # len=817
  train_se_binary = se_labels.binarize(train_se)
  eval_correctness = se_labels.correctness_labels(
      model, eval_data["question"], eval_data["best_answer"])               # len=817

  probe = SemanticEntropyProbe(LAYER_IDX, "last")
  train_hidden = extract_all_hidden_states(probe, model, train_data["question"])  # [11000,4096]
  eval_hidden  = extract_all_hidden_states(probe, model, eval_data["question"])   # [817,4096]
  probe.fit(train_hidden, train_se_binary)
  eval_proba = probe.predict_proba(eval_hidden)[:, 1]                        # [817]
  train_proba = probe.predict_proba(train_hidden)[:, 1]                      # [11000], for dist. plot

  auroc = compute_auroc(eval_correctness, eval_proba)
  gate = check_gate(auroc)

  layer_aurocs = per_layer_auroc(model, train_data["question"], eval_data["question"],
                                  train_se_binary, eval_correctness)         # dict[int,float]

  save_json({"auroc": auroc, "gate": gate, "layer_aurocs": layer_aurocs}, RESULTS_DIR)
  plot_gate_metric(auroc, 0.70, f"{FIGURES_DIR}/gate.png")
  plot_roc_curve(eval_correctness, eval_proba, f"{FIGURES_DIR}/roc.png")
  plot_layer_analysis(layer_aurocs, f"{FIGURES_DIR}/layer_analysis.png")
  plot_calibration(eval_correctness, eval_proba, f"{FIGURES_DIR}/calibration.png")
  plot_distribution_comparison(train_proba, eval_proba, f"{FIGURES_DIR}/dist.png")
  print(gate)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Load model + data | wire config, ModelWrapper, data.py |
| L-9-2 | SE + correctness labels | wire semantic_entropy.py functions |
| L-9-3 | Hidden extraction + probe fit/eval | wire M-4/M-5 |
| L-9-4 | Ablation + save + visualize | wire M-6/M-7/M-8, call all plot_* |

---

## External Dependencies (Base Hypothesis: h-e1)

### API Signatures (From h-e1 03_logic.md — no compiled code exists yet)

```python
# ModelWrapper (h-e1, referenced in A-5 pseudo-code) — copy into h-m1/code/models.py
class ModelWrapper:
    def __init__(self, model_id: str): ...
    def load(self) -> None: ...
    def generate(self, prompt: str, n_samples: int = 5, temperature: float = 1.0) -> list[str]:
        """Hardcodes max_new_tokens=100 per h-e1 architecture.md finding. Returns n_samples strings."""

# SemanticEntropyProbe (h-e1 A-5) — copy into h-m1/code/sep.py
class SemanticEntropyProbe:
    def __init__(self, layer_idx: int, token_position: str = "last"): ...
    def extract_hidden_state(self, model: "ModelWrapper", input_ids, attention_mask) -> "np.ndarray":
        """Requires ModelWrapper instance with .get_hidden_states, not raw tensors. Returns [1, hidden_dim]."""
    def fit(self, hidden_states: "np.ndarray", labels: list[int]) -> None:
        """LogisticRegression(solver='lbfgs', max_iter=1000, C=1.0)."""
    def predict_proba(self, hidden_states: "np.ndarray") -> "np.ndarray":
        """Returns full (N,2) array — h-m1 must index [:, 1] for positive class."""
```

**Verified from**: `h-e1/03_logic.md` (A-5 pseudo-code) and `h-m1/03_architecture.md` Codebase Analysis notes — **no `h-e1/code/` directory exists on disk** (confirmed via glob), so no compiled source was available to inspect directly. Phase 4 Coder must implement `ModelWrapper`/`SemanticEntropyProbe` fresh in `h-m1/code/` following these signatures (h-e1's code has apparently not been materialized either — Phase 4 should implement both hypotheses' shared classes consistently, or check for h-e1/code/ again at implementation time in case it now exists).

**Note**: If `h-e1/code/` exists by Phase 4 time with different actual parameter names, those take precedence over this document (per base-hypothesis verification rule).
