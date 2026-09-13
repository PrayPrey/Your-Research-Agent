# Logic: H-M4 (Probe vs Output-Level Baselines)

Applied: Standard PyTorch — no external UQ dependency (KB search found no directly applicable pattern; confirmed by architecture notes)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: API signatures verified from actual code (Serena had no active project for this path — used direct file Read instead)
**Analyzed Path**: `docs/youra_research/h-m3/code/probe.py`, `docs/youra_research/h-m3/code/data.py`
**Relevant Symbols**:
- `LinearCorrectnessProbe(C: float = 1e-3, max_iter: int = 2000)` — `.fit(X, y)`, `.predict_proba(X) -> np.ndarray`, `.evaluate(X_val, y_val) -> float`
- `load_hidden_states(cache_folder: str) -> tuple[X_train, y_train, X_val, y_val]` — **4-tuple, not 2-tuple** (architecture stub was wrong)
- `scale_features(X_train, X_val) -> tuple[X_train_scaled, X_val_scaled, StandardScaler]`

**Critical correction vs architecture spec**: `03_architecture.md` stub showed `get_probe_scores()` calling `load_hidden_states` as if it returns `(hidden_states, labels)` pairs. Actual signature returns 4 separate arrays `(X_train, y_train, X_val, y_val)`. Logic below uses verified signature.

---

## B-1 + reuse: ProbeReuse [Complexity: 8]

**Applied**: Standard PyTorch/sklearn — direct reuse, retrain in-process (no checkpoint exists)

### API Signatures

