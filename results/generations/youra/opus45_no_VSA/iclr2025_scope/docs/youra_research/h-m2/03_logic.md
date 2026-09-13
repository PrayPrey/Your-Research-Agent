# Logic: H-M2 (Robustness of Routing to Paraphrase/Masking)

Applied: sklearn-Pipeline-Evaluation-Pattern (frozen encoder + linear probe, no training loop)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/{model.py, data.py, config.py}`
**Relevant Symbols**:
- `model.py::AdapterSelectionProbe` — `__init__(encoder_name, num_classes, max_iter=2000, solver="lbfgs", random_state=42)`, `encode`, `fit`, `predict`, `predict_proba`, `evaluate(texts, labels, k=3) -> {"top1_accuracy", "top3_accuracy"}`
- `data.py::stream_instructions(cfg) -> (samples: List[Dict], task_families: List[str])`
- `data.py::encode_labels(samples, task_families) -> List[int]`
- `data.py::stratified_split(samples, labels, cfg) -> {"train": (X,y), "val": (X,y), "test": (X,y)}`
- `config.py::Config` dataclass + `CONFIG` singleton; `random_state=42` throughout

**Deviation from PRD**: no `probe_model.pkl` is ever saved by H-E1 `train.py`. H-M2 must reconstruct the probe in-process using the exact same `CONFIG` and call order (`stream_instructions` → `encode_labels` → `stratified_split` → `AdapterSelectionProbe.fit`) to get an equivalent fitted probe + the same 450-sample test split (seed=42 guarantees identical split).

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
from h_e1.config import CONFIG, Config  # CONFIG is a pre-built Config() singleton, random_state=42

# From: docs/youra_research/h-e1/code/data.py (ACTUAL CODE)
from h_e1.data import stream_instructions, encode_labels, stratified_split
def stream_instructions(cfg: Config) -> tuple[list[dict], list[str]]: ...
    # dict: {"text": str, "task_family": str}
def encode_labels(samples: list[dict], task_families: list[str]) -> list[int]: ...
def stratified_split(samples: list[dict], labels: list[int], cfg: Config) -> dict[str, tuple[list[str], list[int]]]: ...
    # keys: "train", "val", "test" -> (X: list[str], y: list[int])

# From: docs/youra_research/h-e1/code/model.py (ACTUAL CODE)
from h_e1.model import AdapterSelectionProbe
class AdapterSelectionProbe:
    def __init__(self, encoder_name: str, num_classes: int, max_iter: int = 2000,
                 solver: str = "lbfgs", random_state: int = 42): ...
    def encode(self, texts: list[str]) -> np.ndarray: ...       # -> [N, 384]
    def fit(self, texts: list[str], labels: list[int]) -> None: ...
    def predict(self, texts: list[str]) -> np.ndarray: ...      # -> [N]
    def predict_proba(self, texts: list[str]) -> np.ndarray: ... # -> [N, C]
    def evaluate(self, texts: list[str], labels: list[int], k: int = 3) -> dict[str, float]: ...
        # {"top1_accuracy": float, "top3_accuracy": float}
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation; `probe_model.pkl` referenced in PRD does not exist — reconstruct in-process instead).

**Reuse note**: `AdapterSelectionProbe.__init__` requires `num_classes = len(task_families)` (from `stream_instructions`), and `encoder_name = CONFIG.encoder_name`. No code changes needed to H-E1 files.

---

## A-1: Reconstruct H-E1 probe context [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch/sklearn reuse — deterministic reconstruction via shared seed

### API Signatures

```python
# code/reuse_probe.py
from dataclasses import dataclass
from h_e1.config import CONFIG
from h_e1.data import stream_instructions, encode_labels, stratified_split
from h_e1.model import AdapterSelectionProbe

@dataclass
class ProbeContext:
    probe: AdapterSelectionProbe
    X_test: list[str]     # 450 samples (H-E1 15% test split)
    y_test: list[int]
    task_families: list[str]

def build_probe_context(m_cfg: "MConfig") -> ProbeContext:
    """Re-run H-E1 pipeline in-process; same seed => same split + equivalent fitted probe."""
    ...
