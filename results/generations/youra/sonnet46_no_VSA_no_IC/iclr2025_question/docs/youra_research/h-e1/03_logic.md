# Logic Design: H-E1 — Token-Level Log-Probability Aggregation Ablation

**Date:** 2026-08-21
**Hypothesis:** H-E1 (EXISTENCE / LIGHT)
**Phase:** 3 - Implementation Planning

Applied: single-responsibility module pattern (each module owns one concern; no circular imports)
Applied: guard-clause early-return pattern (empty-generation filter before aggregation)

---

## Codebase Analysis (Serena)

Green-field: no existing codebase. Serena not applicable.
Archon KB search performed for "DL API design patterns" and "log probability hallucination detection" — no relevant results (KB contains diffusion model content). Patterns applied from literature (Farquhar 2023, lm-polygraph).

---

## Subtasks

---

### L-1-1: TriviaQA / NQ Farquhar Data Loader

**Parent Epic:** E-1 (Data Setup, complexity 9)

**API Signatures:**

```python
def load_trivia_qa(farquhar_data_dir: str) -> list[dict]:
    """
    Load TriviaQA samples from Farquhar 2023 JSONL split.

    Args:
        farquhar_data_dir: path to cloned jlko/semantic_uncertainty repo root

    Returns:
        list of dicts with keys:
            question: str
            label: int  (1=correct, 0=hallucinated)
            reference_answers: list[str]

    Raises:
        FileNotFoundError: if trivia_qa_val.jsonl not found at expected path
    """

def load_nq(farquhar_data_dir: str) -> list[dict]:
    """
    Load Natural Questions samples from Farquhar 2023 JSONL split.

    Args:
        farquhar_data_dir: path to cloned jlko/semantic_uncertainty repo root

    Returns:
        list of dicts with keys:
            question: str
            label: int  (1=correct, 0=hallucinated)
            reference_answers: list[str]

    Raises:
        FileNotFoundError: if nq_open_val.jsonl not found
    """

def get_dataset(name: str, farquhar_data_dir: str) -> list[dict]:
    """
    Dispatcher. name in {'trivia_qa', 'nq', 'truthful_qa'}.
    Routes to appropriate loader. Raises ValueError on unknown name.
    """
```

**Pseudo-code — load_trivia_qa:**

```python
def load_trivia_qa(farquhar_data_dir):
    path = os.path.join(farquhar_data_dir, "data", "trivia_qa_val.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Farquhar TriviaQA split not found: {path}")

    records = []
    with open(path) as f:
        for line in f:
            item = json.loads(line)
            question = item["question"]
            # Farquhar JSONL has 'answer' with 'aliases' list and binary 'correct' field
            label = int(item.get("correct", 0))
            ref_answers = item.get("answer", {}).get("aliases", [])
            if not ref_answers:
                continue  # skip if no reference answer
            records.append({"question": question, "label": label, "reference_answers": ref_answers})
    return records
```

**Output dict schema:**

```python
{
    "question": str,          # raw question text
    "label": int,             # 1=correct, 0=hallucinated
    "reference_answers": list[str]  # one or more reference strings
}
```

**Edge cases:**
- Items with empty `reference_answers` → skip
- Items with missing `correct` field → default label=0

---

### L-1-2: TruthfulQA Label Extraction with ROUGE-L

**Parent Epic:** E-1 (Data Setup, complexity 9)

**API Signature:**

```python
def load_truthful_qa() -> list[dict]:
    """
    Load TruthfulQA generation subset from HuggingFace hub.
    Labels via ROUGE-L >= 0.3 against best_answer field.

    Returns:
        list of dicts with keys:
            question: str
            label: int  (1=correct if model would produce answer with ROUGE-L>=0.3)
            reference_answers: list[str]  (best_answer + correct_answers)

    Note:
        label is pre-assigned as 1 for correct_answers items, 0 for incorrect.
        At eval time, model-generated answer is scored against reference_answers.
    """
```

**Pseudo-code:**

