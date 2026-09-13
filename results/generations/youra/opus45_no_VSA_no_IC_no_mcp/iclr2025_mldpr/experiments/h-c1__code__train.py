"""Pipeline orchestration for h-c1 domain-stratified correlation."""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CONFIG
from data import build_domain_dataset
from metrics import CorrelationAnalyzer, fisher_z_test
from evaluate import check_domain_pass, check_gate, summarize


def plot_domain_scatter(vision: dict, nlp: dict, out_path: str) -> None:
    """Two-panel scatter: Vision | NLP with regression lines and R annotations."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for ax, dom_dict, title in [(ax1, vision, "Vision"), (ax2, nlp, "NLP")]:
        ax.scatter(dom_dict["dnsi"], dom_dict["gap"], s=80, zorder=3)
        for name, x, y in zip(dom_dict["names"], dom_dict["dnsi"], dom_dict["gap"]):
            ax.annotate(name, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=9)

        slope, intercept = np.polyfit(dom_dict["dnsi"], dom_dict["gap"], 1)
        xs = np.linspace(min(dom_dict["dnsi"]) - 0.05, max(dom_dict["dnsi"]) + 0.05, 50)
        ax.plot(xs, slope * xs + intercept, "--", color="gray", alpha=0.7)

        ax.set_title(f"{title} (R={dom_dict['r_pearson']:.2f}, p={dom_dict['p_pearson']:.3f})")
        ax.set_xlabel("DNSI")
        ax.set_ylabel("Generalization Gap")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_domain_comparison(vision: dict, nlp: dict, out_path: str) -> None:
    """Bar chart comparing domain correlations with 95% CI error bars."""
    labels = ["Vision", "NLP"]
    rs = [vision["r_pearson"], nlp["r_pearson"]]

    errs_lower = [vision["r_pearson"] - vision["ci_95_lower"],
                  nlp["r_pearson"] - nlp["ci_95_lower"]]
    errs_upper = [vision["ci_95_upper"] - vision["r_pearson"],
                  nlp["ci_95_upper"] - nlp["r_pearson"]]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(labels, rs, yerr=[errs_lower, errs_upper], capsize=5, color=["steelblue", "coral"])
    ax.axhline(0, color="gray", linestyle=":", linewidth=1)
    ax.axhline(-0.3, color="red", linestyle="--", linewidth=1, alpha=0.5, label="Threshold |R|>0.3")
    ax.set_ylabel("Pearson R")
    ax.set_title("Domain Correlation Comparison")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_bootstrap_overlay(vision: dict, nlp: dict, out_path: str) -> None:
    """Overlaid histograms of bootstrap R distributions."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(vision["bootstrap_r"], bins=50, alpha=0.5, label="Vision", color="steelblue")
    ax.hist(nlp["bootstrap_r"], bins=50, alpha=0.5, label="NLP", color="coral")
    ax.axvline(vision["r_pearson"], color="steelblue", linestyle="--", label=f"Vision R={vision['r_pearson']:.2f}")
    ax.axvline(nlp["r_pearson"], color="coral", linestyle="--", label=f"NLP R={nlp['r_pearson']:.2f}")
    ax.set_xlabel("Bootstrap Pearson R")
    ax.set_ylabel("Frequency")
    ax.set_title("Bootstrap Distribution Comparison")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def generate_figures(vision: dict, nlp: dict, comparison: dict, out_dir: str) -> None:
    """Generate all visualization figures."""
    os.makedirs(out_dir, exist_ok=True)
    plot_domain_scatter(vision, nlp, os.path.join(out_dir, "domain_scatter.png"))
    plot_domain_comparison(vision, nlp, os.path.join(out_dir, "domain_comparison.png"))
    plot_bootstrap_overlay(vision, nlp, os.path.join(out_dir, "bootstrap_overlay.png"))


def run_pipeline() -> dict:
    """Run full h-c1 domain-stratified correlation analysis."""
    print("[DOMAIN] Building vision dataset...")
    v_names, v_dnsi, v_gap = build_domain_dataset("vision")
    print("[DOMAIN] Building NLP dataset...")
    n_names, n_dnsi, n_gap = build_domain_dataset("nlp")

    analyzer = CorrelationAnalyzer(CONFIG["n_bootstrap"], CONFIG["seed"])

    print(f"[DOMAIN] Analyzing vision domain with n={len(v_names)}...")
    vision = analyzer.analyze(v_dnsi, v_gap)
    vision.update({"names": v_names, "dnsi": v_dnsi.tolist(), "gap": v_gap.tolist()})

    print(f"[DOMAIN] Analyzing NLP domain with n={len(n_names)}...")
    nlp = analyzer.analyze(n_dnsi, n_gap)
    nlp.update({"names": n_names, "dnsi": n_dnsi.tolist(), "gap": n_gap.tolist()})

    print(f"[VISION] n={vision['n']} R={vision['r_pearson']:.3f} p={vision['p_pearson']:.3f} pass={check_domain_pass(vision)}")
    print(f"[NLP] n={nlp['n']} R={nlp['r_pearson']:.3f} p={nlp['p_pearson']:.3f} pass={check_domain_pass(nlp)}")

    comparison = fisher_z_test(vision["r_pearson"], vision["n"], nlp["r_pearson"], nlp["n"])
    gate = check_gate(vision, nlp, comparison)

    generate_figures(vision, nlp, comparison, CONFIG["figures_dir"])

    results = {
        "vision": vision,
        "nlp": nlp,
        "comparison": comparison,
        "gate": gate,
    }
    results["summary"] = summarize(results)

    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    results_path = os.path.join(CONFIG["results_dir"], "results.json")

    def json_serializer(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        return str(obj)

    with open(results_path, "w") as f:
        json.dump(results, f, default=json_serializer, indent=2)

    if gate["success"]:
        print(f"[DOMAIN] SUCCESS: R_vision={gate['vision_r']:.3f}, R_nlp={gate['nlp_r']:.3f}, both negative")
    else:
        print(f"[DOMAIN] FAILED: vision_pass={gate['vision_pass']}, nlp_pass={gate['nlp_pass']}, consistent={gate['consistent_direction']}")

    print(f"[GATE] success={gate['success']}")
    return results


if __name__ == "__main__":
    results = run_pipeline()
