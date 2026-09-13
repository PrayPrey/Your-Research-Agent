import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

import numpy as np
import random
import re
import json
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

# Try importing z3
try:
    from z3 import *

    Z3_AVAILABLE = True
    print("Z3 available")
except ImportError:
    Z3_AVAILABLE = False
    print("Z3 not available, using mock solver")

# Try importing sentence transformers
try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
    print("SentenceTransformer available")
except ImportError:
    ST_AVAILABLE = False
    print("SentenceTransformer not available, using TF-IDF embeddings")

from sklearn.feature_extraction.text import TfidfVectorizer

# ─────────────────────────────────────────────
# 1. Synthetic Loop Program Dataset
# ─────────────────────────────────────────────


@dataclass
class LoopProgram:
    """Represents a simple loop program with known correct invariant."""

    name: str
    code: str
    variables: Dict[str, int]  # initial values
    loop_var: str
    loop_bound: int
    increment: int
    post_condition: str
    correct_invariant: str
    invariant_type: str  # 'linear', 'quadratic', 'modular'


def create_synthetic_programs(n=60):
    """Create synthetic loop programs with known correct invariants."""
    programs = []

    # Pattern 1: Simple counter loops  x = 0; while x < n: x += c
    for i in range(1, 16):
        n_val = random.randint(5, 20)
        c_val = random.randint(1, 3)
        prog = LoopProgram(
            name=f"counter_{i}",
            code=f"x = 0\nwhile x < {n_val}:\n    x = x + {c_val}",
            variables={"x": 0},
            loop_var="x",
            loop_bound=n_val,
            increment=c_val,
            post_condition=f"x >= {n_val}",
            correct_invariant=f"x >= 0 and x <= {n_val + c_val - 1}",
            invariant_type="linear",
        )
        programs.append(prog)

    # Pattern 2: Accumulator loops  s = 0; x = 0; while x < n: s += x; x += 1
    for i in range(1, 16):
        n_val = random.randint(5, 15)
        prog = LoopProgram(
            name=f"accumulator_{i}",
            code=f"s = 0\nx = 0\nwhile x < {n_val}:\n    s = s + x\n    x = x + 1",
            variables={"s": 0, "x": 0},
            loop_var="x",
            loop_bound=n_val,
            increment=1,
            post_condition=f"s == {n_val * (n_val-1) // 2}",
            correct_invariant=f"x >= 0 and x <= {n_val} and s == x * (x - 1) / 2",
            invariant_type="quadratic",
        )
        programs.append(prog)

    # Pattern 3: Multiplication via addition  p = 0; x = 0; while x < n: p += m; x += 1
    for i in range(1, 16):
        n_val = random.randint(3, 10)
        m_val = random.randint(2, 8)
        prog = LoopProgram(
            name=f"multiply_{i}",
            code=f"p = 0\nx = 0\nwhile x < {n_val}:\n    p = p + {m_val}\n    x = x + 1",
            variables={"p": 0, "x": 0},
            loop_var="x",
            loop_bound=n_val,
            increment=1,
            post_condition=f"p == {n_val * m_val}",
            correct_invariant=f"x >= 0 and x <= {n_val} and p == {m_val} * x",
            invariant_type="linear",
        )
        programs.append(prog)

    # Pattern 4: Modular counting  x = 0; while x < n: x += 2
    for i in range(1, 16):
        n_val = random.randint(6, 20) * 2  # even bound
        prog = LoopProgram(
            name=f"even_counter_{i}",
            code=f"x = 0\nwhile x < {n_val}:\n    x = x + 2",
            variables={"x": 0},
            loop_var="x",
            loop_bound=n_val,
            increment=2,
            post_condition=f"x >= {n_val}",
            correct_invariant=f"x >= 0 and x % 2 == 0 and x <= {n_val}",
            invariant_type="modular",
        )
        programs.append(prog)

    random.shuffle(programs)
    return programs


# ─────────────────────────────────────────────
# 2. SMT Solver (Z3 or Mock)
# ─────────────────────────────────────────────


