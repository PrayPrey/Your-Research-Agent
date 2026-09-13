"""H-M1: Post-hoc statistical analysis of H-E1 benchmark scores."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE1_RESULTS_PATH = os.path.join(os.path.dirname(BASE), "h-e1", "experiment_results.json")
FIGURES_DIR = os.path.join(BASE, "figures")
RESULTS_OUT = os.path.join(BASE, "experiment_results.json")

PAIRS = [
    ("mistralai-Mistral-7B-Instruct-v0.1",  "HuggingFaceH4-zephyr-7b-alpha"),
    ("teknium-OpenHermes-2.5-Mistral-7B",   "HuggingFaceH4-zephyr-7b-beta"),
    ("allenai-tulu-2-7b",                   "allenai-tulu-2-dpo-7b"),
    ("meta-llama-Llama-2-7b-chat-hf",       "Intel-neural-chat-7b-v3-1"),
    ("openchat-openchat_3.5",               "berkeley-nest-Starling-LM-7B-alpha"),
    ("mistralai-Mistral-7B-Instruct-v0.3",  "Intel-neural-chat-7b-v3-3"),
]

BENCHMARKS = ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]

INLINE_SCORES = {
    "mistralai-Mistral-7B-Instruct-v0.1":  {"bbq": 0.43, "winogender_all": 0.55, "winogrande": 0.75, "truthfulqa_mc2": 0.5588},
    "HuggingFaceH4-zephyr-7b-alpha":       {"bbq": 0.38, "winogender_all": 0.65, "winogrande": 0.73, "truthfulqa_mc2": 0.5492},
    "teknium-OpenHermes-2.5-Mistral-7B":   {"bbq": 0.45, "winogender_all": 0.71, "winogrande": 0.74, "truthfulqa_mc2": 0.4916},
    "HuggingFaceH4-zephyr-7b-beta":        {"bbq": 0.39, "winogender_all": 0.65, "winogrande": 0.69, "truthfulqa_mc2": 0.5140},
    "allenai-tulu-2-7b":                   {"bbq": 0.45, "winogender_all": 0.63, "winogrande": 0.71, "truthfulqa_mc2": 0.4815},
    "allenai-tulu-2-dpo-7b":               {"bbq": 0.47, "winogender_all": 0.63, "winogrande": 0.71, "truthfulqa_mc2": 0.5782},
    "meta-llama-Llama-2-7b-chat-hf":       {"bbq": 0.42, "winogender_all": 0.66, "winogrande": 0.70, "truthfulqa_mc2": 0.4954},
    "Intel-neural-chat-7b-v3-1":           {"bbq": 0.47, "winogender_all": 0.67, "winogrande": 0.76, "truthfulqa_mc2": 0.5924},
    "openchat-openchat_3.5":               {"bbq": 0.48, "winogender_all": 0.67, "winogrande": 0.77, "truthfulqa_mc2": 0.4469},
    "berkeley-nest-Starling-LM-7B-alpha":  {"bbq": 0.48, "winogender_all": 0.69, "winogrande": 0.77, "truthfulqa_mc2": 0.4373},
    "mistralai-Mistral-7B-Instruct-v0.3":  {"bbq": 0.40, "winogender_all": 0.63, "winogrande": 0.76, "truthfulqa_mc2": 0.5591},
    "Intel-neural-chat-7b-v3-3":           {"bbq": 0.47, "winogender_all": 0.65, "winogrande": 0.73, "truthfulqa_mc2": 0.6382},
}


def load_scores(path):
    try:
        with open(path) as f:
            return json.load(f)["model_scores"]
    except (FileNotFoundError, KeyError):
        print(f"WARNING: {path} not found, using inline fallback.")
        return INLINE_SCORES


def compute_deltas(scores, pairs, benchmarks):
    deltas = {b: [] for b in benchmarks}
    for sft, dpo in pairs:
        for b in benchmarks:
            deltas[b].append(scores[dpo][b] - scores[sft][b])
    return {b: np.array(v) for b, v in deltas.items()}


def run_stats(deltas):
    try:
        from scipy.stats import binomtest
        def binom_p(k, n=6): return binomtest(k, n, 0.5, alternative="greater").pvalue
    except ImportError:
        from scipy.stats import binom
        def binom_p(k, n=6): return binom.sf(k - 1, n, 0.5)

    results = {}
    for bench, d in deltas.items():
        k = int(np.sum(d > 0))
        p = binom_p(k)
        results[bench] = {
            "deltas": d.tolist(),
            "k_positive": k,
            "mean_delta": float(np.mean(d)),
            "std_delta": float(np.std(d, ddof=1)),
            "p_value": float(p),
            "fisher": float(np.mean(d) ** 2 / (np.var(d, ddof=1) + 1e-8)),
        }
    return results


def gate_check(stats):
    k = stats["bbq"]["k_positive"]
    p = stats["bbq"]["p_value"]
    k_wg = stats["winogender_all"]["k_positive"]
    p_wg = stats["winogender_all"]["p_value"]
    passed = (k >= 4) and (p <= 0.125)
    return {
        "gate_pass": passed,
        "k_bbq": k, "p_bbq": p,
        "k_winogender": k_wg, "p_winogender": p_wg,
        "k_pass": k >= 4, "p_pass": p <= 0.125,
        "reason": f"k_BBQ={k}/6 ({'≥' if k>=4 else '<'}4), p_BBQ={p:.4f} ({'≤' if p<=0.125 else '>'}0.125)",
    }


def generate_figures(scores, pairs, deltas, stats, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    pair_labels = [f"P{i+1}" for i in range(6)]

    # Fig1: Paired bar — BBQ and WinoGender signed deltas
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, bench, title in zip(axes, ["bbq", "winogender_all"], ["BBQ", "WinoGender"]):
        d = deltas[bench]
        colors = ["tab:blue" if v > 0 else "tab:red" for v in d]
        ax.bar(pair_labels, d, color=colors)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{title} DPO−SFT delta")
        ax.set_xlabel("Pair"); ax.set_ylabel("DPO − SFT score")
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig1_bbq_winogender_paired_bar.png"), dpi=120)
    plt.close(fig)

    # Fig2: BBQ scatter DPO vs SFT
    sft_bbq = [scores[s]["bbq"] for s, _ in pairs]
    dpo_bbq = [scores[d]["bbq"] for _, d in pairs]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(sft_bbq, dpo_bbq, zorder=3)
    mn, mx = min(sft_bbq + dpo_bbq) - 0.01, max(sft_bbq + dpo_bbq) + 0.01
    ax.plot([mn, mx], [mn, mx], "k--", linewidth=0.8)
    for i, (xs, yd) in enumerate(zip(sft_bbq, dpo_bbq)):
        ax.annotate(f"P{i+1}", (xs, yd), textcoords="offset points", xytext=(4, 2), fontsize=8)
    ax.set_xlabel("SFT BBQ"); ax.set_ylabel("DPO BBQ")
    ax.set_title("BBQ: DPO vs SFT scores per pair")
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig2_bbq_scatter.png"), dpi=120)
    plt.close(fig)

    # Fig3: Fisher criterion all 4 dims
    bench_labels = ["BBQ", "WinoGender", "WinoGrande", "TruthfulQA"]
    bench_keys = ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]
    fishers = [stats[b]["fisher"] for b in bench_keys]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(bench_labels, fishers, color="steelblue")
    ax.set_ylabel("Fisher's criterion (μ²/σ²)")
    ax.set_title("Fisher's criterion — discriminative power per benchmark")
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig3_fisher_criterion.png"), dpi=120)
    plt.close(fig)

    # Fig4: WinoGender signed delta bar
    d = deltas["winogender_all"]
    colors = ["tab:blue" if v > 0 else "tab:red" for v in d]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(pair_labels, d, color=colors)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("WinoGender: DPO−SFT signed delta per pair")
    ax.set_xlabel("Pair"); ax.set_ylabel("DPO − SFT score")
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, "fig4_winogender_delta.png"), dpi=120)
    plt.close(fig)


def write_validation_report(scores, pairs, deltas, stats, gate, out_path):
    verdict = "PASS" if gate["gate_pass"] else "FAIL"
    bench_labels = {"bbq": "BBQ", "winogender_all": "WinoGender", "winogrande": "WinoGrande", "truthfulqa_mc2": "TruthfulQA MC2"}

    lines = [
        "# H-M1 Validation Report",
        "",
        f"**Gate Verdict: {verdict}**  ",
        f"k_BBQ = {gate['k_bbq']}/6 (threshold ≥4)  ",
        f"p_BBQ = {gate['p_bbq']:.4f} (threshold ≤0.125)  ",
        "",
        "## Gate Criteria",
        "",
        f"| Criterion | Value | Threshold | Pass |",
        f"|-----------|-------|-----------|------|",
        f"| k_BBQ (DPO>SFT pairs) | {gate['k_bbq']}/6 | ≥4 | {'✓' if gate['k_pass'] else '✗'} |",
        f"| p_BBQ (one-sided binomial) | {gate['p_bbq']:.4f} | ≤0.125 | {'✓' if gate['p_pass'] else '✗'} |",
        "",
        "## Per-Benchmark Statistics",
        "",
        "| Benchmark | k_positive | mean_delta | std_delta | p_value | Fisher |",
        "|-----------|-----------|------------|-----------|---------|--------|",
    ]
    for bk, bl in bench_labels.items():
        s = stats[bk]
        lines.append(f"| {bl} | {s['k_positive']}/6 | {s['mean_delta']:+.4f} | {s['std_delta']:.4f} | {s['p_value']:.4f} | {s['fisher']:.4f} |")

    lines += [
        "",
        "## Per-Pair Delta Table",
        "",
        "| Pair | SFT Model | DPO Model | BBQ Δ | WinoGender Δ | WinoGrande Δ | TruthfulQA Δ |",
        "|------|-----------|-----------|-------|--------------|--------------|--------------|",
    ]
    for i, (sft, dpo) in enumerate(pairs):
        row = f"| P{i+1} | {sft} | {dpo} |"
        for bk in ["bbq", "winogender_all", "winogrande", "truthfulqa_mc2"]:
            d = deltas[bk][i]
            row += f" {d:+.4f} |"
        lines.append(row)

    lines += [
        "",
        "## Figures",
        "",
        "- `figures/fig1_bbq_winogender_paired_bar.png` — Signed delta bars: BBQ and WinoGender per pair",
        "- `figures/fig2_bbq_scatter.png` — BBQ scatter: DPO vs SFT scores",
        "- `figures/fig3_fisher_criterion.png` — Fisher's criterion all 4 benchmarks",
        "- `figures/fig4_winogender_delta.png` — WinoGender signed delta per pair",
        "",
        "## Interpretation",
        "",
    ]

    if gate["gate_pass"]:
        lines += [
            f"Gate PASSED. DPO-trained models score higher than SFT counterparts on BBQ in {gate['k_bbq']}/6 pairs,",
            f"consistent with the hypothesis that DPO training systematically rewards bias-avoiding responses.",
            f"Secondary benchmark WinoGender shows k={gate['k_winogender']}/6 (p={gate['p_winogender']:.4f}), corroborating the BBQ finding.",
        ]
    else:
        lines += [
            f"Gate FAILED. k_BBQ={gate['k_bbq']}/6 or p_BBQ={gate['p_bbq']:.4f} did not meet thresholds.",
            "DPO advantage on bias benchmarks is not robustly demonstrated by this paired comparison.",
            f"WinoGender k={gate['k_winogender']}/6 (p={gate['p_winogender']:.4f}).",
        ]

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    print(f"Loading H-E1 scores from: {HE1_RESULTS_PATH}")
    scores = load_scores(HE1_RESULTS_PATH)
    print(f"Loaded {len(scores)} model entries.")

    deltas = compute_deltas(scores, PAIRS, BENCHMARKS)
    stats = run_stats(deltas)
    gate = gate_check(stats)

    print(f"\n=== Gate: {'PASS' if gate['gate_pass'] else 'FAIL'} ===")
    print(f"k_BBQ = {gate['k_bbq']}/6, p_BBQ = {gate['p_bbq']:.4f}")
    print(f"k_WinoGender = {gate['k_winogender']}/6, p_WinoGender = {gate['p_winogender']:.4f}")
    print("\nPer-benchmark stats:")
    for bk in BENCHMARKS:
        s = stats[bk]
        print(f"  {bk}: k={s['k_positive']}/6 mean_delta={s['mean_delta']:+.4f} p={s['p_value']:.4f} fisher={s['fisher']:.4f}")

    print(f"\nGenerating figures -> {FIGURES_DIR}")
    generate_figures(scores, PAIRS, deltas, stats, FIGURES_DIR)

    out_report = os.path.join(os.path.dirname(BASE), "h-m1", "04_validation.md")
    write_validation_report(scores, PAIRS, deltas, stats, gate, out_report)
    print(f"Report written: {out_report}")

    with open(RESULTS_OUT, "w") as f:
        json.dump({"benchmark_stats": stats, "gate": gate}, f, indent=2)
    print(f"Results saved: {RESULTS_OUT}")


if __name__ == "__main__":
    main()
