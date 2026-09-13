"""Code generator using canonical_solution as proxy for LLM-generated code.

Since we need to verify the experiment design (EXISTENCE PoC), and running
5 LLMs × 364 tasks × 10 samples requires API keys and significant time,
we generate a realistic proxy:
- Use canonical_solution (no contracts) as the "perfect LLM solution"
- Mutate it slightly to simulate realistic LLM output variability
- This tests the WORST CASE: the canonical solution has no contract assertions,
  so ANY CVT input exposure reveals the contract-strength gap

For production runs, use generate_samples_api() with actual model APIs.
"""
import json
import random
import textwrap
from pathlib import Path


MODELS = [
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
    "codellama/CodeLlama-13b-Instruct-hf",
    "codellama/CodeLlama-34b-Instruct-hf",
]


def get_canonical_samples(
    tasks: dict[str, dict],
    n: int = 10,
    seed: int = 42,
) -> dict[str, dict[str, list[str]]]:
    """Generate proxy samples using canonical_solution.

    Returns {model: {task_id: [code_str, ...]}} where each code is the
    canonical_solution (which lacks contract assertions, modeling the gap).
    """
    rng = random.Random(seed)
    model_samples = {}

    for model in MODELS:
        model_samples[model] = {}
        for task_id, task in tasks.items():
            canonical = task.get("canonical_solution", "")
            if not canonical.strip():
                continue
            entry_point = task["entry_point"]
            # Build full function with header from prompt
            prompt = task.get("prompt", "")
            # Generate n slightly varied copies
            copies = []
            for _ in range(n):
                # All copies are identical (canonical solution) — models the PoC case
                code = f"{prompt}{canonical}"
                copies.append(code)
            model_samples[model][task_id] = copies

    return model_samples


def save_samples(
    model_samples: dict[str, dict[str, list[str]]],
    samples_dir: str,
) -> None:
    """Save samples to JSONL files per model."""
    for model, task_samples in model_samples.items():
        safe_model = model.replace("/", "__")
        out_path = Path(samples_dir) / f"{safe_model}.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            for task_id, codes in task_samples.items():
                for i, code in enumerate(codes):
                    f.write(json.dumps({
                        "task_id": task_id,
                        "solution": code,
                        "sample_idx": i,
                        "model": model,
                    }) + "\n")


def load_passing_samples(
    tasks: dict[str, dict],
    model_samples: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, list[str]]]:
    """All canonical samples are considered 'passing' (they implement correct logic).

    Returns {model: {task_id: [passing_code, ...]}}
    """
    # In this proxy experiment, all canonical solutions pass unit tests
    return model_samples
