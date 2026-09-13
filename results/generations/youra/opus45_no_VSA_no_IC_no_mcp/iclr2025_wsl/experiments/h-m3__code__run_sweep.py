import time
from typing import List, Dict, Tuple

import torch
import torch.nn as nn

from config import ExperimentConfig, ExperimentResult
from synth_data import make_backdoor_dataset, make_accuracy_dataset, build_dataloader, default_weight_shapes
from train_task import build_model, train_task, predict
from metrics import compute_auc, compute_rmse_r2


def set_seed(seed: int):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def verify_param_counts(cfg: ExperimentConfig) -> Dict[str, int]:
    counts = {}
    for arch in cfg.architectures:
        model = build_model(arch, cfg.weight_shapes, cfg.hidden_dim, num_classes=1)
        counts[arch] = sum(p.numel() for p in model.parameters())

    base_count = counts["mlp"]
    for arch, count in counts.items():
        ratio = abs(count - base_count) / base_count
        if ratio > cfg.param_count_tolerance:
            print(f"Warning: {arch} param count {count} differs from MLP {base_count} by {ratio*100:.1f}%")

    return counts


def run_single(task: str, architecture: str, seed: int, cfg: ExperimentConfig) -> Tuple[ExperimentResult, Dict[int, float]]:
    set_seed(seed)

    if task == "backdoor":
        train_w, train_y = make_backdoor_dataset(cfg.n_train, cfg.weight_shapes, seed)
        test_w, test_y = make_backdoor_dataset(cfg.n_test, cfg.weight_shapes, seed + 1000)
        loss_fn = nn.BCEWithLogitsLoss()
    else:
        train_w, train_y = make_accuracy_dataset(cfg.n_train, cfg.weight_shapes, seed)
        test_w, test_y = make_accuracy_dataset(cfg.n_test, cfg.weight_shapes, seed + 1000)
        loss_fn = nn.MSELoss()

    model = build_model(architecture, cfg.weight_shapes, cfg.hidden_dim, num_classes=1)
    train_loader = build_dataloader(train_w, train_y, cfg.batch_size, shuffle=True)
    test_loader = build_dataloader(test_w, test_y, cfg.batch_size, shuffle=False)

    start_time = time.time()
    model, history = train_task(model, train_loader, cfg, loss_fn)
    train_time = time.time() - start_time

    preds, labels = predict(model, test_loader, cfg.device)

    if task == "backdoor":
        metric = compute_auc(preds, labels)
        secondary = None
    else:
        metric, secondary = compute_rmse_r2(preds, labels)

    result = ExperimentResult(
        task=task,
        architecture=architecture,
        seed=seed,
        metric_value=metric,
        secondary_metric=secondary,
        train_time=train_time
    )

    return result, history


def run_sweep(cfg: ExperimentConfig) -> Tuple[List[ExperimentResult], Dict[str, Dict[int, float]]]:
    print("Verifying param counts...")
    param_counts = verify_param_counts(cfg)
    for arch, count in param_counts.items():
        print(f"  {arch}: {count:,} params")

    results = []
    all_histories = {}

    total_runs = len(cfg.tasks) * len(cfg.architectures) * len(cfg.seeds)
    run_idx = 0

    for task in cfg.tasks:
        for arch in cfg.architectures:
            for seed in cfg.seeds:
                run_idx += 1
                print(f"Run {run_idx}/{total_runs}: {task}/{arch}/seed={seed}")

                result, history = run_single(task, arch, seed, cfg)
                results.append(result)
                all_histories[f"{task}_{arch}_{seed}"] = history

                if task == "backdoor":
                    print(f"  AUC: {result.metric_value:.4f}, time: {result.train_time:.1f}s")
                else:
                    print(f"  RMSE: {result.metric_value:.4f}, R2: {result.secondary_metric:.4f}, time: {result.train_time:.1f}s")

    return results, all_histories
