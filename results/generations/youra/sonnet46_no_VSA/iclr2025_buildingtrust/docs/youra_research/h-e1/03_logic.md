# Logic: H-E1 — Transformer Δ*-Vector Fingerprinting

**Hypothesis Type**: EXISTENCE (PoC)
**Date**: 2026-07-29

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-5: Statistical Analysis [Complexity: 17, Budget: 4 subtasks]

**Applied**: statsmodels MixedLM + scipy permutation pattern

### L-5-1: Mixed-Effects Model Setup

```python
# statistical_analysis.py
import statsmodels.formula.api as smf
import pandas as pd

def run_mixed_effects(
    df: pd.DataFrame,
    formula: str = "delta_star ~ arch_family * attack_type + objective + tokenizer + clean_acc",
    group_var: str = "model_id",
) -> dict:
    """Fit LME; return coef, pvalues, aic."""
    # df: n_models × n_attack_categories rows (e.g., 90 rows for 9 models × 10 cats)
    # df columns: delta_star (float), arch_family (str), attack_type (str),
    #             objective (str), tokenizer (str), clean_acc (float), model_id (str)
    model = smf.mixedlm(formula, df, groups=df[group_var])
    result = model.fit(reml=True)
    return {
        "coef": result.params.to_dict(),    # {term: coef}
        "pvalues": result.pvalues.to_dict(), # {term: p}
        "aic": result.aic,
    }
    # Edge: if model fails to converge, catch ConvergenceWarning; return result anyway
```

---

### L-5-2: Bootstrap Interaction CI

```python
def bootstrap_interaction_ci(
    df: pd.DataFrame,
    n_iter: int = 1000,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Bootstrap at model level; refit LME; return 95% CI per term."""
    # Returns {term: (ci_2.5%, ci_97.5%)}
    # ponytail: n_iter=200 default for PoC speed; 1000 for gate condition check
```

Pseudo-code:
```
1. rng = np.random.default_rng(seed)
2. model_ids = df["model_id"].unique()          # [n_models]
3. coefs = defaultdict(list)                    # term -> [n_iter floats]

4. for _ in range(n_iter):
       sampled = rng.choice(model_ids, size=len(model_ids), replace=True)
       boot_df = pd.concat([df[df["model_id"] == m] for m in sampled]).reset_index(drop=True)
       # Re-suffix duplicated model_ids to keep grouping valid
       boot_df["model_id"] += "_" + boot_df.groupby("model_id").cumcount().astype(str)
       try:
           res = smf.mixedlm(formula, boot_df, groups=boot_df["model_id"]).fit(reml=True)
           for term, val in res.params.items():
               coefs[term].append(val)
       except Exception:
           continue

5. return {term: (np.percentile(vals, 2.5), np.percentile(vals, 97.5))
           for term, vals in coefs.items()}
```

Bootstrap samples shape: [n_iter] per term (coefficient distribution).

---

### L-5-3: Permutation MANOVA

```python
def permutation_manova(
    X: np.ndarray,          # [n_models, n_reliable_cats]  e.g. [9, 10]
    y: np.ndarray,          # [n_models] string family labels
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict[str, float]:
    """Per-category eta^2 + permutation p-value. Returns {eta_squared, p_value, eta_per_category}."""
```

η² formula per category c:
```
grand_mean_c = X[:, c].mean()
SS_total     = sum((X[:, c] - grand_mean_c)^2)
SS_between   = sum over families f: n_f * (mean_f_c - grand_mean_c)^2
eta_sq_c     = SS_between / SS_total   (0.0 if SS_total == 0)
```

Pseudo-code:
```
1. rng = np.random.default_rng(seed)
2. families = np.unique(y)
3. observed_eta = mean(eta_sq_c for c in range(n_cats))  # scalar summary

4. null_etas = []
   for _ in range(n_permutations):
       y_perm = rng.permutation(y)
       null_etas.append(mean(eta_sq_c(X, y_perm) for c in range(n_cats)))

5. p_value = (np.array(null_etas) >= observed_eta).mean()
6. return {"eta_squared": observed_eta, "p_value": p_value,
           "eta_per_category": [eta_sq_c for each cat]}
```

Shapes: null_etas [n_permutations], eta_per_category [n_cats].

---

### L-5-4: LOMO Classify

```python
from sklearn.metrics import confusion_matrix as sk_confusion_matrix

def lomo_classify(
    X: np.ndarray,             # [n_models, n_reliable_cats]  e.g. [9, 10]
    family_labels: list[str],  # [n_models]
) -> tuple[float, np.ndarray]:
    """Leave-one-model-out cosine KNN k=1. Returns (accuracy, confusion_matrix [n_fam, n_fam])."""
```

