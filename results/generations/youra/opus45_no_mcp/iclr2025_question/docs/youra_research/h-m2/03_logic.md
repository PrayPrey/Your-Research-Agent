# Logic: H-M2 (Semantic Consistency as Hallucination Predictor)

## Codebase Analysis

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code (not spec assumptions)
**Analyzed Path**: `h-m1/code/` (generate.py, entropy.py, correctness.py, checkpoint.py, stats.py, load_data.py)
**Relevant Symbols**: `generate_responses`, `compute_token_entropy`, `evaluate_correctness`, `majority_answer`, `CheckpointManager`, `compute_correlation`, `load_triviaqa_val`

**Discrepancy found**: h-m1's `stats.py::compute_correlation(entropies, correctness)` inverts score (`y_scores = -entropies`) because low entropy = correct. For consistency, higher consistency = correct, so **no inversion needed** — h-m2's stats function must NOT copy this sign flip verbatim.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/generate.py (ACTUAL CODE)
def load_model(model_name: str = None): ...
def generate_responses(model, tokenizer, question: str, n_samples: int = None,
                        temperature: float = None, max_new_tokens: int = None,
                        seed: int = None) -> list[dict]: ...
# each dict: {"text": str, "scores": list[Tensor]}  # scores: list of [vocab_size] logit tensors

# From: h-m1/code/entropy.py (ACTUAL CODE)
def compute_token_entropy(scores: list) -> float: ...

# From: h-m1/code/correctness.py (ACTUAL CODE)
def evaluate_correctness(generated: str, aliases: list[str]) -> bool: ...
def majority_answer(responses: list[str]) -> str: ...

# From: h-m1/code/checkpoint.py (ACTUAL CODE)
class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50): ...
    def load(self) -> dict: ...  # {"last_idx": int, "results": list}
    def save(self, idx: int, results: list): ...
    def should_save(self, idx: int) -> bool: ...

# From: h-m1/code/load_data.py (ACTUAL CODE)
def load_triviaqa_val(limit: int | None = None) -> list[dict]: ...
# [{"qid": str, "question": str, "answer_aliases": list[str]}, ...]
```

**Verified from**: `h-m1/code/` (actual implementation). Files copied verbatim into `h-m2/code/`: `generate.py`, `entropy.py`, `correctness.py`, `checkpoint.py`, `load_data.py`, `config.py` (with EMBEDDING_MODEL added).
**Not reused**: `h-m1/code/stats.py` — sign convention (entropy inversion) doesn't apply to consistency; h-m2 writes its own `compute_correlation`.
**Raw responses**: not persisted by h-m1 — h-m2 regenerates 10 responses/question independently.

---

## C-1: Config + copy base modules [Complexity: 5, Budget: 5]

**Applied**: Standard config module (copy + extend pattern)

```python
# config.py additions vs h-m1
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
```
Copy `load_data.py`, `generate.py`, `entropy.py`, `correctness.py`, `checkpoint.py` verbatim (signatures above).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | config.py | Copy h-m1 config, add EMBEDDING_MODEL |
| L-1-2 | copy generate/entropy | Copy verbatim |
| L-1-3 | copy correctness | Copy verbatim |
| L-1-4 | copy checkpoint/load_data | Copy verbatim |

---

## C-2: SemanticConsistencyScorer [Complexity: 8, Budget: 8]

**Applied**: sentence-transformers batch encode + pairwise cosine sim (SelfCheckGPT-style)

### API Signatures

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticConsistencyScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Load SentenceTransformer once."""
        self.model = SentenceTransformer(model_name)

    def encode(self, responses: list[str]) -> np.ndarray:
        """Batch encode. responses: N strings -> [N, 384]"""
        return self.model.encode(responses, convert_to_numpy=True, normalize_embeddings=True)

    def compute_consistency(self, responses: list[str]) -> float:
        """N responses -> mean of N*(N-1)/2 pairwise cosine sims (scalar)."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| responses | (N,) | list of strings, N=10 |
| embeddings | (N, 384) | L2-normalized |
| sim_matrix | (N, N) | cosine sim, diag=1 |
| pairwise_sims | (N*(N-1)/2,) | upper triangle, k=1 |
| consistency | scalar | mean(pairwise_sims) |

### Pseudo-code

```
1. embeddings = encode(responses)                    # [N, 384], normalized
2. sim_matrix = embeddings @ embeddings.T             # [N, N], cosine sim (since normalized)
3. iu = np.triu_indices(N, k=1)                        # exclude diagonal + duplicate pairs
4. pairwise_sims = sim_matrix[iu]                      # [N*(N-1)/2]
5. consistency = float(pairwise_sims.mean())
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | __init__ | Load SentenceTransformer model |
| L-2-2 | encode | Batch encode responses -> np.ndarray |
| L-2-3 | compute_consistency | Cosine sim matrix + upper-triangle mean |
| L-2-4 | edge case N<2 | Return 1.0 if single response (no pairs) |

---

## C-3: Consistency stats analyzer [Complexity: 7, Budget: 7]