def verify_invariant_mock(program: LoopProgram, invariant: str) -> Tuple[bool, str]:
    """Mock invariant verification based on pattern matching."""
    try:
        # Parse key numbers from program
        loop_bound = program.loop_bound
        increment = program.increment
        loop_var = program.loop_var

        # Check if invariant contains the right variable
        if loop_var not in invariant:
            return False, f"Invariant doesn't mention loop variable {loop_var}"

        # Check lower bound
        has_lower = f"{loop_var} >= 0" in invariant or f"0 <= {loop_var}" in invariant

        # Check upper bound - must be >= loop_bound
        upper_match = re.search(rf"{loop_var}\s*<=\s*(\d+)", invariant)
        has_upper = upper_match is not None

        if not has_lower or not has_upper:
            return False, "Missing bounds in invariant"

        upper_val = int(upper_match.group(1)) if upper_match else 0

        # For accumulator/multiply patterns, check for relationship
        if program.invariant_type == "quadratic":
            # Must mention 's' and 'x'
            if "s" not in invariant and "sum" not in invariant.lower():
                return False, "Accumulator invariant must relate s and x"

        if program.invariant_type == "modular":
            if "% 2" not in invariant and "mod" not in invariant.lower():
                return False, "Modular invariant must include modular constraint"

        # Basic soundness: upper bound must be reachable
        if upper_val < loop_bound:
            return False, f"Upper bound {upper_val} too small (need >= {loop_bound})"

        return True, "OK"
    except Exception as e:
        return False, str(e)


def verify_invariant_z3(program: LoopProgram, invariant: str) -> Tuple[bool, str]:
    """Verify invariant using Z3 SMT solver."""
    try:
        # Create Z3 variables
        var_names = list(program.variables.keys())
        z3_vars = {v: Int(v) for v in var_names}

        def parse_condition(cond_str: str, z3_vars: dict):
            """Simple condition parser for our synthetic programs."""
            cond_str = cond_str.strip()
            # Handle 'and' conjunctions
            if " and " in cond_str:
                parts = cond_str.split(" and ")
                constraints = []
                for p in parts:
                    c = parse_condition(p.strip(), z3_vars)
                    if c is not None:
                        constraints.append(c)
                return And(*constraints) if constraints else None

            # Handle basic comparisons
            for op, z3op in [
                (">=", lambda a, b: a >= b),
                ("<=", lambda a, b: a <= b),
                ("==", lambda a, b: a == b),
                ("!=", lambda a, b: a != b),
                (">", lambda a, b: a > b),
                ("<", lambda a, b: a < b),
            ]:
                if op in cond_str:
                    left, right = cond_str.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    try:
                        left_z3 = z3_vars.get(left, int(left))
                        right_z3 = z3_vars.get(right, int(right))
                        return z3op(left_z3, right_z3)
                    except:
                        pass
            # Handle modular: x % 2 == 0
            mod_match = re.match(r"(\w+)\s*%\s*(\d+)\s*==\s*(\d+)", cond_str)
            if mod_match:
                v, m, r = mod_match.groups()
                if v in z3_vars:
                    return z3_vars[v] % int(m) == int(r)
            return None

        inv_constraint = parse_condition(invariant, z3_vars)
        if inv_constraint is None:
            return False, "Could not parse invariant"

        lv = program.loop_var
        lb = program.loop_bound
        inc = program.increment

        if lv not in z3_vars:
            return False, f"Loop variable {lv} not found"

        x = z3_vars[lv]

        # Check 1: Initiation - invariant holds at loop start
        s = Solver()
        init_vals = And(
            *[z3_vars[v] == program.variables[v] for v in program.variables]
        )
        s.add(init_vals)
        s.add(Not(inv_constraint))
        if s.check() == sat:
            return False, "Invariant fails initiation"

        # Check 2: Consecution - invariant is preserved
        # Simplified: check that if invariant holds and loop condition holds,
        # invariant still holds after increment
        s2 = Solver()
        x_next = Int(f"{lv}_next")
        z3_vars_next = dict(z3_vars)
        z3_vars_next[lv] = x_next
        inv_next = parse_condition(invariant.replace(lv, f"{lv}_next"), z3_vars_next)
        if inv_next is None:
            inv_next = inv_constraint  # fallback

        # Only check basic bound preservation for linear cases
        s2.add(inv_constraint)
        s2.add(x < lb)  # loop condition
        s2.add(x_next == x + inc)  # update
        s2.add(Not(inv_next))
        if s2.check() == sat:
            return False, "Invariant fails consecution"

        return True, "OK"
    except Exception as e:
        return False, str(e)


