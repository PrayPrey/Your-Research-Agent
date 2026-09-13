import json
import os
import time
from typing import List, Dict
from data_loader import Problem


def generate_completions(
    problems: List[Problem],
    checkpoint_path: str = "results/completions.jsonl",
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> Dict[str, str]:
    """Returns {problem_id: completion_code}. Skips already-cached."""
    import openai
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Load existing completions from checkpoint
    completions: Dict[str, str] = {}
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    completions[obj["problem_id"]] = obj["completion"]
        print(f"✓ Loaded {len(completions)} cached completions")

    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)

    to_generate = [p for p in problems if p.problem_id not in completions]
    print(f"Generating {len(to_generate)} completions (skipping {len(completions)} cached)...")

    with open(checkpoint_path, "a") as f:
        for i, problem in enumerate(to_generate):
            if i % 50 == 0:
                print(f"  [{i}/{len(to_generate)}] generating...")

            prompt = problem.prompt
            for attempt in range(3):
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "Complete the following Python function. Return only the function body code, no explanations."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    completion = resp.choices[0].message.content or ""
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"  ⚠ Failed {problem.problem_id}: {e}")
                        completion = ""
                    else:
                        time.sleep(2 ** attempt)

            completions[problem.problem_id] = completion
            f.write(json.dumps({"problem_id": problem.problem_id, "completion": completion}) + "\n")
            f.flush()

    print(f"✓ Total completions: {len(completions)}")
    return completions
