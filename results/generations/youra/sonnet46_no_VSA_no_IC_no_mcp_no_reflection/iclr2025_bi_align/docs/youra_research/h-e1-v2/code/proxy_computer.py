import re
import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy

CORRECTION_REGEX = r'\b(no[,.]|actually[,.]|that\'s wrong|please redo|i meant|wrong[,.])\b'
_PATTERN = re.compile(CORRECTION_REGEX, re.IGNORECASE)


def tokenize_prompt(text: str, enc) -> int:
    return len(enc.encode(text, disallowed_special=()))


def compute_entropy(win: int, lose: int, tie: int) -> float:
    total = win + lose + tie
    if total == 0:
        return np.nan
    counts = np.array([win, lose, tie], dtype=float)
    return float(scipy_entropy(counts, base=2))


def correction_freq(conversation: list) -> float:
    if not conversation:
        return 0.0
    matches = sum(1 for turn in conversation if _PATTERN.search(turn.get("content", "")))
    return matches / len(conversation)


def proxy2_series(lmsys_monthly: pd.DataFrame) -> pd.Series:
    def row_entropy(row):
        return compute_entropy(row["win_count"], row["lose_count"], row["tie_count"])

    lmsys_monthly = lmsys_monthly.copy()
    lmsys_monthly["entropy"] = lmsys_monthly.apply(row_entropy, axis=1)
    return lmsys_monthly.groupby("month")["entropy"].mean()
