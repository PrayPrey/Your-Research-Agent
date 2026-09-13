"""H-M2 Evaluate: IFEval held-out evaluation for all variants."""
import sys
import json
from pathlib import Path
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from data import load_ifeval_split, build_constraints
from ifeval_signal import BaselineChecker


def evaluate_variant(
    checkpoint_path: str,
    ifeval_test,
    device: str = "cuda",
    max_new_tokens: int = 256
) -> dict:
    """Evaluate variant on held-out IFEval test split."""
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    checker = BaselineChecker()
    strict_correct = 0
    loose_correct = 0
    total = 0
    per_type_scores = defaultdict(list)

    for row in ifeval_test:
        prompt = row["prompt"]
        constraints = build_constraints(row)
        constraint_types = [c.get("type", "unknown") for c in constraints]

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )

        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        # Check each constraint
        constraint_scores = []
        for c in constraints:
            score = checker._check_single(response, c)
            constraint_scores.append(score)
            c_type = c.get("type", "unknown")
            per_type_scores[c_type].append(score)

        # Strict: all constraints satisfied (score >= 1.0 for each)
        all_satisfied = all(s >= 1.0 for s in constraint_scores) if constraint_scores else True
        # Loose: any constraint satisfied
        any_satisfied = any(s >= 1.0 for s in constraint_scores) if constraint_scores else True

        if all_satisfied:
            strict_correct += 1
        if any_satisfied:
            loose_correct += 1
        total += 1

    per_type_accuracy = {k: sum(v) / len(v) for k, v in per_type_scores.items()}

    return {
        "strict_accuracy": strict_correct / total if total > 0 else 0.0,
        "loose_accuracy": loose_correct / total if total > 0 else 0.0,
        "total": total,
        "strict_correct": strict_correct,
        "loose_correct": loose_correct,
        "per_constraint_type": per_type_accuracy,
    }


def evaluate_all(
    run_results: dict[str, dict],
    ifeval_test,
    device: str = "cuda"
) -> dict[str, dict]:
    """Evaluate all variants."""
    eval_results = {}

    for name, result in run_results.items():
        if "error" in result:
            print(f"[{name}] Skipping (training failed)")
            continue

        checkpoint = result.get("checkpoint")
        if not checkpoint:
            print(f"[{name}] Skipping (no checkpoint)")
            continue

        print(f"[{name}] Evaluating checkpoint: {checkpoint}")
        try:
            eval_result = evaluate_variant(checkpoint, ifeval_test, device)
            eval_results[name] = eval_result
            print(f"[{name}] Strict={eval_result['strict_accuracy']:.3f}, "
                  f"Loose={eval_result['loose_accuracy']:.3f}")
        except Exception as e:
            print(f"[{name}] Eval failed: {e}")
            eval_results[name] = {"error": str(e)}

    return eval_results


if __name__ == "__main__":
    _, ifeval_test = load_ifeval_split(seed=1)

    # Load run results from previous stage
    results_path = Path(__file__).parent / "outputs" / "run_results.json"
    if results_path.exists():
        with open(results_path) as f:
            run_results = json.load(f)
    else:
        print("No run_results.json found. Run train_variants.py first.")
        sys.exit(1)

    eval_results = evaluate_all(run_results, ifeval_test)

    # Save
    output_path = Path(__file__).parent / "outputs" / "eval_results.json"
    with open(output_path, "w") as f:
        json.dump(eval_results, f, indent=2)
    print(f"Saved to {output_path}")
