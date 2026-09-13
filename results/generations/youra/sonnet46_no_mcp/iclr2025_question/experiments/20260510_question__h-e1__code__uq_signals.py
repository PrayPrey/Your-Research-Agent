import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import torch
from tqdm import tqdm

from config import ExperimentConfig


# ─── L-A3-4: Batched NLI Pair Helpers ────────────────────────────────────────

def _build_nli_pairs(samples: List[str]) -> List[Dict[str, str]]:
    """Build all ordered (i,j) premise-hypothesis pairs for N samples.
    Returns N*(N-1) dicts for N=5 → 20 pairs.
    """
    N = len(samples)
    return [
        {"text": samples[i], "text_pair": samples[j]}
        for i in range(N) for j in range(N) if i != j
    ]


def _run_nli_batch(
    pairs: List[Dict[str, str]],
    nli_pipeline,
    batch_size: int = 16,
) -> List[Dict[str, Any]]:
    """Run NLI pipeline over pairs with batching. Falls back to batch_size=1 on OOM."""
    results = []
    try:
        for i in range(0, len(pairs), batch_size):
            chunk = pairs[i:i + batch_size]
            out = nli_pipeline(
                chunk,
                truncation=True,
                max_length=512,
                batch_size=batch_size,
            )
            results.extend(out)
    except (RuntimeError, torch.cuda.OutOfMemoryError):
        torch.cuda.empty_cache()
        results = []
        for pair in pairs:
            out = nli_pipeline([pair], truncation=True, max_length=512, batch_size=1)
            results.extend(out)
    return results


# ─── L-A3-1: NLI Clustering + Semantic Entropy ───────────────────────────────

def load_nli_pipeline(cfg: ExperimentConfig):
    """Load deberta-large-mnli text-classification pipeline."""
    from transformers import pipeline
    device = 0 if torch.cuda.is_available() else -1
    return pipeline(
        "text-classification",
        model=cfg.nli_model_id,
        device=device,
        top_k=None,
    )


def _union_find_clusters(N: int, entailment_matrix: Dict) -> Dict[int, int]:
    """Union-Find for transitive cluster closure over bidirectional entailment."""
    parent = list(range(N))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i in range(N):
        for j in range(N):
            if i != j and entailment_matrix.get((i, j), False):
                union(i, j)

    # Normalize cluster IDs
    root_to_id = {}
    cluster_ids = {}
    for i in range(N):
        root = find(i)
        if root not in root_to_id:
            root_to_id[root] = len(root_to_id)
        cluster_ids[i] = root_to_id[root]
    return cluster_ids


def cluster_by_nli(
    samples: List[str],
    nli_pipeline,
    batch_size: int = 16,
) -> Dict[int, int]:
    """Bidirectional NLI entailment clustering (Kuhn 2023).
    Returns {sample_idx: cluster_id}.
    """
    N = len(samples)
    if N <= 1:
        return {0: 0}

    pairs = _build_nli_pairs(samples)
    results = _run_nli_batch(pairs, nli_pipeline, batch_size)

    # Build ordered pair index for matrix lookup
    ordered_pairs = [(i, j) for i in range(N) for j in range(N) if i != j]

    # Parse entailment labels (handles both list-of-dicts and single dict per pair)
    def get_label(result_item):
        if isinstance(result_item, list):
            # top_k=None returns list sorted by score; find ENTAILMENT
            for r in result_item:
                if r["label"].upper() == "ENTAILMENT":
                    return r
            return result_item[0]
        return result_item

    entailment_raw = {}
    for k, (i, j) in enumerate(ordered_pairs):
        item = results[k] if k < len(results) else {"label": "NEUTRAL"}
        parsed = get_label(item)
        entailment_raw[(i, j)] = parsed["label"].upper() == "ENTAILMENT"

    # Build bidirectional entailment matrix
    entailment_matrix = {}
    for i in range(N):
        for j in range(N):
            if i != j:
                entailment_matrix[(i, j)] = (
                    entailment_raw.get((i, j), False) and entailment_raw.get((j, i), False)
                )

    return _union_find_clusters(N, entailment_matrix)


def compute_semantic_entropy(
    samples: List[str],
    nli_pipeline,
    batch_size: int = 16,
) -> float:
    """Shannon entropy over NLI cluster frequency distribution."""
    N = len(samples)
    if N == 0:
        return 0.0
    cluster_ids = cluster_by_nli(samples, nli_pipeline, batch_size)
    counts = Counter(cluster_ids.values())
    probs = [c / N for c in counts.values()]
    H = -sum(p * math.log(p + 1e-9) for p in probs)
    return float(H)


