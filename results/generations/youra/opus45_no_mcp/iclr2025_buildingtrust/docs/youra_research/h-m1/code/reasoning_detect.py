"""A-4 & A-5: Reasoning Chain Detection + Answer/Confidence Extraction"""
import re
import string

NUMBERED = re.compile(r'(?:^|\n)\s*(?:\d+[\.\)]|Step\s+\d+:)', re.IGNORECASE)
ORDINAL = re.compile(r'\b(First|Second|Third|Fourth|Fifth|Finally|Lastly|Next|Then)\b', re.IGNORECASE)
LOGICAL = re.compile(r'\b(therefore|thus|hence|because|so|consequently)\b', re.IGNORECASE)


def detect_reasoning_chain(text: str) -> bool:
    """True if text contains any numbered/ordinal/logical reasoning marker."""
    return bool(NUMBERED.search(text) or ORDINAL.search(text) or LOGICAL.search(text))


def count_reasoning_steps(text: str) -> int:
    """Count of distinct numbered-step markers."""
    return len(NUMBERED.findall(text))


def classify_patterns(text: str) -> dict[str, bool]:
    """Returns {'numbered': bool, 'ordinal': bool, 'logical': bool} for pattern breakdown."""
    return {
        "numbered": bool(NUMBERED.search(text)),
        "ordinal": bool(ORDINAL.search(text)),
        "logical": bool(LOGICAL.search(text)),
    }


def extract_answer(text: str, num_choices: int) -> str | None:
    """Extract letter answer (A..num_choices'th letter). None if not found."""
    valid_letters = string.ascii_uppercase[:num_choices]
    pattern = rf'Answer[:\s]+\(?([{valid_letters}])\)?'
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).upper() if m else None


def extract_confidence(text: str) -> float | None:
    """Extract confidence 0-100 from 'Confidence: N' pattern. None if not found."""
    m = re.search(r'Confidence[:\s]+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    test = """Let me think step by step.
1. First, consider option A
2. Then, option B seems better
3. Therefore, the answer is B

Answer: B Confidence: 85"""

    print(f"Has reasoning: {detect_reasoning_chain(test)}")
    print(f"Step count: {count_reasoning_steps(test)}")
    print(f"Patterns: {classify_patterns(test)}")
    print(f"Answer: {extract_answer(test, 5)}")
    print(f"Confidence: {extract_confidence(test)}")
