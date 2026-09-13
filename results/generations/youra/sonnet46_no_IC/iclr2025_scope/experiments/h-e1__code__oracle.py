from __future__ import annotations
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from config import ExperimentConfig


def layer_to_safe(layer_name: str) -> str:
    """Replace '.' with '__' for filesystem safety."""
    return layer_name.replace(".", "__")


def build_oracle_state_key(model_slug: str, layer_safe: str, rank: int, seed: int) -> str:
    return f"{model_slug}__{layer_safe}__r{rank}__s{seed}"


def get_checkpoint_path(cfg: ExperimentConfig, layer_safe: str, rank: int, seed: int) -> Path:
    model_slug = cfg.model_name.replace("/", "-")
    return Path(cfg.checkpoint_dir) / model_slug / f"{layer_safe}__r{rank}__s{seed}.json"


def is_done(cfg: ExperimentConfig, layer_safe: str, rank: int, seed: int) -> bool:
    path = get_checkpoint_path(cfg, layer_safe, rank, seed)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text())
        return "val_acc" in data
    except Exception:
        return False


def save_result(cfg: ExperimentConfig, layer: str, rank: int, seed: int, val_acc: float) -> None:
    """Atomic write via tmp+rename."""
    layer_safe = layer_to_safe(layer)
    path = get_checkpoint_path(cfg, layer_safe, rank, seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"val_acc": val_acc, "rank": rank, "layer": layer, "seed": seed}))
    tmp.rename(path)


def load_or_resume_oracle(cfg: ExperimentConfig) -> dict[str, dict]:
    """Scan checkpoint dir and load all completed run results."""
    model_slug = cfg.model_name.replace("/", "-")
    ckpt_dir = Path(cfg.checkpoint_dir) / model_slug
    results: dict[str, dict] = {}
    if not ckpt_dir.exists():
        return results
    for p in ckpt_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            if "val_acc" not in data:
                continue
            layer = data["layer"]
            rank = data["rank"]
            seed = data["seed"]
            layer_safe = layer_to_safe(layer)
            key = build_oracle_state_key(model_slug, layer_safe, rank, seed)
            results[key] = data
        except Exception:
            continue
    return results


def compute_oracle_rank_map(
    all_results: dict[str, dict],
    layers: list[str],
    oracle_ranks: list[int],
    seeds: list[int],
    model_slug: str,
) -> dict[str, int]:
    """Mean val_acc over seeds per rank → argmax per layer."""
    oracle_rank_map: dict[str, int] = {}
    for layer in layers:
        layer_safe = layer_to_safe(layer)
        rank_acc: dict[int, float] = {}
        for rank in oracle_ranks:
            accs = []
            for s in seeds:
                key = build_oracle_state_key(model_slug, layer_safe, rank, s)
                if key in all_results:
                    accs.append(all_results[key]["val_acc"])
            if accs:
                rank_acc[rank] = sum(accs) / len(accs)
        if rank_acc:
            oracle_rank_map[layer] = max(rank_acc, key=rank_acc.get)
    return oracle_rank_map


def _run_job(args: tuple) -> tuple[str, int, int, float]:
    """Worker for ProcessPoolExecutor. Imports train inside subprocess."""
    model_name, layer, rank, seed, cfg_dict = args
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from config import ExperimentConfig
    from pathlib import Path
    cfg = ExperimentConfig(**{k: Path(v) if k.endswith("_dir") else v for k, v in cfg_dict.items()})
    from train import train_one_run
    val_acc = train_one_run(model_name, layer, rank, seed, cfg)
    return layer, rank, seed, val_acc


def run_oracle_sweep(
    cfg: ExperimentConfig,
    erank_map: dict[str, float],
    max_workers: int = 1,
) -> dict[str, int]:
    """
    Full sweep: (layer, rank, seed) combos, skip completed, dispatch train_one_run.
    Returns oracle_rank_map {layer_name: best_rank}.
    # ponytail: sequential default, set max_workers=GPU count for parallel
    """
    all_layers = sorted(erank_map.keys())
    step = getattr(cfg, "layer_sample_step", 1)
    layers = all_layers[::step] if step > 1 else all_layers
    if step > 1:
        print(f"  PoC layer sampling (step={step}): {len(layers)} of {len(all_layers)} layers")
    model_slug = cfg.model_name.replace("/", "-")
    jobs = [
        (layer, rank, seed)
        for layer in layers
        for rank in cfg.oracle_ranks
        for seed in cfg.seeds
        if not is_done(cfg, layer_to_safe(layer), rank, seed)
    ]

    print(f"  {len(jobs)} runs remaining (total={len(layers)*len(cfg.oracle_ranks)*len(cfg.seeds)})")

    if max_workers == 1:
        from train import train_one_run
        for (layer, rank, seed) in tqdm(jobs, desc=f"{model_slug} oracle"):
            val_acc = train_one_run(cfg.model_name, layer, rank, seed, cfg)
            save_result(cfg, layer, rank, seed, val_acc)
    else:
        # Serialize cfg to plain dict for pickling
        cfg_dict = {
            "model_name": cfg.model_name,
            "output_dir": str(cfg.output_dir),
            "results_dir": str(cfg.results_dir),
            "figures_dir": str(cfg.figures_dir),
            "checkpoint_dir": str(cfg.checkpoint_dir),
            "epochs_nlp": cfg.epochs_nlp,
            "batch_size_nlp": cfg.batch_size_nlp,
            "lr_nlp": cfg.lr_nlp,
            "epochs_vit": cfg.epochs_vit,
            "batch_size_vit": cfg.batch_size_vit,
            "lr_vit": cfg.lr_vit,
            "weight_decay": cfg.weight_decay,
            "warmup_ratio": cfg.warmup_ratio,
            "max_length": cfg.max_length,
            "oracle_ranks": cfg.oracle_ranks,
            "baseline_rank": cfg.baseline_rank,
            "seeds": cfg.seeds,
        }
        args_list = [(cfg.model_name, layer, rank, seed, cfg_dict) for (layer, rank, seed) in jobs]
        with ProcessPoolExecutor(max_workers=max_workers) as pool:
            futs = {pool.submit(_run_job, args): args[:3] for args in args_list}
            for fut in tqdm(as_completed(futs), total=len(futs), desc=f"{model_slug} oracle parallel"):
                layer, rank, seed, val_acc = fut.result()
                save_result(cfg, layer, rank, seed, val_acc)

    all_results = load_or_resume_oracle(cfg)
    return compute_oracle_rank_map(all_results, layers, cfg.oracle_ranks, cfg.seeds, model_slug)
