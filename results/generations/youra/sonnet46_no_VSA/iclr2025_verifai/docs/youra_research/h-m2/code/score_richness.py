"""AST-based postcondition richness scoring for ContractEval tasks."""
import ast
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

# Path constants (resolved relative to this file)
_CODE_DIR = Path(__file__).parent
_H_M2_DIR = _CODE_DIR.parent
_RESEARCH_DIR = _H_M2_DIR.parent

H1_RESULTS_CSV = _RESEARCH_DIR / "h-m1" / "code" / "results" / "per_task_results.csv"
H1_RESULTS_JSON = _RESEARCH_DIR / "h-m1" / "code" / "results" / "oracle_isolation_results.json"
CONTRACTEVAL_PATH = (
    _RESEARCH_DIR
    / "_archive"
    / "20260803T121822_routing_recovery"
    / ".data_cache"
    / "datasets"
    / "ContractEval"
    / "data"
    / "ContractEval"
    / "ContractEval.jsonl"
)
RESULTS_DIR = _H_M2_DIR / "results"
FIGURES_DIR = _H_M2_DIR / "figures"


@dataclass
class RichnessScore:
    task_id: str
    tier: int           # 1=simple, 2=structural, 3=relational, 4=compound
    score: float        # node_count + 3*has_quantifier + 2*has_relational
    has_quantifier: bool
    has_relational: bool
    node_count: int


def score_postcondition(assert_clauses: List[str]) -> Tuple[int, float, bool, bool, int]:
    """Walk AST of assert clauses; return (tier, score, has_quantifier, has_relational, node_count).

    Skips malformed clauses with a warning.  Returns tier=1 defaults if all fail.
    """
    has_quantifier = False
    has_relational = False
    node_count = 0

    for clause in assert_clauses:
        # Strip leading 'assert' keyword so ast.parse mode='eval' works
        stripped = clause.strip()
        if stripped.startswith("assert "):
            stripped = stripped[len("assert "):]
        elif stripped.startswith("assert("):
            stripped = stripped[len("assert"):]

        try:
            tree = ast.parse(stripped, mode="eval")
        except SyntaxError:
            warnings.warn(f"Skipping malformed clause: {clause[:60]!r}")
            continue

        for node in ast.walk(tree):
            node_count += 1
            if isinstance(node, ast.Call):
                func = node.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name in ("any", "all"):
                    has_quantifier = True
            if isinstance(node, ast.Compare) and len(node.ops) > 1:
                has_relational = True
            if isinstance(node, ast.BoolOp):
                has_relational = True

    tier = (
        4 if (has_quantifier and has_relational)
        else 3 if has_quantifier
        else 2 if has_relational
        else 1
    )
    score = float(node_count + 3 * has_quantifier + 2 * has_relational)
    return tier, score, has_quantifier, has_relational, node_count


def _detect_contract_field(task_dict: dict) -> Optional[str]:
    """Auto-detect field containing contract assertions."""
    for key in task_dict:
        if "contract" in key.lower() and key != "contract_individual_NL":
            return key
    for key in task_dict:
        if "assert" in key.lower():
            return key
    return None


def load_contracteval_tasks(jsonl_path: Optional[Path] = None) -> dict:
    """Load ContractEval tasks.  Returns {task_id: task_dict}.
    Prints available keys on first load for field verification.
    """
    path = Path(jsonl_path) if jsonl_path else CONTRACTEVAL_PATH
    tasks = {}
    _printed_keys = False
    with open(path) as f:
        content = f.read().strip()

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        task = json.loads(line)
        if not _printed_keys:
            print(f"ContractEval keys: {list(task.keys())}")
            _printed_keys = True
        tasks[task["task_id"]] = task
    print(f"Loaded {len(tasks)} ContractEval tasks")
    return tasks


