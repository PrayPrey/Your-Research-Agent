# Logic: H-M2 BAI-Reward Disagreement Analysis

**Type:** MECHANISM

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** API signatures verified from actual H-E1 code (`h-e1/code/model.py`, `data.py`, `config.py`)
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:** `AgencyProxyDetector.{__init__,fit,predict_proba}`, `load_hh_rlhf`, `load_reward_bench_safety`, `extract_responses`, `build_labels`, `config.{PROXY_TYPES,PROXY_PATTERNS,TFIDF_PARAMS,LOGREG_PARAMS,RANDOM_STATE}`

**Critical deviation from PRD/architecture assumption:** `load_hh_rlhf()` and `load_reward_bench_safety()` return a **flat `list[str]`** of already-extracted assistant response texts (no prompt, no chosen/rejected pairing — that structure is discarded inside `extract_responses`/the loader loop). H-M2's `reward.compute_reward_scores(prompts, responses, ...)` therefore **cannot get real prompts from these loaders**. Logic below uses an empty-string prompt fallback for reward scoring (reward model still scores response quality on its own; PRD's "prompt-response pairs" requirement is satisfied only at the response-text level, not true dialogue pairs). Documented as a known limitation, not solved by rewriting H-E1's `data.py` (out of scope / would break H-E1 contract).

---

## Applied Patterns

Applied: sklearn StandardScaler + quartile quadrant-counting for disagreement analysis
Applied: HF AutoModelForSequenceClassification batched scoring (RewardBench pattern) — Archon KB had no closer match; using standard `transformers` sequence-classification inference pattern (num_labels=1 regression head, standard for OpenAssistant reward models)

---

## External Dependencies API (h-e1/code, verified)

```python
# From: h-e1/code/model.py
class AgencyProxyDetector:
    def __init__(self): ...                       # self.vectorizer=None, self.classifier=None
    def fit(self, texts: list[str], labels: list[int]) -> "AgencyProxyDetector": ...
    def predict_proba(self, texts: list[str]) -> list[float]: ...  # P(label=1) per text

# From: h-e1/code/data.py
def load_hh_rlhf() -> list[str]: ...                    # flat response texts, no prompts
def load_reward_bench_safety() -> list[str]: ...        # flat response texts, no prompts
def build_labels(texts: list[str], proxy: str) -> list[int]: ...  # regex-based ground truth

# From: h-e1/code/config.py
PROXY_TYPES: list[str]
PROXY_PATTERNS: dict[str, list[str]]
TFIDF_PARAMS: dict
LOGREG_PARAMS: dict
RANDOM_STATE: int = 42
```

**Import wiring** (h-e1 has no `__init__.py`, flat module names):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code"))
import config as e1_config
from data import load_hh_rlhf, load_reward_bench_safety, build_labels
from model import AgencyProxyDetector
```

---

## config.py

```python
RANDOM_STATE = 42
REWARD_MODEL_NAME = "OpenAssistant/reward-model-deberta-v3-large-v2"
MAX_TOKENS = 512
BATCH_SIZE = 32
LENGTH_NORM_COEF = 0.1
DISAGREEMENT_THRESHOLD = 0.20
PARTIAL_THRESHOLD = 0.10
MIN_SAMPLE_COUNT = 500
FIGURES_DIR = "h-m2/figures"
```

---

## bai.py

```python
def train_proxy_detectors() -> dict[str, AgencyProxyDetector]:
    """Fit one detector per e1_config.PROXY_TYPES using HH-RLHF texts + build_labels."""
    # texts = load_hh_rlhf()
    # for proxy in e1_config.PROXY_TYPES: labels = build_labels(texts, proxy); detectors[proxy] = AgencyProxyDetector().fit(texts, labels)
    ...

def compute_bai_scores(responses: list[str], detectors: dict[str, AgencyProxyDetector]) -> list[float]:
    """Mean of 4 detector.predict_proba(responses), then per-item length_normalize. Returns [N] BAI scores."""
    ...

