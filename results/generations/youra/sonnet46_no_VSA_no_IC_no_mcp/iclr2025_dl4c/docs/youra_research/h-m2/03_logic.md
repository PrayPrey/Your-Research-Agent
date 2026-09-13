---
title: "Logic: H-M2 — RLEF-Fraction Non-Zero Reward Signal at Hard Difficulty"
hypothesis_id: H-M2
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: TRL TrainerCallback reward monitoring pattern (web knowledge fallback)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `SimpleGRPOTrainer.train()` — accumulates rewards per difficulty bucket, writes JSONL at `self.reward_log_path`
- JSONL record format: `{"step": int, "loss": float, "intro_reward": float|null, "interview_reward": float|null, "competition_reward": float|null}`
- Difficulty keys in log: `"intro"`, `"interview"`, `"competition"` (NOT `"introductory"`)
- `self.reward_log_path` defaults to `logs/reward_monitoring.jsonl`

**Critical**: Log records contain per-step **mean** rewards (not per-sample). Non-zero fraction = fraction of steps where mean > 0.

---

## External Dependencies API

### From `h-e1/code/grpo_trainer.py` (ACTUAL CODE — lines 257–267)

```python
# SimpleGRPOTrainer writes per logging_steps:
record = {
    "step": global_step,          # int
    "loss": accum_loss,           # float
    "intro_reward": float | None,      # mean over accum window; None if no intro samples
    "interview_reward": float | None,
    "competition_reward": float | None,
}
# Written via: json.dumps(record) + "\n"  → self.reward_log_path
```

H-M2 reads this log post-hoc. No import of H-E1 modules required.

---

## A-2: DifficultyRewardCallback [Complexity: 8]

**Applied**: Standard PyTorch / transformers TrainerCallback pattern

### API Signatures

```python
from collections import defaultdict
from typing import Optional
from transformers import TrainerCallback, TrainerState, TrainerControl
import numpy as np

class DifficultyRewardCallback(TrainerCallback):
    """Live TRL callback; requires trl >= 0.7 for per-sample reward kwargs."""

    def __init__(self, difficulty_field: str = "difficulty") -> None:
        # difficulty_field: batch key for difficulty labels
        self.difficulty_field = difficulty_field
        self.bucket_indicators: dict[str, list[float]] = defaultdict(list)

    def on_step_end(
        self,
        args,
        state: TrainerState,
        control: TrainerControl,
        rewards: Optional[list[float]] = None,
        batch: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """Accumulate reward>0 indicators per difficulty bucket."""
        # rewards: list[float] length B  (per-sample, from trl >= 0.7 kwargs)
        # batch[self.difficulty_field]: list[str] length B
        # If either missing, no-op (post-hoc fallback handles it)
        if rewards is None or batch is None:
            return
        difficulties = batch.get(self.difficulty_field, [])
        for diff, r in zip(difficulties, rewards):
            self.bucket_indicators[diff].append(float(r > 0))

    def compute_fractions(self) -> dict[str, float]:
        """Return mean non-zero fraction per bucket; {} if no data."""
        return {
            k: float(np.mean(v)) if v else 0.0
            for k, v in self.bucket_indicators.items()
        }

    def log_summary(self) -> dict[str, float]:
        """Print and return fractions dict."""
        fracs = self.compute_fractions()
        for k, v in fracs.items():
            print(f"[H-M2] {k}: nonzero_fraction={v:.4f}")
        return fracs


def verify_trl_version() -> bool:
    """Return True if trl >= 0.7."""
    import trl
    from packaging.version import Version
    return Version(trl.__version__) >= Version("0.7")


def verify_mechanism_activated(
    callback: DifficultyRewardCallback,
) -> tuple[bool, dict]:
    """Check competition bucket > 0.10 and all 3 buckets present."""
    fracs = callback.compute_fractions()
    required = {"intro", "interview", "competition"}
    # Note: live callback uses full names from dataset difficulty field
    # H-E1 JSONL uses short keys; callback sees dataset field values
    all_present = required.issubset(fracs.keys()) or {
        "introductory", "interview", "competition"
    }.issubset(fracs.keys())
    comp_key = "competition"
    comp_frac = fracs.get(comp_key, 0.0)
    indicators = {
        "fractions": fracs,
        "all_buckets_present": all_present,
        "competition_fraction": comp_frac,
        "gate_passed": comp_frac > 0.10,
    }
    passed = all_present and comp_frac > 0.10
    return passed, indicators
```

