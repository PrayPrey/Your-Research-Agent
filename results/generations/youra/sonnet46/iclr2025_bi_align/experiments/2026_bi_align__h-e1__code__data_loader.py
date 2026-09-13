"""
data_loader.py - Load HH-RLHF splits and parse conversations for h-e1.
"""
import re
import datasets
from typing import List, Dict


SPLITS = [
    ("helpful-base", "train"),
    ("helpful-rejection-sampled", "train"),
    ("helpful-online", "train"),
]


def load_all_splits(cache_dir: str) -> List[dict]:
    """Load helpful-base, helpful-rejection-sampled, helpful-online splits.

    Returns a flat list of dicts with 'chosen' and 'rejected' fields.
    """
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
    """Parse HH-RLHF conversation format into list of turn texts.

    Format: \\n\\nHuman: <text>\\n\\nAssistant: <text> ...
    Returns list of turn texts in order (H, A, H, A, ...).
    """
    # Split on \n\nHuman: or \n\nAssistant:
    pattern = r'\n\nHuman: |\n\nAssistant: '
    parts = re.split(pattern, chosen)
    # First element is empty string before first turn
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
    """Extract (h_next, a_actual, h_prompt) triples from conversations.

    For each conversation with >= 3 turns (H, A, H pattern):
      h_prompt = H_t  (turn index 0, 2, 4...)
      a_actual = A_t  (turn index 1, 3, 5...)
      h_next   = H_{t+1}  (turn index 2, 4, 6...)

    Returns dict with keys: h_next, a_actual, h_prompt,
                             token_counts, jaccard_overlaps
    """
    h_nexts = []
    a_actuals = []
    h_prompts = []
    token_counts = []
    jaccard_overlaps = []

    for record in conversations:
        chosen = record.get("chosen", "")
        turns = parse_conversation(chosen)
        # Need at least 3 turns: H, A, H
        # Turns alternate H(0), A(1), H(2), A(3), ...
        # We extract triples: (H_t, A_t, H_{t+1})
        # t goes 0, 2, 4, ... (Human turns)
        # H_t = turns[2*t], A_t = turns[2*t+1], H_{t+1} = turns[2*t+2]
        n = len(turns)
        for i in range(0, n - 2, 2):
            h_prompt = turns[i]
            a_actual = turns[i + 1]
            h_next = turns[i + 2]
            # Filter empty turns
            if not h_prompt or not a_actual or not h_next:
                continue
            h_nexts.append(h_next)
            a_actuals.append(a_actual)
            h_prompts.append(h_prompt)
            tc = compute_token_count(a_actual)
            token_counts.append(tc)
            jac = compute_jaccard(h_next, a_actual)
            jaccard_overlaps.append(jac)

    assert len(h_nexts) == len(a_actuals) == len(h_prompts)
    assert len(h_nexts) >= 1000, f"Too few pairs: {len(h_nexts)}"

    return {
        "h_next": h_nexts,
        "a_actual": a_actuals,
        "h_prompt": h_prompts,
        "token_counts": token_counts,
        "jaccard_overlaps": jaccard_overlaps,
    }
