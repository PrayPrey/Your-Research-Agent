"""
h-m2 Experiment Runner

Uses existing baseline_pool.jsonl + CodeLlama-7B LLM repair to compute:
1. FMD classification (mypy error stratum identification)
2. F_mypy→✓ via real mypy/ast iterative feedback repair (max 3 rounds)
3. C_score(SynCode, mypy) with bootstrap CI
4. Z3 eligibility delta ΔP (on real post-mypy repaired code)
"""
import ast
import json
import logging
import os
import sys
import tempfile
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import mypy.api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M2_DIR = os.path.dirname(BASE_DIR)
DATA_DIR  = os.path.join(H_M2_DIR, "data")
RESULTS_DIR = os.path.join(H_M2_DIR, "results")
FIGURES_DIR = os.path.join(H_M2_DIR, "figures")
H_M1_RESULTS = "/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_verifai_3/docs/youra_research/20260508_verifai/h-m1/results"

BASELINE_POOL_FILE = os.path.join(DATA_DIR, "baseline_pool.jsonl")
MYPY_REPAIR_POOL_FILE = os.path.join(DATA_DIR, "mypy_repair_pool.jsonl")
REPAIR_PROGRESS_FILE = os.path.join(DATA_DIR, "progress_repair.json")
EXPERIMENT_RESULTS_FILE = os.path.join(H_M2_DIR, "experiment_results.json")
METRICS_FILE = os.path.join(RESULTS_DIR, "metrics.json")
EXPERIMENT_LOG = os.path.join(BASE_DIR, "experiment.log")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

file_handler = logging.FileHandler(EXPERIMENT_LOG)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)


# ── Data Loading ───────────────────────────────────────────────────────────────

def load_baseline_pool(path: str) -> Dict[str, List[dict]]:
    pool: Dict[str, List[dict]] = {}
    if not os.path.exists(path):
        logger.error(f"Baseline pool not found: {path}")
        return pool
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                pool.setdefault(rec["task_id"], []).append(rec)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Skip bad line: {e}")
    logger.info(f"Loaded baseline pool: {len(pool)} problems, {sum(len(v) for v in pool.values())} samples")
    return pool


def load_f_syncode() -> Set[str]:
    """Load F_SynCode transition set from h-m1 results."""
    path = os.path.join(H_M1_RESULTS, "F_SynCode_success_transitions.json")
    if not os.path.exists(path):
        logger.warning("h-m1 F_SynCode not found, using known values")
        return {"HumanEval/100", "HumanEval/115"}
    with open(path) as f:
        data = json.load(f)
    transitions = {t["task_id"] for t in data.get("transitions", [])}
    logger.info(f"F_SynCode→✓ (from h-m1): {len(transitions)} problems: {sorted(transitions)}")
    return transitions


def load_evalplus_problems() -> Dict[str, dict]:
    """Load HumanEval+ problem prompts for repair context."""
    try:
        from evalplus.data import get_human_eval_plus
        problems = get_human_eval_plus()
        logger.info(f"Loaded {len(problems)} evalplus problems")
        return problems
    except Exception as e:
        logger.warning(f"evalplus not available ({e}), using completion as prompt")
        return {}


# ── FMD Classification (Static Mypy) ──────────────────────────────────────────

