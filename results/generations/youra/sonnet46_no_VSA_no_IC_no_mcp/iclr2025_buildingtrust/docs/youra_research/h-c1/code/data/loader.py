"""H-C1 data loader: extends H-E1 load_all_datasets with multi_nli key."""
import sys, os, importlib.util

_HE1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../h-e1/code"))

def _import_he1_loader():
    spec = importlib.util.spec_from_file_location(
        "he1_data_loader", os.path.join(_HE1_CODE, "data", "loader.py")
    )
    mod = importlib.util.module_from_spec(spec)
    # data.formatter must be importable for h-e1 loader's own imports
    if _HE1_CODE not in sys.path:
        sys.path.append(_HE1_CODE)  # append so h-c1 code stays at front
    spec.loader.exec_module(mod)
    return mod.load_all_datasets

_he1_load_all = _import_he1_loader()

from datasets import load_dataset


def load_hc1_datasets(seed: int = 1,
                      subsample_clean: int = 1000,
                      subsample_adv: int = 1000) -> dict:
    """Load all H-E1 datasets plus multi_nli (MultiNLI validation_matched)."""
    datasets = _he1_load_all(seed=seed,
                              subsample_clean=subsample_clean,
                              subsample_adv=subsample_adv)

    # Add multi_nli (separate from glue/mnli — using MultiNLI directly)
    print("Loading MultiNLI (multi_nli)...")
    try:
        ds = load_dataset("multi_nli", split="validation_matched")
        datasets["multi_nli"] = ds.shuffle(seed=seed).select(
            range(min(subsample_clean, len(ds)))
        )
        print(f"  multi_nli loaded: {len(datasets['multi_nli'])} examples")
    except Exception as e:
        print(f"  multi_nli failed: {e}; falling back to glue/mnli")
        # Fallback: reuse glue mnli under multi_nli key
        datasets["multi_nli"] = datasets.get("mnli")

    return datasets
