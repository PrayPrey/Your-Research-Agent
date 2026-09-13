import os
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _THIS_DIR)
sys.path.append(os.path.join(_THIS_DIR, "../../h-e1/code"))
from evaluate import generate_completion


def load_mbpp():
    """Load MBPP test split (374 problems)."""
    from datasets import load_dataset
    ds = load_dataset("google-research-datasets/mbpp", split="test")
    return list(ds)


def evaluate_mbpp(
    checkpoint_path: str,
    model_name: str,
    max_new_tokens: int = 512,
) -> float:
    """Evaluate checkpoint on MBPP pass@1. Returns float in [0,1]."""
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading checkpoint: {checkpoint_path}")
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    problems = load_mbpp()
    print(f"Evaluating {len(problems)} MBPP problems...")

    passed = 0
    for i, problem in enumerate(problems):
        prompt = problem["text"]
        test_list = problem.get("test_list", [])
        completion = generate_completion(model, tokenizer, prompt, max_new_tokens=max_new_tokens)

        # Execute completion + test cases
        full_code = completion + "\n" + "\n".join(test_list)
        try:
            exec(compile(full_code, "<string>", "exec"), {})
            passed += 1
        except Exception:
            pass

        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(problems)}] passed so far: {passed}")

    del model
    torch.cuda.empty_cache()

    pass_at_1 = passed / len(problems)
    print(f"MBPP pass@1: {pass_at_1:.4f} ({passed}/{len(problems)})")
    return pass_at_1
