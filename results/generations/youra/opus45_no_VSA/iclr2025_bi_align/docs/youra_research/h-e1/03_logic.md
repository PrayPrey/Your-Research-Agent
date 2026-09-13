# Logic: H-E1 Agency Proxy Extraction

**Type:** EXISTENCE (PoC)
**Applied:** sklearn TF-IDF + LogisticRegression text classification pattern (standard pipeline)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## A-1: Dataset Loading [Complexity: 8, Budget: 0 subtasks]

**Applied:** HuggingFace `datasets` load + text extraction pattern

### API Signatures

```python
def load_hh_rlhf() -> list[str]:
    """Load harmless-base + helpful-base test splits, return assistant turns."""
    ...

def load_reward_bench_safety() -> list[str]:
    """Load RewardBench Safety subset, return response texts."""
    ...

def extract_responses(dataset) -> list[str]:
    """dialogue records -> assistant text, whitespace-normalized, lowercased."""
    ...

def build_labels(texts: list[str], proxy: str) -> list[int]:
    """Binary ground-truth labels per proxy via regex match. proxy in config.PROXY_TYPES."""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| texts | list[str], len N (~17,100+) | raw response strings |
| labels | list[int], len N | 0/1 per proxy |

---

## A-2: Regex Pattern Detectors [Complexity: 5, Budget: 0 subtasks]

**Applied:** Standard Python `re` keyword/pattern matching

### API Signatures

```python
class AgencyProxyDetector:
    PROXY_PATTERNS: dict[str, list[str]] = {
        "clarifying_question": [r"what do you mean", r"could you clarify", r"are you asking"],
        "option_enumeration": [r"there are several options", r"you could either", r"^\s*\d+[\.\)]"],
        "epistemic_hedging": [r"i'?m not sure", r"it'?s possible", r"i think", r"\bmaybe\b"],
        "explicit_deferral": [r"recommend consulting", r"a professional would", r"i can'?t advise"],
    }

    def match_pattern(self, text: str, proxy: str) -> bool:
        """True if any regex in PROXY_PATTERNS[proxy] matches text (case-insensitive)."""
        ...
```

### Pseudo-code

```
match_pattern(text, proxy):
    for pattern in PROXY_PATTERNS[proxy]:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

---

## A-3: Label Construction [Complexity: 6, Budget: 0 subtasks]

**Applied:** Direct reuse of `build_labels` (A-1) — regex-derived binary labels, one call per proxy in `config.PROXY_TYPES`.

```python
labels_per_proxy: dict[str, list[int]] = {
    proxy: build_labels(texts, proxy) for proxy in config.PROXY_TYPES
}
# labels_per_proxy[proxy]: list[int], len N, values in {0, 1}
```

---

## A-4: AgencyProxyDetector Classifier [Complexity: 7, Budget: 0 subtasks]

**Applied:** sklearn `Pipeline(TfidfVectorizer, LogisticRegression)`

### API Signatures

```python
def fit(self, texts: list[str], labels: list[int]) -> "AgencyProxyDetector":
    """Fit TfidfVectorizer(**config.TFIDF_PARAMS) + LogisticRegression(**config.LOGREG_PARAMS)."""
    ...

def predict_proba(self, texts: list[str]) -> list[float]:
    """Return P(label=1) per text."""
    ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_tfidf | [N, ≤5000] | sparse TF-IDF matrix, ngram (1,2) |
| y_score | list[float], len N | P(label=1), values in [0,1] |

### Pseudo-code

```
fit(texts, labels):
    X = TfidfVectorizer(ngram_range=(1,2), max_features=5000).fit_transform(texts)
    clf = LogisticRegression(C=1.0, max_iter=1000, random_state=42).fit(X, labels)
    store vectorizer, clf
    return self

predict_proba(texts):
    X = vectorizer.transform(texts)
    return clf.predict_proba(X)[:, 1]
```

---

## A-5: Baseline Models [Complexity: 3, Budget: 0 subtasks]

**Applied:** sklearn `DummyClassifier`

```python
def random_baseline(n: int) -> list[float]:
    """DummyClassifier(strategy='uniform', random_state=42); returns n scores."""
    ...

def majority_baseline(labels: list[int]) -> list[float]:
    """DummyClassifier(strategy='most_frequent') fit on labels; returns len(labels) scores."""
    ...
```

---

## A-6: Evaluation Pipeline [Complexity: 5, Budget: 0 subtasks]

**Applied:** `sklearn.metrics.roc_auc_score`

```python
def compute_auroc(y_true: list[int], y_score: list[float]) -> float:
    """sklearn.metrics.roc_auc_score(y_true, y_score)."""
    ...

def evaluate_all_proxies(detector_results: dict) -> dict[str, float]:
    """detector_results: {proxy: (y_true, y_score)} -> {proxy: auroc}."""
    ...
```

### Pseudo-code

```
evaluate_all_proxies(detector_results):
    results = {}
    for proxy, (y_true, y_score) in detector_results.items():
        results[proxy] = compute_auroc(y_true, y_score)
    return results
```

---

## A-7: Visualization [Complexity: 6, Budget: 0 subtasks]

**Applied:** matplotlib bar chart + subplot grid

```python
def plot_auroc_bar(results: dict[str, float], out_path: str) -> None:
    """Bar per proxy, horizontal line at config.AUROC_TARGET (0.8)."""
    ...

def plot_roc_curves(results: dict, out_path: str) -> None:
    """4 subplots (2x2), one ROC curve (fpr,tpr) per proxy via sklearn.metrics.roc_curve."""
    ...

def plot_cooccurrence_heatmap(labels: dict, out_path: str) -> None:
    """Optional: proxy x proxy co-occurrence matrix, imshow."""
    ...
```

---

## A-8: Integration + Run [Complexity: 7, Budget: 0 subtasks]

**Applied:** Standard script entrypoint

```python
def main() -> None: ...
```

### Pseudo-code

```
main():
    texts = load_hh_rlhf() + load_reward_bench_safety()
    texts = extract_responses(texts)
    detector_results = {}
    for proxy in config.PROXY_TYPES:
        labels = build_labels(texts, proxy)
        detector = AgencyProxyDetector().fit(texts, labels)
        y_score = detector.predict_proba(texts)
        detector_results[proxy] = (labels, y_score)
        baselines: random_baseline(len(texts)), majority_baseline(labels)
    results = evaluate_all_proxies(detector_results)
    plot_auroc_bar(results, f"{config.FIGURES_DIR}/auroc_bar.png")
    plot_roc_curves(detector_results, f"{config.FIGURES_DIR}/roc_curves.png")
    mean_auroc = mean(results.values())
    print(PASS if mean_auroc >= config.AUROC_TARGET else FAIL)
```

---

## Subtasks

No subtasks — budget is 0 (PoC scope, all tasks Low complexity, signatures fully specified above).
