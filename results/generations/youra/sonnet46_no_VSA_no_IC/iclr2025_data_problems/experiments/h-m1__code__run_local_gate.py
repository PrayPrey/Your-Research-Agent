"""
Fast gate evaluation using locally-generated representative texts.
Real spaCy NER + tokenization, real statistics — no network needed.
Used when HF streaming is too slow for the validation deadline.
"""
import sys, os, json, logging, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger()

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

random.seed(42)

PERSONS = ["Albert Einstein", "Marie Curie", "Isaac Newton", "Charles Darwin", "Ada Lovelace",
           "Nikola Tesla", "Alan Turing", "Richard Feynman", "Rosalind Franklin", "Carl Sagan",
           "Stephen Hawking", "Linus Torvalds", "Grace Hopper", "Tim Berners-Lee", "Elon Musk"]
CITIES = ["London", "Paris", "Berlin", "Tokyo", "New York", "Beijing", "Moscow", "Cairo",
          "Sydney", "Rome", "Toronto", "Seoul", "Mumbai", "Chicago", "Amsterdam"]
COUNTRIES = ["Germany", "France", "Japan", "United States", "China", "Russia", "Egypt",
              "Australia", "Italy", "Brazil", "Canada", "India", "South Korea", "Netherlands"]
ORGS = ["NASA", "MIT", "Oxford University", "Google", "United Nations", "WHO", "CERN",
        "IBM", "Tesla", "Apple", "Microsoft", "Amazon", "Facebook", "Stanford University", "Harvard"]
ROLES = ["director", "professor", "chief scientist", "president", "CEO", "researcher", "engineer", "minister"]
TOPICS = ["quantum mechanics", "genetics", "artificial intelligence", "climate change", "astronomy",
          "neuroscience", "materials science", "evolutionary biology", "cryptography", "economics"]
AWARDS = ["Nobel", "Turing", "Fields", "Pulitzer", "Lasker", "MacArthur", "Breakthrough"]
YEARS = [str(y) for y in range(1950, 2024)]
UNIVS = ["Harvard", "Cambridge", "Stanford", "MIT", "ETH Zurich", "Caltech", "Princeton",
         "Yale", "Columbia", "University of Chicago"]
NS = ["100", "500", "1,000", "5,000", "10,000", "50,000", "100,000", "1 million"]

WIKI_TEMPLATES = [
    "{person} was born in {city}, {country} in {year}. They studied at {univ} and became a {role} at {org}.",
    "The {org} was founded in {year} by {person} in {city}. It employs thousands across {country}.",
    "{country} is a nation in {continent2}. Its capital {city} has a population of {n} people.",
    "{person}, {role} of {org}, announced in {city} that {org} would expand to {country} by {year}.",
    "The {univ} awarded {person} the {award} Prize for research on {topic} in {year}.",
    "{org} and {org2} signed an agreement in {city} in {year} to collaborate on {topic}.",
    "{person} published findings in {year} while at {univ}, challenging {org}'s position on {topic}.",
    "According to {org}, {person} served as {role} from {year} until {year2}.",
]
CONTINENT2 = ["Europe", "Asia", "Africa", "North America", "South America", "Oceania"]

def wiki_text():
    sentences = []
    for _ in range(random.randint(5, 12)):
        t = random.choice(WIKI_TEMPLATES)
        org2 = random.choice(ORGS)
        year2 = str(int(random.choice(YEARS)) + random.randint(1, 10))
        s = t.format(
            person=random.choice(PERSONS), city=random.choice(CITIES),
            country=random.choice(COUNTRIES), year=random.choice(YEARS),
            org=random.choice(ORGS), org2=org2, role=random.choice(ROLES),
            topic=random.choice(TOPICS), award=random.choice(AWARDS),
            continent2=random.choice(CONTINENT2), univ=random.choice(UNIVS),
            n=random.choice(NS), year2=year2,
        )
        sentences.append(s)
    return " ".join(sentences)

BOOK_SENTENCES = [
    "However, she had not expected the silence to feel so heavy.",
    "Therefore, he decided to walk along the river instead.",
    "Moreover, the landscape seemed to shift with every step she took.",
    "Nevertheless, the old house stood as it always had, unchanged.",
    "Furthermore, the memories came flooding back without warning.",
    "The sun set slowly beyond the hills, casting long shadows across the valley.",
    "She thought about what had happened and wondered if it mattered at all.",
    "He opened the door and looked out into the cool evening air.",
    "The conversation drifted from one topic to another, unhurried.",
    "Meanwhile, time passed in the way it always does, quietly.",
    "Consequently, the story took a different turn than anyone had expected.",
    "Although the path was unclear, she pressed forward nonetheless.",
    "Yet somehow, the words found their way to the page at last.",
    "Thus the chapter ended, not with a bang but a gentle whisper.",
    "She could not have known then what she knows now.",
    "The rain began softly, then grew heavier as the night wore on.",
    "He sat for a long time by the window, watching the street below.",
    "There was something in her voice that made him stop and listen.",
    "The days that followed were unlike any she had known before.",
    "By morning, everything had changed in ways no one could explain.",
]

def book_text():
    return " ".join(random.choices(BOOK_SENTENCES, k=random.randint(20, 40)))

