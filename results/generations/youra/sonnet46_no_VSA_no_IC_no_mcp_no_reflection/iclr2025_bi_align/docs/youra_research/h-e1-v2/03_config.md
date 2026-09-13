---
title: "Config: h-e1-v2 Behavioral Proxy Trend Detection"
hypothesis_id: h-e1-v2
type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
---

Applied: argparse CLI config pattern (LIGHT tier, no YAML)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design
**Config Files Found**: None - new config
**Pattern Used**: argparse (hardcoded defaults in add_argument calls)

---

## C-1-1: Argparse Configuration Schema [Complexity: 9, Budget: 1]

### Configuration (argparse setup for main.py)

```python
import argparse

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="h-e1-v2: Behavioral proxy trend detection pipeline"
    )

    # --- Data group ---
    data = p.add_argument_group("data")
    data.add_argument("--date-start", default="2023-01",
                      help="Start month inclusive, format YYYY-MM (default: 2023-01)")
    data.add_argument("--date-end", default="2024-12",
                      help="End month inclusive, format YYYY-MM (default: 2024-12)")
    data.add_argument("--n-workers", type=int, default=4,
                      help="Multiprocessing workers for tiktoken tokenization (default: 4)")

    # --- Cohort group ---
    cohort = p.add_argument_group("cohort")
    cohort.add_argument("--min-bins", type=int, default=3,
                        help="Min monthly appearances for returning-user cohort (default: 3)")
    cohort.add_argument("--min-cohort-size", type=int, default=50,
                        help="Min users per monthly bin to keep bin (default: 50)")

    # --- Statistics group ---
    stats = p.add_argument_group("statistics")
    stats.add_argument("--min-votes", type=int, default=100,
                       help="Min votes per LMSYS model-pair bin (default: 100)")
    stats.add_argument("--top-n-pairs", type=int, default=5,
                       help="Top N model pairs by total vote count (default: 5)")
    stats.add_argument("--bootstrap-B", type=int, default=1000,
                       help="Bootstrap CI resamples for tau (default: 1000)")
    stats.add_argument("--seed", type=int, default=42,
                       help="Random seed for bootstrap (default: 42)")
    stats.add_argument("--acf-threshold", type=float, default=0.1,
                       help="Lag-1 ACF threshold to switch to Hamed-Rao (default: 0.1)")
    stats.add_argument("--significance-threshold", type=float, default=0.05,
                       help="Mann-Kendall p-value significance threshold (default: 0.05)")
    stats.add_argument("--gate-min-significant", type=int, default=2,
                       help="Min proxies passing threshold for gate (default: 2)")

    # --- Output group ---
    out = p.add_argument_group("output")
    out.add_argument("--out-dir", default="results",
                     help="Directory for CSV intermediates and results.json (default: results)")
    out.add_argument("--figures-dir", default="figures",
                     help="Directory for saved figures (default: figures)")
    out.add_argument("--smoke", action="store_true",
                     help="Run smoke test only and exit")

    args = p.parse_args()
    _validate_args(args)
    return args


def _validate_args(args: argparse.Namespace) -> None:
    import re, sys
    month_re = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
    if not month_re.match(args.date_start):
        sys.exit(f"--date-start must be YYYY-MM, got: {args.date_start}")
    if not month_re.match(args.date_end):
        sys.exit(f"--date-end must be YYYY-MM, got: {args.date_end}")
    if args.date_start >= args.date_end:
        sys.exit("--date-start must be before --date-end")
    if args.min_bins < 2:
        sys.exit("--min-bins must be >= 2")
    if args.min_cohort_size < 1:
        sys.exit("--min-cohort-size must be >= 1")
    if args.gate_min_significant not in (1, 2, 3):
        sys.exit("--gate-min-significant must be 1, 2, or 3")
```

### Example Invocation

```bash
# Default run (all parameters use defaults)
python main.py

# Custom date range and output dirs
python main.py --date-start 2023-06 --date-end 2024-06 --out-dir /tmp/results --figures-dir /tmp/figures

# Smoke test only
python main.py --smoke
```

---

### results.json Schema

```json
{
  "hypothesis_id": "h-e1-v2",
  "date_run": "2026-08-31T12:00:00",
  "config": {
    "date_start": "2023-01",
    "date_end": "2024-12",
    "min_bins": 3,
    "min_cohort_size": 50,
    "min_votes": 100,
    "top_n_pairs": 5,
    "bootstrap_B": 1000,
    "seed": 42,
    "acf_threshold": 0.1,
    "significance_threshold": 0.05,
    "gate_min_significant": 2
  },
  "proxies": {
    "proxy1_prompt_tokens": {
      "tau": 0.45,
      "p": 0.012,
      "significant": true,
      "method": "kendalltau",
      "ci_low": 0.21,
      "ci_high": 0.67,
      "n_months": 24
    },
    "proxy2_vote_entropy": {
      "tau": 0.31,
      "p": 0.038,
      "significant": true,
      "method": "hamed_rao",
      "ci_low": 0.05,
      "ci_high": 0.55,
      "n_months": 18
    },
    "proxy3_correction_freq": {
      "tau": 0.12,
      "p": 0.210,
      "significant": false,
      "method": "kendalltau",
      "ci_low": -0.10,
      "ci_high": 0.34,
      "n_months": 24
    }
  },
  "gate": {
    "n_significant": 2,
    "gate_min_significant": 2,
    "gate_passed": true
  },
  "cohort": {
    "wildchat_total_conversations": 980000,
    "users_with_gte1_bin": 450000,
    "users_with_gte3_bins": 85000,
    "analysis_cohort_size": 75000
  }
}
```

---

### CSV Intermediate Schemas

#### wildchat_monthly.csv

| Column | dtype | Description |
|--------|-------|-------------|
| `month` | str (YYYY-MM) | Monthly bin |
| `prompt_tokens_mean` | float64 | Mean first-turn token count |
| `correction_freq_mean` | float64 | Mean correction/negation frequency |
| `cohort_size` | int64 | Distinct hashed_ip users in bin |

#### lmsys_monthly.csv

| Column | dtype | Description |
|--------|-------|-------------|
| `month` | str (YYYY-MM) | Monthly bin |
| `model_pair` | str | "model_a__vs__model_b" (alphabetically sorted) |
| `win_count` | int64 | Votes where model_a won |
| `lose_count` | int64 | Votes where model_b won |
| `tie_count` | int64 | Tie votes (including normalized bothbad) |

#### proxy_results.csv

| Column | dtype | Description |
|--------|-------|-------------|
| `proxy` | str | "proxy1_prompt_tokens" \| "proxy2_vote_entropy" \| "proxy3_correction_freq" |
| `tau` | float64 | Mann-Kendall tau |
| `p` | float64 | p-value |
| `significant` | bool | p < significance_threshold |
| `method` | str | "kendalltau" \| "hamed_rao" |
| `ci_low` | float64 | Bootstrap 95% CI lower bound |
| `ci_high` | float64 | Bootstrap 95% CI upper bound |
| `n_months` | int64 | Number of monthly bins used |

---

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Argparse config schema | CLI args, validation, results.json schema, CSV schemas |
