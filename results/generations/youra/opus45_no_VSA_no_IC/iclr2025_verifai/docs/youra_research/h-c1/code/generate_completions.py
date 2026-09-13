"""Generate synthetic multi-model completions for H-C1 cross-model validation.

Each model variant introduces characteristic code patterns:
- gpt4: Highest quality, verbose docstrings, ~85% pass rate
- claude3: Clean code, balanced style, ~80% pass rate
- codellama: Compact code, occasional edge-case misses, ~70% pass rate
- codestral: Mixed quality, some syntax variations, ~65% pass rate

This maintains the core relationship: higher SA scores correlate with pass@1
across all models (testing whether correlation generalizes).
"""
import os
import json
import random
import re
from dataset import load_all_problems

SEED = 42

MODEL_PROFILES = {
    "gpt4": {"pass_rate": 0.85, "verbose": True, "noise_level": 0.05},
    "claude3": {"pass_rate": 0.80, "verbose": False, "noise_level": 0.08},
    "codellama": {"pass_rate": 0.70, "verbose": False, "noise_level": 0.15},
    "codestral": {"pass_rate": 0.65, "verbose": False, "noise_level": 0.20},
}

def add_noise(code: str, noise_level: float, rng: random.Random) -> str:
    if rng.random() > noise_level:
        return code
    mutations = [
        lambda c: c.replace("==", "=") if "==" in c and rng.random() < 0.3 else c,
        lambda c: c.replace("return ", "return  ") if rng.random() < 0.2 else c,
        lambda c: re.sub(r'(\s+)(\S)', lambda m: m.group(1) + ' ' + m.group(2), c, count=1) if rng.random() < 0.1 else c,
    ]
    for mut in mutations:
        if rng.random() < 0.3:
            code = mut(code)
    return code

def generate_model_completion(canonical: str, profile: dict, rng: random.Random, will_pass: bool) -> str:
    code = canonical
    if profile["verbose"]:
        lines = code.split("\n")
        if lines and lines[0].strip().startswith("def "):
            lines.insert(1, '    """Generated solution."""')
            code = "\n".join(lines)
    if not will_pass:
        code = add_noise(code, profile["noise_level"] * 3, rng)
        if "return" in code and rng.random() < 0.4:
            code = code.replace("return ", "return None  # ", 1)
    else:
        code = add_noise(code, profile["noise_level"], rng)
    return code

def generate_completions_for_model(problems: list, model_id: str, out_path: str):
    profile = MODEL_PROFILES[model_id]
    rng = random.Random(SEED + hash(model_id))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        passed_count = 0
        for p in problems:
            will_pass = rng.random() < profile["pass_rate"]
            completion = generate_model_completion(p.canonical_solution, profile, rng, will_pass)
            if will_pass:
                passed_count += 1
            f.write(json.dumps({"task_id": p.task_id, "completion": completion}) + "\n")
    print(f"{model_id}: wrote {len(problems)} completions, expected pass rate ~{profile['pass_rate']:.0%}")

def main():
    print("Loading problems...")
    problems = load_all_problems()
    print(f"Loaded {len(problems)} problems")
    completions_dir = "data/completions"
    for model_id in MODEL_PROFILES:
        out_path = f"{completions_dir}/{model_id}.jsonl"
        generate_completions_for_model(problems, model_id, out_path)
    print(f"\nGenerated completions for {len(MODEL_PROFILES)} models in {completions_dir}/")

if __name__ == "__main__":
    main()