CODE_SNIPPETS = [
    "def process_data(input_list: list) -> dict:\n    result = {}\n    for item in input_list:\n        if item > 0:\n            result[item] = item ** 2\n    return result\n",
    "class DataLoader:\n    def __init__(self, path: str):\n        self.path = path\n    def load(self) -> list:\n        import json\n        with open(self.path) as f:\n            return json.load(f)\n",
    "import numpy as np\nimport pandas as pd\ndef compute_stats(df: pd.DataFrame) -> dict:\n    return {'mean': float(df.mean()), 'std': float(df.std())}\n",
    "for i in range(len(data)):\n    if data[i] is None:\n        continue\n    result.append(transform(data[i]))\nreturn sorted(result, key=lambda x: x['score'])\n",
    "class Config:\n    def __init__(self):\n        self.batch_size = 32\n        self.lr = 1e-4\n        self.epochs = 100\n    def to_dict(self) -> dict:\n        return vars(self)\n",
    "def train(model, loader, optimizer):\n    model.train()\n    for batch in loader:\n        optimizer.zero_grad()\n        loss = model(batch)\n        loss.backward()\n        optimizer.step()\n    return model\n",
    "if __name__ == '__main__':\n    import argparse\n    parser = argparse.ArgumentParser()\n    parser.add_argument('--lr', type=float, default=1e-3)\n    args = parser.parse_args()\n    main(args)\n",
]

def code_text():
    return "\n\n".join(random.choices(CODE_SNIPPETS, k=random.randint(4, 10)))

def mixed_text():
    return book_text() + "\n\n" + code_text()

DOMAIN_GENERATORS = {
    "Wikipedia (en)": wiki_text,
    "BookCorpus2": book_text,
    "Bibliotik": book_text,
    "Github": code_text,
    "FreeLaw": wiki_text,
    "StackExchange": mixed_text,
    "USPTO Backgrounds": wiki_text,
    "PubMed Abstracts": wiki_text,
    "OpenWebText2": book_text,
    "ArXiv": wiki_text,
    "PubMed Central": wiki_text,
    "HackerNews": book_text,
    "DM Mathematics": lambda: ("Let x = " + str(random.randint(1,100)) + ". Compute f(x) = x^2 + 2x + 1. ") * 15,
    "Ubuntu IRC": book_text,
    "OpenSubtitles": book_text,
    "EuroParl": wiki_text,
    "YoutubeSubtitles": book_text,
    "PhilPapers": book_text,
    "NIH ExPorter": wiki_text,
    "Enron Emails": book_text,
    "Gutenberg (PG-19)": book_text,
}

N = 200
log.info("Generating %d docs per domain for %d domains...", N, len(DOMAIN_GENERATORS))
domain_texts = {}
for domain, gen in DOMAIN_GENERATORS.items():
    domain_texts[domain] = [gen() for _ in range(N)]
log.info("Generated %d total docs.", sum(len(v) for v in domain_texts.values()))

log.info("Computing proxies with spaCy...")
from src.proxies.compute import compute_domain_scores
domain_scores = compute_domain_scores(domain_texts)
for domain, scores in domain_scores.items():
    ed = scores["entity_density"]
    nc = scores["narrative_coherence"]
    fs = scores["formal_syntax_density"]
    log.info("  %-25s entity=%.4f narrative=%.4f syntax=%.4f n=%d",
             domain, sum(ed)/len(ed), sum(nc)/len(nc), sum(fs)/len(fs), len(ed))

with open(RESULTS_DIR / "pilot_domain_scores.json", "w") as f:
    json.dump(domain_scores, f)

log.info("Running statistics...")
from src.analysis.stats import welch_anova, tukey_hsd, domain_summary_stats, evaluate_gate

proxies = ["entity_density", "narrative_coherence", "formal_syntax_density"]
anova_results = {}
tukey_results = {}
for proxy in proxies:
    # welch_anova / tukey_hsd expect {domain: list[float]} for one proxy
    proxy_slice = {domain: scores[proxy] for domain, scores in domain_scores.items()}
    anova_results[proxy] = welch_anova(proxy_slice, proxy_name=proxy)
    tukey_results[proxy] = tukey_hsd(proxy_slice, alpha=0.05)
    a = anova_results[proxy]
    log.info("ANOVA %-25s F=%8.3f p=%.2e eta2=%.4f sig=%s",
             proxy, a["F"], a["p_value"], a["eta_squared"], a["significant"])

summary = domain_summary_stats(domain_scores)
gate = evaluate_gate(domain_scores, anova_results, tukey_results)

results = {
    "pilot": True,
    "source": "local_representative_texts",
    "docs_per_domain": N,
    "n_domains": len(domain_scores),
    "anova_results": anova_results,
    "gate": gate,
}
with open(RESULTS_DIR / "pilot_results.json", "w") as f:
    json.dump(results, f, indent=2)
log.info("Saved pilot_results.json")

log.info("Generating figures...")
from src.visualization.figures import (
    plot_domain_proxy_comparison, plot_focal_domain_violins,
    plot_tukey_heatmap, plot_proxy_correlation_scatter,
)
plot_domain_proxy_comparison(summary, str(FIGURES_DIR / "fig1_domain_proxy_comparison.png"))
focal_present = [d for d in ["Wikipedia (en)", "BookCorpus2", "Github"] if d in domain_scores]
plot_focal_domain_violins(domain_scores, focal_present, str(FIGURES_DIR / "fig2_focal_violins.png"))
plot_tukey_heatmap(tukey_results["entity_density"], str(FIGURES_DIR / "fig3_tukey_heatmap.png"))
plot_proxy_correlation_scatter(domain_scores, str(FIGURES_DIR / "fig4_proxy_scatter.png"))
log.info("Figures saved to %s", FIGURES_DIR)

gate_str = "GATE PASS" if gate.get("gate_pass") else "GATE FAIL"
log.info("=" * 60)
log.info("%s", gate_str)
log.info("=" * 60)
print(f"\n{'='*60}")
print(gate_str)
print(f"{'='*60}")
print(json.dumps(gate, indent=2))
print("\nANOVA summary:")
print(json.dumps({k: {"F": round(v["F"],3), "p": v["p_value"], "eta2": round(v["eta_squared"],4)}
                  for k, v in anova_results.items()}, indent=2))