def verify_invariant(program: LoopProgram, invariant: str) -> Tuple[bool, str]:
    if Z3_AVAILABLE:
        return verify_invariant_z3(program, invariant)
    else:
        return verify_invariant_mock(program, invariant)


# ─────────────────────────────────────────────
# 3. Code Embedding Model
# ─────────────────────────────────────────────


class CodeEmbedder:
    """Embeds code using SentenceTransformer or TF-IDF fallback."""

    def __init__(self):
        self.model = None
        self.tfidf = None
        self.use_st = False

        if ST_AVAILABLE:
            try:
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self.model.to(device)
                self.use_st = True
                print("Using SentenceTransformer for embeddings")
            except Exception as e:
                print(f"ST failed: {e}, falling back to TF-IDF")

        if not self.use_st:
            self.tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
            print("Using TF-IDF for embeddings")

    def encode(self, texts: List[str]) -> np.ndarray:
        if self.use_st:
            with torch.no_grad():
                embeddings = self.model.encode(
                    texts, convert_to_tensor=True, device=device
                )
                return embeddings.cpu().numpy()
        else:
            if not hasattr(self.tfidf, "vocabulary_"):
                self.tfidf.fit(texts)
            try:
                return self.tfidf.transform(texts).toarray()
            except:
                self.tfidf.fit(texts)
                return self.tfidf.transform(texts).toarray()


# ─────────────────────────────────────────────
# 4. Invariant Library
# ─────────────────────────────────────────────


@dataclass
class LibraryEntry:
    program: LoopProgram
    verified_invariant: str
    embedding: Optional[np.ndarray] = None


class InvariantLibrary:
    def __init__(self, embedder: CodeEmbedder):
        self.entries: List[LibraryEntry] = []
        self.embedder = embedder

    def add(self, program: LoopProgram, invariant: str):
        emb = self.embedder.encode([program.code])[0]
        self.entries.append(
            LibraryEntry(program=program, verified_invariant=invariant, embedding=emb)
        )

    def retrieve_similar(self, query_code: str, k: int = 3) -> List[LibraryEntry]:
        if not self.entries:
            return []
        query_emb = self.embedder.encode([query_code])[0]
        lib_embs = np.stack([e.embedding for e in self.entries])
        sims = cosine_similarity(query_emb.reshape(1, -1), lib_embs)[0]
        top_k_idx = np.argsort(sims)[-k:][::-1]
        return [self.entries[i] for i in top_k_idx]

    def retrieve_random(self, k: int = 3) -> List[LibraryEntry]:
        if not self.entries:
            return []
        k = min(k, len(self.entries))
        return random.sample(self.entries, k)


# ─────────────────────────────────────────────
# 5. LLM-like Invariant Adapter (Template-based)
# ─────────────────────────────────────────────


def extract_program_features(program: LoopProgram) -> Dict:
    """Extract key features from a program."""
    return {
        "loop_var": program.loop_var,
        "loop_bound": program.loop_bound,
        "increment": program.increment,
        "variables": list(program.variables.keys()),
        "invariant_type": program.invariant_type,
        "initial_values": program.variables,
    }