```

### Pseudo-code

```
1. samples, task_families = stream_instructions(CONFIG)          # seed=42, deterministic family discovery
2. labels = encode_labels(samples, task_families)
3. splits = stratified_split(samples, labels, CONFIG)             # {"train","val","test"}
4. X_train, y_train = splits["train"]
5. X_test, y_test = splits["test"]                                 # ~450 samples
6. probe = AdapterSelectionProbe(CONFIG.encoder_name, num_classes=len(task_families),
                                  max_iter=CONFIG.max_iter, solver=CONFIG.solver,
                                  random_state=CONFIG.random_state)
7. probe.fit(X_train, y_train)
8. return ProbeContext(probe, X_test, y_test, task_families)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Import H-E1 modules | Wire h_e1.config/data/model (relative import from h-m2/code) |
| L-1-2 | Replay pipeline | stream_instructions → encode_labels → stratified_split, same CONFIG |
| L-1-3 | Fit probe | Instantiate AdapterSelectionProbe with CONFIG params, fit on X_train/y_train |
| L-1-4 | Assemble context | Return ProbeContext dataclass with test split + task_families |

---

## A-2: Config module [Complexity: 4, Budget: 4]

**Applied**: dataclass-config-pattern (mirrors H-E1 `Config`)

### API Signatures

```python
# code/config.py
from dataclasses import dataclass

@dataclass
class MConfig:
    wordnet_pct_swap: float = 0.3
    wordnet_n: int = 5
    embedding_n: int = 3
    embedding_min_cosine: float = 0.8
    mask_ratios: tuple[float, float] = (0.2, 0.5)
    random_state: int = 42  # must match H-E1

M_CONFIG = MConfig()

# Gate thresholds
COSINE_PASS = 0.90
COSINE_FAIL = 0.80
ACC_DROP_PASS = 0.10
ACC_DROP_FAIL = 0.20
ROUTING_CONSISTENCY_PASS = 0.85
ROUTING_CONSISTENCY_FAIL = 0.70
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | MConfig dataclass | Perturbation params |
| L-2-2 | Threshold constants | Gate PASS/FAIL constants |
| L-2-3 | Singleton | M_CONFIG instance |
| L-2-4 | Docstring/comments | Note random_state must match H-E1 |

---

## A-3: WordNet paraphrase generator [Complexity: 8, Budget: 8]

**Applied**: TextAttack-Augmenter-wrapper-pattern

### API Signatures

```python
# code/perturb.py
from textattack.augmentation import WordNetAugmenter

class PerturbationEngine:
    def __init__(self, m_cfg: "MConfig"):
        self._wordnet_aug = WordNetAugmenter(
            pct_words_to_swap=m_cfg.wordnet_pct_swap, transformations_per_example=m_cfg.wordnet_n
        )
        self.m_cfg = m_cfg

    def wordnet_paraphrases(self, text: str) -> list[str]:
        """Returns up to m_cfg.wordnet_n synonym-substituted variants of text."""
        ...
```

### Tensor Shapes

| Variable | Shape/Type | Note |
|----------|------------|------|
| text | str | single instruction (256-char prefix) |
| output | list[str], len ≤ 5 | wordnet_n paraphrases |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Init augmenter | WordNetAugmenter(pct_words_to_swap, transformations_per_example) |
| L-3-2 | wordnet_paraphrases | Call `.augment(text)`, cap at wordnet_n, dedupe |
| L-3-3 | Edge cases | Handle short/empty text (skip augmentation, return [text]) |
| L-3-4 | Batch helper | Optional loop wrapper for list[str] input |

---

## A-4: Embedding paraphrase generator [Complexity: 8, Budget: 8]

**Applied**: TextAttack-Augmenter-wrapper-pattern + cosine filter

### API Signatures

```python
from textattack.augmentation import EmbeddingAugmenter
from sklearn.metrics.pairwise import cosine_similarity

class PerturbationEngine:  # continued
    def __init__(self, m_cfg: "MConfig"):
        ...
        self._embed_aug = EmbeddingAugmenter(transformations_per_example=m_cfg.embedding_n)

    def embedding_paraphrases(self, text: str) -> list[str]:
        """Counter-fitted embedding-neighbor substitution, filtered by embedding_min_cosine."""
        ...
