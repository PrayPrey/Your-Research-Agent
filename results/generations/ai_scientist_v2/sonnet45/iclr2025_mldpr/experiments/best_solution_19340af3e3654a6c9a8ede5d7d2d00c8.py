import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import json

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

# Initialize experiment data tracking
experiment_data = {
    "column_selection_strategy": {
        "synthetic_dataset": {
            "metrics": {},
            "ground_truth": {},
            "predictions": {},
            "timestamps": {},
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


def select_columns_to_modify(df, strategy, exclude_cols=["id", "target"]):
    """Select columns to modify based on strategy"""
    available_cols = [col for col in df.columns if col not in exclude_cols]
    numeric_cols = [
        col for col in available_cols if df[col].dtype in [np.float64, np.int64]
    ]
    categorical_cols = [col for col in available_cols if df[col].dtype == object]

    if strategy == "fixed_two":
        # Original strategy: fixed two columns
        return (
            ["feature_1", "feature_2"]
            if "feature_1" in available_cols
            else available_cols[:2]
        )
    elif strategy == "all_columns":
        return available_cols
    elif strategy == "random_subset_50":
        n_select = max(1, len(available_cols) // 2)
        return list(np.random.choice(available_cols, n_select, replace=False))
    elif strategy == "random_subset_25":
        n_select = max(1, len(available_cols) // 4)
        return list(np.random.choice(available_cols, n_select, replace=False))
    elif strategy == "numeric_only":
        return numeric_cols if numeric_cols else available_cols
    elif strategy == "categorical_only":
        return categorical_cols if categorical_cols else available_cols
    elif strategy == "weighted_numeric":
        # 80% probability for numeric, 20% for categorical
        selected = []
        for col in available_cols:
            if col in numeric_cols:
                if np.random.rand() < 0.8:
                    selected.append(col)
            else:
                if np.random.rand() < 0.2:
                    selected.append(col)
        return selected if selected else available_cols[:1]
    elif strategy == "single_random":
        return [np.random.choice(available_cols)]
    else:
        return available_cols


def introduce_changes(df_base, change_config, column_selection_strategy):
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

    # 3. Modify existing rows with column selection strategy
    n_modifications = change_config["n_modifications"]
    if n_modifications > 0:
        valid_ids = set(df_base["id"]) - set(ground_truth_changes["deletions"])
        modify_ids = np.random.choice(
            list(valid_ids), min(n_modifications, len(valid_ids)), replace=False
        )

        for mod_id in modify_ids:
            idx = df_v2[df_v2["id"] == mod_id].index[0]
            cols_to_modify = select_columns_to_modify(df_v2, column_selection_strategy)

            for col in cols_to_modify:
                if df_v2[col].dtype in [np.float64]:
                    df_v2.loc[idx, col] = np.random.randn()
                elif df_v2[col].dtype in [np.int64]:
                    df_v2.loc[idx, col] = np.random.randint(0, 100)
                elif df_v2[col].dtype == object:
                    unique_vals = df_v2[col].dropna().unique()
                    if len(unique_vals) > 0:
                        df_v2.loc[idx, col] = np.random.choice(unique_vals)

        ground_truth_changes["modifications"] = modify_ids.tolist()

    # 4. Schema changes
    if change_config["add_column"]:
        df_v2["feature_new"] = np.random.randn(len(df_v2))
        ground_truth_changes["schema_changes"].append("added_column_feature_new")

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


# Step 4: Hyperparameter tuning - Column selection strategies
print("=" * 70)
print("HYPERPARAMETER TUNING: Column Selection Strategy")
print("=" * 70)

column_selection_strategies = [
    "fixed_two",
    "all_columns",
    "random_subset_50",
    "random_subset_25",
    "numeric_only",
    "categorical_only",
    "weighted_numeric",
    "single_random",
]

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

for strategy in column_selection_strategies:
    print(f"\n{'='*70}")
    print(f"Testing Column Selection Strategy: {strategy}")
    print(f"{'='*70}")

    strategy_results = []
    experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
        strategy
    ] = {
        "change_detection_accuracy": [],
        "precision": [],
        "recall": [],
        "f1": [],
        "modifications_precision": [],
        "modifications_recall": [],
        "modifications_f1": [],
    }

    for idx, config in enumerate(change_configs):
        print(f"\n  Experiment {idx+1}/{len(change_configs)}: {config['name']}")

        # Create datasets
        df_v1 = create_base_dataset(n_samples=1000)
        df_v2, ground_truth = introduce_changes(df_v1, config, strategy)

        # Detect changes
        detector = DatasetChangeDetector()
        predictions = detector.detect_changes(df_v1, df_v2)

        # Evaluate
        metrics = evaluate_change_detection(ground_truth, predictions)

        print(
            f"    GT Modifications: {len(ground_truth['modifications'])}, "
            f"Detected: {len(predictions['modifications'])}"
        )
        print(
            f"    Overall Accuracy: {metrics['overall_change_detection_accuracy']:.4f}"
        )
        print(f"    Modifications F1: {metrics['modifications_f1']:.4f}")

        # Store results
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
        ]["change_detection_accuracy"].append(
            metrics["overall_change_detection_accuracy"]
        )
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
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
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
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
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
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
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
        ]["modifications_precision"].append(metrics["modifications_precision"])
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
        ]["modifications_recall"].append(metrics["modifications_recall"])
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][
            strategy
        ]["modifications_f1"].append(metrics["modifications_f1"])

        strategy_results.append(
            {
                "config": config,
                "ground_truth": ground_truth,
                "predictions": predictions,
                "metrics": metrics,
            }
        )

    all_results[strategy] = strategy_results

    # Store ground truth and predictions
    experiment_data["column_selection_strategy"]["synthetic_dataset"]["ground_truth"][
        strategy
    ] = [r["ground_truth"] for r in strategy_results]
    experiment_data["column_selection_strategy"]["synthetic_dataset"]["predictions"][
        strategy
    ] = [r["predictions"] for r in strategy_results]
    experiment_data["column_selection_strategy"]["synthetic_dataset"]["timestamps"][
        strategy
    ] = datetime.now().isoformat()