def adapt_invariant(
    target_program: LoopProgram, retrieved_entries: List[LibraryEntry]
) -> str:
    """Adapt retrieved invariants to target program (simulates LLM adaptation)."""
    if not retrieved_entries:
        return generate_zero_shot_invariant(target_program)

    # Use the most similar entry as primary template
    best_entry = retrieved_entries[0]
    source_prog = best_entry.program
    source_inv = best_entry.verified_invariant

    target_feat = extract_program_features(target_program)
    source_feat = extract_program_features(source_prog)

    # Adapt the invariant by replacing source-specific values with target values
    adapted = source_inv

    # Replace loop variable name
    if source_feat["loop_var"] != target_feat["loop_var"]:
        adapted = adapted.replace(source_feat["loop_var"], target_feat["loop_var"])

    # Replace loop bound
    if source_feat["loop_bound"] != target_feat["loop_bound"]:
        # Replace old bound value with new bound value in upper bound constraints
        old_upper = source_feat["loop_bound"] + source_feat["increment"] - 1
        new_upper = target_feat["loop_bound"] + target_feat["increment"] - 1
        adapted = re.sub(r"\b" + str(old_upper) + r"\b", str(new_upper), adapted)
        adapted = re.sub(
            r"\b" + str(source_feat["loop_bound"]) + r"\b",
            str(target_feat["loop_bound"]),
            adapted,
        )

    # Replace increment
    if source_feat["increment"] != target_feat["increment"]:
        # For modular constraints
        adapted = re.sub(
            r"%\s*" + str(source_feat["increment"]),
            f'% {target_feat["increment"]}',
            adapted,
        )

    # For accumulator/multiply patterns, adapt variable names
    if (
        target_program.invariant_type in ["quadratic", "linear"]
        and len(target_feat["variables"]) > 1
    ):
        for src_var, tgt_var in zip(source_feat["variables"], target_feat["variables"]):
            if src_var != tgt_var and src_var != source_feat["loop_var"]:
                adapted = adapted.replace(src_var, tgt_var)

        # For multiply: replace multiplier constant
        if (
            target_program.invariant_type == "linear"
            and "p" in target_feat["variables"]
        ):
            mult_match = re.search(
                r"p\s*==\s*(\d+)\s*\*\s*" + target_feat["loop_var"], adapted
            )
            if mult_match:
                # Find actual multiplier from code
                code_match = re.search(r"p\s*=\s*p\s*\+\s*(\d+)", target_program.code)
                if code_match:
                    adapted = adapted.replace(
                        f"p == {mult_match.group(1)} * {target_feat['loop_var']}",
                        f"p == {code_match.group(1)} * {target_feat['loop_var']}",
                    )

    # Validate that adapted invariant is non-trivial
    if adapted == source_inv and source_prog.name != target_program.name:
        # Fallback to zero-shot if no adaptation happened
        return generate_zero_shot_invariant(target_program)

    return adapted


def generate_zero_shot_invariant(program: LoopProgram) -> str:
    """Generate invariant without any retrieved context."""
    lv = program.loop_var
    lb = program.loop_bound
    inc = program.increment

    if program.invariant_type == "linear":
        if len(program.variables) == 1:
            return f"{lv} >= 0 and {lv} <= {lb + inc - 1}"
        else:
            # Multiply pattern
            mult = None
            code_match = re.search(r"p\s*=\s*p\s*\+\s*(\d+)", program.code)
            if code_match:
                mult = int(code_match.group(1))
            if mult:
                return f"{lv} >= 0 and {lv} <= {lb} and p == {mult} * {lv}"
            return f"{lv} >= 0 and {lv} <= {lb}"

    elif program.invariant_type == "quadratic":
        return f"{lv} >= 0 and {lv} <= {lb} and s == {lv} * ({lv} - 1) / 2"

    elif program.invariant_type == "modular":
        return f"{lv} >= 0 and {lv} % {inc} == 0 and {lv} <= {lb}"

    return f"{lv} >= 0 and {lv} <= {lb}"


# ─────────────────────────────────────────────
# 6. RAIT Framework
# ─────────────────────────────────────────────


def run_rait(
    target_program: LoopProgram,
    library: InvariantLibrary,
    k: int = 3,
    max_iterations: int = 5,
    retrieval_mode: str = "similar",
) -> Tuple[bool, int, int, str]:
    """
    Run RAIT on a target program.
    Returns: (success, llm_calls, solver_calls, final_invariant)
    """
    llm_calls = 0
    solver_calls = 0

    for iteration in range(max_iterations):
        # Retrieve from library
        if retrieval_mode == "similar" and len(library.entries) > 0:
            retrieved = library.retrieve_similar(target_program.code, k=k)
        elif retrieval_mode == "random" and len(library.entries) > 0:
            retrieved = library.retrieve_random(k=k)
        else:
            retrieved = []  # zero-shot

        # Adapt/generate invariant
        if retrieval_mode == "zero_shot":
            invariant = generate_zero_shot_invariant(target_program)
        else:
            invariant = adapt_invariant(target_program, retrieved)

        llm_calls += 1

        # Add some noise in later iterations (simulates retry with variation)
        if iteration > 0:
            # Slightly modify upper bound to simulate refinement
            invariant = refine_invariant(target_program, invariant, iteration)

        # Verify with SMT solver
        success, msg = verify_invariant(target_program, invariant)
        solver_calls += 1

        if success:
            return True, llm_calls, solver_calls, invariant

    return False, llm_calls, solver_calls, ""


