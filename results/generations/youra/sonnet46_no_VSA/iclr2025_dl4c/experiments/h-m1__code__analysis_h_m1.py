"""H-M1: Cross-Benchmark Rank Inversion Analysis (analysis-only, no new training).

Re-uses H-E2 SFT checkpoint evaluation data.
Gate: SHOULD_WORK — failure logs as limitation, does not stop pipeline.
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths (relative to project root; script must be run from project root)
# ---------------------------------------------------------------------------
H_E2_RESULTS_CSV = "docs/youra_research/h-e2/results/all_results.csv"
H_E2_FAST_EVAL_DIR = "docs/youra_research/h-e2/results/fast_eval"
H_M1_MBPP_RESULTS_CSV = "docs/youra_research/h-m1/results/mbpp_results.csv"  # pre-computed MBPP+
OUT_DIR = "docs/youra_research/h-m1/results"
FIGURES_DIR = "docs/youra_research/h-m1/figures"

CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
INVERSION_SEEDS = [42, 123, 777]


# ---------------------------------------------------------------------------
# Section 1: Data loading
# ---------------------------------------------------------------------------

def load_humaneval_scores(csv_path: str) -> dict:
    """Load HumanEval+ pass@1 from all_results.csv into {(cond, seed, 'humaneval'): float}."""
    df = pd.read_csv(csv_path)
    return {
        (row.condition, int(row.seed), row.benchmark): float(row.pass1)
        for row in df.itertuples()
    }


def score_mbpp_samples(fast_eval_dir: str, condition: str, seed: int,
                       evalplus_env: str = "youra-h-e2") -> float | None:
    """Run evalplus.evaluate --dataset mbpp on pre-generated samples.jsonl.

    Uses fast_eval directory where samples.jsonl already exist.
    Returns Base+Extra pass@1 or None on failure.
    """
    samples_path = Path(fast_eval_dir) / f"{condition}_seed{seed}_mbpp" / "samples.jsonl"
    if not samples_path.exists():
        print(f"  [WARN] samples.jsonl missing: {samples_path}")
        return None

    # Run evalplus in youra-h-e2 conda env (has evalplus 0.3.1)
    conda_prefix = Path(sys.executable).parent.parent
    # Try to find conda env with evalplus
    import shutil
    conda_exe = shutil.which("conda")
    if conda_exe is None:
        conda_exe = "/home/PrayPrey/miniforge3/bin/conda"

    cmd = [
        conda_exe, "run", "-n", evalplus_env, "--no-capture-output",
        "python", "-m", "evalplus.evaluate",
        "--dataset", "mbpp",
        "--samples", str(samples_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        # Parse "Base + Extra {'pass@1': 0.xxxx}"
        for line in output.splitlines():
            if "Base + Extra" in line and "pass@1" in line:
                # Extract float from line like: "Base + Extra {'pass@1': 0.3423}"
                try:
                    import re
                    m = re.search(r"pass@1['\"]?\s*:\s*([\d.]+)", line)
                    if m:
                        return float(m.group(1))
                except Exception:
                    pass
            # Also try "pass@1: 0.xxx" pattern
            if "pass@1" in line and "Extra" not in line and "Base" not in line:
                try:
                    import re
                    m = re.search(r"pass@1['\"]?\s*:\s*([\d.]+)", line)
                    if m:
                        return float(m.group(1))
                except Exception:
                    pass
        if result.returncode != 0:
            print(f"  [WARN] evalplus failed ({condition} seed {seed}): {output[-300:]}")
        else:
            print(f"  [WARN] evalplus output not parsed ({condition} seed {seed}): {output[-300:]}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  [WARN] evalplus timed out ({condition} seed {seed})")
        return None
    except Exception as e:
        print(f"  [WARN] evalplus error ({condition} seed {seed}): {e}")
        return None


def load_mbpp_scores(mbpp_csv: str) -> dict:
    """Load pre-computed MBPP+ pass@1 from h-m1/results/mbpp_results.csv."""
    p = Path(mbpp_csv)
    if not p.exists():
        print(f"  [INFO] {mbpp_csv} not found — will run evalplus")
        return {}
    df = pd.read_csv(mbpp_csv)
    return {
        (row.condition, int(row.seed), row.benchmark): float(row.pass1)
        for row in df.itertuples()
    }


def build_score_table(csv_path: str, fast_eval_dir: str,
                      mbpp_csv: str = None) -> dict:
    """Build complete score table: {(condition, seed, benchmark): float | None}.

    HumanEval+ scores come from h-e2 CSV; MBPP+ from pre-computed CSV or evalplus fallback.
    benchmark values: 'humaneval' | 'mbpp'
    """
    scores = load_humaneval_scores(csv_path)
    print(f"Loaded {len(scores)} HumanEval+ rows from CSV")

    # Try pre-computed MBPP+ first
    if mbpp_csv:
        mbpp_scores = load_mbpp_scores(mbpp_csv)
        if mbpp_scores:
            scores.update(mbpp_scores)
            print(f"Loaded {len(mbpp_scores)} pre-computed MBPP+ rows")
            return scores

    # Fallback: run MBPP+ evalplus for all conditions × seeds
    print("Scoring MBPP+ via evalplus (pre-generated samples)...")
    for cond in CONDITIONS:
        for seed in INVERSION_SEEDS:
            if (cond, seed, "mbpp") in scores:
                continue
            print(f"  Running evalplus MBPP: {cond} seed {seed} ...")
            val = score_mbpp_samples(fast_eval_dir, cond, seed)
            if val is not None:
                scores[(cond, seed, "mbpp")] = val
                print(f"    -> pass@1 = {val:.4f}")
            else:
                print(f"    -> FAILED (will be None)")

    return scores


# ---------------------------------------------------------------------------
# Section 2: Inversion checker
# ---------------------------------------------------------------------------

def check_inversion_per_seed(scores: dict, seed: int) -> dict:
    """Check rank inversion for one seed.

    Inversion pattern: HE-only > MBPP-only on HumanEval+  AND
                       MBPP-only > HE-only on MBPP+
    """
    he_on_he = scores.get(("humaneval_only", seed, "humaneval"))
    mb_on_he = scores.get(("mbpp_only", seed, "humaneval"))
    he_on_mb = scores.get(("humaneval_only", seed, "mbpp"))
    mb_on_mb = scores.get(("mbpp_only", seed, "mbpp"))

    missing = [k for k, v in {
        "he_on_he": he_on_he, "mb_on_he": mb_on_he,
        "he_on_mb": he_on_mb, "mb_on_mb": mb_on_mb,
    }.items() if v is None]

    if missing:
        return {"valid": False, "seed": seed, "missing": missing,
                "he_on_he": he_on_he, "mb_on_he": mb_on_he,
                "he_on_mb": he_on_mb, "mb_on_mb": mb_on_mb}

    inversion_he = he_on_he > mb_on_he
    inversion_mb = mb_on_mb > he_on_mb
    return {
        "valid": True,
        "seed": seed,
        "missing": [],
        "he_on_he": he_on_he,
        "mb_on_he": mb_on_he,
        "he_on_mb": he_on_mb,
        "mb_on_mb": mb_on_mb,
        "inversion_he_plus": inversion_he,
        "inversion_mbpp_plus": inversion_mb,
        "both_inverted": inversion_he and inversion_mb,
    }


def evaluate_h_m1_hypothesis(scores: dict, seeds: list) -> dict:
    """Test inversion across seeds. SHOULD_WORK: ≥2/3 valid seeds show full inversion."""
    seed_checks = [check_inversion_per_seed(scores, s) for s in seeds]
    valid = [c for c in seed_checks if c["valid"]]
    n_both = sum(1 for c in valid if c["both_inverted"])

    threshold = 2 / 3
    success = (n_both / len(valid) >= threshold) if valid else False

    note = ""
    if len(valid) < 2:
        note = f"Only {len(valid)} valid seed(s); conclusion tentative"

    return {
        "hypothesis": "H-M1",
        "success": success,
        "n_both_inverted": n_both,
        "n_valid": len(valid),
        "threshold": threshold,
        "fraction_inverted": n_both / len(valid) if valid else 0.0,
        "seed_checks": valid,
        "invalid_checks": [c for c in seed_checks if not c["valid"]],
        "gate": "SHOULD_WORK",
        "note": note,
    }


# ---------------------------------------------------------------------------
# Section 3: Figure generation
# ---------------------------------------------------------------------------

def plot_transfer_heatmap(scores: dict, out_dir: str) -> str:
    """2×4 heatmap: rows={HumanEval+, MBPP+}, cols=4 conditions, cell=mean pass@1."""
    rows = []
    for cond in CONDITIONS:
        for bm in ["humaneval", "mbpp"]:
            vals = [scores[(cond, s, bm)] for s in INVERSION_SEEDS
                    if (cond, s, bm) in scores]
            rows.append({
                "condition": cond.replace("_", "\n"),
                "benchmark": bm,
                "pass1": np.mean(vals) if vals else np.nan,
            })
    df = pd.DataFrame(rows)
    cond_labels = [c.replace("_", "\n") for c in CONDITIONS]
    pivot = df.pivot(index="benchmark", columns="condition", values="pass1")
    pivot = pivot.reindex(index=["humaneval", "mbpp"], columns=cond_labels)

    fig, ax = plt.subplots(figsize=(9, 3))
    try:
        import seaborn as sns
        sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlOrRd",
                    vmin=0, vmax=0.5, ax=ax, linewidths=0.5)
    except ImportError:
        im = ax.imshow(pivot.values.astype(float), cmap="YlOrRd",
                       vmin=0, vmax=0.5, aspect="auto")
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.values[i, j]
                ax.text(j, i, f"{val:.3f}" if not np.isnan(val) else "N/A",
                        ha="center", va="center", fontsize=9)
        ax.set_xticks(range(len(cond_labels)))
        ax.set_xticklabels(cond_labels, fontsize=8)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["HumanEval+", "MBPP+"], rotation=0)
        plt.colorbar(im, ax=ax)

    ax.set_title("H-M1: Transfer Matrix — Training Source × Evaluation Benchmark (mean pass@1)")
    ax.set_ylabel("")
    ax.set_yticklabels(["HumanEval+", "MBPP+"], rotation=0)
    plt.tight_layout()
    path = Path(out_dir) / "heatmap_pass1.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return str(path)


def plot_per_seed_inversion(seed_checks: list, out_dir: str, scores: dict) -> str:
    """Per-seed grouped bar chart: HE-only vs MBPP-only on HumanEval+ and MBPP+."""
    valid = [c for c in seed_checks if c["valid"]]
    if not valid:
        print("No valid seeds for per-seed plot")
        return ""

    n = len(valid)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4), sharey=False)
    if n == 1:
        axes = [axes]

    for ax, check in zip(axes, valid):
        seed = check["seed"]
        bms = ["HumanEval+", "MBPP+"]
        he_vals = [check["he_on_he"], check["he_on_mb"]]
        mb_vals = [check["mb_on_he"], check["mb_on_mb"]]
        x = np.arange(len(bms))
        w = 0.35
        ax.bar(x - w / 2, he_vals, w, label="HE-only", color="#2196F3", alpha=0.8)
        ax.bar(x + w / 2, mb_vals, w, label="MBPP-only", color="#FF9800", alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(bms)
        ax.set_ylabel("pass@1")
        ax.set_title(f"Seed {seed} | {'✓ Inverted' if check['both_inverted'] else '✗ Not inverted'}")
        ax.legend(fontsize=8)
        ax.set_ylim(0, max(max(he_vals + mb_vals) * 1.2, 0.1))

    plt.suptitle("H-M1: Per-Seed Rank Inversion (HE-only vs MBPP-only)")
    plt.tight_layout()
    path = Path(out_dir) / "per_seed_inversion.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return str(path)


def plot_delta_bar_chart(seed_checks: list, out_dir: str) -> str:
    """Delta bar: (HE-only − MBPP-only) per benchmark, per seed.

    Inversion = positive on HumanEval+, negative on MBPP+.
    """
    valid = [c for c in seed_checks if c["valid"]]
    if not valid:
        print("No valid seeds for delta plot")
        return ""

    seeds = [c["seed"] for c in valid]
    he_deltas = [c["he_on_he"] - c["mb_on_he"] for c in valid]
    mb_deltas = [c["he_on_mb"] - c["mb_on_mb"] for c in valid]

    x = np.arange(len(seeds))
    w = 0.35
    fig, ax = plt.subplots(figsize=(max(5, 2 * len(seeds)), 4))
    ax.bar(x - w / 2, he_deltas, w, label="HumanEval+ (pos = HE-only better)", color="#2196F3", alpha=0.8)
    ax.bar(x + w / 2, mb_deltas, w, label="MBPP+ (neg = MBPP-only better)", color="#FF9800", alpha=0.8)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Seed {s}" for s in seeds])
    ax.set_ylabel("HE-only − MBPP-only (pass@1)")
    ax.set_title("H-M1: Transfer Asymmetry Delta\n(inversion = +HE, −MBPP simultaneously)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    path = Path(out_dir) / "delta_bar_chart.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return str(path)


# ---------------------------------------------------------------------------
# Section 4: Reporter + Orchestrator
# ---------------------------------------------------------------------------

def save_result(hypothesis_result: dict, scores: dict, out_path: str) -> None:
    """Write hypothesis_result + scores summary to JSON."""
    # Serialize scores with string keys
    scores_summary = {}
    for cond in CONDITIONS:
        scores_summary[cond] = {}
        for seed in INVERSION_SEEDS:
            scores_summary[cond][str(seed)] = {
                "humaneval_plus": scores.get((cond, seed, "humaneval")),
                "mbpp_plus": scores.get((cond, seed, "mbpp")),
            }
    output = {**hypothesis_result, "scores": scores_summary}
    Path(out_path).write_text(json.dumps(output, indent=2))
    print(f"Result saved: {out_path}")


def main() -> dict:
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-M1: Cross-Benchmark Rank Inversion Analysis")
    print("=" * 60)

    # Step 1: Build score table (HumanEval+ from CSV, MBPP+ from pre-computed or evalplus)
    scores = build_score_table(H_E2_RESULTS_CSV, H_E2_FAST_EVAL_DIR,
                               mbpp_csv=H_M1_MBPP_RESULTS_CSV)

    # Step 2: Evaluate inversion hypothesis
    hypothesis_result = evaluate_h_m1_hypothesis(scores, INVERSION_SEEDS)

    # Step 3: Report
    print(f"\nResult: success={hypothesis_result['success']} "
          f"({hypothesis_result['n_both_inverted']}/{hypothesis_result['n_valid']} seeds inverted)")
    for c in hypothesis_result["seed_checks"]:
        inv_he = c.get("inversion_he_plus", "N/A")
        inv_mb = c.get("inversion_mbpp_plus", "N/A")
        both = c.get("both_inverted", "N/A")
        print(f"  Seed {c['seed']}: HE+={inv_he} MBPP+={inv_mb} both={both}"
              f" | he_on_he={c.get('he_on_he', 'N/A'):.3f}"
              f" mb_on_he={c.get('mb_on_he', 'N/A'):.3f}"
              f" he_on_mb={c.get('he_on_mb', 'N/A'):.3f}"
              f" mb_on_mb={c.get('mb_on_mb', 'N/A'):.3f}")
    for c in hypothesis_result["invalid_checks"]:
        print(f"  Seed {c['seed']}: INVALID (missing: {c['missing']})")

    if hypothesis_result["note"]:
        print(f"Note: {hypothesis_result['note']}")

    # Step 4: Save result JSON
    save_result(hypothesis_result, scores,
                str(Path(OUT_DIR) / "h_m1_result.json"))

    # Step 5: Generate figures
    figs = []
    try:
        figs.append(plot_transfer_heatmap(scores, FIGURES_DIR))
    except Exception as e:
        print(f"[WARN] heatmap failed: {e}")
    try:
        figs.append(plot_per_seed_inversion(
            hypothesis_result["seed_checks"] + hypothesis_result["invalid_checks"],
            FIGURES_DIR, scores))
    except Exception as e:
        print(f"[WARN] per-seed plot failed: {e}")
    try:
        figs.append(plot_delta_bar_chart(
            hypothesis_result["seed_checks"],
            FIGURES_DIR))
    except Exception as e:
        print(f"[WARN] delta bar failed: {e}")

    hypothesis_result["figures"] = [f for f in figs if f]

    if not hypothesis_result["success"]:
        print("\n[H-M1] SHOULD_WORK gate: inversion pattern absent — logging as limitation.")
    else:
        print("\n[H-M1] SHOULD_WORK gate: PASSED — inversion pattern confirmed.")

    return hypothesis_result


if __name__ == "__main__":
    result = main()
    assert isinstance(result["success"], bool), "success must be bool"
    print("Self-check OK")