---

## A-3: Analysis Functions [Complexity: 7]

**Applied**: Standard Python json/pathlib pattern

### API Signatures

```python
import json
from pathlib import Path

def load_reward_log(log_path: str) -> list[dict]:
    """Parse JSONL reward log; skip malformed lines."""
    records = []
    for line in Path(log_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
    # returns: [{"step": int, "intro_reward": float|None, ...}, ...]


def detect_nonzero(reward: float) -> bool:
    """Return reward > 0."""
    return reward > 0.0


def compute_nonzero_fractions(
    log_records: list[dict],
    difficulty_key: str = "difficulty",  # unused — log uses fixed column names
) -> dict[str, float]:
    """Compute per-bucket fraction of steps with mean reward > 0.

    H-E1 log columns: intro_reward, interview_reward, competition_reward.
    Returns keys matching PRD output: "introductory", "interview", "competition".
    """
    # Map log column → output key
    col_map = {
        "intro_reward": "introductory",
        "interview_reward": "interview",
        "competition_reward": "competition",
    }
    indicators: dict[str, list[float]] = {v: [] for v in col_map.values()}
    for rec in log_records:
        for col, bucket in col_map.items():
            val = rec.get(col)
            if val is not None:
                indicators[bucket].append(float(detect_nonzero(val)))
    import numpy as np
    return {k: float(np.mean(v)) if v else 0.0 for k, v in indicators.items()}
    # returns: {"introductory": float, "interview": float, "competition": float}


def compute_step_series(log_records: list[dict]) -> dict[str, list]:
    """Extract per-step reward values for line-plot figure."""
    col_map = {
        "intro_reward": "introductory",
        "interview_reward": "interview",
        "competition_reward": "competition",
    }
    series: dict[str, list] = {"steps": [], "introductory": [], "interview": [], "competition": []}
    for rec in log_records:
        series["steps"].append(rec.get("step", 0))
        for col, bucket in col_map.items():
            series[bucket].append(rec.get(col))  # may be None
    return series
```

---

## A-4: Save Results [Complexity: 5]

**Applied**: Standard Python json output pattern

### API Signatures

```python
import json
from pathlib import Path

def save_results(
    fractions: dict,          # {"introductory": float, "interview": float, "competition": float}
    output_path: str,
    gate_threshold: float = 0.10,
) -> dict:
    """Write reward_fractions.json; return result dict."""
    comp = fractions.get("competition", 0.0)
    intro = fractions.get("introductory", 0.0)
    interview = fractions.get("interview", 0.0)
    monotonicity = intro >= interview >= comp
    result = {
        "hypothesis": "h-m2",
        "gate_condition": f"competition_nonzero_fraction > {gate_threshold}",
        "fractions": {k: round(v, 4) for k, v in fractions.items()},
        "gate_result": "PASS" if comp > gate_threshold else "FAIL",
        "sample_counts": {},   # populated by caller if available
        "monotonicity_holds": monotonicity,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(result, indent=2))
    return result
```

---

## A-5 / A-6: Figure Functions [Complexity: 6 + 8]

**Applied**: Standard matplotlib bar/line/hist/scatter pattern

### API Signatures

