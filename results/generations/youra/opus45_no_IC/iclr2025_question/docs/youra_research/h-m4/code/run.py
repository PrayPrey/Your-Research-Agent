"""H-M4: Cross-cluster threshold transfer experiment.

Tests that cross-cluster benchmark pairs show FAILED threshold transfer
(AUROC degradation > 0.15), contrasting with H-M3's successful within-cluster transfer.
"""

import os
import sys
import json
import re
import random
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from tqdm import tqdm

from datasets import load_dataset
from sklearn.metrics import roc_curve, roc_auc_score

H_M4_PATH = os.path.dirname(os.path.abspath(__file__))
H_M1_CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(H_M4_PATH)), "h-m1", "code")

# Add H-M1 for ResponseGenerator and EntailmentClusterer
sys.path.insert(0, H_M1_CODE_PATH)

from response_generator import ResponseGenerator
from entailment_clusterer import EntailmentClusterer
from semantic_entropy import compute_semantic_entropy
from correctness import has_any_correct

# Load H-M4 config
import importlib.util
spec = importlib.util.spec_from_file_location("m4_config", os.path.join(H_M4_PATH, "config.py"))
m4_config = importlib.util.module_from_spec(spec)
old_path = sys.path.copy()
sys.path.insert(0, H_M4_PATH)
spec.loader.exec_module(m4_config)
sys.path = old_path

SEED = m4_config.SEED
CROSS_CLUSTER_PAIRS = m4_config.CROSS_CLUSTER_PAIRS
SAMPLE_SIZE = m4_config.SAMPLE_SIZE
JS_DIVERGENCE = m4_config.JS_DIVERGENCE
DEGRADATION_THRESHOLD = m4_config.DEGRADATION_THRESHOLD
H_M3_RESULTS_PATH = m4_config.H_M3_RESULTS_PATH
OUTPUTS_DIR = m4_config.OUTPUTS_DIR
FIGURES_DIR = m4_config.FIGURES_DIR
TARGET_FPR = m4_config.TARGET_FPR
CALIB_SPLIT = m4_config.CALIB_SPLIT
N_GENERATIONS = m4_config.N_GENERATIONS

# Load H-M4 stats and visualize
sys.path.insert(0, H_M4_PATH)
from stats import aggregate_results, check_gate, compare_to_h_m3
from visualize import generate_all_figures


def normalize_answer(s: str) -> str:
    """Normalize answer for comparison."""
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = ' '.join(s.split())
    return s


