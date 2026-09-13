"""
data_loader.py - Load HH-RLHF splits and parse conversations for h-e1/h-m1/h-m2.

h-m2 extension: extract_pairs() also returns h_curr (H_t) and a_next (A_{t+1}).
                verify_embedding_cache() checks all required .npy files.
"""
import os
import re
import logging
import datasets
from typing import List, Dict

logger = logging.getLogger(__name__)

SPLITS = [
    ("helpful-base", "train"),
    ("helpful-rejection-sampled", "train"),
    ("helpful-online", "train"),
]

TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
MIN_N_PAIRS_PER_TIER = 1000


def split_by_tier(cache_dir: str) -> Dict[str, Dict]:
    """Load each RLHF tier separately and extract pairs per tier.

    Args:
        cache_dir: Path to HuggingFace datasets cache directory.

    Returns:
        Dict mapping tier_name -> {h_next, a_actual, h_prompt, token_counts,
                                    jaccard_overlaps, h_curr, a_next}

    Raises:
        ValueError: If any tier has fewer than MIN_N_PAIRS_PER_TIER pairs.
    """
    tier_data = {}
    for tier in TIER_ORDER:
        logger.info(f"Loading tier: {tier}")
        ds = datasets.load_dataset(
            "Anthropic/hh-rlhf",
            data_dir=tier,
            cache_dir=cache_dir,
            verification_mode="no_checks",
        )
        records = ds["train"].to_list()
        pairs = extract_pairs(records)

        n_pairs = len(pairs["h_next"])
        if n_pairs < MIN_N_PAIRS_PER_TIER:
            raise ValueError(
                f"Tier '{tier}' has only {n_pairs} pairs "
                f"(minimum required: {MIN_N_PAIRS_PER_TIER})"
            )

        logger.info(f"Tier {tier}: {n_pairs} pairs extracted")
        tier_data[tier] = pairs

    return tier_data


def load_all_splits(cache_dir: str) -> List[dict]:
    """Load helpful-base, helpful-rejection-sampled, helpful-online splits."""
    all_records = []
    for data_dir, split in SPLITS:
        try:
            ds = datasets.load_dataset(
                "Anthropic/hh-rlhf",
                data_dir=data_dir,
                cache_dir=cache_dir,
                verification_mode="no_checks",
            )
            records = ds[split].to_list()
            all_records.extend(records)
        except Exception as e:
            print(f"Warning: could not load {data_dir}/{split}: {e}")
    return all_records


def parse_conversation(chosen: str) -> List[str]:
    """Parse HH-RLHF conversation format into list of turn texts."""
    pattern = r'\n\nHuman: |\n\nAssistant: '
    parts = re.split(pattern, chosen)
    turns = [p.strip() for p in parts if p.strip()]
    return turns


def compute_jaccard(s1: str, s2: str) -> float:
    """Compute Jaccard similarity between two strings (word-level)."""
    tokens1 = set(s1.lower().split())
    tokens2 = set(s2.lower().split())
    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union)


def compute_token_count(text: str) -> int:
    """Approximate token count by whitespace split."""
    return len(text.split())


def extract_pairs(conversations: List[dict]) -> Dict:
    """Extract conversation pairs including h-m2 new fields h_curr and a_next.

    h-m2 extension: also extracts h_curr (H_t) and a_next (A_{t+1}) for A<-H direction.

    For each conversation with >= 3 turns (H, A, H pattern):
      h_prompt = H_t  (turn index i)
      a_actual = A_t  (turn index i+1)
      h_next   = H_{t+1}  (turn index i+2)
      h_curr   = H_t  (= h_prompt, alias for A<-H direction)
      a_next   = A_{t+1}  (turn index i+3, if exists; else empty string)

    Returns dict with keys: h_next, a_actual, h_prompt, token_counts,
                             jaccard_overlaps, h_curr, a_next
    """
    h_nexts = []
    a_actuals = []
    h_prompts = []
    token_counts = []
    jaccard_overlaps = []
    h_currs = []
    a_nexts = []

    for record in conversations:
        chosen = record.get("chosen", "")
        turns = parse_conversation(chosen)
        n = len(turns)
        for i in range(0, n - 2, 2):
            h_prompt = turns[i]
            a_actual = turns[i + 1]
            h_next = turns[i + 2]
            if not h_prompt or not a_actual or not h_next:
                continue
            a_next = turns[i + 3] if (i + 3) < n else ""

            h_nexts.append(h_next)
            a_actuals.append(a_actual)
            h_prompts.append(h_prompt)
            h_currs.append(h_prompt)
            a_nexts.append(a_next)
            token_counts.append(compute_token_count(a_actual))
            jaccard_overlaps.append(compute_jaccard(h_next, a_actual))

    assert len(h_nexts) == len(a_actuals) == len(h_prompts)
    assert len(h_nexts) >= 1000, f"Too few pairs: {len(h_nexts)}"

    return {
        "h_next": h_nexts,
        "a_actual": a_actuals,
        "h_prompt": h_prompts,
        "token_counts": token_counts,
        "jaccard_overlaps": jaccard_overlaps,
        "h_curr": h_currs,
        "a_next": a_nexts,
    }


def verify_embedding_cache(cache_dir: str, model_names: List[str], tiers: List[str]) -> Dict[str, bool]:
    """Check all required .npy embedding files (h-m1 + h-m2 keys).

    Args:
        cache_dir: Embeddings cache directory.
        model_names: List of model names.
        tiers: List of tier names.

    Returns:
        Dict mapping cache_key -> exists_bool
    """
    model_slug_map = {
        "all-MiniLM-L6-v2": "minilm",
        "paraphrase-MiniLM-L6-v2": "paraphrase",
        "all-mpnet-base-v2": "mpnet",
    }
    tier_slug_map = {
        "helpful-base": "base",
        "helpful-rejection-sampled": "rejection_sampled",
        "helpful-online": "online",
    }

    templates = [
        "{model}_H_next_{tier}.npy",
        "{model}_A_curr_{tier}.npy",
        "{model}_A_next_{tier}.npy",
        "{model}_H_curr_{tier}.npy",
    ]

    result = {}
    for template in templates:
        for model in model_names:
            model_slug = model_slug_map.get(model, model)
            for tier in tiers:
                tier_slug = tier_slug_map.get(tier, tier.replace("-", "_"))
                key = template.format(model=model_slug, tier=tier_slug)
                path = os.path.join(cache_dir, key)
                result[key] = os.path.exists(path)

    return result
