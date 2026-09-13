# Logic Specification: H-M1 (MECHANISM)

**Type:** MECHANISM — entropy vs correctness statistical validation. Extends h-e1 generation/entropy code.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: `h-e1/code/` not found on disk (h-e1 is spec-only, no materialized implementation) — API signatures verified against `h-e1/03_logic.md` (Phase 3 spec, most authoritative source available) instead of actual code.
**Analyzed Path**: h-e1/code/ (absent); fallback h-e1/03_logic.md
**Relevant Symbols**: `compute_token_entropy(scores: list[Tensor]) -> float`, `generate_responses(model, tokenizer, question, n_samples, temperature, max_new_tokens, seed) -> list[dict]`, `load_model(model_name) -> tuple`
**Note for Phase 4**: If `h-e1/code/` still absent at implementation time, copy `generate_responses`/`load_model`/`compute_token_entropy` verbatim into `h-m1/code/generate.py` and `h-m1/code/entropy.py` per architecture fallback instructions.

---

Applied: sampling-loop + group-statistical-test pattern for uncertainty-correctness validation (Kuhn et al. 2023 entropy methodology; standard scipy/sklearn group comparison).

## A-M3: Reuse/copy generation+entropy [Complexity: 10, Budget: 2]

**Applied**: Standard PyTorch — verbatim reuse of h-e1 generation/entropy code (no new algorithm).

### API Signatures

```python
# h-m1/code/generate.py (copied from h-e1/03_logic.md, verified)
def load_model(model_name: str = "meta-llama/Llama-2-7b-chat-hf") -> tuple:
    """FP16, device_map='auto'. Returns (model, tokenizer)."""
    ...

def generate_responses(
    model, tokenizer, question: str,
    n_samples: int = 10, temperature: float = 0.7,
    max_new_tokens: int = 128, seed: int = 42,
) -> list[dict]:
    """Returns: list of {'text': str, 'scores': list[Tensor[V]]}"""  # V=32000
    ...

# h-m1/code/entropy.py (copied from h-e1/03_logic.md, verified)
def compute_token_entropy(scores: list["Tensor"]) -> float:
    """Mean Shannon entropy across generated tokens. scores: T x [1, V] -> float"""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1 | port generate.py | Copy load_model + generate_responses from h-e1 spec verbatim |
| L-M3-2 | port entropy.py | Copy compute_token_entropy from h-e1 spec verbatim |

---

## A-M4: Correctness Evaluator [Complexity: 6, Budget: 1]

**Applied**: Standard PyTorch/stdlib — normalized exact-match + majority vote (no external pattern needed).

### API Signatures

```python
# h-m1/code/correctness.py
def evaluate_correctness(generated: str, aliases: list[str]) -> bool:
    """Normalized substring match: alias in lowercased/stripped generated text."""
    ...

def majority_answer(responses: list[str]) -> str:
    """Most frequent normalized (lower/strip) response text across n_samples."""
    ...
```

### Pseudo-code

```
def evaluate_correctness(generated, aliases):
    g = generated.lower().strip()
    return any(a.lower().strip() in g for a in aliases)

def majority_answer(responses):
    normalized = [r.lower().strip() for r in responses]
    return Counter(normalized).most_common(1)[0][0]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M4-1 | correctness.py | evaluate_correctness + majority_answer |

---

## A-M6: Stats analyzer [Complexity: 8, Budget: 1]

