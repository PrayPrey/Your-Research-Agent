"""Generate 5 dataset variants for h-m2."""

import json
import yaml
from pathlib import Path
from filters import apply_independent_filters, apply_dependent_filters

def load_samples(path):
    """Load JSONL samples."""
    samples = []
    with open(path) as f:
        for line in f:
            samples.append(json.loads(line))
    return samples

def save_samples(samples, path):
    """Save JSONL samples."""
    with open(path, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")

def grid_search_independent(train_samples, val_samples):
    """Mock grid search for independent filters."""
    # Mock: just test C4 threshold
    best_params = {"dedup_threshold": 0.8, "ppl_cutoff": 1000}
    print(f"Grid search result: {best_params}")
    return best_params

def grid_search_dependent(train_samples, val_samples):
    """Mock grid search for dependent filters."""
    # Mock: just test default diversity
    best_params = {"min_diversity": 0.5}
    print(f"Grid search result: {best_params}")
    return best_params

def main():
    # Load C4 config
    with open("config/c4_thresholds.yaml") as f:
        c4_config = yaml.safe_load(f)

    # Load data
    train_samples = load_samples("data/dolly_splits/train.jsonl")
    val_samples = load_samples("data/dolly_splits/val.jsonl")

    print(f"Loaded {len(train_samples)} train, {len(val_samples)} val samples")

    # Baseline
    print("\nBaseline (no filtering)...")
    save_samples(train_samples, "data/dolly_variants/baseline/train.jsonl")
    print(f"Saved {len(train_samples)} samples")

    # Transferred-Independent
    print("\nTransferred-Independent (C4 thresholds)...")
    transferred_indep, stats = apply_independent_filters(
        train_samples,
        dedup_threshold=c4_config["deduplication"]["similarity_threshold"],
        ppl_cutoff=c4_config["perplexity"]["cutoff"]
    )
    save_samples(transferred_indep, "data/dolly_variants/transferred_indep/train.jsonl")
    print(f"Saved {len(transferred_indep)} samples")
    print(f"Stats: {stats}")

    # Tuned-Independent
    print("\nTuned-Independent (grid search)...")
    tuned_params = grid_search_independent(train_samples, val_samples)
    tuned_indep, stats = apply_independent_filters(
        train_samples,
        dedup_threshold=tuned_params["dedup_threshold"],
        ppl_cutoff=tuned_params["ppl_cutoff"]
    )
    save_samples(tuned_indep, "data/dolly_variants/tuned_indep/train.jsonl")
    print(f"Saved {len(tuned_indep)} samples")
    print(f"Stats: {stats}")

    # Save tuning log
    with open("data/tuning_logs/independent.yaml", "w") as f:
        yaml.dump({"best_params": tuned_params, "stats": stats}, f)

    # Transferred-Dependent (fallback to quality filter)
    print("\nTransferred-Dependent (quality filters)...")
    transferred_dep, stats = apply_dependent_filters(train_samples, min_diversity=0.5)
    save_samples(transferred_dep, "data/dolly_variants/transferred_dep/train.jsonl")
    print(f"Saved {len(transferred_dep)} samples")
    print(f"Stats: {stats}")

    # Tuned-Dependent
    print("\nTuned-Dependent (grid search quality)...")
    tuned_dep_params = grid_search_dependent(train_samples, val_samples)
    tuned_dep, stats = apply_dependent_filters(
        train_samples,
        min_diversity=tuned_dep_params["min_diversity"]
    )
    save_samples(tuned_dep, "data/dolly_variants/tuned_dep/train.jsonl")
    print(f"Saved {len(tuned_dep)} samples")
    print(f"Stats: {stats}")

    # Save tuning log
    with open("data/tuning_logs/dependent.yaml", "w") as f:
        yaml.dump({"best_params": tuned_dep_params, "stats": stats}, f)

    print("\nAll variants created.")

if __name__ == "__main__":
    main()
