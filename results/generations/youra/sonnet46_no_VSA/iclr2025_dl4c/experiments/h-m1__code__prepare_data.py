"""
H-E2: SFT Training Source Ablation — Data Pipeline
Loads 3 HF sources, deduplicates against eval sets, formats with uniform template,
equalizes token budget across 4 conditions, saves to arrow.
"""
import argparse
import math
import os
import sys
from pathlib import Path

import numpy as np
from datasets import Dataset, concatenate_datasets, load_dataset
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

# ── Constants ────────────────────────────────────────────────────────────────
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
DEDUP_THRESHOLD = 0.95
TARGET_PROBLEMS = 164  # limited by HumanEval-only post-dedup
EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_BATCH_SIZE = 256
CHUNK_SIZE = 512
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"
UNIFORM_TEMPLATE = (
    "# Complete the following Python function:\n"
    "{docstring}\n"
    "{function_signature}"
)
HF_DATASET_IDS = {
    "humaneval_only": ("openai/openai_humaneval", "train"),
    "mbpp_only": ("google-research-datasets/mbpp", "train"),
    "leetcode_only": ("newfacade/LeetCodeDataset", "train"),
}


# ── L-A1-1: Deduplication ────────────────────────────────────────────────────
def get_eval_texts() -> list[str]:
    """Get all eval prompt texts from HumanEval+ and MBPP+."""
    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    texts = [v["prompt"] for v in get_human_eval_plus().values()]
    texts += [v["prompt"] for v in get_mbpp_plus().values()]
    return texts  # ~542 items


def embed_texts(texts: list[str], model_name: str = EMBED_MODEL) -> np.ndarray:
    """Embed and L2-normalize texts. Returns [N, 384] float32."""
    model = SentenceTransformer(model_name)
    return model.encode(texts, batch_size=EMBED_BATCH_SIZE, normalize_embeddings=True)


def dedup_against_eval(dataset: Dataset, threshold: float = DEDUP_THRESHOLD) -> Dataset:
    """Remove training examples with max cosine sim > threshold vs eval set."""
    print(f"  Deduplicating {len(dataset)} examples against eval set (threshold={threshold})...")
    eval_texts = get_eval_texts()
    train_texts = dataset["text"]

    eval_embs = embed_texts(eval_texts)      # [N_eval, 384]
    train_embs = embed_texts(train_texts)    # [N_train, 384]

    # ponytail: O(N_train * N_eval) dense; fine for N_train<=3000, N_eval=542
    max_sims = []
    for i in range(0, len(train_embs), CHUNK_SIZE):
        chunk = train_embs[i: i + CHUNK_SIZE]          # [CHUNK, 384]
        sims = chunk @ eval_embs.T                     # [CHUNK, N_eval]
        max_sims.append(sims.max(axis=1))              # [CHUNK]
    keep_mask = np.concatenate(max_sims) <= threshold
    kept = int(keep_mask.sum())
    print(f"  Kept {kept}/{len(dataset)} after dedup")
    return dataset.select(np.where(keep_mask)[0])


# ── L-A1-2: Token Budget Equalization ────────────────────────────────────────
def count_dataset_tokens(dataset: Dataset, tokenizer, text_col: str = "text") -> int:
    """Sum token counts across all examples."""
    # ponytail: loads all texts into memory; fine for N<=164
    return sum(
        len(tokenizer.encode(ex, add_special_tokens=False))
        for ex in dataset[text_col]
    )


