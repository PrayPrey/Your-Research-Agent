---
hypothesis_id: H-M1
phase: logic
date: 2026-08-20
author: yoon303b@gmail.com
---

# Logic Design: H-M1 — Cognitive Task Pattern Proxies in The Pile

Applied: N/A — Archon KB not indexed for this domain (image-gen content only; similarity < 0.45 for all NLP corpus analysis queries)

---

## Codebase Analysis (Serena)

Green-field: code directory `docs/youra_research/h-m1/code/` not yet created. H-E1 loader.py (MMapIndexedDataset/Pythia checkpoint) was examined but contains no importable modules applicable to this NLP content analysis pipeline. H-M1 is standalone.

---

## Data Flow

```
The Pile (HF streaming / lm_dataformat)
    ↓ stream_pile_hf() / stream_pile_lmd()
Raw (text, domain) pairs
    ↓ is_english() + min-token filter
    ↓ sample_domains()
{domain: [text, ...]} — 1000 docs × 22 domains
    ↓ compute_domain_scores()  [Pool.imap_unordered]
        ↓ compute_proxies()  [per worker]
{domain: {proxy: [float, ...]}}
    ↓ domain_summary_stats()
summary DataFrame (mean, std, 95% CI per domain per proxy)
    ↓ welch_anova()  [per proxy]
{proxy: {F, p_value, eta_squared}}
    ↓ tukey_hsd()  [per proxy]
{proxy: TukeyHSDResults}
    ↓ evaluate_gate()
{gate_pass: bool, entity_density_wiki_mean, ...}
    ↓ plot_*()  [4 figures]
figures/*.png
```

---

## Subtasks

### L-2-1: stream_pile_hf()

**Parent Epic:** A-2 (Data Loader, complexity 13)

```python
from datasets import load_dataset
from typing import Iterator

def stream_pile_hf(seed: int = 42) -> Iterator[tuple[str, str]]:
    """
    Yields (text, domain) from HuggingFace streaming Pile validation split.

    Args:
        seed: Random seed for shuffle buffer (applied server-side via buffer_size)
    Yields:
        (text: str, domain: str) — domain from meta['pile_set_name']
    Raises:
        RuntimeError: if dataset unavailable or pile_set_name missing from meta
    """
    ds = load_dataset(
        "EleutherAI/pile",
        split="validation",
        streaming=True,
    )
    ds = ds.shuffle(seed=seed, buffer_size=10_000)
    for row in ds:
        text = row.get("text", "")
        domain = row.get("meta", {}).get("pile_set_name", "")
        if text and domain:
            yield text, domain

# Self-check
if __name__ == "__main__":
    gen = stream_pile_hf()
    text, domain = next(gen)
    assert isinstance(text, str) and len(text) > 0, "text must be non-empty string"
    assert isinstance(domain, str) and len(domain) > 0, "domain must be non-empty string"
    print("L-2-1 self-check PASS")
```

---

### L-2-2: sample_domains()

**Parent Epic:** A-2 (Data Loader, complexity 13)

```python
from collections import defaultdict
import random
import spacy
from typing import Iterator

def sample_domains(
    stream: Iterator[tuple[str, str]],
    docs_per_domain: int = 1000,
    min_tokens: int = 100,
    nlp_tokenizer=None,
    seed: int = 42,
) -> dict[str, list[str]]:
    """
    Stratified sampling from stream. Stops per-domain once quota filled.
    Continues streaming until all domains filled or stream exhausted.

    Args:
        stream: Iterator of (text, domain) pairs
        docs_per_domain: Target sample size per domain
        min_tokens: Minimum spaCy token count (rejects short docs)
        nlp_tokenizer: spaCy Language object with tokenizer (for len check)
        seed: Random seed (applied to Python random for reproducibility)
    Returns:
        {domain: [text, ...]} with len <= docs_per_domain per domain
    Notes:
        - Logs WARNING if any domain exhausted before quota met
        - Uses only tokenizer component (not full NER pipeline) for speed
    """
    random.seed(seed)
    bucket: dict[str, list[str]] = defaultdict(list)
    full: set[str] = set()

    for text, domain in stream:
        if domain in full:
            continue
        # Fast token length check (tokenizer only, not full pipeline)
        if nlp_tokenizer is not None:
            tok = nlp_tokenizer(text[:5000])  # sample first 5k chars for speed
            if len(tok) < min_tokens:
                continue
        if not is_english(text):
            continue
        bucket[domain].append(text)
        if len(bucket[domain]) >= docs_per_domain:
            full.add(domain)
        # Stop when all known domains are full (requires knowing domain set in advance)
        # Caller checks completeness after return

    for domain, docs in bucket.items():
        if len(docs) < docs_per_domain:
            import logging
            logging.warning(
                f"Domain '{domain}' exhausted at {len(docs)}/{docs_per_domain} docs"
            )

    return dict(bucket)

# Self-check
if __name__ == "__main__":
    fake_stream = [("Hello world this is a test document " * 20, "Wikipedia (en)")] * 5
    result = sample_domains(iter(fake_stream), docs_per_domain=3, min_tokens=5)
    assert "Wikipedia (en)" in result
    assert len(result["Wikipedia (en)"]) == 3
    print("L-2-2 self-check PASS")
```

