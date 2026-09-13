# Logic: H-E1 (Error Class Independence Verification)

**Type:** EXISTENCE (PoC) | Gate: MUST_WORK (Jaccard < 0.30)

Applied: standard generic eval-pipeline / set-overlap-analysis pattern (no close KB match; not a DL model, no tensors)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs, no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Data Loading [Complexity: 10, Budget: 3+2+3+2]

**Applied**: openai/human-eval `read_problems()` standard loader

### API Signatures

```python
# code/data.py

def load_humaneval_problems() -> dict[str, dict]:
    """Load 164 HumanEval problems via human_eval.data.read_problems()."""
    ...

def load_verus_task_ids() -> set[str]:
    """Return 23 task_ids with formal specs (HumanEval-Verus subset)."""
    ...

def generate_samples(
    model_name: str,
    problems: dict[str, dict],
    n: int = 10,
    temperature: float = 0.2,
) -> list[dict]:
    """Generate n completions/problem. CodeLlama via transformers, gpt-4 via OpenAI API."""
    # returns list of {"task_id": str, "completion": str, "model": str}
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_humaneval_problems | Wrap `human_eval.data.read_problems()` |
| L-1-2 | load_verus_task_ids | Hardcode/fetch 23 Verus task_id set |
| L-1-3 | generate_samples (CodeLlama) | HF `AutoModelForCausalLM.generate`, seed=42, temp=0.2, n=10 |
| L-1-4 | generate_samples (GPT-4) | OpenAI chat completions, n=10, temp=0.2, backoff on rate limit |

---

## A-2: Grammar Strategy [Complexity: 8, Budget: 2+2+3+1]

**Applied**: AST-based syntax check + syncode-style constrained decoding

### API Signatures

```python
# code/strategies.py

def check_syntax(code: str) -> bool:
    """True if `ast.parse(code)` succeeds."""
    ...

def apply_grammar_constraints(code: str) -> str:
    """Re-decode/repair code under Python CFG (syncode) to fix syntax errors."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | check_syntax | `try: ast.parse(code); return True except SyntaxError: return False` |
| L-2-2 | apply_grammar_constraints | Integrate syncode grammar-constrained regeneration |
| L-2-3 | grammar loop in run_verification_strategies | baseline vs constrained syntax compare, add task_id to `grammar` set |
| L-2-4 | fallback | If syncode unavailable, minimal indent/paren-balance repair heuristic |

---

## A-3: Static Analysis Strategy [Complexity: 8, Budget: 2+2+3+1]

**Applied**: Bandit + Pylint CLI integration, standard feedback-loop pattern

### API Signatures

```python
# code/strategies.py

def run_static_analysis(code: str) -> list[dict]:
    """Run Bandit + Pylint on code string (temp file). Returns combined issue list."""
    # each issue: {"tool": "bandit"|"pylint", "severity": str, "msg": str}
    ...

def apply_static_feedback(code: str, issues: list[dict]) -> str:
    """Regenerate/patch code using issues as feedback prompt."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | run_static_analysis (bandit) | Write code to tmp `.py`, run `bandit -f json`, parse issues |
| L-3-2 | run_static_analysis (pylint) | Run `pylint --output-format=json`, parse issues, merge with bandit |
| L-3-3 | apply_static_feedback | Prompt model with issues, regenerate; track before/after issue counts |
| L-3-4 | static loop wiring | `len(fixed_issues) < len(baseline_issues)` -> add task_id to `static` set |

---

## A-4: SMT Repair Strategy [Complexity: 9, Budget: 2+3+3+1]

**Applied**: Z3 Python bindings for spec verification, Verus-subset scoping

### API Signatures

```python
# code/strategies.py

def has_formal_spec(task_id: str, verus_ids: set[str]) -> bool:
    """task_id in verus_ids."""
    ...

def verify_spec(code: str, task_id: str) -> bool:
    """Translate code postconditions to Z3 constraints, check SAT/UNSAT."""
    ...

def smt_guided_repair(code: str, task_id: str) -> str:
    """Use Z3 counterexample/unsat core to guide code repair."""
    ...
```

### Pseudo-code (SMT verify/repair loop, non-trivial)