def compute_all_semantic_entropy(
    outputs_dir: str,
    cfg: ExperimentConfig,
    nli_pipeline=None,
) -> Dict[int, float]:
    """Compute semantic entropy for all examples. Returns {id: float}."""
    from inference import load_stochastic_outputs

    stochastic = load_stochastic_outputs(outputs_dir)
    if nli_pipeline is None:
        nli_pipeline = load_nli_pipeline(cfg)

    scores = {}
    for eid, samples in tqdm(stochastic.items(), desc="Semantic entropy"):
        scores[eid] = compute_semantic_entropy(samples, nli_pipeline, cfg.nli_batch_size)

    out_path = Path(outputs_dir) / "uq_scores" / "semantic_entropy.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({str(k): v for k, v in scores.items()}, f)

    return scores


# ─── L-A3-2: Token Entropy Mean ───────────────────────────────────────────────

def compute_token_entropy_mean(logits: torch.Tensor) -> float:
    """Mean Shannon entropy over per-token distributions.
    logits: [seq_len, vocab_size] float16 or float32
    """
    logits_f = logits.float()  # Cast fp16 → float32
    probs = torch.softmax(logits_f, dim=-1)
    token_H = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1)  # [seq_len]
    return float(token_H.mean().item())


def compute_all_token_entropy(
    outputs_dir: str,
    cfg: ExperimentConfig,
) -> Dict[int, float]:
    """Load greedy_logits/*.pt and compute token entropy. Returns {id: float}."""
    logits_dir = Path(outputs_dir) / "greedy_logits"
    scores = {}

    pt_files = sorted(logits_dir.glob("example_*.pt"))
    for pt_file in tqdm(pt_files, desc="Token entropy"):
        eid = int(pt_file.stem.split("_")[-1])
        logits = torch.load(pt_file, map_location="cpu")
        scores[eid] = compute_token_entropy_mean(logits)

    out_path = Path(outputs_dir) / "uq_scores" / "token_entropy_mean.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({str(k): v for k, v in scores.items()}, f)

    return scores


# ─── L-A3-3: SelfCheckGPT-BERTScore ─────────────────────────────────────────

def compute_selfcheckgpt_bertscore(
    greedy_response: str,
    stochastic_samples: List[str],
    checker=None,
) -> float:
    """Segment greedy into sentences, score each vs stochastic_samples.
    Returns mean inconsistency score (higher = more hallucinated).
    """
    import nltk
    try:
        sentences = nltk.sent_tokenize(greedy_response)
    except Exception:
        sentences = []

    if not sentences:
        sentences = [greedy_response] if greedy_response.strip() else [""]

    # Filter out samples that would produce empty spacy sentence lists (len<=3 chars)
    filtered_samples = [s for s in stochastic_samples if s and len(s.strip()) > 3]
    if not filtered_samples:
        return 0.0

    if checker is None:
        from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
        checker = SelfCheckBERTScore(rescale_with_baseline=True)

    try:
        scores = checker.predict(
            sentences=sentences,
            sampled_passages=filtered_samples,
        )
        return float(np.mean(scores))
    except (IndexError, RuntimeError):
        return 0.0


def compute_all_selfcheckgpt(
    outputs_dir: str,
    cfg: ExperimentConfig,
) -> Dict[int, float]:
    """Compute selfcheckgpt_bertscore for all examples with checkpoint-resume. Returns {id: float}."""
    from inference import load_greedy_outputs, load_stochastic_outputs
    from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore
    import nltk

    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)

    out_path = Path(outputs_dir) / "uq_scores" / "selfcheckgpt_bertscore_n5.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Checkpoint-resume: load partial results if they exist
    scores = {}
    partial_path = Path(outputs_dir) / "uq_scores" / "selfcheckgpt_partial.jsonl"
    if partial_path.exists():
        with open(partial_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        scores[int(rec["id"])] = rec["score"]
                    except (KeyError, ValueError, json.JSONDecodeError):
                        pass
        if scores:
            print(f"Resuming SelfCheckGPT from {len(scores)} completed examples")

    greedy = load_greedy_outputs(outputs_dir)
    stochastic = load_stochastic_outputs(outputs_dir)
    checker = SelfCheckBERTScore(rescale_with_baseline=True)

    common_ids = set(greedy.keys()) & set(stochastic.keys())
    remaining = sorted(eid for eid in common_ids if eid not in scores)

    with open(partial_path, "a") as pf:
        for eid in tqdm(remaining, desc="SelfCheckGPT"):
            resp = greedy[eid].get("response", "")
            samples = stochastic[eid]
            score = compute_selfcheckgpt_bertscore(resp, samples, checker)
            scores[eid] = score
            pf.write(json.dumps({"id": eid, "score": score}) + "\n")
            pf.flush()

    with open(out_path, "w") as f:
        json.dump({str(k): v for k, v in scores.items()}, f)

    # Clean up partial file after successful completion
    if partial_path.exists():
        partial_path.unlink()

    return scores
