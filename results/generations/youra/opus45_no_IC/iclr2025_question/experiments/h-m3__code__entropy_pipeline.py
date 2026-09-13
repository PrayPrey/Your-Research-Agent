"""Entropy pipeline wrapping H-M1 components for H-M3."""

import os
import sys
import numpy as np
from typing import List, Dict, Tuple
from tqdm import tqdm

H_M1_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "h-m1", "code")
sys.path.insert(0, H_M1_PATH)

from response_generator import ResponseGenerator
from entailment_clusterer import EntailmentClusterer
from semantic_entropy import compute_semantic_entropy
from correctness import has_any_correct

from config import OUTPUTS_DIR, N_GENERATIONS


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
    cache_dir: str = OUTPUTS_DIR
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