```python
from datasets import load_dataset
from rouge_score import rouge_scorer

def load_truthful_qa():
    ds = load_dataset("truthful_qa", "generation", split="validation")
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    records = []
    for item in ds:
        question = item["question"]
        best_answer = item["best_answer"]
        correct_answers = item["correct_answers"]
        incorrect_answers = item["incorrect_answers"]
        # reference_answers = best + correct for scoring at eval time
        reference_answers = [best_answer] + list(correct_answers)
        records.append({
            "question": question,
            "label": None,  # determined at eval time vs generated answer
            "reference_answers": reference_answers,
            "incorrect_answers": list(incorrect_answers),
            "best_answer": best_answer,
        })
    return records

def score_truthful_qa_answer(generated: str, record: dict, threshold: float = 0.3) -> int:
    """
    Compute ROUGE-L of generated answer vs all reference_answers.
    Returns 1 if max ROUGE-L >= threshold, else 0.
    """
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    max_score = max(
        scorer.score(ref, generated)["rougeL"].fmeasure
        for ref in record["reference_answers"]
    )
    return int(max_score >= threshold)
```

**Edge case:** Multiple reference answers → take max ROUGE-L (most generous correct match).

---

### L-2-1: Model Loading with fp16 + Flash Attention

**Parent Epic:** E-2 (Inference Pipeline, complexity 11)

**API Signature:**

```python
def load_model(model_key: str) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """
    Load frozen fp16 model + tokenizer from HuggingFace hub.

    Args:
        model_key: key in MODELS dict ('llama2' or 'mistral')

    Returns:
        (model, tokenizer) — model in eval mode, no grad, fp16

    Memory:
        7B fp16 ≈ 14 GB VRAM; requires single GPU >= 16 GB
    """
```

**Pseudo-code:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config import MODELS

def load_model(model_key: str):
    model_id = MODELS[model_key]

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        attn_implementation="flash_attention_2",  # falls back if unavailable
    )
    model.eval()
    return model, tokenizer
```

**Note:** `attn_implementation="flash_attention_2"` is speed-only; does not affect log-prob values. Falls back to standard attention if flash_attn not installed.

---

### L-2-2: Log-Prob Extraction from output_scores

**Parent Epic:** E-2 (Inference Pipeline, complexity 11)

**API Signature:**

```python
def extract_token_logprobs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompt: str,
    max_new_tokens: int = 50,
) -> list[float]:
    """
    Single greedy forward pass; returns per-token log-probs for generated tokens only.

    Args:
        model: loaded frozen model in eval mode
        tokenizer: corresponding tokenizer
        prompt: formatted prompt string e.g. "Q: {question}\\nA:"
        max_new_tokens: max tokens to generate (default 50)

    Returns:
        list of float (all <= 0.0), length = number of generated tokens
        Returns [] if no tokens generated (empty answer)

    Tensor shapes at key steps:
        inputs.input_ids:          (1, prompt_len)
        out.sequences:             (1, prompt_len + T)
        out.scores:                tuple of T tensors, each shape (1, vocab_size)
        token_ids:                 (T,)   — generated tokens only
        log_softmax(scores[t]):    (1, vocab_size)
        log_softmax(...)[0, tid]:  scalar float
    """
```

**Pseudo-code:**

```python
import torch

def extract_token_logprobs(model, tokenizer, prompt, max_new_tokens=50):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_len = inputs.input_ids.shape[1]

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,          # greedy
            return_dict_in_generate=True,
            output_scores=True,
        )

    # Extract generated token IDs (exclude prompt prefix)
    token_ids = out.sequences[0, prompt_len:]  # shape: (T,)

    if len(token_ids) == 0:
        return []

    # Extract log-prob for each generated token
    logprobs = []
    for t, score in enumerate(out.scores):          # score shape: (1, vocab_size)
        lp = torch.log_softmax(score, dim=-1)       # shape: (1, vocab_size)
        tid = token_ids[t].item()
        logprobs.append(lp[0, tid].item())          # scalar

    # Stop at first newline token
    nl_ids = tokenizer.encode("\n", add_special_tokens=False)
    for i, tid in enumerate(token_ids.tolist()):
        if tid in nl_ids:
            logprobs = logprobs[:i]
            break

    return logprobs  # list of float, all <= 0.0