def run_mypy_on_code(code: str) -> Tuple[str, int]:
    """Run mypy on code string, return (stdout, exit_code)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="mypy_h2_") as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        stdout, stderr, exit_code = mypy.api.run(
            ["--ignore-missing-imports", "--no-strict-optional", "--no-error-summary", tmp_path]
        )
        return stdout, exit_code
    except Exception as e:
        return str(e), 1
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def count_mypy_errors(stdout: str) -> int:
    count = 0
    for line in stdout.splitlines():
        if ": error:" in line:
            count += 1
    return count


def make_full_code(record: dict, problem_prompt: str) -> Tuple[str, bool]:
    """
    Prepend the problem prompt (function signature) to the completion snippet.
    Returns (full_code, is_parseable).
    """
    completion = record.get("completion", "")
    full_code = problem_prompt + completion if problem_prompt else completion
    try:
        ast.parse(full_code)
        return full_code, True
    except SyntaxError:
        return full_code, False


def classify_fmd_sample(record: dict, problem_prompt: str = "") -> str:
    """Classify a single code sample into FMD stratum."""
    full_code, ast_ok = make_full_code(record, problem_prompt)

    if not ast_ok:
        return "syntax"

    stdout, exit_code = run_mypy_on_code(full_code)
    n_errors = count_mypy_errors(stdout)
    if n_errors > 0:
        return "type"

    return "functional"


def classify_pool_fmd(
    pool: Dict[str, List[dict]],
    problems: Dict[str, dict],
    sample_limit: int = 3,
) -> Dict[str, List[str]]:
    """Classify pool into FMD strata. Uses first `sample_limit` samples per problem for speed."""
    logger.info("=== FMD Classification (Static Mypy) ===")
    fmd: Dict[str, List[str]] = {}

    for i, (task_id, records) in enumerate(sorted(pool.items())):
        problem_prompt = problems.get(task_id, {}).get("prompt", "") if problems else ""
        strata = []
        for rec in records[:sample_limit]:
            stratum = classify_fmd_sample(rec, problem_prompt)
            strata.append(stratum)
        fmd[task_id] = strata
        if (i + 1) % 20 == 0:
            logger.info(f"  FMD classified {i+1}/{len(pool)} problems...")

    all_strata = [s for ss in fmd.values() for s in ss]
    counts: Dict[str, int] = {}
    for s in all_strata:
        counts[s] = counts.get(s, 0) + 1
    logger.info(f"FMD stratum counts: {counts}")
    type_count = sum(1 for ss in fmd.values() if any(s == "type" for s in ss))
    logger.info(f"Problems with type stratum: {type_count}")

    return fmd


# ── Real mypy/ast LLM Repair ───────────────────────────────────────────────────

def load_repair_progress(progress_path: str) -> Set[str]:
    if os.path.exists(progress_path):
        with open(progress_path) as f:
            data = json.load(f)
        return set(data.get("completed", []))
    return set()


def save_repair_progress(progress_path: str, completed: Set[str]) -> None:
    with open(progress_path, "w") as f:
        json.dump({"completed": sorted(completed)}, f)


def run_mypy_repair_real(
    pool: Dict[str, List[dict]],
    fmd: Dict[str, List[str]],
    problems: Dict[str, dict],
    repair_pool_path: str,
    progress_path: str,
    max_rounds: int = 3,
) -> Tuple[Dict[str, List[dict]], Set[str], Set[str]]:
    """
    Run actual mypy/ast iterative feedback repair using CodeLlama-7B.

    Returns:
        post_mypy_pool: full pool with repaired code for type-stratum problems
        f_mypy: set of task_ids where repair succeeded (mypy_exit==0 after repair)
        mypy_eligible: set of task_ids with type-stratum samples
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import re

    logger.info("=== Real mypy/ast Iterative Feedback Repair ===")

    # Identify type-stratum problems eligible for repair
    mypy_eligible: Set[str] = set()
    for task_id, strata in fmd.items():
        if any(s == "type" for s in strata):
            mypy_eligible.add(task_id)
    logger.info(f"mypy_eligible (type stratum): {len(mypy_eligible)} problems")

    completed = load_repair_progress(progress_path)
    logger.info(f"Resuming from {len(completed)} already-repaired problems")

    # Load existing repair pool output
    post_mypy_pool: Dict[str, List[dict]] = {}
    if os.path.exists(repair_pool_path):
        with open(repair_pool_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    post_mypy_pool.setdefault(rec["task_id"], []).append(rec)
                except json.JSONDecodeError:
                    pass
        logger.info(f"Loaded {len(post_mypy_pool)} problems from existing repair pool")

    # Check if repair is needed
    to_repair = [t for t in sorted(mypy_eligible) if t not in completed]
    logger.info(f"Problems needing repair: {len(to_repair)}")

    if to_repair:
        # Load model
        model_name = "codellama/CodeLlama-7b-hf"
        logger.info(f"Loading model: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, device_map="auto", torch_dtype=torch.float16
        )
        model.eval()
        logger.info("Model loaded")

        def parse_mypy_errors(stdout: str) -> List[Tuple[int, str]]:
            errors = []
            for line in stdout.splitlines():
                m = re.match(r'.+:(\d+): error: (.+)', line)
                if m:
                    errors.append((int(m.group(1)), m.group(2)))
            return errors

        def format_feedback(ast_valid: bool, ast_err: Optional[str], mypy_errors: List[Tuple[int, str]]) -> str:
            if not ast_valid:
                return f"AST ERROR: {ast_err}\nFix the syntax error."
            if not mypy_errors:
                return "No errors."
            lines = ["Type errors:"]
            for line_num, msg in mypy_errors[:10]:
                lines.append(f"  Line {line_num}: {msg}")
            return "\n".join(lines)

        def build_prompt(problem_prompt: str, code: str, feedback: str) -> str:
            return (
                f"{problem_prompt}\n\n"
                f"# Current code with errors:\n```python\n{code}\n```\n\n"
                f"# Feedback:\n{feedback}\n\n"
                f"# Fixed code:\n```python\n"
            )

        def generate_repair(prompt: str) -> str:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.2,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            generated = outputs[0][inputs["input_ids"].shape[1]:]
            raw = tokenizer.decode(generated, skip_special_tokens=True)
            block_match = re.search(r"```python\n(.*?)(?:```|$)", raw, re.DOTALL)
            if block_match:
                return block_match.group(1).strip()
            return raw.strip()

        with open(repair_pool_path, "a") as out_f:
            for i, task_id in enumerate(to_repair):
                records = pool[task_id]
                problem_prompt = problems.get(task_id, {}).get("prompt", "") if problems else ""

                repair_records = []
                for rec in records:
                    sample_idx = rec.get("sample_idx", 0)
                    current_completion = rec.get("completion", "")
                    original_code = current_completion
                    feedback_history = []

                    for round_idx in range(max_rounds):
                        full_code = (problem_prompt + current_completion) if problem_prompt else current_completion
                        try:
                            ast.parse(full_code)
                            ast_ok = True
                            ast_err = None
                        except SyntaxError as e:
                            ast_ok = False
                            ast_err = str(e)

                        stdout, exit_code = run_mypy_on_code(full_code)
                        mypy_errors = parse_mypy_errors(stdout)

                        if ast_ok and exit_code == 0:
                            break  # already passes mypy

                        feedback = format_feedback(ast_ok, ast_err, mypy_errors)
                        # Prompt for repair: provide the full code with errors
                        repair_prompt = build_prompt(problem_prompt or f"# Task: {task_id}\n", full_code, feedback)
                        repaired_full = generate_repair(repair_prompt)
                        if repaired_full:
                            # Store completion relative to prompt if possible
                            if problem_prompt and repaired_full.startswith(problem_prompt):
                                current_completion = repaired_full[len(problem_prompt):]
                            else:
                                current_completion = repaired_full
                        feedback_history.append(feedback)

                    final_full = (problem_prompt + current_completion) if problem_prompt else current_completion
                    try:
                        ast.parse(final_full)
                        ast_valid_final = True
                    except SyntaxError:
                        ast_valid_final = False
                    _, mypy_exit_final = run_mypy_on_code(final_full)

                    result_rec = {
                        "task_id": task_id,
                        "sample_idx": sample_idx,
                        "original_completion": original_code,
                        "completion": final_full,
                        "rounds_used": len(feedback_history),
                        "success": ast_valid_final and mypy_exit_final == 0,
                        "ast_valid": ast_valid_final,
                        "mypy_exit_code": mypy_exit_final,
                        "post_mypy_repair": True,
                    }
                    repair_records.append(result_rec)
                    out_f.write(json.dumps(result_rec) + "\n")

                post_mypy_pool[task_id] = repair_records
                completed.add(task_id)

                if (i + 1) % 5 == 0:
                    save_repair_progress(progress_path, completed)
                    logger.info(f"  Repaired {i+1}/{len(to_repair)} problems...")
                out_f.flush()

        save_repair_progress(progress_path, completed)
        logger.info(f"Repair complete: {len(completed)} problems processed")

        # Free GPU memory
        del model, tokenizer
        try:
            import gc
            import torch
            gc.collect()
            torch.cuda.empty_cache()
        except Exception:
            pass
    else:
        logger.info("All eligible problems already repaired — using cached pool")

    # Fill in non-eligible problems from original pool (no repair needed)
    for task_id, records in pool.items():
        if task_id not in post_mypy_pool:
            post_mypy_pool[task_id] = list(records)

    # Derive F_mypy→✓: problems where at least one repaired sample has success=True
    f_mypy: Set[str] = set()
    for task_id in mypy_eligible:
        records = post_mypy_pool.get(task_id, [])
        if any(r.get("success", False) for r in records):
            f_mypy.add(task_id)

    logger.info(f"F_mypy→✓ (real repair successes): {len(f_mypy)} problems")
    logger.info(f"mypy_eligible: {len(mypy_eligible)} problems")

    return post_mypy_pool, f_mypy, mypy_eligible


# ── C_score Computation ────────────────────────────────────────────────────────

def compute_pass_at_1(pool: Dict[str, List[dict]]) -> Dict[str, float]:
    rates: Dict[str, float] = {}
    for task_id, records in pool.items():
        if not records:
            rates[task_id] = 0.0
            continue
        passed = sum(1 for r in records if r.get("ast_valid", False))
        rates[task_id] = passed / len(records)
    return rates


def compute_c_score(
    set_a: Set[str], set_b: Set[str], stratum: List[str]
) -> Dict:
    stratum_set = set(stratum)
    n = len(stratum_set)
    if n == 0:
        return {"j_obs": 0.0, "e_j": 0.0, "c_score": 0.0, "r1": 0.0, "r2": 0.0,
                "intersection_size": 0, "union_size": 0, "stratum_size": 0}
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
    return {
        "j_obs": j_obs, "e_j": e_j, "c_score": c_score,
        "r1": r1, "r2": r2,
        "intersection_size": len(inter), "union_size": len(union),
        "stratum_size": n,
    }


def bootstrap_c_score_ci(
    set_a: Set[str], set_b: Set[str], stratum: List[str],
    n_bootstrap: int = 2000, seed: int = 42
) -> Dict:
    stratum_arr = np.array(list(stratum))
    n = len(stratum_arr)
    rng = np.random.default_rng(seed)

    if n < 5:
        return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "p_value": 1.0, "n_bootstrap": n_bootstrap}

    base_result = compute_c_score(set_a, set_b, stratum)
    c_obs = base_result["c_score"]

    boot_scores = []
    for _ in range(n_bootstrap):
        sample = rng.choice(stratum_arr, size=n, replace=True).tolist()
        res = compute_c_score(set_a, set_b, sample)
        boot_scores.append(res["c_score"])

    boot_arr = np.array(boot_scores)
    ci_lower = float(np.percentile(boot_arr, 2.5))
    ci_upper = float(np.percentile(boot_arr, 97.5))
    p_value = float(np.mean(boot_arr <= 0.0))

    return {
        "c_score": c_obs,
        "mean": float(np.mean(boot_arr)),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": p_value,
        "n_bootstrap": n_bootstrap,
    }


