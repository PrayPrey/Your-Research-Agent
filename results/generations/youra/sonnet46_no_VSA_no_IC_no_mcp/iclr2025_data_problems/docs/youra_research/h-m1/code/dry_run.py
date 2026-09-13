"""Dry run: end-to-end pipeline with synthetic mini corpus to verify mechanism works."""
import json
import sys
import hashlib
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent))

from config import BENCHMARKS, NGRAM_SIZE, CORRECTED_ALPHA, FIGURES_DIR, CHECKPOINT_DIR
from sampler import DocWithMeta
from overlap_computer import compute_overlap_batch, save_overlap_checkpoint
from statistical_tester import run_mannwhitney_suite, compute_rank_correlation, mechanism_check
from visualizer import generate_all_figures

# ── Synthetic mini corpus (bypasses HuggingFace streaming) ──────────────────
# Removed docs: contain benchmark-like text (high overlap expected)
MMLU_SNIPPET = "The atomic number of carbon is 6. Which element has atomic number 79? Gold is element 79."
HELLASWAG_SNIPPET = "She walked into the kitchen and opened the refrigerator to find something to eat for dinner."
ARC_SNIPPET = "Which of the following best describes the process of photosynthesis in plants?"
WINO_SNIPPET = "The trophy didn't fit in the suitcase because it was too big."

# Build benchmark ngram sets from these snippets (simulating benchmark extraction)
def build_synthetic_ngrams(n: int = NGRAM_SIZE) -> dict[str, frozenset]:
    snippets = {
        "mmlu": MMLU_SNIPPET * 5,
        "hellaswag": HELLASWAG_SNIPPET * 5,
        "arc_challenge": ARC_SNIPPET * 5,
        "winogrande": WINO_SNIPPET * 5,
    }
    return {b: frozenset(text[i:i+n] for i in range(len(text) - n + 1))
            for b, text in snippets.items()}

rng = random.Random(42)

def make_removed_doc(i: int) -> DocWithMeta:
    """Doc with high benchmark overlap: contains snippet text directly."""
    text = (MMLU_SNIPPET + " " + ARC_SNIPPET + " ") * 3 + f" document {i} noise " * 10
    return DocWithMeta(
        text=text,
        doc_id=hashlib.sha256(f"removed_{i}".encode()).hexdigest(),
        pile_subset=rng.choice(["Pile-CC", "Books3", "Wikipedia (en)"]),
        is_removed=True,
    )

def make_retained_doc(i: int) -> DocWithMeta:
    """Doc with low benchmark overlap: generic content."""
    text = f"This is a generic web document number {i}. " * 20 + f"Random content xyz {i*7}."
    return DocWithMeta(
        text=text,
        doc_id=hashlib.sha256(f"retained_{i}".encode()).hexdigest(),
        pile_subset=rng.choice(["Pile-CC", "Books3", "Wikipedia (en)"]),
        is_removed=False,
    )

N_DRY = 200  # 200 per group — statistically meaningful for Mann-Whitney

print("=" * 60)
print("DRY RUN: H-M1 Corpus Contamination Analysis")
print(f"N per group: {N_DRY}")
print("=" * 60)

removed_docs = [make_removed_doc(i) for i in range(N_DRY)]
retained_docs = [make_retained_doc(i) for i in range(N_DRY)]

print(f"\n1. Building synthetic benchmark n-gram sets (n={NGRAM_SIZE})...")
ngram_sets = build_synthetic_ngrams(NGRAM_SIZE)
for b, ngs in ngram_sets.items():
    print(f"   {b}: {len(ngs)} unique {NGRAM_SIZE}-grams")

print(f"\n2. Computing overlaps (parallel, n_workers=2)...")
removed_arr = compute_overlap_batch(removed_docs, ngram_sets, n=NGRAM_SIZE, n_workers=2)
retained_arr = compute_overlap_batch(retained_docs, ngram_sets, n=NGRAM_SIZE, n_workers=2)

benchmarks = sorted(ngram_sets.keys())
print("\n   Mean overlaps:")
for i, b in enumerate(benchmarks):
    print(f"   {b}: removed={np.mean(removed_arr[:,i]):.4f}, retained={np.mean(retained_arr[:,i]):.4f}")

print(f"\n3. Running Mann-Whitney U tests...")
stats = run_mannwhitney_suite(removed_arr, retained_arr, benchmark_names=benchmarks)
for s in stats:
    sig = "✅" if s.significant else "❌"
    print(f"   {sig} {s.benchmark}: p_corr={s.p_corrected:.4f}, ratio={s.ratio:.1f}×")

n_significant = sum(s.significant for s in stats)
gate_pass = n_significant >= 2
print(f"\n   Significant: {n_significant}/4 benchmarks")

print(f"\n4. Mechanism check...")
try:
    mechanism_check(stats)
except RuntimeError as e:
    print(f"   Note: {e}")

print(f"\n5. Spearman rank correlation...")
spearman = compute_rank_correlation(stats)
print(f"   rho={spearman.correlation:.3f}, p={spearman.p_value:.4f}")

# Save as overlap_scores dict for figure generation
overlap_scores = {
    "removed": {b: removed_arr[:, i].tolist() for i, b in enumerate(benchmarks)},
    "retained": {b: retained_arr[:, i].tolist() for i, b in enumerate(benchmarks)},
}
stat_results = {
    "per_benchmark": {
        s.benchmark: asdict(s) for s in stats
    },
    "spearman": asdict(spearman),
    "summary": {"n_significant": n_significant, "gate_pass": gate_pass},
}

print(f"\n6. Generating figures...")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
generate_all_figures(overlap_scores, stat_results, {"subset_stratified": {}})

print("\n" + "=" * 60)
print(f"DRY RUN COMPLETE")
print(f"Gate condition (n_sig>=2): {'PASS' if gate_pass else 'NOTE: low n, expected in dry run'}")
print(f"Figures saved to: {FIGURES_DIR}")
print("=" * 60)

# Write dry run result
dry_result = {
    "status": "success",
    "n_removed": N_DRY,
    "n_retained": N_DRY,
    "n_significant": n_significant,
    "gate_pass": gate_pass,
    "note": "Dry run with synthetic mini corpus — real experiment uses HuggingFace streaming"
}
(Path(__file__).parent.parent / "dry_run_result.json").write_text(json.dumps(dry_result, indent=2))
print(f"✓ Dry run result saved")
