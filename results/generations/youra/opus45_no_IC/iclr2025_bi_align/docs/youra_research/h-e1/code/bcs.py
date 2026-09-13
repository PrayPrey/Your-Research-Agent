"""BCS computation using spaCy + TextDescriptives."""

import numpy as np
from scipy.stats import pearsonr
import pickle
import os
from multiprocessing import Pool
from config import SPACY_MODEL, BATCH_SIZE, N_WORKERS, FK_GRADE_MAX, SENT_LEN_MAX, DEP_DIST_MAX

_worker_computer = None


class BCSComputer:
    """Compute Bidirectional Convergence Score."""

    def __init__(self, nlp_model: str = SPACY_MODEL):
        import spacy
        import textdescriptives
        self.nlp = spacy.load(nlp_model)
        self.nlp.add_pipe("textdescriptives/readability")
        self.nlp.add_pipe("textdescriptives/dependency_distance")

    def compute_complexity(self, text: str) -> float:
        """Compute composite complexity score in [0,1]."""
        if not text or not text.strip():
            return 0.0

        doc = self.nlp(text)

        readability = getattr(doc._, "readability", {}) or {}
        fk = readability.get("flesch_kincaid_grade", 0) or 0

        sents = list(doc.sents)
        sent = sum(len(s) for s in sents) / max(1, len(sents))

        dep_dict = getattr(doc._, "dependency_distance", {}) or {}
        dep = dep_dict.get("dependency_distance_mean", 0) or 0

        norm_fk = min(max(fk / FK_GRADE_MAX, 0), 1)
        norm_sent = min(max(sent / SENT_LEN_MAX, 0), 1)
        norm_dep = min(max(dep / DEP_DIST_MAX, 0), 1)

        return (norm_fk + norm_sent + norm_dep) / 3

    def compute_bcs(self, user_turns: list, ai_turns: list) -> float:
        """Compute BCS as Pearson correlation of complexity trajectories."""
        if len(user_turns) < 4 or len(ai_turns) < 4:
            return np.nan

        user_traj = [self.compute_complexity(t) for t in user_turns]
        ai_traj = [self.compute_complexity(t) for t in ai_turns]

        min_len = min(len(user_traj), len(ai_traj))
        user_traj = user_traj[:min_len]
        ai_traj = ai_traj[:min_len]

        if np.std(user_traj) == 0 or np.std(ai_traj) == 0:
            return 0.0

        bcs, _ = pearsonr(user_traj, ai_traj)
        return bcs


def _init_worker(nlp_model: str):
    """Initialize worker-local BCSComputer."""
    global _worker_computer
    _worker_computer = BCSComputer(nlp_model)


def _compute_one(conversation: dict) -> float:
    """Compute BCS for single conversation (worker function)."""
    from data import extract_role_turns
    try:
        user_turns, ai_turns = extract_role_turns(conversation)
        return _worker_computer.compute_bcs(user_turns, ai_turns)
    except Exception:
        return np.nan


def batch_compute_bcs(
    conversations: list,
    batch_size: int = BATCH_SIZE,
    n_workers: int = N_WORKERS,
    checkpoint_path: str = None,
) -> list:
    """Batch compute BCS with multiprocessing and checkpointing."""
    results = []
    start_idx = 0

    if checkpoint_path and os.path.exists(checkpoint_path):
        with open(checkpoint_path, "rb") as f:
            results = pickle.load(f)
        start_idx = len(results)
        print(f"Resumed from checkpoint: {start_idx} results")

    remaining = conversations[start_idx:]
    if not remaining:
        return results

    with Pool(n_workers, initializer=_init_worker, initargs=(SPACY_MODEL,)) as pool:
        for batch_start in range(0, len(remaining), batch_size):
            batch = remaining[batch_start:batch_start + batch_size]
            batch_results = pool.map(_compute_one, batch)
            results.extend(batch_results)

            if checkpoint_path and (batch_start + batch_size) % 1000 == 0:
                with open(checkpoint_path, "wb") as f:
                    pickle.dump(results, f)
                print(f"Checkpoint saved: {len(results)} results")

    if checkpoint_path:
        with open(checkpoint_path, "wb") as f:
            pickle.dump(results, f)

    return results
