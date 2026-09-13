"""Data loading and sampling for H-C1 doctest prevalence scan."""

from datasets import load_dataset
from tqdm import tqdm


def load_python_stream(seed: int = 42, buffer_size: int = 10000):
    """Load Python code corpus as a shuffled streaming dataset.

    Primary: bigcode/the-stack-dedup (Python subset) — requires gated access.
    Fallback: codeparrot/codeparrot-clean-valid — ungated, same content field schema.
    # ponytail: fallback to ungated dataset; swap back to the-stack-dedup when access granted
    """
    import os
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    try:
        ds = load_dataset(
            "bigcode/the-stack-dedup",
            data_dir="data/python",
            streaming=True,
            split="train",
            token=token,
        )
        # Test access with a cheap operation
        ds.info  # noqa: triggers auth check
        print("Using bigcode/the-stack-dedup")
    except Exception:
        print("the-stack-dedup unavailable (gated). Falling back to codeparrot/codeparrot-clean-valid")
        ds = load_dataset(
            "codeparrot/codeparrot-clean-valid",
            streaming=True,
            split="train",
        )
    return ds.shuffle(seed=seed, buffer_size=buffer_size)


def quality_filter(sample: dict) -> bool:
    """True if avg_line_len<=100, max_line_len<=1000, alphanum_frac>=0.25."""
    src = sample.get("content", "")
    if not src:
        return False
    lines = src.splitlines() or [""]
    avg_len = sum(len(l) for l in lines) / len(lines)
    max_len = max(len(l) for l in lines)
    total = len(src)
    alphanum = sum(c.isalnum() for c in src)
    alphanum_frac = alphanum / total if total > 0 else 0.0
    return avg_len <= 100 and max_len <= 1000 and alphanum_frac >= 0.25


def reservoir_sample(stream, n: int = 10000) -> list:
    """Collect first n quality-passing samples from pre-shuffled stream."""
    samples = []
    for item in tqdm(stream, desc="Sampling"):
        if quality_filter(item):
            samples.append(item)
            if len(samples) >= n:
                break
    return samples
