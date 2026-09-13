# Logic: H-C1 (CONDITION)

Applied: pandas merge-join pattern for cross-artifact enrichment (no direct KB match; standard pandas).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena not registered for this workspace — verified h-e1 API via direct file read (`Read` tool), per architecture's precedent.
**Analyzed Path**: `docs/youra_research/h-e1/code/{run.py, data.py, rm_scoring.py, mode_classify.py, config.py}`
**Relevant Symbols**: `cache_scores`, `load_battles`, `assign_modes`, `mode_distribution`, `CONFIG`

**Correction to architecture doc**: `03_architecture.md` states `rm_scores.parquet` contains `prompt, mode, human_entropy, rm_variance`. This is **incorrect** — verified from actual code:

```python
# h-e1/code/rm_scoring.py:120-124
def cache_scores(df: pd.DataFrame, path: str) -> None:
    score_cols = ["battle_id"] + [c for c in df.columns if "_score_" in c]
    df[score_cols].to_parquet(path, index=False)  # ONLY battle_id + *_score_* cols
```

`rm_scores.parquet` = `battle_id` + `<rm>_score_a/b` columns only. `outputs/results.csv` (h-e1/code/run.py:117) has `battle_id, human_entropy, rm_variance, mode` but no `prompt`. **Neither file has `prompt` or Arena category tags.** h-c1 must reload the raw dataset for `prompt`/category and merge on `battle_id`.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
CONFIG = {"dataset_id": "lmsys/lmsys-arena-human-preference-55k", ...}

# From: h-e1/code/data.py (ACTUAL CODE)
def load_battles(dataset_id: str) -> pd.DataFrame: ...
    # datasets.load_dataset(dataset_id, split="train").to_pandas()
def filter_valid(df: pd.DataFrame) -> pd.DataFrame: ...
    # keeps rows with valid winner + non-empty prompt/response_a/response_b
def prepare_battles(df: pd.DataFrame) -> pd.DataFrame: ...
    # adds resp_a, resp_b columns
```

**Artifacts used (not functions)**:
- `h-e1/code/outputs/results.csv` — cols: `battle_id, human_entropy, rm_variance, mode` (int 1-4)

**Verified from**: `h-e1/code/` actual implementation.

---

## C-1: Config + keyword lists [Complexity: 4]

```python
# config.py
H_E1_DIR = "../../h-e1/code/"
H_E1_RESULTS_CSV = H_E1_DIR + "outputs/results.csv"
DATASET_ID = "lmsys/lmsys-arena-human-preference-55k"  # must match h-e1 CONFIG["dataset_id"]
OUTPUT_DIR = "outputs/"
MIN_PER_CATEGORY = 500

SUBJECTIVE_CATEGORIES = {"creative_writing", "general"}
OBJECTIVE_CATEGORIES = {"coding", "math", "hard_prompts"}

OBJECTIVE_KEYWORDS = ["def ", "code", "algorithm", "function", "class ", "import ",
                       "solve", "equation", "calculate", "compute", "bug", "compile"]
SUBJECTIVE_KEYWORDS = ["write a story", "poem", "imagine", "creative", "opinion",
                        "essay", "narrative", "describe how you feel"]
```

Subtasks: none (budget 0).

---

## C-2: Prompt categorization [Complexity: 8]

**Applied**: Standard pandas `.apply` classifier pattern.

```python
def classify_prompt(prompt: str) -> str:
    """Keyword fallback. Returns 'objective' | 'subjective' | 'ambiguous'."""
    ...

def categorize_battles(df: pd.DataFrame) -> pd.DataFrame:
    """Adds 'category' col in {'objective','subjective','ambiguous'}.
    Uses df['category'] tag if present (mapped via *_CATEGORIES sets),
    else classify_prompt(df['prompt']).
    """
    ...
```

### Pseudo-code

```
1. if 'category' column exists in df (Arena tag):
     map raw tag -> SUBJECTIVE_CATEGORIES -> 'subjective'
                  -> OBJECTIVE_CATEGORIES -> 'objective'
                  -> else -> 'ambiguous'
2. else (fallback path, expected — dataset has no tags):
     for each prompt: classify_prompt(prompt) via keyword matching
       - contains any OBJECTIVE_KEYWORDS and no SUBJECTIVE_KEYWORDS -> 'objective'
       - contains any SUBJECTIVE_KEYWORDS and no OBJECTIVE_KEYWORDS -> 'subjective'
       - both or neither -> 'ambiguous'
