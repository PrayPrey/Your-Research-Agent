#!/usr/bin/env python
"""PoC validation sweep: reduced scale to verify mechanism works."""
import os
import csv
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MODEL_HF_IDS, MODELS, TrainConfig, Paths

POC_MODELS = ["pythia-1b", "pythia-2.8b"]
POC_RANKS = [8, 16, 32]
POC_SEEDS = [42, 1337]

DATA_CACHE = "/home/PrayPrey/YOURA_no_VSA_no_IC/opus45/TEST_scope/docs/youra_research/.data_cache/datasets"


def run_poc_sweep():
    """Run PoC sweep with reduced parameters."""
    from train import train_one_run

    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    output_csv = os.path.join(output_dir, "h-e1_rank_sweep.csv")
    checkpoint_dir = "checkpoints"
    os.makedirs(checkpoint_dir, exist_ok=True)

    completed = set()
    if os.path.exists(output_csv):
        with open(output_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["model"], int(row["rank"]), int(row["seed"]))
                completed.add(key)
        print(f"Resuming: {len(completed)} runs done")
    else:
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["model", "rank", "seed", "f1_score", "timestamp"])

    cfg = TrainConfig()
    cfg.epochs = 1

    total = len(POC_MODELS) * len(POC_RANKS) * len(POC_SEEDS)
    run_idx = 0

    for model_id in POC_MODELS:
        for rank in POC_RANKS:
            for seed in POC_SEEDS:
                run_idx += 1
                key = (model_id, rank, seed)

                if key in completed:
                    print(f"[{run_idx}/{total}] Skip {model_id} r={rank} s={seed}")
                    continue

                print(f"\n[{run_idx}/{total}] {model_id} r={rank} s={seed}")

                try:
                    f1 = train_one_run(
                        model_id=model_id,
                        rank=rank,
                        seed=seed,
                        cfg=cfg,
                        output_dir=os.path.join(checkpoint_dir, f"{model_id}_r{rank}_s{seed}"),
                        data_cache_dir=DATA_CACHE,
                    )

                    with open(output_csv, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([model_id, rank, seed, f"{f1:.4f}", datetime.now().isoformat()])

                    print(f"[{run_idx}/{total}] F1={f1:.4f}")

                except Exception as e:
                    print(f"[{run_idx}/{total}] FAILED: {e}")
                    import traceback
                    traceback.print_exc()

    print(f"\nPoC sweep done: {output_csv}")
    return output_csv


if __name__ == "__main__":
    run_poc_sweep()
