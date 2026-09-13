# Logic: H-M2
# Depth-Slope Differential Analysis: MOHAWK-SSM vs LAWCAT

**Applied**: Standard rpy2/statsmodels strategy pattern (KB: no domain match — designed from spec)
**Applied**: Positional index alignment within category (KB: no domain match — designed from traversal analysis)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 reads H-E1 output files)
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/evaluate.py`, `docs/youra_research/h-e1/code/config.py`
**Relevant Symbols**:
- `CATEGORY_MAP` — evaluate.py line 24 (dict literal, maps human-readable → canonical snake_case)
- `RETRIEVAL_HEAVY` — config.py line 64 (set: `{"multi_doc_qa", "long_structured_data"}`)
- `evaluate_model_longbench` — evaluate.py line 82 (writes `output["per_example"]` list at line 265)
- `per_example_results.append(...)` — evaluate.py lines 230–236: keys are `category`, `pred`, `label`, `correct`, `scores`

---

## External Dependencies API

### H-E1 Output Schema (Verified from actual code)

```python
# Output JSON written by evaluate.py lines 255–268
# Top-level key: "per_example"  (NOT a flat list at root!)
output = {
    "model": str,                  # e.g. "mohawk"
    "model_path": str,
    "n_examples": int,
    "overall_accuracy": float,
    "per_category_accuracy": dict[str, float],
    "per_category_counts": {"correct": dict, "total": dict},
    "per_example": [               # ← THIS is what H-M2 reads
        {
            "category": str,       # canonical snake_case e.g. "multi_doc_qa"
            "pred": str,           # "A" | "B" | "C" | "D"
            "label": str,          # "A" | "B" | "C" | "D"  (NOT "answer"!)
            "correct": int,        # 0 or 1
            "scores": dict[str, float],  # {"A": logit, "B": logit, ...}
        },
        ...
    ],
}
```

**Critical field mismatches vs PRD assumptions:**

| PRD Field | Actual H-E1 Field | Action |
|-----------|-------------------|--------|
| `domain` | `category` (canonical) | Use `category` directly |
| `answer` | `label` | Rename on load |
| `context` | ABSENT | Load from LongBench v2 HF |
| `_id` | ABSENT | No ID — use positional alignment |
| flat list | `output["per_example"]` | Unwrap one level |

**Output file paths** (from config.py `RESULTS_DIR = HYPOTHESIS_DIR / "results"`):
- `docs/youra_research/h-e1/results/mohawk_longbench.json`
- `docs/youra_research/h-e1/results/lawcat_longbench.json`

**CATEGORY_MAP** (exact keys from evaluate.py lines 25–38):
```python
CATEGORY_MAP = {
    "single-document QA": "single_doc_qa",
    "multi-document QA": "multi_doc_qa",
    "long in-context learning": "long_in_context_learning",
    "long-dialogue history understanding": "long_dialogue",
    "code repository understanding": "code_repo",
    "long structured data understanding": "long_structured_data",
    # identity fallbacks for already-canonical inputs
    "single_doc_qa": "single_doc_qa",
    "multi_doc_qa": "multi_doc_qa",
    "long_in_context_learning": "long_in_context_learning",
    "long_dialogue": "long_dialogue",
    "code_repo": "code_repo",
    "long_structured_data": "long_structured_data",
}
```

**RETRIEVAL_HEAVY** (config.py line 65): `{"multi_doc_qa", "long_structured_data"}`

**LongBench v2 HF dataset** (evaluate.py line 172–177):
```python
dataset = load_dataset("THUDM/LongBench", "v2", split="train")
# Per-example fields relevant to H-M2:
# example["context"]   → str, the long document
# example["input"]     → str, the question
# example["options"]   → list[str], MCQ choices [A_text, B_text, C_text, D_text]
# example["answer"]    → str, correct letter "A"/"B"/"C"/"D"
# example["category"]  → str, human-readable (needs CATEGORY_MAP normalization)
# NOTE: H-E1 iterates this dataset in-order, no shuffle → positional alignment is valid
```

---

## A-3: DataLoader — LongBench v2 Context Merge [Complexity: 11, Medium]

### L-3-1: load_longbench_v2()

```python
def load_longbench_v2(
    hf_id: str = "THUDM/LongBench",
    hf_config: str = "v2",
    split: str = "train",
    cache_dir: str | None = None,
) -> dict[str, list[dict]]:
    """
    Load LongBench v2 and group by canonical category.
    Returns {canonical_category: [examples in original order]}.
    Order preservation is critical — H-E1 iterated in this exact order.
    """
    ...
