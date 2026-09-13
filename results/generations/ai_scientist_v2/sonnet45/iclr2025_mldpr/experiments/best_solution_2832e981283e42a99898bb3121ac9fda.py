import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import json
import time

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

# Initialize experiment data tracking
experiment_data = {
    "hash_function_ablation": {
        "synthetic_dataset": {
            "metrics": {},
            "ground_truth": {},
            "predictions": {},
            "timestamps": {},
            "computation_times": {},
        }
    }
}

# Step 1: Create synthetic dataset versions with known changes
np.random.seed(42)


def create_base_dataset(n_samples=1000):
    """Create a base dataset version"""
    data = {
        "id": np.arange(n_samples),
        "feature_1": np.random.randn(n_samples),
        "feature_2": np.random.randint(0, 100, n_samples),
        "feature_3": np.random.choice(["A", "B", "C"], n_samples),
        "feature_4": np.random.randn(n_samples),
        "feature_5": np.random.randint(0, 50, n_samples),
        "feature_6": np.random.choice(["X", "Y", "Z"], n_samples),
        "target": np.random.randint(0, 2, n_samples),
    }
    return pd.DataFrame(data)


def introduce_changes(df_base, change_config):
    """Introduce known changes to create version 2"""
    df_v2 = df_base.copy()
    ground_truth_changes = {
        "additions": [],
        "deletions": [],
        "modifications": [],
        "schema_changes": [],
    }

    # 1. Add new rows
    n_additions = change_config["n_additions"]
    if n_additions > 0:
        new_rows = {
            "id": np.arange(len(df_base), len(df_base) + n_additions),
            "feature_1": np.random.randn(n_additions),
            "feature_2": np.random.randint(0, 100, n_additions),
            "feature_3": np.random.choice(["A", "B", "C"], n_additions),
            "feature_4": np.random.randn(n_additions),
            "feature_5": np.random.randint(0, 50, n_additions),
            "feature_6": np.random.choice(["X", "Y", "Z"], n_additions),
            "target": np.random.randint(0, 2, n_additions),
        }
        df_new = pd.DataFrame(new_rows)
        df_v2 = pd.concat([df_v2, df_new], ignore_index=True)
        ground_truth_changes["additions"] = list(new_rows["id"])

    # 2. Delete rows
    n_deletions = change_config["n_deletions"]
    if n_deletions > 0:
        delete_indices = np.random.choice(
            df_base.index[: len(df_base)], n_deletions, replace=False
        )
        deleted_ids = df_base.loc[delete_indices, "id"].tolist()
        df_v2 = df_v2[~df_v2["id"].isin(deleted_ids)]
        ground_truth_changes["deletions"] = deleted_ids

    # 3. Modify existing rows
    n_modifications = change_config["n_modifications"]
    if n_modifications > 0:
        valid_ids = set(df_base["id"]) - set(ground_truth_changes["deletions"])
        modify_ids = np.random.choice(
            list(valid_ids), min(n_modifications, len(valid_ids)), replace=False
        )
        cols_to_modify = ["feature_1", "feature_2"]
        for mod_id in modify_ids:
            idx = df_v2[df_v2["id"] == mod_id].index[0]
            for col in cols_to_modify:
                if df_v2[col].dtype in [np.float64]:
                    df_v2.loc[idx, col] = np.random.randn()
                elif df_v2[col].dtype in [np.int64]:
                    df_v2.loc[idx, col] = np.random.randint(0, 100)
        ground_truth_changes["modifications"] = modify_ids.tolist()

    # 4. Schema changes
    if change_config["add_column"]:
        df_v2["feature_new"] = np.random.randn(len(df_v2))
        ground_truth_changes["schema_changes"].append("added_column_feature_new")

    return df_v2, ground_truth_changes