3. return df with new 'category' column (str)
```

Subtasks: none (budget 0).

---

## C-3: Category filtering [Complexity: 5]

```python
def exclude_ambiguous(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where category == 'ambiguous'."""
    ...

def filter_min_count(df: pd.DataFrame, min_n: int = 500) -> pd.DataFrame:
    """Raises ValueError if count('subjective') < min_n or count('objective') < min_n."""
    ...
```

Subtasks: none (budget 0).

---

## C-4: Mode 3 stratified counts [Complexity: 5]

```python
def category_mode3_counts(df: pd.DataFrame) -> dict:
    """df must have 'category' (objective|subjective) and 'mode' (int) cols.
    Returns {'subjective': {'mode3': int, 'total': int},
             'objective':  {'mode3': int, 'total': int}}
    """
    ...
```

### Tensor/Data shapes

| Variable | Type | Note |
|----------|------|------|
| df['mode'] | int64 Series | values in {1,2,3,4}, from h-e1 `assign_modes` |
| df['category'] | str Series | 'objective' \| 'subjective' (post-filter) |

Subtasks: none (budget 0).

---

## C-5: Two-proportion z-test [Complexity: 6]

```python
def two_proportion_ztest(a: int, n_subj: int, c: int, n_obj: int) -> dict:
    """One-sided z-test: p_subj > p_obj (pooled-proportion SE).
    Returns {'p_subj': float, 'p_obj': float, 'z': float, 'p_value': float}
    """
    ...
```

### Pseudo-code

```
p_subj = a / n_subj
p_obj  = c / n_obj
p_pool = (a + c) / (n_subj + n_obj)
se = sqrt(p_pool * (1 - p_pool) * (1/n_subj + 1/n_obj))
z = (p_subj - p_obj) / se
p_value = 1 - scipy.stats.norm.cdf(z)   # one-sided, subj > obj
```

Subtasks: none (budget 0).

---

## C-6: Ratio CI + effect size [Complexity: 6]

```python
def ratio_ci_log(a: int, n_subj: int, c: int, n_obj: int) -> dict:
    """Log-transform 95% CI for ratio p_subj/p_obj.
    Returns {'ratio': float, 'ci_95_lower': float, 'ci_95_upper': float}
    """
    ...

def cohens_h(p1: float, p2: float) -> float:
    """2 * (arcsin(sqrt(p1)) - arcsin(sqrt(p2)))"""
    ...
```

### Pseudo-code

```
p_subj = a / n_subj; p_obj = c / n_obj
ratio = p_subj / p_obj
se_log = sqrt((1-p_subj)/(a) + (1-p_obj)/(c))   # delta method on log(ratio)
log_ratio = log(ratio)
ci_lower = exp(log_ratio - 1.96 * se_log)
ci_upper = exp(log_ratio + 1.96 * se_log)
```

Subtasks: none (budget 0).

---

## C-7: Result classification [Complexity: 4]

```python
def classify_result(ratio: float, p_value: float, alpha: float = 0.05) -> str:
    """Returns 'CONFIRMED' | 'FALSIFIED' | 'INCONCLUSIVE'.
    CONFIRMED: ratio > 1.5 and p_value < alpha
    FALSIFIED: ratio < 1.0
    else: INCONCLUSIVE
    """
    ...
```

Subtasks: none (budget 0).

---

## C-8: Pipeline integration + outputs [Complexity: 6]

```python
def load_and_merge() -> pd.DataFrame:
    """Load raw dataset (for prompt/category tag), merge with h-e1 results.csv
    (for mode) on battle_id. Falls back to positional index-as-battle_id if
    h-e1 df lacked battle_id column originally (see h-e1 rm_scoring.py:81-82).
    """
    ...

def main() -> None: ...
```

### Pseudo-code

```
1. raw = load_battles(DATASET_ID); raw = filter_valid(raw); raw = prepare_battles(raw)
   # must reproduce h-e1's filter_valid/prepare_battles EXACTLY to get matching
   # row order/battle_id, since h-e1 assigns battle_id = range(len(df)) if absent
2. results = pd.read_csv(H_E1_RESULTS_CSV)  # battle_id, human_entropy, rm_variance, mode
3. df = raw.merge(results, on="battle_id", how="inner")
4. df = categorize_battles(df)          # adds 'category'
5. df = exclude_ambiguous(df)
6. df = filter_min_count(df, MIN_PER_CATEGORY)   # raises if <500/category
7. counts = category_mode3_counts(df)
8. zt = two_proportion_ztest(counts['subjective']['mode3'], counts['subjective']['total'],
                              counts['objective']['mode3'], counts['objective']['total'])
9. ci = ratio_ci_log(...)  # same args
10. h = cohens_h(zt['p_subj'], zt['p_obj'])
11. result = classify_result(ci['ratio'], zt['p_value'])
12. write category_mode_distribution.json (counts), ratio_analysis.json (zt+ci+h+result),
    prompt_categories.parquet (df[['battle_id','prompt','category','mode']])
```

Subtasks: none (budget 0).
