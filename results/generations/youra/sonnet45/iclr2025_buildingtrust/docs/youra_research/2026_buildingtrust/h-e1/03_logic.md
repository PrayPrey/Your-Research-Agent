# Logic: H-E1 — Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17

Applied: Standard PyTorch float16 inference pattern (KB similarity < 0.42 — domain mismatch, green-field design used)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Model Inference + Logprob Extraction [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# h-e1/code/model_runner.py
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm


class ModelRunner:
    def __init__(self, model_id: str, torch_dtype: str = "float16", device_map: str = "auto"):
        """Load AutoModelForCausalLM with float16 and device_map auto."""
        self.model_id = model_id
        self.torch_dtype = torch_dtype
        self.device_map = device_map
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        """Load model and tokenizer into GPU memory."""
        ...

    def extract_logprobs(
        self,
        dataset: list[dict],
        cache_path: str,
        batch_size: int = 1,
    ) -> np.ndarray:
        """Extract log_softmax over 4 option tokens at last position.

        Args:
            dataset: list of items with keys: question, choices, answer_idx
            cache_path: path to .npy cache file (load if exists, save if not)
            batch_size: inference batch size (default 1 for determinism)

        Returns:
            logprobs: (n, 4) log_softmax over [A, B, C, D] option tokens
        """
        # Shape: (n_items, 4)
        ...

    def unload(self) -> None:
        """Delete model from GPU memory; call torch.cuda.empty_cache()."""
        ...


def run_pair_extraction(
    pair_cfg: dict,
    datasets: dict[str, list[dict]],
    cache_dir: str,
) -> dict[str, dict]:
    """Run extraction for one base+aligned pair across all benchmarks.

    Args:
        pair_cfg: {"pair_id", "base", "aligned", "method"}
        datasets: {"mmlu": [...], "truthfulqa": [...], "arc": [...]}
        cache_dir: directory for .npy cache files

    Returns:
        {"mmlu": {"base": ndarray (n,4), "aligned": ndarray (n,4)},
         "truthfulqa": {...}, "arc": {...}}
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| raw_logits | [1, seq_len, vocab_size] | outputs.logits from forward pass |
| option_logits | [4] | logits at position [-1] for option token IDs |
| logprobs (per item) | [4] | F.log_softmax(option_logits, dim=0) |
| logprobs (full dataset) | [n, 4] | stacked over all items, saved as .npy |

### Pseudo-code: extract_logprobs

```
if cache_path exists:
    return np.load(cache_path)

option_token_ids = tokenizer(["A","B","C","D"], add_special_tokens=False).input_ids  # 4 ids

results = []
for item in tqdm(dataset):
    prompt = format_prompt(item)
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        outputs = model(input_ids)
    # outputs.logits: [1, seq_len, vocab_size]
    last_logits = outputs.logits[0, -1, option_token_ids]  # [4]
    log_probs = F.log_softmax(last_logits.float(), dim=0)  # [4]
    results.append(log_probs.cpu().numpy())

arr = np.stack(results)  # [n, 4]
np.save(cache_path, arr)
return arr
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ModelRunner.extract_logprobs | Float16 logit extraction, option token lookup, .npy cache logic |
| L-2-2 | run_pair_extraction | Orchestrate base+aligned extraction across 3 benchmarks, handle cache paths |

---

## A-3: Statistical Analysis Pipeline [Complexity: 14, Budget: 4 subtasks]

### API Signatures

```python
# h-e1/code/analysis_pipeline.py
import numpy as np
from scipy.stats import zscore
from scipy.special import softmax
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm


def compute_margin_and_flip(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
) -> tuple[np.ndarray, np.ndarray]:
    """Compute z-scored top1-top2 margin and argmax flip indicator.

    Returns:
        margin_z: (n,) z-scored confidence margin from base model
        flip: (n,) int — 1 if argmax(base) != argmax(aligned), else 0
    """
    ...


def compute_kl_divergence(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
) -> np.ndarray:
    """Compute item-level KL(base || aligned) over 4-option softmax.

    Returns:
        kl: (n,) KL divergence per item
    """
    ...


def fit_logistic_regression(
    margin_z: np.ndarray,  # (n,)
    kl_div: np.ndarray,    # (n,)
    flip: np.ndarray,      # (n,) int
) -> dict:
    """Fit logistic regression: logit P(flip) = β₀ + β₁·margin_z + β₂·kl_div.

    Returns:
        {"beta1": float, "beta0": float, "pvalue_beta1": float,
         "auroc": float, "partial_eta2": float, "lr_model": LogisticRegression}
    """
    ...


def evaluate_cross_benchmark(
    lr_model: LogisticRegression,
    datasets_logprobs: dict[str, dict],  # {"mmlu":{"base":ndarray,"aligned":ndarray}, ...}
    train_dataset: str = "mmlu",
) -> dict[str, float]:
    """Evaluate trained lr_model on held-out benchmarks.

    Returns:
        {"truthfulqa": auroc_float, "arc": auroc_float}
    """
    ...


def verify_pipeline_activated(
    base_logprobs: np.ndarray,    # [n, 4]
    aligned_logprobs: np.ndarray, # [n, 4]
    margin_z: np.ndarray,         # (n,)
    flip: np.ndarray,             # (n,)
    beta1: float,
    auroc: float,
) -> tuple[bool, dict[str, bool]]:
    """Check all pipeline activation indicators.

    Returns:
        (all_pass, {"logprobs_extracted": bool, "margin_variable": bool,
                    "flip_occurs": bool, "negative_beta": bool, "auroc_above_chance": bool})
    """
    ...


def run_full_analysis(
    pair_cfg: dict,
    datasets_logprobs: dict[str, dict],  # {"mmlu":{"base":ndarray,"aligned":ndarray}, ...}
) -> dict:
    """Run full analysis for one model pair on primary benchmark (MMLU).

    Returns:
        full results dict with beta1, pvalue, auroc, partial_eta2,
        cross_benchmark results, pipeline_activated flag
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| base_logprobs | [n, 4] | log_softmax values from base model |
| aligned_logprobs | [n, 4] | log_softmax values from aligned model |
| sorted_logprobs | [n, 4] | base_logprobs sorted descending per row |
| margin_raw | [n] | sorted[:,0] - sorted[:,1] |
| margin_z | [n] | zscore(margin_raw) |
| flip | [n] | int array {0, 1} |
| kl | [n] | KL(base||aligned) per item |
| X_train | [n, 2] | column-stack([margin_z, kl_div]) |

### Pseudo-code: compute_margin_and_flip

```
sorted_logprobs = np.sort(base_logprobs, axis=1)[:, ::-1]  # [n, 4] descending
margin_raw = sorted_logprobs[:, 0] - sorted_logprobs[:, 1]  # [n]
margin_z = zscore(margin_raw)                                 # [n]

argmax_base    = np.argmax(base_logprobs, axis=1)             # [n]
argmax_aligned = np.argmax(aligned_logprobs, axis=1)          # [n]
flip = (argmax_base != argmax_aligned).astype(int)            # [n]

return margin_z, flip
```

### Pseudo-code: compute_kl_divergence

```
# Convert log_softmax → softmax probabilities
p_base    = np.exp(base_logprobs)    # [n, 4]
p_aligned = np.exp(aligned_logprobs) # [n, 4]

# KL(base || aligned) = sum_k p_base_k * log(p_base_k / p_aligned_k)
# Use log domain: base_logprobs - aligned_logprobs
kl = np.sum(p_base * (base_logprobs - aligned_logprobs), axis=1)  # [n]
return kl
```

### Pseudo-code: fit_logistic_regression

```
X = np.column_stack([margin_z, kl_div])  # [n, 2]
y = flip                                  # [n]

# sklearn for predict_proba / AUROC
lr = LogisticRegression(random_state=42, max_iter=1000)
lr.fit(X, y)
auroc = roc_auc_score(y, lr.predict_proba(X)[:, 1])

# statsmodels for Wald test p-value on β₁
X_sm = sm.add_constant(X)  # [n, 3] with intercept column
logit_model = sm.Logit(y, X_sm).fit(disp=False)
# coef order: [intercept, beta1(margin_z), beta2(kl_div)]
beta0 = logit_model.params[0]
beta1 = logit_model.params[1]
pvalue_beta1 = logit_model.pvalues[1]  # two-sided Wald test

# partial eta² approximation: McFadden pseudo-R² × variance_explained_fraction
# Use: partial_eta2 ≈ (null_llf - llf) / (-null_llf)  (McFadden R²)
partial_eta2 = 1 - (logit_model.llf / logit_model.llnull)

return {"beta1": beta1, "beta0": beta0, "pvalue_beta1": pvalue_beta1,
        "auroc": auroc, "partial_eta2": partial_eta2, "lr_model": lr}
```

### Pseudo-code: evaluate_cross_benchmark

```
results = {}
for ds_name, ds_logprobs in datasets_logprobs.items():
    if ds_name == train_dataset:
        continue
    margin_z_eval, flip_eval = compute_margin_and_flip(
        ds_logprobs["base"], ds_logprobs["aligned"]
    )
    kl_eval = compute_kl_divergence(ds_logprobs["base"], ds_logprobs["aligned"])
    X_eval = np.column_stack([margin_z_eval, kl_eval])
    auroc_eval = roc_auc_score(flip_eval, lr_model.predict_proba(X_eval)[:, 1])
    results[ds_name] = auroc_eval
return results
```

### Pseudo-code: verify_pipeline_activated

```
indicators = {
    "logprobs_extracted": base_logprobs.shape[0] > 1000,
    "margin_variable":    np.std(margin_z) > 0.1,
    "flip_occurs":        np.mean(flip) > 0.05,
    "negative_beta":      beta1 < 0.0,
    "auroc_above_chance": auroc > 0.55,
}
all_pass = all(indicators.values())
return all_pass, indicators
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_margin_and_flip | Sorted logprob margin, zscore, argmax flip indicator |
| L-3-2 | compute_kl_divergence | Item-level KL(base||aligned) via log-domain exp trick |
| L-3-3 | fit_logistic_regression | sklearn LR for AUROC + statsmodels Logit for Wald p-value |
| L-3-4 | evaluate_cross_benchmark + verify_pipeline_activated | Cross-benchmark AUROC eval and pipeline indicator checks |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments and table
- [x] Subtask count within budget (A-2: 2/2, A-3: 4/4)
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field: Serena skip noted in Codebase Analysis
- [x] EXISTENCE PoC: single forward/function signatures, minimal API