# Step 2: Implement change detection system with different hash functions
class DatasetChangeDetector:
    def __init__(self, hash_function="md5"):
        self.hash_function = hash_function
        self.changes_detected = {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "schema_changes": [],
        }
        self.computation_time = 0.0

    def compute_row_hash(self, row):
        """Compute hash for a row using specified hash function"""
        row_str = "".join([str(v) for v in row.values])
        if self.hash_function == "md5":
            return hashlib.md5(row_str.encode()).hexdigest()
        elif self.hash_function == "sha256":
            return hashlib.sha256(row_str.encode()).hexdigest()
        elif self.hash_function == "sha1":
            return hashlib.sha1(row_str.encode()).hexdigest()
        elif self.hash_function == "simple_concat":
            return row_str
        else:
            raise ValueError(f"Unknown hash function: {self.hash_function}")

    def detect_changes(self, df_v1, df_v2, id_column="id"):
        """Detect all types of changes between two dataset versions"""
        start_time = time.time()
        self.changes_detected = {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "schema_changes": [],
        }

        # Detect schema changes
        cols_v1 = set(df_v1.columns)
        cols_v2 = set(df_v2.columns)
        added_cols = cols_v2 - cols_v1
        removed_cols = cols_v1 - cols_v2
        for col in added_cols:
            self.changes_detected["schema_changes"].append(f"added_column_{col}")
        for col in removed_cols:
            self.changes_detected["schema_changes"].append(f"removed_column_{col}")

        # Detect row-level changes
        ids_v1 = set(df_v1[id_column])
        ids_v2 = set(df_v2[id_column])
        self.changes_detected["additions"] = list(ids_v2 - ids_v1)
        self.changes_detected["deletions"] = list(ids_v1 - ids_v2)

        # Modifications
        common_ids = ids_v1 & ids_v2
        common_cols = cols_v1 & cols_v2
        for common_id in common_ids:
            row_v1 = df_v1[df_v1[id_column] == common_id][list(common_cols)].iloc[0]
            row_v2 = df_v2[df_v2[id_column] == common_id][list(common_cols)].iloc[0]
            hash_v1 = self.compute_row_hash(row_v1)
            hash_v2 = self.compute_row_hash(row_v2)
            if hash_v1 != hash_v2:
                self.changes_detected["modifications"].append(common_id)

        self.computation_time = time.time() - start_time
        return self.changes_detected


# Step 3: Evaluate change detection accuracy
def evaluate_change_detection(ground_truth, predictions):
    """Evaluate change detection performance"""
    metrics = {}
    for change_type in ["additions", "deletions", "modifications", "schema_changes"]:
        gt = set(ground_truth.get(change_type, []))
        pred = set(predictions.get(change_type, []))
        if len(gt) == 0 and len(pred) == 0:
            metrics[f"{change_type}_accuracy"] = 1.0
            metrics[f"{change_type}_precision"] = 1.0
            metrics[f"{change_type}_recall"] = 1.0
            metrics[f"{change_type}_f1"] = 1.0
        elif len(gt) == 0:
            metrics[f"{change_type}_accuracy"] = 0.0
            metrics[f"{change_type}_precision"] = 0.0
            metrics[f"{change_type}_recall"] = 1.0
            metrics[f"{change_type}_f1"] = 0.0
        else:
            tp = len(gt & pred)
            fp = len(pred - gt)
            fn = len(gt - pred)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            accuracy = tp / len(gt) if len(gt) > 0 else 0.0
            metrics[f"{change_type}_accuracy"] = accuracy
            metrics[f"{change_type}_precision"] = precision
            metrics[f"{change_type}_recall"] = recall
            metrics[f"{change_type}_f1"] = f1

    # Overall change detection accuracy
    all_gt = set()
    all_pred = set()
    for change_type in ["additions", "deletions", "modifications"]:
        all_gt.update([f"{change_type}_{x}" for x in ground_truth.get(change_type, [])])
        all_pred.update(
            [f"{change_type}_{x}" for x in predictions.get(change_type, [])]
        )
    if len(all_gt) > 0:
        overall_accuracy = len(all_gt & all_pred) / len(all_gt)
    else:
        overall_accuracy = 1.0
    metrics["overall_change_detection_accuracy"] = overall_accuracy
    return metrics


# Step 4: Ablation Study - Hash Function Comparison
print("=" * 70)
print("ABLATION STUDY: Hash Function Comparison")
print("=" * 70)

hash_functions = ["md5", "sha256", "sha1", "simple_concat"]
change_configs = [
    {
        "name": "config_1",
        "n_additions": 50,
        "n_deletions": 30,
        "n_modifications": 40,
        "add_column": True,
    },
    {
        "name": "config_2",
        "n_additions": 100,
        "n_deletions": 50,
        "n_modifications": 80,
        "add_column": False,
    },
    {
        "name": "config_3",
        "n_additions": 20,
        "n_deletions": 10,
        "n_modifications": 15,
        "add_column": True,
    },
]

all_results = {}

