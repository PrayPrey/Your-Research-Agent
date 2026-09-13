# Config: H-C1 (CONDITION)

Applied: no directly relevant KB pattern found (searched "config pattern hardcoded dict experiment"); using plain module-level constants per architecture spec.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: `h-e1/code/config*.py` not found on disk (h-e1 code not yet materialized at this path) — used h-e1 architecture doc's own literal `config.py` spec (already verified in `03_architecture.md`) as source of truth instead. No dataclass to inherit from; h-c1 only consumes h-e1's **output artifact** (`rm_scores.parquet`), not h-e1's config object.
**Config Files Found**: None (green-field for h-c1 itself)
**Pattern Used**: Module-level dict/constants (matches h-e1 style, no dataclass in this pipeline)

---

## Format: Module-level constants (dict-style)

All 8 tasks are Low complexity — single fixed pipeline run, no hyperparameter sweep, no subtasks needed (budget: 0).

```python
# config.py

H_E1_SCORES_PATH = "../../h-e1/code/outputs/rm_scores.parquet"
OUTPUT_DIR = "outputs/"

MIN_PER_CATEGORY = 500

SUBJECTIVE_CATEGORIES = {"creative_writing", "general"}
OBJECTIVE_CATEGORIES = {"coding", "math", "hard_prompts"}

# Fallback keyword classifier (used only when Arena category tag absent)
OBJECTIVE_KEYWORDS = [
    "code", "function", "algorithm", "debug", "compile",
    "solve", "equation", "calculate", "proof", "theorem",
]
SUBJECTIVE_KEYWORDS = [
    "write", "story", "poem", "creative", "imagine",
    "opinion", "feel", "describe", "essay",
]

ALPHA = 0.05          # significance level, one-sided z-test
RATIO_SUCCESS_THRESHOLD = 1.5   # CONFIRMED if ratio > 1.5, p < ALPHA
RATIO_FALSIFY_THRESHOLD = 1.0   # FALSIFIED if ratio < 1.0
```

**Non-standard**: `RATIO_SUCCESS_THRESHOLD = 1.5` / `RATIO_FALSIFY_THRESHOLD = 1.0` — directly from PRD success/falsification criteria (FR success table), not a statistical default.

---

## Per-Task Config Notes

### C-1: Config + keyword lists [Low, Budget: 4]
Uses constants above as-is. No subtasks.

### C-2 – C-7: Categorization, filtering, stats [Low each]
No task-specific config beyond the shared constants — functions take `df`/counts as args, thresholds pulled from `config.py`.

### C-8: Pipeline integration [Low, Budget: 6]
Output paths derived from `OUTPUT_DIR`:
```python
CATEGORY_DIST_PATH = OUTPUT_DIR + "category_mode_distribution.json"
RATIO_ANALYSIS_PATH = OUTPUT_DIR + "ratio_analysis.json"
PROMPT_CATEGORIES_PATH = OUTPUT_DIR + "prompt_categories.parquet"
```

**Subtasks**: 0/0 used (all Low complexity per allocation — no decomposition required).

---

## Inherited Configuration (Base Hypothesis)

No inherited dataclass — h-c1 does not import or extend any h-e1 config class. It only reads h-e1's **output data file** (`rm_scores.parquet`) via the path constant `H_E1_SCORES_PATH` above. h-e1's actual `config.py` was not found on disk to verify field-level inheritance; none was needed since no config object is shared, only a file path.
