"""spaCy proxy computation + parallel dispatch."""
from __future__ import annotations

import re
import sys
import os
from typing import Optional

# Add code dir to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import CONNECTIVES, FORMAL_SYNTAX_PATTERN, MAX_CHARS, POOL_CHUNKSIZE, SPACY_MODEL

FORMAL_SYNTAX_RE: re.Pattern = re.compile(FORMAL_SYNTAX_PATTERN)

_NLP_SINGLETON: Optional[object] = None


def load_nlp(model: str = SPACY_MODEL):
    """Load spaCy model with module-level singleton (safe for fork-based Pool)."""
    global _NLP_SINGLETON
    if _NLP_SINGLETON is None:
        import spacy
        _NLP_SINGLETON = spacy.load(model)
    return _NLP_SINGLETON


def _worker_init():
    """Pool initializer: pre-load spaCy in each worker process."""
    load_nlp()


def compute_proxies(text: str) -> dict[str, float]:
    """
    Compute 3 cognitive task pattern proxies for a single document.

    Returns entity_density, narrative_coherence, formal_syntax_density.
    """
    nlp = load_nlp()
    text_trunc = text[:MAX_CHARS]
    doc = nlp(text_trunc)

    tokens = [tok for tok in doc if not tok.is_space]
    n_tokens = max(len(tokens), 1)

    entity_density = len(doc.ents) / n_tokens

    words_lower = {tok.lower_ for tok in tokens}
    connective_count = len(words_lower & CONNECTIVES)
    narrative_coherence = connective_count / n_tokens

    syntax_matches = len(FORMAL_SYNTAX_RE.findall(text_trunc))
    formal_syntax_density = syntax_matches / n_tokens

    return {
        "entity_density": entity_density,
        "narrative_coherence": narrative_coherence,
        "formal_syntax_density": formal_syntax_density,
    }


def compute_domain_scores(
    domain_texts: dict[str, list[str]],
    chunksize: int = POOL_CHUNKSIZE,
) -> dict[str, dict[str, list[float]]]:
    """Parallel proxy computation via Pool.imap_unordered per domain."""
    from multiprocessing import Pool
    from tqdm import tqdm

    domain_scores: dict[str, dict[str, list[float]]] = {}

    for domain, texts in domain_texts.items():
        scores_list: list[dict[str, float]] = []
        with Pool(initializer=_worker_init) as pool:
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


if __name__ == "__main__":
    result = compute_proxies("The United Nations met in New York. However, France disagreed.")
    assert 0 <= result["entity_density"] <= 1
    assert 0 <= result["narrative_coherence"] <= 1
    assert 0 <= result["formal_syntax_density"] <= 1
    assert result["entity_density"] > 0, "Should detect NER entities"
    assert result["narrative_coherence"] > 0, "Should detect 'however'"
    print("compute self-check PASS")