---

### L-3-1: load_nlp()

**Parent Epic:** A-3 (Proxy Computation, complexity 14)

```python
import spacy
from typing import Optional

_NLP_SINGLETON: Optional[spacy.Language] = None

def load_nlp(model: str = "en_core_web_sm") -> spacy.Language:
    """
    Load spaCy model with module-level singleton (safe for fork-based Pool).
    Workers call this at first use; no cross-process object passing.

    Args:
        model: spaCy model name
    Returns:
        spaCy Language object with NER + tokenizer
    Raises:
        OSError: if model not installed (run: python -m spacy download en_core_web_sm)
    """
    global _NLP_SINGLETON
    if _NLP_SINGLETON is None:
        _NLP_SINGLETON = spacy.load(model)
    return _NLP_SINGLETON
```

---

### L-3-2: compute_proxies()

**Parent Epic:** A-3 (Proxy Computation, complexity 14)

```python
import re
from config import CONNECTIVES, FORMAL_SYNTAX_PATTERN, MAX_CHARS

FORMAL_SYNTAX_RE = re.compile(FORMAL_SYNTAX_PATTERN)

def compute_proxies(text: str) -> dict[str, float]:
    """
    Compute 3 cognitive task pattern proxies for a single document.

    Args:
        text: Raw document string from The Pile (any length)
    Returns:
        {
          "entity_density": float,       # NER ents / tokens
          "narrative_coherence": float,  # connective words / tokens
          "formal_syntax_density": float # regex matches / tokens
        }
    Notes:
        - Truncates to MAX_CHARS (50_000) before processing
        - Denominator is max(n_non_space_tokens, 1) to avoid div-by-zero
        - spaCy loaded via module singleton (load_nlp called once per worker)
    """
    nlp = load_nlp()
    text_trunc = text[:MAX_CHARS]
    doc = nlp(text_trunc)

    tokens = [tok for tok in doc if not tok.is_space]
    n_tokens = max(len(tokens), 1)

    # Proxy 1: entity density (factual-association — Wikipedia proxy)
    entity_density = len(doc.ents) / n_tokens

    # Proxy 2: narrative coherence (discourse connectives — Books proxy)
    words_lower = {tok.lower_ for tok in tokens}
    connective_count = len(words_lower & CONNECTIVES)
    narrative_coherence = connective_count / n_tokens

    # Proxy 3: formal syntax density (bracket/keyword regex — GitHub proxy)
    syntax_matches = len(FORMAL_SYNTAX_RE.findall(text_trunc))
    formal_syntax_density = syntax_matches / n_tokens

    return {
        "entity_density": entity_density,
        "narrative_coherence": narrative_coherence,
        "formal_syntax_density": formal_syntax_density,
    }

# Self-check
if __name__ == "__main__":
    result = compute_proxies("The United Nations met in New York. However, France disagreed.")
    assert 0 <= result["entity_density"] <= 1
    assert 0 <= result["narrative_coherence"] <= 1
    assert 0 <= result["formal_syntax_density"] <= 1
    assert result["entity_density"] > 0, "Should detect NER entities"
    assert result["narrative_coherence"] > 0, "Should detect 'however'"
    print("L-3-2 self-check PASS")
```

---

### L-3-3: compute_domain_scores()

