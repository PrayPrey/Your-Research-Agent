# Logic: H-E1 (EXISTENCE)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-2: Alpha Computation [Complexity: 12, Budget: 12]

**Applied**: WeightWatcher analyze() pattern for per-layer power-law fit

### API Signatures

```python
from typing import Optional
import weightwatcher as ww
from transformers import AutoModel

def load_vit_model(model_id: str) -> Optional["torch.nn.Module"]:
    """AutoModel.from_pretrained(model_id). Returns None on failure."""
    ...

def compute_alpha_for_model(model_id: str) -> Optional[dict]:
    """Load model -> WeightWatcher.analyze() -> filter attention layers -> mean alpha.
    Returns None on load/analysis failure (caller logs skip)."""
    ...

def run_measurement(model_ids: list[str]) -> list[dict]:
    """Iterate model_ids, call compute_alpha_for_model, skip None, log failures."""
    ...
```

### Tensor Shapes (WeightWatcher matrices)

| Variable | Shape | Note |
|----------|-------|------|
| layer.weight (qkv proj) | [out_features, in_features] | 2D matrix WW fits ESD on |
| ww_details (per model) | DataFrame rows = 1 per Linear/Conv2d layer | `alpha` column is per-layer Hill estimate |
| attention_alphas | [n_attn_layers] | filtered subset of ww_details.alpha |
| result["alpha_mean"] | scalar | mean(attention_alphas) |

### Pseudo-code

```
compute_alpha_for_model(model_id):
    try:
        model = AutoModel.from_pretrained(model_id)
    except Exception:
        return None

    watcher = ww.WeightWatcher(model=model)
    details = watcher.analyze()  # DataFrame: layer_id, name, alpha, ...

    mask = details["name"].str.contains(ATTENTION_NAME_PATTERN, case=False, regex=True)
    attn_rows = details[mask]
    if attn_rows.empty:
        return None

    return {
        "model_id": model_id,
        "alpha_mean": attn_rows["alpha"].mean(),
        "alpha_layers": attn_rows["alpha"].tolist(),
        "n_params": sum(p.numel() for p in model.parameters()),
    }

run_measurement(model_ids):
    results = []
    for mid in model_ids:
        r = compute_alpha_for_model(mid)
        if r is None:
            log(f"skip {mid}")
            continue
        results.append(r)
    return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A2-1 | Model load + WW analyze | `load_vit_model`, `compute_alpha_for_model` — wrap HF load + `ww.WeightWatcher(model=model).analyze()`, filter rows by `ATTENTION_NAME_PATTERN`, compute mean alpha, return dict or None |
| L-A2-2 | Batch loop | `run_measurement` — iterate ids, call per-model function, catch/log failures, accumulate results list |

---

## External Dependencies

None — green-field foundation hypothesis, no base hypothesis code to call.
