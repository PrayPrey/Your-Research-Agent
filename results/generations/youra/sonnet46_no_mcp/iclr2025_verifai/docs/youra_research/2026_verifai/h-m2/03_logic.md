# Logic Design: h-m2

**Hypothesis:** h-m2 — Mechanistic Complementarity of mypy/ast Repair vs. SynCode (MECHANISM / INCREMENTAL)
**Date:** 2026-05-10
**Phase:** 3 — Logic Design

Applied: iterative-feedback-repair-loop (Olausson 2023 / SELF-REFINE)
Applied: Jaccard-complement C_score independence null model (bootstrap CI, Bonferroni)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1 code analyzed)
**Status**: API signatures verified from actual h-m1 code files
**Analyzed Path**: `docs/youra_research/20260508_verifai/h-m1/code/`
**Relevant Symbols**:
- `FMDClassifier.__init__(mypy_timeout=30, cleanup_temp_files=True)` — verified from fmd_classifier.py
- `FMDClassifier.classify_completion(completion: str, task_id: str, problem: dict) -> str` — returns `"syntax"`, `"type"`, or `"functional"` (NOT `"type_structural"`)
- `FMDClassifier.classify_pool(pool: Dict[str, List[dict]], problems: Dict[str, dict]) -> Dict[str, List[str]]`
- `BootstrapCI.compute(baseline_rates: np.ndarray, syncode_rates: np.ndarray) -> Tuple[float, float, float, float]` — takes two np.ndarray args
- `TransitionExtractor.extract(baseline_pool, syncode_pool) -> List[dict]` — ast_valid flip, NOT pass@1
- `ExtendedBaselineGenerator.generate_pool(problems, output_path, progress_path, h_e1_pool_path=None)`
- `ExtendedSyncodeGenerator.generate_pool(problems, output_path, progress_path)` — no h_e1_pool_path param

**Critical Notes**:
1. `FMDClassifier` returns `"type"` (not `"type_structural"`) — h-m2 must use `== "type"` when filtering
2. `BootstrapCI.compute()` computes delta between two rate arrays — NOT reusable for C_score bootstrap
3. `TransitionExtractor.extract()` uses ast_valid flip — h-m2 needs separate pass@1 transition extraction

---

## External Dependencies API (Base Hypothesis)

Signatures verified from h-m1 actual code (not specs):

```python
# From: h-m1/code/fmd_classifier.py (ACTUAL CODE)
class FMDClassifier:
    def __init__(self, mypy_timeout: int = 30, cleanup_temp_files: bool = True) -> None: ...
    def classify_completion(self, completion: str, task_id: str, problem: dict) -> str:
        """Returns: 'syntax' | 'type' | 'functional'"""
    def classify_pool(
        self, pool: Dict[str, List[dict]], problems: Dict[str, dict]
    ) -> Dict[str, List[str]]: ...

# From: h-m1/code/bootstrap_ci.py (ACTUAL CODE)
class BootstrapCI:
    def __init__(self, n_bootstrap: int = 10000, alpha: float = 0.05) -> None: ...
    def compute(
        self, baseline_rates: np.ndarray, syncode_rates: np.ndarray
    ) -> Tuple[float, float, float, float]:
        """Returns (delta_mean, ci_lower, ci_upper, p_value)"""

# From: h-m1/code/transition_extractor.py (ACTUAL CODE)
class TransitionExtractor:
    def extract(
        self, baseline_pool: Dict[str, List[dict]], syncode_pool: Dict[str, List[dict]]
    ) -> List[dict]:
        """Returns {task_id, problem_idx, sample_idx} for ast_valid=False -> True transitions"""
    def save_results(self, transitions: List[dict], coverage: List[dict], output_path: str) -> dict: ...

# From: h-m1/code/baseline_generator.py (ACTUAL CODE)
class ExtendedBaselineGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None: ...
    def load_model(self) -> None: ...
    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
        h_e1_pool_path: Optional[str] = None,
    ) -> Dict[str, List[dict]]: ...

# From: h-m1/code/syncode_generator.py (ACTUAL CODE)
class ExtendedSyncodeGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None: ...
    def load_model(self) -> None: ...
    def generate_pool(
        self, problems: Dict[str, dict], output_path: str, progress_path: str
    ) -> Dict[str, List[dict]]:
        """Record keys: task_id, problem_idx, sample_idx, seed, completion, ast_valid, constraint_active"""
```