Pseudo-code:
```
1. y = np.array(family_labels)             # [n_models]
2. classes = sorted(np.unique(y).tolist())
3. preds = []

4. for i in range(len(X)):
       train_X = np.delete(X, i, axis=0)   # [n_models-1, n_cats]
       train_y = np.delete(y, i)
       test_x  = X[i]                       # [n_cats]

       # L2-normalize then dot = cosine similarity
       train_norm = train_X / (np.linalg.norm(train_X, axis=1, keepdims=True) + 1e-8)
       test_norm  = test_x  / (np.linalg.norm(test_x)  + 1e-8)
       sims = train_norm @ test_norm         # [n_models-1]
       preds.append(train_y[np.argmax(sims)])

5. preds = np.array(preds)
6. acc   = (preds == y).mean()
7. cm    = sk_confusion_matrix(y, preds, labels=classes)  # [n_fam, n_fam]
8. return float(acc), cm
```

Shapes: sims [n_models-1 per iter], cm [3, 3] (encoder/decoder/enc_dec).

### Subtasks [4/4 used]

| ID | Subtask |
|----|---------|
| L-5-1 | Mixed-effects model setup (statsmodels MixedLM formula + groups) |
| L-5-2 | Bootstrap interaction CI (model-level resampling, 95% percentile) |
| L-5-3 | Permutation MANOVA (per-category η², permutation p-value) |
| L-5-4 | LOMO classifier (cosine KNN k=1, leave-one-model-out) |

---

## A-2: Fine-tuning Pipeline [Complexity: 16, Budget: 3 subtasks]

**Applied**: HuggingFace AutoModelForSequenceClassification + Trainer pattern

### L-2-1: Decoder-Only Models (GPT-2, OPT)

```python
# fine_tuner.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def _setup_decoder_for_clf(
    model_id: str,
    num_labels: int,
) -> tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """Pad token fix + left-padding for causal LM classification."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # GPT-2/OPT have no pad token
        tokenizer.padding_side = "left"             # classifier reads last non-pad token

    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )
    model.config.pad_token_id = tokenizer.eos_token_id
    return model, tokenizer
    # input_ids:  [B, seq_len]  left-padded
    # logits:     [B, num_labels]  from last non-padding position
```

---

### L-2-2: Encoder-Decoder Models (T5, BART)

```python
def _setup_enc_dec_for_clf(
    model_id: str,
    num_labels: int,
) -> tuple[AutoModelForSequenceClassification, AutoTokenizer]:
    """T5/BART seq classification via encoder pooled output."""
    tokenizer = AutoTokenizer.from_pretrained(model_id, legacy=False)  # T5 legacy warning fix
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id, num_labels=num_labels
    )
    # T5ForSequenceClassification uses encoder hidden states → linear → logits
    # No decoder invoked during classification forward pass
    # BART: same pattern; pad token already defined
    return model, tokenizer
    # input_ids:  [B, src_len]  right-padded (default)
    # logits:     [B, num_labels]
```

---

### L-2-3: Pre-trained Checkpoint Loader

```python
_TEXTATTACK_SHORTCUTS: dict[str, dict[str, str]] = {
    "bert-base-uncased": {
        "sst2": "textattack/bert-base-uncased-SST-2",
        "mnli": "textattack/bert-base-uncased-MNLI",
        "qqp":  "textattack/bert-base-uncased-QQP",
        "qnli": "textattack/bert-base-uncased-QNLI",
        "rte":  "textattack/bert-base-uncased-RTE",
    },
    "roberta-base": {
        "sst2": "textattack/roberta-base-SST-2",
        "mnli": "textattack/roberta-base-MNLI",
        "qqp":  "textattack/roberta-base-QQP",
        "qnli": "textattack/roberta-base-QNLI",
        "rte":  "textattack/roberta-base-RTE",
    },
    # albert/electra: no reliable textattack/* shortcuts; fine-tune fresh
}

def load_pretrained_glue_checkpoint(model_id: str, task: str) -> str | None:
    """Return HF Hub checkpoint ID if shortcut exists, else None."""
    return _TEXTATTACK_SHORTCUTS.get(model_id, {}).get(task.lower())
```

Usage in `finetune_all`:
```
hub_id = load_pretrained_glue_checkpoint(model_id, task)
if hub_id and skip_finetuning:
    ckpt_path = hub_id  # pass directly as model_path to evaluator
    clean_acc = evaluate_on_dataset(hub_id, model_id, glue_clean[task], task)
else:
    ckpt_path, clean_acc = finetune_model(model_id, task, ...)
```

Edge case: verify `model.config.id2label` matches task label ordering before evaluation.

### Subtasks [3/3 used]

| ID | Subtask |
|----|---------|
| L-2-1 | Decoder-only setup: pad=eos_token, padding_side="left", pad_token_id in config |
| L-2-2 | Encoder-decoder setup: T5 legacy=False, encoder-only classification head |
| L-2-3 | Pre-trained checkpoint loader: textattack/* HF Hub shortcuts dict |

---

## Key Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, seq_len] | seq_len <= 512 |
| logits | [B, num_labels] | 2 or 3 |
| Δ*-vector per model | [n_reliable_cats] | float, ~5-15 dims |
| X (all models) | [9, n_reliable_cats] | e.g. [9, 10] |
| family_labels | [9] | "encoder"/"decoder"/"enc_dec" |
| bootstrap coef samples | [n_iter] per term | n_iter=200 PoC / 1000 gate |
| null_etas | [n_permutations] | for p-value |
| confusion_matrix | [3, 3] | LOMO output |