for hash_func in hash_functions:
    print(f"\n{'='*70}")
    print(f"Testing Hash Function: {hash_func}")
    print(f"{'='*70}")

    hash_func_results = []
    experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
        hash_func
    ] = {
        "change_detection_accuracy": [],
        "precision": [],
        "recall": [],
        "f1": [],
        "modifications_precision": [],
        "modifications_recall": [],
        "modifications_f1": [],
    }
    experiment_data["hash_function_ablation"]["synthetic_dataset"]["computation_times"][
        hash_func
    ] = []

    for idx, config in enumerate(change_configs):
        print(f"\n  Experiment {idx+1}/{len(change_configs)}: {config['name']}")

        # Create datasets
        df_v1 = create_base_dataset(n_samples=1000)
        df_v2, ground_truth = introduce_changes(df_v1, config)

        # Detect changes with specified hash function
        detector = DatasetChangeDetector(hash_function=hash_func)
        predictions = detector.detect_changes(df_v1, df_v2)

        # Evaluate
        metrics = evaluate_change_detection(ground_truth, predictions)

        print(
            f"    GT Modifications: {len(ground_truth['modifications'])}, Detected: {len(predictions['modifications'])}"
        )
        print(
            f"    Overall Accuracy: {metrics['overall_change_detection_accuracy']:.4f}"
        )
        print(f"    Modifications F1: {metrics['modifications_f1']:.4f}")
        print(f"    Computation Time: {detector.computation_time:.4f}s")

        # Store results
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["change_detection_accuracy"].append(
            metrics["overall_change_detection_accuracy"]
        )
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["precision"].append(
            np.mean(
                [
                    metrics[f"{ct}_precision"]
                    for ct in [
                        "additions",
                        "deletions",
                        "modifications",
                        "schema_changes",
                    ]
                ]
            )
        )
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["recall"].append(
            np.mean(
                [
                    metrics[f"{ct}_recall"]
                    for ct in [
                        "additions",
                        "deletions",
                        "modifications",
                        "schema_changes",
                    ]
                ]
            )
        )
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["f1"].append(
            np.mean(
                [
                    metrics[f"{ct}_f1"]
                    for ct in [
                        "additions",
                        "deletions",
                        "modifications",
                        "schema_changes",
                    ]
                ]
            )
        )
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["modifications_precision"].append(metrics["modifications_precision"])
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["modifications_recall"].append(metrics["modifications_recall"])
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ]["modifications_f1"].append(metrics["modifications_f1"])
        experiment_data["hash_function_ablation"]["synthetic_dataset"][
            "computation_times"
        ][hash_func].append(detector.computation_time)

        hash_func_results.append(
            {
                "config": config,
                "ground_truth": ground_truth,
                "predictions": predictions,
                "metrics": metrics,
                "computation_time": detector.computation_time,
            }
        )

    all_results[hash_func] = hash_func_results
    experiment_data["hash_function_ablation"]["synthetic_dataset"]["ground_truth"][
        hash_func
    ] = [r["ground_truth"] for r in hash_func_results]
    experiment_data["hash_function_ablation"]["synthetic_dataset"]["predictions"][
        hash_func
    ] = [r["predictions"] for r in hash_func_results]
    experiment_data["hash_function_ablation"]["synthetic_dataset"]["timestamps"][
        hash_func
    ] = datetime.now().isoformat()

# Step 5: Analysis and Visualization
print("\n" + "=" * 70)
print("ANALYSIS: Comparing Hash Functions")
print("=" * 70)

# Calculate summary statistics
summary_stats = {}
for hash_func in hash_functions:
    metrics = experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
        hash_func
    ]
    comp_times = experiment_data["hash_function_ablation"]["synthetic_dataset"][
        "computation_times"
    ][hash_func]
    summary_stats[hash_func] = {
        "mean_accuracy": np.mean(metrics["change_detection_accuracy"]),
        "std_accuracy": np.std(metrics["change_detection_accuracy"]),
        "mean_f1": np.mean(metrics["f1"]),
        "mean_modifications_f1": np.mean(metrics["modifications_f1"]),
        "mean_computation_time": np.mean(comp_times),
        "std_computation_time": np.std(comp_times),
    }
    print(f"\n{hash_func}:")
    print(
        f"  Mean Accuracy: {summary_stats[hash_func]['mean_accuracy']:.4f} ± {summary_stats[hash_func]['std_accuracy']:.4f}"
    )
    print(f"  Mean F1 Score: {summary_stats[hash_func]['mean_f1']:.4f}")
    print(
        f"  Mean Modifications F1: {summary_stats[hash_func]['mean_modifications_f1']:.4f}"
    )
    print(
        f"  Mean Computation Time: {summary_stats[hash_func]['mean_computation_time']:.4f}s ± {summary_stats[hash_func]['std_computation_time']:.4f}s"
    )