---

## A-7: CScoreCalculator [Complexity: 17, Budget: 4 subtasks]

Applied: Jaccard-complement C_score independence null model

### API Signatures

```python
# h-m2/code/c_score_calculator.py
from typing import Dict, List, Set
import numpy as np
from config import CScoreConfig

class CScoreCalculator:
    def __init__(self, cfg: CScoreConfig) -> None:
        """Store cfg; init rng = np.random.default_rng(cfg.seed)"""

    def compute_c_score(
        self,
        set_a: Set[str],      # F_syncode task_ids
        set_b: Set[str],      # F_mypy task_ids
        stratum: List[str],   # eligible task_ids in stratum
    ) -> Dict:
        """Point-estimate C_score within stratum.
        Returns: {j_obs, e_j, c_score, r1, r2, intersection_size, union_size, stratum_size}"""

    def bootstrap_c_score_ci(
        self,
        set_a: Set[str],
        set_b: Set[str],
        stratum: List[str],
    ) -> Dict:
        """10000 problem-level resamples with seed=cfg.seed.
        Returns: {mean, ci_lower, ci_upper, p_value, n_bootstrap}"""

    def define_eligibility_conditioned_stratum(
        self,
        fmd_classifications: Dict[str, List[str]],  # {task_id: ["syntax"|"type"|"functional"]}
        mypy_eligible_problems: Set[str],            # task_ids with >=1 baseline mypy exit_code != 0
    ) -> List[str]:
        """Returns sorted task_ids where >=1 sample == 'type' AND in mypy_eligible_problems."""

    def compute_difficulty_quintiles(
        self,
        problems: List[str],
        baseline_pass_rates: Dict[str, float],
    ) -> Dict[int, List[str]]:
        """Returns {0..4: [task_ids]} sorted ascending by baseline_pass_rates."""

    def compute_c_score_by_quintile(
        self,
        set_a: Set[str],
        set_b: Set[str],
        quintiles: Dict[int, List[str]],
    ) -> Dict[int, Dict]:
        """Returns {quintile_idx: c_score_dict}."""

    def save_results(
        self,
        conditioned_result: Dict,
        conditioned_ci: Dict,
        raw_result: Dict,
        quintile_results: Dict[int, Dict],
        output_path: str,
    ) -> dict:
        """Serialize all C_score results to JSON. Returns merged dict."""
```

### Subtasks [4/4 used]

#### Subtask A-7.1: compute_c_score

**API Signature:** `def compute_c_score(self, set_a: Set[str], set_b: Set[str], stratum: List[str]) -> Dict:`
**Return Schema:** `{"j_obs": float, "e_j": float, "c_score": float, "r1": float, "r2": float, "intersection_size": int, "union_size": int, "stratum_size": int}`
**Algorithm:**
```python
stratum_set = set(stratum)
n = len(stratum_set)
if n == 0: return all-zeros dict with stratum_size=0

a_in = set_a & stratum_set
b_in = set_b & stratum_set
r1 = len(a_in) / n
r2 = len(b_in) / n
inter = a_in & b_in
union = a_in | b_in
j_obs = len(inter) / len(union) if union else 0.0
denom = r1 + r2 - r1 * r2
e_j = (r1 * r2) / denom if denom > 0 else 0.0
c_score = (e_j - j_obs) / e_j if e_j > 0 else 0.0
return assembled dict
```
**Edge Cases:**
- Empty stratum → all-zeros dict, stratum_size=0
- set_a or set_b empty within stratum → r1 or r2=0, e_j=0, c_score=0.0
- Empty union → j_obs=0.0

---

#### Subtask A-7.2: bootstrap_c_score_ci

