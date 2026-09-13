import argparse
import json
import os
import sys
import tempfile
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, os.path.dirname(__file__))
from config import GRPOConfig, load_config


def load_checkpoint(checkpoint_path: str, dtype=torch.bfloat16):
    """Load model and tokenizer from checkpoint_path."""
    print(f"Loading checkpoint from: {checkpoint_path}")
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


def generate_completion(model, tokenizer, prompt: str, max_new_tokens: int = 512) -> str:
    """Greedy decode (do_sample=False). Returns generated text only (no prompt)."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )
    prompt_len = inputs["input_ids"].shape[1]
    generated_ids = output_ids[0][prompt_len:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True)


def load_humaneval_problems() -> list:
    """Load HumanEval problems (164 problems)."""
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
        "datasets package with openai_humaneval"
    )


def eval_humaneval(model, tokenizer, problems: list, max_new_tokens: int = 512) -> float:
    """
    Greedy decode all HumanEval problems. Returns pass@1 as float.
    Uses human_eval.evaluation.evaluate_functional_correctness internally.
    """
    from human_eval.evaluation import evaluate_functional_correctness

    samples = []
    for problem in problems:
        task_id = problem["task_id"]
        prompt = problem["prompt"]
        completion = generate_completion(model, tokenizer, prompt, max_new_tokens)
        samples.append({"task_id": task_id, "completion": completion})
        if len(samples) % 20 == 0:
            print(f"  Evaluated {len(samples)}/{len(problems)} problems")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
        sample_file = f.name

    try:
        results = evaluate_functional_correctness(sample_file, k=[1])
        pass_at_1 = results["pass@1"]
    finally:
        os.unlink(sample_file)

    return float(pass_at_1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["binary", "ratio"], required=True)
    parser.add_argument("--checkpoint-step", type=int, default=200)
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    checkpoint_path = os.path.join(
        cfg.output_dir, "checkpoints", args.condition,
        f"checkpoint-{args.checkpoint_step}"
    )

    if not os.path.exists(checkpoint_path):
        print(f"ERROR: Checkpoint not found at {checkpoint_path}")
        sys.exit(1)

    model, tokenizer = load_checkpoint(checkpoint_path)
    problems = load_humaneval_problems()
    print(f"Evaluating {len(problems)} HumanEval problems (condition={args.condition})...")
    score = eval_humaneval(model, tokenizer, problems)
    print(f"HumanEval pass@1 [{args.condition}]: {score:.4f} ({score*100:.2f}%)")

    # Save result
    result_path = os.path.join(cfg.output_dir, f"humaneval_{args.condition}.json")
    with open(result_path, "w") as f:
        json.dump({"condition": args.condition, "step": args.checkpoint_step, "pass_at_1": score}, f)
    print(f"Result saved to: {result_path}")


if __name__ == "__main__":
    main()
