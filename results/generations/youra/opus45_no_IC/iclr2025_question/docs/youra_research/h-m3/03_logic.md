# Logic: H-M3 (MECHANISM)

**Applied**: No relevant KB pattern (Archon returned unrelated diffusers docs); using sklearn.metrics.roc_curve standard threshold-at-FPR calibration + scipy percentile bootstrap.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code (differ from architecture doc draft — corrected below)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `ResponseGenerator.generate_n(question: str, n: int = N_GENERATIONS) -> List[Dict]` — each dict is `{"text": str, "logprob": float, "token_logprobs": list[float]}`. **Not** a `(responses, logprobs)` tuple as architecture doc implied.
- `EntailmentClusterer.cluster(responses: List[str], question: str) -> List[List[int]]` — matches architecture doc.
- `compute_semantic_entropy(responses: List[str], logprobs: List[float], clusterer: EntailmentClusterer, question: str) -> float` — takes separate `responses`/`logprobs` lists, not raw generate_n output. Caller must unpack.
- `label_responses(responses: List[str], gold_aliases: List[str]) -> List[bool]` — matches architecture doc.

**⚠️ Correction for Phase 4**: `entropy_pipeline.py` must unpack `generate_n` dicts into `texts = [r["text"] for r in gen]` and `logprobs = [r["logprob"] for r in gen]` before calling `label_responses(texts, aliases)` and `compute_semantic_entropy(texts, logprobs, clusterer, question)`.

---

## M3-2: Wire H-M1 pipeline classes [Complexity: 10, Budget: 10]

**Applied**: Adapter/wrapper pattern — thin function wraps external class instances, no new classes.

### API Signatures

```python
# entropy_pipeline.py
from h_m1.code.response_generator import ResponseGenerator
from h_m1.code.entailment_clusterer import EntailmentClusterer
from h_m1.code.semantic_entropy import compute_semantic_entropy
from h_m1.code.correctness import label_responses

def compute_entropy_and_labels(
    items: list[dict],  # [{"question": str, "aliases": list[str]}]
    generator: ResponseGenerator,
    clusterer: EntailmentClusterer,
    n_generations: int = N_GENERATIONS,
) -> tuple[np.ndarray, np.ndarray]:
    """Per query: generate_n -> unpack -> label_responses -> compute_semantic_entropy.
    Returns: (entropies[N] float64, labels[N] bool) — labels = any(response correct)."""
```

### Pseudo-code

```
for item in items:
    gen = generator.generate_n(item["question"], n=n_generations)   # List[Dict]
    texts = [r["text"] for r in gen]
    logprobs = [r["logprob"] for r in gen]
    correct = label_responses(texts, item["aliases"])                # List[bool]
    label = any(correct)
    se = compute_semantic_entropy(texts, logprobs, clusterer, item["question"])
    entropies.append(se); labels.append(label)
return np.array(entropies), np.array(labels)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-2-1 | Init wrappers | Instantiate ResponseGenerator(GEN_MODEL), EntailmentClusterer(NLI_MODEL) once in run.py, pass down |
| L-M3-2-2 | Unpack adapter | Implement generate_n dict -> texts/logprobs unpack inline in compute_entropy_and_labels |
| L-M3-2-3 | Per-query loop | Loop items, call label_responses + compute_semantic_entropy per query |
| L-M3-2-4 | Return arrays | Stack into np.ndarray entropies/labels, dtype float64/bool |

---

## M3-3: Entropy computation + caching [Complexity: 12, Budget: 12]

**Applied**: Standard PyTorch — numpy .npy cache-or-compute pattern (no KB match).

### API Signatures

```python
# entropy_pipeline.py (cont.)
def get_or_compute_benchmark_entropy(
    name: str,
    calib_items: list[dict],
    eval_items: list[dict],
    generator: ResponseGenerator,
    clusterer: EntailmentClusterer,
    cache_dir: str = OUTPUTS_DIR,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load cached {cache_dir}/entropy_{name}_calib.npy etc, else compute + save.
    Returns: (calib_entropies, calib_labels, eval_entropies, eval_labels)."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| calib_entropies | [700] | float64, per-benchmark |
| calib_labels | [700] | bool |
| eval_entropies | [300] | float64 |
| eval_labels | [300] | bool |

### Pseudo-code

```
cache_paths = {split: f"{cache_dir}/entropy_{name}_{split}.npy" for split in ["calib","eval"]}
label_paths = {split: f"{cache_dir}/labels_{name}_{split}.npy" for split in ["calib","eval"]}
if all(os.path.exists(p) for p in [*cache_paths.values(), *label_paths.values()]):
    load and return
else:
    calib_e, calib_l = compute_entropy_and_labels(calib_items, generator, clusterer)
    eval_e, eval_l = compute_entropy_and_labels(eval_items, generator, clusterer)
    np.save each to cache_dir (mkdir -p first)
    return calib_e, calib_l, eval_e, eval_l
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-3-1 | Cache-check | Build cache_dir paths per benchmark/split, check existence |
| L-M3-3-2 | Compute calib | Call compute_entropy_and_labels on calib_items (700) |
| L-M3-3-3 | Compute eval | Call compute_entropy_and_labels on eval_items (300), save all 4 arrays via np.save |
| L-M3-3-4 | Loop 6 benchmarks | Wrap in run.py loop over BENCHMARKS, collect dict[name -> 4-tuple] |

---

## calibration.py

**Applied**: sklearn.metrics.roc_curve threshold-at-target-FPR (standard pattern, no KB match).

```python
from sklearn.metrics import roc_curve, roc_auc_score

def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float = TARGET_FPR) -> float:
    """Threshold on entropy such that FPR (incorrect flagged as low-entropy) ~= target_fpr.
    labels=True means correct; hallucination flagged when entropy > threshold.
    Uses roc_curve on (1-labels) vs entropies, picks threshold at closest fpr <= target_fpr."""
    fpr, tpr, thresholds = roc_curve(~labels.astype(bool), entropies)
    idx = np.argmin(np.abs(fpr - target_fpr))
    return float(thresholds[idx])

