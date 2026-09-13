"""A-2: Corpus Streamer — streaming SHA-256 diff of Pile vs dedup-Pile."""
import hashlib
import json
import os
from pathlib import Path
from typing import Iterator

from config import PILE_HF_ID, PILE_DEDUP_HF_ID, CHECKPOINT_DIR


def stream_hashes(hf_id: str, text_col: str = "text") -> Iterator[tuple[str, str]]:
    """Yield (sha256_hex, pile_subset) for each doc in streaming dataset."""
    from datasets import load_dataset
    ds = load_dataset(hf_id, split="train", streaming=True)
    for doc in ds:
        text = doc[text_col]
        h = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        meta = doc.get("meta")
        if isinstance(meta, dict):
            subset = meta.get("pile_set_name", "unknown")
        else:
            subset = "unknown"
        yield h, subset


def save_hash_checkpoint(
    removed_hashes: dict[str, str],
    checkpoint_path: Path,
    n_processed: int,
) -> None:
    """Atomic write of {hashes, n_processed} to JSON checkpoint."""
    payload = {"hashes": removed_hashes, "n_processed": n_processed}
    tmp = checkpoint_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, checkpoint_path)


def load_hash_checkpoint(checkpoint_path: Path) -> tuple[dict[str, str], int]:
    """Load (removed_hashes, n_processed) from checkpoint. Returns ({}, 0) if missing."""
    if not checkpoint_path.exists():
        return {}, 0
    payload = json.loads(checkpoint_path.read_text())
    return payload["hashes"], payload["n_processed"]


def find_removed_hashes(
    pile_id: str = PILE_HF_ID,
    dedup_id: str = PILE_DEDUP_HF_ID,
    checkpoint_path: Path = CHECKPOINT_DIR / "removed_hashes.json",
) -> dict[str, str]:
    """Return {sha256_hex: pile_subset} for docs in Pile but NOT in dedup-Pile.

    Algorithm:
    1. Stream dedup-Pile → build dedup_set: set[sha256_hex]
    2. Stream Pile → hash not in dedup_set → add to removed_dict
    3. Checkpoint every 100k docs; resumes if checkpoint exists.
    """
    # Resume from checkpoint if available
    if checkpoint_path.exists():
        try:
            payload = json.loads(checkpoint_path.read_text())
            if isinstance(payload, dict) and "hashes" in payload:
                print(f"✓ Resuming from checkpoint: {len(payload['hashes'])} removed hashes")
                return payload["hashes"]
            # Legacy format (plain dict)
            return payload
        except (json.JSONDecodeError, KeyError):
            pass

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    print("Building dedup-Pile hash set (streaming)...")
    dedup_set: set[str] = set()
    for i, (h, _) in enumerate(stream_hashes(dedup_id)):
        dedup_set.add(h)
        if (i + 1) % 500_000 == 0:
            print(f"  dedup-Pile: {i+1:,} docs hashed")

    print(f"dedup-Pile hash set built: {len(dedup_set):,} docs")

    removed: dict[str, str] = {}
    n_processed = 0
    for h, subset in stream_hashes(pile_id):
        if h not in dedup_set:
            removed[h] = subset
        n_processed += 1
        if n_processed % 100_000 == 0:
            print(f"  Pile: {n_processed:,} processed, {len(removed):,} removed")
            save_hash_checkpoint(removed, checkpoint_path, n_processed)

    save_hash_checkpoint(removed, checkpoint_path, n_processed)
    print(f"Corpus diff complete: {len(removed):,} removed docs found")
    return removed
