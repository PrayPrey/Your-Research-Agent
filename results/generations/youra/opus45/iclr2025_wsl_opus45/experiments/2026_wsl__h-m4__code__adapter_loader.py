"""AdapterLoader: Load adapter metadata and B matrices per layer type."""

import json
import os
from pathlib import Path
from typing import NamedTuple, Optional

import numpy as np
from safetensors import safe_open

import config


class AdapterRecord(NamedTuple):
    """Adapter metadata record."""
    task: str
    seed: int
    category: str
    path: str


def load_adapter_metadata(h_e1_results_dir: str) -> list[AdapterRecord]:
    """
    Load adapter_metadata.json from H-E1 results.

    Args:
        h_e1_results_dir: Path to H-E1 results directory

    Returns:
        List of 40 AdapterRecord entries sorted by (task, seed)
    """
    meta_path = os.path.join(h_e1_results_dir, "adapter_metadata.json")

    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Adapter metadata not found: {meta_path}")

    with open(meta_path, 'r') as f:
        metadata = json.load(f)

    # Validate structure
    if not isinstance(metadata, list):
        raise ValueError("adapter_metadata.json should be a list")

    # Convert to AdapterRecord
    records = []
    for entry in metadata:
        records.append(AdapterRecord(
            task=entry["task"],
            seed=entry["seed"],
            category=entry["category"],
            path=entry["adapter_path"],
        ))

    # Sort by (task, seed) for consistent ordering
    records = sorted(records, key=lambda r: (r.task, r.seed))

    return records


def validate_adapter_count(records: list[AdapterRecord], expected: int = 40) -> None:
    """Validate adapter count matches expected."""
    if len(records) != expected:
        raise ValueError(f"Expected {expected} adapters, got {len(records)}")


def load_b_matrices(
    record: AdapterRecord,
    layer_type: str,
) -> list[np.ndarray]:
    """
    Load B matrices for a specific layer type from a single adapter.

    Args:
        record: AdapterRecord with path to adapter
        layer_type: One of ALL_LAYER_TYPES (e.g., "q_proj", "up_proj")

    Returns:
        List of 22 matrices (one per transformer layer), each [dim, r]
    """
    safetensor_path = os.path.join(record.path, "adapter_model.safetensors")

    if not os.path.exists(safetensor_path):
        raise FileNotFoundError(f"Safetensors file not found: {safetensor_path}")

    matrices = []
    with safe_open(safetensor_path, framework="numpy") as f:
        keys = f.keys()

        # Filter keys matching pattern: base_model.model.model.layers.{i}.{layer_type}.lora_B.weight
        # Or simplified: *.{layer_type}.lora_B.weight
        layer_keys = sorted([
            k for k in keys
            if f".{layer_type}.lora_B.weight" in k
        ], key=lambda x: int(x.split(".layers.")[1].split(".")[0]) if ".layers." in x else 0)

        for key in layer_keys:
            tensor = f.get_tensor(key)
            # lora_B has shape [out_dim, r] where r=32
            matrices.append(tensor)

    if len(matrices) != config.N_TRANSFORMER_LAYERS:
        # Some adapters might have different layer counts; log warning
        print(f"Warning: Expected {config.N_TRANSFORMER_LAYERS} layers for {layer_type}, "
              f"got {len(matrices)} in {record.path}")

    return matrices


def load_all_b_matrices(
    records: list[AdapterRecord],
    layer_type: str,
) -> np.ndarray:
    """
    Load B matrices for all adapters for a specific layer type.

    Args:
        records: List of AdapterRecord (40 adapters)
        layer_type: One of ALL_LAYER_TYPES

    Returns:
        Array of shape [40, 22, dim, r] for the given layer type
        Note: dim varies by layer type (attention: 2048, MLP: varies)
    """
    all_matrices = []

    for i, record in enumerate(records):
        matrices = load_b_matrices(record, layer_type)
        # Stack matrices for this adapter: [22, dim, r]
        stacked = np.stack(matrices, axis=0)
        all_matrices.append(stacked)

    # Stack all adapters: [40, 22, dim, r]
    result = np.stack(all_matrices, axis=0)

    return result


def get_layer_type_keys(safetensor_path: str) -> dict[str, list[str]]:
    """
    Get all lora_B keys organized by layer type.

    Args:
        safetensor_path: Path to adapter_model.safetensors

    Returns:
        Dict mapping layer_type -> list of keys
    """
    layer_type_keys = {lt: [] for lt in config.ALL_LAYER_TYPES}

    with safe_open(safetensor_path, framework="numpy") as f:
        for key in f.keys():
            if "lora_B.weight" in key:
                for lt in config.ALL_LAYER_TYPES:
                    if f".{lt}." in key:
                        layer_type_keys[lt].append(key)
                        break

    return layer_type_keys