**API Signature:** `def bootstrap_c_score_ci(self, set_a: Set[str], set_b: Set[str], stratum: List[str]) -> Dict:`
**Return Schema:** `{"mean": float, "ci_lower": float, "ci_upper": float, "p_value": float, "n_bootstrap": int}`
**Algorithm:**
```python
np.random.seed(cfg.seed)  # 42
stratum_arr = np.array(list(stratum))
n = len(stratum_arr)
boot_scores = []
for _ in range(cfg.n_bootstrap):  # 10000
    idx = self.rng.integers(0, n, size=n)
    boot_stratum = list(stratum_arr[idx])
    boot_scores.append(self.compute_c_score(set_a, set_b, boot_stratum)["c_score"])
boot_arr = np.array(boot_scores)
alpha = cfg.alpha  # 0.0167
return {mean, ci_lower (alpha/2*100 pct), ci_upper ((1-alpha/2)*100 pct),
        p_value=float(np.mean(boot_arr <= 0)), n_bootstrap=cfg.n_bootstrap}
```
**Edge Cases:**
- stratum_size < cfg.min_stratum_size (10) → log warning, add `"underpowered": True` in result
- All bootstrap c_scores == 0.0 → p_value=1.0 (valid null result)

---

#### Subtask A-7.3: define_eligibility_conditioned_stratum

**API Signature:** `def define_eligibility_conditioned_stratum(self, fmd_classifications: Dict[str, List[str]], mypy_eligible_problems: Set[str]) -> List[str]:`
**Return Schema:** `List[str]` — sorted task_ids
**Algorithm:**
```python
# CRITICAL: FMDClassifier returns "type" not "type_structural"
result = []
for task_id, labels in fmd_classifications.items():
    if any(lbl == "type" for lbl in labels) and task_id in mypy_eligible_problems:
        result.append(task_id)
# Caller must validate len(result) >= cfg.min_stratum_size
return sorted(result)
```
**Edge Cases:**
- fmd_classifications or mypy_eligible_problems empty → return []
- Result size < 10 → caller aborts with pre-condition failure message

---

#### Subtask A-7.4: compute_difficulty_quintiles + compute_c_score_by_quintile

**API Signatures:**
```python
def compute_difficulty_quintiles(self, problems: List[str], baseline_pass_rates: Dict[str, float]) -> Dict[int, List[str]]:
def compute_c_score_by_quintile(self, set_a: Set[str], set_b: Set[str], quintiles: Dict[int, List[str]]) -> Dict[int, Dict]:
```
**Return Schema:** `{0: [task_ids], ..., 4: [task_ids]}` / `{0: c_score_dict, ..., 4: c_score_dict}`
**Algorithm:**
```python
# compute_difficulty_quintiles:
sorted_probs = sorted(problems, key=lambda t: baseline_pass_rates.get(t, 0.0))
n = len(sorted_probs)
quintiles = {q: sorted_probs[q*n//5 : (q+1)*n//5 if q < 4 else n] for q in range(5)}
return quintiles

# compute_c_score_by_quintile:
return {q: self.compute_c_score(set_a, set_b, stratum) for q, stratum in quintiles.items()}
```
**Edge Cases:**
- fewer than 5 problems → some quintiles empty, compute_c_score returns all-zeros
- Missing task_id in baseline_pass_rates → treat as 0.0 (hardest)

---

## A-4: MypyFeedbackRepair [Complexity: 16, Budget: 4 subtasks]

Applied: iterative-feedback-repair-loop (Olausson 2023 / SELF-REFINE)

### API Signatures

