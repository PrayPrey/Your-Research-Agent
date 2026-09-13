import re
from datasets import load_dataset
import config


def load_hh_rlhf():
    """Load HH-RLHF test split (default config)."""
    ds = load_dataset("Anthropic/hh-rlhf", split="test")
    texts = []
    for item in ds:
        texts.extend(extract_responses(item.get("chosen", "")))
        texts.extend(extract_responses(item.get("rejected", "")))
    return texts


def load_reward_bench_safety():
    """Load RewardBench Safety subset responses."""
    rb = load_dataset("allenai/reward-bench", split="filtered")
    texts = []
    for item in rb:
        subset = item.get("subset", "")
        if "refusal" in subset.lower() or "xstest" in subset.lower():
            for key in ["chosen", "rejected"]:
                resp = item.get(key, "")
                if resp:
                    texts.append(normalize_text(resp))
    return texts


def extract_responses(dialogue):
    """Extract assistant turns from dialogue transcript."""
    if not dialogue:
        return []
    parts = re.split(r"\n(?=(?:Human|Assistant):)", dialogue)
    assistant_texts = []
    for part in parts:
        if part.strip().startswith("Assistant:"):
            text = part.replace("Assistant:", "", 1).strip()
            if text:
                assistant_texts.append(normalize_text(text))
    return assistant_texts


def normalize_text(text):
    """Normalize whitespace and lowercase."""
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def build_labels(texts, proxy):
    """Build binary ground-truth labels for a proxy using regex patterns."""
    patterns = config.PROXY_PATTERNS.get(proxy, [])
    labels = []
    for text in texts:
        match = any(re.search(p, text, re.IGNORECASE | re.MULTILINE) for p in patterns)
        labels.append(1 if match else 0)
    return labels
