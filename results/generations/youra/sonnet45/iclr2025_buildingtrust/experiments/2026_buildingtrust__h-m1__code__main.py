"""H-M1: Main Orchestrator — Logit Delta Anisotropy Analysis.

Full pipeline:
1. Load datasets via H-E1 data_loader
2. Per pair: tokenizer compatibility check → run_pair_extraction (H-E1) → anisotropy analysis
3. Isotropic sanity check
4. Gate evaluation
5. Save figures
6. Save results
7. Print gate summary

Usage:
    export CUDA_VISIBLE_DEVICES=0
    python main.py
"""

import json
import logging
import os
import sys
from datetime import datetime

import numpy as np

# ─────────────────────────────────────────────────────────────
# Set up H-E1 code path BEFORE importing H-M1 modules
# ─────────────────────────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_HE1_CODE = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "h-e1", "code"))
if _HE1_CODE not in sys.path:
    sys.path.insert(0, _HE1_CODE)

# ─────────────────────────────────────────────────────────────
# H-M1 config
# ─────────────────────────────────────────────────────────────
from config import (
    MODEL_PAIRS,
    DATASETS,
    CACHE_DIR,
    FIGURES_DIR,
    SEED,
    GATE_THRESHOLDS,
    HYPOTHESIS_DIR,
)

from analysis_anisotropy import (
    run_anisotropy_analysis,
    evaluate_gate,
    run_isotropic_sanity_check,
    verify_mechanism_activated,
)
from visualization_anisotropy import save_all_figures

# H-E1 modules (via sys.path)
from data_loader import load_all_datasets
from model_runner import run_pair_extraction

# ─────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(_THIS_DIR, "experiment.log"), mode="a"),
    ],
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# A-2: Tokenizer Compatibility Check
# ─────────────────────────────────────────────────────────────

