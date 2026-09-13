import re
from datasets import load_dataset


def parse_conversation(text: str) -> list[dict]:
    pattern = r'\n\n(Human|Assistant): '
    parts = re.split(pattern, text)
    if parts[0] == '':
        parts = parts[1:]
    turns = []
    for i in range(0, len(parts) - 1, 2):
        role = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if content:
            turns.append({"role": role.lower(), "content": content})
    return turns


def load_conversations(split: str = "train") -> list[dict]:
    ds = load_dataset("Anthropic/hh-rlhf", split=split)
    conversations = []
    for i, row in enumerate(ds):
        text = row.get("chosen", "")
        if not text:
            continue
        turns = parse_conversation(text)
        if turns:
            conversations.append({
                "conversation_id": f"conv_{i}",
                "turns": turns
            })
    return conversations


def filter_multiturn(conversations: list[dict], min_turns: int = 2) -> list[dict]:
    filtered = []
    for conv in conversations:
        human_turns = sum(1 for t in conv["turns"] if t["role"] == "human")
        ai_turns = sum(1 for t in conv["turns"] if t["role"] == "assistant")
        if human_turns >= min_turns and ai_turns >= min_turns:
            filtered.append(conv)
    return filtered


def extract_turn_pairs(conversations: list[dict]) -> list[dict]:
    pairs = []
    for conv in conversations:
        turns = conv["turns"]
        human_idx = 0
        for i, turn in enumerate(turns):
            if turn["role"] == "human":
                ai_response = None
                for j in range(i + 1, len(turns)):
                    if turns[j]["role"] == "assistant":
                        ai_response = turns[j]["content"]
                        break
                if ai_response:
                    has_next = any(
                        t["role"] == "human" for t in turns[i + 1:]
                        if turns.index(t) > i
                    )
                    remaining = turns[i + 1:]
                    has_next = any(t["role"] == "human" for t in remaining)
                    pairs.append({
                        "conversation_id": conv["conversation_id"],
                        "turn_idx": human_idx,
                        "human_text": turn["content"],
                        "ai_text": ai_response,
                        "has_next_turn": has_next
                    })
                    human_idx += 1
    return pairs
