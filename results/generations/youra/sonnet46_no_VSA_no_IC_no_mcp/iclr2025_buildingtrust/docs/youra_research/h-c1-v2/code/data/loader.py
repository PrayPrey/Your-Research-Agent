"""Load HuggingFace datasets for 13B-chat new inference."""
import os
from typing import Dict
from datasets import load_dataset, Dataset


def load_hc1v2_datasets(seed: int = 1, subsample_clean: int = 1000) -> Dict[str, Dataset]:
    """
    Load datasets needed for 13B-chat inference and clean ECE baselines.
    Returns {split_key: Dataset}
    """
    datasets: Dict[str, Dataset] = {}

    print("Loading MultiNLI (clean baseline for ANLI)...")
    try:
        mnli = load_dataset("multi_nli", split="validation_matched")
    except Exception:
        mnli = load_dataset("nyu-mll/multi_nli", split="validation_matched")
    if len(mnli) > subsample_clean:
        mnli = mnli.shuffle(seed=seed).select(range(subsample_clean))
    datasets["multi_nli"] = mnli

    print("Loading ANLI R1/R2/R3...")
    for r in [1, 2, 3]:
        split = f"test_r{r}"
        try:
            ds = load_dataset("facebook/anli", split=split)
        except Exception:
            ds = load_dataset("allenai/anli", split=split)
        datasets[f"anli_r{r}"] = ds
        # Clean counterpart = MultiNLI slice
        datasets[f"anli_r{r}_clean"] = mnli

    print("Loading AdvGLUE MNLI (adversarial)...")
    try:
        adv_glue = load_dataset("adv_glue", "adv_mnli", split="validation")
        datasets["advglue_mnli"] = adv_glue
    except Exception as e:
        print(f"⚠ AdvGLUE load failed: {e} — using empty placeholder")
        datasets["advglue_mnli"] = Dataset.from_dict({"premise": [], "hypothesis": [], "label": []})

    print("Loading GLUE MNLI (clean counterpart for AdvGLUE)...")
    glue_mnli = load_dataset("glue", "mnli", split="validation_matched")
    if len(glue_mnli) > subsample_clean:
        glue_mnli = glue_mnli.shuffle(seed=seed).select(range(subsample_clean))
    datasets["glue_mnli"] = glue_mnli

    print(f"✓ Loaded {len(datasets)} dataset splits")
    return datasets