**Applied**: Independent t-test (scipy) + AUROC (sklearn) + Cohen's d — same pattern as h-m1 `stats.py`, sign convention reversed (no inversion, high consistency = correct)

### API Signatures

```python
def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict:
    """t-test/AUROC/Cohen's d for consistency vs correctness."""
    ...
    # returns {t_stat, p_value, auroc, cohens_d,
    #          mean_correct, mean_incorrect, n_correct, n_incorrect}
```

### Pseudo-code

```
1. correct_c, incorrect_c = split consistencies by correctness bool mask
2. t_stat, p_value = ttest_ind(correct_c, incorrect_c, alternative='greater')  # correct > incorrect
3. y_scores = consistencies  # NO inversion (unlike h-m1 entropy)
4. auroc = roc_auc_score(correctness.astype(int), y_scores)
5. cohens_d = (mean(correct_c) - mean(incorrect_c)) / pooled_std
6. return dict(...)
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | t-test | scipy ttest_ind, alternative='greater' |
| L-3-2 | AUROC + Cohen's d | sklearn roc_auc_score, pooled-std effect size |
| L-3-3 | error guard | Return {"error": ...} if one group empty |

---

## C-4: Entropy-consistency correlation [Complexity: 4, Budget: 4]

**Applied**: scipy.stats.pearsonr

```python
def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float:
    """Pearson r, H-M3 preview."""
    from scipy import stats
    r, _ = stats.pearsonr(entropies, consistencies)
    return float(r)
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | pearsonr | Compute r between entropy and consistency arrays |
| L-4-2 | integrate | Wire into stats output dict |

---

## C-5: Visualizer [Complexity: 8, Budget: 8]

**Applied**: matplotlib bar/hist/ROC/scatter (extends h-m1 visualize.py pattern)

```python
def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str): ...
def plot_consistency_distribution(consistencies: list[float], correctness: list[bool], out_path: str): ...
def plot_roc_curve(consistencies: list[float], correctness: list[bool], out_path: str): ...
def plot_entropy_vs_consistency(entropies: list[float], consistencies: list[float],
                                 correctness: list[bool], out_path: str): ...
```

### Tensor Shapes
| Variable | Shape | Note |
|----------|-------|------|
| consistencies, entropies, correctness | (N_questions,) | one value per question, N_questions=100 |

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | gate bar | Bar chart auroc vs target, p_value annotation |
| L-5-2 | histogram | Overlaid hist, correct vs incorrect consistency |
| L-5-3 | ROC curve | sklearn roc_curve + auc, matplotlib plot |
| L-5-4 | scatter | entropy (x) vs consistency (y), colored by correctness |

---

## C-6: Pipeline integration [Complexity: 11, Budget: 11]

**Applied**: sequential orchestration + checkpoint resume (h-m1 run_pipeline.py pattern)

```python
def run(limit: int = 100, resume: bool = True) -> dict:
    """load -> generate(10/q) -> entropy+consistency -> correctness -> stats -> figures -> write json"""
    ...
```

### Pseudo-code

```
1. questions = load_triviaqa_val(limit)                     # [{qid, question, answer_aliases}]
2. ckpt = CheckpointManager(CHECKPOINT_PATH).load() if resume else {"last_idx": -1, "results": []}
3. model, tokenizer = load_model()
4. scorer = SemanticConsistencyScorer(EMBEDDING_MODEL)
5. for idx, q in enumerate(questions[ckpt["last_idx"]+1:]):
     responses = generate_responses(model, tokenizer, q["question"])   # 10 x {text, scores}
     texts = [r["text"] for r in responses]
     entropy = mean([compute_token_entropy(r["scores"]) for r in responses])
     consistency = scorer.compute_consistency(texts)
     maj = majority_answer(texts)
     correct = evaluate_correctness(maj, q["answer_aliases"])
     result = {qid, entropy, consistency, correct}
     append to results; checkpoint.save(idx, results) if should_save(idx)
6. stats = compute_correlation(consistencies, correctness)
7. stats["pearson_r_entropy_consistency"] = pearson_entropy_consistency(entropies, consistencies)
8. plot_* (gate, distribution, roc, scatter) -> figures/
9. write results/h-m2_results.json {results, stats}
10. return stats
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | load + resume | load_triviaqa_val, CheckpointManager resume logic |
| L-6-2 | generate loop | Per-question: generate, entropy, consistency, correctness, checkpoint |
| L-6-3 | stats aggregation | compute_correlation + pearson_entropy_consistency |
| L-6-4 | write results + figures | JSON output, call all plot_* functions |

---

## C-7: Full-run validation [Complexity: 9, Budget: 9]

**Applied**: Standard experiment run + gate check (no new logic, execution task)

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run 100q | Execute `run(limit=100, resume=True)` |
| L-7-2 | verify gate | Check p<0.05, AUROC>0.55, mean_correct>mean_incorrect |
| L-7-3 | inspect figures | Confirm 4 figures generated correctly |
| L-7-4 | document result | Note PASS/SHOULD_WORK-fail in results JSON |
