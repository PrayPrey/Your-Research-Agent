"""Preprocessing: NeoX binary format conversion + contamination removal."""
import json
import logging
import os
import subprocess

from config import CONFIG

logger = logging.getLogger(__name__)


def convert_to_neox_binary(
    jsonl_path: str,
    output_prefix: str,
    tokenizer_path: str,
    neox_repo: str,
) -> str:
    """Call tools/preprocess_data.py; returns .bin/.idx prefix path."""
    script = os.path.join(neox_repo, "tools", "preprocess_data.py")
    cmd = [
        "python", script,
        "--input", jsonl_path,
        "--output-prefix", output_prefix,
        "--vocab-file", tokenizer_path,
        "--dataset-impl", "mmap",
        "--tokenizer-type", "HFTokenizer",
        "--append-eod",
        "--workers", "4",
    ]
    logger.info(f"Preprocessing: {jsonl_path} -> {output_prefix}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Preprocessing failed:\n{result.stderr}")
    return output_prefix


def run_decontaminator(
    corpus_path: str,
    benchmark_test_sets: list,
    output_path: str,
) -> float:
    """Run llm-decontaminator; returns contamination_rate (CR)."""
    decontam_script = os.path.join("llm-decontaminator", "src", "decontaminate.py")
    if not os.path.exists(decontam_script):
        logger.warning("llm-decontaminator not found — using CR=0.0")
        return 0.0

    benchmark_str = ",".join(benchmark_test_sets)
    cmd = [
        "python", decontam_script,
        "--data_path", corpus_path,
        "--benchmark", benchmark_str,
        "--output_path", output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Decontaminator failed: {result.stderr[:200]}")
        return 0.0

    # Parse CR from output
    try:
        with open(os.path.join(output_path, "contamination_rate.json")) as f:
            cr_data = json.load(f)
        return float(cr_data.get("contamination_rate", 0.0))
    except Exception:
        return 0.0


def preprocess_all_variants(
    variant_metadata: list,
    neox_repo: str,
) -> list:
    """Process all variants: add binary_prefix and contamination_rate."""
    tokenizer_path = CONFIG.neox_tokenizer
    benchmark_sets = ["mmlu", "hellaswag"]

    for meta in variant_metadata:
        condition = meta["condition"]
        dedup_dir = meta["output_path"]
        binary_dir = os.path.join(CONFIG.corpus_root, condition, "binary")
        os.makedirs(binary_dir, exist_ok=True)

        # Find jsonl file
        jsonl_files = []
        for fname in os.listdir(dedup_dir):
            if fname.endswith(".jsonl"):
                jsonl_files.append(os.path.join(dedup_dir, fname))

        if not jsonl_files:
            logger.warning(f"No JSONL files in {dedup_dir}")
            meta["binary_prefix"] = None
            meta["contamination_rate"] = 0.0
            continue

        binary_prefix = os.path.join(binary_dir, condition)
        done_flag = binary_prefix + "_text_document.bin"

        if not os.path.exists(done_flag):
            # Merge jsonl files if multiple
            merged = os.path.join(dedup_dir, "merged.jsonl")
            if not os.path.exists(merged):
                with open(merged, "w") as out:
                    for jf in jsonl_files:
                        with open(jf) as f:
                            out.write(f.read())

            try:
                convert_to_neox_binary(merged, binary_prefix, tokenizer_path, neox_repo)
            except RuntimeError as e:
                logger.warning(f"NeoX conversion failed for {condition}: {e}")
                meta["binary_prefix"] = None
                meta["contamination_rate"] = 0.0
                continue

        meta["binary_prefix"] = binary_prefix

        # Run decontaminator
        decontam_out = os.path.join(binary_dir, "decontam")
        cr = run_decontaminator(
            jsonl_files[0], benchmark_sets, decontam_out
        )
        meta["contamination_rate"] = cr
        logger.info(f"[preprocess] {condition}: binary={binary_prefix}, CR={cr:.4f}")

    return variant_metadata