def length_normalize(raw_bai: float, response: str) -> float:
    """raw_bai / (1 + LENGTH_NORM_COEF * log(word_count)); word_count = len(response.split()), min 1."""
    ...
```

---

## reward.py

```python
def load_reward_model() -> tuple:
    """AutoModelForSequenceClassification.from_pretrained(REWARD_MODEL_NAME) + AutoTokenizer, .to(device), device = 'cuda' if available else 'cpu'. Returns (model, tokenizer)."""
    ...

def compute_reward_scores(prompts: list[str], responses: list[str], model, tokenizer) -> list[float]:
    """Batched (BATCH_SIZE) inference: tokenizer(prompts[i:i+B], responses[i:i+B], truncation=True,
    max_length=MAX_TOKENS, padding=True, return_tensors='pt') -> model(**inputs).logits.squeeze(-1) -> list[float].
    prompts may be [""] * len(responses) when true prompt unavailable (see Codebase Analysis note)."""
    ...
```

Tensor shapes:

| Variable | Shape | Note |
|----------|-------|------|
| logits | [B] | squeezed regression head output per batch |

---

## analysis.py

```python
def compute_disagreement_rate(bai_scores: "np.ndarray", reward_scores: "np.ndarray") -> dict:
    """StandardScaler on both -> z-scores. q25/q75 via np.percentile(z, [25,75]).
    Quadrants: HH=(bai_z>=q75_bai)&(rw_z>=q75_rw); HL=(bai_z>=q75_bai)&(rw_z<=q25_rw);
    LH=(bai_z<=q25_bai)&(rw_z>=q75_rw); LL=(bai_z<=q25_bai)&(rw_z<=q25_rw).
    disagreement_rate = (HL.sum()+LH.sum()) / len(bai_scores).
    Returns {disagreement_rate, hh_count, hl_count, lh_count, ll_count, bai_z, reward_z, q_bounds}."""
    ...

def compute_correlations(bai_scores, reward_scores) -> dict:
    """scipy.stats.pearsonr + spearmanr. Returns {pearson_r, pearson_p, spearman_r, spearman_p}."""
    ...

def verify_mechanism(results: dict) -> dict:
    """Checks: var(bai)>0.01, var(reward)>0.01, 0<disagreement_rate<0.5, n>=MIN_SAMPLE_COUNT.
    Returns {**checks_dict, verification_passed: bool}."""
    ...
```

---

## evaluate.py

```python
def plot_gate_bar(disagreement_rate: float, out_path: str) -> None: ...       # bar vs 0.20 threshold line, mandatory
def plot_scatter_quadrants(bai_z: "np.ndarray", reward_z: "np.ndarray", q_bounds: dict, out_path: str) -> None: ...
def plot_density_heatmap(bai_z: "np.ndarray", reward_z: "np.ndarray", out_path: str) -> None: ...
def plot_distributions(bai_scores: "np.ndarray", reward_scores: "np.ndarray", out_path: str) -> None: ...
def top_disagreement_examples(responses: list[str], bai_z: "np.ndarray", reward_z: "np.ndarray", n: int = 10) -> dict:
    """Sort by |bai_z - reward_z| desc, return top-n {response, bai_z, reward_z} dicts."""
    ...
```

---

## run.py

```python
def main() -> str:
    """Pipeline: load_hh_rlhf()+load_reward_bench_safety() -> responses[] ->
    train_proxy_detectors() -> compute_bai_scores() ->
    load_reward_model() -> compute_reward_scores(prompts=[""]*N, responses) ->
    compute_disagreement_rate() -> compute_correlations() -> verify_mechanism() ->
    evaluate.plot_* (save to config.FIGURES_DIR) -> save results.json ->
    gate: 'PASS' if rate>=0.20 else 'PARTIAL' if rate>=0.10 else 'FAIL'.
    Returns gate_result string."""
    ...
```

---

## Subtasks

None (all Low complexity, budget 0).