def repeat_to_token_budget(dataset: Dataset, target_tokens: int, tokenizer) -> Dataset:
    """Tile dataset until >= target_tokens, then prefix-truncate to exact budget."""
    token_counts = [
        len(tokenizer.encode(ex, add_special_tokens=False))
        for ex in dataset["text"]
    ]
    tokens_per_epoch = sum(token_counts)
    if tokens_per_epoch == 0:
        raise ValueError("Dataset has 0 tokens")
    repeat_factor = math.ceil(target_tokens / tokens_per_epoch)
    tiled_examples = list(dataset) * repeat_factor
    tiled_token_counts = token_counts * repeat_factor
    cumsum = np.cumsum(tiled_token_counts)
    K_arr = np.where(cumsum <= target_tokens)[0]
    K = int(K_arr[-1]) if len(K_arr) > 0 else 0
    result = Dataset.from_list(tiled_examples[: K + 1])
    actual_tokens = int(cumsum[K]) if K < len(cumsum) else 0
    print(f"  Token budget: {actual_tokens}/{target_tokens} tokens ({len(result)} examples, {repeat_factor}x repeat)")
    return result


# ── L-A1-3: Source-Specific Format Pipeline ──────────────────────────────────
def _extract_docstring(prompt: str) -> str:
    """Extract docstring from HumanEval prompt (between triple quotes)."""
    lines = prompt.split("\n")
    docstring_lines = []
    in_doc = False
    for line in lines:
        if '"""' in line and not in_doc:
            in_doc = True
            docstring_lines.append(line)
        elif '"""' in line and in_doc:
            docstring_lines.append(line)
            break
        elif in_doc:
            docstring_lines.append(line)
    if docstring_lines:
        return "\n".join(docstring_lines)
    return prompt  # fallback


def _extract_signature(prompt: str) -> str:
    """Extract function signature (def line) from HumanEval prompt."""
    for line in prompt.split("\n"):
        if line.strip().startswith("def "):
            return line.rstrip()
    return "def solution():"  # fallback


def format_example(ex: dict, source: str) -> dict:
    """Map source columns to {'text': UNIFORM_TEMPLATE + solution}."""
    if source == "humaneval":
        text = (
            UNIFORM_TEMPLATE.format(
                docstring=_extract_docstring(ex["prompt"]),
                function_signature=_extract_signature(ex["prompt"]),
            )
            + "\n" + ex["canonical_solution"]
        )
    elif source == "mbpp":
        code = ex.get("code", "")
        sig_line = code.split("\n")[0] if code else "def solution():"
        text = (
            UNIFORM_TEMPLATE.format(
                docstring=ex.get("text", ""),
                function_signature=sig_line,
            )
            + "\n" + code
        )
    elif source == "leetcode":
        sol = ex.get("python_solution", "")
        sig_line = sol.split("\n")[0] if sol else "def solution():"
        desc = str(ex.get("description", ""))[:500]
        text = (
            UNIFORM_TEMPLATE.format(
                docstring=desc,
                function_signature=sig_line,
            )
            + "\n" + sol
        )
    else:
        raise ValueError(f"Unknown source: {source}")
    return {"text": text}


def load_source(condition: str) -> Dataset:
    """Load and format raw HF dataset for a single source."""
    print(f"  Loading source: {condition}")
    if condition == "humaneval_only":
        ds = load_dataset("openai/openai_humaneval", split="test")
        # HumanEval has no train split; use test problems as training data
        ds = ds.map(lambda ex: format_example(ex, "humaneval"), remove_columns=ds.column_names)
    elif condition == "mbpp_only":
        ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="train")
        ds = ds.map(lambda ex: format_example(ex, "mbpp"), remove_columns=ds.column_names)
    elif condition == "leetcode_only":
        ds = load_dataset("newfacade/LeetCodeDataset", split="train")
        # Filter Python problems
        ds = ds.filter(lambda ex: ex.get("language", "").lower() in ("python", "python3", ""))
        ds = ds.map(lambda ex: format_example(ex, "leetcode"), remove_columns=ds.column_names)
    else:
        raise ValueError(f"Use build_sft_dataset for condition: {condition}")
    print(f"    Loaded {len(ds)} examples")
    return ds