**Parent Epic:** A-3 (Proxy Computation, complexity 14)

```python
from multiprocessing import Pool
from tqdm import tqdm
from config import POOL_CHUNKSIZE

def compute_domain_scores(
    domain_texts: dict[str, list[str]],
    chunksize: int = POOL_CHUNKSIZE,
) -> dict[str, dict[str, list[float]]]:
    """
    Parallel proxy computation via Pool.imap_unordered per domain.

    Args:
        domain_texts: {domain: [text, ...]}
        chunksize: Pool imap_unordered chunksize (128 default)
    Returns:
        {domain: {"entity_density": [...], "narrative_coherence": [...],
                  "formal_syntax_density": [...]}}
    Notes:
        - Spawns Pool per domain to keep memory bounded
        - compute_proxies must be module-level (picklable) — it is
        - spaCy loaded inside each worker via load_nlp() singleton
    """
    domain_scores: dict[str, dict[str, list[float]]] = {}

    for domain, texts in domain_texts.items():
        scores_list: list[dict[str, float]] = []
        with Pool() as pool:
            for result in tqdm(
                pool.imap_unordered(compute_proxies, texts, chunksize=chunksize),
                total=len(texts),
                desc=domain[:30],
            ):
                scores_list.append(result)

        domain_scores[domain] = {
            "entity_density": [s["entity_density"] for s in scores_list],
            "narrative_coherence": [s["narrative_coherence"] for s in scores_list],
            "formal_syntax_density": [s["formal_syntax_density"] for s in scores_list],
        }

    return domain_scores
```

---

### L-3-4: worker_init pattern

**Parent Epic:** A-3 (Proxy Computation, complexity 14)

```python
# Pattern: pre-load spaCy model in each worker at pool creation
# Avoids repeated load overhead on every compute_proxies() call

def _worker_init():
    """Pool initializer: pre-load spaCy in each worker process."""
    load_nlp()  # populates _NLP_SINGLETON in this worker's memory space

# Usage:
with Pool(initializer=_worker_init) as pool:
    results = list(pool.imap_unordered(compute_proxies, texts, chunksize=128))

# Notes:
# - On Linux (fork), _NLP_SINGLETON from parent is inherited automatically
# - _worker_init is a safety measure for spawn-based systems (Windows/macOS)
# - Module-level FORMAL_SYNTAX_RE is also inherited via fork — no re-compile needed
```

---

### L-5-1: welch_anova()

**Parent Epic:** A-5 (Statistical Analysis, complexity 15)

```python
import scipy.stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd
import numpy as np

def welch_anova(
    domain_scores: dict[str, list[float]],
    proxy_name: str = "proxy",
) -> dict:
    """
    One-way Welch's ANOVA across all domains for one proxy metric.

    Args:
        domain_scores: {domain: [float, ...]} — scores for one proxy across all domains
        proxy_name: Column name for statsmodels formula (no spaces; use underscores)
    Returns:
        {
          "F": float,
          "p_value": float,
          "eta_squared": float,  # SS_between / SS_total from typ=2 ANOVA
          "n_groups": int,
          "significant": bool  # p < 0.05
        }
    Notes:
        - scipy.stats.f_oneway does NOT accept equal_var kwarg; Welch correction
          applied via unequal group sizes — for true Welch use pingouin.welch_anova
          or construct manually. statsmodels OLS approach used for eta-sq.
        - eta_sq = SS_C(domain) / (SS_C(domain) + SS_Residual)
    """
    groups = list(domain_scores.values())
    group_names = list(domain_scores.keys())

    # scipy ANOVA (F + p)
    F, p_value = scipy.stats.f_oneway(*groups)

    # statsmodels for eta-sq (needs long-format DataFrame)
    rows = []
    for domain, scores in domain_scores.items():
        for score in scores:
            rows.append({"domain": domain, proxy_name: score})
    df = pd.DataFrame(rows)

    model = ols(f"{proxy_name} ~ C(domain)", data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    ss_between = anova_table["sum_sq"]["C(domain)"]
    ss_total = anova_table["sum_sq"].sum()
    eta_squared = float(ss_between / ss_total)

    return {
        "F": float(F),
        "p_value": float(p_value),
        "eta_squared": eta_squared,
        "n_groups": len(groups),
        "significant": bool(p_value < 0.05),
    }

# Self-check
if __name__ == "__main__":
    import numpy as np
    rng = np.random.default_rng(42)
    scores = {
        "A": rng.normal(0.1, 0.02, 100).tolist(),
        "B": rng.normal(0.05, 0.02, 100).tolist(),
        "C": rng.normal(0.08, 0.02, 100).tolist(),
    }
    result = welch_anova(scores, proxy_name="entity_density")
    assert result["p_value"] < 0.05, "Should be significant for well-separated groups"
    assert 0 < result["eta_squared"] <= 1
    print("L-5-1 self-check PASS")
```

