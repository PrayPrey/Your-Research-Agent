"""E1: Compute token-count-matched Pile checkpoint steps for each Pythia model size."""
import json
from pathlib import Path

BATCH_TOKENS: int = 2_097_152
DEDUP_FINAL_STEP: int = 143_000
DEDUP_TARGET_TOKENS: int = 207_000_000_000
SIZES: list[str] = ["160m", "410m", "1b", "6.9b"]

BASE_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BASE_DIR / "checkpoint_map.json"


def step_to_tokens(step: int, batch_tokens: int = BATCH_TOKENS) -> int:
    return step * batch_tokens


def find_matched_pile_step(
    target_tokens: int = DEDUP_TARGET_TOKENS,
    batch_tokens: int = BATCH_TOKENS,
) -> int:
    raw = target_tokens // batch_tokens  # 98705
    # Pythia logs checkpoints at multiples of 1000; round to nearest
    return round(raw / 1000) * 1000  # 99000


def build_checkpoint_map(sizes: list[str] = SIZES) -> dict:
    pile_step = find_matched_pile_step()
    dedup_step = DEDUP_FINAL_STEP
    dedup_tokens = step_to_tokens(dedup_step)

    result = {}
    for size in sizes:
        pile_tokens = step_to_tokens(pile_step)
        mismatch_pct = abs(pile_tokens - DEDUP_TARGET_TOKENS) / DEDUP_TARGET_TOKENS * 100
        result[size] = {
            "pile_step": pile_step,
            "dedup_step": dedup_step,
            "pile_tokens": pile_tokens,
            "dedup_tokens": dedup_tokens,
            "token_mismatch_pct": round(mismatch_pct, 4),
        }
    return result


def main() -> None:
    checkpoint_map = build_checkpoint_map()
    OUTPUT_FILE.write_text(json.dumps(checkpoint_map, indent=2))
    print(f"Wrote {OUTPUT_FILE}")
    for size, info in checkpoint_map.items():
        print(
            f"  {size}: pile=step{info['pile_step']} ({info['pile_tokens']/1e9:.1f}B tokens)  "
            f"dedup=step{info['dedup_step']}  mismatch={info['token_mismatch_pct']:.2f}%"
        )


if __name__ == "__main__":
    main()