```python
# code/reuse_probe.py
import sys
sys.path.insert(0, "../h-m3/code")
from probe import LinearCorrectnessProbe
from data import load_hidden_states, scale_features

def get_probe_scores(h_m1_cache_folder: str, seed: int = 42) -> dict:
    """Retrain H-M3 probe identically; return val scores + labels."""
    X_train, y_train, X_val, y_val = load_hidden_states(h_m1_cache_folder)
    X_train_s, X_val_s, scaler = scale_features(X_train, X_val)
    probe = LinearCorrectnessProbe(C=1e-3, max_iter=2000).fit(X_train_s, y_train)
    probe_scores = probe.predict_proba(X_val_s)  # [1700] float in [0,1]
    return {"probe_scores": probe_scores, "y_val": y_val, "probe": probe, "scaler": scaler}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_train | (9500, 4096) | H-M1 cache |
| X_val | (1700, 4096) | H-M1 cache |
| probe_scores | (1700,) | P(correct), used directly as confidence score |
| y_val | (1700,) | int64 binary labels |

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B1-1 | ProbeReuse | Retrain probe via verified `load_hidden_states`/`scale_features`/`LinearCorrectnessProbe` API; sanity-check `probe.evaluate(X_val_s, y_val) ≈ 0.8851` |

---

## B-3/B-4/B-5: Generation + Baseline Metrics [Complexity: 10+6+6]

**Applied**: HuggingFace `generate(output_scores=True, return_dict_in_generate=True)` (standard PyTorch, per PRD FR-1/FR-2 pseudo-code)

### API Signatures

```python
# code/generate.py
def load_model(model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct") -> tuple:
    """Returns (model, tokenizer). fp16, device_map='auto'."""
    ...

def generate_with_scores(model, tokenizer, prompt: str, max_new_tokens: int = 50) -> dict:
    """Greedy decode with per-step logits.
    Returns {"text": str, "scores": Tensor[gen_len, vocab], "generated_ids": Tensor[gen_len]}
    """
    ...

# code/baselines.py
import torch.nn.functional as F

def compute_token_entropy(logits: torch.Tensor) -> float:
    """logits: [gen_len, vocab] -> mean per-token entropy (float)."""
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    return (-(probs * log_probs).sum(dim=-1)).mean().item()

def compute_sequence_nll(logits: torch.Tensor, token_ids: torch.Tensor) -> float:
    """logits: [gen_len, vocab], token_ids: [gen_len] -> avg NLL (float, unnegated)."""
    log_probs = F.log_softmax(logits, dim=-1)
    token_lp = log_probs.gather(1, token_ids.unsqueeze(1)).squeeze(1)
    return (-token_lp.mean()).item()

def run_generation_batch(model, tokenizer, questions: list[dict], max_new_tokens: int = 50) -> list[dict]:
    """Loop generate_with_scores over all questions.
    Returns per-example: {"id", "text", "entropy": float, "nll": float}
    """
    ...

def compute_all_baselines(gen_outputs: list[dict]) -> dict:
    """Aggregate + negate for confidence direction (higher = more confident).
    Returns {"entropy_scores": np.ndarray[N], "nll_scores": np.ndarray[N]}
    entropy_scores = -entropy per example; nll_scores = -nll per example.
    """
    ...
```

### Pseudo-code (generation loop, sequential — batching optional per NFR-1)

```
for q in questions:
    inputs = tokenizer(q["question"], return_tensors="pt").to(model.device)
    out = model.generate(**inputs, max_new_tokens=50, do_sample=False,
                          return_dict_in_generate=True, output_scores=True)
    gen_ids = out.sequences[0, inputs.input_ids.shape[1]:]        # [gen_len]
    scores = torch.stack(out.scores, dim=0).squeeze(1)            # [gen_len, vocab]
    entropy = compute_token_entropy(scores)
    nll = compute_sequence_nll(scores, gen_ids)
    text = tokenizer.decode(gen_ids, skip_special_tokens=True)
    label = exact_match(text, q["gold_answers"])                  # B-6
    store(entropy, nll, label)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | [gen_len, vocab] | per-example, vocab=128256 (Llama-3) |
| generated_ids | [gen_len] | greedy decode ids |
| entropy_scores | (1700,) | negated: higher = more confident |
| nll_scores | (1700,) | negated: higher = more confident |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B3-1 | GenerationRunner | `load_model`, `generate_with_scores`, `run_generation_batch` over 1700 val questions |
| L-B4-1 | BaselineMetrics + labeling | `compute_token_entropy`, `compute_sequence_nll`, `compute_all_baselines`; exact-match labels (B-6) recomputed against live generation text |

---

## B-6/B-7: Correctness Labels + AUROC/Delta (no new subtask — folded into above budget)

### API Signatures

```python
# code/evaluate.py (also used for B-6 exact-match helper)
def exact_match(pred_text: str, gold_answers: list[str]) -> int:
    """Normalize + compare; returns 0/1."""
    ...

def compute_auroc_all(probe_scores: np.ndarray, entropy_scores: np.ndarray,
                       nll_scores: np.ndarray, labels: np.ndarray) -> dict:
    """{"probe_auroc": float, "entropy_auroc": float, "nll_auroc": float}"""
    ...

def compute_deltas(aurocs: dict) -> dict:
    """{"delta_entropy": probe - entropy, "delta_nll": probe - nll}"""
    ...

def check_gate(deltas: dict, threshold: float = 0.05) -> dict:
    """{"gate_entropy_pass": bool, "gate_nll_pass": bool, "gate_pass": bool (AND)}"""
    ...
```

**Note**: labels used for probe AUROC must be the *same* recomputed exact-match labels from the current live generation (not H-M1/H-M3 cached labels), to avoid label/score mismatch — probe_scores are indexed by same val ordering as generation loop.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: docs/youra_research/h-m3/code/probe.py (ACTUAL CODE)
class LinearCorrectnessProbe:
    def __init__(self, C: float = 1e-3, max_iter: int = 2000): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "LinearCorrectnessProbe": ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...  # [:, 1] slice already applied
    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> float: ...  # roc_auc_score

# From: docs/youra_research/h-m3/code/data.py (ACTUAL CODE)
def load_hidden_states(cache_folder: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Returns (X_train, y_train, X_val, y_val) — 4-tuple, NOT (hidden_states, labels)."""
    ...

def scale_features(X_train: np.ndarray, X_val: np.ndarray) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    ...
```

**Verified from**: `docs/youra_research/h-m3/code/probe.py`, `docs/youra_research/h-m3/code/data.py` (actual implementation, not `03_architecture.md` stub, which incorrectly showed a 2-tuple return for `load_hidden_states`).

---

## Subtask Budget Summary [2/2 used]

| ID | Subtask |
|----|---------|
| L-B1-1 | ProbeReuse (retrain + validate probe) |
| L-B3-1 / L-B4-1 combined under budget | Generation + baseline metrics + labeling (grouped as one implementation subtask in Phase 4 due to tight coupling — generation loop must compute entropy/NLL/label in the same pass) |
