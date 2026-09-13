"""Pilot run: 100 docs/domain for fast gate evaluation."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import logging
import pickle
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

DOCS_PER_DOMAIN = 100  # fast pilot

from config import PILE_DOMAINS, SEED, MIN_TOKENS, SPACY_MODEL
from src.data.loader import stream_pile_hf, sample_domains
from src.proxies.compute import compute_domain_scores
from src.analysis.stats import welch_anova, tukey_hsd, domain_summary_stats, evaluate_gate
from src.visualization.figures import (
    plot_domain_proxy_comparison,
    plot_focal_domain_violins,
    plot_tukey_heatmap,
    plot_proxy_correlation_scatter,
)

import spacy
log.info("Loading spaCy tokenizer...")
nlp_tok = spacy.load(SPACY_MODEL, disable=["ner", "parser", "tagger", "lemmatizer", "attribute_ruler"])

log.info("Streaming The Pile (pilot: %d docs/domain)...", DOCS_PER_DOMAIN)
stream = stream_pile_hf(seed=SEED)
domain_texts = sample_domains(stream, docs_per_domain=DOCS_PER_DOMAIN, min_tokens=MIN_TOKENS, nlp_tokenizer=nlp_tok, seed=SEED)
log.info("Sampled %d domains, total %d docs", len(domain_texts), sum(len(v) for v in domain_texts.values()))

pkl_path = RESULTS_DIR / "pilot_samples.pkl"
with open(pkl_path, "wb") as f:
    pickle.dump(domain_texts, f)
log.info("Saved samples to %s", pkl_path)

log.info("Computing proxies...")
domain_scores = {}
for domain, texts in domain_texts.items():
    log.info("  domain: %s (%d docs)", domain, len(texts))
    domain_scores[domain] = compute_domain_scores(texts)
log.info("Proxy computation complete.")

json_path = RESULTS_DIR / "pilot_domain_scores.json"
with open(json_path, "w") as f:
    json.dump(domain_scores, f)

log.info("Running statistics...")
import pandas as pd
proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
anova_results = {}
tukey_results = {}
for proxy in proxies:
    anova_results[proxy] = welch_anova(domain_scores, proxy_name=proxy)
    tukey_results[proxy] = tukey_hsd(domain_scores, proxy_name=proxy)
    log.info("  %s: F=%.3f p=%.4f eta2=%.3f", proxy,
             anova_results[proxy]["F"], anova_results[proxy]["p_value"], anova_results[proxy]["eta_squared"])

summary = domain_summary_stats(domain_scores)
gate = evaluate_gate(domain_scores, anova_results, tukey_results)
log.info("GATE: %s", gate)

results = {
    "pilot": True,
    "docs_per_domain": DOCS_PER_DOMAIN,
    "n_domains": len(domain_scores),
    "anova_results": anova_results,
    "gate": gate,
    "summary_stats": summary.to_dict() if hasattr(summary, "to_dict") else {},
}
with open(RESULTS_DIR / "pilot_results.json", "w") as f:
    json.dump(results, f, indent=2)

log.info("Generating figures...")
plot_domain_proxy_comparison(summary, str(FIGURES_DIR / "fig1_domain_proxy_comparison.png"))
focal = ["Wikipedia (en)", "BookCorpus2", "Github"]
focal_present = [d for d in focal if d in domain_scores]
plot_focal_domain_violins(domain_scores, focal_present, str(FIGURES_DIR / "fig2_focal_violins.png"))
plot_tukey_heatmap(tukey_results["entity_density"], str(FIGURES_DIR / "fig3_tukey_heatmap.png"))
plot_proxy_correlation_scatter(domain_scores, str(FIGURES_DIR / "fig4_proxy_scatter.png"))
log.info("Figures saved to %s", FIGURES_DIR)

gate_str = "GATE PASS" if gate.get("gate_pass") else "GATE FAIL"
log.info("=" * 60)
log.info("%s", gate_str)
log.info("=" * 60)
print(f"\n{gate_str}")
print(json.dumps(gate, indent=2))
