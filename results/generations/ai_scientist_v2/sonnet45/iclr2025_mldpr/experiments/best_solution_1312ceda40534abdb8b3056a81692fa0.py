import os
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score
import json
from datetime import datetime
import hashlib

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data tracking
experiment_data = {"n_samples_tuning": {}}

# Step 1: Create synthetic dataset versions with known changes
np.random.seed(42)


def create_base_dataset(n_samples=1000):
    """Create a base dataset version"""
    data = {
        "id": np.arange(n_samples),
        "feature_1": np.random.randn(n_samples),
        "feature_2": np.random.randint(0, 100, n_samples),
        "feature_3": np.random.choice(["A", "B", "C"], n_samples),
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
        for mod_id in modify_ids:
            idx = df_v2[df_v2["id"] == mod_id].index[0]
            df_v2.loc[idx, "feature_1"] = np.random.randn()
            df_v2.loc[idx, "feature_2"] = np.random.randint(0, 100)
        ground_truth_changes["modifications"] = modify_ids.tolist()

    # 4. Schema changes (add new column)
    if change_config["add_column"]:
        df_v2["feature_4"] = np.random.randn(len(df_v2))
        ground_truth_changes["schema_changes"].append("added_column_feature_4")

    return df_v2, ground_truth_changes


# Step 2: Implement change detection system
class DatasetChangeDetector:
    def __init__(self):
        self.changes_detected = {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "schema_changes": [],
        }

    def compute_row_hash(self, row):
        """Compute hash for a row to detect modifications"""
        row_str = "".join([str(v) for v in row.values])
        return hashlib.md5(row_str.encode()).hexdigest()

    def detect_changes(self, df_v1, df_v2, id_column="id"):
        """Detect all types of changes between two dataset versions"""
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

        # Additions
        self.changes_detected["additions"] = list(ids_v2 - ids_v1)

        # Deletions
        self.changes_detected["deletions"] = list(ids_v1 - ids_v2)

        # Modifications (rows that exist in both but have different values)
        common_ids = ids_v1 & ids_v2
        common_cols = cols_v1 & cols_v2

        for common_id in common_ids:
            row_v1 = df_v1[df_v1[id_column] == common_id][list(common_cols)].iloc[0]
            row_v2 = df_v2[df_v2[id_column] == common_id][list(common_cols)].iloc[0]

            hash_v1 = self.compute_row_hash(row_v1)
            hash_v2 = self.compute_row_hash(row_v2)

            if hash_v1 != hash_v2:
                self.changes_detected["modifications"].append(common_id)

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


# Step 4: Hyperparameter tuning - test different n_samples values
print("=" * 50)
print("Starting Dataset Change Detection with n_samples Hyperparameter Tuning")
print("=" * 50)

# Hyperparameter: different dataset sizes to test
n_samples_values = [500, 1000, 2000, 5000, 10000]

# Change configurations to test with each dataset size
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
    {
        "name": "config_4",
        "n_additions": 150,
        "n_deletions": 100,
        "n_modifications": 120,
        "add_column": True,
    },
    {
        "name": "config_5",
        "n_additions": 5,
        "n_deletions": 5,
        "n_modifications": 10,
        "add_column": False,
    },
]

