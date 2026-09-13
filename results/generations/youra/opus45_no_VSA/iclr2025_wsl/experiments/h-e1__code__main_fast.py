#!/usr/bin/env python3
"""Optimized extraction: diverse model families, skips huge models."""
import logging
import sys
import time
from math import isfinite
from pathlib import Path

import timm
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).parent))

from model import compute_cv_pr
from evaluate import aggregate_results, check_success_criteria, save_results
from visualize import plot_cv_pr_distribution, plot_success_rate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

CONFIG = {
    "n_seeds": 20,
    "rank": 50,
    "n_models": 100,
    "output_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",
}


def get_diverse_models(n: int) -> list[str]:
    """Get n models from diverse families, skip huge ones."""
    models = timm.list_models(pretrained=True)
    selected = []
    families = set()
    skip_patterns = ['3b', '1b', '7b', '22b', 'giant', 'huge', 'xlarge', 'xxlarge']

    for m in models:
        if len(selected) >= n:
            break
        if any(p in m.lower() for p in skip_patterns):
            continue
        family = m.split('_')[0] if '_' in m else m.split('.')[0]
        if family not in families:
            families.add(family)
            selected.append(m)

    # Fill remaining with non-duplicate models if needed
    for m in models:
        if len(selected) >= n:
            break
        if m not in selected and not any(p in m.lower() for p in skip_patterns):
            selected.append(m)

    return selected[:n]


def get_target_layers(model: nn.Module) -> list[tuple[str, torch.Tensor]]:
    layers = []
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Linear)):
            w = module.weight.data
            if w.dim() == 4:
                w = w.reshape(w.shape[0], -1)
            layers.append((name, w))
    return layers


def process_model(model_name: str, cfg: dict) -> dict | None:
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
        del model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        return {"model": model_name, "model_cv_pr": model_cv_pr, "layers": layer_results}
    except Exception as e:
        log.warning(f"skip {model_name}: {e}")
        return None


def main():
    log.info(f"Starting optimized extraction: {CONFIG['n_models']} diverse models")

    model_names = get_diverse_models(CONFIG["n_models"])
    log.info(f"Selected {len(model_names)} models from {len(set(m.split('_')[0] for m in model_names))} families")

    results = []
    for i, name in enumerate(model_names):
        t0 = time.time()
        r = process_model(name, CONFIG)
        elapsed = time.time() - t0
        if r is not None:
            r["time_sec"] = elapsed
            results.append(r)
        status = "ok" if r else "skipped"
        log.info(f"[{i+1}/{len(model_names)}] {name}: {status} ({elapsed:.1f}s)")

    log.info(f"Extraction complete: {len(results)} models processed")

    summary = aggregate_results(results)
    log.info(f"Summary: completion={summary['completion_rate']:.2%}, mean_cv_pr={summary['mean_cv_pr']:.4f}")

    base = Path(__file__).parent.parent
    out_dir = base / CONFIG["output_dir"]
    fig_dir = base / CONFIG["figures_dir"]

    save_results(results, summary, str(out_dir))
    plot_success_rate(summary, str(fig_dir / "success_rate.png"))
    plot_cv_pr_distribution(results, str(fig_dir / "cv_pr_distribution.png"))

    success = check_success_criteria(summary)

    print(f"\n{'='*50}")
    print("EXPERIMENT RESULTS")
    print(f"{'='*50}")
    print(f"Models processed: {summary['n_models_processed']}")
    print(f"Models valid: {summary['n_models_valid']}")
    print(f"Completion rate: {summary['completion_rate']:.2%}")
    print(f"Mean CV_PR: {summary['mean_cv_pr']:.4f}")
    print(f"Std CV_PR: {summary['std_cv_pr']:.4f}")
    print(f"Range: [{summary['min_cv_pr']:.4f}, {summary['max_cv_pr']:.4f}]")
    print(f"SUCCESS: {success}")
    print(f"{'='*50}\n")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
