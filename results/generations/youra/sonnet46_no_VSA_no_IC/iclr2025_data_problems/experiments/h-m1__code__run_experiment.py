"""H-M1: Cognitive Task Pattern Proxies in The Pile — CLI entrypoint."""
from __future__ import annotations

import argparse
import json
import logging
import os
import pickle
import sys

import pandas as pd
from pathlib import Path

# Ensure code dir is on path
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    DOCS_PER_DOMAIN, FIGURES_DIR, FOCAL_DOMAINS, RESULTS_DIR, SEED,
    SPACY_MODEL,
)
from src.data.loader import sample_domains, stream_pile_hf, stream_pile_lmd
from src.proxies.compute import compute_domain_scores
from src.analysis.stats import (
    domain_summary_stats, evaluate_gate, tukey_hsd, welch_anova,
)
from src.visualization.figures import (
    plot_domain_proxy_comparison, plot_focal_domain_violins,
    plot_proxy_correlation_scatter, plot_tukey_heatmap,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="H-M1: Cognitive Task Pattern Proxies in The Pile"
    )
    p.add_argument(
        "--loader", choices=["hf", "lmd"], default="hf",
        help="Data source: HuggingFace streaming (hf) or local lm_dataformat (lmd)",
    )
    p.add_argument(
        "--data-path", default="",
        help="Path to val.jsonl.zst (required when --loader=lmd)",
    )
    p.add_argument(
        "--skip-sampling", action="store_true",
        help="Skip streaming/sampling; reuse results/domain_texts.pkl",
    )
    p.add_argument(
        "--skip-proxies", action="store_true",
        help="Skip proxy computation; reuse results/domain_scores.json",
    )
    p.add_argument(
        "--results-dir", default=RESULTS_DIR,
        help="Directory for intermediate and final results",
    )
    p.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING"],
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger(__name__)

    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = Path(FIGURES_DIR)
    figures_dir.mkdir(parents=True, exist_ok=True)

    texts_path = results_dir / "domain_texts.pkl"
    scores_path = results_dir / "domain_scores.json"

    # ── Step 1: Load/sample domain texts ─────────────────────────────────────
    if args.skip_sampling and texts_path.exists():
        log.info("Loading domain_texts from cache: %s", texts_path)
        with open(texts_path, "rb") as f:
            domain_texts = pickle.load(f)
    else:
        import spacy
        log.info("Loading spaCy tokenizer for min-token filtering...")
        nlp_tok = spacy.load(SPACY_MODEL, disable=["ner", "parser"])

        log.info("Streaming The Pile (%s loader)...", args.loader)
        if args.loader == "hf":
            stream = stream_pile_hf(seed=SEED)
        else:
            if not args.data_path:
                sys.exit("ERROR: --data-path required when --loader=lmd")
            stream = stream_pile_lmd(args.data_path, seed=SEED)

        domain_texts = sample_domains(
            stream,
            docs_per_domain=DOCS_PER_DOMAIN,
            min_tokens=100,
            nlp_tokenizer=nlp_tok,
            seed=SEED,
        )
        log.info(
            "Sampled %d domains, %d total docs",
            len(domain_texts),
            sum(len(v) for v in domain_texts.values()),
        )

        with open(texts_path, "wb") as f:
            pickle.dump(domain_texts, f)
        log.info("Saved domain_texts to %s", texts_path)

    # ── Step 2: Compute proxies ───────────────────────────────────────────────
    if args.skip_proxies and scores_path.exists():
        log.info("Loading domain_scores from cache: %s", scores_path)
        with open(scores_path) as f:
            domain_scores = json.load(f)
    else:
        log.info("Computing proxies (parallel)...")
        domain_scores = compute_domain_scores(domain_texts)

        with open(scores_path, "w") as f:
            json.dump(domain_scores, f)
        log.info("Saved domain_scores to %s", scores_path)

    # ── Step 3: Summary stats ─────────────────────────────────────────────────
    log.info("Computing summary statistics...")
    summary_df = domain_summary_stats(domain_scores)
    summary_df.to_csv(results_dir / "summary_stats.csv", index=False)

    # ── Step 4: Statistical analysis ─────────────────────────────────────────
    proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
    anova_results: dict[str, dict] = {}
    tukey_results: dict[str, object] = {}

    for proxy in proxies:
        proxy_scores = {d: scores[proxy] for d, scores in domain_scores.items()
                        if proxy in scores and len(scores[proxy]) > 0}
        log.info("Running Welch ANOVA for %s across %d domains...", proxy, len(proxy_scores))
        anova_results[proxy] = welch_anova(proxy_scores, proxy_name=proxy)
        log.info(
            "  F=%.3f, p=%.4e, eta²=%.4f",
            anova_results[proxy]["F"],
            anova_results[proxy]["p_value"],
            anova_results[proxy]["eta_squared"],
        )
        tukey_results[proxy] = tukey_hsd(proxy_scores)

    # Save ANOVA table
    anova_df = pd.DataFrame(anova_results).T
    anova_df.to_csv(results_dir / "statistical_results.csv")

    # ── Step 5: Gate evaluation ───────────────────────────────────────────────
    log.info("Evaluating gate...")
    gate_metrics = evaluate_gate(domain_scores, anova_results, tukey_results)

    with open(results_dir / "h_m1_results.json", "w") as f:
        json.dump(gate_metrics, f, indent=2, default=str)

    # ── Step 6: Figures ───────────────────────────────────────────────────────
    log.info("Generating figures...")

    plot_domain_proxy_comparison(
        summary_df,
        out_path=str(figures_dir / "domain_proxy_comparison.png"),
    )

    plot_focal_domain_violins(
        domain_scores,
        focal_domains=FOCAL_DOMAINS,
        out_path=str(figures_dir / "focal_domain_violins.png"),
    )

    plot_tukey_heatmap(
        tukey_results["entity_density"],
        out_path=str(figures_dir / "tukey_heatmap_entity_density.png"),
    )

    plot_proxy_correlation_scatter(
        domain_scores,
        out_path=str(figures_dir / "proxy_correlation_scatter.png"),
    )

    # ── Step 7: Report ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("H-M1 GATE EVALUATION")
    print("=" * 60)
    c1 = gate_metrics["criterion_1_entity_density"]
    c2 = gate_metrics["criterion_2_narrative_coherence"]
    print(f"Criterion 1 (entity_density wiki > books):")
    print(f"  Wikipedia mean: {c1['wiki_mean']:.4f}")
    print(f"  Books mean:     {c1['books_mean']:.4f}")
    print(f"  p-value:        {c1['p_value']:.4e}")
    print(f"  eta²:           {c1['eta_squared']:.4f}")
    print(f"  PASS: {c1['pass']}")
    print(f"\nCriterion 2 (narrative_coherence books > wiki):")
    print(f"  Books mean:     {c2['books_mean']:.4f}")
    print(f"  Wikipedia mean: {c2['wiki_mean']:.4f}")
    print(f"  p-value:        {c2['p_value']:.4e}")
    print(f"  PASS: {c2['pass']}")
    print("=" * 60)

    if gate_metrics["gate_pass"]:
        print("GATE PASS")
    else:
        print("GATE FAIL")
    print("=" * 60)


if __name__ == "__main__":
    main()