def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """AUROC of entropies vs (1-correct) as hallucination score; threshold reported for reference."""
    auroc = roc_auc_score(~target_labels.astype(bool), target_entropies)
    return {"auroc": float(auroc), "threshold_used": source_threshold}

def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float:
    return source_auroc - target_auroc
```

---

## transfer.py

**Applied**: Standard Python — nested loop over directional pairs, dict aggregation.

```python
def run_pair_transfer(source: str, target: str, entropy_cache: dict) -> dict:
    """entropy_cache[name] = (calib_e, calib_l, eval_e, eval_l).
    Calibrate threshold + AUROC on source eval split; evaluate transfer on target eval split."""
    _, _, src_eval_e, src_eval_l = entropy_cache[source]
    _, _, tgt_eval_e, tgt_eval_l = entropy_cache[target]
    src_calib_e, src_calib_l, _, _ = entropy_cache[source]

    threshold = calibrate_threshold(src_calib_e, src_calib_l, TARGET_FPR)
    source_result = evaluate_transfer(threshold, src_eval_e, src_eval_l)
    target_result = evaluate_transfer(threshold, tgt_eval_e, tgt_eval_l)
    degradation = compute_auroc_degradation(source_result["auroc"], target_result["auroc"])

    return {"source": source, "target": target,
            "source_auroc": source_result["auroc"], "target_auroc": target_result["auroc"],
            "degradation": degradation, "source_threshold": threshold}

def run_all_transfers(pairs: list[tuple[str, str]], entropy_cache: dict) -> list[dict]:
    """Runs both directions per pair -> 12 results."""
    results = []
    for a, b in pairs:
        results.append(run_pair_transfer(a, b, entropy_cache))
        results.append(run_pair_transfer(b, a, entropy_cache))
    return results
```

---

## stats.py

**Applied**: scipy percentile bootstrap (standard pattern, no KB match).

```python
import numpy as np

def bootstrap_ci(degradations: list[float], n_bootstrap: int = N_BOOTSTRAP, ci: float = 0.95) -> tuple[float, float]:
    """Percentile bootstrap on the mean. Returns (ci_lower, ci_upper)."""
    rng = np.random.default_rng(SEED)
    arr = np.array(degradations)
    means = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(n_bootstrap)]
    alpha = (1 - ci) / 2
    return float(np.percentile(means, 100 * alpha)), float(np.percentile(means, 100 * (1 - alpha)))

def aggregate_results(transfer_results: list[dict]) -> dict:
    degs = [r["degradation"] for r in transfer_results]
    ci_lower, ci_upper = bootstrap_ci(degs)
    return {"mean_degradation": float(np.mean(degs)), "ci_lower": ci_lower,
            "ci_upper": ci_upper, "max_degradation": float(np.max(degs))}

def check_gate(agg: dict) -> bool:
    return agg["mean_degradation"] <= DEGRADATION_THRESHOLD and agg["ci_upper"] < CI_UPPER_THRESHOLD
```

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/response_generator.py (ACTUAL CODE, verified via Serena)
class ResponseGenerator:
    def generate_n(self, question: str, n: int = N_GENERATIONS) -> List[Dict]:
        """Returns: [{"text": str, "logprob": float, "token_logprobs": list[float]}]"""

# From: h-m1/code/entailment_clusterer.py
class EntailmentClusterer:
    def cluster(self, responses: List[str], question: str) -> List[List[int]]: ...

# From: h-m1/code/semantic_entropy.py
def compute_semantic_entropy(responses: List[str], logprobs: List[float],
                              clusterer: EntailmentClusterer, question: str) -> float: ...

# From: h-m1/code/correctness.py
def label_responses(responses: List[str], gold_aliases: List[str]) -> List[bool]: ...
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation via Serena `find_symbol`, not architecture doc draft).