```

**Pseudo-code:**
```
1. dataset = load_dataset(hf_id, hf_config, split=split, cache_dir=cache_dir)
2. result: dict[str, list[dict]] = defaultdict(list)
3. for example in dataset:          # iterate in original order — NO shuffle
       raw_cat = example["category"]
       canon = _map_category(raw_cat)   # same logic as H-E1 evaluate.py _map_category()
       result[canon].append({
           "context":     example["context"],
           "question":    example["input"],
           "options":     example["options"],   # list[str], len == 4
           "answer_text": example["options"][ord(example["answer"]) - ord("A")],
           "answer_letter": example["answer"],
       })
4. return dict(result)
```

**Output shape:**
```python
# Returns: {"multi_doc_qa": [...], "long_structured_data": [...], ...}
# Each entry: {"context": str, "question": str, "options": list[str],
#              "answer_text": str, "answer_letter": str}
```

**_map_category() — exact copy from H-E1 evaluate.py (lines 42–53):**
```python
def _map_category(raw: str) -> str:
    """Normalize LongBench v2 category string to canonical form. Copied from H-E1."""
    if raw in CATEGORY_MAP:
        return CATEGORY_MAP[raw]
    raw_lower = raw.lower().strip()
    for k, v in CATEGORY_MAP.items():
        if raw_lower == k.lower():
            return v
    return raw_lower.replace(" ", "_").replace("-", "_")
```

---

### L-3-2: merge_context()

**Alignment rationale**: H-E1 `evaluate_model_longbench()` iterates `dataset` with a simple `for example in dataset` (evaluate.py line 186), no shuffle, no sort. It appends to `per_example_results` in arrival order within that iteration. Therefore, for each canonical category, the i-th H-E1 record corresponds exactly to the i-th example in the same-category slice of the HF dataset.

```python
def merge_context(
    h_e1_records: list[dict],
    longbench_by_category: dict[str, list[dict]],
) -> list[dict]:
    """
    Align H-E1 records with LongBench v2 by positional index within category.
    Adds 'context', 'question', 'answer_text' to each H-E1 record (in-place + returned).
    Logs a warning if any category has count mismatch (uses min-length truncation).
    """
    ...
```

**Pseudo-code:**
```
1. # Build per-category position counters
   category_cursors: dict[str, int] = defaultdict(int)

2. merged: list[dict] = []
   for rec in h_e1_records:
       cat = rec["category"]                       # e.g. "multi_doc_qa"
       idx = category_cursors[cat]
       category_cursors[cat] += 1

       lb_examples = longbench_by_category.get(cat, [])
       if idx >= len(lb_examples):
           # ponytail: skip examples past LB length, log warning
           warnings.warn(f"Category {cat}: H-E1 has more records than LB v2 ({idx+1} > {len(lb_examples)})")
           rec["context"] = ""
           rec["question"] = ""
           rec["answer_text"] = ""
       else:
           lb = lb_examples[idx]
           rec["context"]     = lb["context"]
           rec["question"]    = lb["question"]
           rec["answer_text"] = lb["answer_text"]

       merged.append(rec)

3. return merged
```

**Edge cases:**
- Category in H-E1 but not in LB v2: `context=""`, `question=""` — depth_computer will hit fallback
- Category count mismatch: warn + truncate (H-E1 may have skipped invalid-label examples; see evaluate.py line 193–194 `if not label or label not in valid_answers: continue`)

**Subtasks [2/3 used for A-3]:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_longbench_v2 | HF dataset load, CATEGORY_MAP normalization, grouping by canonical category |
| L-3-2 | merge_context | Positional alignment algorithm, cursor-per-category, field extraction, mismatch handling |

---

## A-5: RegressionFitter [Complexity: 14, High]

### L-5-1: fit_glmer_rpy2()

```python
def fit_glmer_rpy2(df: "pd.DataFrame") -> dict:
    """
    Primary GLMM via rpy2 + lme4::glmer.
    df columns: depth_percentile (float), correct (int 0/1), task_id (str).
    Returns {beta, ci_low, ci_high, p_value, method}.
    Raises ImportError if rpy2 or R packages unavailable.
    """
    ...
