"""Corpus curation: PPL filtering + MinHash deduplication."""
import csv
import json
import logging
import math
import os
import pathlib

import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

from config import CONFIG

logger = logging.getLogger(__name__)

VARIANTS = [
    {"ppl_threshold": tau, "dedup_j": j}
    for tau in CONFIG.ppl_thresholds
    for j in CONFIG.dedup_jaccard
]


def get_corpus_stream(corpus_name: str):
    """Return HF streaming dataset for 'dolma' or 'fineweb'."""
    from datasets import load_dataset
    if corpus_name == "dolma":
        return load_dataset("allenai/dolma", split="train", streaming=True, trust_remote_code=True)
    elif corpus_name == "fineweb":
        return load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)
    else:
        raise ValueError(f"Unknown corpus: {corpus_name}")


def score_and_filter_ppl(
    dataset_iter,
    ppl_threshold: int,
    output_path: str,
    batch_size: int = 64,
) -> dict:
    """Score docs with GPT-2 PPL; retain PPL <= threshold.
    Returns: {"retained": int, "total": int, "output_path": str}
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = GPT2LMHeadModel.from_pretrained(CONFIG.gpt2_ppl_model).eval().to(device)
    tokenizer = GPT2TokenizerFast.from_pretrained(CONFIG.gpt2_ppl_model)
    tokenizer.pad_token = tokenizer.eos_token

    os.makedirs(output_path, exist_ok=True)
    out_file = os.path.join(output_path, "filtered.jsonl")
    total, retained = 0, 0

    with open(out_file, "w") as writer:
        for doc in dataset_iter:
            text = doc.get("text", "")
            if not text.strip():
                total += 1
                continue
            # Per-document forward to avoid padding bias
            ids = tokenizer(
                text, return_tensors="pt", truncation=True, max_length=1024
            ).input_ids.to(device)
            with torch.no_grad():
                loss = model(ids, labels=ids).loss.item()
            ppl = math.exp(loss)
            total += 1
            if ppl <= ppl_threshold:
                writer.write(json.dumps(doc) + "\n")
                retained += 1

    del model
    torch.cuda.empty_cache()
    return {"retained": retained, "total": total, "output_path": output_path}


def apply_minhash_dedup(
    input_path: str,
    jaccard_threshold: float,
    output_path: str,
    cache_dir: str,
) -> dict:
    """Run NeMo-Curator FuzzyDuplicates; remove near-duplicates.
    Returns: {"retained": int, "total": int, "output_path": str}
    """
    try:
        from nemo_curator import FuzzyDuplicates, FuzzyDuplicatesConfig
        from nemo_curator.datasets import DocumentDataset

        BAND_PARAMS = CONFIG.minhash_params
        params = BAND_PARAMS[jaccard_threshold]

        cfg = FuzzyDuplicatesConfig(
            cache_dir=cache_dir,
            id_field="id",
            text_field="text",
            seed=CONFIG.minhash_seed,
            char_ngrams=CONFIG.char_ngrams,
            num_buckets=params["num_buckets"],
            hashes_per_bucket=params["hashes_per_bucket"],
            use_64_bit_hash=False,
            jaccard_threshold=jaccard_threshold,
        )
        deduper = FuzzyDuplicates(logger=logger, config=cfg)

        input_file = os.path.join(input_path, "filtered.jsonl")
        dataset = DocumentDataset.read_json(input_file, add_filename=True)
        total = len(dataset.df)
        deduped = deduper(dataset)
        retained = len(deduped.df)

        os.makedirs(output_path, exist_ok=True)
        deduped.to_json(output_path, write_to_filename=True)
        return {"retained": retained, "total": total, "output_path": output_path}

    except ImportError:
        # Fallback: simple exact-hash dedup if NeMo-Curator unavailable
        logger.warning("nemo_curator not available — falling back to exact dedup")
        return _fallback_exact_dedup(input_path, output_path, jaccard_threshold)


def _fallback_exact_dedup(input_path: str, output_path: str, jaccard_threshold: float) -> dict:
    """Exact dedup fallback when NeMo-Curator unavailable."""
    import hashlib
    os.makedirs(output_path, exist_ok=True)
    seen = set()
    total, retained = 0, 0
    input_file = os.path.join(input_path, "filtered.jsonl")
    out_file = os.path.join(output_path, "deduped.jsonl")
    with open(input_file) as f, open(out_file, "w") as w:
        for line in f:
            doc = json.loads(line)
            h = hashlib.md5(doc.get("text", "").encode()).hexdigest()
            total += 1
            if h not in seen:
                seen.add(h)
                w.write(json.dumps(doc) + "\n")
                retained += 1
    return {"retained": retained, "total": total, "output_path": output_path}


def _count_tokens_approx(jsonl_dir: str) -> int:
    """Approximate token count: avg 4 chars/token."""
    total_chars = 0
    for fname in pathlib.Path(jsonl_dir).glob("*.jsonl"):
        try:
            with open(fname) as f:
                for line in f:
                    doc = json.loads(line)
                    total_chars += len(doc.get("text", ""))
        except Exception:
            pass
    return total_chars // 4


def curate_all_variants(
    corpus_name: str,
    base_stream,
    output_root: str,
) -> list:
    """Produce 6 variants (3 PPL × 2 dedup J) for one corpus.
    Idempotent via _SUCCESS flag.
    Returns list of variant_metadata dicts.
    """
    results = []
    for v in VARIANTS:
        tau = v["ppl_threshold"]
        j = v["dedup_j"]
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

        logger.info(f"Curating {condition}...")
        stream = get_corpus_stream(corpus_name)
        ppl_stats = score_and_filter_ppl(stream, tau, ppl_dir)
        dedup_stats = apply_minhash_dedup(ppl_dir, j, dedup_dir, cache_dir)

        meta = {
            "condition": condition,
            "corpus": corpus_name,
            "ppl_threshold": tau,
            "dedup_j": j,
            "output_path": dedup_dir,
            "token_count": _count_tokens_approx(dedup_dir),
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

    return results


def log_corpus_stats(variant_metadata: list) -> None:
    """Write per-variant stats to corpus_stats.csv."""
    stats_path = os.path.join(CONFIG.corpus_root, "corpus_stats.csv")
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)
    fieldnames = [
        "condition", "corpus", "ppl_threshold", "dedup_j",
        "token_count", "contamination_rate",
    ]
    with open(stats_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for m in variant_metadata:
            w.writerow({k: m.get(k) for k in fieldnames})

    for m in variant_metadata:
        cr = m.get("contamination_rate")
        cr_str = f"{cr:.4f}" if cr is not None else "N/A"
        logger.info(
            f"[stats] {m['condition']:30s} "
            f"tokens={m.get('token_count', 0):>15,}  "
            f"CR={cr_str}"
        )