```python
# h-m2/code/mypy_feedback_repair.py
from typing import Dict, List, Optional, Tuple
from config import MypyRepairConfig

class MypyFeedbackRepair:
    def __init__(self, cfg: MypyRepairConfig, model=None, tokenizer=None) -> None:
        """Store cfg; model/tokenizer loaded lazily via load_model()."""

    def load_model(self, model_name: str = "codellama/CodeLlama-7b-hf") -> None:
        """Load with device_map='auto', torch_dtype=torch.float16."""

    def parse_mypy_output(self, stdout: str) -> List[Tuple[int, str, str]]:
        """Parse mypy stdout into [(line_num, error_type, message), ...]."""

    def format_structured_feedback(
        self,
        ast_valid: bool,
        ast_error: Optional[str],
        mypy_errors: List[Tuple[int, str, str]],
    ) -> str:
        """Format structured feedback string for repair prompt."""

    def build_repair_prompt(
        self,
        problem_prompt: str,
        current_code: str,
        feedback: str,
    ) -> str:
        """Construct repair prompt: problem + broken code + feedback + fix instruction."""

    def repair_sample(
        self,
        baseline_code: str,
        problem: dict,
        task_id: str,
        sample_idx: int,
    ) -> dict:
        """Run up to cfg.max_rounds repair iterations on one sample."""

    def repair_pool(
        self,
        baseline_pool: Dict[str, List[dict]],
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
    ) -> Dict[str, List[dict]]:
        """Repair all problems; checkpoint every 10 problems; resume from progress_path."""

    def compute_mechanism_activated_rate(
        self, repair_pool: Dict[str, List[dict]]
    ) -> float:
        """Fraction of all repair records where rounds_used > 0."""
```

### Subtasks [4/4 used]

#### Subtask A-4.1: parse_mypy_output + format_structured_feedback

**API Signatures:**
```python
def parse_mypy_output(self, stdout: str) -> List[Tuple[int, str, str]]:
def format_structured_feedback(self, ast_valid: bool, ast_error: Optional[str], mypy_errors: List[Tuple[int, str, str]]) -> str:
```
**Return Schema (parse):** `[(line_num, error_type, message), ...]`
**Algorithm (parse_mypy_output):**
```python
import re
errors = []
for line in stdout.splitlines():
    m = re.match(r'.+:(\d+): (\w+): (.+)', line)
    if m and m.group(2) == "error":
        errors.append((int(m.group(1)), "error", m.group(3)))
return errors
```
**Algorithm (format_structured_feedback):**
```python
if not ast_valid:
    return f"AST ERROR: {ast_error}\nFix the syntax error."
if not mypy_errors:
    return "No errors."
lines = ["Type errors:"]
for line_num, _, msg in mypy_errors[:10]:   # cap at 10
    lines.append(f"  Line {line_num}: {msg}")
return "\n".join(lines)
```
**Edge Cases:**
- stdout empty → return []
- mypy_errors > 10 → truncate to first 10 in feedback

---

#### Subtask A-4.2: build_repair_prompt

**API Signature:** `def build_repair_prompt(self, problem_prompt: str, current_code: str, feedback: str) -> str:`
**Return Schema:** `str`
**Algorithm:**
```python
return (
    f"{problem_prompt}\n\n"
    f"# Current code with errors:\n```python\n{current_code}\n```\n\n"
    f"# Feedback:\n{feedback}\n\n"
    f"# Fixed code:\n```python\n"
)
```
**Edge Cases:**
- Empty problem_prompt → use empty string, no exception
- Empty feedback → prompt still includes "# Feedback:\n\n" for format consistency

---

#### Subtask A-4.3: repair_sample

**API Signature:** `def repair_sample(self, baseline_code: str, problem: dict, task_id: str, sample_idx: int) -> dict:`
**Return Schema:**
```python
{
    "task_id": str,
    "sample_idx": int,
    "rounds_used": int,
    "final_code": str,
    "success": bool,           # ast_valid AND mypy_exit_code == 0
    "ast_valid_final": bool,
    "mypy_exit_code_final": int,
    "feedback_history": List[str],
}
```
**Algorithm:**
```python
current_code = baseline_code; feedback_history = []
for r in range(cfg.max_rounds):
    try: ast.parse(current_code); ast_valid=True; ast_err=None
    except SyntaxError as e: ast_valid=False; ast_err=str(e)
    # write to tempfile, run mypy with cfg.mypy_flags + timeout
    stdout, _, mypy_exit = mypy.api.run(cfg.mypy_flags + [tmpfile_path])
    mypy_errors = parse_mypy_output(stdout)
    errors_before = len(mypy_errors)
    if ast_valid and mypy_exit == 0: break   # early stop
    feedback = format_structured_feedback(ast_valid, ast_err, mypy_errors)
    prompt = build_repair_prompt(problem["prompt"], current_code, feedback)
    current_code = _generate_repair(prompt)  # T=0.2
    new_errs = len(parse_mypy_output(mypy.api.run(cfg.mypy_flags + [tmpfile_new])[0]))
    print(f"mypy_feedback_applied: round={r}, errors_before={errors_before}, errors_after={new_errs}")
    feedback_history.append(feedback)
