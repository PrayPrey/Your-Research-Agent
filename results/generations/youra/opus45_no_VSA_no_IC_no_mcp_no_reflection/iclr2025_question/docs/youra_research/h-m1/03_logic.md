# Logic: h-m1 (MECHANISM — NLI-Clustered Semantic Entropy)

Applied: NLI bidirectional-entailment greedy clustering (Kuhn et al. 2023, `lorenzkuhn/semantic_uncertainty`)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (not spec).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `load_truthfulqa_mc1` (data.py), `load_model_and_tokenizer`, `generate_samples` (model.py), `compute_metrics`/`apply_gate` (evaluate.py)

**Critical finding**: h-e1's actual `run_experiment.py` produces `results/scores.csv` with columns `idx, question, category, label, token_entropy, semantic_entropy, p_true, selfcheck` — **no `max_prob` or `choice_entropy` columns exist**, despite PRD/experiment-brief referencing those baselines (0.8068 / 0.7703). h-m1's `baselines.py` must read whatever columns are actually present in h-e1's `results/scores.csv` and fail gracefully (log a warning, skip missing baseline) rather than assume `max_prob`/`choice_entropy` keys exist. `token_entropy` is the closest available analog to a token-level baseline.

## Fixed Signatures Reused As-Is From h-e1 (verified)

```python
# from h_e1.data import load_truthfulqa_mc1
def load_truthfulqa_mc1(cache_dir: str = CACHE_DIR) -> list[dict]: ...
# returns [{"question": str, "choices": list[str], "correct_idx": int, "category": str}, ...]  len=817

# from h_e1.model import load_model_and_tokenizer, generate_samples
def load_model_and_tokenizer(model_id: str = MODEL_ID) -> tuple: ...  # (model, tokenizer)
def generate_samples(model, tokenizer, prompt: str, n: int = 10, temperature: float = 0.7) -> list[str]: ...
```

---

## M-2/M-3: nli_cluster.py

**Applied**: Standard PyTorch NLI forward pass (DeBERTa-mnli: logits[2] = entailment)

```python
def load_nli_model(model_id: str = NLI_MODEL_ID) -> tuple:
    """Load DeBERTa-v3-large-mnli. Returns (model, tokenizer)."""
    ...

def entailment_prob(nli_model, nli_tokenizer, premise: str, hypothesis: str, device: str = "cuda") -> float:
    """P(entailment). logits: [1, 3] -> softmax[0, 2]."""
    ...

def bidirectional_entailment(nli_model, nli_tokenizer, text1: str, text2: str,
                              threshold: float = 0.7, device: str = "cuda") -> bool:
    """min(P(1->2), P(2->1)) > threshold."""
    ...

def cluster_samples(nli_model, nli_tokenizer, samples: list[str],
                     threshold: float = 0.7, device: str = "cuda") -> list[list[str]]:
    """Greedy clustering vs. first member of each existing cluster."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| nli inputs (input_ids) | [1, L] | L <= 512 (truncated) |
| logits | [1, 3] | [contradiction, neutral, entailment] |
| probs | [1, 3] | softmax(logits) |

### Pseudo-code: greedy clustering (O(k^2) NLI calls, k=len(samples))

```
clusters = [[samples[0]]]
for s in samples[1:]:
    placed = False
    for c in clusters:
        if bidirectional_entailment(c[0], s, threshold):  # 2 NLI calls
            c.append(s); placed = True; break
    if not placed:
        clusters.append([s])
return clusters
```

### Subtasks [4/4 used, M-2] / [4/4 used, M-3]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_nli_model | AutoModelForSequenceClassification + tokenizer load, `.to(device).eval()` |
| L-2-2 | entailment_prob | tokenize(premise, hypothesis) -> logits -> softmax[0,2] |
| L-3-1 | bidirectional_entailment | two entailment_prob calls, min() > threshold |
| L-3-2 | cluster_samples core loop | greedy assignment per pseudo-code above |
| L-3-3 | batching optimization | batch all pairwise NLI calls per question via tokenizer padding, `[k*2, L]` batch |
| L-3-4 | result caching | dict cache keyed by (text1, text2) pair hash to avoid redundant calls |

---

## M-4/M-5: semantic_entropy.py

**Applied**: Standard PyTorch generation loop + scipy.stats.entropy

```python
class SemanticEntropy:
    def __init__(self, llm_model, llm_tokenizer, nli_model, nli_tokenizer,
                 num_samples: int = 10, threshold: float = 0.7, device: str = "cuda"):
        ...

    def compute(self, prompt: str, temperature: float = 0.7, max_tokens: int = 128) -> dict:
        """Generate -> cluster -> entropy. Returns:
        {"semantic_entropy": float, "num_clusters": int,
         "cluster_sizes": list[int], "samples": list[str]}
        """
        ...

