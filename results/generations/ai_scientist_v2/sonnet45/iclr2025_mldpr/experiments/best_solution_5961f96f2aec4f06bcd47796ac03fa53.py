import os
import numpy as np
import pandas as pd
import hashlib
import json
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import matplotlib.pyplot as plt
import torch

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

# Initialize experiment data structure
experiment_data = {
    "synthetic_tabular": {
        "metrics": {"change_detection_accuracy": []},
        "detected_changes": [],
        "ground_truth_changes": [],
        "epochs": [],
    },
    "synthetic_text": {
        "metrics": {"change_detection_accuracy": []},
        "detected_changes": [],
        "ground_truth_changes": [],
        "epochs": [],
    },
    "synthetic_mixed": {
        "metrics": {"change_detection_accuracy": []},
        "detected_changes": [],
        "ground_truth_changes": [],
        "epochs": [],
    },
}


def create_hash(value):
    """Create hash for a value"""
    if pd.isna(value):
        return hashlib.md5(b"__NA__").hexdigest()
    return hashlib.md5(str(value).encode()).hexdigest()


def create_synthetic_dataset_v1(dataset_type="tabular", n_rows=100):
    """Create initial version of synthetic dataset"""
    np.random.seed(42)

    if dataset_type == "tabular":
        data = {
            "id": range(n_rows),
            "feature_1": np.random.randn(n_rows),
            "feature_2": np.random.choice(["A", "B", "C"], n_rows),
            "label": np.random.randint(0, 2, n_rows),
        }
    elif dataset_type == "text":
        data = {
            "id": range(n_rows),
            "text": [f"Sample text number {i}" for i in range(n_rows)],
            "category": np.random.choice(["cat1", "cat2", "cat3"], n_rows),
            "label": np.random.randint(0, 3, n_rows),
        }
    else:  # mixed
        data = {
            "id": range(n_rows),
            "numeric_feat": np.random.randn(n_rows),
            "text_feat": [f"Text {i}" for i in range(n_rows)],
            "categorical_feat": np.random.choice(["X", "Y", "Z"], n_rows),
            "label": np.random.randint(0, 2, n_rows),
        }

    return pd.DataFrame(data)


def create_synthetic_dataset_v2(df_v1, change_spec):
    """Create modified version of dataset with controlled changes"""
    df_v2 = df_v1.copy()
    ground_truth_changes = []

    # Row additions
    if "add_rows" in change_spec:
        n_add = change_spec["add_rows"]
        new_rows = []
        for i in range(n_add):
            new_id = df_v2["id"].max() + i + 1
            new_row = {
                col: df_v2[col].iloc[0] if col != "id" else new_id
                for col in df_v2.columns
            }
            new_rows.append(new_row)
        df_v2 = pd.concat([df_v2, pd.DataFrame(new_rows)], ignore_index=True)
        for i in range(n_add):
            ground_truth_changes.append(
                {"type": "row_addition", "row_id": df_v2.iloc[-(n_add - i)]["id"]}
            )

    # Row deletions
    if "delete_rows" in change_spec:
        indices_to_delete = change_spec["delete_rows"]
        for idx in indices_to_delete:
            if idx < len(df_v2):
                ground_truth_changes.append(
                    {"type": "row_deletion", "row_id": df_v2.iloc[idx]["id"]}
                )
        df_v2 = df_v2.drop(df_v2.index[indices_to_delete]).reset_index(drop=True)

    # Cell modifications
    if "modify_cells" in change_spec:
        for row_idx, col_name, new_value in change_spec["modify_cells"]:
            if row_idx < len(df_v2):
                old_value = df_v2.loc[row_idx, col_name]
                df_v2.loc[row_idx, col_name] = new_value
                ground_truth_changes.append(
                    {
                        "type": "cell_modification",
                        "row_id": df_v2.loc[row_idx, "id"],
                        "column": col_name,
                        "old_value": old_value,
                        "new_value": new_value,
                    }
                )

    # Schema changes (column additions)
    if "add_columns" in change_spec:
        for col_name in change_spec["add_columns"]:
            df_v2[col_name] = np.random.randn(len(df_v2))
            ground_truth_changes.append(
                {
                    "type": "schema_change",
                    "change": "column_addition",
                    "column": col_name,
                }
            )

    # Schema changes (column deletions)
    if "delete_columns" in change_spec:
        for col_name in change_spec["delete_columns"]:
            if col_name in df_v2.columns:
                df_v2 = df_v2.drop(columns=[col_name])
                ground_truth_changes.append(
                    {
                        "type": "schema_change",
                        "change": "column_deletion",
                        "column": col_name,
                    }
                )

    return df_v2, ground_truth_changes