final_ast = bool(try ast.parse(current_code))
final_exit = mypy.api.run(cfg.mypy_flags + [tmpfile])[2]
return assembled record
```
**Edge Cases:**
- Model not loaded → raise RuntimeError("call load_model() first")
- mypy timeout → treat as exit_code=1, empty errors, log warning
- Generated repair empty → keep current_code, count as round used

---

#### Subtask A-4.4: repair_pool + compute_mechanism_activated_rate

**API Signatures:**
```python
def repair_pool(self, baseline_pool, problems, output_path, progress_path) -> Dict[str, List[dict]]:
def compute_mechanism_activated_rate(self, repair_pool: Dict[str, List[dict]]) -> float:
```
**Return Schema (repair_pool):** `{task_id: [repair_record, ...]}`
**Algorithm (repair_pool):**
```python
completed = load_progress(progress_path)  # Set[str]
pool = load_existing_jsonl(output_path)   # {task_id: [records]}
with open(output_path, "a") as out_f:
    for i, (task_id, records) in enumerate(sorted(baseline_pool.items())):
        if task_id in completed: continue
        problem = problems[task_id]
        repair_records = [repair_sample(r["completion"], problem, task_id, r["sample_idx"]) for r in records]
        for rr in repair_records: out_f.write(json.dumps(rr) + "\n")
        pool[task_id] = repair_records
        completed.add(task_id)
        if (i + 1) % 10 == 0: save_progress(progress_path, completed)
        out_f.flush()
save_progress(progress_path, completed)
return pool
```
**Algorithm (compute_mechanism_activated_rate):**
```python
total = activated = 0
for records in repair_pool.values():
    for rec in records:
        total += 1
        if rec.get("rounds_used", 0) > 0: activated += 1
return activated / total if total > 0 else 0.0
```
**Edge Cases:**
- task_id in baseline_pool missing from problems → skip, log warning
- Corrupt JSONL on resume → skip line, log
- Empty repair_pool → return 0.0

---

## A-8: Z3EligibilityDelta [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
# h-m2/code/z3_eligibility_delta.py
from typing import Dict, List, Tuple
from config import Z3DeltaConfig

class Z3EligibilityDelta:
    def __init__(self, cfg: Z3DeltaConfig) -> None:
        """Store cfg; cfg.z3_timeout_seconds=60, cfg.arith_density_threshold=0.1"""

    def _compute_arith_density(self, code: str) -> float:
        """Fraction of AST nodes that are BinOp (arithmetic) or Compare."""

    def _has_return_annotation(self, code: str) -> bool:
        """True if any FunctionDef has a return type annotation."""

    def check_z3_eligible_heuristic(self, code: str) -> bool:
        """arith_density > cfg.arith_density_threshold AND _has_return_annotation."""

    def compute_eligibility_rate(
        self,
        pool: Dict[str, List[dict]],
        use_best_of: bool = True,
    ) -> Dict[str, bool]:
        """Returns {task_id: z3_eligible}; picks first ast_valid sample if use_best_of."""

    def compute_delta_p(
        self,
        baseline_eligible: Dict[str, bool],
        post_mypy_eligible: Dict[str, bool],
    ) -> Tuple[float, float, float, float]:
        """Bootstrap ΔP = mean(post_mypy) - mean(baseline). Returns (delta_p, ci_lower, ci_upper, p_value)."""

    def save_results(
        self,
        delta_p: float,
        ci_lower: float,
        ci_upper: float,
        p_value: float,
        output_path: str,
    ) -> dict:
        """Serialize to JSON; returns result dict."""
```

### Subtasks [2/2 used]

#### Subtask A-8.1: check_z3_eligible_heuristic + compute_eligibility_rate

