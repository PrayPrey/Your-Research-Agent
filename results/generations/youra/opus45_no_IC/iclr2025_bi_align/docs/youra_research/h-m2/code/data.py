"""Data loading and pairing for H-M2 formality correlation experiment."""

import re
from datasets import load_dataset
from config import DATASET_NAME, MIN_TURNS, MIN_MSG_LEN


def load_conversations(dataset_name: str = DATASET_NAME, max_samples: int = None) -> list:
    """Load conversations from HuggingFace dataset."""
    ds = load_dataset(dataset_name, split="train")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))

    conversations = []
    for idx, row in enumerate(ds):
        chosen = row.get("chosen", "")
        turns = _parse_hh_rlhf_turns(chosen)
        conversations.append({
            "conversation_id": f"hh_{idx}",
            "model": "anthropic",
            "turns": turns
        })
    return conversations


def _parse_hh_rlhf_turns(text: str) -> list:
    """Parse HH-RLHF Human:/Assistant: format into turns list."""
    turns = []
    pattern = r"\n\n(Human|Assistant): "
    parts = re.split(pattern, text)
    i = 1
    while i < len(parts) - 1:
        role = "human" if parts[i] == "Human" else "assistant"
        content = parts[i + 1].strip()
        if content:
            turns.append({"role": role, "content": content})
        i += 2
    return turns


def extract_role_turns(conversation: dict) -> tuple:
    """Extract (human_texts, ai_texts) from conversation."""
    human_turns = []
    ai_turns = []
    for turn in conversation.get("turns", []):
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "human":
            human_turns.append(content)
        elif role == "assistant":
            ai_turns.append(content)
    return human_turns, ai_turns


def validate_pair(human_1: str, ai_1: str, min_len: int = MIN_MSG_LEN) -> bool:
    """Validate a (human, AI) message pair."""
    if not human_1 or not ai_1:
        return False
    human_1 = human_1.strip()
    ai_1 = ai_1.strip()
    if len(human_1) < min_len or len(ai_1) < min_len:
        return False
    try:
        human_1.encode('utf-8')
        ai_1.encode('utf-8')
    except UnicodeError:
        return False
    return True


def load_and_pair(dataset_name: str = DATASET_NAME, min_turns: int = MIN_TURNS) -> list:
    """Load conversations and extract valid (human_1, ai_1) pairs."""
    convos = load_conversations(dataset_name)
    pairs = []

    for conv in convos:
        turns = conv.get("turns", [])
        if len(turns) < min_turns:
            continue
        human_texts, ai_texts = extract_role_turns(conv)
        if not human_texts or not ai_texts:
            continue
        human_1, ai_1 = human_texts[0], ai_texts[0]
        if validate_pair(human_1, ai_1):
            pairs.append((human_1, ai_1))

    return pairs
