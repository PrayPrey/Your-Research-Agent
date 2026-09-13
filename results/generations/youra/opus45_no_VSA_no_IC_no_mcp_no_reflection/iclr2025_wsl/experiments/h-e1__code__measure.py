"""Alpha measurement using WeightWatcher."""
import re
import logging
from typing import Optional
import torch
import weightwatcher as ww
from transformers import AutoModel
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_alpha_for_model(model_id: str) -> Optional[dict]:
    """Compute heavy-tailed alpha for a single ViT model."""
    try:
        model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
        model.eval()
    except Exception as e:
        logger.warning(f"Failed to load {model_id}: {e}")
        return None

    try:
        watcher = ww.WeightWatcher(model=model)
        details = watcher.analyze()
    except Exception as e:
        logger.warning(f"WeightWatcher failed for {model_id}: {e}")
        del model
        torch.cuda.empty_cache()
        return None

    pattern = re.compile(CONFIG.attention_name_pattern, re.IGNORECASE)
    if "name" in details.columns:
        mask = details["name"].apply(lambda x: bool(pattern.search(str(x))))
    else:
        mask = details.index.to_series().apply(lambda x: bool(pattern.search(str(x))))

    attn_rows = details[mask]
    if attn_rows.empty or "alpha" not in attn_rows.columns:
        logger.warning(f"No attention layers found for {model_id}")
        del model
        torch.cuda.empty_cache()
        return None

    alpha_values = attn_rows["alpha"].dropna().tolist()
    if not alpha_values:
        del model
        torch.cuda.empty_cache()
        return None

    n_params = sum(p.numel() for p in model.parameters())
    family = model_id.split("/")[0] if "/" in model_id else "unknown"

    del model
    torch.cuda.empty_cache()

    return {
        "model_id": model_id,
        "family": family,
        "alpha_mean": float(sum(alpha_values) / len(alpha_values)),
        "alpha_per_layer": alpha_values,
        "n_params": n_params,
        "n_layers": len(alpha_values)
    }


def run_measurement(model_ids: list[str]) -> list[dict]:
    """Run measurement on list of model IDs."""
    results = []
    for i, mid in enumerate(model_ids):
        logger.info(f"[{i+1}/{len(model_ids)}] Processing {mid}")
        r = compute_alpha_for_model(mid)
        if r is not None:
            results.append(r)
            logger.info(f"  alpha_mean={r['alpha_mean']:.3f}, n_layers={r['n_layers']}")
    return results


if __name__ == "__main__":
    from collect_models import fetch_vit_model_ids
    ids = fetch_vit_model_ids(5)
    results = run_measurement(ids)
    print(f"Measured {len(results)} models")