# Run experiments for each n_samples value
for n_samples in n_samples_values:
    print(f"\n{'='*50}")
    print(f"Testing n_samples = {n_samples}")
    print(f"{'='*50}")

    # Initialize storage for this n_samples value
    experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"] = {
        "metrics": {
            "change_detection_accuracy": [],
            "precision": [],
            "recall": [],
            "f1": [],
        },
        "change_types": {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "schema_changes": [],
        },
        "ground_truth": [],
        "predictions": [],
        "timestamps": [],
        "n_samples": n_samples,
    }

    all_results = []

    for idx, config in enumerate(change_configs):
        print(f"\n  Experiment {idx+1}/{len(change_configs)}: {config['name']}")

        # Create datasets with the current n_samples
        df_v1 = create_base_dataset(n_samples=n_samples)
        df_v2, ground_truth = introduce_changes(df_v1, config)

        # Detect changes
        detector = DatasetChangeDetector()
        predictions = detector.detect_changes(df_v1, df_v2)

        # Evaluate
        metrics = evaluate_change_detection(ground_truth, predictions)

        # Print results
        print(
            f"  Ground Truth - Additions: {len(ground_truth['additions'])}, Deletions: {len(ground_truth['deletions'])}, "
            f"Modifications: {len(ground_truth['modifications'])}, Schema: {len(ground_truth['schema_changes'])}"
        )
        print(
            f"  Detected - Additions: {len(predictions['additions'])}, Deletions: {len(predictions['deletions'])}, "
            f"Modifications: {len(predictions['modifications'])}, Schema: {len(predictions['schema_changes'])}"
        )
        print(
            f"  Overall Change Detection Accuracy: {metrics['overall_change_detection_accuracy']:.4f}"
        )

        # Store results
        experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"]["metrics"][
            "change_detection_accuracy"
        ].append(metrics["overall_change_detection_accuracy"])
        experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"]["metrics"][
            "precision"
        ].append(
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
        experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"]["metrics"][
            "recall"
        ].append(
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
        experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"]["metrics"][
            "f1"
        ].append(
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
        experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"][
            "timestamps"
        ].append(datetime.now().isoformat())

        all_results.append(
            {
                "config": config,
                "ground_truth": ground_truth,
                "predictions": predictions,
                "metrics": metrics,
            }
        )

    # Store aggregate results for this n_samples
    experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"][
        "all_results"
    ] = all_results

# Step 5: Visualization and analysis across different n_samples values
print("\n" + "=" * 50)
print("Generating Visualizations for Hyperparameter Tuning")
print("=" * 50)

# Plot 1: Mean metrics across different n_samples values
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
metrics_to_plot = ["change_detection_accuracy", "precision", "recall", "f1"]
titles = ["Change Detection Accuracy", "Precision", "Recall", "F1 Score"]

for idx, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
    ax = axes[idx // 2, idx % 2]

    mean_values = []
    std_values = []

    for n_samples in n_samples_values:
        values = experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"][
            "metrics"
        ][metric]
        mean_values.append(np.mean(values))
        std_values.append(np.std(values))

    ax.errorbar(
        n_samples_values,
        mean_values,
        yerr=std_values,
        marker="o",
        linewidth=2,
        capsize=5,
        markersize=8,
    )
    ax.set_xlabel("n_samples (Dataset Size)", fontsize=11)
    ax.set_ylabel(title, fontsize=11)
    ax.set_title(f"{title} vs Dataset Size", fontsize=12, fontweight="bold")
    ax.set_xscale("log")
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "n_samples_tuning_metrics.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 2: Heatmap of performance across n_samples and configs
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, (metric, title) in enumerate(zip(metrics_to_plot, titles)):
    ax = axes[idx // 2, idx % 2]

    # Create matrix: rows = n_samples, cols = configs
    matrix = []
    for n_samples in n_samples_values:
        values = experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"][
            "metrics"
        ][metric]
        matrix.append(values)

    matrix = np.array(matrix)
    im = ax.imshow(matrix, aspect="auto", cmap="viridis", vmin=0, vmax=1)

    ax.set_yticks(range(len(n_samples_values)))
    ax.set_yticklabels([str(n) for n in n_samples_values])
    ax.set_xticks(range(len(change_configs)))
    ax.set_xticklabels([f"C{i+1}" for i in range(len(change_configs))])
    ax.set_xlabel("Config", fontsize=11)
    ax.set_ylabel("n_samples", fontsize=11)
    ax.set_title(f"{title} Heatmap", fontsize=12, fontweight="bold")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(title, fontsize=10)

    # Add text annotations
    for i in range(len(n_samples_values)):
        for j in range(len(change_configs)):
            text = ax.text(
                j,
                i,
                f"{matrix[i, j]:.2f}",
                ha="center",
                va="center",
                color="white",
                fontsize=8,
            )

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "n_samples_tuning_heatmap.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 3: Change type specific performance across n_samples
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
change_types = ["additions", "deletions", "modifications", "schema_changes"]