```

---

### L-2-3: Batch Inference Runner

**Parent Epic:** E-2 (Inference Pipeline, complexity 11)

**API Signature:**

```python
def run_inference(
    samples: list[dict],
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
) -> list[dict]:
    """
    Run inference over all samples; attach logprobs to each record.

    Args:
        samples: list of dicts with 'question', 'label', 'reference_answers'
        model, tokenizer: loaded model pair

    Returns:
        list of dicts with original fields plus:
            logprobs: list[float]  — per-token log-probs (may be empty, filtered below)
            prompt: str            — formatted prompt used

    Note:
        Samples with empty logprobs (T=0) are excluded from returned list.
        For TruthfulQA, label is set at this stage via score_truthful_qa_answer().
    """
```

**Pseudo-code:**

```python
def run_inference(samples, model, tokenizer):
    results = []
    for sample in samples:
        prompt = f"Q: {sample['question']}\nA:"
        logprobs = extract_token_logprobs(model, tokenizer, prompt)

        if len(logprobs) == 0:
            continue  # skip empty generations

        record = dict(sample)
        record["logprobs"] = logprobs
        record["prompt"] = prompt

        # TruthfulQA: resolve label from generated answer
        if "best_answer" in sample:
            generated = tokenizer.decode(...)  # decoded generated tokens
            record["label"] = score_truthful_qa_answer(generated, sample)

        results.append(record)
    return results
```

**Output record schema:**

```python
{
    "question": str,
    "label": int,               # 1=correct, 0=hallucinated
    "reference_answers": list[str],
    "logprobs": list[float],    # per-token, all <= 0, length T >= 1
    "prompt": str,
}
```

---

### L-3-1: Aggregation Functions

**Parent Epic:** E-3 (Aggregation + Evaluation, complexity 10)

**API Signatures:**

```python
def aggregate(logprobs: list[float], method: str) -> float:
    """
    Aggregate token log-prob sequence to scalar.

    Args:
        logprobs: list of float, all <= 0, length >= 1
        method: one of 'min', 'mean', 'sum'

    Returns:
        float (not negated; negation done in compute_all_scores)

    Raises:
        ValueError: unknown method
        ValueError: empty logprobs
    """

