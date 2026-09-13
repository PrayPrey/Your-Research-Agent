"""Dataset loading for H-E1."""
import ast
from dataclasses import dataclass
from datasets import load_dataset
from config import CONFIG

@dataclass
class Sample:
    task_id: str
    source: str
    code: str

def load_humaneval() -> list[Sample]:
    ds = load_dataset(CONFIG.HUMANEVAL_SOURCE, split="test", trust_remote_code=True)
    samples = []
    for row in ds:
        code = row.get("prompt", "") + row.get("canonical_solution", "")
        samples.append(Sample(task_id=row["task_id"], source="humaneval", code=code))
    return samples

def load_mbpp() -> list[Sample]:
    ds = load_dataset(CONFIG.MBPP_SOURCE, split=CONFIG.MBPP_SPLIT, trust_remote_code=True)
    samples = []
    for row in ds:
        samples.append(Sample(task_id=str(row["task_id"]), source="mbpp", code=row["code"]))
    return samples

def validate_syntax(sample: Sample) -> bool:
    try:
        ast.parse(sample.code)
        return True
    except SyntaxError:
        return False

def load_all_samples() -> list[Sample]:
    humaneval = load_humaneval()
    mbpp = load_mbpp()
    all_samples = humaneval + mbpp
    valid = [s for s in all_samples if validate_syntax(s)]
    print(f"Loaded {len(humaneval)} HumanEval + {len(mbpp)} MBPP = {len(all_samples)} total, {len(valid)} valid")
    return valid
