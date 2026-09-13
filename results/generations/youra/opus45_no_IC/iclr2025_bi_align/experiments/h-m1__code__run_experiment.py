#!/usr/bin/env python3
"""H-M1 Experiment: User Adaptation to AI Patterns via Lagged Correlation."""

import os
import sys
import pickle
import json
import time
from datetime import datetime
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    OUTPUT_DIR, FIGURES_DIR, RESULTS_PATH,
    MIN_ALIGNED_TURNS, MAX_LAG, N_PERMUTATIONS, SEED, LENGTH_BINS, N_WORKERS
)
from lagcorr import batch_lag1, batch_multilag
from baseline import run_permutation_test
from stats import one_sample_ttest, cohens_d, check_gate, stratify_by_length
from visualize import plot_lag_profile, plot_gate_pvalue, plot_lag1_histogram

TRAJECTORY_CACHE = os.path.join(OUTPUT_DIR, "trajectories_cache.pkl")


def load_hh_rlhf_conversations():
    """Load HH-RLHF dataset and extract conversations."""
    from datasets import load_dataset
    import re

    print("Loading HH-RLHF dataset from HuggingFace...")
    ds = load_dataset("Anthropic/hh-rlhf", split="train")
    print(f"Loaded {len(ds)} samples")

    conversations = []
    for idx, row in enumerate(ds):
        chosen = row.get("chosen", "")
        turns = []
        pattern = r"\n\n(Human|Assistant): "
        parts = re.split(pattern, chosen)
        i = 1
        while i < len(parts) - 1:
            role = "user" if parts[i] == "Human" else "assistant"
            content = parts[i + 1].strip()
            if content:
                turns.append({"role": role, "content": content})
            i += 2
        if turns:
            conversations.append({"id": f"hh_{idx}", "turns": turns})

    print(f"Parsed {len(conversations)} conversations")
    return conversations


def filter_min_turns(conversations, min_turns=MIN_ALIGNED_TURNS):
    """Keep conversations with >= min_turns per role."""
    filtered = []
    for conv in conversations:
        turns = conv.get("turns", [])
        user_count = sum(1 for t in turns if t.get("role") == "user")
        ai_count = sum(1 for t in turns if t.get("role") == "assistant")
        if user_count >= min_turns and ai_count >= min_turns:
            filtered.append(conv)
    return filtered


_worker_computer = None

def _init_worker():
    """Initialize worker-local spaCy model."""
    global _worker_computer
    import spacy
    import textdescriptives
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("textdescriptives/readability")
    nlp.add_pipe("textdescriptives/dependency_distance")
    _worker_computer = nlp


def _compute_complexity_batch(texts):
    """Compute complexity for a batch of texts."""
    global _worker_computer
    results = []
    for text in texts:
        if not text or not text.strip():
            results.append(0.0)
            continue
        try:
            doc = _worker_computer(text)
            readability = getattr(doc._, "readability", {}) or {}
            fk = readability.get("flesch_kincaid_grade", 0) or 0
            sents = list(doc.sents)
            sent = sum(len(s) for s in sents) / max(1, len(sents))
            dep_dict = getattr(doc._, "dependency_distance", {}) or {}
            dep = dep_dict.get("dependency_distance_mean", 0) or 0
            norm_fk = min(max(fk / 20, 0), 1)
            norm_sent = min(max(sent / 50, 0), 1)
            norm_dep = min(max(dep / 5, 0), 1)
            results.append((norm_fk + norm_sent + norm_dep) / 3)
        except:
            results.append(0.0)
    return results


def _compute_trajectory(conv):
    """Compute complexity trajectory for one conversation."""
    global _worker_computer
    turns = conv.get("turns", [])
    user_texts = [t["content"] for t in turns if t["role"] == "user"]
    ai_texts = [t["content"] for t in turns if t["role"] == "assistant"]

    user_complexity = _compute_complexity_batch(user_texts)
    ai_complexity = _compute_complexity_batch(ai_texts)

    return (user_complexity, ai_complexity)


def build_trajectories_parallel(conversations):
    """Build complexity trajectories using multiprocessing."""
    print(f"Computing complexity for {len(conversations)} conversations...")

    with Pool(N_WORKERS, initializer=_init_worker) as pool:
        from tqdm import tqdm
        trajectories = list(tqdm(
            pool.imap(_compute_trajectory, conversations, chunksize=50),
            total=len(conversations),
            desc="Computing complexity"
        ))

    valid = [(u, a) for u, a in trajectories
             if len(u) >= MIN_ALIGNED_TURNS and len(a) >= MIN_ALIGNED_TURNS]
    print(f"Built {len(valid)} valid trajectories")
    return valid


def load_or_compute_trajectories():
    """Load cached trajectories or compute from scratch."""
    if os.path.exists(TRAJECTORY_CACHE):
        print(f"Loading cached trajectories from {TRAJECTORY_CACHE}")
        with open(TRAJECTORY_CACHE, 'rb') as f:
            return pickle.load(f)

    conversations = load_hh_rlhf_conversations()
    conversations = filter_min_turns(conversations)
    print(f"After filtering: {len(conversations)} conversations")

    trajectories = build_trajectories_parallel(conversations)

    with open(TRAJECTORY_CACHE, 'wb') as f:
        pickle.dump(trajectories, f)
    print(f"Cached trajectories to {TRAJECTORY_CACHE}")

    return trajectories