```

**Exact rpy2 call sequence:**
```python
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

pandas2ri.activate()

lme4    = importr("lme4")
lmerTest = importr("lmerTest")  # shadows lme4::glmer to add Satterthwaite df

# Convert DataFrame to R
r_df = pandas2ri.py2rpy(df)  # df must have columns: depth_percentile, correct, task_id

# Fit model — correct is 0/1 integer, binomial family
formula = ro.Formula("correct ~ depth_percentile + (1|task_id)")
model   = lme4.glmer(formula, data=r_df, family=ro.r("binomial"))

# Extract fixed-effect coefficient for depth_percentile
coef_table = ro.r("summary")(model).rx2("coefficients")
# coef_table rows: (Intercept), depth_percentile
# columns: Estimate, Std. Error, z value, Pr(>|z|)
beta    = float(coef_table.rx("depth_percentile", "Estimate")[0])
p_value = float(coef_table.rx("depth_percentile", "Pr(>|z|)")[0])

# 95% CI via confint (profile likelihood; slower but accurate for GLMM)
# confint returns matrix with rows ".sig01", "(Intercept)", "depth_percentile"
ci_matrix = ro.r("confint")(model, parm="beta_", method="Wald")  # Wald for speed
ci_row    = ci_matrix.rx("depth_percentile", True)
ci_low    = float(ci_row[0])
ci_high   = float(ci_row[1])

return {
    "beta": beta,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": p_value,
    "method": "glmer",
}
```

**Note on confint method**: Use `method="Wald"` for runtime (<10 min constraint); profile likelihood would be more accurate but slow on N~150. Document as `# ponytail: Wald CI, use method="profile" for publication-quality`.

---

### L-5-2: fit_mixedlm_statsmodels()

```python
def fit_mixedlm_statsmodels(df: "pd.DataFrame") -> dict:
    """
    Fallback: linear mixed model (approximation for binary outcome).
    df columns: depth_percentile (float), correct (int 0/1), task_id (str).
    Returns {beta, ci_low, ci_high, p_value, method, approximation_warning}.
    """
    ...
```

**Implementation:**
```python
import statsmodels.formula.api as smf

# Linear mixed model — linear approximation for binary outcome
# ponytail: LMM not logistic; fine for PoC, replace with glmer if R available
model  = smf.mixedlm("correct ~ depth_percentile", data=df, groups=df["task_id"])
result = model.fit(reml=False)   # ML not REML for fixed-effect inference

beta    = float(result.params["depth_percentile"])
ci      = result.conf_int()       # DataFrame: columns [0, 1], index = param names
ci_low  = float(ci.loc["depth_percentile", 0])
ci_high = float(ci.loc["depth_percentile", 1])
p_value = float(result.pvalues["depth_percentile"])

return {
    "beta": beta,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": p_value,
    "method": "mixedlm_approx",
    "approximation_warning": True,
}
```

---

### L-5-3: fit_model() — Strategy Dispatcher

```python
def fit_model(records: list[dict], model_label: str) -> dict:
    """
    Strategy dispatcher: try rpy2 glmer, fall back to statsmodels mixedlm.
    Constructs DataFrame; adds model_label to returned dict.
    records must have keys: depth_percentile (float), correct (int), category (str).
    """
    ...
```

**Implementation:**
```python
import pandas as pd

df = pd.DataFrame({
    "depth_percentile": [r["depth_percentile"] for r in records],
    "correct":          [int(r["correct"])       for r in records],
    "task_id":          [r["category"]           for r in records],
    # task_id = category (e.g. "multi_doc_qa", "long_structured_data")
    # these form the random-intercept groups; 2 groups is minimal but acceptable for PoC
    # ponytail: with only 2 groups, random intercept is weakly identified; glmer may warn
})

# Validate: both outcome classes present
if df["correct"].nunique() < 2:
    raise ValueError(f"[{model_label}] Only one outcome class in retrieval subset — cannot fit regression")

try:
    result = fit_glmer_rpy2(df)
except (ImportError, Exception) as e:
    # ImportError: rpy2 not installed or R unavailable
    # Other exceptions: convergence failure, R package missing
    import warnings
    warnings.warn(f"[{model_label}] rpy2/glmer failed ({type(e).__name__}: {e}), falling back to statsmodels MixedLM")
    result = fit_mixedlm_statsmodels(df)

result["model_label"] = model_label
return result
```