def score_dataset(se: SemanticEntropy, questions: list[dict],
                   checkpoint_every: int = 50, checkpoint_path: str | None = None) -> list[dict]:
    """Loop 817 questions. Each result dict merges compute() output +
    {"idx": int, "question": str, "category": str, "correct_idx": int, "label": int}.
    label = 0 if greedy/majority answer matches correct choice else 1 (hallucination)."""
    ...
```

### Pseudo-code: compute()

```
samples = generate_samples(llm_model, llm_tokenizer, prompt, n=num_samples, temperature=temperature)
clusters = cluster_samples(nli_model, nli_tokenizer, samples, threshold=threshold)
sizes = [len(c) for c in clusters]
probs = sizes / sum(sizes)                 # [num_clusters]
H = -sum(p * log(p) for p in probs)        # semantic entropy scalar
return {"semantic_entropy": H, "num_clusters": len(clusters),
        "cluster_sizes": sizes, "samples": samples}
```

### Label Note

Ground truth per PRD FR-4 uses `correct_mc1_answer` match on the *generation*, not `mc1_targets` choice index directly. Reuse h-e1's `get_ground_truth_label(question, response)` pattern: substring match of `choices[correct_idx]` in the response (case-insensitive) -> label 0, else 1. Apply to the first generated sample (or a separate greedy call) as the "answer" for labeling; the N=10 samples are used only for clustering/entropy, not for the label itself.

### Subtasks [3/3 used, M-4] / [2/2 used, M-5]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | SemanticEntropy.__init__ | store model/tokenizer refs + config |
| L-4-2 | compute() | wire generate -> cluster -> entropy pseudo-code above |
| L-4-3 | greedy answer + label | one extra greedy generation call for ground-truth labeling |
| L-5-1 | score_dataset loop | iterate 817 questions, call compute(), attach label |
| L-5-2 | checkpointing | write partial results to JSON every `checkpoint_every` questions (resume safety) |

---

## M-6: baselines.py

**Applied**: pandas CSV read with defensive column check

```python
def load_h_e1_scores(scores_csv_path: str) -> dict[str, list[float]]:
    """Read h-e1 results/scores.csv. Returns {col: [...]} for all numeric
    UQ-method columns present (excludes idx/question/category/label).
    Actual h-e1 columns: token_entropy, semantic_entropy, p_true, selfcheck.
    NOTE: max_prob/choice_entropy (PRD-referenced) are NOT in h-e1's actual
    output; if absent, log a warning and omit from comparison dict."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | read CSV | `pd.read_csv(scores_csv_path)` |
| L-6-2 | column detection | intersect df.columns with known UQ method names, warn on missing max_prob/choice_entropy |
| L-6-3 | index alignment | align by `idx` column against h-m1's question ordering |
| L-6-4 | return dict | `{method: df[method].tolist()}` |

---

## M-7: evaluate.py

**Applied**: sklearn roc_auc_score, standard AUROC + mechanism assertions

```python
def compute_auroc(y_true: list[int], scores: list[float]) -> float:
    """roc_auc_score(y_true, scores). scores: higher = more likely hallucination."""
    ...

def verify_mechanism(results: list[dict]) -> dict:
    """Checks: avg_clusters < num_samples, entropy std > 0, cluster sizes vary.
    Returns {"avg_clusters": float, "entropy_std": float,
             "cluster_size_variety": bool, "passed": bool}"""
    ...

def apply_gate(semantic_auroc: float, threshold: float = 0.70) -> dict:
    """Returns {"gate": "PASSED"|"FAILED", "action": str, "result": str}"""
    ...
```

### Pseudo-code: verify_mechanism

```
avg_clusters = mean([r["num_clusters"] for r in results])
entropies = [r["semantic_entropy"] for r in results]
all_sizes = [s for r in results for s in r["cluster_sizes"]]
passed = (avg_clusters < NUM_SAMPLES) and (std(entropies) > 0) and (len(set(all_sizes)) > 1)
return {"avg_clusters": avg_clusters, "entropy_std": std(entropies),
        "cluster_size_variety": len(set(all_sizes)) > 1, "passed": passed}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_auroc | wraps sklearn roc_auc_score, try/except -> 0.5 fallback on single-class y_true |
| L-7-2 | verify_mechanism | pseudo-code above |
| L-7-3 | apply_gate | 0.70 threshold check, PASSED/FAILED dict |
| L-7-4 | combine into report | build results/metrics.json payload (auroc per method + mechanism + gate) |

---

## M-8: visualize.py

**Applied**: matplotlib standard plots

```python
def plot_auroc_comparison(aurocs: dict[str, float], out_path: str) -> None: ...
def plot_cluster_histogram(results: list[dict], out_path: str) -> None: ...
def plot_score_correlation(semantic_scores: list[float], other_scores: list[float],
                            other_label: str, out_path: str) -> None: ...
def plot_roc_overlay(y_true: list[int], scores: dict[str, list[float]], out_path: str) -> None: ...
```

Note: `other_label` parameterizes correlation baseline since `max_prob` may be unavailable (see M-6); default to `token_entropy` if `max_prob` missing.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | plot_auroc_comparison | bar chart, methods on x-axis |
| L-8-2 | plot_cluster_histogram | hist of `num_clusters` across 817 results |
| L-8-3 | plot_score_correlation | scatter, pick fallback baseline per note above |
| L-8-4 | plot_roc_overlay | sklearn.metrics.roc_curve per method, overlay lines |

---

## M-9: run_experiment.py

```python
def main() -> None:
    """load data -> load LLM + NLI models -> SemanticEntropy.score_dataset ->
    load_h_e1_scores -> compute_auroc (per method) -> verify_mechanism ->
    apply_gate -> visualize -> write results/{scores.csv,metrics.json,cluster_stats.json}"""
    ...
```

### Pseudo-code

```
set_seed(42)
data = load_truthfulqa_mc1()                          # 817 questions
llm_model, llm_tok = load_model_and_tokenizer()
nli_model, nli_tok = load_nli_model()
se = SemanticEntropy(llm_model, llm_tok, nli_model, nli_tok, num_samples=10, threshold=0.7)
results = score_dataset(se, data, checkpoint_every=50)  # 817 dicts
y_true = [r["label"] for r in results]
sem_scores = [r["semantic_entropy"] for r in results]

baseline_scores = load_h_e1_scores(H_E1_SCORES_CSV)     # may lack max_prob/choice_entropy
all_scores = {"semantic_entropy": sem_scores, **baseline_scores}
aurocs = {m: compute_auroc(y_true, s) for m, s in all_scores.items()}

mech = verify_mechanism(results)
gate = apply_gate(aurocs["semantic_entropy"], threshold=0.70)

plot_auroc_comparison(aurocs, ...)
plot_cluster_histogram(results, ...)
plot_score_correlation(sem_scores, baseline_scores.get("max_prob", baseline_scores.get("token_entropy")), ...)
plot_roc_overlay(y_true, all_scores, ...)

write results/scores.csv, results/metrics.json (aurocs + mech + gate), results/cluster_stats.json
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | wire imports + seed | h_e1 imports, config, set_seed(42) |
| L-9-2 | orchestrate pipeline | pseudo-code above end-to-end |
| L-9-3 | checkpoint/resume | reuse score_dataset checkpointing, skip already-scored idx on restart |
| L-9-4 | write results | scores.csv / metrics.json / cluster_stats.json to `results/` |

---

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
def load_truthfulqa_mc1(cache_dir: str = CACHE_DIR) -> list[dict]: ...
# returns [{"question": str, "choices": list[str], "correct_idx": int, "category": str}]

# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
def load_model_and_tokenizer(model_id: str = MODEL_ID) -> tuple: ...  # (model, tokenizer)
def generate_samples(model, tokenizer, prompt: str, n: int = NUM_SAMPLES,
                      temperature: float = TEMPERATURE) -> list[str]: ...

# From: docs/youra_research/h-e1/code/evaluate.py (ACTUAL CODE) — reference pattern only, not imported
def compute_metrics(y_true: list[int], scores: dict[str, list[float]]) -> dict: ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation).
**Discrepancy flagged**: PRD/experiment-brief cite `max_prob` (0.8068) and `choice_entropy` (0.7703) baselines, but h-e1's actual `run_experiment.py`/`scores.csv` never compute or persist these — only `token_entropy`, `semantic_entropy`, `p_true`, `selfcheck` exist. `baselines.py` (M-6) and `visualize.py` (M-8) handle this via graceful column-presence checks and fallback labels; `evaluate.py`'s AUROC comparison will only include whatever baseline columns are actually found in h-e1's `results/scores.csv`.
