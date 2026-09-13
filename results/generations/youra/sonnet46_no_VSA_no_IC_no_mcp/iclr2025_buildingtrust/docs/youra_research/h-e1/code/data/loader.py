import json
import os
from datasets import load_dataset


TASK_LABEL_FIELD = {
    "qqp": "label",
    "sst2": "label",
    "nli": "label",
    "anli": "label",
}


def load_all_datasets(seed: int = 1, subsample_clean: int = 500, subsample_adv: int = 500):
    datasets = {}

    # AdvGLUE (adversarial)
    print("Loading AdvGLUE...")
    try:
        adv = load_dataset("adv_glue", "adv_qqp", split="validation")
        datasets["advglue_qqp"] = adv.shuffle(seed=seed).select(range(min(subsample_adv, len(adv))))
    except Exception as e:
        print(f"  advglue_qqp failed: {e}")
        datasets["advglue_qqp"] = None

    try:
        adv = load_dataset("adv_glue", "adv_sst2", split="validation")
        datasets["advglue_sst2"] = adv.shuffle(seed=seed).select(range(min(subsample_adv, len(adv))))
    except Exception as e:
        print(f"  advglue_sst2 failed: {e}")
        datasets["advglue_sst2"] = None

    try:
        adv = load_dataset("adv_glue", "adv_mnli", split="validation")
        datasets["advglue_mnli"] = adv.shuffle(seed=seed).select(range(min(subsample_adv, len(adv))))
    except Exception as e:
        print(f"  advglue_mnli failed: {e}")
        datasets["advglue_mnli"] = None

    # ANLI
    print("Loading ANLI...")
    for r in [1, 2, 3]:
        try:
            ds = load_dataset("anli", split=f"test_r{r}")
            datasets[f"anli_r{r}"] = ds.shuffle(seed=seed).select(range(min(subsample_adv, len(ds))))
        except Exception as e:
            print(f"  anli_r{r} failed: {e}")
            datasets[f"anli_r{r}"] = None

    # Clean GLUE
    print("Loading GLUE (clean)...")
    try:
        ds = load_dataset("glue", "qqp", split="validation")
        datasets["glue_qqp"] = ds.shuffle(seed=seed).select(range(min(subsample_clean, len(ds))))
    except Exception as e:
        print(f"  glue_qqp failed: {e}")
        datasets["glue_qqp"] = None

    try:
        ds = load_dataset("glue", "sst2", split="validation")
        datasets["glue_sst2"] = ds.shuffle(seed=seed).select(range(min(subsample_clean, len(ds))))
    except Exception as e:
        print(f"  glue_sst2 failed: {e}")
        datasets["glue_sst2"] = None

    # Clean MultiNLI (via GLUE)
    try:
        ds = load_dataset("glue", "mnli", split="validation_matched")
        datasets["mnli"] = ds.shuffle(seed=seed).select(range(min(subsample_clean, len(ds))))
        print(f"  mnli loaded via glue/mnli: {len(datasets['mnli'])} examples")
    except Exception as e:
        print(f"  mnli failed: {e}")
        datasets["mnli"] = None

    return datasets


def save_manifest(datasets, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    manifest = {k: len(v) if v is not None else 0 for k, v in datasets.items()}
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest saved: {manifest}")