**Applied**: scipy/sklearn group-comparison pattern (t-test + AUROC + Cohen's d + Pearson r).

### API Signatures

```python
# h-m1/code/stats.py
def compute_correlation(entropies: list[float], correctness: list[bool]) -> dict:
    """Returns: {t_stat, p_value, auroc, cohens_d, pearson_r, mean_correct, mean_incorrect}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropies | [N] | N = num questions (~11,313) |
| correctness | [N] | bool labels |
| y_scores | [N] | -entropies, for AUROC (low entropy = confident) |

### Pseudo-code

```
correct_e = [e for e,c in zip(entropies, correctness) if c]
incorrect_e = [e for e,c in zip(entropies, correctness) if not c]
t_stat, p_value = scipy.stats.ttest_ind(incorrect_e, correct_e)
auroc = sklearn.metrics.roc_auc_score(correctness, [-e for e in entropies])
pooled_std = sqrt(((n1-1)*std(incorrect_e)**2 + (n2-1)*std(correct_e)**2) / (n1+n2-2))
cohens_d = (mean(incorrect_e) - mean(correct_e)) / pooled_std
pearson_r, _ = scipy.stats.pearsonr(entropies, [int(c) for c in correctness])
return {t_stat, p_value, auroc, cohens_d, pearson_r,
        mean_correct: mean(correct_e), mean_incorrect: mean(incorrect_e)}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M6-1 | stats.py | compute_correlation: t-test, AUROC, Cohen's d, Pearson r |

---

## A-M8: Pipeline + full-run validation [Complexity: 12, Budget: 1]

**Applied**: Checkpointed batch-loop pattern (reused from h-e1 orchestration).

### API Signatures

```python
# h-m1/code/run_pipeline.py
def run(limit: int = 11313) -> None:
    """Orchestrates: load -> generate -> entropy -> correctness -> merge -> stats -> visualize -> write JSON."""
    ...

# h-m1/code/visualize.py
def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str) -> None: ...
def plot_entropy_distribution(entropies: list[float], correctness: list[bool], out_path: str) -> None: ...
def plot_roc_curve(entropies: list[float], correctness: list[bool], out_path: str) -> None: ...
```

### Pseudo-code

```
questions = load_triviaqa_val(limit)
model, tokenizer = load_model(MODEL_NAME)
ckpt = CheckpointManager(CHECKPOINT_PATH)
results = ckpt.load().get("results", [])
done_ids = {r["qid"] for r in results}

for idx, q in enumerate(questions):
    if q["qid"] in done_ids: continue
    responses = generate_responses(model, tokenizer, q["question"], n_samples=10)
    entropies = [compute_token_entropy(r["scores"]) for r in responses]
    mean_entropy = mean(entropies)
    maj = majority_answer([r["text"] for r in responses])
    correct = evaluate_correctness(maj, q["answer_aliases"])
    results.append({"qid": q["qid"], "entropy": mean_entropy, "correct": correct})
    if (idx + 1) % 50 == 0:
        ckpt.save(idx, results)
ckpt.save(len(questions), results)

stats = compute_correlation([r["entropy"] for r in results], [r["correct"] for r in results])
plot_gate_metrics(stats["auroc"], AUROC_TARGET, stats["p_value"], f"{FIGURES_DIR}/gate_metrics.png")
plot_entropy_distribution([r["entropy"] for r in results], [r["correct"] for r in results],
                           f"{FIGURES_DIR}/entropy_distribution.png")
plot_roc_curve([r["entropy"] for r in results], [r["correct"] for r in results],
               f"{FIGURES_DIR}/roc_curve.png")
write_json({"stats": stats, "results": results}, OUTPUT_PATH)
```

### Subtasks [1/1 used — total 5/5 project budget used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M8-1 | run_pipeline.py + visualize.py | Wire load->generate->entropy->correctness->stats->figures->JSON, validate gate criteria on full 11K set |

---

## External Dependencies API (Base Hypothesis h-e1)

### API Signatures (Verified from h-e1/03_logic.md — actual code absent)

```python
# From: h-e1/03_logic.md A-2 (load_model, generate_responses), A-3 (compute_token_entropy)
def load_model(
    model_name: str = "meta-llama/Llama-2-7b-chat-hf",
) -> tuple:  # (PreTrainedModel, PreTrainedTokenizer), FP16, device_map='auto'
    ...

def generate_responses(
    model, tokenizer, question: str,
    n_samples: int = 10, temperature: float = 0.7,
    max_new_tokens: int = 128, seed: int = 42,
) -> list[dict]:
    """Returns list of {'text': str, 'scores': list[Tensor[1, V]]}, T entries per response."""
    ...

def compute_token_entropy(scores: list["Tensor"]) -> float:
    """scores: T x [1, V] -> mean Shannon entropy (float)."""
    ...

# From: h-e1/03_architecture.md CheckpointManager
class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50): ...
    def load(self) -> dict: ...            # {"last_qid_idx": int, "results": list}
    def save(self, idx: int, results: list): ...
```

**Verified from**: `h-e1/03_logic.md` (Phase 3 spec; `h-e1/code/` not present on disk — no actual implementation to verify against). Phase 4 must copy these three modules verbatim into `h-m1/code/` rather than cross-import if `h-e1/code/` remains absent.

---

## Non-Allocated Modules (Low/VeryLow complexity — signatures only, no subtask budget consumed)

```python
# h-m1/code/load_data.py
def load_triviaqa_val(limit: int | None = None) -> list[dict]: ...
# [{"qid": str, "question": str, "answer_aliases": list[str]}, ...]

# h-m1/code/config.py
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 128
AUROC_TARGET = 0.55
P_VALUE_TARGET = 0.05
CHECKPOINT_PATH = "results/checkpoint.json"
OUTPUT_PATH = "results/h-m1_results.json"
FIGURES_DIR = "figures/"
```