---

### L-5-2: tukey_hsd()

**Parent Epic:** A-5 (Statistical Analysis, complexity 15)

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd
import numpy as np

def tukey_hsd(
    domain_scores: dict[str, list[float]],
    alpha: float = 0.05,
) -> object:
    """
    Tukey HSD post-hoc pairwise comparisons for one proxy metric.

    Args:
        domain_scores: {domain: [float, ...]}
        alpha: Significance level (default 0.05)
    Returns:
        statsmodels TukeyHSDResults object
        Attributes: .summary(), .reject (bool array), .groupsunique
    Usage:
        results = tukey_hsd(entity_scores)
        summary_df = pd.DataFrame(
            data=results._results_table.data[1:],
            columns=results._results_table.data[0]
        )
        # Check specific pair:
        wiki_books_reject = get_pair_result(results, "Wikipedia (en)", "BookCorpus2")
    """
    endog = []
    groups = []
    for domain, scores in domain_scores.items():
        endog.extend(scores)
        groups.extend([domain] * len(scores))

    return pairwise_tukeyhsd(
        endog=np.array(endog),
        groups=np.array(groups),
        alpha=alpha,
    )


def get_pair_result(tukey_result, group1: str, group2: str) -> dict:
    """
    Extract result for a specific domain pair from Tukey HSD results.

    Returns: {"reject": bool, "meandiff": float, "p_adj": float}
    """
    import pandas as pd
    data = tukey_result._results_table.data
    df = pd.DataFrame(data[1:], columns=data[0])
    mask = (
        ((df["group1"] == group1) & (df["group2"] == group2)) |
        ((df["group1"] == group2) & (df["group2"] == group1))
    )
    row = df[mask]
    if row.empty:
        return {"reject": None, "meandiff": None, "p_adj": None}
    return {
        "reject": bool(row["reject"].iloc[0]),
        "meandiff": float(row["meandiff"].iloc[0]),
        "p_adj": float(row["p-adj"].iloc[0]),
    }
```

---

### L-5-3: domain_summary_stats()

**Parent Epic:** A-5 (Statistical Analysis, complexity 15)

```python
import pandas as pd
import numpy as np
import scipy.stats

def domain_summary_stats(
    domain_scores: dict[str, dict[str, list[float]]],
) -> pd.DataFrame:
    """
    Per-domain summary statistics for all 3 proxy metrics.

    Args:
        domain_scores: {domain: {proxy: [float, ...]}}
    Returns:
        DataFrame with columns:
          domain, proxy, mean, std, ci_lower, ci_upper, n
        Sorted by entity_density mean descending.
    """
    rows = []
    for domain, proxies in domain_scores.items():
        for proxy, scores in proxies.items():
            arr = np.array(scores)
            n = len(arr)
            mean = float(arr.mean())
            std = float(arr.std(ddof=1))
            sem = scipy.stats.sem(arr)
            ci = scipy.stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)
            rows.append({
                "domain": domain,
                "proxy": proxy,
                "mean": mean,
                "std": std,
                "ci_lower": float(ci[0]),
                "ci_upper": float(ci[1]),
                "n": n,
            })

    df = pd.DataFrame(rows)
    # Sort: entity_density rows by mean descending (for bar chart ordering)
    entity_order = (
        df[df["proxy"] == "entity_density"]
        .sort_values("mean", ascending=False)["domain"]
        .tolist()
    )
    df["domain_order"] = df["domain"].map(
        {d: i for i, d in enumerate(entity_order)}
    )
    return df.sort_values(["domain_order", "proxy"]).drop(columns="domain_order")