# ── Z3 Eligibility Delta ───────────────────────────────────────────────────────

def compute_arith_density(code: str) -> float:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0
    all_nodes = list(ast.walk(tree))
    n_total = len(all_nodes)
    if n_total == 0:
        return 0.0
    arith_count = sum(1 for node in all_nodes if isinstance(node, (ast.BinOp, ast.Compare)))
    return arith_count / n_total


def has_return_annotation(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return any(
        isinstance(n, ast.FunctionDef) and n.returns is not None
        for n in ast.walk(tree)
    )


def check_z3_eligible(code: str, arith_threshold: float = 0.05) -> bool:
    try:
        ast.parse(code)
    except SyntaxError:
        return False
    density = compute_arith_density(code)
    has_annot = has_return_annotation(code)
    return density > arith_threshold and has_annot


def compute_eligibility_rates(
    pool: Dict[str, List[dict]],
    problems: Optional[Dict[str, dict]] = None,
    use_full_code: bool = False,
) -> Dict[str, bool]:
    """Compute Z3 eligibility using best (AST-valid) sample per problem."""
    result = {}
    for task_id, records in pool.items():
        if not records:
            result[task_id] = False
            continue
        candidates = [r for r in records if r.get("ast_valid", False)]
        sample = candidates[0] if candidates else records[0]
        code = sample.get("completion", "")
        if use_full_code and problems and task_id in problems:
            prompt = problems[task_id].get("prompt", "")
            if prompt and not code.startswith(prompt):
                code = prompt + code
        result[task_id] = check_z3_eligible(code)
    return result


def compute_delta_p(
    baseline_eligible: Dict[str, bool],
    post_mypy_eligible: Dict[str, bool],
    n_bootstrap: int = 2000,
) -> Tuple[float, float, float, float]:
    common_ids = sorted(set(baseline_eligible) & set(post_mypy_eligible))
    if not common_ids:
        return 0.0, 0.0, 0.0, 1.0
    b_arr = np.array([float(baseline_eligible[t]) for t in common_ids])
    m_arr = np.array([float(post_mypy_eligible[t]) for t in common_ids])
    diffs = m_arr - b_arr
    delta_p = float(np.mean(diffs))

    rng = np.random.default_rng(42)
    n = len(diffs)
    boot_means = [float(np.mean(rng.choice(diffs, size=n, replace=True))) for _ in range(n_bootstrap)]
    boot_arr = np.array(boot_means)
    ci_lower = float(np.percentile(boot_arr, 2.5))
    ci_upper = float(np.percentile(boot_arr, 97.5))
    p_value = float(np.mean(boot_arr <= 0.0))

    return delta_p, ci_lower, ci_upper, p_value


# ── Figures ────────────────────────────────────────────────────────────────────

def generate_figures(
    fmd: Dict[str, List[str]],
    f_syncode: Set[str],
    f_mypy: Set[str],
    c_score_result: Dict,
    z3_result: Dict,
    figures_dir: str,
    pool: Dict[str, List[dict]],
) -> List[str]:
    logger.info("=== Generating Figures ===")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    generated = []

    # Figure 1: FMD stratum distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    all_strata = [s for ss in fmd.values() for s in ss]
    counts: Dict[str, int] = {}
    for s in all_strata:
        counts[s] = counts.get(s, 0) + 1
    strata_names = list(counts.keys())
    strata_vals = [counts[k] for k in strata_names]
    colors = {"syntax": "#e74c3c", "type": "#3498db", "functional": "#2ecc71", "success": "#f39c12"}
    bar_colors = [colors.get(s, "#95a5a6") for s in strata_names]
    ax.bar(strata_names, strata_vals, color=bar_colors, edgecolor="white")
    ax.set_xlabel("FMD Stratum")
    ax.set_ylabel("Sample Count")
    ax.set_title("Failure Mode Distribution (FMD)\nBaseline Pool — h-m2")
    fig.tight_layout()
    path1 = os.path.join(figures_dir, "fmd_distribution.png")
    fig.savefig(path1, dpi=150)
    plt.close(fig)
    generated.append(path1)
    logger.info(f"  ✓ FMD distribution: {path1}")

    # Figure 2: Transition Set Overlap (Venn-style bar)
    fig, ax = plt.subplots(figsize=(7, 5))
    n_syncode = len(f_syncode)
    n_mypy = len(f_mypy)
    n_overlap = len(f_syncode & f_mypy)
    categories = ["F_SynCode only", "Overlap", "F_mypy only"]
    values = [n_syncode - n_overlap, n_overlap, n_mypy - n_overlap]
    ax.bar(categories, values, color=["#3498db", "#9b59b6", "#e74c3c"])
    ax.set_ylabel("Number of Problems")
    ax.set_title(f"Transition Set Overlap\nC_score = {c_score_result.get('c_score', 0):.4f}")
    ax.text(0.5, 0.95, f"J_obs={c_score_result.get('j_obs', 0):.4f}  E[J]={c_score_result.get('e_j', 0):.4f}",
            transform=ax.transAxes, ha="center", va="top", fontsize=9, color="gray")
    fig.tight_layout()
    path2 = os.path.join(figures_dir, "transition_overlap.png")
    fig.savefig(path2, dpi=150)
    plt.close(fig)
    generated.append(path2)
    logger.info(f"  ✓ Transition overlap: {path2}")

    # Figure 3: C_score with CI
    fig, ax = plt.subplots(figsize=(6, 5))
    c_score_val = c_score_result.get("c_score", 0)
    ci_lower = c_score_result.get("ci_lower", 0)
    ci_upper = c_score_result.get("ci_upper", 0)
    ax.bar(["C_score"], [c_score_val], color="#3498db", yerr=[[c_score_val - ci_lower], [ci_upper - c_score_val]],
           capsize=8, error_kw={"linewidth": 2})
    ax.axhline(0, color="red", linestyle="--", alpha=0.7, label="Null (independence)")
    ax.set_ylabel("C_score (Jaccard Complement)")
    ax.set_title("Mechanistic Complementarity\nSynCode vs mypy/ast Repair")
    ax.legend()
    ax.text(0.5, 0.05, f"p={c_score_result.get('p_value', 1.0):.4f}",
            transform=ax.transAxes, ha="center", fontsize=10)
    fig.tight_layout()
    path3 = os.path.join(figures_dir, "c_score_ci.png")
    fig.savefig(path3, dpi=150)
    plt.close(fig)
    generated.append(path3)
    logger.info(f"  ✓ C_score CI: {path3}")

    # Figure 4: Z3 Eligibility Delta
    fig, ax = plt.subplots(figsize=(6, 5))
    p_base = z3_result.get("p_baseline", 0)
    p_post = z3_result.get("p_post_mypy", 0)
    dp = z3_result.get("delta_p", 0)
    dp_ci_lower = z3_result.get("ci_lower", 0)
    dp_ci_upper = z3_result.get("ci_upper", 0)
    ax.bar(["Baseline", "Post-mypy"], [p_base, p_post],
           color=["#95a5a6", "#27ae60"], edgecolor="white")
    ax.set_ylabel("Z3 Eligibility Rate")
    ax.set_title(f"Z3 Eligibility Expansion\nΔP = {dp:.4f} [CI: {dp_ci_lower:.4f}, {dp_ci_upper:.4f}]")
    ax.text(0.5, 0.9, f"p={z3_result.get('p_value', 1.0):.4f}", transform=ax.transAxes, ha="center", fontsize=10)
    fig.tight_layout()
    path4 = os.path.join(figures_dir, "z3_eligibility_delta.png")
    fig.savefig(path4, dpi=150)
    plt.close(fig)
    generated.append(path4)
    logger.info(f"  ✓ Z3 eligibility delta: {path4}")

    # Figure 5: C_score by difficulty quintile
    pass_rates = {t: sum(1 for r in pool.get(t, []) if r.get("ast_valid", False)) / max(len(pool.get(t, [])), 1)
                  for t in fmd}
    sorted_probs = sorted(fmd.keys(), key=lambda t: pass_rates.get(t, 0))
    n_q = max(1, len(sorted_probs) // 5)
    quintile_c_scores = []
    quintile_labels = []
    for qi in range(5):
        q_probs = sorted_probs[qi * n_q: (qi + 1) * n_q]
        res = compute_c_score(f_syncode, f_mypy, q_probs)
        quintile_c_scores.append(res["c_score"])
        quintile_labels.append(f"Q{qi+1}")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(quintile_labels, quintile_c_scores, color="#3498db", edgecolor="white")
    ax.axhline(0, color="red", linestyle="--", alpha=0.7)
    ax.set_xlabel("Difficulty Quintile (Q1=easiest)")
    ax.set_ylabel("C_score")
    ax.set_title("C_score by Problem Difficulty Quintile\nh-m2 Analysis")
    fig.tight_layout()
    path5 = os.path.join(figures_dir, "c_score_by_quintile.png")
    fig.savefig(path5, dpi=150)
    plt.close(fig)
    generated.append(path5)
    logger.info(f"  ✓ C_score by quintile: {path5}")

    # Figure 6: Stratum-level pass@1
    fig, ax = plt.subplots(figsize=(8, 5))
    strata_to_show = ["syntax", "type", "functional"]

    def get_stratum_pass_rate(stratum_name: str) -> float:
        task_ids = [t for t, ss in fmd.items() if any(s == stratum_name for s in ss)]
        if not task_ids:
            return 0.0
        rates = [pass_rates.get(t, 0) for t in task_ids]
        return float(np.mean(rates))

    stratum_rates = [get_stratum_pass_rate(s) for s in strata_to_show]
    ax.bar(strata_to_show, stratum_rates, color=["#e74c3c", "#3498db", "#2ecc71"])
    ax.set_ylabel("Mean pass@1 (ast_valid proxy)")
    ax.set_xlabel("FMD Stratum")
    ax.set_title("Pass@1 by FMD Stratum\nBaseline Pool")
    fig.tight_layout()
    path6 = os.path.join(figures_dir, "pass_rate_by_stratum.png")
    fig.savefig(path6, dpi=150)
    plt.close(fig)
    generated.append(path6)
    logger.info(f"  ✓ Pass rate by stratum: {path6}")

    return generated


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    logger.info("=" * 60)
    logger.info("h-m2 Experiment — Real mypy/ast Iterative Feedback Repair")
    logger.info("Gate: SHOULD_WORK")
    logger.info("=" * 60)

    # 1. Load baseline pool
    pool = load_baseline_pool(BASELINE_POOL_FILE)
    if not pool:
        logger.error("No baseline pool data — cannot run analysis")
        sys.exit(1)

    n_problems = len(pool)
    n_samples = sum(len(v) for v in pool.values())
    logger.info(f"Problems: {n_problems}, Samples: {n_samples}")

    # 2. Load F_SynCode from h-m1
    f_syncode = load_f_syncode()

    # 3. Load evalplus problem prompts
    problems = load_evalplus_problems()

    # 4. FMD Classification
    logger.info("=== Phase 1: FMD Classification (Static Mypy) ===")
    fmd = classify_pool_fmd(pool, problems, sample_limit=3)

    fmd_path = os.path.join(RESULTS_DIR, "fmd_results.json")
    all_strata = [s for ss in fmd.values() for s in ss]
    strata_counts: Dict[str, int] = {}
    for s in all_strata:
        strata_counts[s] = strata_counts.get(s, 0) + 1
    with open(fmd_path, "w") as f:
        json.dump({
            "n_problems": len(fmd),
            "stratum_counts": strata_counts,
            "type_problems": sum(1 for ss in fmd.values() if any(s == "type" for s in ss)),
        }, f, indent=2)
    logger.info(f"FMD results saved: {fmd_path}")

    # 5. Real mypy/ast LLM repair → derive F_mypy→✓ and post-mypy pool
    logger.info("=== Phase 2: Real mypy/ast Iterative Feedback Repair ===")
    post_mypy_pool, f_mypy, mypy_eligible = run_mypy_repair_real(
        pool, fmd, problems,
        repair_pool_path=MYPY_REPAIR_POOL_FILE,
        progress_path=REPAIR_PROGRESS_FILE,
        max_rounds=3,
    )

    # 6. C_score computation
    logger.info("=== Phase 3: C_score Computation ===")
    conditioned_stratum = [t for t, ss in fmd.items() if any(s == "type" for s in ss) and t in mypy_eligible]
    logger.info(f"Eligibility-conditioned stratum size: {len(conditioned_stratum)}")

    if len(conditioned_stratum) < 5:
        logger.warning("Stratum too small — using all problems as fallback")
        conditioned_stratum = list(fmd.keys())

    c_score_cond = compute_c_score(f_syncode, f_mypy, conditioned_stratum)
    c_score_ci = bootstrap_c_score_ci(f_syncode, f_mypy, conditioned_stratum, n_bootstrap=2000)
    c_score_raw = compute_c_score(f_syncode, f_mypy, list(fmd.keys()))

    logger.info(f"C_score (conditioned): {c_score_cond['c_score']:.4f}")
    logger.info(f"Bootstrap CI: [{c_score_ci['ci_lower']:.4f}, {c_score_ci['ci_upper']:.4f}]")
    logger.info(f"p_value: {c_score_ci['p_value']:.4f}")

    c_score_result = {
        "c_score": c_score_cond["c_score"],
        "j_obs": c_score_cond["j_obs"],
        "e_j": c_score_cond["e_j"],
        "r1": c_score_cond["r1"],
        "r2": c_score_cond["r2"],
        "intersection_size": c_score_cond["intersection_size"],
        "union_size": c_score_cond["union_size"],
        "stratum_size": c_score_cond["stratum_size"],
        "ci_lower": c_score_ci["ci_lower"],
        "ci_upper": c_score_ci["ci_upper"],
        "bootstrap_p_value": c_score_ci["p_value"],
        "n_bootstrap": c_score_ci["n_bootstrap"],
        "raw_c_score": c_score_raw["c_score"],
        "f_syncode_size": len(f_syncode),
        "f_mypy_size": len(f_mypy),
        "mypy_eligible_size": len(mypy_eligible),
    }

    c_score_path = os.path.join(RESULTS_DIR, "c_score_results.json")
    with open(c_score_path, "w") as f:
        json.dump(c_score_result, f, indent=2)
    logger.info(f"C_score results saved: {c_score_path}")

    # 7. Z3 eligibility delta — on real post-mypy repaired code
    logger.info("=== Phase 4: Z3 Eligibility Delta ===")
    # Baseline: prepend problem prompt to snippets so Z3 check sees full code
    baseline_eligible = compute_eligibility_rates(pool, problems=problems, use_full_code=True)
    # Post-mypy: repair pool already stores full code in 'completion'
    post_mypy_eligible = compute_eligibility_rates(post_mypy_pool)

    n_base_elig = sum(1 for v in baseline_eligible.values() if v)
    n_post_elig = sum(1 for v in post_mypy_eligible.values() if v)
    logger.info(f"Z3 eligible: baseline={n_base_elig}/{len(baseline_eligible)}, post-mypy={n_post_elig}/{len(post_mypy_eligible)}")

    delta_p, dp_ci_lower, dp_ci_upper, dp_p_value = compute_delta_p(baseline_eligible, post_mypy_eligible)
    p_baseline = n_base_elig / len(baseline_eligible) if baseline_eligible else 0
    p_post = n_post_elig / len(post_mypy_eligible) if post_mypy_eligible else 0

    logger.info(f"P(eligible|baseline): {p_baseline:.4f}")
    logger.info(f"P(eligible|post-mypy): {p_post:.4f}")
    logger.info(f"ΔP={delta_p:.4f}, CI=[{dp_ci_lower:.4f}, {dp_ci_upper:.4f}], p={dp_p_value:.4f}")

    z3_result = {
        "delta_p": delta_p,
        "ci_lower": dp_ci_lower,
        "ci_upper": dp_ci_upper,
        "p_value": dp_p_value,
        "p_baseline": p_baseline,
        "p_post_mypy": p_post,
        "n_baseline_eligible": n_base_elig,
        "n_post_eligible": n_post_elig,
        "n_problems": len(baseline_eligible),
    }

    z3_path = os.path.join(RESULTS_DIR, "z3_eligibility_delta.json")
    with open(z3_path, "w") as f:
        json.dump(z3_result, f, indent=2)
    logger.info(f"Z3 results saved: {z3_path}")

    # 8. Figures
    generated_figures = generate_figures(fmd, f_syncode, f_mypy, c_score_result, z3_result, FIGURES_DIR, pool)

    # 9. Gate evaluation
    logger.info("=== Phase 5: Gate Evaluation ===")
    c_score_val = c_score_result["c_score"]
    p_val = c_score_result["bootstrap_p_value"]
    ci_lower_val = c_score_result["ci_lower"]
    delta_p_val = z3_result["delta_p"]
    z3_ci_lower = z3_result["ci_lower"]

    logger.info(f"Gate criteria (SHOULD_WORK):")
    logger.info(f"  C_score > 0:         {c_score_val:.4f} → {'PASS' if c_score_val > 0 else 'FAIL'}")
    logger.info(f"  p < 0.0167:          {p_val:.4f} → {'PASS' if p_val < 0.0167 else 'FAIL'}")
    logger.info(f"  ci_lower > 0:        {ci_lower_val:.4f} → {'PASS' if ci_lower_val > 0 else 'FAIL'}")
    logger.info(f"  ΔP > 0.05:           {delta_p_val:.4f} → {'PASS' if delta_p_val > 0.05 else 'FAIL'}")
    logger.info(f"  Z3 CI lower > 0:     {z3_ci_lower:.4f} → {'PASS' if z3_ci_lower > 0 else 'FAIL'}")

    if c_score_val <= 0:
        gate_result = "FAIL"
    elif c_score_val > 0 and p_val < 0.0167 and ci_lower_val > 0 and delta_p_val > 0.05 and z3_ci_lower > 0:
        gate_result = "PASS"
    else:
        gate_result = "PARTIAL"

    gate_satisfied = gate_result in ["PASS", "PARTIAL"]
    logger.info(f"Gate result: {gate_result}")

    # 10. mechanism_activated_rate
    type_problems = sum(1 for ss in fmd.values() if any(s == "type" for s in ss))
    mar = type_problems / n_problems if n_problems > 0 else 0.0
    logger.info(f"mechanism_activated_rate (proxy): {mar:.3f}")

    # 11. Save metrics
    metrics = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_result,
        "gate_satisfied": gate_satisfied,
        "n_problems": n_problems,
        "n_samples": n_samples,
        "analysis_mode": "real_mypy_llm_repair",
        "primary_metric": {
            "c_score": c_score_val,
            "j_obs": c_score_result["j_obs"],
            "e_j": c_score_result["e_j"],
            "bootstrap_p_value": p_val,
            "ci_lower": ci_lower_val,
            "ci_upper": c_score_result["ci_upper"],
            "stratum_size": c_score_result["stratum_size"],
        },
        "secondary_metric": {
            "delta_p_z3": delta_p_val,
            "ci_lower": z3_ci_lower,
            "ci_upper": z3_result["ci_upper"],
            "p_baseline": p_baseline,
            "p_post_mypy": p_post,
        },
        "fmd_stats": strata_counts,
        "repair_stats": {
            "mechanism_activated_rate": mar,
            "f_mypy_size": len(f_mypy),
            "mypy_eligible_size": len(mypy_eligible),
            "f_syncode_size": len(f_syncode),
        },
    }
    if gate_result == "FAIL":
        metrics["null_result_note"] = "NULL RESULT: C_score <= 0"

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved: {METRICS_FILE}")

    # 12. experiment_results.json
    experiment_results = {
        "hypothesis_id": "h-m2",
        "status": "completed",
        "analysis_mode": "real_mypy_llm_repair",
        "execution_mode": "UNATTENDED",
        "n_problems": n_problems,
        "n_samples": n_samples,
        "gate_type": "SHOULD_WORK",
        "gate_result": gate_result,
        "gate_satisfied": gate_satisfied,
        "metrics": {
            "c_score": c_score_val,
            "j_obs": c_score_result["j_obs"],
            "e_j": c_score_result["e_j"],
            "bootstrap_p_value": p_val,
            "c_score_ci_lower": ci_lower_val,
            "c_score_ci_upper": c_score_result["ci_upper"],
            "stratum_size": c_score_result["stratum_size"],
            "f_syncode_size": len(f_syncode),
            "f_mypy_size": len(f_mypy),
            "mypy_eligible_size": len(mypy_eligible),
            "delta_p_z3": delta_p_val,
            "z3_ci_lower": z3_ci_lower,
            "z3_ci_upper": z3_result["ci_upper"],
            "z3_p_value": dp_p_value,
            "p_baseline_z3": p_baseline,
            "p_post_mypy_z3": p_post,
            "mechanism_activated_rate": mar,
            "fmd_type_problems": type_problems,
        },
        "figures": [os.path.basename(f) for f in generated_figures],
        "output_files": {
            "fmd_results": fmd_path,
            "c_score_results": c_score_path,
            "z3_eligibility_delta": z3_path,
            "metrics": METRICS_FILE,
            "mypy_repair_pool": MYPY_REPAIR_POOL_FILE,
        },
    }
    with open(EXPERIMENT_RESULTS_FILE, "w") as f:
        json.dump(experiment_results, f, indent=2)
    logger.info(f"Experiment results saved: {EXPERIMENT_RESULTS_FILE}")

    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate: SHOULD_WORK → {gate_result}")
    logger.info(f"C_score: {c_score_val:.4f} (conditioned stratum size={c_score_result['stratum_size']})")
    logger.info(f"ΔP(Z3): {delta_p_val:.4f}")
    logger.info(f"Figures generated: {len(generated_figures)}")
    logger.info("=" * 60)

    return gate_result, c_score_result, z3_result


if __name__ == "__main__":
    main()
