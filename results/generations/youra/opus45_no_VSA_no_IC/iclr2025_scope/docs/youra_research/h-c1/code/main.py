"""Sweep driver: runs 72 training runs (4 models x 6 ranks x 3 seeds) on HotpotQA."""
import os
import csv
import argparse
from datetime import datetime

from config import MODELS, RANKS, SEEDS, TrainConfig, Paths


def run_sweep(
    output_csv: str | None = None,
    checkpoint_dir: str = "checkpoints",
    data_cache_dir: str | None = None,
    resume: bool = True,
) -> None:
    """Run full sweep and write results to CSV incrementally."""
    from train_hotpot import train_one_run

    paths = Paths()
    output_csv = output_csv or paths.rank_sweep_csv

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)

    completed = set()
    if resume and os.path.exists(output_csv):
        with open(output_csv, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["model"], int(row["rank"]), int(row["seed"]))
                completed.add(key)
        print(f"Resuming: {len(completed)} runs already completed")

    if not os.path.exists(output_csv):
        with open(output_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["model", "rank", "seed", "f1_score", "exact_match", "timestamp"])

    cfg = TrainConfig()
    total_runs = len(MODELS) * len(RANKS) * len(SEEDS)
    run_idx = 0

    for model_id in MODELS:
        for rank in RANKS:
            for seed in SEEDS:
                run_idx += 1
                key = (model_id, rank, seed)

                if key in completed:
                    print(f"[{run_idx}/{total_runs}] Skipping {model_id} r={rank} s={seed} (already done)")
                    continue

                print(f"\n[{run_idx}/{total_runs}] Training {model_id} r={rank} s={seed}")

                try:
                    metrics = train_one_run(
                        model_id=model_id,
                        rank=rank,
                        seed=seed,
                        cfg=cfg,
                        output_dir=os.path.join(checkpoint_dir, f"{model_id}_r{rank}_s{seed}"),
                        data_cache_dir=data_cache_dir,
                    )

                    with open(output_csv, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            model_id, rank, seed,
                            f"{metrics['answer_f1']:.4f}",
                            f"{metrics['exact_match']:.4f}",
                            datetime.now().isoformat()
                        ])

                    print(f"[{run_idx}/{total_runs}] {model_id} r={rank} s={seed}: F1={metrics['answer_f1']:.4f}")

                except Exception as e:
                    print(f"[{run_idx}/{total_runs}] FAILED {model_id} r={rank} s={seed}: {e}")
                    with open(output_csv + ".errors", "a") as f:
                        f.write(f"{datetime.now().isoformat()},{model_id},{rank},{seed},{e}\n")

    print(f"\nSweep complete. Results: {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LoRA Rank Sweep Driver for HotpotQA")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--checkpoint-dir", default="checkpoints", help="Checkpoint directory")
    parser.add_argument("--data-cache", default=None, help="Data cache directory")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh (don't resume)")

    args = parser.parse_args()
    run_sweep(
        output_csv=args.output,
        checkpoint_dir=args.checkpoint_dir,
        data_cache_dir=args.data_cache,
        resume=not args.no_resume,
    )