# Step 5: Analysis and Visualization
print("\n" + "=" * 70)
print("ANALYSIS: Comparing Column Selection Strategies")
print("=" * 70)

# Calculate summary statistics for each strategy
summary_stats = {}
for strategy in column_selection_strategies:
    metrics = experiment_data["column_selection_strategy"]["synthetic_dataset"][
        "metrics"
    ][strategy]
    summary_stats[strategy] = {
        "mean_accuracy": np.mean(metrics["change_detection_accuracy"]),
        "std_accuracy": np.std(metrics["change_detection_accuracy"]),
        "mean_f1": np.mean(metrics["f1"]),
        "mean_modifications_f1": np.mean(metrics["modifications_f1"]),
    }
    print(f"\n{strategy}:")
    print(
        f"  Mean Accuracy: {summary_stats[strategy]['mean_accuracy']:.4f} ± {summary_stats[strategy]['std_accuracy']:.4f}"
    )
    print(f"  Mean F1 Score: {summary_stats[strategy]['mean_f1']:.4f}")
    print(
        f"  Mean Modifications F1: {summary_stats[strategy]['mean_modifications_f1']:.4f}"
    )

# Find best strategy
best_strategy = max(summary_stats.items(), key=lambda x: x[1]["mean_accuracy"])
print(f"\n{'='*70}")
print(
    f"BEST STRATEGY: {best_strategy[0]} with mean accuracy {best_strategy[1]['mean_accuracy']:.4f}"
)
print(f"{'='*70}")

# Step 6: Visualizations
print("\nGenerating visualizations...")

# Plot 1: Overall accuracy comparison across strategies
fig, ax = plt.subplots(1, 1, figsize=(14, 6))
x_pos = np.arange(len(column_selection_strategies))
accuracies = [summary_stats[s]["mean_accuracy"] for s in column_selection_strategies]
stds = [summary_stats[s]["std_accuracy"] for s in column_selection_strategies]