def verify_tokenizer_compatibility(pair_cfg: dict, n_pilot: int = 100) -> bool:
    """Load tokenizers for base+aligned; check token overlap for [' A',' B',' C',' D'].

    Also runs a pilot extraction to detect NaN/inf in logits.

    Args:
        pair_cfg: pair configuration dict with pair_id, base, aligned
        n_pilot: number of pilot items to test (default 100)

    Returns:
        True if compatible, False if mismatch (pair should be skipped)
    """
    try:
        from transformers import AutoTokenizer

        pair_id = pair_cfg["pair_id"]
        base_id = pair_cfg["base"]
        aligned_id = pair_cfg["aligned"]

        logger.info(f"Checking tokenizer compatibility for {pair_id}...")

        # Load tokenizers
        try:
            base_tok = AutoTokenizer.from_pretrained(base_id)
            aligned_tok = AutoTokenizer.from_pretrained(aligned_id)
        except Exception as e:
            logger.warning(f"  {pair_id}: Tokenizer load failed: {e}")
            return False

        # Check option token IDs for [' A', ' B', ' C', ' D']
        option_tokens = [" A", " B", " C", " D"]
        base_ids = []
        aligned_ids = []

        for tok_str in option_tokens:
            # Encode single token (no special tokens)
            b_ids = base_tok.encode(tok_str, add_special_tokens=False)
            a_ids = aligned_tok.encode(tok_str, add_special_tokens=False)
            base_ids.append(b_ids)
            aligned_ids.append(a_ids)

        # Check if same token IDs
        mismatch = False
        for tok_str, b, a in zip(option_tokens, base_ids, aligned_ids):
            if b != a:
                logger.warning(
                    f"  {pair_id}: Token ID mismatch for '{tok_str}': "
                    f"base={b}, aligned={a}"
                )
                mismatch = True

        if mismatch:
            logger.warning(f"  {pair_id}: Token ID mismatch detected — skipping pair")
            return False

        logger.info(f"  {pair_id}: Tokenizer compatible ✓")
        return True

    except Exception as e:
        logger.error(f"Tokenizer compatibility check failed for {pair_cfg['pair_id']}: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# Results Serialization (A-12)
# ─────────────────────────────────────────────────────────────

class NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy arrays and scalars."""

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def _serialize_pair_result(pair_result: dict) -> dict:
    """Serialize pair result, converting numpy arrays to lists."""
    serialized = {
        "pair_id": pair_result["pair_id"],
        "method": pair_result.get("method", "unknown"),
        "primary_ratio": float(pair_result["primary_ratio"]),
        "primary_p_value": float(pair_result["primary_p_value"]),
        "passes_gate": bool(pair_result["passes_gate"]),
        "datasets": {},
    }

    for ds_name, ds_result in pair_result.get("datasets", {}).items():
        serialized["datasets"][ds_name] = {
            "anisotropy_ratio": float(ds_result.get("anisotropy_ratio", 0)),
            "significance": {
                "t_stat": float(ds_result["significance"]["t_stat"]),
                "p_value": float(ds_result["significance"]["p_value"]),
                "is_significant": bool(ds_result["significance"]["is_significant"]),
            },
            "eigenvalues": ds_result["eigenvalues"].tolist() if isinstance(ds_result.get("eigenvalues"), np.ndarray) else [],
            "quintile_results": ds_result.get("quintile_results", []),
        }

    return serialized


def save_results(results: dict, hypothesis_dir: str) -> str:
    """Save experiment results as JSON.

    JSON schema: {gate, pairs, sanity, metadata}

    Args:
        results: full results dict with gate, pairs, sanity
        hypothesis_dir: h-m1/ directory path

    Returns:
        Path to saved JSON file
    """
    output_path = os.path.join(hypothesis_dir, "experiment_results.json")

    # Serialize pairs (numpy arrays → lists)
    serializable = {
        "gate": results.get("gate", {}),
        "pairs": [_serialize_pair_result(p) for p in results.get("pairs", [])],
        "sanity": results.get("sanity", {}),
        "metadata": {
            "hypothesis_id": "h-m1",
            "date": datetime.now().isoformat(),
            "seed": SEED,
        },
    }

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2, cls=NumpyEncoder)

    logger.info(f"Results saved to: {output_path}")
    return output_path


# ─────────────────────────────────────────────────────────────
# Gate Summary
# ─────────────────────────────────────────────────────────────

def print_gate_summary(results: dict) -> None:
    """Print formatted gate result and per-family summary.

    Args:
        results: full results dict with gate, pairs, sanity
    """
    gate = results.get("gate", {})
    pairs = results.get("pairs", [])
    sanity = results.get("sanity", {})

    print("\n" + "=" * 65)
    print("  H-M1 GATE EVALUATION SUMMARY")
    print("=" * 65)
    print(f"\n  Gate Result:     {gate.get('gate_result', 'N/A')}")
    print(f"  Families pass:   {gate.get('families_pass', 0)} / {gate.get('families_total', 0)}")
    print()
    print("  Per-pair results:")
    print(f"  {'Pair':<12} {'Method':<8} {'Ratio':>8} {'p-value':>10} {'Pass?':>7}")
    print("  " + "-" * 50)

    for pair_detail in gate.get("pair_details", []):
        pair_id = pair_detail["pair_id"]
        ratio = pair_detail["ratio"]
        p_value = pair_detail["p_value"]
        passed = pair_detail["passed"]
        # Find method
        method = ""
        for p in pairs:
            if p["pair_id"] == pair_id:
                method = p.get("method", "")
                break
        print(
            f"  {pair_id:<12} {method:<8} {ratio:>8.4f} {p_value:>10.4f} {'✓ PASS' if passed else '✗ FAIL':>7}"
        )

    print()
    print(f"  Sanity check (isotropic Gaussian):  "
          f"ratio={sanity.get('anisotropy_ratio', 0):.4f}  "
          f"≈1.0: {sanity.get('expected_approx_1', False)}")
    print("=" * 65 + "\n")


# ─────────────────────────────────────────────────────────────
# Main Pipeline
# ─────────────────────────────────────────────────────────────

def main() -> str:
    """Full H-M1 pipeline. Returns gate_result string ('PASS' or 'FAIL')."""
    logger.info("=" * 60)
    logger.info("H-M1: Logit Delta Anisotropy Analysis — Starting")
    logger.info("=" * 60)

    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    # ──────────────────────────────────────────
    # Step 1: Load datasets
    # ──────────────────────────────────────────
    logger.info("Loading datasets...")
    datasets = load_all_datasets(DATASETS)
    for ds_name, ds_items in datasets.items():
        logger.info(f"  {ds_name}: {len(ds_items)} items")

    # ──────────────────────────────────────────
    # Step 2: Per pair: tokenizer check + extraction + analysis
    # ──────────────────────────────────────────
    all_pair_results = []

    for pair_cfg in MODEL_PAIRS:
        pair_id = pair_cfg["pair_id"]
        logger.info(f"\n{'─'*50}")
        logger.info(f"Processing {pair_id} ({pair_cfg['method']})...")

        # Tokenizer compatibility check
        if not verify_tokenizer_compatibility(pair_cfg, n_pilot=100):
            logger.warning(f"Skipping {pair_id}: tokenizer incompatibility")
            continue

        # Run pair extraction (H-E1 function; uses cache if available)
        logger.info(f"Running pair extraction for {pair_id}...")
        try:
            datasets_logprobs = run_pair_extraction(
                pair_cfg, datasets, CACHE_DIR, DATASETS
            )
        except Exception as e:
            logger.error(f"Pair extraction failed for {pair_id}: {e}")
            continue

        # Verify extraction output
        if not datasets_logprobs:
            logger.warning(f"No logprobs extracted for {pair_id}, skipping")
            continue

        for ds_name, logprobs in datasets_logprobs.items():
            base_shape = logprobs.get("base", np.array([])).shape
            aligned_shape = logprobs.get("aligned", np.array([])).shape
            logger.info(f"  {ds_name}: base={base_shape}, aligned={aligned_shape}")

        # Anisotropy analysis
        logger.info(f"Running anisotropy analysis for {pair_id}...")
        try:
            pair_result = run_anisotropy_analysis(pair_cfg, datasets_logprobs)
            all_pair_results.append(pair_result)

            # Mechanism verification
            primary_ds = pair_result["datasets"].get(
                "mmlu", list(pair_result["datasets"].values())[0]
            )
            base_lp = list(datasets_logprobs.values())[0]["base"]
            aligned_lp = list(datasets_logprobs.values())[0]["aligned"]
            activated, indicators = verify_mechanism_activated(
                pair_id, base_lp, aligned_lp, pair_result
            )
            logger.info(f"  Mechanism activated: {activated}")
        except Exception as e:
            logger.error(f"Anisotropy analysis failed for {pair_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            continue

    if not all_pair_results:
        logger.error("No pair results obtained. Cannot evaluate gate.")
        gate = {
            "gate_result": "FAIL",
            "families_pass": 0,
            "families_total": 0,
            "pair_details": [],
        }
        full_results = {
            "gate": gate,
            "pairs": [],
            "sanity": {"anisotropy_ratio": 0.0, "expected_approx_1": False},
        }
        save_results(full_results, HYPOTHESIS_DIR)
        return "FAIL"

    # ──────────────────────────────────────────
    # Step 3: Isotropic sanity check
    # ──────────────────────────────────────────
    logger.info("\nRunning isotropic sanity check...")
    sanity = run_isotropic_sanity_check(n_items=1000, seed=SEED)
    logger.info(
        f"  Sanity: ratio={sanity['anisotropy_ratio']:.4f}, ≈1.0={sanity['expected_approx_1']}"
    )
    if not sanity["expected_approx_1"]:
        logger.warning(
            f"Sanity check warning: isotropic Gaussian ratio={sanity['anisotropy_ratio']:.4f} "
            f"outside [0.8, 1.5]"
        )

    # ──────────────────────────────────────────
    # Step 4: Gate evaluation
    # ──────────────────────────────────────────
    logger.info("\nEvaluating gate...")
    gate = evaluate_gate(all_pair_results, GATE_THRESHOLDS)
    logger.info(f"Gate result: {gate['gate_result']} ({gate['families_pass']}/{gate['families_total']})")

    # ──────────────────────────────────────────
    # Step 5: Save figures
    # ──────────────────────────────────────────
    logger.info("\nGenerating figures...")
    try:
        save_all_figures(all_pair_results, FIGURES_DIR)
    except Exception as e:
        logger.error(f"Figure generation failed: {e}")

    # ──────────────────────────────────────────
    # Step 6: Save results
    # ──────────────────────────────────────────
    full_results = {
        "gate": gate,
        "pairs": all_pair_results,
        "sanity": sanity,
    }
    save_results(full_results, HYPOTHESIS_DIR)

    # ──────────────────────────────────────────
    # Step 7: Print summary
    # ──────────────────────────────────────────
    print_gate_summary(full_results)

    logger.info(f"H-M1 pipeline complete. Gate: {gate['gate_result']}")
    return gate["gate_result"]


if __name__ == "__main__":
    import os
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    result = main()
    print(f"\nFinal gate result: {result}")
