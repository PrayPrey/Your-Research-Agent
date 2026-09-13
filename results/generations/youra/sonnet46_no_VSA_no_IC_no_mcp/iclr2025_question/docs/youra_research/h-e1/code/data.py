"""Data loading for H-E1: TriviaQA + h-e2-v2 K=10 samples."""
import json
import os
import numpy as np


H_E2V2_CACHE = (
    "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_question/docs/youra_research"
    "/_archive/20260825T162535_routing_recovery/h-e2-v2/code/results/interim_cache.jsonl"
)


def load_h_e2v2_samples(samples_path: str = H_E2V2_CACHE) -> dict:
    """Load h-e2-v2 samples. Returns {question_id: {samples, log_probs, answers, greedy, te_score, is_correct}}."""
    samples_map = {}
    with open(samples_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            qid = d["question_id"]
            samples_map[qid] = {
                "samples": d.get("answers", []),
                "log_probs": d.get("norm_log_probs", []),
                "answer_aliases": d.get("answer_aliases", []),
                "greedy_answer": d.get("greedy_answer", ""),
                "te_score": d.get("te_score", None),
                "is_correct": d.get("is_correct", None),
                "question": d.get("question", ""),
            }
    return samples_map


def get_pilot_questions(samples_map: dict, n: int = 98, seed: int = 42) -> list:
    """Get pilot questions from samples_map (first N by sorted qid for reproducibility)."""
    rng = np.random.default_rng(seed)
    qids = sorted(samples_map.keys())
    # filter to questions with K=10 samples and both se/te data
    valid_qids = [q for q in qids if len(samples_map[q]["samples"]) >= 10]
    idx = rng.choice(len(valid_qids), size=min(n, len(valid_qids)), replace=False)
    selected = [valid_qids[i] for i in sorted(idx)]
    questions = []
    for qid in selected:
        s = samples_map[qid]
        questions.append({
            "question_id": qid,
            "question": s["question"],
            "answers": s["answer_aliases"],
            "greedy_answer": s["greedy_answer"],
            "te_score": s["te_score"],
            "is_correct": s["is_correct"],
        })
    return questions
