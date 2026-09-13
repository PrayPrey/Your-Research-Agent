"""H-M2: Accuracy metrics - F1/ROUGE-L per LongBench convention."""

import re
from typing import List


def normalize_text(text: str) -> str:
    """Normalize for comparison."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text


def token_f1(pred: str, ref: str) -> float:
    """Token-level F1 score."""
    pred_tokens = set(normalize_text(pred).split())
    ref_tokens = set(normalize_text(ref).split())

    if not pred_tokens or not ref_tokens:
        return 0.0

    common = pred_tokens & ref_tokens
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(ref_tokens)

    return 2 * precision * recall / (precision + recall)


def lcs_length(a: List[str], b: List[str]) -> int:
    """Longest common subsequence length."""
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0

    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]


def rouge_l_f1(pred: str, ref: str) -> float:
    """ROUGE-L F1 score."""
    pred_tokens = normalize_text(pred).split()
    ref_tokens = normalize_text(ref).split()

    if not pred_tokens or not ref_tokens:
        return 0.0

    lcs = lcs_length(pred_tokens, ref_tokens)
    if lcs == 0:
        return 0.0

    precision = lcs / len(pred_tokens)
    recall = lcs / len(ref_tokens)

    return 2 * precision * recall / (precision + recall)


SUMMARIZATION_DOMAINS = {
    "Long Structured Data Understanding",
}


def compute_accuracy(generated_text: str, reference: str, domain: str = None) -> float:
    """Compute accuracy using domain-appropriate metric."""
    if domain in SUMMARIZATION_DOMAINS:
        return rouge_l_f1(generated_text, reference)
    return token_f1(generated_text, reference)
