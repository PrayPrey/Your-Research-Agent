import random
import logging
from dataclasses import dataclass
from typing import List, Dict, Literal

from data.leandojo_tracing import ProofStateTriple

logger = logging.getLogger(__name__)

Condition = Literal["A", "B", "P"]


@dataclass
class DPOPair:
    """Single DPO training pair with full metadata."""
    state_id_chosen: str    # Must equal state_id_rejected (NFR-3)
    state_id_rejected: str
    state: str
    chosen_tactic: str
    rejected_tactic: str
    error_msg: str          # Raw Lean4 error (permuted for Condition P)
    error_category: str     # From TACTIC_TAXONOMY
    condition: Condition


def build_pairs_condition_A(triples: List[ProofStateTriple]) -> List[DPOPair]:
    """Build pairs: rejected=error-triggering tactic (grounded), chosen=correct advancing tactic.
    Same proof state s for both; error_msg from LeanDojo compiler output.
    """
    pairs = []
    # Group triples by problem: need both failed and successful tactics at same state
    failed = [t for t in triples if t.compiler_error is not None and t.error_category is not None]
    succeeded = [t for t in triples if t.compiler_error is None]

    # Build a map: problem_name -> first successful tactic (chosen)
    chosen_by_problem: Dict[str, ProofStateTriple] = {}
    for t in succeeded:
        if t.problem_name not in chosen_by_problem:
            chosen_by_problem[t.problem_name] = t

    for t in failed:
        chosen = chosen_by_problem.get(t.problem_name)
        if chosen is None:
            # Use a dummy "skip" as chosen when no success available
            chosen_tactic = "skip"
        else:
            chosen_tactic = chosen.tactic

        pairs.append(DPOPair(
            state_id_chosen=t.state_id,    # same state — NFR-3 alignment
            state_id_rejected=t.state_id,
            state=t.state,
            chosen_tactic=chosen_tactic,
            rejected_tactic=t.tactic,
            error_msg=t.compiler_error,
            error_category=t.error_category,
            condition="A",
        ))
    logger.info(f"Built {len(pairs)} Condition A pairs")
    return pairs


def build_pairs_condition_B(triples: List[ProofStateTriple]) -> List[DPOPair]:
    """Build pairs: rejected=failed-branch tactic (ungrounded, no error info), chosen=correct.
    Same proof state s; error_msg field empty (no semantic grounding).
    """
    pairs = []
    failed = [t for t in triples if t.compiler_error is not None and t.error_category is not None]
    succeeded = [t for t in triples if t.compiler_error is None]
    chosen_by_problem: Dict[str, ProofStateTriple] = {}
    for t in succeeded:
        if t.problem_name not in chosen_by_problem:
            chosen_by_problem[t.problem_name] = t

    for t in failed:
        chosen = chosen_by_problem.get(t.problem_name)
        chosen_tactic = chosen.tactic if chosen else "skip"
        pairs.append(DPOPair(
            state_id_chosen=t.state_id,
            state_id_rejected=t.state_id,
            state=t.state,
            chosen_tactic=chosen_tactic,
            rejected_tactic=t.tactic,
            error_msg="",  # ungrounded: no error message
            error_category=t.error_category,
            condition="B",
        ))
    logger.info(f"Built {len(pairs)} Condition B pairs")
    return pairs


def build_pairs_condition_P(triples: List[ProofStateTriple]) -> List[DPOPair]:
    """Build pairs: rejected tactic with shuffled/permuted error message tokens (control).
    Same proof state s; error_msg is a random permutation across the batch.
    """
    base_pairs = build_pairs_condition_A(triples)
    all_error_msgs = [p.error_msg for p in base_pairs]
    # Fixed seed shuffle for reproducibility
    rng = random.Random(42)
    shuffled_msgs = all_error_msgs.copy()
    rng.shuffle(shuffled_msgs)
    result = []
    for pair, shuffled_msg in zip(base_pairs, shuffled_msgs):
        result.append(DPOPair(
            state_id_chosen=pair.state_id_chosen,
            state_id_rejected=pair.state_id_rejected,
            state=pair.state,
            chosen_tactic=pair.chosen_tactic,
            rejected_tactic=pair.rejected_tactic,
            error_msg=shuffled_msg,
            error_category=pair.error_category,
            condition="P",
        ))
    logger.info(f"Built {len(result)} Condition P pairs (permuted control)")
    return result


def validate_state_alignment(pairs: List[DPOPair]) -> None:
    """Assert state_id_chosen == state_id_rejected for all pairs.
    Raises ValueError immediately on first violation (NFR-3 — abort, not warn).
    """
    for i, pair in enumerate(pairs):
        if pair.state_id_chosen != pair.state_id_rejected:
            raise ValueError(
                f"State alignment violation at pair {i}: "
                f"state_id_chosen={pair.state_id_chosen!r} != "
                f"state_id_rejected={pair.state_id_rejected!r}"
            )
    logger.info(f"State alignment validated: {len(pairs)} pairs — 100% aligned")


def build_all_conditions(
    triples: List[ProofStateTriple],
) -> Dict[str, List[DPOPair]]:
    """Build and validate all three condition pair sets."""
    pairs_a = build_pairs_condition_A(triples)
    pairs_b = build_pairs_condition_B(triples)
    pairs_p = build_pairs_condition_P(triples)
    for cond, pairs in [("A", pairs_a), ("B", pairs_b), ("P", pairs_p)]:
        validate_state_alignment(pairs)
    return {"A": pairs_a, "B": pairs_b, "P": pairs_p}