**Unified output schema:**
```python
{
    "beta":                 float,   # depth_percentile coefficient (negative = deeper → worse)
    "ci_low":               float,   # 95% CI lower bound
    "ci_high":              float,   # 95% CI upper bound
    "p_value":              float,   # raw (pre-Holm) p-value for depth_percentile
    "method":               str,     # "glmer" | "mixedlm_approx"
    "model_label":          str,     # "mohawk_ssm" | "lawcat"
    "approximation_warning": bool,   # True only for mixedlm_approx path
}
```

---

### L-5-4: apply_holm_correction()

```python
def apply_holm_correction(p_values: list[float]) -> list[float]:
    """
    Holm-Bonferroni correction for exactly 2 tests.
    Returns corrected p-values in same order as input.
    """
    ...
```

**Pseudo-code (exact algorithm for n=2):**
```
Given p_values = [p_ssm, p_lawcat]:

1. Sort ascending: indexed_sorted = sorted(enumerate(p_values), key=lambda x: x[1])
   e.g. [(0, 0.003), (1, 0.12)]  for p_ssm=0.003, p_lawcat=0.12

2. n = 2  # HOLM_N_TESTS from config
   corrected = [None, None]

3. For rank 0 (smallest p):  p_corr[rank=0] = min(p * (n - 0), 1.0) = min(p * 2, 1.0)
   For rank 1 (largest p):   p_corr[rank=1] = min(p * (n - 1), 1.0) = min(p * 1, 1.0)

   # Step-down: p_corr[rank] = max(p_corr[rank], p_corr[rank-1]) to ensure monotonicity
   p_corr[rank=1] = max(p_corr[rank=1], p_corr[rank=0])

4. Write back to original positions:
   corrected[original_index_of_rank_0] = p_corr[rank=0]
   corrected[original_index_of_rank_1] = p_corr[rank=1]

5. return corrected  # [corrected_p_ssm, corrected_p_lawcat]
```

**Example:**
```
p_values = [0.003, 0.12]
sorted: [(0, 0.003), (1, 0.12)]
rank=0: 0.003 * 2 = 0.006
rank=1: 0.12  * 1 = 0.12 → max(0.12, 0.006) = 0.12
result: [0.006, 0.12]
```

**Subtasks [4/4 used for A-5]:**

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | fit_glmer_rpy2 | rpy2+lme4::glmer full call sequence, Wald CI, coefficient extraction |
| L-5-2 | fit_mixedlm_statsmodels | statsmodels MixedLM, ML fit, conf_int extraction, approximation_warning flag |
| L-5-3 | fit_model (dispatcher) | DataFrame construction, ImportError catch, unified output schema |
| L-5-4 | apply_holm_correction | Step-down Holm algorithm for n=2, monotonicity enforcement |

---

## Notes for Phase 4 Coder

1. **H-E1 output path**: actual path is `docs/youra_research/h-e1/results/{model}_longbench.json` (from config.py `RESULTS_DIR = HYPOTHESIS_DIR / "results"` where HYPOTHESIS_DIR is `h-e1/`). Probe alt-paths if missing.

2. **Schema unwrap**: `json.load(f)["per_example"]` — the list is nested, not at root.

3. **Field rename**: H-E1 uses `label` for the correct answer letter. PRD calls it `answer`. Use `label` throughout internal code, only alias in reporter output if needed.

4. **Positional alignment validity**: H-E1 evaluate.py line 193 skips examples with invalid labels (`if not label or label not in valid_answers: continue`). This means H-E1 per_example count may be less than LB v2 count for a category. The cursor approach handles this correctly — H-E1 records map to the subset of LB v2 examples that had valid labels, but we don't know which ones were skipped. This is a known approximation: `# ponytail: positional alignment assumes no label-skipped gaps in LB v2; true _id merge would require H-E1 rerun saving _id`.

5. **Random effects groups**: With only 2 groups (`multi_doc_qa`, `long_structured_data`), lme4 may emit a singular fit warning. This is expected and acceptable for PoC — do not suppress, just log.