class DatasetChangeDetector:
    """Automated dataset change detection system"""

    def __init__(self):
        self.detected_changes = []

    def detect_changes(self, df_v1, df_v2):
        """Detect all changes between two dataset versions"""
        self.detected_changes = []

        # Detect schema changes
        self._detect_schema_changes(df_v1, df_v2)

        # Detect row-level changes
        self._detect_row_changes(df_v1, df_v2)

        return self.detected_changes

    def _detect_schema_changes(self, df_v1, df_v2):
        """Detect column additions and deletions"""
        cols_v1 = set(df_v1.columns)
        cols_v2 = set(df_v2.columns)

        # Column additions
        added_cols = cols_v2 - cols_v1
        for col in added_cols:
            self.detected_changes.append(
                {"type": "schema_change", "change": "column_addition", "column": col}
            )

        # Column deletions
        deleted_cols = cols_v1 - cols_v2
        for col in deleted_cols:
            self.detected_changes.append(
                {"type": "schema_change", "change": "column_deletion", "column": col}
            )

    def _detect_row_changes(self, df_v1, df_v2):
        """Detect row additions, deletions, and modifications"""
        # Use 'id' column as key
        if "id" not in df_v1.columns or "id" not in df_v2.columns:
            return

        ids_v1 = set(df_v1["id"].values)
        ids_v2 = set(df_v2["id"].values)

        # Row additions
        added_ids = ids_v2 - ids_v1
        for row_id in added_ids:
            self.detected_changes.append({"type": "row_addition", "row_id": row_id})

        # Row deletions
        deleted_ids = ids_v1 - ids_v2
        for row_id in deleted_ids:
            self.detected_changes.append({"type": "row_deletion", "row_id": row_id})

        # Cell modifications (for common rows and columns)
        common_ids = ids_v1 & ids_v2
        common_cols = set(df_v1.columns) & set(df_v2.columns)
        common_cols.discard("id")

        for row_id in common_ids:
            row_v1 = df_v1[df_v1["id"] == row_id].iloc[0]
            row_v2 = df_v2[df_v2["id"] == row_id].iloc[0]

            for col in common_cols:
                val_v1 = row_v1[col]
                val_v2 = row_v2[col]

                # Handle NaN comparison
                if pd.isna(val_v1) and pd.isna(val_v2):
                    continue

                if pd.isna(val_v1) or pd.isna(val_v2) or val_v1 != val_v2:
                    self.detected_changes.append(
                        {
                            "type": "cell_modification",
                            "row_id": row_id,
                            "column": col,
                            "old_value": val_v1,
                            "new_value": val_v2,
                        }
                    )


def normalize_change(change):
    """Normalize change representation for comparison"""
    change_copy = change.copy()
    # Remove values for cell modifications in comparison
    if change_copy["type"] == "cell_modification":
        return (change_copy["type"], change_copy["row_id"], change_copy["column"])
    elif change_copy["type"] == "schema_change":
        return (change_copy["type"], change_copy["change"], change_copy["column"])
    elif change_copy["type"] in ["row_addition", "row_deletion"]:
        return (change_copy["type"], change_copy["row_id"])
    return tuple(sorted(change_copy.items()))


def calculate_change_detection_accuracy(detected_changes, ground_truth_changes):
    """Calculate accuracy of change detection"""
    if len(ground_truth_changes) == 0:
        return 1.0 if len(detected_changes) == 0 else 0.0

    # Normalize changes for comparison
    detected_normalized = set([normalize_change(c) for c in detected_changes])
    ground_truth_normalized = set([normalize_change(c) for c in ground_truth_changes])

    # Calculate true positives
    true_positives = len(detected_normalized & ground_truth_normalized)

    # Accuracy = TP / Total ground truth changes
    accuracy = true_positives / len(ground_truth_changes)

    return accuracy


def generate_change_report(detected_changes):
    """Generate human-readable change report"""
    report = {
        "total_changes": len(detected_changes),
        "by_type": defaultdict(int),
        "details": detected_changes,
    }

    for change in detected_changes:
        report["by_type"][change["type"]] += 1

    return report


# Run experiments on different dataset types
print("=" * 60)
print("Starting Dataset Change Detection Experiments")
print("=" * 60)

dataset_configs = [
    (
        "synthetic_tabular",
        "tabular",
        {
            "add_rows": 5,
            "delete_rows": [2, 5, 8],
            "modify_cells": [
                (10, "feature_1", 999.9),
                (15, "feature_2", "D"),
                (20, "label", 1),
            ],
            "add_columns": ["new_feature"],
        },
    ),
    (
        "synthetic_text",
        "text",
        {
            "add_rows": 3,
            "delete_rows": [1, 4],
            "modify_cells": [(5, "text", "Modified text"), (10, "category", "cat4")],
            "delete_columns": ["category"],
        },
    ),
    (
        "synthetic_mixed",
        "mixed",
        {
            "add_rows": 4,
            "delete_rows": [3, 7, 11],
            "modify_cells": [
                (8, "numeric_feat", -5.5),
                (12, "text_feat", "Changed"),
                (18, "categorical_feat", "W"),
            ],
            "add_columns": ["extra_col_1", "extra_col_2"],
        },
    ),
]

detector = DatasetChangeDetector()
all_results = []