**API Signatures:**
```python
def check_z3_eligible_heuristic(self, code: str) -> bool:
def compute_eligibility_rate(self, pool: Dict[str, List[dict]], use_best_of: bool = True) -> Dict[str, bool]:
```
**Return Schema (compute_eligibility_rate):** `{task_id: bool}`
**Algorithm (check_z3_eligible_heuristic):**
```python
try: tree = ast.parse(code)
except SyntaxError: return False
all_nodes = list(ast.walk(tree))
n_total = len(all_nodes)
if n_total == 0: return False
arith_count = sum(1 for n in all_nodes if isinstance(n, (ast.BinOp, ast.Compare)))
density = arith_count / n_total
has_annot = any(isinstance(n, ast.FunctionDef) and n.returns is not None for n in all_nodes)
return density > cfg.arith_density_threshold and has_annot
```
**Algorithm (compute_eligibility_rate):**
```python
result = {}
for task_id, records in pool.items():
    if use_best_of:
        candidates = [r for r in records if r.get("ast_valid", False)]
        sample = candidates[0] if candidates else (records[0] if records else None)
    else:
        sample = records[0] if records else None
    result[task_id] = check_z3_eligible_heuristic(sample["completion"]) if sample else False
return result
```
**Edge Cases:**
- SyntaxError in ast.parse → return False
- No ast_valid samples in use_best_of mode → fallback to records[0]
- Empty records for task_id → False

---

#### Subtask A-8.2: compute_delta_p + save_results

**API Signatures:**
```python
def compute_delta_p(self, baseline_eligible: Dict[str, bool], post_mypy_eligible: Dict[str, bool]) -> Tuple[float, float, float, float]:
def save_results(self, delta_p, ci_lower, ci_upper, p_value, output_path) -> dict:
```
**Return Schema (save_results):**
```python
{
    "delta_p": float,
    "ci_lower": float,
    "ci_upper": float,
    "p_value": float,
    "n_problems": int,
    "p_baseline": float,
    "p_post_mypy": float,
    "n_bootstrap": 10000,
}
```
**Algorithm (compute_delta_p):**
```python
common_ids = sorted(set(baseline_eligible) & set(post_mypy_eligible))
if not common_ids: return (0.0, 0.0, 0.0, 1.0)
b_arr = np.array([float(baseline_eligible[t]) for t in common_ids])
m_arr = np.array([float(post_mypy_eligible[t]) for t in common_ids])
diffs = m_arr - b_arr
delta_p = float(np.mean(diffs))
rng = np.random.default_rng(42); n = len(diffs)
boot = np.array([np.mean(diffs[rng.integers(0, n, size=n)]) for _ in range(10000)])
ci_lower = float(np.percentile(boot, 2.5))
ci_upper = float(np.percentile(boot, 97.5))
p_value = float(np.mean(boot <= 0))
return delta_p, ci_lower, ci_upper, p_value
```
**Edge Cases:**
- No common task_ids → return (0.0, 0.0, 0.0, 1.0)
- All diffs == 0 → delta_p=0.0, p_value=1.0

---

## A-5: SynCode Pool Extension [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch (reuses ExtendedSyncodeGenerator from h-m1)

### API Signatures

The extension adds one helper to run_experiment.py (no new class file needed):

```python
# In h-m2/code/run_experiment.py

def extend_syncode_pool(
    cfg: H2ExperimentConfig,
    problems: Dict[str, dict],
    generator: ExtendedSyncodeGenerator,
) -> Dict[str, List[dict]]:
    """Load h-m1 pool; generate remaining problems to full 164.
    Returns merged {task_id: [record, ...]} for all 164 problems."""

def extract_f_syncode_pass_at_1(
    baseline_pool: Dict[str, List[dict]],
    syncode_pool: Dict[str, List[dict]],
    baseline_pass_rates: Dict[str, float],
    syncode_pass_rates: Dict[str, float],
) -> Set[str]:
    """Return task_ids where baseline pass@1=0 AND syncode pass@1 > 0.
    NOTE: h-m1 TransitionExtractor uses ast_valid flip — this function uses pass@1."""
```

### Subtasks [2/2 used]

#### Subtask A-5.1: extend_syncode_pool

