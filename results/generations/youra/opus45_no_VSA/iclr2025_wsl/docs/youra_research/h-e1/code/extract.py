import logging
import time
from math import isfinite

import timm
import torch
import torch.nn as nn

from model import compute_cv_pr

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def get_target_layers(model: nn.Module) -> list[tuple[str, torch.Tensor]]:
    """Yields (name, weight) for Conv2d/Linear, reshaped to 2D."""
    layers = []
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            w = module.weight.data
            if w.dim() == 4:
                w = w.reshape(w.shape[0], -1)
            layers.append((name, w))
    return layers


def process_model(model_name: str, cfg: dict) -> dict | None:
    """Loads model via timm, computes CV_PR per layer, aggregates."""
    try:
        model = timm.create_model(model_name, pretrained=True)
        model.eval()
        layer_results = []
        for name, w in get_target_layers(model):
            try:
                r = compute_cv_pr(w, cfg["n_seeds"], cfg["rank"])
                layer_results.append({"layer": name, **r})
            except Exception:
                continue
        if not layer_results:
            return None
        valid_cvs = [r["cv_pr"] for r in layer_results if isfinite(r["cv_pr"])]
        model_cv_pr = sum(valid_cvs) / len(valid_cvs) if valid_cvs else float("nan")
        return {"model": model_name, "model_cv_pr": model_cv_pr, "layers": layer_results}
    except Exception as e:
        log.warning(f"skip {model_name}: {e}")
        return None


def run_extraction(cfg: dict) -> list[dict]:
    """Iterates timm pretrained models, extracts CV_PR."""
    names = timm.list_models(pretrained=True)[: cfg["n_models"]]
    results = []
    for i, name in enumerate(names):
        t0 = time.time()
        r = process_model(name, cfg)
        elapsed = time.time() - t0
        if r is not None:
            r["time_sec"] = elapsed
            results.append(r)
        log.info(f"[{i+1}/{len(names)}] {name}: {'ok' if r else 'skipped'} ({elapsed:.1f}s)")
    return results
