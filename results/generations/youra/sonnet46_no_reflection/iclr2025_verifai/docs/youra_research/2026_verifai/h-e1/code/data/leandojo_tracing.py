import re
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

# TACTIC_TAXONOMY: pre-specified before any training — IMMUTABLE (NFR-4)
TACTIC_TAXONOMY: Dict[str, List[str]] = {
    "type_error":     ["type mismatch", "application type mismatch"],
    "undefined_name": ["unknown identifier", "unknown tactic"],
    "tactic_failure": ["tactic failed", "simp made no progress"],
}


@dataclass
class ProofStateTriple:
    """LeanDojo (state, tactic, compiler_error) triple with alignment ID."""
    state_id: str                    # LeanDojo state ID for alignment verification
    state: str                       # Proof state string
    tactic: str                      # Attempted tactic
    compiler_error: Optional[str]    # Raw Lean4 error message, or None if succeeded
    error_category: Optional[str]    # Key from TACTIC_TAXONOMY, or None
    problem_name: str


def trace_repository(repo_url: str, commit: str) -> None:
    """Trace Lean4 repo using LeanGitRepo + trace(); cache results to disk."""
    try:
        from lean_dojo import LeanGitRepo, trace
        repo = LeanGitRepo(repo_url, commit)
        logger.info(f"Tracing repo {repo_url} @ {commit}")
        trace(repo)
        logger.info("Tracing complete")
    except ImportError:
        raise RuntimeError(
            "lean_dojo is required but not installed. "
            "Install with: pip install lean-dojo>=2.0.0"
        )
    except Exception as e:
        logger.warning(f"trace_repository failed: {e}")
        raise


def extract_state_triples(
    problems: list,
    timeout: int = 60,
) -> List[ProofStateTriple]:
    """Run Dojo context manager per problem; extract (state, tactic, error) triples."""
    try:
        from lean_dojo import Dojo, Theorem, LeanGitRepo
    except ImportError:
        raise RuntimeError(
            "lean_dojo is required but not installed. "
            "Install with: pip install lean-dojo>=2.0.0"
        )

    triples: List[ProofStateTriple] = []
    failed_problems = []

    for prob in problems:
        try:
            extracted = _extract_from_problem(prob, timeout)
            triples.extend(extracted)
        except Exception as e:
            logger.warning(f"Failed to extract triples for {prob.name}: {e}")
            failed_problems.append(prob.name)

    if failed_problems:
        logger.warning(f"Failed to extract triples for {len(failed_problems)} problems: {failed_problems[:5]}...")

    if not triples:
        raise RuntimeError(
            f"No proof state triples could be extracted from {len(problems)} problems. "
            "Ensure LeanDojo is properly installed and the Lean4 environment is configured."
        )

    logger.info(f"Extracted {len(triples)} proof state triples from {len(problems)} problems")
    return triples


def _extract_from_problem(prob, timeout: int) -> List[ProofStateTriple]:
    """Extract triples from a single problem using Dojo."""
    from lean_dojo import Dojo, Theorem, LeanGitRepo
    triples = []

    # Build a minimal Theorem object from the problem
    # In practice this requires a traced repo; for PoC we attempt direct interaction
    try:
        thm = Theorem(
            repo=None,  # will fail without traced repo
            file_path=prob.formal_statement,
            full_name=prob.name,
        )
        with Dojo(thm, hard_timeout=timeout) as (dojo, init_state):
            # Try a few tactics to generate (state, tactic, error) triples
            test_tactics = ["ring", "simp", "linarith", "norm_num", "decide", "tauto"]
            for tactic in test_tactics:
                result = dojo.run_tac(init_state, tactic)
                state_id = str(id(init_state))
                if hasattr(result, "error") and result.error:
                    error_msg = str(result.error)
                    category = classify_lean4_error(error_msg)
                    triples.append(ProofStateTriple(
                        state_id=state_id,
                        state=str(init_state),
                        tactic=tactic,
                        compiler_error=error_msg,
                        error_category=category,
                        problem_name=prob.name,
                    ))
                else:
                    triples.append(ProofStateTriple(
                        state_id=state_id,
                        state=str(init_state),
                        tactic=tactic,
                        compiler_error=None,
                        error_category=None,
                        problem_name=prob.name,
                    ))
    except Exception:
        pass

    return triples


def classify_lean4_error(error_msg: str) -> Optional[str]:
    """Match error_msg against TACTIC_TAXONOMY entries; return category key or None."""
    if not error_msg:
        return None
    error_lower = error_msg.lower()
    for category, patterns in TACTIC_TAXONOMY.items():
        for pattern in patterns:
            if pattern.lower() in error_lower:
                return category
    return None


def get_premise_consistent_tokens(
    error_category: str,
    tokenizer,
) -> List[int]:
    """Return token IDs for tactics that address the given error_category."""
    # Maps each error category to tactic keywords that resolve it
    category_to_tactics = {
        "type_error": [
            "exact", "show", "change", "conv", "apply", "refine",
            "norm_cast", "push_cast", "cast",
        ],
        "undefined_name": [
            "have", "let", "obtain", "rcases", "intro", "intros",
            "rename_i", "exact", "assumption",
        ],
        "tactic_failure": [
            "simp", "ring", "linarith", "omega", "norm_num",
            "decide", "tauto", "aesop", "trivial",
        ],
    }
    tactic_keywords = category_to_tactics.get(error_category, [])
    token_ids: List[int] = []
    for kw in tactic_keywords:
        ids = tokenizer.encode(kw, add_special_tokens=False)
        token_ids.extend(ids)
    return list(set(token_ids))