**API Signature:** `def extend_syncode_pool(cfg: H2ExperimentConfig, problems: Dict[str, dict], generator: ExtendedSyncodeGenerator) -> Dict[str, List[dict]]:`
**Return Schema:** `{task_id: [record, ...]}` for 164 task_ids
**Algorithm:**
```python
# Load h-m1 syncode pool
h_m1_pool = {}
if os.path.exists(cfg.h_m1_syncode_pool):
    with open(cfg.h_m1_syncode_pool) as f:
        for line in f:
            rec = json.loads(line.strip())
            h_m1_pool.setdefault(rec["task_id"], []).append(rec)

# Copy h-m1 records to h-m2 output path
out_path = os.path.join(cfg.output.data_dir, cfg.output.syncode_pool_file)
existing = load_existing_jsonl(out_path)
with open(out_path, "a") as f:
    for task_id, records in h_m1_pool.items():
        if task_id not in existing:
            for rec in records: f.write(json.dumps(rec) + "\n")
            existing[task_id] = records

# Generate remaining problems (those not in h_m1_pool + not already in output)
completed = set(existing.keys())
remaining = {t: p for t, p in problems.items() if t not in completed}
new_pool = generator.generate_pool(remaining, out_path, cfg.output.progress_syncode_file)
existing.update(new_pool)
return existing
```
**Edge Cases:**
- cfg.h_m1_syncode_pool missing → skip, regenerate all 164
- Task already in output from previous run → skip (resume via progress_path)

---

#### Subtask A-5.2: extract_f_syncode_pass_at_1

**API Signature:** `def extract_f_syncode_pass_at_1(baseline_pool, syncode_pool, baseline_pass_rates, syncode_pass_rates) -> Set[str]:`
**Return Schema:** `Set[str]` — task_ids in F_SynCode→✓ (pass@1 based)
**Algorithm:**
```python
# NOTE: Uses pass@1 rates (not ast_valid flip like h-m1's TransitionExtractor)
f_syncode = set()
for task_id in syncode_pool:
    if task_id not in baseline_pool: continue
    b_rate = baseline_pass_rates.get(task_id, 0.0)
    s_rate = syncode_pass_rates.get(task_id, 0.0)
    if b_rate == 0.0 and s_rate > 0.0:
        f_syncode.add(task_id)
return f_syncode
```
**Edge Cases:**
- task_id missing from baseline_pass_rates → assume 0.0 (baseline fails), include in candidates
- syncode_pass_rates missing for task_id → skip (no improvement confirmed)
- Both rates == 0.0 → not in F_SynCode (no transition)

---

## Summary: Subtask Budget

| Task | Subtasks | Budget | Used |
|------|----------|--------|------|
| A-7 | A-7.1, A-7.2, A-7.3, A-7.4 | 4 | 4 |
| A-4 | A-4.1, A-4.2, A-4.3, A-4.4 | 4 | 4 |
| A-8 | A-8.1, A-8.2 | 2 | 2 |
| A-5 | A-5.1, A-5.2 | 2 | 2 |
| **Total** | **12** | **12** | **On budget** |

## Key Notes for Phase 4 Coder

1. **FMD label**: `FMDClassifier` returns `"type"` — use `== "type"` in stratum filter, not `"type_structural"`.
2. **BootstrapCI not reused for C_score**: h-m1 `BootstrapCI.compute()` operates on two rate arrays — incompatible with set-based C_score bootstrap. Implement independently in `CScoreCalculator.bootstrap_c_score_ci()`.
3. **TransitionExtractor not reused for F_SynCode**: h-m1 version checks `ast_valid` flip. h-m2 uses `pass@1` improvement. Use `extract_f_syncode_pass_at_1()` instead.
4. **sys.path**: `run_experiment.py` must call `sys.path.insert(0, cfg.h_m1_code_dir)` before any h-m1 imports.
5. **Seed**: `np.random.seed(42)` or `np.random.default_rng(42)` before each bootstrap loop — not global at module level.
6. **mypy tempfile**: h-m1 `FMDClassifier` writes a tempfile; `MypyFeedbackRepair` should also write a tempfile (not `-c` flag) to match behavior — use `tempfile.NamedTemporaryFile` with cleanup.
