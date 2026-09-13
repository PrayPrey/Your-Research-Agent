# Architecture: H-C1 (CONDITION)

Applied: no directly relevant KB pattern found; reused h-e1's stratified-test structure instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1 code read directly (Serena project not registered for this workspace; verified via direct file read per "trust actual code" rule)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `run.py` calls `cache_scores(df, ...)` on the full post-classification `df`, so `outputs/rm_scores.parquet` already contains `prompt`, `battle_id`, `human_entropy`, `rm_variance`, `mode` columns. h-c1 can load this single file directly — no need to re-run mode classification.

---

## File Structure (Minimal - CONDITION)

```
h-c1/code/
├── config.py
├── categorize.py
├── analysis.py
├── run.py
└── outputs/
    ├── category_mode_distribution.json
    ├── ratio_analysis.json
    └── prompt_categories.parquet
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| RM scores + modes (data, not code) | `pd.read_parquet(H_E1_SCORES_PATH)` | `h-e1/code/outputs/rm_scores.parquet` |

**Verified from**: `h-e1/code/run.py` (actual pipeline) — no h-e1 function calls are reused, only its output artifact. Columns available: `battle_id, prompt, resp_a, resp_b, model_a, model_b, winner, <rm>_score_*, <rm>_norm_*, rm_variance, human_entropy, mode`.

---

## Modules

### config.py

**Dependencies**: none

```python
H_E1_SCORES_PATH = "../../h-e1/code/outputs/rm_scores.parquet"
OUTPUT_DIR = "outputs/"
MIN_PER_CATEGORY = 500
SUBJECTIVE_CATEGORIES = {"creative_writing", "general"}
OBJECTIVE_CATEGORIES = {"coding", "math", "hard_prompts"}
OBJECTIVE_KEYWORDS = [...]   # from experiment brief
SUBJECTIVE_KEYWORDS = [...]  # from experiment brief
```

### categorize.py

**Dependencies**: config.py

```python
def classify_prompt(prompt: str) -> str: ...  # 'objective' | 'subjective' | 'ambiguous'
def categorize_battles(df: "pd.DataFrame") -> "pd.DataFrame": ...
    # adds 'category' col; uses df['category'] tag if present, else classify_prompt(df['prompt'])
def filter_min_count(df: "pd.DataFrame", min_n: int) -> "pd.DataFrame": ...
    # raises ValueError if either category < min_n
```

### analysis.py

**Dependencies**: scipy, numpy

```python
def category_mode3_counts(df: "pd.DataFrame") -> dict: ...
    # {'subjective': {'mode3': a, 'total': a+b}, 'objective': {'mode3': c, 'total': c+d}}
def two_proportion_ztest(a: int, n_subj: int, c: int, n_obj: int) -> dict: ...
    # one-sided z-test subj > obj -> {p_subj, p_obj, z, p_value}
def ratio_ci_log(a: int, n_subj: int, c: int, n_obj: int) -> dict: ...
    # log-transform 95% CI -> {ratio, ci_95_lower, ci_95_upper}
def cohens_h(p1: float, p2: float) -> float: ...
def classify_result(ratio: float, p_value: float) -> str: ...
    # 'CONFIRMED' | 'FALSIFIED' | 'INCONCLUSIVE'
```

### run.py

**Dependencies**: config.py, categorize.py, analysis.py

```python
def main() -> None: ...
    # load rm_scores.parquet -> categorize_battles -> exclude ambiguous ->
    # filter_min_count -> category_mode3_counts -> ztest + ratio_ci + cohens_h ->
    # classify_result -> serialize 3 output files
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Config + keyword lists | Define paths, category mappings, keyword lists from brief | 4 | 1+1+1+1 |
| C-2 | Prompt categorization | Arena-tag primary path + keyword fallback classifier | 8 | 2+1+3+2 |
| C-3 | Category filtering | Exclude ambiguous, enforce min-500 per category | 5 | 1+1+1+2 |
| C-4 | Mode 3 stratified counts | Compute mode3/total per category from loaded parquet | 5 | 1+1+2+1 |
| C-5 | Two-proportion z-test | Pooled-proportion z-test, one-sided p-value | 6 | 1+1+3+1 |
| C-6 | Ratio CI + effect size | Log-transform 95% CI for ratio, Cohen's h | 6 | 1+1+3+1 |
| C-7 | Result classification | Map (ratio, p_value) to CONFIRMED/FALSIFIED/INCONCLUSIVE | 4 | 1+1+1+1 |
| C-8 | Pipeline integration + outputs | Wire run.py, serialize JSON/parquet artifacts | 6 | 1+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8]