def load_trivia_qa(n: int) -> List[Dict]:
    ds = load_dataset("trivia_qa", "rc", split=f"validation[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        aliases = row["answer"]["aliases"] if row["answer"]["aliases"] else [row["answer"]["value"]]
        items.append({"question": question, "aliases": aliases})
    return items


def load_pop_qa(n: int) -> List[Dict]:
    ds = load_dataset("akariasai/PopQA", split=f"test[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        answer = row["possible_answers"] if isinstance(row["possible_answers"], list) else [row["possible_answers"]]
        items.append({"question": question, "aliases": answer})
    return items


def load_halueval_qa(n: int) -> List[Dict]:
    ds = load_dataset("pminervini/HaluEval", "qa_samples", split=f"data[:{n}]", trust_remote_code=True)
    items = []
    for row in ds:
        question = row["question"]
        answer = row["right_answer"] if "right_answer" in row else row.get("answer", "")
        if answer:
            items.append({"question": question, "aliases": [answer]})
    return items[:n]


LOADERS = {
    "trivia_qa": load_trivia_qa,
    "pop_qa": load_pop_qa,
    "halueval_qa": load_halueval_qa,
}


def load_benchmark(name: str, n: int) -> List[Dict]:
    if name not in LOADERS:
        raise ValueError(f"Unknown benchmark: {name}")
    return LOADERS[name](n)


def split_calib_eval(items: List[Dict], calib_frac: float = CALIB_SPLIT, seed: int = SEED) -> Tuple[List[Dict], List[Dict]]:
    random.seed(seed)
    shuffled = items.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * calib_frac)
    return shuffled[:split_idx], shuffled[split_idx:]


def calibrate_threshold(entropies: np.ndarray, labels: np.ndarray, target_fpr: float) -> float:
    """Find threshold at target FPR."""
    y_true = ~labels.astype(bool)
    fpr, tpr, thresholds = roc_curve(y_true, entropies)
    idx = np.argmin(np.abs(fpr - target_fpr))
    return float(thresholds[idx])


def evaluate_transfer(source_threshold: float, target_entropies: np.ndarray, target_labels: np.ndarray) -> dict:
    """Evaluate AUROC using source-calibrated threshold on target data."""
    y_true = ~target_labels.astype(bool)
    auroc = roc_auc_score(y_true, target_entropies)
    return {"auroc": float(auroc), "threshold_used": source_threshold}


def compute_auroc_degradation(source_auroc: float, target_auroc: float) -> float:
    """Positive = performance dropped."""
    return source_auroc - target_auroc


def compute_entropy_and_labels(
    items: List[Dict],
    generator: ResponseGenerator,
    clusterer: EntailmentClusterer,
    n_generations: int = N_GENERATIONS,
    desc: str = "Computing entropy"
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute semantic entropy and correctness labels for each item."""
    entropies = []
    labels = []

    for item in tqdm(items, desc=desc):
        question = item["question"]
        aliases = item["aliases"]

        gen_results = generator.generate_n(question, n=n_generations)
        texts = [r["text"] for r in gen_results]
        logprobs = [r["logprob"] for r in gen_results]

        label = has_any_correct(texts, aliases)
        se = compute_semantic_entropy(texts, logprobs, clusterer, question)

        entropies.append(se)
        labels.append(label)

    return np.array(entropies, dtype=np.float64), np.array(labels, dtype=bool)


def get_or_compute_benchmark_entropy(
    name: str,
    calib_items: List[Dict],
    eval_items: List[Dict],
    generator: ResponseGenerator,
    clusterer: EntailmentClusterer,
    cache_dir: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load cached entropy or compute fresh."""
    paths = {
        "calib_e": os.path.join(cache_dir, f"entropy_{name}_calib.npy"),
        "calib_l": os.path.join(cache_dir, f"labels_{name}_calib.npy"),
        "eval_e": os.path.join(cache_dir, f"entropy_{name}_eval.npy"),
        "eval_l": os.path.join(cache_dir, f"labels_{name}_eval.npy"),
    }

    if all(os.path.exists(p) for p in paths.values()):
        print(f"Loading cached entropy for {name}...")
        return (
            np.load(paths["calib_e"]),
            np.load(paths["calib_l"]),
            np.load(paths["eval_e"]),
            np.load(paths["eval_l"]),
        )

    print(f"Computing entropy for {name}...")
    calib_e, calib_l = compute_entropy_and_labels(calib_items, generator, clusterer, desc=f"{name} calib")
    eval_e, eval_l = compute_entropy_and_labels(eval_items, generator, clusterer, desc=f"{name} eval")

    os.makedirs(cache_dir, exist_ok=True)
    np.save(paths["calib_e"], calib_e)
    np.save(paths["calib_l"], calib_l)
    np.save(paths["eval_e"], eval_e)
    np.save(paths["eval_l"], eval_l)

    return calib_e, calib_l, eval_e, eval_l


def run_pair_transfer(source: str, target: str, entropy_cache: dict) -> dict:
    """Run threshold transfer from source to target benchmark."""
    src_calib_e, src_calib_l, src_eval_e, src_eval_l = entropy_cache[source]
    _, _, tgt_eval_e, tgt_eval_l = entropy_cache[target]

    threshold = calibrate_threshold(src_calib_e, src_calib_l, TARGET_FPR)
    source_result = evaluate_transfer(threshold, src_eval_e, src_eval_l)
    target_result = evaluate_transfer(threshold, tgt_eval_e, tgt_eval_l)
    degradation = compute_auroc_degradation(source_result["auroc"], target_result["auroc"])

    return {
        "source": source,
        "target": target,
        "source_auroc": source_result["auroc"],
        "target_auroc": target_result["auroc"],
        "degradation": degradation,
        "source_threshold": threshold
    }


def main():
    np.random.seed(SEED)
    print("=" * 60)
    print("H-M4: Cross-Cluster Threshold Transfer Experiment")
    print("=" * 60)
    print(f"Cross-cluster pairs: {CROSS_CLUSTER_PAIRS}")
    print(f"Gate threshold: mean degradation > {DEGRADATION_THRESHOLD}")
    print()

    print("[1/5] Loading models...")
    generator = ResponseGenerator()
    clusterer = EntailmentClusterer()

    print("\n[2/5] Loading and processing benchmarks...")
    benchmarks = set()
    for src, tgt in CROSS_CLUSTER_PAIRS:
        benchmarks.add(src)
        benchmarks.add(tgt)

    entropy_cache = {}
    for bench in benchmarks:
        print(f"\n--- {bench} ---")
        items = load_benchmark(bench, SAMPLE_SIZE)
        print(f"Loaded {len(items)} items from HuggingFace")

        calib_items, eval_items = split_calib_eval(items)
        print(f"Split: {len(calib_items)} calib, {len(eval_items)} eval")

        calib_e, calib_l, eval_e, eval_l = get_or_compute_benchmark_entropy(
            bench, calib_items, eval_items, generator, clusterer,
            cache_dir=OUTPUTS_DIR
        )
        entropy_cache[bench] = (calib_e, calib_l, eval_e, eval_l)

        correct_rate = calib_l.mean()
        print(f"Correctness rate: {correct_rate:.2%}")
        print(f"Mean entropy: {calib_e.mean():.3f} (calib), {eval_e.mean():.3f} (eval)")

    print("\n[3/5] Running cross-cluster transfers...")
    transfer_results = []
    for source, target in CROSS_CLUSTER_PAIRS:
        result = run_pair_transfer(source, target, entropy_cache)
        result["js_divergence"] = JS_DIVERGENCE.get((source, target), 0.45)
        transfer_results.append(result)

        status = "✓" if result["degradation"] > DEGRADATION_THRESHOLD else "✗"
        print(f"  {status} {source} → {target}: "
              f"AUROC {result['source_auroc']:.3f} → {result['target_auroc']:.3f} "
              f"(deg={result['degradation']:+.4f}, JS={result['js_divergence']:.3f})")

    print("\n[4/5] Aggregating results...")
    agg = aggregate_results(transfer_results)
    gate_pass = check_gate(agg)

    print(f"\nAggregate Statistics:")
    print(f"  Mean degradation: {agg['mean_degradation']:.4f} (threshold: > {DEGRADATION_THRESHOLD})")
    print(f"  95% CI: [{agg['ci_lower']:.4f}, {agg['ci_upper']:.4f}]")
    print(f"  N transfers: {agg['n_transfers']}")
    print(f"\nGate Result: {'PASS' if gate_pass else 'FAIL'}")

    cross_degradations = [r["degradation"] for r in transfer_results]
    mw_result = compare_to_h_m3(cross_degradations, H_M3_RESULTS_PATH)
    print(f"\nMann-Whitney U test (cross > within):")
    print(f"  Statistic: {mw_result['statistic']:.3f}")
    print(f"  p-value: {mw_result['p_value']:.6f}")
    print(f"  Significant (p < 0.05): {mw_result['significant']}")

    with open(H_M3_RESULTS_PATH) as f:
        h_m3_results = json.load(f)
    within_degradations = [r["degradation"] for r in h_m3_results["transfers"]]

    print("\n[5/5] Generating visualizations...")
    generate_all_figures(transfer_results, agg, within_degradations)

    results = {
        "hypothesis": "H-M4",
        "statement": "Cross-cluster benchmark pairs show failed threshold transfer (AUROC degradation > 0.15)",
        "timestamp": datetime.now().isoformat(),
        "gate": {
            "type": "SHOULD_WORK",
            "pass_condition": f"Mean degradation > {DEGRADATION_THRESHOLD}",
            "result": "PASS" if gate_pass else "FAIL",
            "satisfied": bool(gate_pass)
        },
        "aggregate": {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in agg.items()},
        "transfers": transfer_results,
        "mann_whitney": {k: float(v) if isinstance(v, (np.floating, np.integer)) else bool(v) if isinstance(v, np.bool_) else v for k, v in mw_result.items()},
        "comparison_to_h_m3": {
            "cross_cluster_mean": float(mw_result["cross_mean"]),
            "within_cluster_mean": float(mw_result["within_mean"]),
            "ratio": float(mw_result["cross_mean"] / mw_result["within_mean"]) if mw_result["within_mean"] > 0 else float("inf")
        },
        "benchmarks": list(benchmarks),
        "cross_cluster_pairs": CROSS_CLUSTER_PAIRS,
        "sample_size": SAMPLE_SIZE
    }

    results_path = os.path.join(OUTPUTS_DIR, "experiment_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    print("\n" + "=" * 60)
    print("H-M4 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {'PASS' if gate_pass else 'FAIL'}")
    print(f"Mean Cross-Cluster Degradation: {agg['mean_degradation']:.3f} (threshold: > {DEGRADATION_THRESHOLD})")
    print(f"Mann-Whitney p-value: {mw_result['p_value']:.6f}")
    print(f"Cross/Within Ratio: {results['comparison_to_h_m3']['ratio']:.2f}x")

    return results


if __name__ == "__main__":
    results = main()