# Find best hash function (by accuracy)
best_hash_func = max(summary_stats.items(), key=lambda x: x[1]["mean_accuracy"])
fastest_hash_func = min(
    summary_stats.items(), key=lambda x: x[1]["mean_computation_time"]
)

print(f"\n{'='*70}")
print(
    f"BEST ACCURACY: {best_hash_func[0]} with mean accuracy {best_hash_func[1]['mean_accuracy']:.4f}"
)
print(
    f"FASTEST: {fastest_hash_func[0]} with mean time {fastest_hash_func[1]['mean_computation_time']:.4f}s"
)
print(f"{'='*70}")

# Step 6: Visualizations
print("\nGenerating visualizations...")

# Plot 1: Overall accuracy and computation time comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
x_pos = np.arange(len(hash_functions))
accuracies = [summary_stats[h]["mean_accuracy"] for h in hash_functions]
stds = [summary_stats[h]["std_accuracy"] for h in hash_functions]
bars = ax1.bar(x_pos, accuracies, yerr=stds, capsize=5, alpha=0.7, color="steelblue")
ax1.set_xlabel("Hash Function", fontsize=12)
ax1.set_ylabel("Mean Change Detection Accuracy", fontsize=12)
ax1.set_title(
    "Hash Function Ablation: Detection Accuracy", fontsize=14, fontweight="bold"
)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(hash_functions, rotation=45, ha="right")
ax1.set_ylim([0, 1.1])
ax1.axhline(
    y=np.mean(accuracies),
    color="r",
    linestyle="--",
    linewidth=2,
    label=f"Overall Mean: {np.mean(accuracies):.3f}",
)
ax1.legend()
ax1.grid(True, alpha=0.3, axis="y")

comp_times = [summary_stats[h]["mean_computation_time"] for h in hash_functions]
comp_stds = [summary_stats[h]["std_computation_time"] for h in hash_functions]
bars2 = ax2.bar(x_pos, comp_times, yerr=comp_stds, capsize=5, alpha=0.7, color="coral")
ax2.set_xlabel("Hash Function", fontsize=12)
ax2.set_ylabel("Mean Computation Time (seconds)", fontsize=12)
ax2.set_title(
    "Hash Function Ablation: Computation Time", fontsize=14, fontweight="bold"
)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(hash_functions, rotation=45, ha="right")
ax2.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "hash_function_comparison.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 2: Detailed metrics heatmap
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
metric_names = ["change_detection_accuracy", "precision", "recall", "f1"]
titles = ["Change Detection Accuracy", "Precision", "Recall", "F1 Score"]
for idx, (metric_name, title) in enumerate(zip(metric_names, titles)):
    ax = axes[idx // 2, idx % 2]
    data_matrix = []
    for hash_func in hash_functions:
        row = experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][
            hash_func
        ][metric_name]
        data_matrix.append(row)
    data_matrix = np.array(data_matrix)
    im = ax.imshow(data_matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(change_configs)))
    ax.set_yticks(np.arange(len(hash_functions)))
    ax.set_xticklabels([c["name"] for c in change_configs])
    ax.set_yticklabels(hash_functions)
    ax.set_xlabel("Experiment Config", fontsize=10)
    ax.set_ylabel("Hash Function", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    for i in range(len(hash_functions)):
        for j in range(len(change_configs)):
            text = ax.text(
                j,
                i,
                f"{data_matrix[i, j]:.2f}",
                ha="center",
                va="center",
                color="black",
                fontsize=8,
            )
    plt.colorbar(im, ax=ax)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "hash_function_heatmap.png"), dpi=300, bbox_inches="tight"
)
plt.close()