```python
import matplotlib.pyplot as plt
from pathlib import Path

BUCKETS = ["introductory", "interview", "competition"]
COLORS = ["steelblue", "darkorange", "firebrick"]

def plot_bucket_fractions(
    fractions: dict,    # {"introductory": float, "interview": float, "competition": float}
    threshold: float,
    output_dir: str,
) -> None:
    """Figure 1: bar chart per bucket with threshold line."""
    vals = [fractions.get(b, 0.0) for b in BUCKETS]
    fig, ax = plt.subplots()
    ax.bar(BUCKETS, vals, color=COLORS)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylabel("Non-zero reward fraction")
    ax.set_title("H-M2: Non-Zero Reward Fraction by Difficulty")
    ax.legend()
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(str(Path(output_dir) / "fig1_nonzero_fraction_bar.png"), dpi=150)
    plt.close(fig)


def plot_fraction_over_steps(
    step_records: dict,   # from compute_step_series()
    output_dir: str,
) -> None:
    """Figure 2: non-zero reward fraction vs training step (3 curves)."""
    steps = step_records["steps"]
    fig, ax = plt.subplots()
    for bucket, color in zip(BUCKETS, COLORS):
        vals = step_records.get(bucket, [])
        # Convert raw mean reward to nonzero indicator per step
        nz = [float(v > 0) if v is not None else float("nan") for v in vals]
        ax.plot(steps, nz, label=bucket, color=color, alpha=0.8)
    ax.set_xlabel("Training step")
    ax.set_ylabel("Non-zero reward (step)")
    ax.set_title("H-M2: Non-Zero Reward Over Training Steps")
    ax.legend()
    fig.savefig(str(Path(output_dir) / "fig2_nonzero_fraction_step.png"), dpi=150)
    plt.close(fig)


def plot_reward_histogram(
    log_records: list[dict],
    output_dir: str,
) -> None:
    """Figure 3: reward distribution histogram per bucket."""
    col_map = {
        "intro_reward": "introductory",
        "interview_reward": "interview",
        "competition_reward": "competition",
    }
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    for ax, (col, bucket), color in zip(axes, col_map.items(), COLORS):
        vals = [r[col] for r in log_records if r.get(col) is not None]
        ax.hist(vals, bins=20, color=color, edgecolor="white")
        ax.set_title(bucket)
        ax.set_xlabel("Mean reward per step")
    axes[0].set_ylabel("Count")
    fig.suptitle("H-M2: Reward Distribution by Difficulty")
    fig.tight_layout()
    fig.savefig(str(Path(output_dir) / "fig3_reward_histogram.png"), dpi=150)
    plt.close(fig)


def plot_correlation(
    fractions: dict,    # {"introductory": float, "interview": float, "competition": float}
    output_dir: str,
) -> None:
    """Figure 4: difficulty bucket index vs mean non-zero fraction scatter."""
    vals = [fractions.get(b, 0.0) for b in BUCKETS]
    fig, ax = plt.subplots()
    ax.scatter(range(len(BUCKETS)), vals, c=COLORS, s=120, zorder=3)
    ax.plot(range(len(BUCKETS)), vals, "--", color="gray", alpha=0.5)
    ax.set_xticks(range(len(BUCKETS)))
    ax.set_xticklabels(BUCKETS)
    ax.set_ylabel("Non-zero fraction")
    ax.set_title("H-M2: Difficulty vs Non-Zero Fraction (Correlation)")
    fig.savefig(str(Path(output_dir) / "fig4_correlation_scatter.png"), dpi=150)
    plt.close(fig)
```

---

## A-7: Gate Assertion [Complexity: 5]

**Applied**: Standard Python assertion pattern

### API Signatures

```python
def assert_gate(fractions: dict, threshold: float = 0.10) -> bool:
    """Return True if competition fraction > threshold; print PASS/FAIL."""
    comp = fractions.get("competition", 0.0)
    result = "PASS" if comp > threshold else "FAIL"
    print(f"[H-M2 GATE] competition={comp:.4f} threshold={threshold} → {result}")
    return comp > threshold
```

---

## Integration: `main()` in `analyze_reward_fractions.py`

```python
def main(log_path: str, results_dir: str, figures_dir: str) -> None:
    """End-to-end post-hoc analysis pipeline."""
    records = load_reward_log(log_path)
    fractions = compute_nonzero_fractions(records)
    series = compute_step_series(records)
    save_results(fractions, output_path=f"{results_dir}/reward_fractions.json")
    plot_bucket_fractions(fractions, threshold=0.10, output_dir=figures_dir)
    plot_fraction_over_steps(series, output_dir=figures_dir)
    plot_reward_histogram(records, output_dir=figures_dir)
    plot_correlation(fractions, output_dir=figures_dir)
    assert_gate(fractions)
```
