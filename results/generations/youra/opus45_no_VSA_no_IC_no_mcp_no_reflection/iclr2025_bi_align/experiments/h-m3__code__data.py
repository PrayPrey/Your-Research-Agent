"""H-M1 Data Pipeline: UltraFeedback + IFEval loading."""
import random
from datasets import load_dataset


def load_ultrafeedback(split: str = "train", max_samples: int = None):
    """Load UltraFeedback dataset."""
    ds = load_dataset("openbmb/UltraFeedback", split=split, trust_remote_code=True)
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))
    return ds


def load_ifeval_split(train_ratio: float = 0.7, seed: int = 42):
    """Load IFEval with train/test split."""
    ds = load_dataset("google/IFEval", split="train")
    ds = ds.shuffle(seed=seed)

    split_idx = int(len(ds) * train_ratio)
    train_ds = ds.select(range(split_idx))
    test_ds = ds.select(range(split_idx, len(ds)))

    return train_ds, test_ds


def build_constraints(ifeval_row: dict) -> list[dict]:
    """Parse IFEval row into H-E1 constraint format."""
    constraints = []

    instruction_ids = ifeval_row.get("instruction_id_list", [])
    kwargs_list = ifeval_row.get("kwargs", [])

    if not instruction_ids:
        return constraints

    for i, inst_id in enumerate(instruction_ids):
        kw = kwargs_list[i] if i < len(kwargs_list) else {}

        if "keywords" in inst_id.lower():
            constraints.append({
                "type": "keyword",
                "keywords": kw.get("keywords", []),
                "must_include": "include" in inst_id.lower()
            })
        elif "length" in inst_id.lower() or "word" in inst_id.lower():
            target = kw.get("num_words") or kw.get("num_sentences") or kw.get("min_num_words") or kw.get("max_num_words") or 100
            op = "at_least" if "least" in inst_id.lower() else "at_most" if "most" in inst_id.lower() else "exactly"
            unit = "sentences" if "sentence" in inst_id.lower() else "words"
            constraints.append({
                "type": "length",
                "target": int(target) if target else 100,
                "op": op,
                "unit": unit
            })
        elif "format" in inst_id.lower():
            subtype = "json" if "json" in inst_id.lower() else "bullet" if "bullet" in inst_id.lower() else ""
            constraints.append({"type": "format", "subtype": subtype})
        elif "case" in inst_id.lower():
            case_type = "capital" if "capital" in inst_id.lower() or "upper" in inst_id.lower() else "lowercase"
            constraints.append({"type": "case", "case_type": case_type})
        else:
            constraints.append({"type": "unknown"})

    return constraints if constraints else [{"type": "unknown"}]


def sample_ppo_batch(
    ultrafeedback_ds,
    ifeval_ds,
    batch_size: int,
    ifeval_ratio: float = 0.3,
    seed: int = None
):
    """Sample mixed batch for PPO training."""
    if seed is not None:
        random.seed(seed)

    n_ifeval = max(1, int(batch_size * ifeval_ratio))
    n_uf = batch_size - n_ifeval

    prompts = []
    constraints = []

    # IFEval samples
    ifeval_indices = random.sample(range(len(ifeval_ds)), min(n_ifeval, len(ifeval_ds)))
    for idx in ifeval_indices:
        row = ifeval_ds[idx]
        prompts.append(row["prompt"])
        constraints.append(build_constraints(row))

    # UltraFeedback samples (no constraints)
    uf_indices = random.sample(range(len(ultrafeedback_ds)), min(n_uf, len(ultrafeedback_ds)))
    for idx in uf_indices:
        row = ultrafeedback_ds[idx]
        # UltraFeedback structure: instruction field
        prompt = row.get("instruction", row.get("prompt", str(row)))
        prompts.append(prompt)
        constraints.append([])  # empty constraints for non-IFEval

    return prompts, constraints
