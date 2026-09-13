"""Parse and structure HH-RLHF conversations."""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Turn:
    """Single conversation turn."""
    user_query: str
    ai_response: str
    turn_index: int


@dataclass
class Conversation:
    """Structured conversation with metadata."""
    conversation_id: str
    turns: List[Turn]
    turn_count: int


def parse_conversation(raw_conv: Dict[str, Any], conv_idx: int) -> Conversation:
    """
    Parse HH-RLHF conversation into structured format.

    Args:
        raw_conv: Raw conversation dict from dataset
        conv_idx: Conversation index (for ID generation)

    Returns:
        Structured Conversation object
    """
    conversation_text = raw_conv["chosen"]
    turns = extract_turns(conversation_text)

    return Conversation(
        conversation_id=f"conv_{conv_idx}",
        turns=turns,
        turn_count=len(turns)
    )


def extract_turns(conversation_text: str) -> List[Turn]:
    """
    Extract turns from HH-RLHF conversation format.

    Format: "\n\nHuman: query1 \n\nAssistant: response1 \n\nHuman: query2..."

    Returns:
        List of Turn objects
    """
    turns = []

    # Split by Human/Assistant markers
    parts = conversation_text.split("\n\n")
    human_parts = []
    assistant_parts = []

    for part in parts:
        if part.startswith("Human:"):
            human_parts.append(part.replace("Human:", "").strip())
        elif part.startswith("Assistant:"):
            assistant_parts.append(part.replace("Assistant:", "").strip())

    # Pair human queries with assistant responses
    for i, (query, response) in enumerate(zip(human_parts, assistant_parts)):
        turns.append(Turn(
            user_query=query,
            ai_response=response,
            turn_index=i
        ))

    return turns