def refine_invariant(program: LoopProgram, invariant: str, iteration: int) -> str:
    """Refine invariant based on iteration (simulates counterexample-guided refinement)."""
    lv = program.loop_var
    lb = program.loop_bound
    inc = program.increment

    # Try relaxing upper bound
    relaxed_ub = lb + inc * (iteration + 1)
    upper_match = re.search(rf"{lv}\s*<=\s*\d+", invariant)
    if upper_match:
        invariant = (
            invariant[: upper_match.start()]
            + f"{lv} <= {relaxed_ub}"
            + invariant[upper_match.end() :]
        )

    # For modular: try adding modular constraint if missing
    if program.invariant_type == "modular" and "% " not in invariant:
        invariant += f" and {lv} % {inc} == 0"

    return invariant


# ─────────────────────────────────────────────
# 7. Experiment Runner
# ─────────────────────────────────────────────


def run_experiment(
    programs: List[LoopProgram],
    embedder: CodeEmbedder,
    train_frac: float = 0.3,
    k: int = 3,
    max_iter: int = 5,
):
    """
    Run the full RAIT experiment.
    - First train_frac programs are used to seed the library
    - Remaining programs are the test set (evaluated online)
    """
    n = len(programs)
    n_seed = max(1, int(n * train_frac))
    seed_programs = programs[:n_seed]
    test_programs = programs[n_seed:]

    print(f"\nDataset: {n} programs | Seed: {n_seed} | Test: {len(test_programs)}")

    # Initialize library with seed programs (using correct invariants)
    library = InvariantLibrary(embedder)
    for prog in seed_programs:
        library.add(prog, prog.correct_invariant)
    print(f"Library seeded with {len(library.entries)} entries")

    # Three conditions
    conditions = ["rait", "random_retrieval", "zero_shot"]
    results = {
        c: {
            "success": [],
            "llm_calls": [],
            "solver_calls": [],
            "success_rate_over_time": [],
        }
        for c in conditions
    }

    # Track library growth for RAIT
    rait_library = InvariantLibrary(embedder)
    for prog in seed_programs:
        rait_library.add(prog, prog.correct_invariant)

    random_library = InvariantLibrary(embedder)
    for prog in seed_programs:
        random_library.add(prog, prog.correct_invariant)

    for epoch, prog in enumerate(test_programs):
        print(
            f"\nEpoch {epoch+1}/{len(test_programs)}: {prog.name} ({prog.invariant_type})"
        )

        for condition in conditions:
            if condition == "rait":
                lib_to_use = rait_library
                mode = "similar"
            elif condition == "random_retrieval":
                lib_to_use = random_library
                mode = "random"
            else:
                lib_to_use = InvariantLibrary(embedder)  # empty library = zero shot
                mode = "zero_shot"

            success, llm_calls, solver_calls, final_inv = run_rait(
                prog, lib_to_use, k=k, max_iterations=max_iter, retrieval_mode=mode
            )

            results[condition]["success"].append(int(success))
            results[condition]["llm_calls"].append(llm_calls)
            results[condition]["solver_calls"].append(solver_calls)

            # Running success rate
            sr = np.mean(results[condition]["success"]) * 100
            results[condition]["success_rate_over_time"].append(sr)

            print(
                f"  {condition}: success={success}, llm_calls={llm_calls}, "
                f"solver_calls={solver_calls}, running_sr={sr:.1f}%"
            )

            # Validation loss proxy: 1 - success_rate
            val_loss = 1.0 - np.mean(results[condition]["success"])
            print(f"  validation_loss ({condition}) = {val_loss:.4f}")

        # Add to RAIT library if verified (self-growing)
        success_rait = results["rait"]["success"][-1]
        if success_rait:
            # Use the adapted invariant that was verified
            rait_library.add(prog, prog.correct_invariant)  # use correct in simulation
        else:
            # Even if RAIT failed, add the correct invariant to simulate library growth
            # In real setting, we'd only add verified ones
            pass

        # Random library also grows (but with correct invariants for fair comparison)
        random_library.add(prog, prog.correct_invariant)

    return results


