"""Generate synthetic but realistic SOTA histories for DNSI PoC validation.

Uses realistic patterns from known benchmark trajectories:
- ImageNet: 2012-2024, from 63% to 91% top-1
- CIFAR-10: 2012-2024, from 84% to 99.5%
- CIFAR-100: 2012-2024, from 65% to 96%
- MNIST: 1998-2020, from 99.2% to 99.87%
"""

import json
import os
from datetime import datetime, timedelta
import random
from config import CONFIG, TARGET_BENCHMARKS


def generate_sota_trajectory(
    start_date: datetime,
    end_date: datetime,
    start_acc: float,
    end_acc: float,
    num_entries: int,
    saturation_year: int | None = None,
) -> list[dict]:
    """Generate realistic SOTA trajectory with optional saturation point."""
    random.seed(CONFIG["seed"])

    span_days = (end_date - start_date).days
    entries = []

    # Generate entry dates evenly spread across the full range with small jitter
    dates = []
    step = span_days / num_entries
    for i in range(num_entries):
        base_offset = int(i * step)
        jitter = random.randint(-15, 15)
        offset = max(0, min(span_days, base_offset + jitter))
        dates.append(start_date + timedelta(days=offset))
    dates = sorted(dates)

    # Generate accuracies with diminishing returns (saturation curve)
    improvement_range = end_acc - start_acc
    current_acc = start_acc
    best_acc = start_acc

    # Ensure we get enough entries by guaranteeing improvement at each step
    target_entries = min(num_entries, 50)  # Cap at 50 entries
    step_improvement = improvement_range / target_entries

    for i, dt in enumerate(dates[:target_entries]):
        # Diminishing returns: smaller improvements over time
        progress = i / target_entries
        jitter = random.uniform(0.5, 1.5)
        improvement = step_improvement * (1.0 - 0.5 * progress) * jitter

        if saturation_year and dt.year >= saturation_year:
            improvement *= 0.2  # Post-saturation: much slower

        best_acc = min(end_acc, best_acc + improvement)
        entries.append({
            "date": dt.strftime("%Y-%m-%d"),
            "metrics": {"Accuracy": round(best_acc, 2)},
            "paper": {"title": f"SOTA Model v{len(entries)+1}", "date": dt.strftime("%Y-%m-%d")},
        })

    return entries


def generate_benchmark_data() -> dict:
    """Generate complete synthetic benchmark dataset."""
    benchmarks = {}

    # ImageNet: saturated benchmark, 1000 classes
    benchmarks["ImageNet"] = {
        "task": "Image Classification",
        "dataset": "ImageNet",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2012, 1, 1), datetime(2024, 1, 1),
            63.0, 91.0, 150, saturation_year=2021
        )}
    }

    # CIFAR-10: highly saturated, 10 classes
    benchmarks["CIFAR-10"] = {
        "task": "Image Classification",
        "dataset": "CIFAR-10",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2012, 1, 1), datetime(2024, 1, 1),
            84.0, 99.5, 120, saturation_year=2019
        )}
    }

    # CIFAR-100: moderately saturated, 100 classes
    benchmarks["CIFAR-100"] = {
        "task": "Image Classification",
        "dataset": "CIFAR-100",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2012, 1, 1), datetime(2024, 1, 1),
            65.0, 96.0, 100, saturation_year=2022
        )}
    }

    # MNIST: very saturated, 10 classes
    benchmarks["MNIST"] = {
        "task": "Image Classification",
        "dataset": "MNIST",
        "sota": {"rows": generate_sota_trajectory(
            datetime(1998, 1, 1), datetime(2020, 1, 1),
            99.2, 99.87, 80, saturation_year=2015
        )}
    }

    # COCO Detection: 80 classes
    benchmarks["COCO Detection"] = {
        "task": "Object Detection",
        "dataset": "COCO",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2014, 1, 1), datetime(2024, 1, 1),
            30.0, 63.0, 90, saturation_year=2022
        )}
    }

    # GLUE: NLP, varies (set to 9 tasks average)
    benchmarks["GLUE"] = {
        "task": "Natural Language Understanding",
        "dataset": "GLUE",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2018, 1, 1), datetime(2024, 1, 1),
            70.0, 92.0, 80, saturation_year=2022
        )}
    }

    # SQuAD: Reading comprehension (no difficulty proxy)
    benchmarks["SQuAD"] = {
        "task": "Question Answering",
        "dataset": "SQuAD",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2016, 1, 1), datetime(2024, 1, 1),
            67.0, 93.0, 70, saturation_year=2020
        )}
    }

    # WMT En-De: Translation (no difficulty proxy)
    benchmarks["WMT En-De"] = {
        "task": "Machine Translation",
        "dataset": "WMT En-De",
        "sota": {"rows": generate_sota_trajectory(
            datetime(2014, 1, 1), datetime(2024, 1, 1),
            20.0, 35.0, 60, saturation_year=2021
        )}
    }

    return list(benchmarks.values())


def save_synthetic_data(output_path: str) -> None:
    """Save synthetic data to JSON file."""
    data = generate_benchmark_data()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[SYNTHETIC] Generated {len(data)} benchmark histories -> {output_path}")


if __name__ == "__main__":
    save_synthetic_data("data/pwc/evaluation-tables.json")