```

---

### L-5-4: evaluate_gate()

**Parent Epic:** A-5 (Statistical Analysis, complexity 15)

```python
def evaluate_gate(
    domain_scores: dict[str, dict[str, list[float]]],
    anova_results: dict[str, dict],
    tukey_results: dict[str, object],
    wiki_domain: str = "Wikipedia (en)",
    books_domain: str = "BookCorpus2",
) -> dict:
    """
    Evaluate H-M1 gate criteria and return machine-readable result.

    Gate criteria (MUST_WORK — both required):
      1. entity_density: mean(Wikipedia) > mean(Books), p < 0.05, eta² > 0.1
      2. narrative_coherence: mean(Books) > mean(Wikipedia), p < 0.05

    Args:
        domain_scores: {domain: {proxy: [float, ...]}}
        anova_results: {proxy: {F, p_value, eta_squared, significant}}
        tukey_results: {proxy: TukeyHSDResults}
        wiki_domain: Domain name for Wikipedia in pile_set_name
        books_domain: Domain name for Books in pile_set_name
    Returns:
        Full gate metrics dict with gate_pass: bool
    """
    import numpy as np

    def mean_score(domain: str, proxy: str) -> float:
        scores = domain_scores.get(domain, {}).get(proxy, [])
        return float(np.mean(scores)) if scores else float("nan")

    wiki_entity = mean_score(wiki_domain, "entity_density")
    books_entity = mean_score(books_domain, "entity_density")
    wiki_coherence = mean_score(wiki_domain, "narrative_coherence")
    books_coherence = mean_score(books_domain, "narrative_coherence")

    entity_anova = anova_results.get("entity_density", {})
    coherence_anova = anova_results.get("narrative_coherence", {})

    entity_tukey = get_pair_result(
        tukey_results["entity_density"], wiki_domain, books_domain
    )
    coherence_tukey = get_pair_result(
        tukey_results["narrative_coherence"], books_domain, wiki_domain
    )

    # Gate criterion 1
    crit1 = (
        wiki_entity > books_entity
        and entity_anova.get("p_value", 1.0) < 0.05
        and entity_anova.get("eta_squared", 0.0) > 0.1
    )

    # Gate criterion 2
    crit2 = (
        books_coherence > wiki_coherence
        and coherence_anova.get("p_value", 1.0) < 0.05
    )

    gate_pass = crit1 and crit2

    return {
        "gate_pass": gate_pass,
        "criterion_1_entity_density": {
            "wiki_mean": wiki_entity,
            "books_mean": books_entity,
            "direction_correct": wiki_entity > books_entity,
            "p_value": entity_anova.get("p_value"),
            "eta_squared": entity_anova.get("eta_squared"),
            "tukey_reject": entity_tukey.get("reject"),
            "pass": crit1,
        },
        "criterion_2_narrative_coherence": {
            "books_mean": books_coherence,
            "wiki_mean": wiki_coherence,
            "direction_correct": books_coherence > wiki_coherence,
            "p_value": coherence_anova.get("p_value"),
            "tukey_reject": coherence_tukey.get("reject"),
            "pass": crit2,
        },
    }
```

---

## Summary

| Subtask ID | Function | Parent Epic | Lines |
|------------|----------|-------------|-------|
| L-2-1 | stream_pile_hf() | A-2 (13) | HF streaming + seed shuffle |
| L-2-2 | sample_domains() | A-2 (13) | Stratified sampler with quota + min-token filter |
| L-3-1 | load_nlp() | A-3 (14) | Module singleton, fork-safe |
| L-3-2 | compute_proxies() | A-3 (14) | 3 proxy formulas, truncation, self-check |
| L-3-3 | compute_domain_scores() | A-3 (14) | Pool.imap_unordered dispatch per domain |
| L-3-4 | _worker_init pattern | A-3 (14) | Pre-load spaCy in worker |
| L-5-1 | welch_anova() | A-5 (15) | scipy F + statsmodels eta-sq, self-check |
| L-5-2 | tukey_hsd() + get_pair_result() | A-5 (15) | Post-hoc pairwise |
| L-5-3 | domain_summary_stats() | A-5 (15) | 95% CI per domain/proxy, sorted |
| L-5-4 | evaluate_gate() | A-5 (15) | Gate criteria evaluation → bool |