```
1. spec = load_verus_spec(task_id)          # pre/post conditions
2. solver = z3.Solver()
3. solver.add(encode(code, spec))
4. if solver.check() == sat: return True    # spec holds
5. else: extract counterexample -> patch code -> re-verify (bounded retries)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | has_formal_spec | Membership check against 23-id Verus set |
| L-4-2 | verify_spec | Encode pre/post conditions to Z3, solver.check() |
| L-4-3 | smt_guided_repair | Counterexample-guided patch loop, bounded iterations |
| L-4-4 | smt loop wiring | Only run on Verus subset; baseline fail -> repaired pass -> add to `smt` set |

---

## A-5: Overlap Analysis [Complexity: 5, Budget: 1+2+1+1]

**Applied**: Standard Jaccard set-overlap metric

### API Signatures

```python
# code/overlap.py

def jaccard_index(set_a: set, set_b: set) -> float:
    """|A∩B| / |A∪B|, 0.0 if union empty."""
    ...

def compute_jaccard_overlap(sets: dict[str, set]) -> dict[str, float]:
    """Pairwise Jaccard for (grammar,static), (grammar,smt), (static,smt) + mean."""
    # returns {"grammar_vs_static": float, "grammar_vs_smt": float,
    #          "static_vs_smt": float, "mean": float}
    ...

def gate_check(overlaps: dict[str, float], threshold: float = 0.30) -> bool:
    """True iff all pairwise (non-mean) values < threshold."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | jaccard_index | `len(a&b)/len(a|b)` with zero-union guard |
| L-5-2 | compute_jaccard_overlap | Loop 3 fixed pairs, add mean key |
| L-5-3 | gate_check | `all(v < threshold for k,v in overlaps.items() if k != "mean")` |
| L-5-4 | per-model variant | Call above per model_name, produce `overlaps_by_model` dict |

---

## A-6: Visualization [Complexity: 6, Budget: 2+1+1+2]

**Applied**: matplotlib + matplotlib_venn standard plotting

### API Signatures

```python
# code/visualize.py

def plot_jaccard_bar(overlaps: dict[str, float], threshold: float, out_path: str) -> None:
    """Bar chart: 3 pairwise Jaccard values + horizontal threshold line."""
    ...

def plot_venn(sets: dict[str, set], out_path: str) -> None:
    """3-circle Venn (matplotlib_venn.venn3) of grammar/static/smt sets."""
    ...

def plot_per_model_comparison(overlaps_by_model: dict[str, dict], out_path: str) -> None:
    """Grouped bar chart: Jaccard values, CodeLlama vs GPT-4."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | plot_jaccard_bar | matplotlib bar + `axhline(threshold, ls="--")`, save PNG |
| L-6-2 | plot_venn | `venn3([grammar, static, smt], set_labels=(...))`, save PNG |
| L-6-3 | plot_per_model_comparison | grouped bar, x=pair, hue=model |
| L-6-4 | figure I/O | Ensure `figures/` dir exists, dpi=150, tight_layout |

---

## A-7: Orchestration + Run [Complexity: 7, Budget: 2+3+1+1]

**Applied**: Standard main() pipeline orchestration

### API Signatures

```python
# code/run_experiment.py

def main() -> None:
    """
    1. load_humaneval_problems(), load_verus_task_ids()
    2. generate_samples() per model in config.MODELS -> pooled samples
    3. run_verification_strategies(samples, verus_ids) -> {"grammar","static","smt"} sets
       (pooled across models + per-model for A-6.3)
    4. compute_jaccard_overlap() pooled + per-model; gate_check()
    5. plot_jaccard_bar / plot_venn / plot_per_model_comparison -> figures/
    6. save results/overlap_data.json
    """
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | data + sample generation wiring | Call A-1 functions for both models, pool samples |
| L-7-2 | strategies + overlap wiring | Call A-2/A-3/A-4 via `run_verification_strategies`, then A-5 |
| L-7-3 | gate decision + logging | Print/log gate_check result, exit code reflects pass/fail |
| L-7-4 | save artifacts | Write `results/overlap_data.json`, call all 3 A-6 plot functions |

---

## `run_verification_strategies` Signature (referenced by A-2/A-3/A-4/A-7)

```python
def run_verification_strategies(
    samples: list[dict], verus_ids: set[str]
) -> dict[str, set[str]]:
    """Apply grammar/static/smt strategies over samples. Returns {"grammar": set, "static": set, "smt": set}."""
    ...
```

---

## Notes

- Green-field: no External Dependencies section (no base hypothesis).
- No tensor shapes: this is a set-overlap analysis pipeline, not a neural module — omitted per EXISTENCE PoC brevity rule.
- A-1 and A-4 are Medium complexity (budget 2 subtasks each per allocation note in architecture doc); all tasks kept to exactly 4 subtasks matching architecture breakdown column.
