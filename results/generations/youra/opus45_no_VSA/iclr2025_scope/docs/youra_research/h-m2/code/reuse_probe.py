"""H-M2 Probe Context - Reconstruct H-E1 probe + test split in-process"""
import sys
import importlib.util
from pathlib import Path
from dataclasses import dataclass

# Load H-E1 modules by absolute path to avoid ANY name conflicts
h_e1_code = Path(__file__).resolve().parent.parent.parent / "h-e1" / "code"
h_m2_code = Path(__file__).resolve().parent


def _load_module(name, filepath):
    """Load a Python module from filepath, temporarily fixing sys.path."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)

    # Clear any conflicting 'config' from sys.modules
    config_backup = sys.modules.pop("config", None)

    # Remove h-m2/code from path, add h-e1/code at front
    old_path = sys.path.copy()
    sys.path = [p for p in sys.path if str(h_m2_code) not in p]
    sys.path.insert(0, str(h_e1_code))

    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path = old_path
        if config_backup is not None:
            sys.modules["config"] = config_backup

    return mod


# Load H-E1 modules in dependency order
_e1_config = _load_module("h_e1_config_mod", h_e1_code / "config.py")
_e1_data = _load_module("h_e1_data_mod", h_e1_code / "data.py")
_e1_model = _load_module("h_e1_model_mod", h_e1_code / "model.py")

E1_CONFIG = _e1_config.CONFIG
stream_instructions = _e1_data.stream_instructions
encode_labels = _e1_data.encode_labels
stratified_split = _e1_data.stratified_split
AdapterSelectionProbe = _e1_model.AdapterSelectionProbe


@dataclass
class ProbeContext:
    probe: "AdapterSelectionProbe"
    X_test: list
    y_test: list
    task_families: list


def build_probe_context() -> ProbeContext:
    """Re-run H-E1 pipeline in-process; same seed => same split + equivalent fitted probe."""
    print("Building H-E1 probe context (same seed=42, deterministic reconstruction)...")

    samples, task_families = stream_instructions(E1_CONFIG)
    labels = encode_labels(samples, task_families)
    splits = stratified_split(samples, labels, E1_CONFIG)

    X_train, y_train = splits["train"]
    X_test, y_test = splits["test"]

    probe = AdapterSelectionProbe(
        encoder_name=E1_CONFIG.encoder_name,
        num_classes=len(task_families),
        max_iter=E1_CONFIG.max_iter,
        solver=E1_CONFIG.solver,
        random_state=E1_CONFIG.random_state,
    )
    probe.fit(X_train, y_train)

    print(f"ProbeContext ready: {len(X_test)} test samples, {len(task_families)} classes")
    return ProbeContext(probe, X_test, y_test, task_families)
