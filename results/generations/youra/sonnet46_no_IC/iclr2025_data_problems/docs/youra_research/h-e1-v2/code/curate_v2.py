"""FineWeb-only curation with 1B token budget enforcement for h-e1-v2."""
import json
import logging
import os
import pathlib
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from curate import (  # noqa: E402
    get_corpus_stream,
    score_and_filter_ppl,
    apply_minhash_dedup,
    _count_tokens_approx,
)

logger = logging.getLogger(__name__)


def pad_to_token_budget(
    docs: list,
    target_tokens: int = 1_000_000_000,
    token_key: str = "text",
    seed: int = 1,
) -> list:
    """Repeat-sample docs (circular) until target_tokens reached.

    Uses word-count * 4/3 as approx token estimate.
    ponytail: word-based token estimate; replace with tokenizer if off >10%.
    """
    rng = random.Random(seed)
    current = sum(len(d.get(token_key, "").split()) * 4 // 3 for d in docs)
    if current >= target_tokens:
        return docs
    pool = docs[:]
    rng.shuffle(pool)
    idx = 0
    while current < target_tokens:
        doc = pool[idx % len(pool)]
        docs.append(doc)
        current += len(doc.get(token_key, "").split()) * 4 // 3
        idx += 1
    return docs


def _load_jsonl_docs(jsonl_dir: str) -> list:
    """Load all docs from .jsonl files in directory."""
    docs = []
    for fname in pathlib.Path(jsonl_dir).glob("*.jsonl"):
        try:
            with open(fname) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        docs.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error reading {fname}: {e}")
    return docs


def curate_all_variants_v2(
    corpus_name: str = "fineweb",
    output_root: str = None,
    target_tokens: int = 1_000_000_000,
    seeds: list = None,
) -> list:
    """Produce 6 filtered+deduped FineWeb variants, each padded to target_tokens.

    Returns list of variant_metadata dicts (same schema as h-e1 curate_all_variants).
    """
    if seeds is None:
        seeds = [1, 2]
    if output_root is None:
        raise ValueError("output_root required")

    from config_v2 import CURATION_CONDITIONS

    results = []
    for cond in CURATION_CONDITIONS:
        tau = cond["ppl_threshold"]
        j = cond["jaccard_threshold"]
        condition = f"{corpus_name}_ppl{tau}_j{int(j*10):02d}"
        ppl_dir = os.path.join(output_root, condition, "ppl_filtered")
        dedup_dir = os.path.join(output_root, condition, "deduped")
        cache_dir = os.path.join(output_root, ".cache", condition)
        done_flag = os.path.join(dedup_dir, "_SUCCESS")
        meta_file = os.path.join(dedup_dir, "meta.json")

        if os.path.exists(done_flag):
            with open(meta_file) as f:
                meta = json.load(f)
            results.append(meta)
            logger.info(f"Skipping {condition} (already done)")
            continue

        logger.info(f"Curating {condition} ...")
        stream = get_corpus_stream(corpus_name)
        ppl_stats = score_and_filter_ppl(stream, tau, ppl_dir)
        dedup_stats = apply_minhash_dedup(ppl_dir, j, dedup_dir, cache_dir)

        # Token budget enforcement via repeat-sampling
        token_count = _count_tokens_approx(dedup_dir)
        if token_count < target_tokens:
            logger.info(
                f"{condition}: {token_count:,} tokens < {target_tokens:,} — padding via repeat-sampling"
            )
            docs = _load_jsonl_docs(dedup_dir)
            docs = pad_to_token_budget(docs, target_tokens, seed=seeds[0])
            # Write padded docs back
            padded_file = os.path.join(dedup_dir, "padded.jsonl")
            with open(padded_file, "w") as f:
                for doc in docs:
                    f.write(json.dumps(doc) + "\n")
            token_count = sum(len(d.get("text", "").split()) * 4 // 3 for d in docs)
            logger.info(f"{condition}: padded to {token_count:,} tokens")

        meta = {
            "condition": condition,
            "corpus": corpus_name,
            "ppl_threshold": tau,
            "dedup_j": j,
            "output_path": dedup_dir,
            "token_count": token_count,
            "contamination_rate": None,
            "ppl_retained": ppl_stats["retained"],
            "ppl_total": ppl_stats["total"],
            "dedup_retained": dedup_stats["retained"],
            "dedup_total": dedup_stats["total"],
        }
        os.makedirs(dedup_dir, exist_ok=True)
        with open(meta_file, "w") as f:
            json.dump(meta, f, indent=2)
        pathlib.Path(done_flag).touch()
        results.append(meta)
        logger.info(f"Done: {condition} — {token_count:,} tokens")

    return results