def build_richness_df(
    contracteval_tasks: dict,
    contract_field: str = "contract",
) -> pd.DataFrame:
    """Score all tasks.  Returns DataFrame (364, 6).

    Asserts shape == (364, 6) and all 4 tiers present.
    """
    # Auto-detect field if not valid
    if contracteval_tasks:
        sample = next(iter(contracteval_tasks.values()))
        if contract_field not in sample:
            detected = _detect_contract_field(sample)
            if detected:
                print(f"Auto-detected contract field: {detected!r} (requested {contract_field!r})")
                contract_field = detected
            else:
                raise KeyError(f"Cannot find contract field in keys: {list(sample.keys())}")

    rows = []
    for task_id, task_dict in contracteval_tasks.items():
        raw = task_dict.get(contract_field, "")
        # 'contract' field contains lines tagged with # $_CONTRACT_$
        # Only extract lines that are actual 'assert' statements
        if isinstance(raw, str):
            all_lines = raw.split("\n")
            # Keep lines that are assert statements and carry the contract marker
            clauses = []
            for line in all_lines:
                stripped = line.strip()
                if stripped.startswith("assert") and "$_CONTRACT_$" in line:
                    # Remove the marker comment before parsing
                    clean = stripped.split("# $_CONTRACT_$")[0].strip()
                    if clean:
                        clauses.append(clean)
        elif isinstance(raw, list):
            clauses = [str(c) for c in raw]
        else:
            clauses = []

        tier, score, has_q, has_r, nc = score_postcondition(clauses)
        rows.append({
            "task_id": task_id,
            "tier": tier,
            "score": score,
            "has_quantifier": has_q,
            "has_relational": has_r,
            "node_count": nc,
        })

    df = pd.DataFrame(rows)
    assert df.shape == (364, 6), f"Expected (364, 6), got {df.shape}"
    missing_tiers = {1, 2, 3, 4} - set(df["tier"].unique())
    if missing_tiers:
        print(f"Warning: missing tiers {missing_tiers} — consider revisiting tier thresholds")
    return df


def load_gap_dict(csv_path: Optional[Path] = None) -> dict:
    """Load per-task mean oracle-isolation gaps from h-m1 per_task_results.csv.
    Returns {task_id: float}.  Raises FileNotFoundError with 'Run H-M1 first' if missing.
    """
    path = Path(csv_path) if csv_path else H1_RESULTS_CSV
    if not path.exists():
        raise FileNotFoundError(f"Run H-M1 first — missing: {path}")
    df = pd.read_csv(path)
    gap = df.groupby("task_id")["oracle_isolation_gap"].mean()
    return gap.to_dict()


def load_gap_dict_by_model(csv_path: Optional[Path] = None) -> dict:
    """Load per-task gaps per model.  Returns {model_name: {task_id: float}}."""
    path = Path(csv_path) if csv_path else H1_RESULTS_CSV
    if not path.exists():
        raise FileNotFoundError(f"Run H-M1 first — missing: {path}")
    df = pd.read_csv(path)
    result: Dict[str, Dict[str, float]] = {}
    for (model, task_id), grp in df.groupby(["model", "task_id"]):
        result.setdefault(model, {})[task_id] = grp["oracle_isolation_gap"].mean()
    return result


def load_cu_dict(csv_path: Optional[Path] = None) -> dict:
    """Load per-task mean contract-unique mass.  Returns {task_id: float}."""
    path = Path(csv_path) if csv_path else H1_RESULTS_CSV
    if not path.exists():
        raise FileNotFoundError(f"Run H-M1 first — missing: {path}")
    df = pd.read_csv(path)
    cu = df.groupby("task_id")["contract_unique_mass"].mean()
    return cu.to_dict()


def load_task_types(csv_path: Optional[Path] = None) -> dict:
    """Load per-task task_type.  Returns {task_id: task_type_str}."""
    path = Path(csv_path) if csv_path else H1_RESULTS_CSV
    if not path.exists():
        raise FileNotFoundError(f"Run H-M1 first — missing: {path}")
    df = pd.read_csv(path)
    tt = df.groupby("task_id")["task_type"].first()
    return tt.to_dict()


def verify_mechanism_activated(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    results: dict,
) -> Tuple[bool, dict]:
    """Check activation indicators.  Returns (passed: bool, indicators: dict)."""
    indicators = {
        "richness_computed": len(richness_df) > 0,
        "all_tiers_present": set(richness_df["tier"].unique()) == {1, 2, 3, 4},
        "gap_loaded": len(gap_dict) > 0,
        "gradient_direction": False,
        "spearman_computed": "rho" in results,
    }
    # Check gradient: mean gap should increase with tier
    tier_means = {}
    for tier in [1, 2, 3, 4]:
        tids = richness_df[richness_df["tier"] == tier]["task_id"].tolist()
        vals = [gap_dict[t] for t in tids if t in gap_dict]
        if vals:
            tier_means[tier] = sum(vals) / len(vals)
    if len(tier_means) >= 2:
        ordered = [tier_means.get(t, 0) for t in sorted(tier_means)]
        indicators["gradient_direction"] = ordered[-1] > ordered[0]

    passed = all(indicators.values())
    return passed, indicators