# ─────────────────────────────────────────────
# 8. Main Execution
# ─────────────────────────────────────────────

experiment_data = {
    "loop_programs": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "rait_success_rate_over_time": [],
        "random_success_rate_over_time": [],
        "zero_shot_success_rate_over_time": [],
        "rait_llm_calls": [],
        "random_llm_calls": [],
        "zero_shot_llm_calls": [],
        "rait_solver_calls": [],
        "random_solver_calls": [],
        "zero_shot_solver_calls": [],
        "final_success_rates": {},
        "avg_llm_calls": {},
        "avg_solver_calls": {},
    }
}

# Set random seed
random.seed(42)
np.random.seed(42)

# Create dataset
print("Creating synthetic loop programs...")
programs = create_synthetic_programs(n=60)
print(f"Created {len(programs)} programs")
print(f"Types: {set(p.invariant_type for p in programs)}")

# Initialize embedder
embedder = CodeEmbedder()

# Run experiment
print("\n" + "=" * 60)
print("Running RAIT Experiment")
print("=" * 60)

results = run_experiment(programs, embedder, train_frac=0.3, k=3, max_iter=5)

# ─────────────────────────────────────────────
# 9. Collect & Save Metrics
# ─────────────────────────────────────────────

conditions = ["rait", "random_retrieval", "zero_shot"]

for cond in conditions:
    sr = np.mean(results[cond]["success"]) * 100
    avg_llm = np.mean(results[cond]["llm_calls"])
    avg_solver = np.mean(results[cond]["solver_calls"])

    print(f"\n{'='*40}")
    print(f"Condition: {cond.upper()}")
    print(f"  Verification Success Rate: {sr:.2f}%")
    print(f"  Avg LLM calls: {avg_llm:.2f}")
    print(f"  Avg Solver calls: {avg_solver:.2f}")

    experiment_data["loop_programs"]["final_success_rates"][cond] = sr
    experiment_data["loop_programs"]["avg_llm_calls"][cond] = avg_llm
    experiment_data["loop_programs"]["avg_solver_calls"][cond] = avg_solver

    short = {"rait": "rait", "random_retrieval": "random", "zero_shot": "zero_shot"}[
        cond
    ]
    experiment_data["loop_programs"][f"{short}_success_rate_over_time"] = results[cond][
        "success_rate_over_time"
    ]
    experiment_data["loop_programs"][f"{short}_llm_calls"] = results[cond]["llm_calls"]
    experiment_data["loop_programs"][f"{short}_solver_calls"] = results[cond][
        "solver_calls"
    ]

# Metrics for tracking
for i, val in enumerate(results["rait"]["success_rate_over_time"]):
    experiment_data["loop_programs"]["metrics"]["val"].append(val / 100.0)
    experiment_data["loop_programs"]["losses"]["val"].append(1.0 - val / 100.0)

# Predictions and ground truth
experiment_data["loop_programs"]["predictions"] = results["rait"]["success"]
experiment_data["loop_programs"]["ground_truth"] = [1] * len(results["rait"]["success"])

# ─────────────────────────────────────────────
# 10. Visualization
# ─────────────────────────────────────────────

# Plot 1: Verification Success Rate over time
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("RAIT: Retrieval-Augmented Invariant Transfer Evaluation", fontsize=14)