for idx, change_type in enumerate(change_types):
    ax = axes[idx // 2, idx % 2]

    for metric_type in ["accuracy", "precision", "recall"]:
        mean_values = []
        for n_samples in n_samples_values:
            values = []
            for result in experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"][
                "all_results"
            ]:
                values.append(result["metrics"][f"{change_type}_{metric_type}"])
            mean_values.append(np.mean(values))

        ax.plot(
            n_samples_values,
            mean_values,
            marker="o",
            label=metric_type.capitalize(),
            linewidth=2,
        )

    ax.set_xlabel("n_samples (Dataset Size)", fontsize=11)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title(
        f"{change_type.capitalize()} Detection vs Dataset Size",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xscale("log")
    ax.set_ylim([0, 1.1])
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "n_samples_tuning_change_types.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 4: Summary comparison - best performing n_samples
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

mean_accuracies = []
for n_samples in n_samples_values:
    values = experiment_data["n_samples_tuning"][f"n_samples_{n_samples}"]["metrics"][
        "change_detection_accuracy"
    ]
    mean_accuracies.append(np.mean(values))

bars = ax.bar(
    range(len(n_samples_values)), mean_accuracies, color="steelblue", alpha=0.7
)
ax.set_xlabel("n_samples (Dataset Size)", fontsize=12)
ax.set_ylabel("Mean Change Detection Accuracy", fontsize=12)
ax.set_title(
    "Overall Performance Comparison Across Dataset Sizes",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(range(len(n_samples_values)))
ax.set_xticklabels([str(n) for n in n_samples_values])
ax.set_ylim([0, 1.1])

# Highlight best performer
best_idx = np.argmax(mean_accuracies)
bars[best_idx].set_color("green")
bars[best_idx].set_alpha(0.9)

# Add value labels on bars
for i, v in enumerate(mean_accuracies):
    ax.text(
        i,
        v + 0.02,
        f"{v:.4f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

ax.axhline(
    y=np.mean(mean_accuracies),
    color="r",
    linestyle="--",
    label=f"Overall Mean: {np.mean(mean_accuracies):.4f}",
)
ax.legend()
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "n_samples_tuning_summary.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Step 6: Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Save detailed results as JSON
results_summary = {
    "hyperparameter": "n_samples",
    "values_tested": n_samples_values,
    "results_by_n_samples": {},
}

for n_samples in n_samples_values:
    key = f"n_samples_{n_samples}"
    results_summary["results_by_n_samples"][n_samples] = {
        "mean_change_detection_accuracy": float(
            np.mean(
                experiment_data["n_samples_tuning"][key]["metrics"][
                    "change_detection_accuracy"
                ]
            )
        ),
        "std_change_detection_accuracy": float(
            np.std(
                experiment_data["n_samples_tuning"][key]["metrics"][
                    "change_detection_accuracy"
                ]
            )
        ),
        "mean_precision": float(
            np.mean(experiment_data["n_samples_tuning"][key]["metrics"]["precision"])
        ),
        "mean_recall": float(
            np.mean(experiment_data["n_samples_tuning"][key]["metrics"]["recall"])
        ),
        "mean_f1": float(
            np.mean(experiment_data["n_samples_tuning"][key]["metrics"]["f1"])
        ),
    }

# Find best n_samples value
best_n_samples = max(
    results_summary["results_by_n_samples"].items(),
    key=lambda x: x[1]["mean_change_detection_accuracy"],
)

results_summary["best_n_samples"] = {
    "value": int(best_n_samples[0]),
    "mean_accuracy": float(best_n_samples[1]["mean_change_detection_accuracy"]),
}

with open(os.path.join(working_dir, "results_summary.json"), "w") as f:
    json.dump(results_summary, f, indent=2)

# Final summary
print("\n" + "=" * 50)
print("FINAL RESULTS SUMMARY - HYPERPARAMETER TUNING")
print("=" * 50)
print(f"Hyperparameter Tested: n_samples (Dataset Size)")
print(f"Values Tested: {n_samples_values}")
print(f"\nPerformance by n_samples:")

for n_samples in n_samples_values:
    metrics = results_summary["results_by_n_samples"][n_samples]
    print(f"\n  n_samples = {n_samples}:")
    print(
        f"    Mean Accuracy: {metrics['mean_change_detection_accuracy']:.4f} ± {metrics['std_change_detection_accuracy']:.4f}"
    )
    print(f"    Mean Precision: {metrics['mean_precision']:.4f}")
    print(f"    Mean Recall: {metrics['mean_recall']:.4f}")
    print(f"    Mean F1 Score: {metrics['mean_f1']:.4f}")

print(f"\n{'='*50}")
print(f"BEST PERFORMING n_samples: {results_summary['best_n_samples']['value']}")
print(f"Accuracy: {results_summary['best_n_samples']['mean_accuracy']:.4f}")
print(f"{'='*50}")
print(f"\nAll results saved to: {working_dir}")
print("=" * 50)
