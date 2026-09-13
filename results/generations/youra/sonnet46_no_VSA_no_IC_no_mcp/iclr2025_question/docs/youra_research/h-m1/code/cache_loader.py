"""Cache loader for H-M1: loads H-E1 outputs and computes per-sample TE + cluster assignments."""
import os
import sys
import numpy as np

HE1_CODE_DIR = os.path.join(
    os.path.dirname(__file__), "../../h-e1/code"
)


def _import_he1(he1_code_dir: str):
    he1_code_dir = os.path.abspath(he1_code_dir)
    if he1_code_dir not in sys.path:
        sys.path.insert(0, he1_code_dir)
    from data import load_h_e2v2_samples, get_pilot_questions
    from compute_se import get_semantic_ids, load_nli_model
    return load_h_e2v2_samples, get_pilot_questions, get_semantic_ids, load_nli_model


def _check_he1_cache(he1_results_dir: str) -> dict:
    files = ["te_scores.npy", "se_scores.npy", "correctness.npy", "results.json"]
    return {f: os.path.exists(os.path.join(he1_results_dir, f)) for f in files}


def compute_per_sample_te(questions: list, samples_map: dict) -> dict:
    """
    Proxy TE per sample from sequence log-probs: -lp / token_count.
    Returns dict[qid -> list[float]] len K per question.
    """
    per_sample_te = {}
    for q in questions:
        qid = q["question_id"]
        sdata = samples_map[qid]
        samples = sdata["samples"]
        log_probs = sdata["log_probs"]
        K = min(len(samples), len(log_probs))
        tes = []
        for s, lp in zip(samples[:K], log_probs[:K]):
            n_tokens = max(len(s.split()), 1)
            val = -lp / n_tokens
            tes.append(val if not (val != val) else 0.0)  # replace NaN with 0
        per_sample_te[qid] = tes
    return per_sample_te


def compute_cluster_assignments(questions: list, samples_map: dict, nli_pipeline) -> dict:
    """
    Runs get_semantic_ids per question.
    Returns dict[qid -> {sample_idx: cluster_id}].
    """
    from compute_se import get_semantic_ids
    assignments = {}
    for i, q in enumerate(questions):
        qid = q["question_id"]
        samples = samples_map[qid]["samples"]
        cluster_ids = get_semantic_ids(samples, nli_pipeline)
        assignments[qid] = {idx: cid for idx, cid in enumerate(cluster_ids)}
        if (i + 1) % 10 == 0:
            print(f"  Clustering: {i+1}/{len(questions)} done")
    return assignments


def load_or_recompute(
    he1_results_dir: str,
    he1_code_dir: str,
    samples_path: str = None,
    n: int = 98,
    seed: int = 42,
    nli_model_id: str = "cross-encoder/nli-deberta-v3-large",
    nli_device: int = 0,
) -> dict:
    """
    Returns dict with keys:
      questions, samples_map, per_sample_te, cluster_assignments, correctness, se_scores
    """
    load_h_e2v2_samples, get_pilot_questions, get_semantic_ids, load_nli_model = _import_he1(he1_code_dir)

    cache = _check_he1_cache(he1_results_dir)
    print(f"[H-M1] H-E1 cache: {cache}")

    # Load data
    if samples_path:
        samples_map = load_h_e2v2_samples(samples_path)
    else:
        samples_map = load_h_e2v2_samples()
    questions = get_pilot_questions(samples_map, n=n, seed=seed)
    print(f"[H-M1] Loaded {len(questions)} questions")

    # Load se_scores from cache
    if cache.get("se_scores.npy"):
        se_scores = np.load(os.path.join(he1_results_dir, "se_scores.npy")).tolist()
        print(f"[H-M1] Loaded se_scores from cache ({len(se_scores)} values)")
    else:
        raise RuntimeError("se_scores.npy not found in H-E1 results — cannot proceed without SE scores")

    # Load correctness
    if cache.get("correctness.npy"):
        correctness = np.load(os.path.join(he1_results_dir, "correctness.npy")).tolist()
        print(f"[H-M1] Loaded correctness from cache ({len(correctness)} values)")
    else:
        correctness = [int(q.get("is_correct", 0) or 0) for q in questions]
        print(f"[H-M1] Computed correctness from samples_map")

    # Per-sample TE (proxy from log_probs — no GPU needed)
    print("[H-M1] Computing per-sample TE proxies from log_probs...")
    per_sample_te = compute_per_sample_te(questions, samples_map)

    # Cluster assignments via NLI
    print("[H-M1] Loading NLI model for cluster assignments...")
    nli_pipeline = load_nli_model(model_id=nli_model_id, device=nli_device)
    print("[H-M1] Computing cluster assignments...")
    cluster_assignments = compute_cluster_assignments(questions, samples_map, nli_pipeline)

    return {
        "questions": questions,
        "samples_map": samples_map,
        "per_sample_te": per_sample_te,
        "cluster_assignments": cluster_assignments,
        "correctness": correctness,
        "se_scores": se_scores,
    }
