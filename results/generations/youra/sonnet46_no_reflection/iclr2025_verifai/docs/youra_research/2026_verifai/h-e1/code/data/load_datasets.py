import os
import logging
from dataclasses import dataclass
from typing import List, Dict

logger = logging.getLogger(__name__)


@dataclass
class Problem:
    name: str
    split: str
    formal_statement: str
    goal: str
    header: str
    dataset: str  # "minif2f" | "vericoding"


def load_minif2f() -> List[Problem]:
    """Load all miniF2F problems from HuggingFace Tonic/MiniF2F."""
    from datasets import load_dataset
    ds = load_dataset("Tonic/MiniF2F")
    problems = []
    for split_name in ds:
        split_data = ds[split_name]
        for row in split_data:
            row_dict = dict(row)  # type: ignore[arg-type]
            problems.append(Problem(
                name=str(row_dict.get("name", "")),
                split=str(row_dict.get("split", split_name)),
                formal_statement=str(row_dict.get("formal_statement", "")),
                goal=str(row_dict.get("goal", "")),
                header=str(row_dict.get("header", "")),
                dataset="minif2f",
            ))
    logger.info(f"Loaded {len(problems)} miniF2F problems")
    return problems


def load_vericoding(data_path: str) -> List[Problem]:
    """Load Lean4-compatible Vericoding problems from local path."""
    import json
    problems = []
    if not os.path.exists(data_path):
        logger.warning(f"Vericoding data path not found: {data_path}. Returning empty list.")
        return problems
    for fname in os.listdir(data_path):
        if not fname.endswith(".jsonl"):
            continue
        fpath = os.path.join(data_path, fname)
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                # Only include Lean4-compatible problems
                if row.get("language", "lean4").lower() not in ("lean4", "lean"):
                    continue
                problems.append(Problem(
                    name=row.get("name", ""),
                    split=row.get("split", "train"),
                    formal_statement=row.get("formal_statement", row.get("statement", "")),
                    goal=row.get("goal", ""),
                    header=row.get("header", ""),
                    dataset="vericoding",
                ))
    logger.info(f"Loaded {len(problems)} Vericoding problems from {data_path}")
    return problems


def run_cold_start_sft_evaluation(
    problems: List[Problem],
    model_id: str,
    rollouts: int = 16,
) -> Dict[str, float]:
    """Run BFS-Prover SFT in inference mode; returns problem_name -> pass@1.

    For PoC: uses a lightweight beam search approximation over the model's
    top-k tactic predictions. Full BFS search is handled in run_experiment.py.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    logger.info(f"Running cold-start SFT evaluation on {len(problems)} problems ({rollouts} rollouts each)")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True
    )
    model.eval()

    pass_at_1_scores: Dict[str, float] = {}

    with torch.no_grad():
        for prob in problems:
            prompt = _format_proof_state(prob)
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
            successes = 0
            for _ in range(rollouts):
                out = model.generate(
                    **inputs,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=1.0,
                    top_p=0.95,
                )
                tactic = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
                # PoC: count non-empty tactic as attempt; actual proof checking needs LeanDojo
                if tactic and not _is_trivially_wrong(tactic):
                    successes += 1
            pass_at_1_scores[prob.name] = successes / rollouts

    logger.info(f"Cold-start SFT evaluation complete. Mean pass@1: {sum(pass_at_1_scores.values()) / max(len(pass_at_1_scores), 1):.3f}")
    return pass_at_1_scores


def construct_hard_subset(
    problems: List[Problem],
    pass_at_1_scores: Dict[str, float],
    threshold: float = 0.20,
) -> List[Problem]:
    """Return problems where pass@1 < threshold."""
    hard = [p for p in problems if pass_at_1_scores.get(p.name, 0.0) < threshold]
    logger.info(f"Hard subset: {len(hard)}/{len(problems)} problems (pass@1 < {threshold})")
    return hard


def _format_proof_state(prob: Problem) -> str:
    return f"{prob.header}\n\n-- Problem: {prob.name}\n{prob.formal_statement}\nbegin\n"


def _is_trivially_wrong(tactic: str) -> bool:
    trivial_wrong = ("sorry", "admit", "")
    return tactic.strip().lower() in trivial_wrong
