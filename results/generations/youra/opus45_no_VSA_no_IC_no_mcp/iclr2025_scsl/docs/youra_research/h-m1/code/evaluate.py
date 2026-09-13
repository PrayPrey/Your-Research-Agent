import json
import os
import numpy as np
from config import Config


def early_epoch_ratio(records: list, early_range: tuple = (1, 10)) -> float:
    early_records = [r for r in records if early_range[0] <= r["epoch"] <= early_range[1]]
    return np.mean([r["ratio"] for r in early_records])


def ratio_trend_decreasing(records: list) -> bool:
    first_half = records[:len(records)//2]
    second_half = records[len(records)//2:]
    avg_first = np.mean([r["ratio"] for r in first_half])
    avg_second = np.mean([r["ratio"] for r in second_half])
    return avg_second < avg_first


def check_gate(all_seed_records: dict, config: Config) -> dict:
    per_seed = {}
    early_ratios = []
    decreasing_results = []

    for seed, records in all_seed_records.items():
        er = early_epoch_ratio(records, config.early_epoch_range)
        dec = ratio_trend_decreasing(records)
        early_ratios.append(er)
        decreasing_results.append(dec)
        per_seed[seed] = {
            "early_ratio": er,
            "decreasing": dec,
            "pass": er >= config.ratio_threshold
        }

    mean_early_ratio = np.mean(early_ratios)
    all_decreasing = all(decreasing_results)
    majority_pass = sum(1 for er in early_ratios if er >= config.ratio_threshold) >= len(early_ratios) / 2

    return {
        "pass": majority_pass,
        "mean_early_ratio": mean_early_ratio,
        "all_decreasing": all_decreasing,
        "per_seed": per_seed,
        "threshold": config.ratio_threshold
    }


def save_metrics(all_seed_records: dict, gate_result: dict, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    serializable = {
        "pass": bool(gate_result["pass"]),
        "mean_early_ratio": float(gate_result["mean_early_ratio"]),
        "all_decreasing": bool(gate_result["all_decreasing"]),
        "threshold": float(gate_result["threshold"]),
        "per_seed": {
            int(k): {
                "early_ratio": float(v["early_ratio"]),
                "decreasing": bool(v["decreasing"]),
                "pass": bool(v["pass"])
            } for k, v in gate_result["per_seed"].items()
        }
    }

    with open(os.path.join(output_dir, "gate_result.json"), "w") as f:
        json.dump(serializable, f, indent=2)


def main():
    config = Config()
    records_path = os.path.join(config.output_dir, "gradient_norm_records.json")

    with open(records_path, "r") as f:
        all_seed_records = json.load(f)

    all_seed_records = {int(k): v for k, v in all_seed_records.items()}
    gate_result = check_gate(all_seed_records, config)
    save_metrics(all_seed_records, gate_result, config.output_dir)

    print("\n" + "="*60)
    print("GATE CHECK RESULTS (MUST_WORK)")
    print("="*60)
    print(f"Pass: {gate_result['pass']}")
    print(f"Mean Early Ratio (epochs 1-10): {gate_result['mean_early_ratio']:.4f}")
    print(f"Threshold: {gate_result['threshold']}")
    print(f"All Seeds Decreasing Trend: {gate_result['all_decreasing']}")
    print("\nPer-seed results:")
    for seed, res in gate_result["per_seed"].items():
        print(f"  Seed {seed}: early_ratio={res['early_ratio']:.4f}, "
              f"decreasing={res['decreasing']}, pass={res['pass']}")
    print("="*60)

    return gate_result


if __name__ == "__main__":
    main()