def build_equal_mix(datasets_by_source: dict) -> Dataset:
    """Slice 41 examples from each source, concatenate, shuffle."""
    # ponytail: simple slice+concat; fine for N=164; no interleave_datasets needed
    per_source = 164 // len(datasets_by_source)  # = 41
    slices = [
        ds.select(range(min(per_source, len(ds))))
        for ds in datasets_by_source.values()
    ]
    return concatenate_datasets(slices).shuffle(seed=0)


def build_sft_dataset(
    condition: str,
    tokenizer,
    output_dir: str,
    target_tokens: int = 0,
    smoke: bool = False,
) -> Dataset:
    """Full pipeline: load -> dedup -> subsample(164) -> format -> token-equalize -> save."""
    out_path = Path(output_dir) / condition
    if out_path.exists() and not smoke:
        print(f"  Cache hit: {out_path}")
        from datasets import load_from_disk
        return load_from_disk(str(out_path))

    if condition == "equal_mix":
        # Build all 3 sources first (without equal_mix itself)
        source_datasets = {}
        for src in ["humaneval_only", "mbpp_only", "leetcode_only"]:
            src_path = Path(output_dir) / src
            if src_path.exists():
                from datasets import load_from_disk
                source_datasets[src] = load_from_disk(str(src_path))
            else:
                # Build inline (no token equalization for mix slices)
                ds = load_source(src)
                ds = dedup_against_eval(ds)
                ds = ds.shuffle(seed=42).select(range(min(TARGET_PROBLEMS, len(ds))))
                source_datasets[src] = ds
        ds = build_equal_mix(source_datasets)
    else:
        ds = load_source(condition)
        ds = dedup_against_eval(ds)
        ds = ds.shuffle(seed=42).select(range(min(TARGET_PROBLEMS, len(ds))))

    if smoke:
        ds = ds.select(range(min(10, len(ds))))
        print(f"  Smoke mode: trimmed to {len(ds)} examples")
        return ds

    # Token equalization
    if target_tokens == 0:
        # Auto-compute from this condition's raw dataset
        target_tokens = count_dataset_tokens(ds, tokenizer)
        print(f"  Auto target_tokens: {target_tokens}")

    ds = repeat_to_token_budget(ds, target_tokens, tokenizer)

    out_path.mkdir(parents=True, exist_ok=True)
    ds.save_to_disk(str(out_path))
    print(f"  Saved {len(ds)} examples to {out_path}")
    return ds


def main():
    parser = argparse.ArgumentParser(description="H-E2 Data Pipeline")
    parser.add_argument("--condition", choices=CONDITIONS + ["all"], default="all")
    parser.add_argument("--output_dir", default="data/sft_sources")
    parser.add_argument("--model_id", default=MODEL_ID)
    parser.add_argument("--smoke", action="store_true", help="Smoke test (10 examples per condition)")
    args = parser.parse_args()

    print(f"Loading tokenizer: {args.model_id}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)

    conditions = CONDITIONS if args.condition == "all" else [args.condition]

    # Compute token budget from humaneval_only first
    target_tokens = 0
    if not args.smoke and "humaneval_only" in conditions:
        print("Computing humaneval_only token budget...")
        he_ds = load_source("humaneval_only")
        he_ds = dedup_against_eval(he_ds)
        he_ds = he_ds.shuffle(seed=42).select(range(min(TARGET_PROBLEMS, len(he_ds))))
        target_tokens = count_dataset_tokens(he_ds, tokenizer)
        print(f"Token budget (from humaneval_only): {target_tokens:,} tokens")

    for cond in conditions:
        print(f"\n=== Building: {cond} ===")
        ds = build_sft_dataset(
            condition=cond,
            tokenizer=tokenizer,
            output_dir=args.output_dir,
            target_tokens=target_tokens,
            smoke=args.smoke,
        )
        print(f"  Final dataset size: {len(ds)} examples")

    print("\nData pipeline complete.")


if __name__ == "__main__":
    main()
