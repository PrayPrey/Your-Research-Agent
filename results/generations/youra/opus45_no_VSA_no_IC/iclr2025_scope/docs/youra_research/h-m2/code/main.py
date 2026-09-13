"""Sweep driver for h-m2: runs HotpotQA sweep + combines with h-e1 SQuAD-v2 results."""
import os
import csv
import argparse
from datetime import datetime
import pandas as pd

from config import MODELS, RANKS, SEEDS, TrainConfig, Paths


def run_hotpotqa_sweep(
    output_csv: str | None = None,
    checkpoint_dir: str = "checkpoints",
    data_cache_dir: str | None = None,
    resume: bool = True,
) -> None:
    """Run HotpotQA sweep (72 runs) and write results to CSV incrementally."""
    from train_hotpotqa import train_one_run_hotpotqa

    paths = Paths()
    output_csv = output_csv or paths.rank_sweep_hotpotqa_csv

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
            writer.writerow(["model", "rank", "seed", "f1_score", "timestamp"])

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

                print(f"\n[{run_idx}/{total_runs}] Training HotpotQA {model_id} r={rank} s={seed}")

                try:
                    f1 = train_one_run_hotpotqa(
                        model_id=model_id,
                        rank=rank,
                        seed=seed,
                        cfg=cfg,
                        output_dir=os.path.join(checkpoint_dir, f"hotpotqa_{model_id}_r{rank}_s{seed}"),
                        data_cache_dir=data_cache_dir,
                    )

                    with open(output_csv, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([model_id, rank, seed, f"{f1:.4f}", datetime.now().isoformat()])

                    print(f"[{run_idx}/{total_runs}] {model_id} r={rank} s={seed}: F1={f1:.4f}")

                except Exception as e:
                    print(f"[{run_idx}/{total_runs}] FAILED {model_id} r={rank} s={seed}: {e}")
                    with open(output_csv + ".errors", "a") as f:
                        f.write(f"{datetime.now().isoformat()},{model_id},{rank},{seed},{e}\n")

    print(f"\nHotpotQA sweep complete. Results: {output_csv}")


def build_combined_dataset(
    squad_csv: str | None = None,
    hotpotqa_csv: str | None = None,
    output_csv: str | None = None,
) -> pd.DataFrame:
    """Merge h-e1 SQuAD-v2 CSV + h-m2 HotpotQA CSV into combined DataFrame."""
    paths = Paths()
    squad_csv = squad_csv or paths.rank_sweep_squad_csv
    hotpotqa_csv = hotpotqa_csv or paths.rank_sweep_hotpotqa_csv
    output_csv = output_csv or "results/h-m2_combined.csv"

    squad_df = pd.read_csv(squad_csv)
    squad_df["dataset"] = "squad_v2"

    hotpotqa_df = pd.read_csv(hotpotqa_csv)
    hotpotqa_df["dataset"] = "hotpotqa"

    combined = pd.concat([squad_df, hotpotqa_df], ignore_index=True)

    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    combined.to_csv(output_csv, index=False)
    print(f"Combined dataset saved: {output_csv}")

    return combined


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="h-m2 Rank Sensitivity Sweep Driver")
    parser.add_argument("--output", default=None, help="Output CSV path")
    parser.add_argument("--checkpoint-dir", default="checkpoints", help="Checkpoint directory")
    parser.add_argument("--data-cache", default=None, help="Data cache directory")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh (don't resume)")
    parser.add_argument("--combine-only", action="store_true", help="Only combine existing results")

    args = parser.parse_args()

    if args.combine_only:
        build_combined_dataset()
    else:
        run_hotpotqa_sweep(
            output_csv=args.output,
            checkpoint_dir=args.checkpoint_dir,
            data_cache_dir=args.data_cache,
            resume=not args.no_resume,
        )
