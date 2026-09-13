"""A-3: Stratified Sampler — reservoir sample by Pile subset proportions."""
import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from config import PILE_HF_ID, PILE_DEDUP_HF_ID, SAMPLE_SIZE, RANDOM_SEED, CHECKPOINT_DIR


@dataclass
class DocWithMeta:
    text: str
    doc_id: str
    pile_subset: str
    is_removed: bool


def compute_subset_proportions(removed_hashes: dict[str, str]) -> dict[str, float]:
    """Compute fraction of removed docs from each Pile subset."""
    counts = Counter(removed_hashes.values())
    total = sum(counts.values())
    return {subset: count / total for subset, count in counts.items()}


def reservoir_sample_stratified(
    hf_id: str,
    target_hashes: set[str],
    proportions: dict[str, float],
    n: int = SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
    is_removed: bool = True,
    checkpoint_path: Optional[Path] = None,
) -> list[DocWithMeta]:
    """Reservoir sample n docs, stratified by Pile subset proportions."""
    from datasets import load_dataset

    rng = random.Random(seed)
    subset_caps = {s: max(1, round(p * n)) for s, p in proportions.items()}
    reservoirs: dict[str, list[DocWithMeta]] = {s: [] for s in proportions}
    counts: dict[str, int] = {s: 0 for s in proportions}

    ds = load_dataset(hf_id, split="train", streaming=True)
    docs_seen = 0
    for doc in ds:
        text = doc["text"]
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        subset = doc.get("meta", {}).get("pile_set_name", "unknown")

        if subset not in subset_caps:
            continue
        if is_removed and h not in target_hashes:
            continue
        if not is_removed and h in target_hashes:
            continue

        counts[subset] += 1
        k = counts[subset]
        cap = subset_caps[subset]
        item = DocWithMeta(text=text, doc_id=h, pile_subset=subset, is_removed=is_removed)

        if len(reservoirs[subset]) < cap:
            reservoirs[subset].append(item)
        else:
            j = rng.randint(0, k - 1)
            if j < cap:
                reservoirs[subset][j] = item

        docs_seen += 1
        if docs_seen % 500_000 == 0:
            total_sampled = sum(len(v) for v in reservoirs.values())
            print(f"  Streaming {hf_id}: {docs_seen:,} docs seen, {total_sampled:,} sampled")

        # Early exit: all subsets at ≥20× their cap (enough for reservoir stability)
        if all(counts[s] >= subset_caps[s] * 20 for s in subset_caps):
            break

    result = [doc for res in reservoirs.values() for doc in res]
    return result


def _docs_to_json(docs: list[DocWithMeta]) -> list[dict]:
    return [asdict(d) for d in docs]


def _docs_from_json(data: list[dict]) -> list[DocWithMeta]:
    return [DocWithMeta(**d) for d in data]


def stratified_reservoir_sample(
    removed_hashes: dict[str, str],
    pile_stream_id: str = PILE_HF_ID,
    dedup_stream_id: str = PILE_DEDUP_HF_ID,
    sample_size: int = SAMPLE_SIZE,
    seed: int = RANDOM_SEED,
    checkpoint_path: Path = CHECKPOINT_DIR / "sampled_docs.json",
) -> dict[str, list[DocWithMeta]]:
    """Return {"removed": [...], "retained": [...]} each ~sample_size docs."""
    if checkpoint_path.exists():
        print(f"✓ Loading sampled_docs from checkpoint")
        data = json.loads(checkpoint_path.read_text())
        return {
            "removed": _docs_from_json(data["removed"]),
            "retained": _docs_from_json(data["retained"]),
        }

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    proportions = compute_subset_proportions(removed_hashes)
    print(f"Subset proportions: {len(proportions)} subsets")

    removed_set = set(removed_hashes.keys())

    print("Sampling removed docs...")
    removed_docs = reservoir_sample_stratified(
        pile_stream_id, removed_set, proportions,
        n=sample_size, seed=seed, is_removed=True,
    )
    print(f"  Removed sampled: {len(removed_docs)}")

    print("Sampling retained docs...")
    retained_docs = reservoir_sample_stratified(
        dedup_stream_id, removed_set, proportions,
        n=sample_size, seed=seed + 1, is_removed=False,
    )
    print(f"  Retained sampled: {len(retained_docs)}")

    result = {"removed": removed_docs, "retained": retained_docs}
    payload = {
        "removed": _docs_to_json(removed_docs),
        "retained": _docs_to_json(retained_docs),
    }
    import os
    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, checkpoint_path)
    print(f"✓ sampled_docs.json saved")
    return result