def main() -> dict:
    """Run full H-M1 experiment pipeline."""
    start_time = time.time()
    print("=" * 60)
    print("H-M1: User Adaptation to AI Patterns (Lagged Correlation)")
    print("=" * 60)

    trajectories = load_or_compute_trajectories()

    if len(trajectories) < 1000:
        raise ValueError(f"Insufficient trajectories: {len(trajectories)} < 1000")

    print(f"\n[1/5] Computing lag-1 correlations for {len(trajectories)} conversations...")
    lag1_rs = batch_lag1(trajectories)
    print(f"Valid lag-1 correlations: {len(lag1_rs)}")

    print(f"\n[2/5] Multi-lag analysis (lag -{MAX_LAG} to +{MAX_LAG})...")
    multilag_results = batch_multilag(trajectories, max_lag=MAX_LAG)
    for lag in sorted(multilag_results.keys()):
        n = len(multilag_results[lag])
        mean = sum(multilag_results[lag])/n if n > 0 else 0
        print(f" Lag {lag:+d}: n={n}, mean={mean:.4f}")

    print(f"\n[3/5] Permutation test ({N_PERMUTATIONS} shuffles)...")
    baseline_stats = run_permutation_test(trajectories, n_permutations=N_PERMUTATIONS, seed=SEED)
    print(f" Null mean: {baseline_stats['null_mean']:.4f}")
    print(f" Null p-value: {baseline_stats['null_p']:.4f}")

    print("\n[4/5] Statistical testing...")
    real_stats = one_sample_ttest(lag1_rs)
    effect_size = cohens_d(lag1_rs)
    gate_result = check_gate(real_stats, baseline_stats)

    print(f" n = {real_stats['n']}")
    print(f" Mean lag-1 r = {real_stats['mean']:.4f}")
    print(f" SD = {real_stats['std']:.4f}")
    print(f" t = {real_stats['t_statistic']:.4f}")
    print(f" p = {real_stats['p_value']:.6f}")
    print(f" 95% CI = ({real_stats['ci95'][0]:.4f}, {real_stats['ci95'][1]:.4f})")
    print(f" Cohen's d = {effect_size:.4f}")

    print("\n[4b] Length stratification...")
    length_strat = stratify_by_length(trajectories, lag1_rs, LENGTH_BINS)
    for bin_name, stats_bin in length_strat.items():
        print(f" {bin_name}: n={stats_bin.get('n', 0)}, mean={stats_bin.get('mean', 'N/A')}")

    print("\n[5/5] Gate evaluation (MUST_WORK)...")
    print(f" Criterion 1: p < 0.05 = {gate_result['criteria']['p_value_lt_0.05']['passed']} ({real_stats['p_value']:.6f})")
    print(f" Criterion 2: mean > 0 = {gate_result['criteria']['mean_positive']['passed']} ({real_stats['mean']:.4f})")
    print(f" Criterion 3: baseline p > 0.10 = {gate_result['criteria']['baseline_p_gt_0.10']['passed']} ({baseline_stats['null_p']:.4f})")
    print(f"\n GATE VERDICT: {'PASS' if gate_result['gate_passed'] else 'FAIL'}")

    results = {
        'hypothesis_id': 'H-M1',
        'hypothesis_type': 'MECHANISM',
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': time.time() - start_time,
        'n_conversations': len(trajectories),
        'n_valid_lag1': len(lag1_rs),
        'lag1_rs': lag1_rs,
        'multilag_results': multilag_results,
        'real_stats': real_stats,
        'effect_size': effect_size,
        'baseline_stats': baseline_stats,
        'length_stratification': length_strat,
        'gate_result': gate_result,
    }

    print("\n[6/6] Generating figures...")
    plot_lag_profile(multilag_results)
    plot_gate_pvalue(real_stats['p_value'])
    plot_lag1_histogram(lag1_rs)

    with open(RESULTS_PATH, 'wb') as f:
        pickle.dump(results, f)
    print(f"Results saved: {RESULTS_PATH}")

    json_results = {
        'hypothesis_id': 'H-M1',
        'gate_satisfied': gate_result['gate_passed'],
        'statistics': {
            'n': real_stats['n'],
            'mean_lag1_r': real_stats['mean'],
            'std': real_stats['std'],
            'p_value': real_stats['p_value'],
            'cohens_d': effect_size
        },
        'baseline': {
            'null_mean': baseline_stats['null_mean'],
            'null_p': baseline_stats['null_p']
        },
        'duration_seconds': results['duration_seconds']
    }

    json_path = os.path.join(os.path.dirname(OUTPUT_DIR), 'experiment_results.json')
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2)
    print(f"JSON results: {json_path}")

    print(f"\nExperiment completed in {results['duration_seconds']:.1f}s")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