```

### Pseudo-code

```
1. candidates = self._embed_aug.augment(text)   # up to embedding_n variants
2. emb_orig, emb_cands = probe.encode([text] + candidates)   # [1+K, 384]
3. sims = cosine_similarity(emb_orig, emb_cands)[0]          # [K]
4. return [c for c, s in zip(candidates, sims) if s >= m_cfg.embedding_min_cosine]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Init augmenter | EmbeddingAugmenter(transformations_per_example) |
| L-4-2 | Generate candidates | `.augment(text)` |
| L-4-3 | Cosine filter | Encode via probe.encoder, filter by embedding_min_cosine |
| L-4-4 | Fallback | If none pass filter, return empty list (handled downstream) |

---

## A-5: Keyword + random masking [Complexity: 9, Budget: 9]

**Applied**: nlpaug-TfIdfAug-pattern + random baseline control

### API Signatures

```python
import nlpaug.augmenter.word as naw
import random

class PerturbationEngine:  # continued
    def __init__(self, m_cfg: "MConfig"):
        ...
        self._tfidf_augs = {r: naw.TfIdfAug(model_path=..., aug_p=r) for r in m_cfg.mask_ratios}

    def mask_keywords(self, text: str, ratio: float) -> str:
        """TF-IDF-weighted keyword removal at given ratio (0.2 or 0.5)."""
        ...

    def mask_random(self, text: str, ratio: float) -> str:
        """Control baseline: mask `ratio` fraction of random (non-keyword) words."""
        ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | TF-IDF model fit | Fit TfIdfAug's TF-IDF stats on H-M2 test corpus (X_test) |
| L-5-2 | mask_keywords | Apply TfIdfAug at ratio, return masked string |
| L-5-3 | mask_random | Random-word masking control (same ratio, uniform sampling) |
| L-5-4 | Structure preservation | Replace masked tokens with `[MASK]`/blank, keep sentence length stable |

---

## A-6: Cosine/routing metrics [Complexity: 10, Budget: 10]

**Applied**: sklearn cosine_similarity + majority-vote-routing-consistency pattern

### API Signatures

```python
# code/robustness_eval.py
def eval_paraphrase_robustness(
    ctx: "ProbeContext", engine: "PerturbationEngine", variant: str  # "wordnet" | "embedding"
) -> dict:
    """cosine_mean/min + routing_consistency across all paraphrases of variant."""
    ...
    # returns: {"cosine_mean": float, "cosine_min": float,
    #           "routing_consistency": float, "per_sample": list[dict]}
```

### Pseudo-code

```
1. orig_emb = ctx.probe.encode(ctx.X_test)              # [450, 384]
2. orig_pred = ctx.probe.classifier.predict(orig_emb)   # [450]
3. for each x_i, y_i in zip(X_test, orig_pred):
     paras = engine.wordnet_paraphrases(x_i) if variant=="wordnet" else engine.embedding_paraphrases(x_i)
     if not paras: continue
     para_emb = ctx.probe.encode(paras)                 # [K, 384]
     sims = cosine_similarity(orig_emb[i:i+1], para_emb)[0]   # [K]
     para_preds = ctx.probe.classifier.predict(para_emb)      # [K]
     consistent = (para_preds == y_i)
     record per_sample: {text, sims, consistent}
4. cosine_mean/min = aggregate over all per_sample sims
5. routing_consistency = mean(all consistent flags)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Original embeddings/preds | Encode + predict X_test once, cache |
| L-6-2 | Per-sample paraphrase loop | Generate + encode paraphrases per variant |
| L-6-3 | Cosine + consistency calc | cosine_similarity + prediction match |
| L-6-4 | Aggregate | mean/min cosine, overall routing_consistency, per_sample list |

---

## A-7: Accuracy drop metrics [Complexity: 8, Budget: 8]

**Applied**: original-vs-perturbed accuracy delta pattern

### API Signatures

```python
def eval_masking_robustness(
    ctx: "ProbeContext", engine: "PerturbationEngine", ratio: float, mode: str  # "keyword" | "random"
) -> dict:
    """original_acc vs masked_acc for given ratio/mode."""
    ...
    # returns: {"original_acc": float, "masked_acc": float, "accuracy_drop": float}
```

### Pseudo-code

