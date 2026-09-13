import os
import importlib.util as _ilu
from typing import Dict, List, Callable

# Dynamic import of h-m1/code/data.py
_H_M1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-m1/code"))
_spec = _ilu.spec_from_file_location("h_m1_data", os.path.join(_H_M1_CODE, "data.py"))
_data_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_data_mod)

# Re-exported symbols from H-M1
LongBenchDataLoader = _data_mod.LongBenchDataLoader
LONGBENCH_TASKS: List[str] = _data_mod.LONGBENCH_TASKS
LONGBENCH_CATEGORIES: Dict[str, List[str]] = _data_mod.LONGBENCH_CATEGORIES

from config import TASK_SCORER_MAP, TASK_MAX_NEW_TOKENS


def _f1_score(prediction: str, answers: List[str]) -> float:
    """Token-level F1 score."""
    pred_tokens = set(prediction.lower().split())
    best = 0.0
    for ans in answers:
        ans_tokens = set(ans.lower().split())
        if not pred_tokens or not ans_tokens:
            continue
        common = pred_tokens & ans_tokens
        if not common:
            continue
        p = len(common) / len(pred_tokens)
        r = len(common) / len(ans_tokens)
        f1 = 2 * p * r / (p + r)
        best = max(best, f1)
    return best


def _rouge_l_score(prediction: str, answers: List[str]) -> float:
    """Simple ROUGE-L (LCS-based) score."""
    def lcs_len(a, b):
        a, b = a.lower().split(), b.lower().split()
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                dp[i][j] = dp[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]

    best = 0.0
    pred_len = len(prediction.split())
    for ans in answers:
        ans_len = len(ans.split())
        lcs = lcs_len(prediction, ans)
        if pred_len == 0 or ans_len == 0:
            continue
        p = lcs / pred_len
        r = lcs / ans_len
        if p + r > 0:
            best = max(best, 2 * p * r / (p + r))
    return best


def _accuracy_score(prediction: str, answers: List[str]) -> float:
    pred = prediction.strip().lower()
    return float(any(pred == a.strip().lower() for a in answers))


def _edit_distance_score(prediction: str, answers: List[str]) -> float:
    """Edit-distance similarity (1 - normalized edit distance)."""
    def edit_dist(s1, s2):
        m, n = len(s1), len(s2)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            prev = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                temp = dp[j]
                dp[j] = prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1])
                prev = temp
        return dp[n]

    best = 0.0
    for ans in answers:
        max_len = max(len(prediction), len(ans), 1)
        sim = 1.0 - edit_dist(prediction, ans) / max_len
        best = max(best, sim)
    return best


_SCORER_FNS: Dict[str, Callable] = {
    "f1": _f1_score,
    "rouge-l": _rouge_l_score,
    "accuracy": _accuracy_score,
    "edit-distance": _edit_distance_score,
}


def score_prediction(task_name: str, prediction: str, answers: List[str]) -> float:
    """Route to appropriate scorer via TASK_SCORER_MAP. Returns score in [0, 1]."""
    scorer_type = TASK_SCORER_MAP.get(task_name, "f1")
    scorer_fn = _SCORER_FNS[scorer_type]
    return scorer_fn(prediction, answers)


def run_task_evaluation(
    model,
    tokenizer,
    task_name: str,
    max_seq_length: int = 4096,
    device: str = "cuda",
) -> float:
    """Run full test split for one task; return mean score. batch_size=1, greedy decoding."""
    import torch

    max_new_tokens = TASK_MAX_NEW_TOKENS.get(task_name, 64)

    try:
        loader = LongBenchDataLoader(tokenizer, max_seq_length=max_seq_length, tasks=[task_name])
        samples = list(loader.iter_all_samples())
    except Exception:
        # Fallback: try HuggingFace datasets directly
        try:
            from datasets import load_dataset
            ds = load_dataset("THUDM/LongBench", task_name, split="test",
                              storage_options={"client_kwargs": {"timeout": 60}})
            samples = list(ds)
        except Exception:
            return 0.0

    if not samples:
        return 0.0

    scores = []
    model.eval()
    with torch.no_grad():
        for sample in samples:
            try:
                if isinstance(sample, dict) and "input_ids" in sample:
                    input_ids = sample["input_ids"]
                    if not isinstance(input_ids, torch.Tensor):
                        input_ids = torch.tensor(input_ids)
                    input_ids = input_ids.unsqueeze(0).to(device)
                    answers = sample.get("answers", sample.get("answer", [""]))
                else:
                    # Raw HuggingFace sample
                    context = sample.get("context", "")
                    question = sample.get("input", context)
                    enc = tokenizer(question, return_tensors="pt",
                                    truncation=True, max_length=max_seq_length)
                    input_ids = enc["input_ids"].to(device)
                    answers = sample.get("answers", [sample.get("answer", "")])

                if isinstance(answers, str):
                    answers = [answers]

                out = model.generate(
                    input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )
                generated = out[0][input_ids.shape[1]:]
                prediction = tokenizer.decode(generated, skip_special_tokens=True).strip()
                scores.append(score_prediction(task_name, prediction, answers))
            except Exception:
                scores.append(0.0)

    return float(sum(scores) / len(scores)) if scores else 0.0


def compute_category_accuracies(per_task_scores: Dict[str, float]) -> Dict[str, float]:
    """Aggregate per-task scores into 6-category means."""
    import numpy as np
    result = {}
    for cat, tasks in LONGBENCH_CATEGORIES.items():
        cat_scores = [per_task_scores[t] for t in tasks if t in per_task_scores]
        result[cat] = float(np.mean(cat_scores)) if cat_scores else float("nan")
    return result