def compute_all_scores(
    records: list[dict],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Compute negated aggregation scores and labels for all three methods.

    Returns:
        {method: (scores, labels)} where:
            scores: np.ndarray shape (N,), negated (higher = more uncertain)
            labels: np.ndarray shape (N,), int (1=correct, 0=hallucinated)
    """
```

**Pseudo-code:**

```python
import numpy as np

def aggregate(logprobs, method):
    lp = np.array(logprobs)
    if len(lp) == 0:
        raise ValueError("empty logprobs")
    if method == "min":
        return float(np.min(lp))    # most uncertain token
    elif method == "mean":
        return float(np.mean(lp))   # average NLL negated
    elif method == "sum":
        return float(np.sum(lp))    # raw sequence log-prob (length-biased)
    raise ValueError(f"Unknown method: {method}")

def compute_all_scores(records):
    results = {}
    labels = np.array([r["label"] for r in records], dtype=int)
    for method in ["min", "mean", "sum"]:
        raw = np.array([aggregate(r["logprobs"], method) for r in records])
        scores = -raw  # negate: higher = more uncertain = predicted hallucinated
        results[method] = (scores, labels)
    return results
```

**Edge cases:**
- Single-token answer (T=1): `min == mean == sum` (all identical; expected behavior)
- `sum` is length-biased: longer answers always have more negative sum regardless of confidence

---

### L-3-2: Bootstrap CI Computation

**Parent Epic:** E-3 (Aggregation + Evaluation, complexity 10)

**API Signature:**

```python
def bootstrap_auroc_diff(
    scores_a: np.ndarray,
    scores_b: np.ndarray,
    labels: np.ndarray,
    n_resamples: int = 1000,
) -> tuple[float, float]:
    """
    Bootstrap 95% CI for AUROC(scores_a) - AUROC(scores_b).

    Args:
        scores_a, scores_b: shape (N,) float arrays
        labels: shape (N,) int array
        n_resamples: bootstrap iterations (default 1000)

    Returns:
        (ci_lower, ci_upper): 95% percentile bootstrap interval
    """

def compute_all_pairwise_ci(
    method_scores: dict[str, np.ndarray],
    labels: np.ndarray,
    n_resamples: int = 1000,
) -> dict[str, tuple[float, float]]:
    """
    Compute bootstrap CI for all 3 pairwise AUROC differences.

    Returns:
        {
            "min_vs_mean": (ci_lower, ci_upper),
            "min_vs_sum":  (ci_lower, ci_upper),
            "mean_vs_sum": (ci_lower, ci_upper),
        }
    """
```

**Pseudo-code:**

```python
from scipy.stats import bootstrap
from sklearn.metrics import roc_auc_score
import numpy as np

def bootstrap_auroc_diff(scores_a, scores_b, labels, n_resamples=1000):
    idx = np.arange(len(labels))

    def stat(idx_sample):
        idx_sample = idx_sample.astype(int)
        return (roc_auc_score(labels[idx_sample], scores_a[idx_sample])
                - roc_auc_score(labels[idx_sample], scores_b[idx_sample]))

    result = bootstrap(
        (idx,), stat,
        n_resamples=n_resamples,
        confidence_level=0.95,
        method="percentile",
        random_state=42,
    )
    return result.confidence_interval.low, result.confidence_interval.high

def compute_all_pairwise_ci(method_scores, labels, n_resamples=1000):
    pairs = [("min", "mean"), ("min", "sum"), ("mean", "sum")]
    out = {}
    for a, b in pairs:
        key = f"{a}_vs_{b}"
        ci = bootstrap_auroc_diff(method_scores[a], method_scores[b], labels, n_resamples)
        out[key] = ci
    return out
```

---

### L-3-3: Gate Check + Length Stratification

**Parent Epic:** E-3 (Aggregation + Evaluation, complexity 10)

**API Signatures:**

```python
def check_gate(
    ci_table: dict[str, dict[str, dict[str, tuple[float, float]]]],
    auroc_table: dict[str, dict[str, dict[str, float]]],
    diff_threshold: float = 0.02,
) -> tuple[bool, str]:
    """
    H-E1 gate: pass if any pairwise diff >= threshold AND ci_lower > 0.

    Args:
        ci_table: {model: {dataset: {pair_key: (ci_lower, ci_upper)}}}
        auroc_table: {model: {dataset: {method: auroc_value}}}
        diff_threshold: minimum AUROC difference (default 0.02)

    Returns:
        (passed: bool, justification: str)
    """

def length_stratified_auroc(
    records: list[dict],
    method: str,
    threshold: int = 5,
) -> dict[str, float]:
    """
    Compute AUROC for short (T <= threshold) and long (T > threshold) answers.

    Args:
        records: inference records with 'logprobs' and 'label'
        method: aggregation method ('min', 'mean', 'sum')
        threshold: token count boundary (default 5)

    Returns:
        {"short": auroc_short, "long": auroc_long, "n_short": int, "n_long": int}
        Returns None for stratum with < 2 unique labels (AUROC undefined)
    """
```

**Pseudo-code:**

```python
def check_gate(ci_table, auroc_table, diff_threshold=0.02):
    pairs = [("min", "mean"), ("min", "sum"), ("mean", "sum")]
    for model in auroc_table:
        for dataset in auroc_table[model]:
            aurocs = auroc_table[model][dataset]
            cis = ci_table[model][dataset]
            for a, b in pairs:
                diff = aurocs[a] - aurocs[b]
                ci_lower, _ = cis[f"{a}_vs_{b}"]
                if abs(diff) >= diff_threshold and ci_lower > 0:
                    justification = (
                        f"PASS: {model}/{dataset} {a} vs {b}: "
                        f"diff={diff:.4f}, CI_lower={ci_lower:.4f}"
                    )
                    return True, justification
    return False, "FAIL: No pairwise diff >= 0.02 with CI_lower > 0"

def length_stratified_auroc(records, method, threshold=5):
    short = [(r, aggregate(r["logprobs"], method)) for r in records if len(r["logprobs"]) <= threshold]
    long_ = [(r, aggregate(r["logprobs"], method)) for r in records if len(r["logprobs"]) > threshold]

    def safe_auroc(subset):
        if len(subset) < 10:
            return None
        labels = np.array([r["label"] for r, _ in subset])
        scores = -np.array([s for _, s in subset])
        if len(np.unique(labels)) < 2:
            return None
        return roc_auc_score(labels, scores)

    return {
        "short": safe_auroc(short),
        "long": safe_auroc(long_),
        "n_short": len(short),
        "n_long": len(long_),
    }
```
