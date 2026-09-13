import json
import os
import sys
import tempfile
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.append(os.path.join(_THIS_DIR, "../../h-e1/code"))
from evaluate import generate_completion


def load_humaneval():
    """Load HumanEval test set (164 problems)."""
    try:
        from human_eval.data import read_problems
        problems = read_problems()
        return list(problems.values())
    except ImportError:
        pass
    try:
        from datasets import load_dataset
        ds = load_dataset("openai_humaneval", split="test")
        return list(ds)
    except Exception:
        pass
    raise RuntimeError(
        "Could not load HumanEval. Install: pip install human-eval  OR  "
        "pip install datasets"
    )


def evaluate_humaneval_checkpoint(
    checkpoint_path: str,
    tokenizer,
    problems: list,
    timeout: float = 10.0,
) -> float:
    """Evaluate one checkpoint on HumanEval. Returns pass@1 float in [0,1]."""
    from human_eval.evaluation import evaluate_functional_correctness

    dtype = torch.bfloat16
    print(f"  Loading checkpoint: {checkpoint_path}")
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    samples = []
    for i, problem in enumerate(problems):
        task_id = problem["task_id"]
        prompt = problem["prompt"]
        completion = generate_completion(model, tokenizer, prompt, max_new_tokens=512)
        samples.append({"task_id": task_id, "completion": completion})
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(problems)}] problems evaluated")

    del model
    torch.cuda.empty_cache()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
        sample_file = f.name

    try:
        results = evaluate_functional_correctness(sample_file, k=[1], timeout=timeout)
        pass_at_1 = float(results["pass@1"])
    finally:
        os.unlink(sample_file)

    return pass_at_1


def batch_evaluate_humaneval(
    checkpoint_paths: dict,
    model_name: str,
    problems: Optional[list] = None,
) -> dict:
    """Evaluate multiple checkpoints sequentially. Returns {step: pass@1}."""
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if problems is None:
        print("Loading HumanEval dataset...")
        problems = load_humaneval()
    print(f"Evaluating {len(problems)} HumanEval problems across {len(checkpoint_paths)} checkpoints")

    results = {}
    for step in sorted(checkpoint_paths.keys()):
        ckpt_path = checkpoint_paths[step]
        print(f"\n[step={step}] Evaluating checkpoint: {ckpt_path}")
        score = evaluate_humaneval_checkpoint(ckpt_path, tokenizer, problems)
        results[step] = score
        print(f"[step={step}] pass@1 = {score:.4f}")

    return results