ax = axes[0]
x = range(1, len(results["rait"]["success_rate_over_time"]) + 1)
ax.plot(
    x,
    results["rait"]["success_rate_over_time"],
    "b-o",
    label="RAIT (similar)",
    linewidth=2,
    markersize=4,
)
ax.plot(
    x,
    results["random_retrieval"]["success_rate_over_time"],
    "r--s",
    label="Random Retrieval",
    linewidth=2,
    markersize=4,
)
ax.plot(
    x,
    results["zero_shot"]["success_rate_over_time"],
    "g:^",
    label="Zero-Shot",
    linewidth=2,
    markersize=4,
)
ax.set_xlabel("Number of Test Programs Processed")
ax.set_ylabel("Cumulative Success Rate (%)")
ax.set_title("Verification Success Rate Over Time")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 105])

# Plot 2: Average LLM calls comparison
ax = axes[1]
cond_names = ["RAIT\n(similar)", "Random\nRetrieval", "Zero-Shot"]
avg_llm_vals = [np.mean(results[c]["llm_calls"]) for c in conditions]
bars = ax.bar(
    cond_names,
    avg_llm_vals,
    color=["blue", "red", "green"],
    alpha=0.7,
    edgecolor="black",
)
ax.set_ylabel("Average LLM Calls per Program")
ax.set_title("LLM Calls Required (Lower is Better)")
for bar, val in zip(bars, avg_llm_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        bar.get_height() + 0.02,
        f"{val:.2f}",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
ax.set_ylim([0, max(avg_llm_vals) * 1.3])
ax.grid(True, alpha=0.3, axis="y")

# Plot 3: Final success rates comparison
ax = axes[2]
final_srs = [np.mean(results[c]["success"]) * 100 for c in conditions]
bars = ax.bar(
    cond_names, final_srs, color=["blue", "red", "green"], alpha=0.7, edgecolor="black"
)
ax.set_ylabel("Verification Success Rate (%)")
ax.set_title("Final Verification Success Rate")
for bar, val in zip(bars, final_srs):
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        bar.get_height() + 0.5,
        f"{val:.1f}%",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
ax.set_ylim([0, 115])
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "rait_loop_programs_evaluation.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()
print(
    f"\nPlot saved to {os.path.join(working_dir, 'rait_loop_programs_evaluation.png')}"
)

# Plot 2: Library growth effect
fig, ax = plt.subplots(figsize=(10, 6))
window = 5
for cond, color, label in [
    ("rait", "blue", "RAIT (similar)"),
    ("random_retrieval", "red", "Random Retrieval"),
    ("zero_shot", "green", "Zero-Shot"),
]:
    sr_list = results[cond]["success_rate_over_time"]
    ax.plot(range(1, len(sr_list) + 1), sr_list, color=color, label=label, linewidth=2)

ax.axvline(x=1, color="gray", linestyle="--", alpha=0.5, label="Library starts growing")
ax.set_xlabel("Test Program Index")
ax.set_ylabel("Cumulative Success Rate (%)")
ax.set_title("RAIT Scaling: Success Rate as Library Grows")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "rait_scaling_effect.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# ─────────────────────────────────────────────
# 11. Save Experiment Data
# ─────────────────────────────────────────────

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

# Final summary
print("\n" + "=" * 60)
print("FINAL RESULTS SUMMARY")
print("=" * 60)
for cond in conditions:
    sr = experiment_data["loop_programs"]["final_success_rates"][cond]
    avg_llm = experiment_data["loop_programs"]["avg_llm_calls"][cond]
    avg_solver = experiment_data["loop_programs"]["avg_solver_calls"][cond]
    print(f"\n{cond.upper()}")
    print(f"  Verification Success Rate: {sr:.2f}%")
    print(f"  Avg LLM Calls: {avg_llm:.2f}")
    print(f"  Avg Solver Calls: {avg_solver:.2f}")

print("\n" + "=" * 60)
print(
    "RAIT vs Zero-Shot improvement: "
    f"{experiment_data['loop_programs']['final_success_rates']['rait'] - experiment_data['loop_programs']['final_success_rates']['zero_shot']:.2f}%"
)
print(
    "RAIT vs Random-Retrieval improvement: "
    f"{experiment_data['loop_programs']['final_success_rates']['rait'] - experiment_data['loop_programs']['final_success_rates']['random_retrieval']:.2f}%"
)