```
1. orig_metrics = ctx.probe.evaluate(ctx.X_test, ctx.y_test, k=3)   # top1_accuracy
2. masked_texts = [engine.mask_keywords(x, ratio) if mode=="keyword" else engine.mask_random(x, ratio)
                    for x in ctx.X_test]
3. masked_metrics = ctx.probe.evaluate(masked_texts, ctx.y_test, k=3)
4. accuracy_drop = orig_metrics["top1_accuracy"] - masked_metrics["top1_accuracy"]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Original accuracy | probe.evaluate(X_test, y_test) baseline |
| L-7-2 | Mask corpus | Apply mask_keywords/mask_random per ratio+mode |
| L-7-3 | Masked accuracy | probe.evaluate(masked_texts, y_test) |
| L-7-4 | Drop calc | original_acc - masked_acc, return dict |

---

## A-8: Per-class robustness aggregation [Complexity: 6, Budget: 6]

**Applied**: groupby-aggregation pattern

### API Signatures

```python
def per_class_consistency(ctx: "ProbeContext", results: list[dict]) -> dict[str, float]:
    """class_name -> consistency rate, for heatmap. results = per_sample records from A-6."""
    ...
```

### Pseudo-code

```
1. y_test labels -> task_families[label] gives class name per sample
2. group per_sample records by class name
3. consistency_rate[class] = mean(consistent flags in group)
4. return dict[class_name, float]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Group by class | Map y_test idx -> task_families name, bucket per_sample records |
| L-8-2 | Aggregate rate | mean consistency per class, return dict |

---

## A-9: Visualization suite [Complexity: 9, Budget: 9]

**Applied**: matplotlib/seaborn subplot pattern (mirrors H-E1 `evaluate.py` plot functions)

### API Signatures

```python
# code/visualize.py
def plot_gate_metrics(cosine_mean: float, acc_drop: float, path: str) -> None: ...
def plot_cosine_distribution(cosine_values: list[float], path: str) -> None: ...
def plot_drop_by_perturbation(drops: dict[str, float], path: str) -> None: ...
def plot_per_class_heatmap(per_class: dict[str, float], path: str) -> None: ...
def plot_failure_cases(failures: list[dict], path: str, n: int = 5) -> None: ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Gate + distribution plots | Bar chart (cosine/drop vs threshold) + cosine histogram |
| L-9-2 | Drop-by-type + heatmap | Bar chart per perturbation type, seaborn heatmap per class |
| L-9-3 | Failure cases | Table/text render of top-n routing-inconsistent examples |

---

## A-10: Orchestration + gate check [Complexity: 8, Budget: 8]

**Applied**: sklearn-Pipeline-Evaluation-Pattern orchestration (mirrors H-E1 `train.py`)

### API Signatures

```python
# code/train.py
def main() -> str:  # "PASS" | "PARTIAL" | "FAIL"
    ...
```

### Pseudo-code

```
1. ctx = build_probe_context(M_CONFIG)
2. engine = PerturbationEngine(M_CONFIG)
3. wordnet_res = eval_paraphrase_robustness(ctx, engine, "wordnet")
4. embed_res   = eval_paraphrase_robustness(ctx, engine, "embedding")
5. mask20_res  = eval_masking_robustness(ctx, engine, 0.2, "keyword")
6. mask50_res  = eval_masking_robustness(ctx, engine, 0.5, "keyword")
7. rand_res    = eval_masking_robustness(ctx, engine, 0.5, "random")   # control
8. per_class = per_class_consistency(ctx, wordnet_res["per_sample"] + embed_res["per_sample"])
9. cosine_mean = mean(wordnet_res["cosine_mean"], embed_res["cosine_mean"])
10. acc_drop = max(mask20_res["accuracy_drop"], mask50_res["accuracy_drop"])
11. gate = "PASS" if cosine_mean>=COSINE_PASS and acc_drop<ACC_DROP_PASS else \
           "FAIL" if cosine_mean<COSINE_FAIL or acc_drop>ACC_DROP_FAIL else "PARTIAL"
12. dump results to outputs/results.csv + experiment_results.json
13. call all plot_* functions from visualize.py
14. return gate
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Wire pipeline | Call build_probe_context, PerturbationEngine, all eval_* functions |
| L-10-2 | Gate logic | PASS/PARTIAL/FAIL per thresholds in config.py |
| L-10-3 | Persist results | JSON (experiment_results.json) + CSV (outputs/results.csv) |
| L-10-4 | Trigger visualization | Call all 5 plot_* functions with computed metrics |
