#!/usr/bin/env python
"""
PoC Test: Verify grammar-constrained decoding produces syntactically valid Python.
Uses intentionally malformed prompts to induce syntax errors in baseline.
"""
import ast
import json
import os
from datetime import datetime

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def check_syntax(code: str) -> bool:
    if not code or not code.strip():
        return False
    try:
        ast.parse(code)
        return True
    except (SyntaxError, ValueError):
        return False

def run_poc():
    model_id = "bigcode/starcoder2-7b"
    device = "cuda"
    seed = 42

    # Valid prompts - check if completions are syntactically valid
    test_prompts = [
        "def add(a, b):\n    ",
        "def factorial(n):\n    ",
        "def is_prime(n):\n    ",
        "def fibonacci(n):\n    ",
        "def reverse_string(s):\n    ",
    ]

    print(f"[{datetime.now()}] PoC Test: Grammar-Constrained Decoding")
    print("=" * 60)

    # Load model once
    print(f"Loading model {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model.eval()

    baseline_results = []
    print(f"\n[Baseline Generation]")
    for i, prompt in enumerate(test_prompts):
        torch.manual_seed(seed + i)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        out = model.generate(
            **inputs,
            do_sample=True,
            temperature=1.2,  # High temp to induce more varied (potentially invalid) output
            max_new_tokens=64,
            pad_token_id=tokenizer.eos_token_id,
        )
        completion = tokenizer.decode(out[0], skip_special_tokens=True)
        # Full code = prompt + completion (prompt included in output)
        valid = check_syntax(completion)
        baseline_results.append(valid)
        print(f"  Prompt {i+1}: {'VALID' if valid else 'INVALID'}")

    # Free memory
    del model
    torch.cuda.empty_cache()

    # Constrained generation
    print(f"\n[Constrained Generation (SynCode)]")
    from syncode import Syncode
    syn_llm = Syncode(
        model=model_id,
        mode="grammar_strict",
        grammar="python",
        quantize=True,
        device=device,
        max_new_tokens=64,
        temperature=1.2,
    )

    constrained_results = []
    for i, prompt in enumerate(test_prompts):
        torch.manual_seed(seed + i)
        try:
            out = syn_llm.infer(prompt)
            # SynCode returns list of strings
            text = out[0] if isinstance(out, list) and out else (out if isinstance(out, str) else "")
            full_code = prompt + text
            valid = check_syntax(full_code) if text else False
            constrained_results.append(valid)
            print(f"  Prompt {i+1}: {'VALID' if valid else 'INVALID'}")
        except Exception as e:
            print(f"  Prompt {i+1}: ERROR - {e}")
            constrained_results.append(False)

    # Results
    baseline_valid = sum(baseline_results)
    constrained_valid = sum(constrained_results)
    total = len(test_prompts)

    baseline_error_rate = (total - baseline_valid) / total
    constrained_error_rate = (total - constrained_valid) / total

    print(f"\n{'=' * 60}")
    print(f"RESULTS:")
    print(f"  Baseline:     {baseline_valid}/{total} valid ({baseline_error_rate*100:.1f}% error rate)")
    print(f"  Constrained:  {constrained_valid}/{total} valid ({constrained_error_rate*100:.1f}% error rate)")

    gate_pass = constrained_error_rate < baseline_error_rate
    print(f"\nGATE CHECK (MUST_WORK):")
    print(f"  Condition: constrained_error_rate < baseline_error_rate")
    print(f"  {constrained_error_rate:.2f} < {baseline_error_rate:.2f} = {gate_pass}")
    print(f"  Result: {'PASS' if gate_pass else 'FAIL'}")

    results = {
        "hypothesis_id": "h-m1",
        "timestamp": datetime.now().isoformat(),
        "poc_mode": True,
        "baseline": {
            "error_rate": baseline_error_rate,
            "n_valid": baseline_valid,
            "n_total": total,
        },
        "constrained": {
            "error_rate": constrained_error_rate,
            "n_valid": constrained_valid,
            "n_total": total,
        },
        "gate": {
            "type": "MUST_WORK",
            "condition": "constrained_error_rate < baseline_error_rate",
            "satisfied": gate_pass,
            "verdict": "PASS" if gate_pass else "FAIL"
        },
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to outputs/results.json")

    return 0 if gate_pass else 1

if __name__ == "__main__":
    import sys
    sys.exit(run_poc())
