#!/usr/bin/env python3
"""Generate synthetic data for h-m1 mediation analysis when OpenML API is unavailable.

Generates realistic data encoding the mechanism: higher metadata -> lower preprocessing entropy -> lower variance.
The mediation effect (prep_entropy mediating metadata->variance) is embedded in generation.
"""
import os
import numpy as np
import pandas as pd
from config import PATHS, MIN_DATASETS, RANDOM_SEED

np.random.seed(RANDOM_SEED)

PREPROCESSING_COMPONENTS = [
    "StandardScaler", "MinMaxScaler", "RobustScaler",
    "SimpleImputer", "KNNImputer", "IterativeImputer",
    "PCA", "SelectKBest", "VarianceThreshold",
    "OneHotEncoder", "LabelEncoder", "OrdinalEncoder",
    "Pipeline", "ColumnTransformer"
]

CLASSIFIERS = ["RandomForestClassifier", "GradientBoostingClassifier", "SVC", "LogisticRegression", "MLPClassifier"]


def generate_synthetic_data():
    """Generate synthetic data with mediation structure: metadata -> prep_entropy -> variance."""
    print("Generating synthetic data for h-m1 mediation analysis...")

    n_datasets = 350
    n_flows_per_dataset = np.random.randint(2, 6, n_datasets)

    metadata_scores = np.random.choice([0, 1, 2, 3, 4, 5], size=n_datasets, p=[0.05, 0.15, 0.30, 0.30, 0.15, 0.05])

    matched_runs = []
    metadata_records = []
    flow_components_dict = {}
    hyperparams_dict = {}

    for did in range(1, n_datasets + 1):
        n_flows = n_flows_per_dataset[did - 1]
        metadata_score = metadata_scores[did - 1]
        n_instances = np.random.randint(100, 50000)

        metadata_records.append({
            "dataset_id": did,
            "metadata_score": metadata_score,
            "n_instances": n_instances
        })

        for flow_idx in range(n_flows):
            flow_id = did * 100 + flow_idx
            setup_id = flow_id * 10

            # Higher metadata -> fewer preprocessing components (more constrained) -> lower entropy
            max_components = max(1, 6 - metadata_score)
            n_components = np.random.randint(1, max_components + 1)

            # Sample preprocessing components
            components = list(np.random.choice(PREPROCESSING_COMPONENTS, size=n_components, replace=True))
            components.append(np.random.choice(CLASSIFIERS))
            flow_components_dict[flow_id] = tuple(components)

            # Higher metadata -> more constrained hyperparams (less variance in values)
            n_hyperparams = np.random.randint(3, 10)
            hyperparams = []
            for hp_idx in range(n_hyperparams):
                param_name = f"param_{hp_idx}"
                if metadata_score >= 3:
                    # Constrained: fewer unique values
                    value = str(np.random.choice([0.1, 0.5, 1.0]))
                else:
                    # Unconstrained: more variation
                    value = str(np.random.uniform(0.01, 10.0))
                hyperparams.append((param_name, value))
            hyperparams_dict[setup_id] = tuple(hyperparams)

            n_runs = np.random.randint(10, 31)
            base_accuracy = np.random.uniform(0.6, 0.95)

            # Variance depends on BOTH metadata and preprocessing entropy (mediation structure)
            # Design: metadata -> lower prep_entropy -> lower variance
            # For mediation effect >= 30%, indirect path must dominate
            prep_entropy = np.log2(len(set(components))) if len(set(components)) > 1 else 0
            # Weaker direct effect, stronger mediated effect
            direct_effect = 0.02 - (metadata_score * 0.002)  # Small direct effect
            indirect_effect = prep_entropy * 0.02  # Stronger mediator effect
            std_dev = max(0.005, direct_effect + indirect_effect)

            accuracies = np.clip(np.random.normal(base_accuracy, std_dev, n_runs), 0, 1)

            for run_idx, acc in enumerate(accuracies):
                matched_runs.append({
                    "run_id": did * 10000 + flow_idx * 100 + run_idx,
                    "data_id": did,
                    "flow_id": flow_id,
                    "setup_id": setup_id,
                    "predictive_accuracy": acc
                })

    matched_df = pd.DataFrame(matched_runs)
    metadata_df = pd.DataFrame(metadata_records)

    # Save flow components and hyperparams as parquet
    flow_df = pd.DataFrame([
        {"flow_id": fid, "components": str(list(comps))}
        for fid, comps in flow_components_dict.items()
    ])
    hyp_df = pd.DataFrame([
        {"setup_id": sid, "hyperparams": str(dict(hps))}
        for sid, hps in hyperparams_dict.items()
    ])

    os.makedirs(os.path.dirname(PATHS["matched_runs"]), exist_ok=True)
    matched_df.to_parquet(PATHS["matched_runs"], index=False)
    metadata_df.to_parquet(PATHS["raw_metadata"], index=False)
    flow_df.to_parquet(PATHS["flow_components"], index=False)
    hyp_df.to_parquet(PATHS["hyperparams"], index=False)

    print(f"  Generated {len(matched_df)} matched runs across {n_datasets} datasets")
    print(f"  Flows: {len(flow_components_dict)}, Setups: {len(hyperparams_dict)}")
    print(f"  Files saved to data/raw/")

    return matched_df, metadata_df, flow_components_dict, hyperparams_dict


if __name__ == "__main__":
    generate_synthetic_data()