bars = ax.bar(x_pos, accuracies, yerr=stds, capsize=5, alpha=0.7, color="steelblue")
ax.set_xlabel("Column Selection Strategy", fontsize=12)
ax.set_ylabel("Mean Change Detection Accuracy", fontsize=12)
ax.set_title(
    "Hyperparameter Tuning: Column Selection Strategy Performance",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(x_pos)
ax.set_xticklabels(column_selection_strategies, rotation=45, ha="right")
ax.set_ylim([0, 1.1])
ax.axhline(
    y=np.mean(accuracies),
    color="r",
    linestyle="--",
    linewidth=2,
    label=f"Overall Mean: {np.mean(accuracies):.3f}",
)
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "column_strategy_comparison.png"),
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
    for strategy in column_selection_strategies:
        if metric_name == "change_detection_accuracy":
            row = experiment_data["column_selection_strategy"]["synthetic_dataset"][
                "metrics"
            ][strategy][metric_name]
        else:
            row = experiment_data["column_selection_strategy"]["synthetic_dataset"][
                "metrics"
            ][strategy][metric_name]
        data_matrix.append(row)

    data_matrix = np.array(data_matrix)
    im = ax.imshow(data_matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(change_configs)))
    ax.set_yticks(np.arange(len(column_selection_strategies)))
    ax.set_xticklabels([c["name"] for c in change_configs])
    ax.set_yticklabels(column_selection_strategies)
    ax.set_xlabel("Experiment Config", fontsize=10)
    ax.set_ylabel("Strategy", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")

    # Add text annotations
    for i in range(len(column_selection_strategies)):
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
    os.path.join(working_dir, "column_strategy_heatmap.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 3: Modifications detection performance
fig, ax = plt.subplots(1, 1, figsize=(14, 6))
x_pos = np.arange(len(column_selection_strategies))
width = 0.25

modifications_precision = [
    np.mean(
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][s][
            "modifications_precision"
        ]
    )
    for s in column_selection_strategies
]
modifications_recall = [
    np.mean(
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][s][
            "modifications_recall"
        ]
    )
    for s in column_selection_strategies
]
modifications_f1 = [
    np.mean(
        experiment_data["column_selection_strategy"]["synthetic_dataset"]["metrics"][s][
            "modifications_f1"
        ]
    )
    for s in column_selection_strategies
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

ax.set_xlabel("Column Selection Strategy", fontsize=12)
ax.set_ylabel("Score", fontsize=12)
ax.set_title(
    "Modifications Detection Performance by Strategy", fontsize=14, fontweight="bold"
)
ax.set_xticks(x_pos)
ax.set_xticklabels(column_selection_strategies, rotation=45, ha="right")
ax.set_ylim([0, 1.1])
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "modifications_detection_performance.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Plot 4: Strategy performance across experiments
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
for strategy in column_selection_strategies:
    accuracies = experiment_data["column_selection_strategy"]["synthetic_dataset"][
        "metrics"
    ][strategy]["change_detection_accuracy"]
    ax.plot(
        range(len(accuracies)),
        accuracies,
        marker="o",
        linewidth=2,
        label=strategy,
        alpha=0.7,
    )

ax.set_xlabel("Experiment Index", fontsize=12)
ax.set_ylabel("Change Detection Accuracy", fontsize=12)
ax.set_title(
    "Strategy Performance Across Different Change Configurations",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(range(len(change_configs)))
ax.set_xticklabels([c["name"] for c in change_configs])
ax.set_ylim([0, 1.1])
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "strategy_performance_across_experiments.png"),
    dpi=300,
    bbox_inches="tight",
)
plt.close()

# Step 7: Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Save detailed results as JSON
results_summary = {
    "hyperparameter": "column_selection_strategy",
    "strategies_tested": column_selection_strategies,
    "num_experiments_per_strategy": len(change_configs),
    "best_strategy": best_strategy[0],
    "best_strategy_accuracy": float(best_strategy[1]["mean_accuracy"]),
    "summary_statistics": {
        strategy: {
            "mean_accuracy": float(summary_stats[strategy]["mean_accuracy"]),
            "std_accuracy": float(summary_stats[strategy]["std_accuracy"]),
            "mean_f1": float(summary_stats[strategy]["mean_f1"]),
            "mean_modifications_f1": float(
                summary_stats[strategy]["mean_modifications_f1"]
            ),
        }
        for strategy in column_selection_strategies
    },
}

with open(os.path.join(working_dir, "hyperparameter_tuning_results.json"), "w") as f:
    json.dump(results_summary, f, indent=2)

# Final summary
print("\n" + "=" * 70)
print("HYPERPARAMETER TUNING COMPLETE")
print("=" * 70)
print(f"Total Strategies Tested: {len(column_selection_strategies)}")
print(f"Experiments per Strategy: {len(change_configs)}")
print(
    f"Total Experiments Conducted: {len(column_selection_strategies) * len(change_configs)}"
)
print(f"\nBest Strategy: {best_strategy[0]}")
print(
    f"Best Mean Accuracy: {best_strategy[1]['mean_accuracy']:.4f} ± {best_strategy[1]['std_accuracy']:.4f}"
)
print(f"Best Mean F1 Score: {best_strategy[1]['mean_f1']:.4f}")
print(f"Best Mean Modifications F1: {best_strategy[1]['mean_modifications_f1']:.4f}")
print(f"\nAll results saved to: {working_dir}")
print("=" * 70)