for dataset_name, dataset_type, change_spec in dataset_configs:
    print(f"\n{'=' * 60}")
    print(f"Experiment: {dataset_name}")
    print(f"{'=' * 60}")

    # Create datasets
    df_v1 = create_synthetic_dataset_v1(dataset_type, n_rows=100)
    df_v2, ground_truth_changes = create_synthetic_dataset_v2(df_v1, change_spec)

    print(f"Dataset V1 shape: {df_v1.shape}")
    print(f"Dataset V2 shape: {df_v2.shape}")
    print(f"Ground truth changes: {len(ground_truth_changes)}")

    # Detect changes
    detected_changes = detector.detect_changes(df_v1, df_v2)
    print(f"Detected changes: {len(detected_changes)}")

    # Calculate accuracy
    accuracy = calculate_change_detection_accuracy(
        detected_changes, ground_truth_changes
    )
    print(f"Change Detection Accuracy: {accuracy:.4f}")

    # Generate report
    report = generate_change_report(detected_changes)
    print(f"\nChange Report Summary:")
    for change_type, count in report["by_type"].items():
        print(f"  {change_type}: {count}")

    # Store results
    experiment_data[dataset_name]["metrics"]["change_detection_accuracy"].append(
        accuracy
    )
    experiment_data[dataset_name]["detected_changes"] = detected_changes
    experiment_data[dataset_name]["ground_truth_changes"] = ground_truth_changes
    experiment_data[dataset_name]["epochs"].append(0)

    all_results.append(
        {
            "dataset": dataset_name,
            "accuracy": accuracy,
            "detected": len(detected_changes),
            "ground_truth": len(ground_truth_changes),
        }
    )

# Visualization
print(f"\n{'=' * 60}")
print("Generating Visualizations")
print(f"{'=' * 60}")

# Plot 1: Change Detection Accuracy by Dataset
fig, ax = plt.subplots(figsize=(10, 6))
datasets = [r["dataset"] for r in all_results]
accuracies = [r["accuracy"] for r in all_results]
colors = ["#3498db", "#e74c3c", "#2ecc71"]

bars = ax.bar(datasets, accuracies, color=colors, alpha=0.7)
ax.set_ylabel("Change Detection Accuracy", fontsize=12)
ax.set_xlabel("Dataset Type", fontsize=12)
ax.set_title(
    "Change Detection Accuracy Across Dataset Types", fontsize=14, fontweight="bold"
)
ax.set_ylim([0, 1.1])
ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="Perfect Detection")
ax.grid(axis="y", alpha=0.3)

for bar, acc in zip(bars, accuracies):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 0.02,
        f"{acc:.2f}",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "change_detection_accuracy.png"), dpi=300)
plt.close()

# Plot 2: Change Type Distribution
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, (dataset_name, _, _) in enumerate(dataset_configs):
    detected = experiment_data[dataset_name]["detected_changes"]
    change_types = defaultdict(int)
    for change in detected:
        change_types[change["type"]] += 1

    if change_types:
        axes[idx].bar(
            change_types.keys(), change_types.values(), color=colors[idx], alpha=0.7
        )
        axes[idx].set_title(f"{dataset_name}", fontsize=12, fontweight="bold")
        axes[idx].set_ylabel("Count", fontsize=10)
        axes[idx].tick_params(axis="x", rotation=45)
        axes[idx].grid(axis="y", alpha=0.3)

plt.suptitle("Distribution of Detected Change Types", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "change_type_distribution.png"), dpi=300)
plt.close()

# Plot 3: Detection Performance Comparison
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(datasets))
width = 0.35

detected_counts = [r["detected"] for r in all_results]
ground_truth_counts = [r["ground_truth"] for r in all_results]

bars1 = ax.bar(
    x - width / 2,
    ground_truth_counts,
    width,
    label="Ground Truth",
    color="#34495e",
    alpha=0.7,
)
bars2 = ax.bar(
    x + width / 2, detected_counts, width, label="Detected", color="#e67e22", alpha=0.7
)

ax.set_ylabel("Number of Changes", fontsize=12)
ax.set_xlabel("Dataset Type", fontsize=12)
ax.set_title("Ground Truth vs Detected Changes", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(datasets)
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "detection_comparison.png"), dpi=300)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Save detailed results as JSON
results_summary = {
    "overall_metrics": {
        "mean_accuracy": np.mean(accuracies),
        "std_accuracy": np.std(accuracies),
        "min_accuracy": np.min(accuracies),
        "max_accuracy": np.max(accuracies),
    },
    "per_dataset_results": all_results,
}

with open(os.path.join(working_dir, "results_summary.json"), "w") as f:
    json.dump(results_summary, f, indent=2)

# Print final summary
print(f"\n{'=' * 60}")
print("FINAL RESULTS SUMMARY")
print(f"{'=' * 60}")
print(
    f"Mean Change Detection Accuracy: {results_summary['overall_metrics']['mean_accuracy']:.4f}"
)
print(
    f"Std Change Detection Accuracy: {results_summary['overall_metrics']['std_accuracy']:.4f}"
)
print(
    f"Min Change Detection Accuracy: {results_summary['overall_metrics']['min_accuracy']:.4f}"
)
print(
    f"Max Change Detection Accuracy: {results_summary['overall_metrics']['max_accuracy']:.4f}"
)
print(f"\nAll results saved to: {working_dir}")
print(f"{'=' * 60}")
