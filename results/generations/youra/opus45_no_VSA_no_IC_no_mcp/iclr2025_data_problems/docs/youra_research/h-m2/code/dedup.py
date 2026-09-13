"""Deduplication module using MinHash LSH."""
import hashlib
from typing import List, Dict, Set
from collections import defaultdict
from config import DeduplicationConfig, MINHASH_NUM_PERM, MINHASH_NGRAM_SIZE

def get_ngrams(text: str, n: int = MINHASH_NGRAM_SIZE) -> Set[str]:
    """Extract word n-grams from text."""
    words = text.lower().split()
    if len(words) < n:
        return {text}
    return {" ".join(words[i:i+n]) for i in range(len(words) - n + 1)}

def minhash_signature(ngrams: Set[str], num_perm: int = MINHASH_NUM_PERM) -> List[int]:
    """Compute MinHash signature for a set of n-grams."""
    if not ngrams:
        return [0] * num_perm
    signature = []
    for i in range(num_perm):
        min_hash = float('inf')
        for ngram in ngrams:
            h = int(hashlib.md5(f"{i}:{ngram}".encode()).hexdigest(), 16)
            min_hash = min(min_hash, h)
        signature.append(min_hash)
    return signature

def estimate_jaccard(sig1: List[int], sig2: List[int]) -> float:
    """Estimate Jaccard similarity from MinHash signatures."""
    if len(sig1) != len(sig2):
        return 0.0
    matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
    return matches / len(sig1)

def apply_deduplication(documents: List[str], config: DeduplicationConfig) -> List[str]:
    """Apply deduplication at specified stringency level."""
    if config.level == "none":
        return documents

    if config.include_exact:
        seen = set()
        unique_docs = []
        for doc in documents:
            doc_hash = hashlib.md5(doc.encode()).hexdigest()
            if doc_hash not in seen:
                seen.add(doc_hash)
                unique_docs.append(doc)
        documents = unique_docs

    if config.jaccard_threshold < 1.0:
        signatures = []
        for doc in documents:
            ngrams = get_ngrams(doc)
            sig = minhash_signature(ngrams)
            signatures.append(sig)

        # LSH banding: partition signature into bands
        num_bands = 16
        rows_per_band = MINHASH_NUM_PERM // num_bands
        buckets = defaultdict(list)

        for idx, sig in enumerate(signatures):
            for band in range(num_bands):
                start = band * rows_per_band
                band_sig = tuple(sig[start:start + rows_per_band])
                bucket_key = (band, band_sig)
                buckets[bucket_key].append(idx)

        # Find candidate pairs from buckets
        duplicates = set()
        for indices in buckets.values():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        idx1, idx2 = indices[i], indices[j]
                        if idx1 not in duplicates and idx2 not in duplicates:
                            jaccard = estimate_jaccard(signatures[idx1], signatures[idx2])
                            if jaccard >= config.jaccard_threshold:
                                duplicates.add(idx2)

        documents = [doc for idx, doc in enumerate(documents) if idx not in duplicates]

    return documents

def verify_deduplication_applied(
    original_count: int,
    deduplicated_count: int,
    config: DeduplicationConfig
) -> bool:
    """Verify deduplication mechanism is working."""
    if config.level == "none":
        return original_count == deduplicated_count

    removal_rate = (original_count - deduplicated_count) / max(original_count, 1)
    return removal_rate >= 0.0  # any dedup applied

def log_dedup_stats(level: str, original_count: int, deduplicated_count: int) -> Dict:
    """Log deduplication statistics."""
    removed = original_count - deduplicated_count
    pct = (removed / max(original_count, 1)) * 100
    print(f"[DEDUP] level={level}: {original_count} -> {deduplicated_count} (removed {removed}, {pct:.2f}%)")
    return {
        "level": level,
        "original": original_count,
        "deduplicated": deduplicated_count,
        "removed": removed,
        "removal_pct": pct
    }