# Plot 3: Accuracy vs Computation Time Trade-off
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
for hash_func in hash_functions:
    mean_acc = summary_stats[hash_func]["mean_accuracy"]
    mean_time = summary_stats[hash_func]["mean_computation_time"]
    std_acc = summary_stats[hash_func]["std_accuracy"]
    std_time = summary_stats[hash_func]["std_computation_time"]
    ax.errorbar(
        mean_time,
        mean_acc,
        xerr=std_time,
        yerr=std_acc,
        fmt="o",
        markersize=12,
        capsize=5,
        label=hash_func,
        alpha=0.7,
    )
    ax.annotate(
        hash_func,
        (mean_time, mean_acc),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=10,
    )
ax.set_xlabel("Mean Computation Time (seconds)", fontsize=12)
ax.set_ylabel("Mean Detection Accuracy", fontsize=12)
ax.set_title(
    "Hash Function Trade-off: Accuracy vs Computation Time",
    fontsize=14,
    fontweight="bold",
)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "hash_function_tradeoff.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 4: Modifications detection performance
fig, ax = plt.subplots(1, 1, figsize=(12, 6))
x_pos = np.arange(len(hash_functions))
width = 0.25
modifications_precision = [
    np.mean(
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][h][
            "modifications_precision"
        ]
    )
    for h in hash_functions
]
modifications_recall = [
    np.mean(
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][h][
            "modifications_recall"
        ]
    )
    for h in hash_functions
]
modifications_f1 = [
    np.mean(
        experiment_data["hash_function_ablation"]["synthetic_dataset"]["metrics"][h][
            "modifications_f1"
        ]
    )
    for h in hash_functions
]
ax.bar(
    x_pos - width,
    modifications_precision,
    width,
    label="Precision",
    alpha=0.8,
    color="blue",
)
ax.bar(x_pos, modifications_recall, width, label="Recall", alpha=0.8, color="green")
ax.bar(
    x_pos + width, modifications_f1, width, label="F1 Score", alpha=0.8, color="orange"
)
ax.set_xlabel("Hash Function", fontsize=12)
ax.set_ylabel("Score", fontsize=12)
ax.set_title(
    "Modifications Detection Performance by Hash Function",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(x_pos)
ax.set_xticklabels(hash_functions, rotation=45, ha="right")
ax.set_ylim([0, 1.1])
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "hash_modifications_detection.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Step 7: Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Save detailed results as JSON
results_summary = {
    "ablation_type": "hash_function",
    "hash_functions_tested": hash_functions,
    "num_experiments_per_function": len(change_configs),
    "best_accuracy_function": best_hash_func[0],
    "best_accuracy": float(best_hash_func[1]["mean_accuracy"]),
    "fastest_function": fastest_hash_func[0],
    "fastest_time": float(fastest_hash_func[1]["mean_computation_time"]),
    "summary_statistics": {
        hash_func: {
            "mean_accuracy": float(summary_stats[hash_func]["mean_accuracy"]),
            "std_accuracy": float(summary_stats[hash_func]["std_accuracy"]),
            "mean_f1": float(summary_stats[hash_func]["mean_f1"]),
            "mean_modifications_f1": float(
                summary_stats[hash_func]["mean_modifications_f1"]
            ),
            "mean_computation_time": float(
                summary_stats[hash_func]["mean_computation_time"]
            ),
            "std_computation_time": float(
                summary_stats[hash_func]["std_computation_time"]
            ),
        }
        for hash_func in hash_functions
    },
}

with open(os.path.join(working_dir, "hash_ablation_results.json"), "w") as f:
    json.dump(results_summary, f, indent=2)

# Final summary
print("\n" + "=" * 70)
print("HASH FUNCTION ABLATION COMPLETE")
print("=" * 70)
print(f"Total Hash Functions Tested: {len(hash_functions)}")
print(f"Experiments per Function: {len(change_configs)}")
print(f"Total Experiments Conducted: {len(hash_functions) * len(change_configs)}")
print(f"\nBest Accuracy: {best_hash_func[0]}")
print(
    f"  Mean Accuracy: {best_hash_func[1]['mean_accuracy']:.4f} ± {best_hash_func[1]['std_accuracy']:.4f}"
)
print(f"  Mean Computation Time: {best_hash_func[1]['mean_computation_time']:.4f}s")
print(f"\nFastest: {fastest_hash_func[0]}")
print(
    f"  Mean Computation Time: {fastest_hash_func[1]['mean_computation_time']:.4f}s ± {fastest_hash_func[1]['std_computation_time']:.4f}s"
)
print(f"  Mean Accuracy: {fastest_hash_func[1]['mean_accuracy']:.4f}")
print(f"\nAll results saved to: {working_dir}")
print("=" * 70)
