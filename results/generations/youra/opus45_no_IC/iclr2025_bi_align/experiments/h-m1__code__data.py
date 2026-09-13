"""Data loading and preprocessing for H-E1 BCS experiment."""

import re
from datasets import load_dataset
from config import DATASET_PRIMARY, DATASET_SECONDARY, MIN_TURNS


def load_conversations(dataset_name: str, max_samples: int = None) -> list:
    """Load conversations from HuggingFace dataset."""
    ds = load_dataset(dataset_name, split="train")
    if max_samples:
        ds = ds.select(range(min(max_samples, len(ds))))

    conversations = []
    if dataset_name == DATASET_PRIMARY:
        for row in ds:
            conv = row.get("conversation", [])
            lang = row.get("language", "unknown")
            conversations.append({
                "conversation_id": row.get("conversation_id", ""),
                "model": row.get("model", "unknown"),
                "language": lang,
                "turns": conv
            })
    elif dataset_name == DATASET_SECONDARY:
        for idx, row in enumerate(ds):
            chosen = row.get("chosen", "")
            turns = _parse_hh_rlhf_turns(chosen)
            conversations.append({
                "conversation_id": f"hh_{idx}",
                "model": "anthropic",
                "language": "English",
                "turns": turns
            })
    return conversations


def _parse_hh_rlhf_turns(text: str) -> list:
    """Parse HH-RLHF format into turns list."""
    turns = []
    pattern = r"\n\n(Human|Assistant): "
    parts = re.split(pattern, text)
    i = 1
    while i < len(parts) - 1:
        role = "user" if parts[i] == "Human" else "assistant"
        content = parts[i + 1].strip()
        if content:
            turns.append({"role": role, "content": content})
        i += 2
    return turns


def filter_min_turns(conversations: list, min_turns: int = MIN_TURNS) -> list:
    """Keep conversations with >= min_turns per role."""
    filtered = []
    for conv in conversations:
        turns = conv.get("turns", [])
        user_count = sum(1 for t in turns if t.get("role") == "user")
        ai_count = sum(1 for t in turns if t.get("role") == "assistant")
        if user_count >= min_turns and ai_count >= min_turns:
            filtered.append(conv)
    return filtered


def filter_english(conversations: list) -> list:
    """Keep English conversations only."""
    return [c for c in conversations if c.get("language", "").lower() in ("english", "en")]


def remove_redacted(conversations: list) -> list:
    """Remove conversations with NAME_X patterns."""
    pattern = re.compile(r"NAME_\d+")
    filtered = []
    for conv in conversations:
        has_redacted = False
        for turn in conv.get("turns", []):
            if pattern.search(turn.get("content", "")):
                has_redacted = True
                break
        if not has_redacted:
            filtered.append(conv)
    return filtered


def extract_role_turns(conversation: dict) -> tuple:
    """Extract (user_texts, assistant_texts) from conversation."""
    user_turns = []
    ai_turns = []
    for turn in conversation.get("turns", []):
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            user_turns.append(content)
        elif role == "assistant":
            ai_turns.append(content)
    return user_turns, ai_turns
